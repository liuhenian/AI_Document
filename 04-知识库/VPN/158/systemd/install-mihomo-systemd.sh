#!/bin/bash
# install-mihomo-systemd.sh —— 在 158 上安装 mihomo 开机自启（由 AI 一次性执行）
set -u

BASE_DIR=/home/u/VPN
UNIT_DIR=/etc/systemd/system

echo "== 1. 安装 unit 文件 =="
cp /tmp/mihomo.service /tmp/mihomo-pick.service "$UNIT_DIR"/ || exit 1
chmod 644 "$UNIT_DIR"/mihomo.service "$UNIT_DIR"/mihomo-pick.service
ls -l "$UNIT_DIR"/mihomo.service "$UNIT_DIR"/mihomo-pick.service

echo "== 2. 停掉手工启动的 mihomo 进程 =="
# 按带锚点的完整命令行匹配，避免误杀本脚本自身
pkill -f '^/home/u/VPN/mihomo -d' 2>/dev/null
for i in $(seq 1 10); do
    pgrep -f '^/home/u/VPN/mihomo -d' >/dev/null || break
    sleep 1
done
if pgrep -f '^/home/u/VPN/mihomo -d' >/dev/null; then
    echo "  仍在运行，强制结束"
    pkill -9 -f '^/home/u/VPN/mihomo -d'
    sleep 1
fi
echo "  剩余进程: $(pgrep -fc '^/home/u/VPN/mihomo -d' 2>/dev/null || echo 0)"

echo "== 3. 修正数据文件属主（此前由 root 启动过）=="
chown -R u:u "$BASE_DIR"
chown u:u "$BASE_DIR"/mihomo.log 2>/dev/null

echo "== 4. 加载并设为开机自启 =="
systemctl daemon-reload
systemctl enable mihomo.service mihomo-pick.service 2>&1 | sed 's/^/  /'

echo "== 5. 立即启动 =="
systemctl start mihomo.service
sleep 3
systemctl is-active mihomo.service
ss -lntp 2>/dev/null | grep -E ':(7890|9090|1053)' | awk '{print "  "$4}'
