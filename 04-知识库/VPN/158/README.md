# VPN 使用说明（10.104.11.158）

本目录为 mihomo 代理（Mihomo Meta v1.19.33，linux-amd64-compatible）的全部文件，路径 `/home/u/VPN`。
内核已由 systemd（system and service manager，系统与服务管理器）托管，**开机自动启动**，无需手工拉起。

## 一、目录内容

| 文件 | 作用 |
|---|---|
| `mihomo` | 内核二进制 |
| `config.yaml` | 由订阅生成的运行配置，**不要手改**，下次更新会被覆盖 |
| `update-mihomo-sub.py` | 下载订阅 → 注入本机参数 → 内核校验 → 原子替换 config.yaml |
| `pick-node.py` | 测速 → 选延迟最低 → 真实复核 → 不通再顺延/重测 |
| `boot-pick.sh` | 开机后跑一次上述流程（由 `mihomo-pick.service` 调用） |
| `start-vpn.sh` | 一键入口：保证内核在跑（systemd 优先）+ 选节点 |
| `sub-work/` | 原始订阅留档、可用 IP 缓存、内核校验用的临时目录 |
| `mihomo.log` | 内核日志（systemd 也追加写这里） |
| `cache.db` | 内核状态（含上次选中的节点，重启后沿用） |
| `geoip.metadb` | GeoIP 数据库，首次运行自动下载 |

systemd 单元文件在 `/etc/systemd/system/` 下：`mihomo.service`（内核）、`mihomo-pick.service`（开机测速）。

## 二、开机自启（systemd）

两个单元的职责分得很开：`mihomo.service` 只负责把内核跑起来并守护；`mihomo-pick.service` 是一次性任务（oneshot），在内核起来后测速一次然后退出，**不做任何后台周期性探测**。

| 单元 | 类型 | 行为 |
|---|---|---|
| `mihomo.service` | simple | 启动前 `mihomo -t` 校验配置；异常退出 5 秒后自动重启；以 `u` 用户运行 |
| `mihomo-pick.service` | oneshot | 等 `9090` 控制端口就绪（最多 60 秒）→ 跑 `pick-node.py --rounds 2 --top 3 --always-switch` → 打印连通性 → 退出 |

常用命令：

```bash
# 看内核是否在跑 / 看开机自启是否开启
systemctl status mihomo.service
systemctl is-enabled mihomo.service mihomo-pick.service

# 停止 / 启动 / 重启
sudo systemctl stop mihomo.service
sudo systemctl start mihomo.service
sudo systemctl restart mihomo.service

# 重新跑一次「开机测速」流程（不重启内核）
sudo systemctl start mihomo-pick.service
journalctl -u mihomo-pick.service -b --no-pager | tail -20

# 取消开机自启（装回手工启动方式）
sudo systemctl disable --now mihomo.service mihomo-pick.service

# 内核实时日志
journalctl -u mihomo.service -f
```

### 更新订阅后怎么让它生效

```bash
cd /home/u/VPN && sudo python3 update-mihomo-sub.py --restart
```

这一条命令干完了全流程：下载新订阅 → 注入本机参数并用 `mihomo -t` 校验 → 替换 `config.yaml` →
`systemctl restart mihomo.service` 重启内核 → **一次性测速并直切最快节点** → 实测代理连通性。

| 想做的事 | 命令 |
|---|---|
| 更新 + 重启 + 测速切最快（最常用） | `sudo python3 update-mihomo-sub.py --restart` |
| 更新 + 重启，但不动当前节点 | `sudo python3 update-mihomo-sub.py --restart --no-probe` |
| 只下载和校验，不落盘 | `sudo python3 update-mihomo-sub.py --dry-run` |
| 只重启，不更新订阅 | `sudo systemctl restart mihomo.service` |

测速参数是 `--rounds 2 --top 3 --always-switch`：两轮取每节点最小值，忽略 100ms 容差直接切到最快，
与开机自启 `boot-pick.sh` 的取法完全一致。测完还会打一行 `连通性：OK (http 204)`，不用自己再验。

### 为什么不用 `start-vpn.sh` 做 ExecStart

`start-vpn.sh` 是「保证在跑 + 后台 nohup」的写法，适合人工执行；放进 systemd 会让主进程立即退出、被反复重启。
所以 systemd 直接托管 `mihomo` 二进制。

`start-vpn.sh` 现在是一键入口，会自动判断当前是否由 systemd 托管：
装了单元就走 `systemctl start/restart`，没装才回退到 kill + nohup。
它**不会**绕过 systemd 直接拉进程，所以不存在抢端口的问题。

## 三、三条常用命令

```bash
# 1) 一键启动 + 测速选最低延迟节点（已运行则不重启，只重新选节点）
sudo bash /home/u/VPN/start-vpn.sh

# 2) 更新订阅（加 --restart 会顺带重启内核 + 测速选节点）
cd /home/u/VPN && sudo python3 update-mihomo-sub.py --restart

# 3) 只重新选节点（不动内核）
sudo python3 /home/u/VPN/pick-node.py --always-switch
```

`start-vpn.sh` 的三个开关：

| 参数 | 说明 |
|---|---|
| 无参数 | 内核没跑就启动；已在跑则不动；随后一律测速选节点 |
| `--restart` | 先 `systemctl restart mihomo.service`，再测速选节点 |
| `--no-probe` | 只保证内核在跑，不测速、不换节点 |

### 选节点到底怎么选（测速 → 最低延迟 → 复核 → 不通再测）

1. **测速**：一次 `GET /group/Flybit/delay` 让内核并发测完整组，`--rounds 2` 取每节点两次中的最小值，压掉抖动。
2. **排序**：剔除机场信息节点后按延迟升序，取前 `--verify`（默认 3）个作为候选。
3. **复核**：逐个切过去，用 `curl` 走本机 7890 真实访问 `generate_204`；**204 才算通过**。
   测速接口通但实际连不通的情况在拥塞线路上确实存在，所以不只看探测值。
4. **顺延**：候选复核不通就看下一个候选，最多 `--verify` 个。
5. **重测**：候选全不通 → 整组重测（`--outer-rounds`，默认 2 轮）；
   整组一个可用节点都没有 → 间隔 `--retry-delay`（默认 3s）重测，最多 `--retry`（默认 3）次。
6. **落定**：第一个复核通过的节点即为结果，选择写入 `cache.db`，重启后沿用。

只有全部重测都失败才返回非 0 退出码（开机时会被 `SuccessExitStatus=0 1` 忽略，沿用时上次选择，不报红）。

### `pick-node.py` 选项

| 参数 | 说明 |
|---|---|
| `--dry-run` | 只测速打印排名，不切换、不复核 |
| `--top N` | 打印前 N 名（默认 5） |
| `--rounds N` | 测速轮数，取每节点最小值（默认 2，单轮噪声可达 400ms） |
| `--timeout MS` | 单节点测速超时（默认 3000） |
| `--always-switch` | 忽略容差，直接选最快（开机/启动脚本用这个） |
| `--keep-tolerance MS` | 当前节点比最快慢该值以内就保留（默认 100ms，运行中手动测速时用） |
| `--verify N` | 切换后最多复核 N 个候选，0 = 关闭复核（默认 3） |
| `--verify-timeout S` | 单次复核超时秒数（默认 8） |
| `--retry N` | 整组测速 0 可用时的重测次数（默认 3） |
| `--retry-delay S` | 两次重测间隔秒数（默认 3） |
| `--outer-rounds N` | 候选全部复核不通时整组重测轮数（默认 2） |

### 机场的「信息节点」会被自动排除

Flybit 的订阅里有 2 个伪节点，名字是「到期：2026-11-26 …，重置：…」和「已用：0.66G，总共：128.00G」。
它们是 Hysteria2 类型的真实配置，测速也能通，会抢到第一名——但它只是套餐信息展示，不是给用户用的线路。
`pick-node.py` 用关键词黑名单（到期／已用／总共／重置／剩余／流量／套餐／过期／官网／订阅／客服／群组）把它们剔除，
所以输出里会看到「真实节点 57 个，已排除 2 个信息节点」。若机场换了别的文案，往 `INFO_NODE_KEYWORDS` 里补词即可。

## 四、PC 侧怎么用

代理地址 `10.104.11.158`，端口 `7890`（混合端口，HTTP 与 SOCKS5 同一端口）。

```bat
:: Windows 命令行临时生效
set http_proxy=http://10.104.11.158:7890
set https_proxy=http://10.104.11.158:7890
```

- HTTP 代理：`http://10.104.11.158:7890`（http 和 https 目标都填这个）
- SOCKS5：`socks5h://10.104.11.158:7890`（需要 UDP 透传时只能用它）
- 控制接口：`http://10.104.11.158:9090`，`secret: 123456`（可查节点、手动切换）

验证：

```bash
curl -x http://10.104.11.158:7890 https://ipinfo.io/json
```

## 五、故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `systemctl status` 显示 failed | 配置校验没过 | `journalctl -u mihomo.service -n 50`，再跑 `python3 update-mihomo-sub.py --dry-run` |
| 服务反复重启 | `ExecStartPre` 校验失败 | 同上；修好配置后 `sudo systemctl reset-failed mihomo` 再 start |
| 连通性测试非 204 | 当前节点失效 | `sudo python3 /home/u/VPN/pick-node.py` 重新测速 |
| 全部节点不可用 | 订阅过期或整段被封 | 看节点名里的「到期：」；过期需续费 |
| PC 连不上 7890 | 防火墙/监听地址 | `ss -lnt \| grep 7890` 应显示 `*:7890` |
| 下载订阅 403 | 订阅端按 UA 拒绝 | 脚本已内置 UA 轮换，通常无需处理 |

日志：`tail -50 /home/u/VPN/mihomo.log`，或 `journalctl -u mihomo.service -n 100 --no-pager`。

## 六、需要注意的三点

1. **订阅有效期**：节点名里写着「到期：2026-11-26」，到期后需要续费。脚本**不会自动更新订阅**，
   到期前后记得手工跑一次 `update-mihomo-sub.py --restart`（也可以另配一个 systemd timer 定时更新）。
2. **文件属主**：内核现在以 `u` 用户运行（systemd 里 `User=u`），`cache.db`／`mihomo.log` 归 `u` 所有；
   用 `sudo` 手工跑脚本可能产生 root 属主文件，若出现权限问题执行 `sudo chown -R u:u /home/u/VPN`。
3. **监听范围**：`allow-lan: true` + `bind-address: '*'` + 未设置 `authentication`，
   且系统防火墙关闭 → 同网段任何机器都能直接使用 7890，9090 仅靠口令 `123456` 保护。
   如需收紧，在 `update-mihomo-sub.py` 的 `OVERRIDES` 里加
   `("authentication", '["user:pass"]')`，客户端改用 `http://user:pass@10.104.11.158:7890`。
