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
    python3 pick-node.py                 # 测速并选中最快节点
    python3 pick-node.py --dry-run       # 只测速打印排名，不改变选择
    python3 pick-node.py --top 10        # 打印前 10 名
    python3 pick-node.py --timeout 2000  # 单节点测速超时（毫秒）
    python3 pick-node.py --rounds 2      # 测两轮取每节点最小值，抗抖动（+约 3 秒）
    python3 pick-node.py --always-switch # 只要不是最快就切，忽略 100ms 容差
"""

import http.client
import json
import os
import re
import sys
import time
import urllib.parse

BASE_DIR = "/mnt/disk/henian/vpn"
CFG = os.path.join(BASE_DIR, "config.yaml")

TEST_URL = "http://www.gstatic.com/generate_204"
TEST_TIMEOUT_MS = 3000
TOP_N = 5
MIN_IMPROVE_MS = 0          # 0 = 只要最快就切
WARN_DELAY_MS = 2000        # 最快节点也慢于此值时给出提示
ROUNDS = 1                  # 测速轮数，多轮取最小值，降低并发测速的抖动误差
KEEP_TOLERANCE_MS = 100     # 当前节点比最快慢不超过该值时保持不动，避免噪声导致来回切


def log(msg=""):
    print(msg, flush=True)


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


# -------------------------------------------------------------------- 主流程 ----

def main():
    dry_run = "--dry-run" in sys.argv
    global TEST_TIMEOUT_MS, TOP_N, MIN_IMPROVE_MS, ROUNDS, KEEP_TOLERANCE_MS

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

    host, port, secret = read_api_endpoint(CFG)
    api = Api(host, port, secret)

    try:
        group, ginfo = pick_group(api, CFG)
    except Exception as exc:
        log("错误：%s" % exc)
        return 1

    all_nodes = ginfo.get("all") or []
    current = ginfo.get("now") or "(未选)"

    log("策略组: %s（类型 %s，共 %d 个节点）" % (group, ginfo.get("type"), len(all_nodes)))
    log("当前节点: %s" % current)
    if ginfo.get("type") == "URLTest":
        log("提示：该组是 url-test，内核仍会按 interval 周期探测；"
            "若只想启动测一次，请用 update-mihomo-sub.py --manual-select 重建配置。")
    log("")
    log("开始测速（一次性，单节点超时 %dms%s）..."
        % (TEST_TIMEOUT_MS, "，%d 轮取最优" % ROUNDS if ROUNDS > 1 else ""))

    t0 = time.time()
    delays = {}
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

    if not delays:
        log("错误：没有任何节点测速成功，保留当前选择（%s）" % current)
        return 1

    ranked = sorted(delays.items(), key=lambda kv: kv[1])
    log("测速完成，耗时 %.1fs；可用 %d/%d 个节点" % (cost, len(ranked), len(all_nodes)))
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
        log("注意：最快的节点也慢于 %dms，可能是线路整体拥塞或订阅到期。" % WARN_DELAY_MS)

    if dry_run:
        log("")
        log("--dry-run：不改变当前选择")
        return 0

    if best_name == current:
        log("当前已是最快节点，无需切换。")
        return 0

    if cur_delay and KEEP_TOLERANCE_MS >= 0 \
            and (cur_delay - best_delay) <= KEEP_TOLERANCE_MS:
        log("当前节点只比最快慢 %dms（容差 %dms 内），保持不变，避免来回抖动。"
            % (cur_delay - best_delay, KEEP_TOLERANCE_MS))
        return 0

    if cur_delay and MIN_IMPROVE_MS > 0 and (cur_delay - best_delay) < MIN_IMPROVE_MS:
        log("当前节点领先不足 %dms，保持不变。" % MIN_IMPROVE_MS)
        return 0

    st, body = api.put("/proxies/%s" % urllib.parse.quote(group, safe=""),
                       {"name": best_name})
    if st not in (200, 204):
        log("切换失败：HTTP %s %s" % (st, body[:200]))
        return 1

    st, body = api.get("/proxies/%s" % urllib.parse.quote(group, safe=""), timeout=10)
    now = json.loads(body.decode("utf-8")).get("now") if st == 200 else best_name
    log("已切换到: %s" % now)
    return 0


if __name__ == "__main__":
    sys.exit(main())
