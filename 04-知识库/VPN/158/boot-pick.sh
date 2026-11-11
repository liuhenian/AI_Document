#!/bin/bash
# boot-pick.sh —— 开机后一次性测速选节点（由 mihomo-pick.service 调用）
# 与 start-vpn.sh 的区别：这里不负责启动内核（交给 systemd），只等控制端口就绪后测速。

BASE_DIR=/home/u/VPN
API=http://127.0.0.1:9090
PICKER=$BASE_DIR/pick-node.py
# --verify 3：切过去后用真实请求复核，不通顺延下一个候选
# --retry 3 ：整组测速 0 可用时重测，避免开机瞬间网络没就绪就把节点判死
PICK_ARGS="--rounds 2 --top 3 --always-switch --verify 3 --retry 3"

cd "$BASE_DIR" || exit 1

# 等控制端口就绪（最多 60s）。/version 未带 secret 会返回 401，
# 只要 curl 能连上就说明 API 已监听，所以不加 --fail。
for _ in $(seq 1 30); do
    if curl -s -o /dev/null -m 2 "$API/version"; then
        break
    fi
    sleep 2
done

sleep 1
echo "[boot-pick] $(date '+%F %T') 开始启动测速"

if [ ! -f "$PICKER" ]; then
    echo "[boot-pick] 未找到 $PICKER，跳过"
    exit 0
fi

python3 "$PICKER" $PICK_ARGS
rc=$?

echo -n "[boot-pick] 连通性："
CODE=$(curl -s -o /dev/null -w "%{http_code}" -x http://127.0.0.1:7890 --max-time 15 \
       "https://www.gstatic.com/generate_204")
if [ "$CODE" = "204" ]; then
    echo "OK (http 204)"
else
    echo "异常 (http $CODE)"
fi

exit $rc
