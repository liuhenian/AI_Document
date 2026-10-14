# 交换机认证方案：MAC 无感知认证（MAB）技术解析

> 适用范围：802.1X / Portal / MAC 无感知认证方向的方案理解与故障根因分析
> 术语对照：MAB（MAC Authentication Bypass，MAC 认证旁路）在国内厂商文档中常称"MAC 地址认证""MAC 无感知认证"

---

## 一、原理

### 1.1 一句话定义

MAB 是**基于端口 + 终端 MAC 地址**的接入控制技术。它把终端网卡的 MAC 地址**同时当作 RADIUS 认证的用户名和密码**，由接入设备（NAS）代终端完成认证，终端侧零配置、用户无感知。

### 1.2 三个角色

| 角色 | 标准术语 | 典型设备 | 职责 |
|---|---|---|---|
| 认证客户端 | Supplicant | 打印机、摄像头、IP 电话、老旧 PC、IoT | 无 802.1X 客户端，只发普通数据帧 |
| 认证设备 | Authenticator / NAS | 接入交换机、无线 AC、BRAS | 学习源 MAC、构造 RADIUS 请求、控制端口准入 |
| 认证服务器 | Authentication Server | 锐捷 SAM、Cisco ISE、Windows NPS、FreeRADIUS | 校验 MAC、返回认证结果与授权属性 |

### 1.3 核心机制

**身份构造**：NAS 抓到终端的源 MAC 后，构造：

```
User-Name      = A8-5E-45-1B-2C-3D
User-Password  = A8-5E-45-1B-2C-3D     （与用户名相同的 MAC 字符串）
Calling-Station-Id = A8-5E-45-1B-2C-3D （携带真实 MAC，供服务器校验/审计）
```

**密码加密**：采用 RADIUS PAP（RFC 2865 §5.2）：

```
b1 = MD5(Secret + Request-Authenticator)
c1 = p1 XOR b1
c2 = p2 XOR MD5(Secret + c1)      # 密码超过 16 字节时继续链式处理
User-Password = c1 + c2 + ...
```

其中 `Secret` 是交换机与 RADIUS 服务器之间的共享密钥。**共享密钥不一致 → 服务器校验 User-Password 失败 → 直接 Reject。**

**准入控制**：认证通过前，端口处于未授权态，除 EAPoL / DHCP / ARP 等必要控制报文外，业务流量一律丢弃；收到 Access-Accept 后端口置为授权态，并按服务器下发的属性执行授权（VLAN、ACL、QoS、带宽）。

### 1.4 MAC 地址格式（最常见的踩坑点）

不同厂商/服务器要求的 MAC 字符串格式不同，**交换机发出的格式必须与服务器库中存储的格式完全一致**，否则认证必然失败：

| 格式 | 示例 | 典型来源 |
|---|---|---|
| 点分十六进制 | `a85e.451b.2c3d` | Cisco 默认 |
| 短横线分隔 | `a8-5e-45-1b-2c-3d` | 锐捷 / 华为常见 |
| 冒号分隔 | `a8:5e:45:1b:2c:3d` | Windows、Linux 默认显示 |
| 连续无分隔 | `a85e451b2c3d` | 部分服务器数据库 |

大小写（`A8-5E` vs `a8-5e`）同样是常见不一致来源。

### 1.5 主机模式

| 模式 | 说明 | 适用 |
|---|---|---|
| Single-Host | 单端口单 MAC，出现第二个 MAC 触发安全违规（默认） | 普通哑终端 |
| Multi-Domain | 允许 2 个 MAC：语音 VLAN + 数据 VLAN | IP 电话 + PC 串联 |
| Multi-Auth | 多个 MAC 独立认证 | 下挂小交换机的场景 |
| Multi-Host | 只认证第一个 MAC，其余自动放行 | 下挂集线器/非受控设备 |

### 1.6 安全边界

**MAC 地址极易伪造**，因此 MAB 只能提供"可见性与基础准入"，不能作为强认证手段。生产环境通常叠加：

- 802.1X 优先 + MAB 兜底（认证回退）
- MAC 白名单 + 首次侦听（先学习登记，再放行）
- IP Source Guard / 动态 ARP 检测（DAI），防 MAC-IP 仿冒
- 端口安全（Port Security）限制 MAC 数量
- CoA 动态改授权 / 强制下线
- 终端指纹（DHCP Option 指纹、HTTP User-Agent）辅助识别

---

## 二、报文交互

### 2.1 MAB 的三种触发方式

| 触发方式 | 机制 | 备注 |
|---|---|---|
| 链路触发 | 端口 link-up 即发起 MAB | 部分平台支持，速度快 |
| 报文触发 | 收到终端首个 ARP / DHCP / ND / IP 报文，学习源 MAC 后触发 | **主流实现**；该报文被丢弃，不转发 |
| 回退触发 | 先发 EAPoL-Request/Identity，默认 30s 间隔、3 次共 90s 无响应 → 判定无 supplicant → 转 MAB | 即 802.1X + MAB 组合场景 |

### 2.2 完整报文时序

```
 终端                    接入交换机(NAS)                RADIUS 服务器
  │                          │                              │
  │ ① 链路 UP / ARP 首包 ───▶│                              │
  │   （端口未授权，包被丢弃）│                              │
  │                          │                              │
  │ ◀── ② EAPoL-Req/Identity │   （若启用 802.1X 回退）      │
  │   （无响应，3×30s 超时）  │                              │
  │                          │                              │
  │                          │ ③ Access-Request ──────────▶│
  │                          │   User-Name = MAC            │
  │                          │   User-Password = MAC(PAP)   │
  │                          │   Calling-Station-Id = MAC   │
  │                          │                              │
  │                          │ ◀──────── ④ Access-Accept    │
  │                          │   Tunnel-Private-Group-Id    │
  │                          │   Filter-Id / cisco-av-pair  │
  │                          │                              │
  │ ◀── ⑤ 端口置授权态        │                              │
  │      业务流量放行         │                              │
  │                          │                              │
  │                          │ ⑥ Accounting-Request Start ─▶│
  │                          │ ◀─────── Accounting-Response │
  │                          │                              │
  │                          │ ◀──────── ⑦ CoA / Disconnect │  （运维侧下发）
```

### 2.3 关键 RADIUS 属性清单

**Access-Request（Code = 1）**

| 属性 | 编号 | 取值 |
|---|---|---|
| User-Name | 1 | 终端 MAC 字符串 |
| User-Password | 2 | 与 User-Name 相同的 MAC，PAP 加密 |
| Service-Type | 6 | Call-Check(10)，部分实现用 Framed(2) |
| NAS-IP-Address | 4 | 交换机认证源 IP |
| NAS-Port / NAS-Port-Id | 5 / 87 | 物理端口号 / 端口名 |
| Calling-Station-Id | 31 | 终端 MAC（服务器常以此做二次校验） |
| NAS-Port-Type | 61 | Ethernet(15) / IEEE-802.11(19) |
| NAS-Identifier | 32 | 设备名 |
| Message-Authenticator | 80 | 带签名的请求必填 |

**Access-Accept（Code = 2）——授权下发**

| 属性 | 编号 | 作用 |
|---|---|---|
| Tunnel-Type | 64 | 13 = VLAN |
| Tunnel-Medium-Type | 65 | 6 = IEEE-802 |
| Tunnel-Private-Group-Id | 81 | 下发的 VLAN ID |
| Filter-Id | 11 | 下发 ACL 名称 |
| Session-Timeout | 27 | 会话时长，到期重认证 |
| Termination-Action | 29 | 1 = RADIUS-Request（触发重认证） |
| Vendor-Specific | 26 | 厂商私有属性（Cisco cisco-av-pair、华为 HW-*、锐捷私有属性） |

**其他报文**

| 报文 | Code | 说明 |
|---|---|---|
| Access-Reject | 3 | 认证失败，端口保持未授权 |
| Accounting-Request | 4 | Acct-Status-Type：Start(1) / Interim-Update(3) / Stop(2) |
| Accounting-Response | 5 | 计费应答 |
| CoA-Request / ACK / NAK | 43 / 44 / 45 | RFC 5176，动态改授权 |
| Disconnect-Request / ACK / NAK | 40 / 41 / 42 | RFC 5176，强制下线 |

### 2.4 认证失败时的行为

- **RADIUS 返回 Reject**：删除端口上的客户端编程，默认按 60s 间隔重试 2 次；仍失败则清除会话、端口回到 MAC 学习态。
- **RADIUS 不可达**：按 `server dead action` 配置决定是否保留已认证终端的编程；周期性重试直至服务器恢复；期间不学习新 MAC。
- **无重试配置**：周期性重试，超出次数后端口回学习态。

---

## 三、整体流程：从前端到后端

### 3.1 端到端链路

| 层 | 组件 | 职责 |
|---|---|---|
| 前端 · 终端侧 | 哑终端 / PC / 手机 / IoT | 无客户端；上电后发 ARP / DHCP |
| 接入层 | 接入交换机（NAS） | MAB 认证点：学 MAC、构造并发送 RADIUS 请求、执行端口准入 |
| 汇聚 / 核心层 | 三层交换机 / 路由器 | 转发 RADIUS 报文（UDP 1812/1813），保证服务器路由可达 |
| 后端 · 认证服务 | RADIUS 服务器（SAM / ISE / NPS） | 校验 MAC、执行授权策略、返回属性 |
| 数据源 | 本地 MAC 库 / AD / LDAP / MySQL | 存储 MAC 白名单与账号-MAC 绑定关系 |
| 管理面 | 认证管理平台 | 在线用户表、审计流水、CoA 动态授权/踢线 |

### 3.2 三种典型部署形态

**形态 A：纯 MAB（哑终端场景）**

1. 终端上电，端口 up，发首包
2. 交换机学习源 MAC，构造 RADIUS Access-Request
3. RADIUS 服务器查本地 MAC 白名单库
4. 命中 → Access-Accept，下发 VLAN/ACL → 端口授权
5. 未命中 → Access-Reject → 端口保持未授权，周期重试

**形态 B：802.1X + MAB 回退（混合终端场景）**

1. 端口 up，交换机先发 EAPoL-Request/Identity
2. 支持 802.1X 的终端正常走 EAP 流程
3. 90s 无响应的终端判定为无 supplicant，自动转 MAB
4. 后续流程同形态 A

**形态 C：Portal + MAB（锐捷"无感知认证"典型方案）**

这是锐捷方案中最常见的形态，也是"无感知"一词的来源：

1. **首次接入**：用户通过浏览器访问网络，被重定向到 Portal 页面（锐捷 ePortal），输入账号密码完成 Web 认证
2. **记录绑定**：认证成功后，RADIUS 服务器（锐捷 SAM）在接入控制策略中登记 **账号 ↔ 终端 MAC** 的绑定关系（对应 SAM 侧勾选"自动绑定 MA 快速认证信息"）
3. **后续接入**：终端下线再上线时，NAS（如 N18K、接入交换机、无线 AC）识别到 MAC，直接以该 MAC 作为账号和密码发起 MAB / 802.1X 认证
4. **无感放行**：SAM 命中绑定表 → Access-Accept → 端口授权，**用户全程无需再次输入账号密码**
5. **老化**：MAC 绑定记录存在空闲老化时间（锐捷默认 15 天），超期未上线则删除，终端需重新 Web 认证

### 3.3 锐捷设备侧关键配置对照

**有线交换机（单用户 / 多用户）**

```
interface GigabitEthernet 0/1
 dot1x mac-auth-bypass                 ! 单用户 MAB
 dot1x mac-auth-bypass multi-user      ! 多用户 MAB（需较新版本）
```

**无线 AC（MAB AAA 与 WLAN 启用）**

```
aaa new-model
aaa group server radius MAB
 server 192.168.34.183
aaa accounting network dot1x-mab start-stop group MAB
aaa authentication dot1x dot1x-mab group MAB
radius-server host 192.168.34.183 key ruijie

wlansec 1
 dot1x-mab
 dot1x accounting dot1x-mab
 dot1x authentication dot1x-mab
```

**三层 IPoE 场景（Web 认证 + 无感）**

```
interface GigabitEthernet 2/1/5.3120
 web-auth mac-auth enable                       ! 开启无感认证
 web-auth offline-detect idle-timeout 15 threshold 0   ! 15 分钟零流量踢线
```

**SAM+ 侧**

- 用户套餐的接入控制策略：勾选"自动绑定 MA 快速认证信息"
- 用户信息校验：勾选"MAC 快速接入"
- 配置可无感认证的终端数量（默认 1）

---

## 四、故障根因分析速查（面向 APM）

### 4.1 高频故障与定位方向

| 现象 | 可能根因 | 定位手段 |
|---|---|---|
| 全部终端认证失败 | RADIUS 共享密钥不一致 / 服务器宕机 / 1812 端口被 ACL 拦截 | 交换机 AAA 日志、`radius` 调试、连通性探测 |
| 认证超时无响应 | 到 RADIUS 路由不可达、UDP 丢包、服务器过载 | 交换机与服务器双向 ping/traceroute、抓包 |
| 部分终端 Reject | MAC 格式不匹配、MAC 未登记、绑定关系老化 | 对比交换机日志中的 MAC 与库中记录格式 |
| Accept 后仍不通 | 下发 VLAN 在设备上不存在、ACL 拦截、上行 Trunk 未放通该 VLAN | 检查 VLAN 表、ACL 计数器、Trunk 允许列表 |
| 认证时延高 | RADIUS 查库慢（AD/LDAP/MySQL）、大量终端同时上线 | 服务器响应时延 P95、数据库慢查询 |
| 静默终端长期未认证 | 终端不发任何报文，报文触发失效 | 改用链路触发或开启 802.1X 回退 |
| 手机反复掉线重认证 | 终端启用 MAC 随机化（Private MAC） | 识别随机 MAC 前缀、调整策略或关闭随机化 |
| CoA 不生效 | CoA 端口不通、NAS 不支持对应属性、密钥不一致 | CoA 失败率、CoA-NAK 原因码 |
| 无感突然失效 | MAC 绑定记录超老化时间被清除 | 检查 SAM 侧绑定表与老化配置 |

### 4.2 建议采集的指标

**认证可用性**
- 认证成功率 = Access-Accept / Access-Request 总数
- 认证失败原因码分布（Reject / Timeout / 服务器不可达）
- CoA 成功率

**认证性能**
- 认证时延：交换机发出请求 → 收到响应，P50 / P95 / P99
- 接入时延：端口 UP → 认证成功耗时
- 数据源查询耗时（AD / LDAP / MySQL）

**链路与设备状态**
- 端口 UP/DOWN 事件、端口授权态变化
- MAC 地址表变化量（识别 MAC 漂移/仿冒）
- RADIUS 服务器健康状态、1812/1813 端口连通性

### 4.3 数据采集建议

| 数据源 | 采集内容 |
|---|---|
| 交换机 Syslog | AAA 认证日志、端口状态、MAB 触发日志 |
| RADIUS 服务器日志 | Access-Request/Reject 明细、失败原因、处理时延 |
| SNMP / Trap | 端口状态、链路状态、设备告警 |
| 设备 CLI 快照 | MAC 表、VLAN 表、ACL 计数器 |
| 数据库 | MAC 绑定表、在线用户表、绑定记录老化情况 |
