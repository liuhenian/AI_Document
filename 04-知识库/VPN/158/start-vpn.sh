#!/bin/bash
# start-vpn.sh —— 一键启动并选节点
#   保证内核在跑（systemd 托管时走 systemctl）→ 测速 → 选延迟最低且复核通过的节点 → 打印状态
#
# 用法:
#   sudo bash /home/u/VPN/start-vpn.sh              # 已运行则不动，只测速选节点
#   sudo bash /home/u/VPN/start-vpn.sh --restart    # 先重启内核，再测速选节点
#   sudo bash /home/u/VPN/start-vpn.sh --no-probe   # 只保证跑起来，不测速不换节点

BASE_DIR=/home/u/VPN
CORE=$BASE_DIR/mihomo
CFG=$BASE_DIR/config.yaml
LOG=$BASE_DIR/mihomo.log
API=http://127.0.0.1:9090
SECRET=123456
PICKER=$BASE_DIR/pick-node.py
SYSTEMD_UNIT=mihomo.service

# --rounds 2        两轮取每节点最小值（单轮并发测速噪声可达 400ms）
# --always-switch   启动时没有业务流量，直接选最快，不保留 100ms 容差
# --verify 3        切过去后用真实请求复核，不通就顺延到下一个候选
# --retry 3         整组测速一个可用节点都没有时重测 3 次
PICK_ARGS="--rounds 2 --top 3 --always-switch --verify 3 --retry 3"

PROBE=1
FORCE_RESTART=0
for a in "$@"; do
    case "$a" in
        --no-probe) PROBE=0 ;;
        --restart)  FORCE_RESTART=1 ;;
    esac
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

use_systemd() {
    command -v systemctl >/dev/null 2>&1 || return 1
    systemctl is-enabled --quiet "$SYSTEMD_UNIT" 2>/dev/null
}

# 等控制端口就绪（最多 60s）
wait_api() {
    local i
    for i in $(seq 1 30); do
        curl -s -o /dev/null -m 2 "$API/version" && return 0
        sleep 2
    done
    return 1
}

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

# ---------------------------------------------------------------- 保证内核在跑 ----
if use_systemd; then
    if [ "$FORCE_RESTART" = "1" ]; then
        echo "重启内核（systemd: $SYSTEMD_UNIT）..."
        systemctl restart "$SYSTEMD_UNIT" || { echo "重启失败，见 journalctl -u $SYSTEMD_UNIT"; exit 1; }
    elif systemctl is-active --quiet "$SYSTEMD_UNIT"; then
        echo "内核已在运行（systemd 托管，PID $(systemctl show -p MainPID --value "$SYSTEMD_UNIT")）"
    else
        echo "启动内核（systemd: $SYSTEMD_UNIT）..."
        systemctl start "$SYSTEMD_UNIT" || { echo "启动失败，见 journalctl -u $SYSTEMD_UNIT"; exit 1; }
    fi
    wait_api || { echo "控制接口 60s 内未就绪，见 journalctl -u $SYSTEMD_UNIT"; exit 1; }
else
    # 未装 systemd 单元时回退到手工方式（旧机器 / 测试环境）
    RUNNING=$(core_pids)
    if [ -n "$RUNNING" ]; then
        echo "mihomo 已在运行，PID:$RUNNING"
    else
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
    fi
fi

echo "监听端口："
ss -lntp 2>/dev/null | grep -E ":(7890|9090|1053)" | awk '{print "  "$4}'

# ------------------------------------------------------- 测速 → 选最低延迟节点 ----
if [ "$PROBE" = "1" ]; then
    if [ -f "$PICKER" ]; then
        echo
        echo "启动测速（测速 → 选延迟最低 → 真实复核，约 8 秒）..."
        python3 "$PICKER" $PICK_ARGS
        PICK_RC=$?
        if [ $PICK_RC -ne 0 ]; then
            echo "  没能找到复核可用的节点（退出码 $PICK_RC），沿用当前选择"
        fi
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

[ "$PROBE" = "1" ] && [ "${PICK_RC:-0}" -ne 0 ] && exit 1
exit 0
