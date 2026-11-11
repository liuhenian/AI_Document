---
title: SONiC 可观测采集框架与容器架构调研
date: 2026-11-10
tags:
  - SONiC
  - 网络操作系统
  - 可观测性
  - gNMI
  - 容器
status: 调研中
number headings: off
---

# SONiC 可观测采集框架与容器架构调研

> 本文是个人信息收集阶段的调研笔记，目标是把三件事讲清楚：**SONiC 的整体组成**、**它的可观测采集框架由什么构成**、**采集框架如何穿过容器边界拿到设备数据**。文末附全部来源链接与待核实项。

## 目录

- [[#0 结论先行|0 结论先行]]
- [[#1 SONiC 整体组成|1 SONiC 整体组成]]
- [[#2 可观测采集框架的组成|2 可观测采集框架的组成]]
- [[#3 采集框架通过容器获取设备信息的路径|3 采集框架通过容器获取设备信息的路径]]
- [[#4 容器在其中扮演什么角色|4 容器在其中扮演什么角色]]
- [[#5 版本演进与选型注意|5 版本演进与选型注意]]
- [[#6 对自研采集框架的启示|6 对自研采集框架的启示]]
- [[#7 参考资料|7 参考资料]]
- [[#8 待核实项|8 待核实项]]

## 0 结论先行

1. **SONiC 的本质是"Linux 发行版 + 一组 Docker 容器 + 一个共享 Redis"**，而不是一个单体网络操作系统。模块之间不直接 RPC，全部通过 Redis 的键值与发布/订阅（publish/subscribe）交换状态。官方原文：「SONiC places each module in independent docker containers...」，并依赖 Redis 提供「language independent interface」「multi-process communication」——见 [SONiC Architecture（官方 Wiki）](https://github.com/sonic-net/SONiC/wiki/Architecture)。
2. **采集框架的主干是 gNMI（gRPC Network Management Interface）遥测**：`telemetry` 容器（旧）或 `gnmi` 容器（2023.11 起替代）对外提供 Get / Set / Subscribe / Capabilities，内部由 DB client、non-DB client、events client 分别对接 Redis、`/proc`/平台数据、事件总线。见 [sonic-gnmi 仓库](https://github.com/sonic-net/sonic-gnmi) 与 [grpc_telemetry.md](https://github.com/sonic-net/sonic-gnmi/blob/master/doc/grpc_telemetry.md)。
3. **采集容器不直接访问 ASIC**。它读的是 `database` 容器里的 Redis；而 Redis 里的计数器是 `syncd` 容器通过 SAI（Switch Abstraction Interface）周期性 `get` 出来写进去的。容器在这一环里不是"通道"，而是**进程与权限的隔离边界 + 数据汇合点**。
4. **容器承担的是"故障隔离 + 独立生命周期 + 依赖编排"三件事，不是资源配额**。官方的容器启动模板里没有 `--memory` / `--cpus` 限制，也没有 `--privileged`，硬件访问改用显式 `--device` 与 device cgroup 规则——见 [docker_image_ctl.j2](https://github.com/sonic-net/sonic-buildimage/blob/master/files/build_templates/docker_image_ctl.j2)。

---

## 1 SONiC 整体组成

### 1.1 四个基座

| 基座           | 中文说明       | 作用                                                              | 来源                                                                                                                           |
| ------------ | ---------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Debian Linux | Debian 发行版 | 主机系统、内核网络栈、systemd、包管理；202405 周期升级到 Debian 12（Bookworm）         | [架构综述](https://safeguard.sh/resources/blog/how-a-network-switch-is-made-switch-asics-network-operating-systems-and-firmware) |
| SAI          | 交换机抽象接口    | 厂商无关的 ASIC 控制 API，向下对接各芯片 SDK                                   | [OCP SAI](https://github.com/opencomputeproject/SAI)                                                                         |
| Redis        | 内存键值数据库    | 全局状态总线：CONFIG_DB / APPL_DB / STATE_DB / COUNTERS_DB / ASIC_DB 等 | [官方 Wiki](https://github.com/sonic-net/SONiC/wiki/Architecture)                                                              |
| Docker       | 容器运行时      | 每个功能模块一个容器，独立启停、独立镜像                                            | [官方 Wiki](https://github.com/sonic-net/SONiC/wiki/Architecture)                                                              |
|              |            |                                                                 |                                                                                                                              |

分层关系（自下而上）：**ASIC → SAI/SDK → syncd → SWSS（orchagent）→ 应用容器 → 管理面**。

```mermaid
flowchart TB
  subgraph M["管理面 Management Plane"]
    CLI["CLI / REST / gNMI"]
  end
  subgraph APP["应用容器 Application Containers"]
    BGP["bgp (FRR)"]
    SNMP["snmp"]
    PMON["pmon"]
    TELE["telemetry / gnmi"]
  end
  subgraph INFRA["基础设施容器 Infrastructure Containers"]
    DB["database (Redis)"]
    SWSS["swss (orchagent)"]
    SYNCD["syncd (SAI + 厂商 SDK)"]
  end
  ASIC["交换 ASIC"]
  CLI --> DB
  BGP --> DB
  PMON --> DB
  DB <--> SWSS
  SWSS --> SYNCD
  SYNCD --> ASIC
  TELE <--> DB
  SNMP <--> DB
```

### 1.2 容器清单

官方 Wiki 的架构页列了 9 个容器（database / swss / syncd / bgp / lldp / teamd / snmp / pmon / dhcp-relay），现网版本还多了 nat、macsec、radv、sflow、rest-api、eventd、p4rt、telemetry 或 gnmi 等可选容器。功能开关由 `CONFIG_DB` 的 `FEATURE` 表控制（`config feature state <name> enabled|disabled`）。

| 容器（Container） | 镜像（Image） | 角色 | 关键进程 |
|---|---|---|---|
| database | docker-database | 唯一的数据枢纽 | 多个 redis-server 实例（按 `database_config.json`） |
| swss | docker-swss | 状态仲裁与编排 | orchagent、portsyncd、neighsyncd、fdbsyncd、intfmgrd、vlanmgrd、coppmgrd 等 |
| syncd | docker-syncd-&lt;vendor&gt; | 硬件同步 | syncd、SAI、厂商 SDK、FlexCounter 线程 |
| bgp | docker-fpm-frr | 路由协议栈 | bgpd、zebra、fpmsyncd |
| lldp | docker-lldp | 拓扑发现 | lldpd、lldp_syncd、lldpmgr |
| teamd | docker-teamd | 链路聚合 | teamd、teamsyncd |
| snmp | docker-snmp | 传统监控出口 | snmpd + AgentX 子代理 `sonic_ax_impl` |
| pmon | docker-platform-monitor | 平台/硬件监控 | xcvrd、thermalctld、sensord、fancontrol、ledd、pcied、syseepromd |
| telemetry / gnmi | docker-sonic-telemetry / docker-sonic-gnmi | 遥测出口 | `telemetry` 二进制、dialout client |
| rest-api | docker-sonic-mgmt-framework | REST/RESTCONF 出口 | rest_server（Translib） |
| eventd | docker-eventd | 系统事件总线 | eventd、事件发布/订阅库 |

来源：容器清单见 [官方 Wiki 架构页](https://github.com/sonic-net/SONiC/wiki/Architecture)；容器与镜像对应、supervisord 托管方式见 [DeepWiki: Core Runtime Services](https://deepwiki.com/sonic-net/sonic-buildimage/3-core-runtime-services)；Feature 开关见 [SONiC Feature Control](https://netbergtw.com/top-support/netberg-sonic/sonic-feature-control/)。

### 1.3 七个核心 Redis 库

| DB | 编号 | 内容 | 谁写 | 谁读 |
|---|---|---|---|---|
| APPL_DB | 0 | 应用层运行数据（路由、邻居、下一跳） | fpmsyncd、portsyncd 等 | orchagent |
| ASIC_DB | 1 | 面向 ASIC 的配置与状态（SAI 对象） | orchagent（经 sairedis） | syncd |
| COUNTERS_DB | 2 | 端口/队列/LAG 计数器 | syncd（FlexCounter） | telemetry/gnmi、snmp、CLI |
| LOGLEVEL_DB | 3 | 各模块日志级别 | CLI / 配置 | 各守护进程 |
| CONFIG_DB | 4 | 配置真相源（Source of Truth） | CLI、REST、gNMI Set、minigraph | orchagent、各 mgrd、hostcfgd |
| FLEX_COUNTER_DB | 5 | 计数器组开关与轮询间隔 | orchagent（FlexCounterOrch） | syncd |
| STATE_DB | 6 | 已配置对象的运行状态 | syncd、pmon、应用容器 | telemetry/gnmi、snmp、各 mgrd |

来源：[grpc_telemetry.md](https://github.com/sonic-net/sonic-gnmi/blob/master/doc/grpc_telemetry.md)；数据库职责划分见 [DeepWiki: SONiC Architecture](https://deepwiki.com/sonic-net/sonic-buildimage/1.1-sonic-architecture)。

### 1.4 三条典型数据流

- **配置下行**：CLI / REST / gNMI Set → `CONFIG_DB` → orchagent 翻译 → `ASIC_DB` → syncd → SAI → ASIC。
- **协议下行**：bgpd → zebra → fpmsyncd → `APPL_DB` → orchagent → `ASIC_DB` → syncd。
- **状态上行**：ASIC → SAI → syncd（FlexCounter）→ `COUNTERS_DB`；平台传感器 → pmon → `STATE_DB`。

官方对路由链路的完整描述见 [架构页](https://github.com/sonic-net/SONiC/wiki/Architecture) 的 "Route state interaction" 一节（bgpd → zebra → fpmsyncd → APPL_DB → orchagent → ASIC_DB → syncd → ASIC）。

---

## 2 可观测采集框架的组成

### 2.1 全景：四类数据源 + 四类出口

**数据源**

| 数据源 | 中文说明 | 典型内容 | 采集方式 |
|---|---|---|---|
| Redis DB | 结构化键值数据 | 端口状态、计数器、路由、配置 | DB client（HGET/订阅） |
| 非 DB 数据 | 主机侧文件与平台接口 | `/proc/stat`、`/proc/meminfo`、`/proc/loadavg`、`platform/cpu` | non-DB client |
| 事件 | 系统事件流 | 端口 down、容器异常、BGP 邻居变化 | events client（target=`EVENTS`） |
| 平台硬件 | 传感器、光模块、风扇、电源 | 温度、电压、DDM、PSU 状态 | pmon 守护进程写 `STATE_DB` |

**出口**

| 出口 | 中文说明 | 适用场景 | 来源 |
|---|---|---|---|
| gNMI 遥测 | gRPC 结构化订阅 | 主力，秒级/亚秒级指标、事件 | [sonic-gnmi](https://github.com/sonic-net/sonic-gnmi) |
| SNMP | 传统轮询协议 | 存量 NMS 兼容 | [sonic-snmpagent](https://github.com/sonic-net/sonic-snmpagent) |
| REST / RESTCONF | HTTP 按需查询 | 配置校验、临时取数 | [sonic-mgmt-framework](https://github.com/sonic-net/sonic-mgmt-framework) |
| Syslog | 文本日志 | 故障排查、审计 | 各容器 rsyslog 转发至 host |

补充：CLI（`show`/`counterpoll`）本身也是一条采集路径，直接读 Redis，见 [sonic-utilities](https://github.com/sonic-net/sonic-utilities)。

### 2.2 gNMI 遥测：两种模式、四个 RPC

**RPC**：`Get`（快照）、`Set`（写配置）、`Subscribe`（流式/轮询）、`Capabilities`（能力与模型）。SONiC 的 gNMI 实现基于标准 gNMI 并做定制，见 [gNMI proto 规范](https://github.com/openconfig/gnmi/blob/master/proto/gnmi/gnmi.proto)。

**两种部署模式**

| 模式 | 中文说明 | 连接发起方 | 适用 |
|---|---|---|---|
| Dial-in | 采集器连设备 | Collector → Switch | 常规监控，采集器掌握订阅 |
| Dial-out | 设备连采集器 | Switch → Collector | 设备在 NAT/防火墙后，或采集器无状态 |

Dial-out 的配置写在 `CONFIG_DB` 的 `TELEMETRY_CLIENT` 表，分三类：`Global`（encoding、src_ip、retry_interval、unidirectional）、`DestinationGroup_*`（dst_addr，可多个，失败切换下一个）、`Subscription_*`（dst_group、path_target、paths、report_type、report_interval）。示例：

```json
{
  "TELEMETRY_CLIENT": {
    "Global": {
      "encoding": "JSON_IETF",
      "retry_interval": "30",
      "src_ip": "30.57.185.38",
      "unidirectional": "true"
    },
    "DestinationGroup_HS": {
      "dst_addr": "30.57.186.214:8081,30.57.185.39:8081"
    },
    "Subscription_HS_RDMA": {
      "dst_group": "HS",
      "path_target": "COUNTERS_DB",
      "paths": "COUNTERS/Ethernet*,COUNTERS_PORT_NAME_MAP",
      "report_interval": "5000",
      "report_type": "periodic"
    }
  }
}
```

字段语义与失败重连行为（默认 30 秒重试、按 DestinationGroup 顺序切换）见 [dialout.md](https://github.com/sonic-net/sonic-gnmi/blob/master/doc/dialout.md)。传输层用 `gNMIDialOut.Publish`，消息体复用 gNMI 的 `SubscribeResponse`。

**路径模型**：SONiC 没有完整 YANG 数据模型，路径直接映射 Redis 层级 `DB / TABLE / KEY / FIELD`，`target` 填 DB 名：

```
target = COUNTERS_DB
path   = COUNTERS/Ethernet36/SAI_PORT_STAT_IF_IN_OCTETS
```

支持虚拟路径（服务端做映射，不是真实 key）：`COUNTERS/Ethernet*`（所有口全部计数器）、`COUNTERS/Ethernet*/<counter>`、`COUNTERS/Ethernet<port>/Queues`、`PERIODIC_WATERMARKS/Ethernet*/PriorityGroups`。非 DB 数据用 `target=OTHERS`，路径如 `proc/loadavg`、`platform/cpu`。见 [grpc_telemetry.md](https://github.com/sonic-net/sonic-gnmi/blob/master/doc/grpc_telemetry.md)。

**监听与认证**（以 `gnmi` 容器启动脚本为准）：

- 端口来自 `CONFIG_DB` 的 `TELEMETRY|gnmi.port`，**未配置时默认 8080**；
- 无证书时回落 `--noTLS --bind_address 127.0.0.1`，只允许本机访问；
- `user_auth` 未配置时**默认 `cert`**（fail-closed），证书白名单表为 `GNMI_CLIENT_CERT`；
- 支持 `--vrf mgmt`（管理 VRF）、`--unix_socket /var/run/gnmi/gnmi.sock`（UDS 模式）。

来源：[gnmi-native.sh](https://github.com/sonic-net/sonic-buildimage/blob/master/dockers/docker-sonic-gnmi/gnmi-native.sh)。

### 2.3 计数器链路：从 ASIC 到 gNMI

这是"采集框架如何拿到设备信息"的核心链路，五个环节：

1. **配置**：`CONFIG_DB` 的 `FLEX_COUNTER_TABLE` 决定哪些计数器组开启、轮询间隔多少毫秒（`counterpoll` 命令写入），orchagent 的 FlexCounterOrch 同步到 `FLEX_COUNTER_DB`。
2. **轮询**：syncd 的 FlexCounter 线程按组周期调用 SAI `get_stats`，把结果写入 `COUNTERS_DB`。
3. **落库**：键形如 `COUNTERS:<OID>`，另有 `COUNTERS_PORT_NAME_MAP` 做"端口名 → OID"映射。
4. **读取**：gnmi 容器的 DB client 通过 Unix socket 读 `COUNTERS_DB`，STREAM 模式按 sample interval 周期性读取，或按变更推送。
5. **编码**：按 `JSON_IETF` / `PROTO` / `ASCII` 编码，经 gRPC 流回传采集器。

社区实现里常见的默认轮询间隔：PORT 1000 ms、QUEUE 10000 ms、watermark 类 60000 ms；`PORT_BUFFER_DROP` 允许 30–300 s，`ACL` 允许 1–30 s。这些是社区默认值，**厂商发行版可能调整**，应以设备上的 `counterpoll show` 为准。来源：[DeepWiki: Database Architecture](https://deepwiki.com/edge-core/sonic-swss/5-database-architecture-and-schema)、[DeepWiki: Network Statistics](https://deepwiki.com/sonic-net/sonic-utilities/4.4-network-statistics)、[rates-and-utilization HLD 引用](https://github.com/sonic-net/sonic-sairedis/pull/878)。

### 2.4 高频与事件：两条补强路径

**高频流式遥测（HFST，High Frequency Streaming Telemetry）**：软件轮询在毫秒级微突发面前失效——计数器被读到时事件已经结束。SONiC 2025.11 引入的做法是**反向推送**：ASIC 以 IPFIX 格式按毫秒级节奏推送每端口计数器，`countersyncd`（Rust 实现）接收并按已注册的 IPFIX 模板解析，写入本地计数器库，再通过 OpenTelemetry 导出到 Prometheus/InfluxDB 等。见 [SONiC Foundation 综述](https://sonicfoundation.dev/how-sonic-powers-the-worlds-largest-ai-infrastructure/) 与 [HFST HLD](https://github.com/sonic-net/SONiC/blob/master/doc/high-frequency-telemetry/high-frequency-telemetry-hld.md)；实现提交见 [sonic-swss #3872](https://github.com/sonic-net/sonic-swss/pull/3872)。

**事件遥测**：gNMI 的 `target=EVENTS` 走 events client，**只支持 STREAM 模式**，底层通过 CGO 接 SONiC 事件系统（eventd）。路径参数可调 `heartbeat`（≤600 s）、`qsize`（1024–102400）、`usecache`；自身统计写入 `COUNTERS_DB:COUNTERS_EVENTS`（`missed_internal`、`missed_by_slow_receiver`、`latency_in_ms`）。见 [events_client.go](https://github.com/sonic-net/sonic-gnmi/blob/master/sonic_data_client/events_client.go)。

### 2.5 采集框架的组件拆解

| 组件 | 中文说明 | 职责 | 代码位置 |
|---|---|---|---|
| telemetry / gnmi server | 遥测服务主进程 | 启动 gRPC 服务、TLS、鉴权、路由请求 | `telemetry/telemetry.go` |
| DB client | 数据库客户端 | 按 target 连对应 Redis 实例，读表/键/字段 | `sonic_data_client/db_client.go` |
| non-DB client | 非数据库客户端 | 读 `/proc`、`platform` 等 | `sonic_data_client/non_db_client.go` |
| events client | 事件客户端 | 订阅事件总线，优先级队列缓冲 | `sonic_data_client/events_client.go` |
| dialout client | 拨出客户端 | 按 `TELEMETRY_CLIENT` 配置主动连采集器 | `dialout/` |
| translib / REST client | 模型翻译客户端 | 把 OpenConfig 路径翻译为后端 REST 调用 | `transl_utils/` |

来源：[sonic-gnmi 仓库目录](https://github.com/sonic-net/sonic-gnmi)、[DeepWiki: System Architecture](https://deepwiki.com/sonic-net/sonic-telemetry/1.1-system-architecture)。

---

## 3 采集框架通过容器获取设备信息的路径

先给结论：**采集容器不穿透到 ASIC，也不调用其他容器的进程；它只连一个 Unix socket，读 `database` 容器里的 Redis。**所谓"通过容器采集"，准确说是"**数据在生产容器里被写入共享 Redis，采集容器再从 Redis 取走**"。

### 3.1 容器是怎么被拉起来的

```mermaid
flowchart LR
  SD["systemd unit<br/>telemetry.service / gnmi.service"] --> SH["/usr/bin/xxx.sh<br/>start / stop / wait"]
  SH --> CTL["docker_image_ctl.j2 生成的脚本"]
  CTL --> DC["docker create + start"]
  DC --> SUP["容器内 supervisord"]
  SUP --> P1["redis-server / telemetry / syncd ..."]
```

- 每个容器对应一个 systemd unit（如 `gnmi.service`），unit 调用宿主机上的 `*.sh` 脚本；
- 脚本由构建期模板 [docker_image_ctl.j2](https://github.com/sonic-net/sonic-buildimage/blob/master/files/build_templates/docker_image_ctl.j2) 生成，统一实现 `start/stop/wait` 语义；
- 容器内由 **supervisord** 托管具体进程，配置按容器定制（database 容器用它拉起多个 redis 实例）；
- 启动顺序由脚本里的 flock 锁 + 轮询 Redis 就绪（`CONFIG_DB_INITIALIZED`）保证，见 [Core Runtime Services](https://deepwiki.com/sonic-net/sonic-buildimage/3-core-runtime-services)。

### 3.2 关键挂载与运行参数

| 参数/挂载 | 值 | 为什么采集需要它 |
|---|---|---|
| 网络模式 | `--net=host`（单实例）；多 ASIC 为 `--net=container:database$DEV` | 采集器可直接访问宿主管理 IP 的 8080/57400 端口，无需端口映射 |
| Redis 套接字 | `-v /var/run/redis:/var/run/redis:rw` | **采集容器与 database 容器的唯一数据通道** |
| HWSKU | `-v /usr/share/sonic/device/$PLATFORM/$HWSKU/$DEV:/usr/share/sonic/hwsku` | 端口映射、平台差异 |
| 平台目录 | `-v /usr/share/sonic/device/$PLATFORM:/usr/share/sonic/platform:ro` | 读取平台元数据、传感器配置 |
| 热启动状态 | `-v /host/warmboot$DEV:/var/warmboot` | 重启后恢复状态 |
| supervisor 日志 | `--tmpfs /var/log/supervisor:rw` | 容器内日志不落盘 |
| 设备节点 | `--device=...`（syncd/pmon） | 访问 ASIC、I2C、光模块 |
| UTS | `--uts=host` | 共享主机名 |
| 特权 | **不使用 `--privileged`** | 改用 device cgroup 精确授权 |
| 资源限制 | **无 `--memory` / `--cpus`** | 容器不是资源配额边界 |

以上均取自 [docker_image_ctl.j2](https://github.com/sonic-net/sonic-buildimage/blob/master/files/build_templates/docker_image_ctl.j2) 的实际 `docker create` 参数。

### 3.3 一次 Subscribe 的完整路径

```mermaid
sequenceDiagram
  participant C as Collector
  participant G as gnmi / telemetry 容器
  participant R as database 容器 (Redis)
  participant S as syncd 容器
  participant A as ASIC

  S->>A: SAI get_stats（FlexCounter 周期）
  S->>R: HSET COUNTERS_DB
  R-->>R: 键值更新 / keyspace 通知
  C->>G: gNMI Subscribe(target=COUNTERS_DB, path=COUNTERS/Ethernet36)
  G->>R: Unix socket 读 HGETALL（或订阅变更）
  R-->>G: 字段与数值
  G-->>C: SubscribeResponse（JSON_IETF，带 timestamp）
```

分步说明：

1. **采集器建连**：连设备管理 IP 的 gNMI 端口（`TELEMETRY|gnmi.port`，默认 8080）。因为容器是 host 网络，连接直接落到容器内进程。
2. **鉴权与 TLS**：按 `user_auth`（默认 `cert`）、`GNMI_CLIENT_CERT` 白名单校验；无证书场景只绑 `127.0.0.1`。
3. **路径解析**：`target` 决定去哪个 DB（`COUNTERS_DB` / `STATE_DB` / `APPL_DB` / `OTHERS` / `EVENTS`）。
4. **选客户端**：db_client / non_db_client / events_client 三选一。
5. **读 Redis**：通过挂载进来的 `/var/run/redis/redis.sock` 连接 database 容器内的 redis-server，读 table/key/field。**整个过程没有跨容器的 RPC 调用**。
6. **数据从哪来**：`syncd` 容器里的 FlexCounter 线程按 `FLEX_COUNTER_DB` 的间隔调用 SAI，把 ASIC 计数器写进 `COUNTERS_DB`；平台数据由 `pmon` 容器读 `/sys`、hw-management、I2C 后写 `STATE_DB`；协议状态由 `bgp` 容器经 fpmsyncd 写 `APPL_DB`。
7. **编码回传**：按请求的 encoding 序列化，gRPC 流式返回，附 `timestamp`。
8. **反向验证**：采集到的每个数值都能在设备上 `redis-cli -n 2 HGETALL COUNTERS:Ethernet36` 复现——这是排查"采集不到"最快的手段。

### 3.4 为什么容器之间不需要互相调用

Redis 在这里扮演的是**共享内存总线**，不是普通缓存：

- 生产者只写自己的表，消费者只读自己关心的表，双方不需要知道对方存在；
- 支持 pub/sub 与 keyspace 通知，实现"变更即推送"；
- 任一容器重启，其他容器读到的仍是一致状态，系统**降级而不雪崩**；
- 官方表述："applications can subscribe only to the data-views that they require"（[架构页](https://github.com/sonic-net/SONiC/wiki/Architecture)）。

代价也很明确：**Redis 成为单点与性能瓶颈**，且表结构（schema）靠约定而非强类型约束。

### 3.5 三类非 Redis 数据的采集路径

先给结论：**这三类数据的采集主体、通道、权限要求完全不同**，不能笼统说成"通过容器采集"。

| 数据类型 | 谁去取 | 通道 | 是否经过 Redis | 采集容器的权限要求 |
|---|---|---|---|---|
| 非 DB 数据（`/proc`、版本文件） | gnmi 容器自己读 | 容器内文件系统 | 否 | 无额外权限 |
| 系统事件流 | gnmi 容器订阅 eventd | ZMQ（XPUB/XSUB 代理） | 否（另一路 eventd 才落 EventDB） | 能连本机 ZMQ 端点 |
| 平台硬件（光模块/温度/风扇/PSU） | pmon 容器独占 | I2C / sysfs / hw-management → STATE_DB | 是（STATE_DB） | `--device` + device cgroup |

#### 3.5.1 非 DB 数据：采集器直接读 `/proc`

`non_db_client.go` 用一棵前缀树（trie）把**固定**路径映射到取数函数，不是任意文件都能读：

| 路径（target=`OTHERS`） | 实际读取 | 说明 |
|---|---|---|
| `OTHERS/proc/stat` | `/proc/stat` | CPU 时间片，解析后转 JSON |
| `OTHERS/proc/meminfo` | `/proc/meminfo` | 内存 |
| `OTHERS/proc/loadavg` | `/proc/loadavg` | 负载 |
| `OTHERS/proc/uptime` | `/proc/uptime` | 运行时长 |
| `OTHERS/proc/vmstat` | `/proc/vmstat` | 虚拟内存统计 |
| `OTHERS/proc/diskstats` | `/proc/diskstats` | 块设备 IO |
| `OTHERS/platform/cpu` | 由 `/proc/stat` 计算 | CPU 利用率，多时间窗 |
| `OTHERS/osversion/build` | `/etc/sonic/sonic_version.yml` | 镜像版本（带缓存，只读一次） |

两个关键点：

1. **为什么容器里能读到整机数据**：这些 `/proc` 文件属于全局内核视图，不随容器的 PID/网络命名空间隔离。因此采集容器不需要挂载宿主 `/proc`，也不需要 `--pid=host`。例外是 `/proc/meminfo`，在部分 cgroup 配置下会被裁剪成容器视角。
2. **`platform/cpu` 不是平台传感器**：它是从 `/proc/stat` 算出的 CPU 利用率。后台每 100 ms 采样一次写入 3000 槽环形缓冲，对外提供 `100ms` / `1s` / `5s` / `1min` / `5min` 五个窗口，属于"预采样 + 短窗口峰值"，不是每次请求现算。

能力边界：仅支持 `SAMPLE` 流式与 `POLL`，`ONCE` 未实现（函数体直接 `return`）。来源：[non_db_client.go](https://github.com/sonic-net/sonic-gnmi/blob/master/sonic_data_client/non_db_client.go)。

#### 3.5.2 系统事件流：ZMQ 代理跑在 eventd 容器里

> 事件流的输入方、输出方、交互方式与两个设计取舍（为什么不用 Redis、为什么要有代理），已单独整理为 [[SONiC-事件数据抓取框架-输入输出与设计取舍]]。本节只保留架构视角的概述。

事件不走 Redis，走 **ZeroMQ（ZMQ）的 PUB/SUB**，拓扑是"中央代理 + 多发布者 + 多订阅者"。ZMQ 本身是什么、怎么用，见 [[#3.7 ZeroMQ（ZMQ）是什么、怎么用|3.7]]：

```mermaid
flowchart LR
  P1["直接调 API：disk_check / container_checker / orchagent"] -- event_publish --> Z["eventd 容器<br/>proxy 线程（XPUB/XSUB）"]
  P2["rsyslog 插件：bgp / swss / syncd / dhcp-relay / host 日志"] -- event_publish --> Z
  PM["pmon：thermalctld / xcvrd / psud"] -. "只写 STATE_DB 与日志" .-> DB["STATE_DB"]
  Z -- 订阅 --> G["gnmi 容器<br/>events client"]
  Z -- 订阅 --> E["eventd 内 EventDB<br/>写 EVENT / ALARM 表"]
```

- **代理**：`eventd` 容器内，`eventd` 进程的一个线程承担代理（`eventd_proxy`，HLD 文档称 zmqproxy），bind XSUB/XPUB；由 supervisord 保证常驻。发布者连 SUB 端、订阅者连 PUB 端；默认端点硬编码在 `libswsscommon`，可用 `/etc/sonic/init_cfg.json` 覆盖。
- **发布**：`events_init_publisher(source)` + `event_publish(handle, tag, params)`。消息按 YANG 校验，内嵌全局序列号（用于丢事件检测），缺时间戳时自动补齐。
- **订阅**：`events_init_subscriber(use_cache, sources)` + 阻塞式 `event_receive()`，每次返回一个 JSON 字符串，并给出 `missed_cnt`。
- **gNMI 出口**：`target=EVENTS`、路径 `/events`，**只支持 STREAM**（`PollRun` / `OnceRun` 是空实现，源码不校验 subscription mode）；背压由优先级队列 `qsize`（默认 10240，范围 1024–102400）控制，队列满即丢弃并计入 `missed_by_slow_receiver`。gNMI 侧通过 CGO 直接调 swss-common 的订阅 API，**不经过 Redis**。
- **另一路落库**：eventd 内的 EventDB 消费者同样订阅这个代理，把事件写进 `EVENT_DB`（**主 redis 实例上的逻辑库 19**，`database_config.json` 中 `instance: redis`）的 `EVENT` / `ALARM` / `EVENT_STATS` / `ALARM_STATS` 表，供 CLI 与 REST 查询；历史默认保留 4 万条或 30 天。
- **缓存与回放**：订阅方 `use_cache=true` 时，eventd 内的 events-cache 侧车会缓存事件，断连重连后回放，缓存溢出计入 `missed-offline-cache`。

**链路与端点（源码确认）**

| 段 | 组件 | 地址 |
|---|---|---|
| 发布者 → 代理 | publisher 连 XSUB | `tcp://127.0.0.1:5570` |
| 订阅者 ← 代理 | subscriber 连 XPUB | `tcp://127.0.0.1:5571` |
| 控制面 | 服务请求 / 应答 | `tcp://127.0.0.1:5572` |
| 缓存抓取 | 代理内部通道 | `tcp://127.0.0.1:5573` |

对应键名 `xsub_path` / `xpub_path` / `req_rep_path` / `capture_path`，可写入 `/etc/sonic/init_cfg.json` 的 `events` 段覆盖；同段还有 `stats_upd_secs`（默认 5）。

**线上消息是两段式 ZMQ 消息**

- part1 = 事件源（如 `sonic-events-bgp`），供 ZMQ 侧做订阅过滤；
- part2 = `boost::serialization` 文本归档的 map，键用单字母压缩：`d`=数据（JSON 字符串）、`r`=runtime-id（UUID）、`s`=sequence（uint32）、`t`=epoch；
- 同一个进程对同一 source 重复 init 会复用同一 publisher；进程退出时发 `CONTROL_DEINIT` 退休 runtime-id，避免缓存泄漏（publisher 缓存上限 1000）。

**订阅参数写在 path 的 key 里**

| key | 默认 | 取值范围 | 作用 |
|---|---|---|---|
| `heartbeat` | 不设置 | ≤ 600 秒 | 空闲心跳；经 `event_set_global_options` 设为进程级全局值 |
| `qsize` | 10240 | 1024–102400 | 优先级队列上限，满则丢弃 |
| `usecache` | true | true / false | 断连期间由 eventd 的 cache 服务缓存并回放 |

**事件有两条产生路径**

1. **应用显式调用 API**：`events_init_publisher()` + `event_publish()`。社区代码里这类调用并不多——`scripts/disk_check.py`（磁盘）、monit 的 `container_checker` 脚本（容器健康）、orchagent 的个别事件，以及 `events_publish_tool` 这类调试工具；
2. **日志转事件（大头）**：rsyslog 插件按正则把日志行解析成事件后发布。[docker-eventd](https://github.com/sonic-net/sonic-buildimage/tree/master/dockers/docker-eventd) 下的 `host_events_info.json`、`swss_events_info.json`、`syncd_events_info.json`、`bgp_events_info.json`、`dhcp_relay_events_info.json` 就是这套映射：每份只声明 `yang_module` 与 `proclist`（进程名 + 正则文件），其中 host 源覆盖 `monit`、`systemd`、`kernel`、`dockerd`、`arista`、`python3`。**bgp / swss / syncd 的事件基本都是这条路，不是应用直接发的。**

**事件标识与负载**

- 标识 = `<YANG 模块名>:<container 名>`，例 `sonic-events-bgp:bgp-state`；
- 公共字段来自 `sonic-events-common` 的 `sonic-events-cmn` grouping，目前只有 `timestamp`（`yang::date-and-time`）；
- 线上 JSON：`{"sonic-events-bgp:bgp-state":{"ip":"100.126.188.90","status":"down","timestamp":"2022-08-17T02:39:21.286611Z"}}`；
- 自测事件 `sonic-host:device-test-event` 会被 events client 主动过滤，不下发给订阅者。

**采集质量的三个指标（可直接查库）**

events client 周期性把计数写回 **COUNTERS_DB 的 `COUNTERS_EVENTS` 表**，字段统一为 `value`：

| key | 含义 |
|---|---|
| `COUNTERS_EVENTS:missed_internal` | 框架内丢失，按 runtime-id 的序号缺口累计 |
| `COUNTERS_EVENTS:missed_by_slow_receiver` | 队列满丢弃 + 下发失败 |
| `COUNTERS_EVENTS:latency_in_ms` | 最近 10 次下发的平均时延（发布时刻到当前时刻） |

查询命令：`redis-cli -n 2 HGETALL COUNTERS_EVENTS`。

**gNMI 侧封装**

- Prefix：`target=EVENTS`；Path：`/events`；
- Value：`TypedValue_JsonIetfVal`，内容即上述 JSON；
- Timestamp 取 **`publish_epoch_ms`（发布时刻）**，不是接收时刻，因此设备与采集端的时钟偏差会直接体现为采集侧时延。

来源：[events-producer.md](https://github.com/sonic-net/SONiC/blob/master/doc/event-alarm-framework/events-producer.md)、[event-alarm-framework.md](https://github.com/sonic-net/SONiC/blob/master/doc/event-alarm-framework/event-alarm-framework.md)、[events_common.h](https://github.com/sonic-net/sonic-swss-common/blob/master/common/events_common.h)、[events_common.cpp](https://github.com/sonic-net/sonic-swss-common/blob/master/common/events_common.cpp)、[events_client.go](https://github.com/sonic-net/sonic-gnmi/blob/master/sonic_data_client/events_client.go)、[events.cpp](https://github.com/sonic-net/sonic-swss-common/blob/master/common/events.cpp)。

#### 3.5.3 平台硬件：只有 pmon 碰硬件，其他人读 STATE_DB

这是三条路径里唯一"必须持有设备权限"的一条，链路有五段：

1. **pmon 容器内的守护进程**：`xcvrd`（光模块）、`thermalctld`（温度与风扇）、`psud`（电源）、`syseepromd`（EEPROM）、`ledd`、`pcied`、`sensormond`、`chassisd` 等，清单见 [sonic-platform-daemons](https://github.com/sonic-net/sonic-platform-daemons)。
2. **调用 Platform API**：统一接口在 [sonic-platform-common](https://github.com/sonic-net/sonic-platform-common)（Chassis / Sfp / Thermal / Fan / PSU / Component），具体实现由厂商 `sonic_platform` 包提供，底层是 I2C、sysfs、CPLD 寄存器或 `hw-management`。
3. **容器如何获得权限**：pmon 的启动参数按平台动态生成 `--device=/dev/i2c-*` 与 `--device-cgroup-rule=c <major>:* rwm`（支持热插拔总线与 FRU），并挂载 `/var/run/hw-management`、`/sys/module/sx_core`、`/usr/share/sonic/firmware`、`/host/bmc` 等。**不使用 `--privileged`**。
4. **落到 STATE_DB**：`TRANSCEIVER_INFO`、`TRANSCEIVER_DOM_SENSOR`、`TRANSCEIVER_STATUS`、`TEMPERATURE_INFO`、`FAN_INFO`、`PSU_INFO` 等表（表名随版本略有差异，以设备上 `redis-cli -n 6 KEYS '*'` 为准）。
5. **出口只读**：gnmi 容器经 db client 读 `STATE_DB`，SNMP 容器经 AgentX 子代理读 `STATE_DB`，**两者都不碰 I2C**。平台数据在采集侧没有"直采"选项，只有"读库"。

**更正一处**：pmon 的守护进程**不调** `event_publish()`——已核对 `thermalctld` 源码，全文只有 STATE_DB 写表与日志输出（`EventLogger` 只是把日志 tee 到 `/host/bmc/event.log`），没有任何事件 API 调用。所以硬件越阈值只产生两样东西：STATE_DB 的状态快照、syslog 日志；只有当这条日志被 `host_events_info.json` 的 `proclist` 覆盖时，才会被 rsyslog 插件转成事件。**"show 里有值、事件流里没有"的常见原因就在这里。**

#### 3.5.4 三条路径的工程含义

| 维度 | 非 DB（/proc） | 事件（ZMQ） | 平台（pmon → STATE_DB） |
|---|---|---|---|
| 采集粒度 | 由订阅 sample interval 决定 | 事件驱动，毫秒级 | 由 pmon 轮询周期决定（光模块/温度常见数十秒） |
| 历史数据 | 无，只有瞬时值 | 有缓存回放，EventDB 可查历史 | 只有当前值，历史需外部存储 |
| 失败表现 | 路径不在 trie 中 → 直接报错 | 背压/断连 → 丢事件并计数 | pmon 异常 → STATE_DB 停更，值变陈旧 |
| 扩展方式 | 改代码加路径（硬编码 trie） | 新增 YANG 事件 + 发布路径（调 API 或加 rsyslog 正则） | 厂商实现 Platform API |

一句话概括：**非 DB 是"采集器自己看"，事件是"别人主动告诉它"，平台是"别人写好了它去读"**。三种模式对应三种可靠性边界，排障时应先判断问题落在哪一类，再去查对应的容器与表。

### 3.6 跨容器访问 Redis 的具体机制

先纠正两个容易混淆的前提：

- **Redis 不在"基础镜像"里**，它跑在独立的 `database` 容器（镜像 `docker-database`）中；
- **七个库不是七个进程**，而是同一批 redis-server 实例上的**逻辑库**（`SELECT 0..6`）。映射写在 `database_config.json` 的 `DATABASES` 段：库名 → `id` + `separator` + `instance`。

**三条访问通道**

| 通道 | 适用场景 | 实现方式 | 证据 |
|---|---|---|---|
| Unix domain socket（主通道） | 单 ASIC / 多 ASIC 通用 | 宿主机 `/var/run/redis<DEV>` 同时 bind mount 到 database 与各业务容器的 `/var/run/redis` | [docker_image_ctl.j2](https://github.com/sonic-net/sonic-buildimage/blob/master/files/build_templates/docker_image_ctl.j2) |
| TCP 回环 | 单 ASIC（`--net=host`） | 所有容器共享 host 网络命名空间，`127.0.0.1:6379` 即达 | [docker-database-init.sh](https://github.com/sonic-net/sonic-buildimage/blob/master/dockers/docker-database/docker-database-init.sh) |
| TCP bridge IP | 多 ASIC 命名空间 | database 用 bridge 网络；其他容器 `--net=container:database$DEV`，地址取 eth0 | 同上 |

**为什么这不叫"跨容器网络"**

1. bind mount 共享的是**宿主机同一个 inode**，不是复制文件；
2. Unix socket 是**文件系统对象**，连接时内核按路径解析到该 inode，在两个容器内的进程之间建立 socket pair；
3. 全程不经过 veth / docker0 / NAT / 端口映射，也不要求两个容器在同一网络命名空间。

真正跨命名空间的是多 ASIC 场景：database 容器独立在 bridge 网络里，业务容器共享它的网络命名空间，才需要用到 TCP。

**客户端如何定位数据库**

swsscommon / redis 客户端读取 `/var/run/redis/sonic-db/database_config.json`（可用 `SONIC_DB_CONFIG_FILE` 覆盖路径），按库名查 `instance`，再取该实例的 `unix_socket_path` 或 `hostname:port`。精简后的结构：

```json
{
  "INSTANCES": {
    "redis": { "hostname": "127.0.0.1", "port": 6379,
               "unix_socket_path": "/var/run/redis/redis.sock" }
  },
  "DATABASES": {
    "APPL_DB":     { "id": 0, "separator": ":", "instance": "redis" },
    "COUNTERS_DB": { "id": 2, "separator": ":", "instance": "redis" },
    "CONFIG_DB":   { "id": 4, "separator": "|", "instance": "redis" },
    "STATE_DB":    { "id": 6, "separator": "|", "instance": "redis" }
  }
}
```

注意 `separator` 的差异：`CONFIG_DB`/`STATE_DB` 用 `|` 分隔表名与键（`PORT|Ethernet0`），`APPL_DB`/`COUNTERS_DB` 用 `:`（`COUNTERS:Ethernet0`）。这是拼 key 时最常见的错。

**权限与失败模式**

- redis-server 以 `redis` 用户运行，supervisord 里显式 `user=redis`；socket 位于 bind mount 目录内，业务容器以 root 运行可直接连接。非 root 客户端需要调整 `unixsocketperm`。
- 启动参数为 `--bind 127.0.0.1 <hostname> --port <port> --unixsocket <path>`；`hostname` 是 `127.0.0.1` 时保持 protected mode，非回环地址时显式 `--protected-mode no`。
- 三类典型故障：socket 文件不存在（database 未就绪）、`database_config.json` 与实际实例不一致、客户端容器非 root 且 socket 权限不足。

**多 ASIC 与 chassis 的差异**

- 多 ASIC：socket 路径带设备后缀（`/var/run/redis0/redis.sock`、`/var/run/redis1/redis.sock`），每个 ASIC 一套 `database<DEV>` / `swss<DEV>` / `syncd<DEV>`；
- chassis：另起 `redis_chassis` 实例（端口 6380，socket `/var/run/redis-chassis/redis_chassis.sock`），并给容器加 `--add-host redis_chassis.server:<ip>`。

来源：[database_config.json.j2](https://github.com/sonic-net/sonic-buildimage/blob/master/dockers/docker-database/database_config.json.j2)、[supervisord.conf.j2](https://github.com/sonic-net/sonic-buildimage/blob/master/dockers/docker-database/supervisord.conf.j2)。

### 3.7 ZeroMQ（ZMQ）是什么、怎么用

> 这一节是 [[#3.5.2 系统事件流：ZMQ 代理跑在 eventd 容器里|3.5.2]] 的前置知识：先把 ZeroMQ 本身讲清楚，再看 SONiC 怎么用它，最后回答"你自己怎么用"。

#### 3.7.1 定义：它是一个库，不是中间件

**ZeroMQ（零消息队列，ZeroMQ，缩写 ZMQ）是一个嵌入式消息库（embeddable messaging library）**：它把"套接字（socket）+ 消息队列 + 异步 I/O 线程"打包成一段能链接进你进程的代码，让进程之间、线程之间用同一套接口传消息。

与常见消息中间件的区别，一张表就分得清：

| 维度 | ZeroMQ | Kafka / RabbitMQ 这类消息中间件（message broker） |
|---|---|---|
| 形态 | 库（`libzmq`），链接进你的程序 | 独立服务进程，客户端连它 |
| 是否要部署 | 不要，装个共享库即可 | 要，部署 broker、配集群与副本 |
| 谁是中心 | 无中心，点对点，或自建代理 | broker 是中心 |
| 持久化 | 无，内存队列，进程退出即失 | 有，磁盘日志或持久队列 |
| 投递语义 | 至多一次（at-most-once），PUB/SUB 无 ACK | 至少一次 / 精确一次可配 |
| 认证加密 | 默认无，可选 CURVE / PLAIN / GSSAPI | 内建 ACL、TLS、账号体系 |
| 典型用途 | 机内/进程内高速 fan-out、采集侧车、控制面 | 跨机房数据管道、事件溯源 |

所以在设备上 `ps` 里永远找不到叫 `zmqd` 的守护进程——**ZMQ 没有服务端**。SONiC 里的代理也不是独立服务：它是 `eventd` 进程内的一个线程（代码里叫 `eventd_proxy`，HLD 文档称 zmqproxy）。

三个必须记住的语义，后面所有的坑都由它们派生：

1. **消息边界被保留**：一次 `send` 就是一帧（frame），一次 `recv` 拿一帧，不会被 TCP 粘包切开；多帧消息用 `ZMQ_SNDMORE` 拼、用 `ZMQ_RCVMORE` 判断还有没有下一帧。
2. **连接是异步的**：`connect()` 立即返回，后台 I/O 线程才去建链。连上之前发出的消息直接丢弃——这就是"慢加入者（slow joiner）"问题。
3. **不重传**：PUB/SUB 下，没人订阅、队列满、对端太慢，消息都是**静默丢弃**，发送方完全无感知。

#### 3.7.2 六种 socket 模式与两条关键语义

ZMQ 的 socket 不是"一条 TCP 连接"，而是"一条带语义的消息通道"。常用的六种：

| 模式 | 形状 | 方向 | 可靠性 | 典型用途 |
|---|---|---|---|---|
| PUB / SUB | 一对多 | 单向 | 丢就丢了 | 事件广播、遥测推送 |
| XPUB / XSUB | 一对多 | 双向（订阅可见） | 同上，但能看到订阅/退订 | 写代理、做订阅审计 |
| REQ / REP | 一对一 | 请求-应答 | 有重试，严格配对 | RPC、健康探测 |
| DEALER / ROUTER | 多对多 | 双向 | 异步、可路由 | 自定义协议、网关 |
| PUSH / PULL | 一对多 | 单向 | 轮询分发、负载均衡 | 任务流水线 |
| PAIR | 一对一 | 双向 | — | 线程间专用通道 |

其中 XPUB/XSUB 是 SONiC 能搭出那个代理的关键，值得单独说：

- **普通 PUB 对订阅者是"隐形"的**：发布端看不到谁订了、订了什么，也没法据此做任何决策；
- **XSUB ↔ XPUB 之间会传订阅消息**：首字节 `0x01` 表示订阅、`0x00` 表示退订，后面跟主题过滤串。代理据此维护 fan-out 表，才知道该把哪条消息转给谁。

这也是 `zmq_proxy()` 存在的意义：它把 frontend（XSUB）与 backend（XPUB）桥接起来，等于一个**可编程的交换机**。见 [ZeroMQ 指南第 5 章](https://zguide.zeromq.org/docs/chapter5/) 中 Espresso 与 Last Value Cache 两个例子。

#### 3.7.3 connect 与 bind：谁监听端口

ZMQ 里 `bind` / `connect` 与"谁是客户端、谁是服务端"无关，只决定**谁占端口**：

- `bind()` = 监听，端点必须先存在；
- `connect()` = 主动连，对端不在时会自动重连（带退避）。

SONiC 的拓扑是"代理 bind 两端，生产者与消费者都 connect"：

```mermaid
flowchart LR
  P["发布者进程<br/>ZMQ_PUB"] -- "connect :5570" --> X["eventd 内 proxy 线程<br/>ZMQ_XSUB（bind 5570）"]
  X --- XP["ZMQ_XPUB（bind 5571）"]
  XP -- "connect :5571 + 订阅过滤" --> S["订阅者进程<br/>ZMQ_SUB"]
```

这个方向不是随手定的：发布者只该发、不该占端口（否则每加一个发布者就多一个监听端口）；代理固定占两个端口，才能把 N 个发布者与 M 个订阅者汇聚成多对多。

#### 3.7.4 SONiC 的具体用法（源码确认）

| 端点 | 键名（`init_cfg.json` 的 `events` 段） | socket 类型与归属 | 对端 |
|---|---|---|---|
| `tcp://127.0.0.1:5570` | `xsub_path` | `ZMQ_XSUB`，由 `eventd` 内的 proxy 线程 bind | 发布者用 `ZMQ_PUB` connect |
| `tcp://127.0.0.1:5571` | `xpub_path` | `ZMQ_XPUB`，由 `eventd` 内的 proxy 线程 bind | 订阅者用 `ZMQ_SUB` connect |
| `tcp://127.0.0.1:5572` | `req_rep_path` | `REQ` / `REP` 控制面（eventd 侧提供缓存与回显服务） | 发布方/订阅方用来探测连接就绪、开关缓存 |
| `tcp://127.0.0.1:5573` | `capture_path` | `zmq_proxy` 的 capture 通道 | 代理内部，复制一份流给缓存侧车 |

四个默认值硬编码在 [events_common.cpp](https://github.com/sonic-net/sonic-swss-common/blob/master/common/events_common.cpp) 的 `cfg_default`，可被 `/etc/sonic/init_cfg.json` 覆盖。

**这条链路不经过 Redis**

| 段 | 两端 | 传输 | 经过 Redis？ |
|---|---|---|---|
| 发布 → 代理 | 发布进程 ↔ `:5570` | ZMQ over TCP 回环（ZMTP 握手 + 分帧） | 否 |
| 代理内部 | `ZMQ_XSUB` ↔ `ZMQ_XPUB` | 进程内内存队列 | 否 |
| 代理 → 订阅 | `:5571` ↔ 订阅进程 | 同上 | 否 |
| 下发给采集端 | `telemetry` ↔ Collector | gRPC（默认 8080） | 否 |
| EventDB 落库 | `eventdb` ↔ `database` 容器 | Redis RESP over `redis.sock` | **是**（`EVENT_DB`，逻辑库 19） |
| 采集质量指标 | events client ↔ `COUNTERS_DB` | 同上 | **是**（`COUNTERS_EVENTS`） |

两个容易混的"发布订阅"：

- **ZMQ 的 PUB/SUB**：socket 语义，点对点 TCP，没有 broker（这里的 proxy 只是转发器）；
- **Redis 的 PUBLISH/SUBSCRIBE**：`libswsscommon` 的 `NotificationProducer` 用 `PUBLISH <频道> <json>` 做 DB 变更通知（频道名由调用方传入），与事件流是两套东西。

一句话：**事件从产生到送到采集端，全程只碰 ZMQ 与 gRPC；Redis 只在"存历史"和"存质量指标"两个落点出现。** 验证命令 `ss -tnp | grep -E ':557[0-3]'`，看到的对端是本地进程，不是 `6379`。

**线上消息是两帧**（[events_common.h](https://github.com/sonic-net/sonic-swss-common/blob/master/common/events_common.h) 的 `zmq_message_send`）：

| 帧 | 内容 | 作用 |
|---|---|---|
| part1 | 事件源字符串，如 `sonic-events-bgp` | 供 ZMQ 侧做**前缀过滤**（订阅者只收匹配的源） |
| part2 | `boost::serialization` **文本归档**的 `map<string,string>` | 承载 `d`（JSON 数据）、`r`（runtime-id）、`s`（序号）、`t`（epoch 微秒） |

注意 part2 **不是 JSON**：它是 boost 文本归档，头部形如 `serialization::archive <版本号>`，之后按 map 结构依次排列条目数与各键值对的长度和内容、以空格分隔。`json.loads()` 对它一定报错——这一点决定了"能不能自己写个脚本直接订阅"。

源码里另外三个细节：发布端 socket 只设了 `ZMQ_LINGER=100 ms`（进程退出时最多等 100 ms 把残留在队列里的消息发出去）；订阅端设 `ZMQ_RCVTIMEO` 与 `ZMQ_SUBSCRIBE`；`MAX_PUBLISHERS_COUNT=1000`，用于限制"按 runtime-id 记录序号缺口"的缓存规模。

#### 3.7.5 你自己怎么用：三条路，别一上来就连 ZMQ

| 做法 | 接口 | 你拿到什么 | 适用 |
|---|---|---|---|
| ① gNMI `EVENTS`（推荐） | gRPC `Subscribe`，`target=EVENTS`、`path=/events` | 已解码的 JSON、发布时刻时间戳、`missed` 计数 | 跨机采集、要认证、想复用现成 gNMI 客户端 |
| ② `libswsscommon` 的 `event_receive()` | C++ / C / Go（cgo） | JSON 字符串 + `missed_cnt` + `publish_epoch_ms` | 在设备内写原生采集器 |
| ③ 直连 XPUB `5571` | `pyzmq` / `libzmq` | 两帧原始数据，第二帧要自己解 boost 归档 | 只在必须拿原始 source、且能接受自己解包时 |

**做法 ③ 的最小骨架**（Python，`pip install pyzmq`）：

```python
import zmq

ctx = zmq.Context.instance()
sub = ctx.socket(zmq.SUB)
sub.setsockopt(zmq.LINGER, 100)          # 与 SONiC 的 LINGER_TIMEOUT 对齐
sub.setsockopt(zmq.RCVTIMEO, 2000)       # 2 秒无数据抛 zmq.Again
sub.connect("tcp://127.0.0.1:5571")      # XPUB 端点
sub.setsockopt(zmq.SUBSCRIBE, b"sonic-events-bgp")   # 过滤的是 part1（事件源）

while True:
    source = sub.recv_string()   # part1: sonic-events-bgp
    body   = sub.recv_string()   # part2: boost 文本归档，不是 JSON
    print(source, body[:160])
```

顺带说明，**ZMQ 本身的用法**只有三步，其余都是模式选择：建上下文（`zmq_ctx_new`）→ 建 socket（`zmq_socket`）→ `bind` 或 `connect`，然后 `send` / `recv`。

```python
# 通用写法：一端 bind 监听，一端 connect；PUB 端不要在没订阅者时"以为发出去了"
pub = ctx.socket(zmq.PUB);  pub.bind("tcp://*:5555");  pub.send_multipart([b"topic", b"payload"])
sub = ctx.socket(zmq.SUB);  sub.connect("tcp://127.0.0.1:5555")
sub.setsockopt(zmq.SUBSCRIBE, b"topic")
```

#### 3.7.6 四个坑，都会实际咬人

| 坑 | 现象 | 原因与对策 |
|---|---|---|
| 只绑回环 | 远端采集器连 `设备IP:5571` 直接超时 | 默认端点写死 `127.0.0.1`。单 ASIC 下容器用 `--net=host`，**宿主机 shell 能直连**；多 ASIC 要进对应 netns。要跨机就得改 `events.xpub_path`，但 ZMQ 默认无认证无加密，暴露前先想安全 |
| 慢加入者 | 程序启动后头几条事件收不到 | `connect` 是异步的，订阅生效前发布的消息被丢弃。SONiC 用 5572 的 echo 探测规避；自研客户端可靠序号缺口 `s` 判断，别假设"连上就全有" |
| 静默丢弃 | 事件数比预期少，且没有任何错误 | PUB/SUB 不重传；libzmq 每对端默认高水位（high water mark，HWM）1000 条，满了就丢。gNMI 侧另有自己的 `qsize`（默认 10240） |
| 过滤串写错 | 订阅 `bgp-state` 一条都收不到 | 过滤是**前缀匹配 part1（事件源）**，要写 `sonic-events-bgp`。另外 XPUB 默认不上报重复订阅，需要时得开 `ZMQ_XPUB_VERBOSE` |

#### 3.7.7 自研 APM 要不要用 ZMQ

| 场景 | 结论 | 理由 |
|---|---|---|
| 设备内多进程向多个消费者广播 | 合适 | 无 broker、时延低、fan-out 天然支持，SONiC 已是范例 |
| 跨机、要求不丢、要认证 | 不合适 | 无持久化、无 ACK、默认无加密；这活该交给 gNMI 或 Kafka 一类 |
| 需要历史回放 | 不合适 | ZMQ 不存历史；回放要靠 `EVENT_DB` 或下游存储 |

**结论：在 SONiC 场景里，ZMQ 是"设备内部的传输层"，不是"对外的采集接口"。要做 APM 助手，消费事件优先走 gNMI 的 `EVENTS` target；只有在设备内写原生 agent、且确实需要极低时延时，才考虑直连 5571。**

#### 3.7.8 四个高频疑问

**① 为什么非要两帧，合成一帧不行吗**

不行，至少"用 ZMQ 的过滤"这件事会直接失效。原因很具体：**所有事件的载荷开头都是同一串 `serialization::archive`**，如果只有一帧，前缀过滤面对每条消息看到的前缀都一样，等于没有过滤。

| 好处 | 机制 |
|---|---|
| 让 ZMQ 层能按来源过滤 | 订阅匹配只作用于**第一帧**；把 `sonic-events-bgp` 单独放一帧，才有了可区分的路由标签 |
| 过滤几乎不花钱 | 只比对短字符串，不解析 boost 归档；不匹配的消息在 zmq 引擎里就被丢弃，不会进应用 |
| 编码可独立演进 | part1 是纯文本 source，part2 将来换序列化格式也不影响路由 |
| 中间件只搬载荷 | 缓存服务按源码注释**只存 part2**（`event_serialized_t`），source 由通道决定，不必解包 |

一句话：**part1 是信封上的地址，part2 是信；没有地址，邮局只能把每封信都拆开看。**

**② 代理（zmqproxy）存在的目的**

核心是把 **N×M 连接压成 N+M**：

| 没有代理 | 有代理 |
|---|---|
| PUB 必须 bind，N 个发布者就是 N 个端点 | 代理统一 bind 两个固定端点 |
| M 个订阅者要连 N 个地址，发布者增减就得改订阅方配置 | 订阅者只连 `5571` 一个地址 |
| 发布者重启，订阅者重连并重新传播订阅，中间丢一段 | 订阅关系留在代理侧，发布者重启不影响订阅者 |
| 想做缓存、审计，得改每个发布者 | 代理一个 capture 口就能复制全量流（`5573`） |

同时要强调它**不是 broker**：不落盘、不 ACK、不重传；`zmq_proxy()` 只是 libzmq 里的一个函数，跑在 `eventd` 进程的第二个线程里（`eventd_proxy::run`），不是独立可执行文件。

**③ 发布者是谁**

发布者是**进程**，不是容器。分两类：

| 类型 | 谁 | 怎么发 |
|---|---|---|
| 直接调 API | `disk_check.py`、monit 的 `container_checker`、orchagent 的个别事件 | `events_init_publisher(source)` + `event_publish(tag, params)` |
| 日志转事件（多数） | rsyslog 插件，覆盖 bgp / swss / syncd / dhcp-relay / host | 插件按 `*_events_info.json` 的 proclist 与正则解析日志后发布 |

一个进程可为多个 source 各建一个 publisher；同一 source 重复 init 会复用实例（`s_publishers` 按 source 去重）。

**④ 订阅者又是谁**

| 订阅者 | 位置 | 目的 |
|---|---|---|
| events client | gnmi 容器的 `telemetry` 进程 | 转成 gNMI `EVENTS` 下发，供外部采集 |
| EventDB 消费者 | eventd 容器 | 写 `EVENT` / `ALARM` 表，供 CLI / REST 查历史 |
| cache 服务 | eventd 容器 | 断连期间缓存、重连回放（走 capture `5573`） |
| 自研进程 | 任意链接 `libswsscommon` 的程序 | 厂商或自研 agent 直接消费 |

两个限制要记住：**每个进程只允许一个 subscriber**（`EventSubscriber::s_subscriber` 单例），所以 gNMI 的多客户端过滤只能在 gNMI 层做；**ZMQ 层只能按 source 过滤，不能按事件 tag 过滤**——只想要 `bgp-state` 这一类，得在 gNMI 或应用层再筛一次。

#### 3.7.9 生产者链接的是哪个库：建连与发送的完整调用链

先纠一个容易混的说法：**不存在"zmqproxy 的库"**。代理侧和生产者侧用的是同一个传输库，但它们是两个进程，之间只有一条 TCP 连接。

| 层 | 具体名字 | 形态 | 与生产者的关系 |
|---|---|---|---|
| 传输协议库 | `libzmq.so.5`（ZeroMQ 本体，纯 C 接口） | 共享库 | 间接依赖，由下一层链接进来 |
| SONiC 封装库 | `libswsscommon.so`（C++）／`_swsscommon.so`（Python 扩展） | 共享库 | **直接链接**，代码里只 include `events.h` |
| 代理（proxy） | `eventd` 进程里的 `eventd_proxy` 线程 | 进程内线程 | **不链接**，只通过 `tcp://127.0.0.1:5570` 对话 |

#### 3.7.9.1 初始化：六步，前五步在 `EventPublisher::init()` 里

| # | 调用 | 所属库 | 作用 |
|---|---|---|---|
| 1 | `events_init_publisher("sonic-events-xxx")` | libswsscommon | 按 source 查静态表 `s_publishers`，命中就复用 |
| 2 | `zmq_ctx_new()` | libzmq | 建 ZMQ 上下文（context），同时拉起自己的 I/O 线程 |
| 3 | `zmq_socket(ctx, ZMQ_PUB)` | libzmq | 建发布者（PUB）类型的 socket |
| 4 | `zmq_setsockopt(ZMQ_LINGER, LINGER_TIMEOUT)` | libzmq | 退出时最多等这么久，避免残留消息被直接丢 |
| 5 | `zmq_connect(get_config(XSUB_END_KEY))` | libzmq | 连 `tcp://127.0.0.1:5570`，**立即返回** |
| 6 | `m_event_service.echo_send("hello")` | libswsscommon | 走 5572 的 REQ/REP 往返，探测代理是否真的就绪 |

第 5 步必须配第 6 步，源码注释写得很直白：

> `REQ socket is connected and a message is sent & received, more to ensure PUB socket had enough time to establish connection. Any message published before connection establishment is dropped.`

**这就是慢加入者（slow joiner）问题的官方解法**：`zmq_connect()` 只是登记端点，真正的握手在后台 I/O 线程完成，返回 0 不代表对端在线。所以封装库额外用一条 REQ/REP 往返，把"连接已建立"这件事同步出来。

#### 3.7.9.2 发送：五步，最后落在两次 `zmq_send`

| # | 调用 | 做什么 |
|---|---|---|
| 1 | `event_publish(h, "bgp-state", params)` | 应用侧入口 |
| 2 | `EventPublisher::publish()` | 参数里没有时间戳就补 `EVENT_TS_PARAM` |
| 3 | `convert_to_json(source + ":" + tag, params)` | 拼事件标识，序列化成 JSON 正文 |
| 4 | `send_evt()` | 组 `internal_event_t`：`d` 正文、`r` runtime-id、`s` 递增序号、`t` epoch 微秒 |
| 5 | `zmq_message_send(socket, source, evt)` | 发两帧，内部用 `ZMQ_SNDMORE` 拼接 |

四个会实际影响设计的行为：

1. **每个 source 一套上下文和连接**。`init()` 每次都 `zmq_ctx_new()`，去重只按 source 做。一个进程发 3 类事件，就是 3 个上下文、3 条到 5570 的 TCP 连接，彼此不共享。
2. **`zmq_send` 成功不等于送达**。PUB 没有确认（ACK），返回值只表示"进了本地发送队列"；订阅者不在、高水位（HWM）满，消息直接丢。`event_publish` 的返回值不能当投递凭据。
3. **代理是线程，不是进程**。`eventd.cpp` 里 `eventd_proxy::run()` 创建 `ZMQ_XSUB`（bind 5570）、`ZMQ_XPUB`（bind 5571）、`ZMQ_PUB`（capture，5573），然后一行 `zmq_proxy()` 永久阻塞。容器内 `ps` 只能看到 `eventd`。
4. **`event_publish` 的 tag 不含 source**。source 在 init 时给，`source:tag` 由库内部拼接；两处都写 source 会得到 `sonic-events-bgp:sonic-events-bgp:bgp-state` 这类错标识。

#### 3.7.9.3 两种写法

Python 版摘自官方工具 `events_publish_tool.py`，是实际在用的接口，不是示意：

```cpp
// C++
#include "events.h"
event_handle_t h = events_init_publisher("sonic-events-vendor");
event_params_t p{{"ip", "10.0.0.1"}, {"status", "down"}};
event_publish(h, "link-state", &p);
events_deinit_publisher(h);
```

```python
# Python
from swsscommon.swsscommon import (events_init_publisher, events_deinit_publisher,
                                   event_publish, FieldValueMap)
h = events_init_publisher("sonic-events-vendor")
p = FieldValueMap()
p["ip"] = "10.0.0.1"
p["status"] = "down"
event_publish(h, "link-state", p)
events_deinit_publisher(h)
```

Python 侧参数是 `FieldValueMap`（本质为 `map<string,string>`），值必须转成字符串，直接传整数会报类型错。

#### 3.7.9.4 四条验证命令

```bash
docker exec eventd ps -ef | grep eventd        # 只有 eventd，没有 zmqproxy
ldd /usr/bin/eventd | grep zmq                  # 确认链接 libzmq
ss -tnp | grep 5570                             # 生产者到代理的 ESTABLISHED
nm -D /usr/lib/x86_64-linux-gnu/libswsscommon.so | grep event_publish
```

**结论：生产者做的是"调 `libswsscommon` 的 `events_init_publisher` 建连、调 `event_publish` 发送"；`libswsscommon` 再调 `libzmq` 的 `zmq_connect` / `zmq_send` 落到 TCP。全程没有任何代码"调用 zmqproxy"——代理只是这条 TCP 的另一端。**

---

## 4 容器在其中扮演什么角色

### 4.1 六个角色

1. **部署与生命周期单元**：一个功能 = 一个镜像 = 一个容器 = 一个 systemd unit。可以单独 `systemctl restart gnmi`，不影响转发面。
2. **故障隔离边界**：某容器崩溃或内存泄漏不会拖垮其他容器；`CONTAINER_FEATURE.auto_restart` 可配置关键进程退出后整容器重启。见 [Monitoring and Auto-Mitigating Unhealthy Containers](https://github.com/sonic-net/SONiC/blob/master/doc/monitoring_containers/monitoring_containers.md)。
3. **依赖编排单元**：`swss.sh` 等脚本用 flock + 轮询 Redis 就绪状态，决定 syncd、teamd、bgp 的启动顺序；多 ASIC 下按 `asic0/asic1` 命名空间起多实例（`swss0`、`syncd1`）。
4. **权限边界**：不做 `--privileged`，改为显式 `--device` 与 `--device-cgroup-rule`，把"能碰哪些设备节点"写进容器配置——这比单纯 root 运行更可控。
5. **交付单元**：升级即换镜像；2023.11 起 `gnmi` 容器整体替代 `telemetry` 容器，就是一次容器级替换（见 [sonic-buildimage PR #19153](https://github.com/sonic-net/sonic-buildimage/pull/19153)）。
6. **扩展单元**：sidecar 模式（`telemetry-sidecar`）在不重启主容器的前提下同步证书、脚本与依赖；`telemetry-watchdog` 独立探活 gRPC 端点。见 [Management and Telemetry Services](https://deepwiki.com/sonic-net/sonic-buildimage/3.3-routing-services)。

### 4.2 边界与代价（重要）

- **不是强资源隔离**：启动模板未设置 `--memory` / `--cpus`，一个容器占满内存仍会影响整机。SONiC 用 monit 的 `memory_checker` 做阈值告警，而不是 cgroup 硬限制。
- **不是编排平台**：单机 Docker + systemd，没有 Kubernetes 式调度、滚动升级、健康探针体系。
- **共享内核**：容器共用宿主内核，内核态问题（驱动、ASIC SDK）无法被容器隔离。
- **镜像体积代价**：每个容器各带一套 Debian 用户态，镜像与内存开销显著，这是社区 SONiC 在接入层交换机（2 核 / 2 GB 内存）上吃力的原因之一，见 [Containerized NOS 分析](https://plvision.eu/blog/products/containerized-nos)。

## 5 版本演进与选型注意

| 时间点 | 变化 | 影响 | 来源 |
|---|---|---|---|
| 2023.11 | `gnmi` 容器替代 `telemetry` 容器 | 容器名、镜像名、`systemctl` 单元名都变；`FEATURE` 表仍可能残留 `telemetry` 条目 | [PR #19153](https://github.com/sonic-net/sonic-buildimage/pull/19153) |
| 2024 | `gnmi` 原生代理增强：管理 VRF、SmartSwitch/DPU、ZMQ 8100、GNOI | 采集需按 VRF 与 DPU 场景调整连接地址 | [gnmi-native.sh](https://github.com/sonic-net/sonic-buildimage/blob/master/dockers/docker-sonic-gnmi/gnmi-native.sh) |
| 2025.11 | HFST 进入 release：IPFIX 毫秒级推送 + OpenTelemetry 导出 | 从"软件轮询"转向"硬件推送"，需要平台/芯片支持 | [HFST HLD](https://github.com/sonic-net/SONiC/blob/master/doc/high-frequency-telemetry/high-frequency-telemetry-hld.md) |

实践注意：

1. **先确认容器名**：`docker ps | grep -E "gnmi|telemetry"`，再看 `show feature status`。
2. **先确认端口与认证**：`redis-cli -n 4 HGETALL "TELEMETRY|gnmi"`；默认 8080、默认 `user_auth=cert`。

## 6 对自研采集框架的启示

> 以下为个人判断，不是官方结论。

1. **采集端只依赖"稳定的数据契约"，不依赖生产者**。SONiC 的采集器不知道 orchagent 怎么实现，只知道 `COUNTERS_DB` 的表结构。自研 APM 若把采集器与具体数据源进程耦合，任何一侧升级都会互相牵连。
2. **三层分离值得照搬**：生产（syncd/pmon）→ 汇聚（Redis）→ 出口（gNMI）→ 消费（Collector）。映射到 APM 现有栈，汇聚层就是 VictoriaMetrics / Loki / MySQL，出口层才是采集 Agent。**出口层应可独立重启、独立限流**。
3. **轮询有天花板**。SONiC 用 FlexCounter 轮询撑到 1 s 级，毫秒级必须换硬件推送（HFST）。若 APM 的诊断场景需要亚秒级，就要在选型阶段确认芯片是否支持 IPFIX/INT，而不是先堆采集频率。
4. **通配符与虚拟路径能显著降请求数**。`COUNTERS/Ethernet*` 一次拿全端口，避免 N 次 RPC；自研接口设计应保留"批量/通配"语义。
5. **容器化解决隔离，不解决配额**。若把采集 Agent 容器化，内存/CPU 限制、日志轮转、优雅退出都要自己补，SONiC 这套模板里没有。
6. **弱 schema 是隐性成本**。Redis 表结构靠社区约定，跨版本漂移只能靠适配层兜。自研采集应对指标名做注册表与版本兼容层。

## 7 参考资料

### 7.1 官方架构与代码

| 资料 | 说明 | 链接 |
|---|---|---|
| SONiC Wiki | 官方文档总入口 | https://github.com/sonic-net/SONiC/wiki |
| SONiC Architecture | 容器清单、DB 职责、状态交互链路（官方权威） | https://github.com/sonic-net/SONiC/wiki/Architecture |
| sonic-buildimage | 镜像与容器构建主仓库 | https://github.com/sonic-net/sonic-buildimage |
| sonic-swss | orchagent 与各 syncd/mgrd | https://github.com/sonic-net/sonic-swss |
| sonic-sairedis | syncd、SAI redis、FlexCounter 实现 | https://github.com/sonic-net/sonic-sairedis |
| sonic-utilities | CLI、`counterpoll`、`show` 系列 | https://github.com/sonic-net/sonic-utilities |
| sonic-platform-daemons | pmon 内各平台守护进程 | https://github.com/sonic-net/sonic-platform-daemons |
| OCP SAI | 交换机抽象接口规范 | https://github.com/opencomputeproject/SAI |

### 7.2 遥测协议与实现

| 资料 | 说明 | 链接 |
|---|---|---|
| sonic-gnmi | 现行 gNMI/gNOI 实现（原 sonic-telemetry） | https://github.com/sonic-net/sonic-gnmi |
| grpc_telemetry.md | 路径模型、DB target、RPC、端口与认证 | https://github.com/sonic-net/sonic-gnmi/blob/master/doc/grpc_telemetry.md |
| dialout.md | Dial-out 配置模型、重连策略、示例 | https://github.com/sonic-net/sonic-gnmi/blob/master/doc/dialout.md |
| gNMI proto | 协议规范（Subscribe/Subscription 语义） | https://github.com/openconfig/gnmi/blob/master/proto/gnmi/gnmi.proto |
| OpenConfig telemetry model | Dial-out 配置参考的 YANG 模型 | https://github.com/openconfig/public/blob/master/release/models/telemetry/openconfig-telemetry.yang |
| events_client.go | 事件订阅实现与统计口径 | https://github.com/sonic-net/sonic-gnmi/blob/master/sonic_data_client/events_client.go |
| non_db_client.go | `OTHERS` 路径清单、`/proc` 读取与 CPU 利用率计算 | https://github.com/sonic-net/sonic-gnmi/blob/master/sonic_data_client/non_db_client.go |
| sonic-telemetry（旧仓库） | 历史实现，已迁移至 sonic-gnmi | https://github.com/sonic-net/sonic-telemetry |

### 7.3 容器与运行时

| 资料 | 说明 | 链接 |
|---|---|---|
| docker_image_ctl.j2 | 容器 `docker create` 参数、挂载、多 ASIC 命名 | https://github.com/sonic-net/sonic-buildimage/blob/master/files/build_templates/docker_image_ctl.j2 |
| gnmi-native.sh | gnmi 容器启动参数：端口、VRF、认证、UDS | https://github.com/sonic-net/sonic-buildimage/blob/master/dockers/docker-sonic-gnmi/gnmi-native.sh |
| sonic-platform-common | Platform API：Chassis / Sfp / Thermal / Fan / PSU | https://github.com/sonic-net/sonic-platform-common |
| 容器监控与自愈 | `CONTAINER_FEATURE.auto_restart`、monit 检查 | https://github.com/sonic-net/SONiC/blob/master/doc/monitoring_containers/monitoring_containers.md |
| Feature 开关实践 | `config feature state` 与 `FEATURE` 表 | https://netbergtw.com/top-support/netberg-sonic/sonic-feature-control/ |
| DeepWiki: 架构总览 | 社区对 buildimage 的结构化解读（非官方） | https://deepwiki.com/sonic-net/sonic-buildimage/1.1-sonic-architecture |
| DeepWiki: 运行时服务 | 容器生命周期、database 初始化、启动依赖 | https://deepwiki.com/sonic-net/sonic-buildimage/3-core-runtime-services |

### 7.4 计数器、高频与事件

| 资料 | 说明 | 链接 |
|---|---|---|
| COUNTERS_DB 与 FlexCounter | 表结构、默认轮询组、Lua 插件（社区解读） | https://deepwiki.com/edge-core/sonic-swss/5-database-architecture-and-schema |
| counterpoll 与统计工具 | 轮询间隔约束、`portstat`/`queuestat` 实现 | https://deepwiki.com/sonic-net/sonic-utilities/4.4-network-statistics |
| 轮询间隔单位修复 | 毫秒/秒换算的社区讨论，含 HLD 引用 | https://github.com/sonic-net/sonic-sairedis/pull/878 |
| HFST HLD | 高频流式遥测设计（IPFIX + countersyncd） | https://github.com/sonic-net/SONiC/blob/master/doc/high-frequency-telemetry/high-frequency-telemetry-hld.md |
| HFST 实现提交 | countersyncd（Rust）与 Actor 模型 | https://github.com/sonic-net/sonic-swss/pull/3872 |
| SONiC Foundation 综述 | HFST 在 AI 集群中的动机与效果 | https://sonicfoundation.dev/how-sonic-powers-the-worlds-largest-ai-infrastructure/ |
| events-producer.md | 事件发布/订阅 API、zmqproxy 拓扑与序列号机制 | https://github.com/sonic-net/SONiC/blob/master/doc/event-alarm-framework/events-producer.md |
| event-alarm-framework.md | EventDB 消费者、EVENT/ALARM 表结构与持久化 | https://github.com/sonic-net/SONiC/blob/master/doc/event-alarm-framework/event-alarm-framework.md |

### 7.5 第三方分析（非官方，供交叉验证）

| 资料 | 说明 | 链接 |
|---|---|---|
| Containerized NOS 分析 | 容器化架构的收益与接入层资源瓶颈 | https://plvision.eu/blog/products/containerized-nos |
| SONiC 深度架构解读 | 容器、DB、SAI 的分层说明 | https://sonicfoundation.dev/deep-dive-into-sonic-architecture-design/ |
| NOS 构成拆解 | 镜像里到底装了什么（Debian、SDK、平台包） | https://safeguard.sh/resources/blog/how-a-network-switch-is-made-switch-asics-network-operating-systems-and-firmware |

### 7.6 ZeroMQ 与事件传输

| 资料 | 说明 | 链接 |
|---|---|---|
| ZeroMQ 官网 | 项目主页、模式总览与语言绑定 | https://zeromq.org/ |
| ZeroMQ 指南（zguide） | 官方推荐教程；第 1/2 章讲模式，第 5 章讲高级 PUB/SUB | https://zguide.zeromq.org/ |
| zguide 第 5 章 | XPUB/XSUB 代理、Espresso 追踪、Last Value Cache | https://zguide.zeromq.org/docs/chapter5/ |
| libzmq API 参考 | `zmq_socket` / `zmq_bind` / `zmq_proxy` / `zmq_setsockopt` | https://libzmq.readthedocs.io/en/latest/ |
| pyzmq 文档 | Python 绑定与示例 | https://pyzmq.readthedocs.io/en/latest/ |
| events_common.h | 两帧消息格式、四个端点默认值、boost 序列化实现 | https://github.com/sonic-net/sonic-swss-common/blob/master/common/events_common.h |
| events.cpp | publisher/subscriber 的 socket 建立与选项（`LINGER`/`SUBSCRIBE`/`RCVTIMEO`） | https://github.com/sonic-net/sonic-swss-common/blob/master/common/events.cpp |
| eventd.cpp | 代理实现：`eventd_proxy::run()` 建 XSUB/XPUB/capture 并调 `zmq_proxy()`；可据此确认代理是线程而非进程 | https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-eventd/src/eventd.cpp |
| events_publish_tool.py | 官方发布工具：Python 侧 `events_init_publisher` / `event_publish` / `FieldValueMap` 的可用示例 | https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-eventd/tools/events_publish_tool.py |

## 8 待核实项

| # | 问题 | 为何重要 | 建议验证方式 |
|---|---|---|---|
| 1 | 目标版本是 `telemetry` 还是 `gnmi` 容器 | 容器名/单元名/镜像名全不同 | `docker ps`、`show feature status` |
| 2 | 实际 gNMI 端口与认证模式 | 默认 8080、默认 `cert`，发行版可能改 | `redis-cli -n 4 HGETALL "TELEMETRY\|gnmi"` |
| 3 | 各计数器组实际轮询间隔 | 决定可达到的最小采集粒度 | `counterpoll show` |
| 4 | 平台是否支持 HFST / INT | 决定能否做毫秒级诊断 | 查芯片与厂商发行版说明 |
| 5 | 多 ASIC / DPU 的容器与命名空间布局 | 影响采集寻址与 Redis 实例选择 | `ip netns list`、`docker ps` |
| 6 | `STATE_DB` 中平台表的版本差异 | 光模块/传感器字段名随版本变化 | `redis-cli -n 6 KEYS '*'` 抽样比对 |
| 7 | ZMQ 端点是否被改过、是否暴露到网络 | 决定能否跨机直连 5571，且涉及安全边界 | `jq .events /etc/sonic/init_cfg.json`、`ss -ltnp \| grep 557` |

---

## 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v0.1 | 2026-11-10 | 首版：整体组成、采集框架、容器角色、参考链接与待核实项 |
| v0.2 | 2026-11-10 | 新增 [[#3.6 跨容器访问 Redis 的具体机制\|§3.6]] 跨容器访问 Redis 的机制：bind mount + Unix socket、三条通道、database_config.json 与失败模式 |
| v0.3 | 2026-11-10 | 重写 [[#3.5 三类非 Redis 数据的采集路径\|§3.5]]：非 DB 数据（non_db_client 直读 /proc）、事件流（eventd 的 ZMQ 代理 + EventDB）、平台硬件（pmon 独占 I2C → STATE_DB）三条路径，补三条路径对比与工程含义 |
| v0.4 | 2026-11-11 | 新增 [[#3.7 ZeroMQ（ZMQ）是什么、怎么用\|§3.7]] ZeroMQ 基础与用法：库与中间件的区别、六种 socket 模式、`bind`/`connect` 语义、SONiC 四端点与两帧消息、三条消费路径（含 pyzmq 骨架）、四个坑与选型建议；补 [[#7.6 ZeroMQ 与事件传输\|§7.6]] 参考资料与待核实项第 7 条 |
| v0.5 | 2026-11-11 | 新增 [[#3.7.8 四个高频疑问\|§3.7.8]] 四个高频疑问（两帧的收益、zmqproxy 的目的、发布者与订阅者清单）；更正三处：pmon 守护进程不调 `event_publish`、bgp/swss/syncd 事件主要来自 rsyslog 正则、[[#3.5.2 系统事件流：ZMQ 代理跑在 eventd 容器里\|§3.5.2]] 拓扑图的生产者改为"直接调 API + rsyslog 插件" |
| v0.6 | 2026-11-11 | [[#3.7.4 SONiC 的具体用法（源码确认）\|§3.7.4]] 补"这条链路不经过 Redis"：六段跳转的传输方式对照、ZMQ PUB/SUB 与 Redis PUBLISH/SUBSCRIBE 的区别、`ss` 验证命令 |
| v0.7 | 2026-11-11 | 新增 [[#3.7.9 生产者链接的是哪个库：建连与发送的完整调用链\|§3.7.9]]：libzmq / libswsscommon / 代理三层辨析、初始化六步与发送五步（含 `echo_send` 探测与 slow joiner）、C++ 与 Python 两种写法、四条验证命令；**更正结构性错误**：不存在独立 `zmqproxy` 进程，代理是 `eventd_proxy::run()` 线程（`zmq_proxy()` 在 eventd 进程内），同步修正 [[#3.5.2 系统事件流：ZMQ 代理跑在 eventd 容器里\|§3.5.2]]、[[#3.7.4 SONiC 的具体用法（源码确认）\|§3.7.4]]、[[#3.7.8 四个高频疑问\|§3.7.8]] 九处表述 |
