# mihomo VPN 使用文档

> 服务器：`10.104.11.253`（用户 `u`，提权用 `root`）
> 安装目录：`/mnt/disk/henian/vpn`
> 最后验证：2026-10-26，出口 IP `35.187.250.161`（新加坡），google/youtube 均 200
> 本文档对应的脚本版本：`update-mihomo-sub.py` v2、`pick-node.py` v1、`start-vpn.sh` v2

---

## 0. 体例说明

本文档中的英文术语一律保留原文并附中文释义，格式统一为 `中文（English）`，例如：混合端口（mixed-port）、内容协商（content negotiation）。命令、路径、代码、节点名、版本号不翻译。

---

## 1. 这套东西在做什么

一句话：**从机场订阅地址拉取配置 → 伪装客户端身份下载 → 校验内核兼容性 → 启动时测速选最快节点 → 起一个应用层代理**。

整体链路：

```
订阅地址 (HTTPS)
   │  ① update-mihomo-sub.py：伪装 mihomo UA + 逐 IP 探测下载
   ▼
sub-work/sub-raw.yaml（订阅原文，只读留档）
   │  ② 注入本机运行参数（端口/控制接口/日志级别）
   ▼
sub-work/config.candidate.yaml（候选配置）
   │  ③ mihomo -t 内核语法校验（不通过就中止，绝不覆盖线上）
   ▼
config.yaml（线上配置，带 5 份滚动备份）
   │  ④ start-vpn.sh 拉起 mihomo 内核
   ▼
7890 混合端口（HTTP 代理 + SOCKS5）
   │  ⑤ pick-node.py 启动时一次性测速，把最快节点钉进 select 组
   ▼
业务流量
```

---

## 2. 文件清单

| 文件 | 作用 | 谁调用 |
|---|---|---|
| `update-mihomo-sub.py` | 更新订阅、生成并校验配置 | 手动执行 |
| `start-vpn.sh` | 启动内核（幂等）、校验、连通性自检 | 手动执行 |
| `pick-node.py` | 一次性测速并选最快节点 | `start-vpn.sh` 自动调用，也可手动 |
| `mihomo` | 代理内核二进制（v1.19.33 linux-amd64-compatible） | 被 `start-vpn.sh` 启动 |
| `config.yaml` | 线上生效的配置 | 内核读取 |
| `sub-work/` | 工作目录：`sub-raw.yaml`、`config.candidate.yaml`、`good-ips.txt` | 脚本内部使用 |
| `mihomo.log` | 内核运行日志 | 排障用 |
| `cache.db` | 内核状态，**含上次选中的节点** | 内核读写 |

> ⚠️ `clash` 旧二进制（Clash 2023.08.17 Premium）仍在目录里留着，但它**不支持 vless + REALITY 协议**，已无法加载新订阅，别再用它启动。

---

## 3. 快速上手（三条命令）

```bash
# 1) 更新节点（服务器重启后、或订阅节点变了之后执行）
cd /mnt/disk/henian/vpn && python3 update-mihomo-sub.py --restart

# 2) 启动（内核已经是 mihomo，命令与过去不同，必须改）
bash /mnt/disk/henian/vpn/start-vpn.sh

# 3) 看状态（已在运行时会直接打印策略组与当前节点，不重启）
bash /mnt/disk/henian/vpn/start-vpn.sh
```

正常输出长这样：

```
校验配置...
  校验通过
启动 mihomo...
已启动，PID:2979060
监听端口：
  *:7890  *:1053  *:9090

启动测速（一次性，约 6 秒）...
策略组: Flybit（类型 Selector，共 73 个节点）
当前节点: 🇸🇬 新加坡 | 01
测速完成，耗时 6.0s；可用 64/73 个节点
延迟排名（前 3）：
   1.   287ms  🇸🇬 新加坡 | 03
   2.   333ms  🇸🇬 新加坡 | 01  <- 当前
已切换到: 🇸🇬 新加坡 | 03
连通性测试：OK (http 204)
策略组与当前节点：
  Flybit     Selector  -> 🇸🇬 新加坡 | 03
  GLOBAL     Selector  -> DIRECT
```

总耗时约 **12 秒**，其中测速占 6 秒。

---

## 4. `update-mihomo-sub.py`——订阅更新

### 4.1 它解决的历史问题

v1 脚本在新订阅下**必定失败**，原因不是一行代码写错，而是三层变化同时发生：

| # | 问题 | 表现 | 处理方式 |
|---|---|---|---|
| 1 | 订阅端按 **User-Agent** 做内容协商（content negotiation） | `Mozilla/5.0` → **403 订阅访问被拒绝** | 改用 `mihomo/*`、`clash.meta/*` 等客户端 UA，逐个轮换 |
| 2 | 订阅格式变了 | 现在直接返回 Clash YAML，不再是 base64 编码的 `ss://` 列表 | 删除 base64 解码与 `ss://` 解析，改为直接处理 YAML |
| 3 | 协议升级 | 73 个节点**全部是 vless + REALITY** | 换 mihomo 内核；脚本内置 `mihomo -t` 强校验 |
| 4 | DNS 会轮换到坏 IP | 6 个 CDN 边缘 IP 里只有部分可用，其余 TLS 握手中被 reset | 种子 IP + 好 IP 缓存 + 逐 IP 探测 |
| 5 | 用 IP 直连时 `Host` 头被写成 IP | 即使 UA 对了，ESA 仍返回 403 | 显式带真实域名 `Host` 头 + SNI |

UA 实测对照（同一 IP，只换 UA）：

| User-Agent | 结果 |
|---|---|
| `Mozilla/5.0` | **403** |
| `curl/7.x` | 403 |
| `ClashforWindows/0.20.39` | 422 此客户端格式不支持当前套餐节点 |
| `mihomo/1.19.33` | **200，61867 字节** |
| `clash.meta/1.19.0` | 200 |

### 4.2 参数

```bash
python3 update-mihomo-sub.py                      # 更新并安装 config.yaml
python3 update-mihomo-sub.py --restart            # 更新 + 重启 + 启动测速
python3 update-mihomo-sub.py --restart --no-probe # 更新 + 重启，不测速
python3 update-mihomo-sub.py --dry-run            # 只下载校验，不写 config.yaml
python3 update-mihomo-sub.py --auto-select        # 备选：生成 url-test 常驻探测组
python3 update-mihomo-sub.py --manual-select      # 保持订阅原生 select 组（默认）
```

### 4.3 每次都会覆盖的配置项

脚本会把下列键强制写入 `config.yaml` 顶层（来源：脚本内 `OVERRIDES` 常量）：

| 键 | 值 | 说明 |
|---|---|---|
| `mixed-port` | `7890` | 混合端口，见第 6 节 |
| `allow-lan` | `true` | 允许局域网访问 |
| `bind-address` | `'*'` | 监听所有网卡 ⚠️ |
| `mode` | `rule` | 规则模式 |
| `log-level` | `info` | 日志级别 |
| `external-controller` | `0.0.0.0:9090` | 控制接口 ⚠️ |
| `secret` | `"123456"` | 控制接口密钥 ⚠️ 弱口令 |

> ⚠️ **重要**：`config.yaml` 是「生成物」，不是「配置文件」。每次跑更新脚本都会整份覆盖，**手改 config.yaml 的内容会丢**。要改端口/密钥/规则，改脚本里的 `OVERRIDES` 和 `ENSURE_FINAL_MATCH` 常量，然后重新执行脚本。

### 4.4 备份与回滚

- 安装前会把现有 `config.yaml` 备份成 `config.yaml.bak-<时间戳>`，**保留最近 5 份**（`KEEP_BACKUPS = 5`）。
- 候选配置先写到 `sub-work/config.candidate.yaml`，通过 `mihomo -t` 校验才替换线上文件；**校验失败时线上配置完全不动**。

回滚一条命令：

```bash
cd /mnt/disk/henian/vpn
ls -lt config.yaml.bak-* | head -5              # 挑一个时间点
cp config.yaml.bak-20261026-093615 config.yaml  # 覆盖回滚
bash start-vpn.sh
```

---

## 5. `start-vpn.sh`——启动

### 5.1 它做四件事

1. **前置检查**：内核文件存在且可执行、`config.yaml` 存在。
2. **幂等（idempotent）启动**：已经在跑就不重复启动，直接打印策略组与当前节点（0.5 秒返回）。
3. `mihomo -t` 再校验一次配置，然后 `setsid nohup` 后台拉起，等 5 秒确认进程存活、端口已监听。
4. 调用 `pick-node.py` **测速一次**选最快节点，最后做连通性自检。

### 5.2 参数

```bash
bash start-vpn.sh              # 启动 + 一次性测速选最快
bash start-vpn.sh --no-probe   # 启动但不测速，沿用 cache.db 里上次的选择
```

### 5.3 进程识别为什么用 `/proc`

脚本不用 `pgrep -f` 判断进程，而是遍历 `/proc/<pid>/exe` 比对真实可执行文件路径。原因：`pgrep -f` 按命令行字符串匹配，会把「命令行里恰好包含相同字符串的 shell」也算进去，实测曾导致两个内核实例同时跑、7890 端口冲突。

---

## 6. 端口说明

| 端口 | 协议 | 用途 |
|---|---|---|
| **7890** | **HTTP 代理 + SOCKS5（混合端口 mixed-port）** | 业务流量入口 |
| 9090 | HTTP RESTful API | 内核控制接口，`secret: 123456` |
| 1053 | DNS（TCP/UDP） | 内核内置 DNS 解析 |

### 6.1 7890 是「混合端口」

同一端口同时接受两种协议，内核按**首字节**自动分流，不需要配两个端口：

| 首字节 | 判定 | 实测结果 |
|---|---|---|
| ASCII `GET http://...` | HTTP 代理明文请求 | 204 ✅ |
| 明文 + `CONNECT` | HTTPS 隧道 | 204 ✅ |
| `0x05 0x01 0x00` | SOCKS5 握手 | 回 `05 00`（无认证）✅ |

两种方式的出口 IP 完全一致。

### 6.2 客户端配置写法

```bash
# HTTP 代理：http 和 https 目标都写 http:// 形式
export http_proxy=http://10.104.11.253:7890
export https_proxy=http://10.104.11.253:7890

# SOCKS5 写法（注意：SOCKS5 不能写进 http_proxy）
curl -x socks5h://10.104.11.253:7890 https://api.ipify.org
```

### 6.3 它不是「系统级 VPN」

当前配置**没有** `tun:`、没有 `redir-port`、没有 `tproxy-port`，属于**纯应用层代理（application-level proxy）**：

- 不接管路由表，不拦截系统流量；
- 每个程序必须**显式**配置代理才生效；
- `ping`、`telnet` 这类纯 ICMP/TCP 探测无法通过代理。

需要全局透明代理才需要开 `tun:`，但那会改动路由表，与当前方案是两套东西，别混。

---

## 7. `pick-node.py`——启动时一次性测速

### 7.1 设计取舍：为什么不用 url-test

`url-test` 组会让内核**每隔 interval 秒对全部节点做一次健康检查**，常态下有持续探测流量（73 节点 × 每 5 分钟）。本方案改成：**只在启动时测一次，把结果钉死在 `select` 组里**，运行期内核零探测。

实测确认：配置里 `health-check` 相关配置 **0 处**，策略组只有 `type: select` 1 个，启动后连续观察 70 秒日志无任何 health/delay 记录。

### 7.2 怎么测的

不逐节点发请求，而是调内核的整组测速接口：

```
GET /group/Flybit/delay?url=http://www.gstatic.com/generate_204&timeout=3000
```

内核内部**并发**测完 73 个节点，一次调用约 3 秒返回全部延迟。接口不可用时自动降级为逐节点并发（16 线程）兜底。

组名不硬编码：先读 `config.yaml` 里 `MATCH` 规则指向的组，读不到才退回第一个非 `GLOBAL` 的 Selector。

测完 `PUT /proxies/<组名>` 选中，并回读校验。

### 7.3 参数

```bash
python3 pick-node.py                      # 测速并选最快（100ms 容差防抖）
python3 pick-node.py --dry-run            # 只测速打印排名，不改选择
python3 pick-node.py --top 10             # 打印前 10 名
python3 pick-node.py --timeout 2000       # 单节点测速超时（毫秒）
python3 pick-node.py --rounds 2           # 测两轮取每节点最小值（+约 3 秒）
python3 pick-node.py --always-switch      # 只要不是最快就切，忽略容差
python3 pick-node.py --keep-tolerance 200 # 自定义容差（毫秒）
python3 pick-node.py --min-improve 80     # 快 80ms 以上才切
```

### 7.4 为什么需要「容差」和「多轮」

**实测噪声**：单轮并发测速时 73 个节点互相抢带宽，同一个节点两次结果能差 **400ms 以上**。曾出现单轮选出 484ms 的印尼节点，而两分钟后新加坡只有 237ms。

两个对策：

| 参数 | 默认值 | 作用 |
|---|---|---|
| `--rounds` | 启动时 2 | 测多轮，取每个节点的**最小值** |
| `KEEP_TOLERANCE_MS` | 100ms | 当前节点比最快慢 100ms 以内就**不切**，避免噪声导致来回抖 |
| `--always-switch` | 启动时启用 | 启动时没有业务流量，不必保留容差，直接选最快 |

逻辑分工很清晰：**启动时选最快（`--always-switch`），运行中重跑则保守（保留容差）**。

---

## 8. 节点选择机制（这是最容易误解的一点）

**`start-vpn.sh` 本身不选节点**，它只是调用 `pick-node.py`。节点选择完全由 `config.yaml` 里的策略组决定。

订阅自带策略组只有 **`Flybit`，类型 `select`（手动选择）**，73 个节点全在里面。规则尾部：

```yaml
- 'GEOIP,CN,DIRECT'
- 'MATCH,Flybit'
```

即只有**非中国大陆流量**进组走代理。

### 选择优先级（实测验证）

1. **`cache.db` 里有 `selected` 记录时 → 沿用上次的选择**
2. **没有记录 → 落到组内第一个节点**

第 1 条做过可逆实验：API 切到「🇭🇰 香港 | 01」→ `--restart` → 重启后仍是香港 01；`strings cache.db` 可见 `selected` / `Flybit` 键。

### 这套机制的已知局限

- **不具备故障自动切换（failover）**：`select` 组不测延迟、不排序、不切备用。节点在运行中途失效，流量会一直断，直到下次启动或你手动跑 `pick-node.py`。
- **订阅更新后节点改名/删除**，`cache.db` 记录失配 → 静默回落到第一个节点，你不会收到任何提示。
- 只能保证「启动那一刻最快」，不保证「一直最快」。

如果之后觉得「运行期断线不能自动恢复」不可接受，备选方案是 `--auto-select`（生成 `url-test` 常驻探测组，代价是常态探测流量），两个方案互斥，一般不用。

---

## 9. 常见故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `HTTP Error 403: Forbidden` | UA 被判定为非法客户端 | 确认脚本里 `UA_LIST` 用的是 `mihomo/*` 族；别用浏览器 UA |
| `Connection reset by peer` | DNS 解析落到坏 CDN IP | 脚本会自动逐 IP 探测；多试几次，或手动往 `sub-work/good-ips.txt` 里补可用 IP |
| `unsupport proxy type: vless` | 用的是旧 `clash` 内核 | 必须用 `mihomo` 内核，检查 `start-vpn.sh` 里 `CORE` 路径 |
| 启动后 7890 连不上 | 端口被旧实例占用 | `ss -lntp \| grep 7890` 看占用；按第 5.3 节方式清理进程 |
| 测速后仍然很慢 | 线路整体拥塞 / 订阅到期 | 跑 `pick-node.py --rounds 3 --top 10` 看全局延迟；若最快也 > 2000ms，脚本会提示 |
| `已切换到` 但流量没变化 | 浏览器/程序没配代理 | 见第 6.2 节；本方案不接管系统路由 |
| 配置改了没生效 | `config.yaml` 被脚本覆盖 | 改脚本常量，不要手改 `config.yaml`（第 4.3 节） |

### 看日志

```bash
tail -50 /mnt/disk/henian/vpn/mihomo.log          # 内核日志
grep -iE "error|warn" /mnt/disk/henian/vpn/mihomo.log | tail -10
```

### 单点连通性自检

```bash
# 走代理访问 204 探测地址
curl -s -o /dev/null -w "%{http_code}\n" -x http://127.0.0.1:7890 --max-time 15 \
  https://www.gstatic.com/generate_204

# 看出口 IP 与地区
curl -s -x http://127.0.0.1:7890 --max-time 15 "https://ipinfo.io/json"

# 读当前选中的节点
curl -s -H "Authorization: Bearer 123456" http://127.0.0.1:9090/proxies/Flybit
```

---

## 10. 运维操作清单

| 场景 | 命令 |
|---|---|
| 首次安装 / 换订阅地址 | 改脚本 `SUB_URL` → `python3 update-mihomo-sub.py --restart` |
| 日常更新节点 | `python3 update-mihomo-sub.py --restart` |
| 只更新不重启（先看效果） | `python3 update-mihomo-sub.py --dry-run` |
| 服务器重启后拉起 | `bash /mnt/disk/henian/vpn/start-vpn.sh` |
| 觉得当前节点慢 | `python3 pick-node.py --rounds 2` |
| 强制重选最快 | `python3 pick-node.py --rounds 2 --always-switch` |
| 只看排名不改选择 | `python3 pick-node.py --dry-run --top 10` |
| 回滚配置 | 见第 4.4 节 |

---

## 11. 安全提醒（当前配置的风险）

现状同时满足三条：`allow-lan: true` + `bind-address: '*'` + **未配置 `authentication`**，且 `ufw` 处于 inactive。

**实际后果**：

- 同网段**任何机器**都能直接把 `10.104.11.253:7890` 当出口用，**无需密码**；
- `9090` 控制接口对外暴露，只靠 `123456` 这个弱口令守着；
- 拿到控制接口的人可以切换节点、读取全部配置，**其中包括 73 个节点的 UUID 与 REALITY 私钥信息**。

两条加固路径，按代价从低到高：

**方案 A：给代理端口加认证（改动小）**

在脚本 `OVERRIDES` 里追加一行，让每次更新都保留该字段：

```python
("authentication", '["user:pass"]'),
```

客户端改用 `http://user:pass@10.104.11.253:7890`，SOCKS5 会自动走用户名密码握手。

**方案 B：用防火墙限制来源（更彻底）**

只放行实际使用的网段访问 7890/9090，其余 DROP。不影响客户端配置。

另建议把 `secret` 从 `123456` 换掉。注意：`pick-node.py` 会自动从 `config.yaml` 读 `secret`，**但 `start-vpn.sh` 里的 `SECRET` 是硬编码的**，改密钥时要同步改这个常量，否则状态显示会读不到策略组。

---

## 12. 已知小问题

1. `start-vpn.sh` 里 `SECRET=123456` 硬编码，与第 11 节的密钥轮换建议冲突，需手工同步。
2. `pick-node.py` 的 `BASE_DIR` 硬编码为 `/mnt/disk/henian/vpn`，换目录部署要改常量。
3. `BASE_DIR` 在三个脚本里各写了一份（`update-mihomo-sub.py`、`start-vpn.sh`、`pick-node.py`），没有抽公共配置。换目录需要改三处。
4. 当前**无 systemd 开机自启**，服务器重启后需人工执行 `start-vpn.sh`。如需自启可加 unit 文件。
