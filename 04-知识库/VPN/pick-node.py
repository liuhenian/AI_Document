#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pick-node.py —— 启动时一次性测速并选中最快节点（不做后台定期探测）

设计取舍
--------------------------------------------------------------------------------
· 不生成 url-test 组：url-test 会让内核每隔 interval 秒对全部节点做一次健康检查，
  常态下有持续的探测流量。这里改成「只在启动时测一次，然后把结果钉死在 select 组里」，
  运行期间内核不再发起任何探测。
· 一次 API 调用测完整组：`GET /group/<组名>/delay` 是内核内并发测速，
  73 个节点约 3 秒返回，比逐个节点发 73 次请求快且省。
· 测完立即 `PUT /proxies/<组名>` 选中，选择结果由内核写入 cache.db 持久化。

用法
--------------------------------------------------------------------------------
    python3 pick-node.py                 # 测速 → 选延迟最低 → 真实复核 → 落到该节点
    python3 pick-node.py --dry-run       # 只测速打印排名，不切换、不复核
    python3 pick-node.py --top 10        # 打印前 10 名
    python3 pick-node.py --timeout 2000  # 单节点测速超时（毫秒）
    python3 pick-node.py --rounds 2      # 测两轮取每节点最小值，抗抖动（+约 3 秒）
    python3 pick-node.py --always-switch # 只要不是最快就切，忽略 100ms 容差
    python3 pick-node.py --verify 3      # 切换后最多复核 3 个候选（默认 3，0 = 关闭复核）
    python3 pick-node.py --retry 3       # 整组测速 0 可用时的重测次数（默认 3）
    python3 pick-node.py --retry-delay 3 # 两次重测间隔秒数（默认 3）
    python3 pick-node.py --outer-rounds 2 # 候选全部复核不通时整组重测轮数（默认 2）

「测不通就再测一次」的两层含义
--------------------------------------------------------------------------------
1) 整组测速一个可用节点都没有 → 间隔 RETRY_DELAY_S 秒重测，最多 RETRY 次；
2) 候选节点切过去之后用真实请求复核（curl 走本机 7890 访问 generate_204），
   不通就顺延到延迟排名里的下一个候选，最多 VERIFY_N 个；
   全部候选都不通 → 整组重测，最多 OUTER_ROUNDS 轮。
这样「最快」不只是测速接口的快，而是「实测能通」的最快。
"""

import http.client
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

BASE_DIR = "/home/u/VPN"
CFG = os.path.join(BASE_DIR, "config.yaml")

TEST_URL = "http://www.gstatic.com/generate_204"
TEST_TIMEOUT_MS = 3000

# 切换后用真实请求复核（测速接口说通、实际连不通的情况在拥塞线路上确实存在）
VERIFY_URL = "https://www.gstatic.com/generate_204"
VERIFY_TIMEOUT_S = 8
VERIFY_N = 3                # 依次实测的候选个数，0 = 关闭实测（退回旧行为）
RETRY = 3                   # 整组测速 0 可用时的重试次数（含首次）
RETRY_DELAY_S = 3           # 两次重测之间的间隔
OUTER_ROUNDS = 2            # 候选全部实测不通时，整组重测的轮数

# 机场会把「套餐到期 / 已用流量」这类信息行也做成节点下发（实测 Flybit 59 个节点里混了 2 个），
# 它们能测通，会抢到第一名，但语义上不是给用户用的节点，必须排除。
INFO_NODE_KEYWORDS = ("到期", "已用", "总共", "重置", "剩余", "流量",
                      "套餐", "过期", "官网", "订阅", "客服", "群组")

TOP_N = 5
MIN_IMPROVE_MS = 0          # 0 = 只要最快就切
WARN_DELAY_MS = 2000        # 最快节点也慢于此值时给出提示
ROUNDS = 1                  # 测速轮数，多轮取最小值，降低并发测速的抖动误差
KEEP_TOLERANCE_MS = 100     # 当前节点比最快慢不超过该值时保持不动，避免噪声导致来回切


def log(msg=""):
    print(msg, flush=True)


def is_info_node(name):
    """判断是否为机场下发的信息展示行（非真实节点）。"""
    return any(k in name for k in INFO_NODE_KEYWORDS)


# ---------------------------------------------------------------- 读取配置 ----

def read_api_endpoint(cfg_path):
    """从 config.yaml 读 external-controller 与 secret，避免脚本里重复硬编码。"""
    host, port, secret = "127.0.0.1", 9090, ""
    if not os.path.exists(cfg_path):
        return host, port, secret
    with open(cfg_path, "r", encoding="utf-8", errors="replace") as f:
        for ln in f:
            m = re.match(r"^external-controller:\s*(.+?)\s*$", ln)
            if m:
                val = m.group(1).strip().strip("'\"")
                if ":" in val:
                    h, p = val.rsplit(":", 1)
                    host = "127.0.0.1" if h in ("0.0.0.0", "*", "") else h
                    try:
                        port = int(p)
                    except ValueError:
                        pass
                continue
            m = re.match(r"^secret:\s*(.+?)\s*$", ln)
            if m:
                secret = m.group(1).strip().strip("'\"")
    return host, port, secret


def read_local_port(cfg_path, default=7890):
    """读 mixed-port，用于切换后的真实连通性复核。"""
    if not os.path.exists(cfg_path):
        return default
    with open(cfg_path, "r", encoding="utf-8", errors="replace") as f:
        for ln in f:
            m = re.match(r"^mixed-port:\s*(\d+)", ln)
            if m:
                return int(m.group(1))
    return default


# ---------------------------------------------------------------- API 客户端 ----

class Api(object):
    def __init__(self, host, port, secret):
        self.host = host
        self.port = port
        self.headers = {"Content-Type": "application/json"}
        if secret:
            self.headers["Authorization"] = "Bearer " + secret

    def _conn(self, timeout):
        return http.client.HTTPConnection(self.host, self.port, timeout=timeout)

    def get(self, path, timeout=120):
        c = self._conn(timeout)
        try:
            c.request("GET", path, headers=self.headers)
            r = c.getresponse()
            return r.status, r.read()
        finally:
            c.close()

    def put(self, path, payload, timeout=15):
        c = self._conn(timeout)
        try:
            c.request("PUT", path, body=json.dumps(payload), headers=self.headers)
            r = c.getresponse()
            return r.status, r.read()
        finally:
            c.close()


# ---------------------------------------------------------------- 选组逻辑 ----

def pick_group(api, cfg_path):
    """优先用 MATCH 规则指向的组；否则取第一个非 GLOBAL 的 Selector 组。"""
    match_target = None
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8", errors="replace") as f:
            for ln in f:
                m = re.search(r"^\s*-\s*'?MATCH,([^'\s]+)", ln)
                if m:
                    match_target = m.group(1)

    st, body = api.get("/proxies", timeout=15)
    if st != 200:
        raise RuntimeError("读取 /proxies 失败：HTTP %s" % st)
    proxies = json.loads(body.decode("utf-8"))["proxies"]

    if match_target and match_target in proxies:
        v = proxies[match_target]
        if v.get("type") in ("Selector", "URLTest", "Fallback", "LoadBalance"):
            return match_target, v

    for name, v in proxies.items():
        if name == "GLOBAL":
            continue
        if v.get("type") == "Selector":
            return name, v
    raise RuntimeError("没有找到可用的策略组（Selector）")


# ---------------------------------------------------------------- 测速逻辑 ----

def probe_group(api, group):
    """一次调用测完整组，返回 {节点名: 延迟ms}。"""
    q = urllib.parse.urlencode({"url": TEST_URL, "timeout": TEST_TIMEOUT_MS})
    path = "/group/%s/delay?%s" % (urllib.parse.quote(group, safe=""), q)
    st, body = api.get(path, timeout=TEST_TIMEOUT_MS / 1000.0 + 40)
    if st != 200:
        raise RuntimeError("整组测速失败：HTTP %s %s" % (st, body[:120]))
    raw = json.loads(body.decode("utf-8"))
    return {k: v for k, v in raw.items() if isinstance(v, int) and v > 0}


def probe_individually(api, names):
    """整组接口不可用时的兜底：并发逐节点测速。"""
    from concurrent.futures import ThreadPoolExecutor

    def one(name):
        q = urllib.parse.urlencode({"url": TEST_URL, "timeout": TEST_TIMEOUT_MS})
        path = "/proxies/%s/delay?%s" % (urllib.parse.quote(name, safe=""), q)
        try:
            st, body = api.get(path, timeout=TEST_TIMEOUT_MS / 1000.0 + 10)
            if st != 200:
                return name, None
            d = json.loads(body.decode("utf-8")).get("delay", 0)
            return name, (d if isinstance(d, int) and d > 0 else None)
        except Exception:
            return name, None

    out = {}
    with ThreadPoolExecutor(max_workers=16) as ex:
        for name, d in ex.map(one, names):
            if d:
                out[name] = d
    return out


# ------------------------------------------------------------ 切换与真实复核 ----

def switch_to(api, group, name):
    st, body = api.put("/proxies/%s" % urllib.parse.quote(group, safe=""),
                       {"name": name})
    if st not in (200, 204):
        log("      切换失败：HTTP %s %s" % (st, body[:120]))
        return False
    return True


def verify_via_proxy(port, timeout=VERIFY_TIMEOUT_S):
    """通过本机代理口发一次真实请求，判断当前选中的节点是否真的可用。

    测速接口（/group/<name>/delay）与真实流量走的是同一条出站链路，
    但拥塞时的线路常出现「探测小包能过、实际请求超时」，所以切完必须复核一次。
    """
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "-x", "http://127.0.0.1:%d" % port, "--max-time", str(timeout),
             VERIFY_URL],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        log("      未找到 curl，跳过真实复核")
        return True          # 没有复核手段时按通处理，避免把功能卡死
    except Exception:
        return False
    code = r.stdout.decode("utf-8", "replace").strip()
    return code == "204"


def probe_with_retry(api, group, all_nodes):
    """整组测速，一轮下来 0 个可用就再测一次（机场偶发全超时很常见）。"""
    for attempt in range(1, RETRY + 1):
        delays = {}
        t0 = time.time()
        for r in range(ROUNDS):
            try:
                one = probe_group(api, group)
            except Exception as exc:
                log("  第 %d 轮整组接口失败（%s），改用逐节点并发测速" % (r + 1, exc))
                one = probe_individually(api, all_nodes)
            for name, d in one.items():
                if name not in delays or d < delays[name]:
                    delays[name] = d
            if r + 1 < ROUNDS:
                log("  第 %d/%d 轮完成" % (r + 1, ROUNDS))
        cost = time.time() - t0
        # 整组测速会把信息节点也测出来，这里统一剔除，避免被选为「最快」
        delays = {k: v for k, v in delays.items() if not is_info_node(k)}
        if delays:
            return delays, cost
        if attempt < RETRY:
            log("  本轮没有任何可用节点，%ds 后重测（第 %d/%d 次）..."
                % (RETRY_DELAY_S, attempt + 1, RETRY))
            time.sleep(RETRY_DELAY_S)
    return {}, 0.0


# -------------------------------------------------------------------- 主流程 ----

def main():
    dry_run = "--dry-run" in sys.argv
    global TEST_TIMEOUT_MS, TOP_N, MIN_IMPROVE_MS, ROUNDS, KEEP_TOLERANCE_MS
    global VERIFY_N, VERIFY_TIMEOUT_S, RETRY, RETRY_DELAY_S, OUTER_ROUNDS

    if "--timeout" in sys.argv:
        TEST_TIMEOUT_MS = int(sys.argv[sys.argv.index("--timeout") + 1])
    if "--top" in sys.argv:
        TOP_N = int(sys.argv[sys.argv.index("--top") + 1])
    if "--min-improve" in sys.argv:
        MIN_IMPROVE_MS = int(sys.argv[sys.argv.index("--min-improve") + 1])
    if "--rounds" in sys.argv:
        ROUNDS = max(1, int(sys.argv[sys.argv.index("--rounds") + 1]))
    if "--keep-tolerance" in sys.argv:
        KEEP_TOLERANCE_MS = int(sys.argv[sys.argv.index("--keep-tolerance") + 1])
    if "--always-switch" in sys.argv:
        KEEP_TOLERANCE_MS = -1
    if "--verify" in sys.argv:
        VERIFY_N = max(0, int(sys.argv[sys.argv.index("--verify") + 1]))
    if "--verify-timeout" in sys.argv:
        VERIFY_TIMEOUT_S = max(1, int(sys.argv[sys.argv.index("--verify-timeout") + 1]))
    if "--retry" in sys.argv:
        RETRY = max(1, int(sys.argv[sys.argv.index("--retry") + 1]))
    if "--retry-delay" in sys.argv:
        RETRY_DELAY_S = max(0, int(sys.argv[sys.argv.index("--retry-delay") + 1]))
    if "--outer-rounds" in sys.argv:
        OUTER_ROUNDS = max(1, int(sys.argv[sys.argv.index("--outer-rounds") + 1]))

    host, port, secret = read_api_endpoint(CFG)
    api = Api(host, port, secret)

    try:
        group, ginfo = pick_group(api, CFG)
    except Exception as exc:
        log("错误：%s" % exc)
        return 1

    raw_nodes = ginfo.get("all") or []
    all_nodes = [n for n in raw_nodes if not is_info_node(n)]
    skipped = len(raw_nodes) - len(all_nodes)
    current = ginfo.get("now") or "(未选)"

    log("策略组: %s（类型 %s，真实节点 %d 个%s）"
        % (group, ginfo.get("type"), len(all_nodes),
           "，已排除 %d 个信息节点" % skipped if skipped else ""))
    log("当前节点: %s" % current)
    if skipped and is_info_node(current):
        log("提示：当前落在机场的信息节点上，本次会切到真实节点。")
    if ginfo.get("type") == "URLTest":
        log("提示：该组是 url-test，内核仍会按 interval 周期探测；"
            "若只想启动测一次，请用 update-mihomo-sub.py --manual-select 重建配置。")
    log("")
    log("开始测速（一次性，单节点超时 %dms%s）..."
        % (TEST_TIMEOUT_MS, "，%d 轮取最优" % ROUNDS if ROUNDS > 1 else ""))

    port = read_local_port(CFG)
    chosen = None

    for outer in range(1, OUTER_ROUNDS + 1):
        if outer > 1:
            log("")
            log("第 %d 轮整组重测（上一轮候选复核都不通）..." % outer)

        delays, cost = probe_with_retry(api, group, all_nodes)
        if not delays:
            log("错误：连续 %d 次测速都没有可用节点，保留当前选择（%s）"
                % (RETRY, current))
            return 1

        ranked = sorted(delays.items(), key=lambda kv: kv[1])
        log("测速完成，耗时 %.1fs；可用 %d/%d 个节点"
            % (cost, len(ranked), len(all_nodes)))
        log("")
        log("延迟排名（前 %d）：" % min(TOP_N, len(ranked)))
        for i, (name, d) in enumerate(ranked[:TOP_N], 1):
            flag = "  <- 当前" if name == current else ""
            log("  %2d. %5dms  %s%s" % (i, d, name, flag))

        best_name, best_delay = ranked[0]
        cur_delay = delays.get(current)
        log("")
        log("最快: %s (%dms)" % (best_name, best_delay))
        if cur_delay:
            log("当前: %s (%dms)" % (current, cur_delay))
        if best_delay > WARN_DELAY_MS:
            log("注意：最快的节点也慢于 %dms，可能是线路整体拥塞或订阅到期。"
                % WARN_DELAY_MS)

        if dry_run:
            log("")
            log("--dry-run：只测速，不切换、不复核")
            return 0

        # 1) 当前节点已在最快附近（容差/最小提升内）时优先保留，但必须复核通过
        keep_current = False
        if cur_delay is not None:
            gap = cur_delay - best_delay
            if KEEP_TOLERANCE_MS >= 0 and gap <= KEEP_TOLERANCE_MS:
                keep_current = True
                reason = "差 %dms ≤ 容差 %dms" % (gap, KEEP_TOLERANCE_MS)
            elif MIN_IMPROVE_MS > 0 and gap < MIN_IMPROVE_MS:
                keep_current = True
                reason = "提升不足 %dms" % MIN_IMPROVE_MS

        if keep_current:
            log("")
            log("当前节点在最快附近（%s），先复核它..." % reason)
            if verify_via_proxy(port):
                log("  复核通过，保持当前节点 %s。" % current)
                return 0
            log("  复核不通，改为在候选中挑选。")

        # 2) 按延迟从低到高逐个切换 + 真实复核，第一个通的即为结果
        if VERIFY_N > 0:
            candidates = ranked[:VERIFY_N]
        else:
            candidates = ranked[:1]

        log("")
        log("按延迟从低到高验证候选（最多 %d 个）..." % len(candidates))
        for idx, (name, d) in enumerate(candidates, 1):
            log("  [%d/%d] %s (%dms)" % (idx, len(candidates), name, d))
            if name != current:
                if not switch_to(api, group, name):
                    continue
                log("      已切换，复核连通性...")
            else:
                log("      已是当前节点，复核连通性...")

            if VERIFY_N == 0:
                chosen = (name, d)
                break
            if verify_via_proxy(port):
                log("      复核通过")
                chosen = (name, d)
                break
            log("      复核不通，看下一个候选")

        if chosen:
            break
        log("")
        log("本轮 %d 个候选复核都不通。" % len(candidates))

    if not chosen:
        log("错误：连续 %d 轮（每轮最多 %d 个候选）都没找到复核可用的节点。"
            % (OUTER_ROUNDS, max(VERIFY_N, 1)))
        log("  可能订阅已到期或线路整体被封，当前选择保持 %s。" % current)
        return 1

    chosen_name, chosen_delay = chosen
    st, body = api.get("/proxies/%s" % urllib.parse.quote(group, safe=""), timeout=10)
    now = json.loads(body.decode("utf-8")).get("now") if st == 200 else chosen_name
    log("")
    log("已选定：%s（%dms）" % (chosen_name, chosen_delay))
    if now != chosen_name:
        log("  注意：内核当前显示为 %s，与期望不一致，请检查" % now)
    return 0


if __name__ == "__main__":
    sys.exit(main())
