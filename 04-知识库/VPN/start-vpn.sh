#!/bin/bash
# start-vpn.sh —— 启动 mihomo 内核（幂等：已在运行则不重复启动）
# 用法: sudo bash /mnt/disk/henian/vpn/start-vpn.sh
#       sudo bash /mnt/disk/henian/vpn/start-vpn.sh --no-probe   # 跳过启动测速

BASE_DIR=/mnt/disk/henian/vpn
CORE=$BASE_DIR/mihomo
CFG=$BASE_DIR/config.yaml
LOG=$BASE_DIR/mihomo.log
API=http://127.0.0.1:9090
SECRET=123456
PICKER=$BASE_DIR/pick-node.py
# 两轮取最优：单轮并发测速噪声较大（实测同一节点两次可差 400ms 以上）
# --always-switch：启动时还没有业务流量，直接选最快，不必保留 100ms 容差
PICK_ARGS="--rounds 2 --top 3 --always-switch"

PROBE=1
for a in "$@"; do
    [ "$a" = "--no-probe" ] && PROBE=0
done

cd "$BASE_DIR" || exit 1

# 按 /proc/<pid>/exe 指向的真实文件识别进程，
# 避免 pgrep -f 把命令行里含相同字符串的其它 shell 也算进来
core_pids() {
    local out=""
    for p in /proc/[0-9]*; do
        local pid=${p#/proc/}
        local exe
        exe=$(readlink "/proc/$pid/exe" 2>/dev/null) || continue
        [ "$exe" = "$CORE" ] && out="$out $pid"
    done
    echo $out
}

# 打印策略组与当前选中节点（本脚本不选节点，这里只是把内核的选择结果show出来）
show_groups() {
    curl -s -H "Authorization: Bearer $SECRET" --max-time 8 "$API/proxies" \
    | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)['proxies']
except Exception:
    print('  (控制接口不可用，无法读取策略组)'); raise SystemExit
rows = [(k, v) for k, v in d.items()
        if v.get('type') in ('Selector', 'URLTest', 'Fallback', 'LoadBalance')]
if not rows:
    print('  (无策略组)')
for k, v in rows:
    print('  %-10s %-9s -> %s' % (k, v.get('type'), v.get('now')))
"
}

if [ ! -x "$CORE" ]; then
    echo "错误：未找到内核 $CORE"
    exit 1
fi
if [ ! -f "$CFG" ]; then
    echo "错误：未找到配置 $CFG，请先执行 python3 update-mihomo-sub.py"
    exit 1
fi

RUNNING=$(core_pids)
if [ -n "$RUNNING" ]; then
    echo "mihomo 已在运行，PID:$RUNNING"
    echo "策略组与当前节点："
    show_groups
    echo
    echo "需要重新测速选节点：python3 $PICKER"
    exit 0
fi

echo "校验配置..."
if ! "$CORE" -t -d "$BASE_DIR" > /tmp/mihomo-check.log 2>&1; then
    echo "配置校验失败："
    tail -5 /tmp/mihomo-check.log
    exit 1
fi
echo "  校验通过"

echo "启动 mihomo..."
setsid nohup "$CORE" -d "$BASE_DIR" >> "$LOG" 2>&1 < /dev/null &
sleep 5

RUNNING=$(core_pids)
if [ -z "$RUNNING" ]; then
    echo "启动失败，日志末尾："
    tail -15 "$LOG"
    exit 1
fi

echo "已启动，PID:$RUNNING"
echo "监听端口："
ss -lntp 2>/dev/null | grep -E ":(7890|9090|1053)" | awk '{print "  "$4}'

# 启动时一次性测速选最快节点；运行期间内核不做任何周期性探测
if [ "$PROBE" = "1" ]; then
    if [ -f "$PICKER" ]; then
        echo
        echo "启动测速（一次性，约 6 秒）..."
        python3 "$PICKER" $PICK_ARGS || echo "  测速失败，沿用上次选择"
    else
        echo "未找到 $PICKER，跳过启动测速"
    fi
fi

echo -n "连通性测试："
CODE=$(curl -s -o /dev/null -w "%{http_code}" -x http://127.0.0.1:7890 --max-time 15 \
       "https://www.gstatic.com/generate_204")
if [ "$CODE" = "204" ]; then
    echo "OK (http 204)"
else
    echo "异常 (http $CODE)，请检查节点是否可用 / 订阅是否过期"
fi

echo "策略组与当前节点："
show_groups
