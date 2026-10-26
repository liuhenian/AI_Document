#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update-mihomo-sub.py  (v2 / 2026-10-26)

用途：从机场订阅地址拉取 mihomo(Clash.Meta) 兼容的 YAML 配置，注入本机运行参数，
      经内核语法校验通过后，原子替换 config.yaml。

v2 相对 v1 的关键改动
--------------------------------------------------------------------------------
1) 订阅端按 User-Agent 做内容协商：浏览器/curl UA 直接返回 403「订阅访问被拒绝」。
   必须伪装成 mihomo / clash.meta 客户端，v1 用的 "Mozilla/5.0" 正是 403 的直接原因。
2) 订阅端现在直接返回 Clash YAML（不再是 base64 编码的 ss:// 列表），
   因此删除 base64 解码 + ss:// 解析逻辑，避免出现「没有解析到有效的 ss 节点」。
3) 该域名有 6 个 CDN 边缘 IP，其中只有一部分可用（其余 TLS 握手被 reset）。
   改为逐 IP 探测 + 好 IP 缓存，避免偶发的 Connection reset by peer。
4) 节点类型已升级为 vless + REALITY，旧 clash(2023.08.17 Premium) 内核不支持，
   必须使用 mihomo 内核；脚本内置 `mihomo -t` 强校验，坏配置绝不覆盖线上配置。

用法
--------------------------------------------------------------------------------
    python3 update-mihomo-sub.py                    # 更新并安装 config.yaml
    python3 update-mihomo-sub.py --restart          # 更新 + 重启 + 启动测速选节点
    python3 update-mihomo-sub.py --restart --no-probe  # 更新 + 重启，不测速
    python3 update-mihomo-sub.py --dry-run          # 只下载并检查，不写 config.yaml
    python3 update-mihomo-sub.py --auto-select      # 备选：生成 url-test 常驻探测组

节点选择说明
--------------------------------------------------------------------------------
本方案默认「启动时测一次、运行期不探测」：
  · 配置保持订阅原生的 `Flybit`（type: select），内核不会周期性探测任何节点；
  · 每次启动由 pick-node.py 一次性测速，选中最快节点写进 select 组；
  · 选择结果存 cache.db，运行期间保持不变，节点挂了不会自动切换（需重新跑 pick-node.py）。
`--auto-select` 是另一条路：生成 url-test 组让内核按 interval 常驻探测 + 自动切换，
代价是常态探测流量，与「启动测一次」互斥，一般不用。
"""

import http.client
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import time
import urllib.parse

# ---------------------------------------------------------------- 基础配置 ----

SUB_URL = "https://fb.750bet.shop/api/v1/dy/y7etr3nr2z64pkh4fbqmmpkz85g86si8"

# 订阅端只认这些客户端族；按顺序尝试，第一个成功的即使用
UA_LIST = [
    "mihomo/1.19.33",
    "clash.meta/1.19.0",
    "ClashMetaForAndroid/2.10.1.Meta",
    "Mihomo/1.19.33",
]

# 该域名在多组 CDN 边缘 IP 之间轮换，其中只有部分 IP 的 TLS 握手不会被重置。
# 这里的种子 IP 是实测可用的；DNS 解析结果不稳定，仅作为补充候选。
SEED_IPS = [
    "112.48.144.91",
    "112.48.144.94",
    "112.48.144.97",
    "112.48.144.130",
]

BASE_DIR = "/mnt/disk/henian/vpn"
WORKDIR = os.path.join(BASE_DIR, "sub-work")
CORE = os.path.join(BASE_DIR, "mihomo")
TARGET_CFG = os.path.join(BASE_DIR, "config.yaml")
RAW_YAML = os.path.join(WORKDIR, "sub-raw.yaml")
GOOD_IPS = os.path.join(WORKDIR, "good-ips.txt")
TEST_DIR = os.path.join(WORKDIR, "test-run")
KEEP_BACKUPS = 5

HTTP_TIMEOUT = 15

# 覆盖写入 config.yaml 顶层的运行参数（键名, 值字面量）
OVERRIDES = [
    ("mixed-port", "7890"),
    ("allow-lan", "true"),
    ("bind-address", "'*'"),
    ("mode", "rule"),
    ("log-level", "info"),
    ("external-controller", "0.0.0.0:9090"),
    ("secret", '"123456"'),
]
OVERRIDE_KEYS = set(k for k, _ in OVERRIDES)

# 订阅默认只代理白名单域名，末尾没有 MATCH，其余流量走 DIRECT。
# 如需「全量走代理」保持 True；想完全沿用机场规则就改成 False。
ENSURE_FINAL_MATCH = True

# 订阅自带的 Flybit 组是 select（手动选择）：不会按延迟排序，也不会故障自动切换，
# 选中项存在 cache.db 里；一旦该节点失效且不手动切，流量就一直断。
# AUTO_SELECT = True 时，脚本额外生成一个 url-test 组并把 MATCH 指向它，实现自动择优 + 自动切换。
# 也可用命令行临时控制：--auto-select / --manual-select
AUTO_SELECT = False
AUTO_GROUP_NAME = "自动选择"
AUTO_TEST_URL = "http://www.gstatic.com/generate_204"
AUTO_TEST_INTERVAL = 300      # 秒
AUTO_TEST_TOLERANCE = 50      # ms，延迟差在此范围内不切换，避免抖动

TOP_KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):")


# ---------------------------------------------------------------- 工具函数 ----

def log(msg=""):
    print(msg, flush=True)


class SNIConn(http.client.HTTPSConnection):
    """连接指定 IP，但 TLS SNI 用真实域名 —— 用于绕过坏 IP / DNS 轮询问题。"""

    def __init__(self, ip, port, sni, timeout):
        ctx = ssl.create_default_context()
        super(SNIConn, self).__init__(ip, port, timeout=timeout, context=ctx)
        self._sni = sni

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self._sni)


def fetch(host, path, ip, ua, timeout=HTTP_TIMEOUT):
    """返回 (status, body_bytes)。ip 为 None 时走系统 DNS。

    注意：用 IP 直连时必须显式带上真实域名的 Host 头，
    否则 http.client 会把 Host 写成 IP，CDN 无法路由到正确站点，返回 403。
    """
    if ip:
        conn = SNIConn(ip, 443, host, timeout)
    else:
        conn = http.client.HTTPSConnection(
            host, 443, timeout=timeout, context=ssl.create_default_context()
        )
    headers = {
        "Host": host,
        "User-Agent": ua,
        "Accept": "*/*",
        "Accept-Encoding": "identity",
        "Connection": "close",
    }
    try:
        conn.request("GET", path, headers=headers)
        resp = conn.getresponse()
        return resp.status, resp.read()
    finally:
        try:
            conn.close()
        except Exception:
            pass


def resolve_ips(host):
    ips = []
    try:
        for info in socket.getaddrinfo(host, 443, socket.AF_INET, socket.SOCK_STREAM):
            ip = info[4][0]
            if ip not in ips:
                ips.append(ip)
    except Exception as exc:
        log("    DNS 解析失败: %s" % exc)
    return ips


def load_cached_ips():
    if not os.path.exists(GOOD_IPS):
        return []
    with open(GOOD_IPS, "r") as f:
        return [ln.strip() for ln in f if ln.strip()]


def save_cached_ips(ip):
    """把成功过的 IP 记下来，连同种子一起作为下次的首选候选。"""
    ips = [ip]
    for old in load_cached_ips():
        if old != ip and old not in ips and len(ips) < 4:
            ips.append(old)
    try:
        with open(GOOD_IPS, "w") as f:
            f.write("\n".join(ips) + "\n")
    except Exception:
        pass


def count_nodes(text):
    """统计 proxies 段内的节点数与类型分布。"""
    in_block = False
    total = 0
    types = {}
    for ln in text.splitlines():
        if TOP_KEY_RE.match(ln):
            in_block = ln.startswith("proxies:")
            continue
        if not in_block:
            continue
        if re.match(r"^\s*-\s", ln):
            total += 1
        m = re.match(r"^\s+(?:-\s+)?type:\s*['\"]?([A-Za-z0-9._-]+)", ln)
        if m:
            types[m.group(1)] = types.get(m.group(1), 0) + 1
    return total, types


def first_select_group(text):
    for ln in text.splitlines():
        if "type: select" not in ln:
            continue
        m = re.search(r"name:\s*'([^']+)'", ln) or re.search(r'name:\s*"([^"]+)"', ln)
        if m:
            return m.group(1)
    return None


def proxy_names(text):
    """按出现顺序取出 proxies 段内所有节点名（含 emoji）。"""
    names = []
    in_block = False
    for ln in text.splitlines():
        if TOP_KEY_RE.match(ln):
            in_block = ln.startswith("proxies:")
            continue
        if not in_block:
            continue
        m = re.match(r'^\s+(?:-\s+)?name:\s*"((?:[^"\\]|\\.)*)"\s*$', ln)
        if not m:
            m = re.match(r"^\s+(?:-\s+)?name:\s*'([^']*)'\s*$", ln)
        if m:
            names.append(m.group(1))
    return names


def ensure_auto_group(text):
    """在 proxy-groups 末尾追加 url-test 组，并把 MATCH 指向它。

    订阅自带的 select 组不会自动择优也不会自动切换；
    这里补一个 url-test 组，让内核按实测延迟自动选节点、节点失效自动漂移。
    """
    names = proxy_names(text)
    if not names:
        log("  ! 未取到节点列表，跳过自动选择组")
        return text

    if re.search(r"^\s*-?\s*(?:name:\s*['\"]%s['\"])" % re.escape(AUTO_GROUP_NAME),
                 text, re.M):
        log("  自动选择组已存在，跳过")
        return text

    quoted = ", ".join('"%s"' % n.replace("\\", "\\\\").replace('"', '\\"')
                       for n in names)
    block = (
        "    - name: \"%s\"\n"
        "      type: url-test\n"
        "      url: \"%s\"\n"
        "      interval: %d\n"
        "      tolerance: %d\n"
        "      lazy: false\n"
        "      proxies: [%s]\n"
    ) % (AUTO_GROUP_NAME, AUTO_TEST_URL, AUTO_TEST_INTERVAL,
         AUTO_TEST_TOLERANCE, quoted)

    lines = text.splitlines()
    out = []
    inserted = False
    for ln in lines:
        if not inserted and TOP_KEY_RE.match(ln) and ln.startswith("rules:"):
            out.append(block.rstrip("\n"))
            inserted = True
        out.append(ln)
    if not inserted:
        out.append(block.rstrip("\n"))
    text = "\n".join(out) + "\n"

    # 把 MATCH 目标改为自动选择组
    text, n = re.subn(r"^(\s*-\s*'?)MATCH,[^'\"\n]*", r"\g<1>MATCH,%s" % AUTO_GROUP_NAME,
                      text, flags=re.M)
    if n == 0:
        text += "    - 'MATCH,%s'\n" % AUTO_GROUP_NAME

    log("  已注入自动选择组「%s」：%d 个节点参与 url-test，MATCH 指向该组"
        % (AUTO_GROUP_NAME, len(names)))
    return text


# ---------------------------------------------------------------- 核心步骤 ----

def download_subscription():
    u = urllib.parse.urlsplit(SUB_URL)
    host = u.hostname
    path = u.path or "/"
    if u.query:
        path += "?" + u.query

    cached = load_cached_ips()
    resolved = resolve_ips(host)
    # 候选顺序：缓存好 IP -> 实测种子 IP -> 本次 DNS 解析结果
    ips = []
    for ip in cached + SEED_IPS + resolved:
        if ip and ip not in ips:
            ips.append(ip)
    if not ips:
        raise RuntimeError("域名解析不到任何 IPv4 地址，检查本机 DNS/网络")

    log("  域名 %s 候选 IP %d 个（缓存 %d / 种子 %d / DNS %d）"
        % (host, len(ips), len(cached), len(SEED_IPS), len(resolved)))

    last_err = "未知错误"
    for ip in ips:
        for ua in UA_LIST:
            try:
                status, body = fetch(host, path, ip, ua)
            except Exception as exc:
                last_err = "%s @ %s -> %s" % (ua, ip, exc)
                log("    × %-16s %s" % (ip, exc))
                break  # 该 IP 网络层就不通，换 IP，不必换 UA
            if status == 403:
                # UA 不被认可：同一 IP 换 UA 继续试
                snippet = body[:110].decode("utf-8", "replace").replace("\n", " ")
                last_err = "%s @ %s -> HTTP 403 %s" % (ua, ip, snippet)
                log("    × %-16s HTTP 403 (UA=%s) %s" % (ip, ua, snippet))
                continue

            if status == 200 and b"proxies:" in body:
                log("    √ %-16s HTTP 200, %d 字节, UA=%s" % (ip, len(body), ua))
                save_cached_ips(ip)
                return body.decode("utf-8", "replace")

            snippet = body[:110].decode("utf-8", "replace").replace("\n", " ")
            last_err = "%s @ %s -> HTTP %s %s" % (ua, ip, status, snippet)
            log("    × %-16s HTTP %s %s" % (ip, status, snippet))
            break

    raise RuntimeError(
        "订阅下载失败。最后一次错误：%s\n"
        "提示：403『订阅访问被拒绝』= UA 不被认可；"
        "Connection reset = 该边缘 IP 不可用；请检查订阅链接是否过期。" % last_err
    )


def patch_config(text):
    """剔除冲突的顶层键，写入本机运行参数。"""
    kept = []
    for ln in text.splitlines():
        m = TOP_KEY_RE.match(ln)
        if m and m.group(1) in OVERRIDE_KEYS:
            continue
        kept.append(ln)

    body = "\n".join(kept).strip("\n")
    head = "\n".join("%s: %s" % (k, v) for k, v in OVERRIDES)
    merged = head + "\n\n" + body + "\n"

    if ENSURE_FINAL_MATCH and not re.search(r"^\s*-\s*'?MATCH", merged, re.M):
        target = first_select_group(merged)
        if target:
            # 沿用规则段的缩进
            indent = "    "
            m = re.search(r"^(\s*)-\s*'?DOMAIN", merged, re.M)
            if m:
                indent = m.group(1)
            if not merged.endswith("\n"):
                merged += "\n"
            merged += "%s- 'MATCH,%s'\n" % (indent, target)
            log("  已追加兜底规则：MATCH,%s（其余流量走该组）" % target)

    return merged


def validate_with_core(candidate_path):
    """用 mihomo -t 做真实语法/协议校验；顺带保证 Country.mmdb 可达。"""
    if not os.path.exists(CORE):
        log("  ! 未找到内核 %s，跳过内核校验" % CORE)
        return True, ""

    if os.path.isdir(TEST_DIR):
        shutil.rmtree(TEST_DIR, ignore_errors=True)
    os.makedirs(TEST_DIR, exist_ok=True)

    shutil.copyfile(candidate_path, os.path.join(TEST_DIR, "config.yaml"))
    mmdb = os.path.join(BASE_DIR, "Country.mmdb")
    if os.path.exists(mmdb):
        dst = os.path.join(TEST_DIR, "Country.mmdb")
        try:
            os.symlink(mmdb, dst)
        except Exception:
            shutil.copyfile(mmdb, dst)

    proc = subprocess.run(
        [CORE, "-t", "-d", TEST_DIR],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=90,
    )
    out = proc.stdout.decode("utf-8", "replace")
    return proc.returncode == 0, out


def backup_current():
    if not os.path.exists(TARGET_CFG):
        return None
    dst = "%s.bak-%s" % (TARGET_CFG, time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(TARGET_CFG, dst)
    olds = sorted(
        [os.path.join(BASE_DIR, f) for f in os.listdir(BASE_DIR)
         if f.startswith("config.yaml.bak-")],
        key=os.path.getmtime,
    )
    for f in olds[:-KEEP_BACKUPS] if len(olds) > KEEP_BACKUPS else []:
        try:
            os.remove(f)
        except Exception:
            pass
    return dst


def find_core_pids():
    """扫描 /proc 找本目录内核进程。

    不用 pkill/pgrep -f 的字符串匹配：当调用方命令行里也含有该字符串时
    （例如在 shell 里写 pkill -f 'mihomo -d <dir>'），会把自己也匹配上一起杀掉。
    这里改为比对 /proc/<pid>/exe 指向的真实文件，最精确。
    """
    core_real = os.path.realpath(CORE)
    pids = []
    try:
        names = os.listdir("/proc")
    except Exception:
        return pids
    for name in names:
        if not name.isdigit():
            continue
        try:
            exe = os.readlink("/proc/%s/exe" % name)
        except Exception:
            continue
        if exe == core_real or exe == core_real + " (deleted)":
            pids.append(name)
    return pids


def kill_core():
    pids = find_core_pids()
    for pid in pids:
        try:
            os.kill(int(pid), 15)
        except Exception:
            pass
    for _ in range(20):
        if not find_core_pids():
            return True
        time.sleep(0.5)
    for pid in find_core_pids():
        try:
            os.kill(int(pid), 9)
        except Exception:
            pass
    time.sleep(1)
    return not find_core_pids()


def restart_core():
    """重启本目录下的 mihomo。"""
    if not os.path.exists(CORE):
        log("  ! 未找到内核 %s，跳过重启" % CORE)
        return False

    if not kill_core():
        log("  ! 旧内核未能退出，请手动清理后重试")
        return False

    logf = open(os.path.join(BASE_DIR, "mihomo.log"), "ab")
    subprocess.Popen(
        [CORE, "-d", BASE_DIR],
        stdout=logf, stderr=logf, stdin=subprocess.DEVNULL,
        start_new_session=True, close_fds=True,
    )
    time.sleep(4)

    pids = find_core_pids()
    if len(pids) == 1:
        log("  内核已重启，PID: %s" % pids[0])
        return True
    if len(pids) > 1:
        log("  ! 检测到多个内核实例 %s" % ",".join(pids))
        return False
    log("  ! 内核重启失败，请查看 %s/mihomo.log" % BASE_DIR)
    return False



def write_atomic(path, content):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    os.replace(tmp, path)


# -------------------------------------------------------------------- 主流程 ----

def main():
    dry_run = "--dry-run" in sys.argv

    for d in (WORKDIR,):
        if not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)

    log("[1/4] 下载订阅（按 mihomo UA + 多 IP 探测）...")
    try:
        raw = download_subscription()
    except Exception as exc:
        log("")
        log("错误：%s" % exc)
        return 1

    with open(RAW_YAML, "w", encoding="utf-8", newline="\n") as f:
        f.write(raw)
    log("  原始配置已存: %s" % RAW_YAML)

    log("")
    log("[2/4] 检查订阅内容...")
    total, types = count_nodes(raw)
    if total == 0 or not types:
        log("错误：订阅里没有解析到任何节点，疑似返回了错误页。")
        log("原始内容前 200 字节：%r" % raw[:200])
        return 1
    log("  节点总数 %d，类型分布: %s" % (
        total, ", ".join("%s×%d" % (k, v) for k, v in sorted(types.items()))
    ))

    log("")
    log("[3/4] 注入本机参数并做内核校验...")
    merged = patch_config(raw)

    auto = AUTO_SELECT
    if "--auto-select" in sys.argv:
        auto = True
    if "--manual-select" in sys.argv:
        auto = False
    if auto:
        merged = ensure_auto_group(merged)
    log("  节点选择方式: %s" % ("url-test 自动择优 + 自动切换" if auto
                             else "手动 select（默认选中第一个节点，除非 cache.db 有记录）"))

    cand = os.path.join(WORKDIR, "config.candidate.yaml")
    write_atomic(cand, merged)

    ok, out = validate_with_core(cand)
    tail = "\n".join([ln for ln in out.splitlines() if ln.strip()][-3:])
    if not ok:
        log("  内核校验失败，已保留线上旧配置未做替换：")
        log("  " + tail)
        log("  候选文件: %s" % cand)
        return 1
    log("  内核校验通过")

    if dry_run:
        log("")
        log("--dry-run 模式：不写 %s" % TARGET_CFG)
        log("候选配置: %s" % cand)
        return 0

    log("")
    log("[4/4] 备份并安装...")
    bak = backup_current()
    if bak:
        log("  旧配置备份: %s" % bak)
    write_atomic(TARGET_CFG, merged)
    log("  已写入: %s" % TARGET_CFG)

    if "--restart" in sys.argv:
        log("")
        log("重启内核使新配置生效...")
        if restart_core():
            picker = os.path.join(BASE_DIR, "pick-node.py")
            if os.path.exists(picker) and "--no-probe" not in sys.argv:
                log("")
                log("启动测速（一次性）...")
                subprocess.call([sys.executable, picker, "--rounds", "2", "--top", "3"])
    else:
        log("")
        log("完成。若内核正在运行，需要重启才能生效：")
        log("  python3 update-mihomo-sub.py --restart    # 或手动执行：")
        log("  pkill -f 'mihomo -d' ; nohup %s -d %s > %s/mihomo.log 2>&1 &"
            % (CORE, BASE_DIR, BASE_DIR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
