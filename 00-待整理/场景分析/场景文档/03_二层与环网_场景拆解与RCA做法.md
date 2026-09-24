# 二层与环网　场景拆解与 RCA 做法

> **大场景ID**：`DS-L2`　|　**归属领域**：二层与环网　|　**记录条数**：80 条　|　**子场景**：10 个

> **已归类 69 条**　|　**机理缺失 11 条**　|　**机理属他场景待外归 0 条**

> **数据来源**：飞书表格 Sheet8 市场故障工单（按表内「领域」列归入本大场景）

> **归类方法**：领域专家逐条阅读「根因 + 方案」字段的技术失效机理；「主题」「原表标签」仅作提示

> **版本**：v2（经 2 位交换机专家交叉评审 2 轮修订）


---

## 一、场景定义与边界

### 1.1 场景定义

二层与环网（DS-L2）覆盖交换机在数据链路层（L2）及环网保护相关的功能与故障，包括 VLAN / 协议VLAN / superVLAN / QinQ 等二层隔离与标签技术、MAC 地址学习/老化/漂移、生成树（STP/MSTP）/环路检测（RLDP）/环网保护（ERPS）、链路聚合（LACP/AP）、二层组播、ACL/VLAN CLASS 等二层表项与匹配，以及上送 CPU 的二层控制报文与 L2 表项（TCAM/SDK/芯片寄存器）处理。其技术内涵是：二层转发依赖 MAC 表、VLAN 表、STP 状态、聚合/环网状态等软硬结合的数据面与控制面协同，任何一层（配置未生效、表项未下发/残留、芯片寄存器异常、进程挂死、资源耗尽）出错都会表现为不通、丢包、环路或显示异常。

### 1.2 边界判据

**属于本场景：**

- VLAN/协议VLAN/superVLAN/QinQ 等二层隔离与标签功能不生效或标签解析错误
- MAC 表项学习/老化/漂移异常
- 生成树/环路检测/环网保护（STP/MSTP/RLDP/ERPS）异常
- 链路聚合（LACP/AP）协商/震荡/显示异常
- 二层 ACL/VLAN CLASS 匹配与残留异常
- 上送 CPU 的二层控制报文与 L2 表项（TCAM/SDK/寄存器）处理异常
- 接口 LINK 状态通告与芯片中断掩码异常
- 二层组播、二层转发面丢包
- 配置丢失/未持久化与 WEB/EMB/CLI/SNMP/sFlow 管理面异常
- MMU/内存/表项资源耗尽

**不属于本场景（易误入，需外归）：**

- 三层路由/网关不通、VRF、静态路由等归属『三层路由（DS-L3）』；本场景仅收纳 VRF/VLAN 引发的二层表象（如 row=682 内核挂死上送、row=92 SVI配VRF致组播不泛洪）
- DHCP 地址分配协议交互本身（lease/DORA 流程）归属『DHCP 场景』；本场景仅收纳『二层/VLAN/表项导致的 DHCP 不通表象』（如 row=200 AM 规则、row=595 直连获取失败无环路）
- 无线终端接入/AP 转发归属『无线（WLAN）』（如旧归类线索『无线终端接入转发失败』）
- 安全 ACL/QoS 策略本身的策略语义错误归属『安全/QoS』；本场景仅收纳『ACL/VLAN CLASS 表项匹配或残留导致的二层误生效』
- 硬件单板物理损坏、光模块发光硬件故障归属『硬件/单板』；本场景仅收纳『芯片寄存器/驱动软件导致接口 Up/收发包中断』
- 堆叠/VSU 分裂主备切换本身归属『堆叠/VSU（DS-STACK）』；本场景仅收纳『分裂/切换触发的 STP/LACP/RLDP 二层状态异常』（如 row=793、row=582）

---

## 二、这个场景是怎么拆出来的

### 2.1 拆解维度

| 维度 | 取值 | 为什么按这个维度切 |
|---|---|---|
| 失效层面（控制面/数据面/管理面） | 控制面(STP/LACP/表项下发/上送CPU)／数据面(转发/标签/丢包/MAC)／管理面(WEB/EMB/CLI/SNMP/sFlow/配置持久化) | 决定排查入口与可观测点：控制面看协议状态与表项，数据面看转发计数与标签，管理面看配置与采集。三层入口命令完全不同，必须分开。 |
| 二层对象/表项类型 | VLAN/协议VLAN/superVLAN/QinQ／MAC 表／STP/MSTP/RLDP/ERPS／LACP/AP 聚合／ACL/VLAN CLASS／组播/转发面／芯片寄存器/TCAM/SDK／接口 LINK | 不同对象对应不同命令与失效机理（如 MAC 表残留与 VLAN CLASS 残留排查命令不同），规程要求必须严格区分。 |
| 拓扑/功能角色 | 接入/下联／核心/上联／VSU/堆叠／MLAG/peer-link／降速模块(万兆口用千兆模块) | 降速模块触发 MMU/标签识别错误（row=141/530/637/685/831/878），MLAG peer-link 裁剪导致 MAC 漂移（row=615），需按角色定位。 |

### 2.2 拆解原则

1. **机理优先**：以「根因 + 方案」里的技术失效机理作为第一判据，不按主题字面归类。
2. **排查动作一致**：同一个子场景内的记录，必须能用**同一套排查动作**定位；做不到就再拆。
3. **不硬凑**：机理描述缺失的记录不强行塞进任何子场景；机理明确属于别的大场景的记录，标为「待外归」而非塞进兜底子场景。

### 2.3 子场景总览

| 子场景ID | 子场景名称 | 机理定义 | 条数 | 占已归类比 |
|---|---|---|---:|---:|
| `DS-L2-07` | 上送 CPU / 二层表项分配 / 转发面丢包异常 | 二层转发依赖的 TCAM/SDK 表项（my_station_tcam、VLAN CLASS、fpem）、控制面进程（DHCP/AM、ce.l3intf.sw、内核）、以及上下层（CLI/SSA/SDK）状态一致性异常，导致 ARP/三层转发/组播/RS 等报文被丢弃或上送异常；也包括芯片对分片/收包解析出错导致的二层转发丢包。 | 12 | 17.4% |
| `DS-L2-09` | 配置丢失/未持久化 与 WEB/EMB/CLI/SNMP/sFlow 管理显示面异常 | 配置因版本缺陷、模块混用（DC/ED 卡）、EMB 逻辑、ZCM 功能等，在重启或 WEB 操作下丢失或未下发；WEB/EMB/CLI/SNMP/sFlow 管理面因版本 BUG 或逻辑缺陷导致加载慢、配置清空、OID 不支持、采样缺失、丢包计数显示。 | 12 | 17.4% |
| `DS-L2-01` | 协议VLAN/IP子网VLAN/superVLAN 功能不生效 | 协议VLAN（基于协议/IP子网划分VLAN）、superVLAN/subVLAN、普通业务VLAN 因版本BUG、配置未生效，或与其他二层特性（protocol-vlan 走 ACL 匹配、supervlan 走 SCL 匹配）叠加冲突，导致 VLAN 功能不生效、对应网段不通。 | 9 | 13.0% |
| `DS-L2-06` | 链路聚合（LACP/AP）协商/显示/震荡异常 | 聚合口因软件显示 BUG、LACP 协商/选举逻辑、线程冲突误自愈、速率下发顺序、堆叠分裂或切换逻辑等，表现为速率显示错误、单端口 susp、LACP 震荡、聚合口失效或影响其他聚合口。 | 7 | 10.1% |
| `DS-L2-02` | 万兆光口降速千兆 VLAN 标签解析错误 | 5300-L 等定制版本在万兆光口降速为千兆（使用千兆模块）工作时，MAC 芯片将报文自带的 outer vlan tag 错误识别为 inner vlan tag，导致非 vlan1（如管理 VLAN、native VLAN≠1）网段无法 Ping 通/通信；同类还有收包单层标签被快转打印为双层的解析错误。 | 5 | 7.2% |
| `DS-L2-04` | 生成树/环路检测/环网保护（STP/MSTP/RLDP/ERPS）异常 | 生成树（STP/MSTP）阻塞端口状态、环路检测（RLDP）、环网保护（ERPS）因软件逻辑缺陷、配置冲突、堆叠分裂未收到 BPDU、或启机同步超时而失效，导致环路、误报环路或保护不生效。 | 5 | 7.2% |
| `DS-L2-05` | 二层 ACL / VLAN CLASS 匹配与残留异常 | SVI 下 ACL（router-acl）、VLAN CLASS（acl_label/classid）因芯片硬件限制、acl_label mask 问题、或 ACL 调用残留（残留 ACL 的 classid 与另一 VLAN 的 classid 一致），导致 ACL 跨卡不生效、业务叠加失败或跨 VLAN 误生效。 | 5 | 7.2% |
| `DS-L2-08` | 接口 LINK 状态通告 / 芯片寄存器中断异常 | 接口 LINK 状态在 CLI 与底层（SSA/驱动）不一致、内联口未通告无成员口、或线卡芯片中断掩码寄存器异常，导致接口状态错误、收发包中断、协议（LACP/VSL/ARP/ICMP）异常。 | 5 | 7.2% |
| `DS-L2-10` | MMU/内存/表项资源耗尽异常 | 芯片 MMU（队头阻塞 holdrop）、系统内存泄漏、或 VLAN 映射 range 资源（芯片资源总数 64）耗尽，导致端口丢包、业务中断或 QINQ 不生效。 | 5 | 7.2% |
| `DS-L2-03` | MAC 表项学习/老化/漂移异常 | MAC 地址表因 share-vlan 复制机制、软件表项残留、MLAG peer-link 同步未裁剪 VLAN、或环路等原因，出现 MAC 残留、表项沾满、MAC 漂移，导致转发异常。 | 4 | 5.8% |
| | **合计** | | **69** | 100% |

---

## 三、子场景明细

### DS-L2-07　上送 CPU / 二层表项分配 / 转发面丢包异常（12 条）

- **机理定义**：二层转发依赖的 TCAM/SDK 表项（my_station_tcam、VLAN CLASS、fpem）、控制面进程（DHCP/AM、ce.l3intf.sw、内核）、以及上下层（CLI/SSA/SDK）状态一致性异常，导致 ARP/三层转发/组播/RS 等报文被丢弃或上送异常；也包括芯片对分片/收包解析出错导致的二层转发丢包。
- **归类判据**：满足：① supervlan 的 subvlan 未下发底层（my_station_tcam 异常）；② PE-vlan 未下发线卡；③ 进程异常（PID 冲突致 l3intf 进程未拉起、DHCP/AM 规则异常、VRF 增删内核挂死）；④ VLAN CLASS 残留（PBR 删除时序）；⑤ 跨三层转发丢包（软件问题，重启恢复）；⑥ ofdpa 软件缓存 vid 错误致 ARP 上送异常；⑦ 上下层 STP 状态不一致致 RS 报文未转发；⑧ 芯片丢弃分片报文；⑨ SVI 配 VRF 致二层组播无法泛洪。机理为表项/进程/上送/转发面。
- **典型现象**：sub/super vlan 不通、新增 VLAN 后与网关不通、终端获取不到 IP、VRF 配 VLAN 无法 ping 网关、三层转发丢包、二层组播不转发、分片报文转发异常、ARP 被丢弃、RS 未转发。
- **排查动作**：1) show l2-table 底层诊断看 TCAM（my_station_tcam、fpem、vlan class）是否下发（待实机核对）；2) show arp / show mac-address-table 确认表项；3) show ip interface / show vlan 确认 SVI 与 VLAN 绑定；4) show process 看关键进程（ce.l3intf.sw、dhcpd、ssc）是否拉起；5) show cpu-protect / debug 上送 CPU 的报文（ARP/RS/ICMP）；6) 检查 CLI/SSA/SDK 上下层状态一致性；7) 升级/重启规避。
- **记录抽样**：
    - Sheet8行 94（CS20230823-2287548）：N18012 直连不通，sub vlan下设备不能和super vlan互通
    - Sheet8行 186（CS20230423-1690064）：RG-S7805C 上周六客户在25、26、27口下加了三台我司交换机后，vlan199下电脑终端无法学习到其他终端arp信息（同网段跨网段都是），拔掉三台设备后故障未恢复，后从S
    - Sheet8行 200（CS20230403-1594256）：RG-N18012 终端获取不到ip地址

### DS-L2-09　配置丢失/未持久化 与 WEB/EMB/CLI/SNMP/sFlow 管理显示面异常（12 条）

- **机理定义**：配置因版本缺陷、模块混用（DC/ED 卡）、EMB 逻辑、ZCM 功能等，在重启或 WEB 操作下丢失或未下发；WEB/EMB/CLI/SNMP/sFlow 管理面因版本 BUG 或逻辑缺陷导致加载慢、配置清空、OID 不支持、采样缺失、丢包计数显示。
- **归类判据**：满足：① VLAN/CE-VLAN 配置因重启/模块混用/ZCM 丢失；② WEB/EMB 创建地址池清空接口配置、模板缺 native vlan 致下发卡住；③ 聚合口配置失效；④ WEB 界面加载慢；⑤ SNMP OID 不支持；⑥ sFlow 未携带 vlan_id；⑦ 接口 drop 计数因 rdbgc 寄存器统计预期丢包被显示；⑧ option43 默认 vlan1 下发。机理为管理/配置/显示面，非数据面转发。
- **典型现象**：vlan 配置丢失、WEB 配置被清空、设备卡在下发配置中、聚合口失效、WEB 加载慢、OID 读取报错、sFlow 缺 vlan_id、接口 drop 计数显示、option43 下发异常。
- **排查动作**：1) show running-config 确认配置是否真实存在/丢失；2) show version / show flash 确认版本与补丁；3) 检查 EMB 数据库 native vlan / 模板完整性；4) show snmp 验证 OID 支持；5) show sflow 配置与采样；6) show interface GigabitEthernet 0/1 counters 看计数；7) 升级版本/补丁、清除残留模块信息（remove configuration module）。
- **记录抽样**：
    - Sheet8行 153（CS20230615-1953849）：晋兴职院S5760X vlan配置丢失
    - Sheet8行 416（CS20240627-3738649）：【中国移动通信集团湖南有限公司株洲分公司】【N18007】湖南化工学院校园网有线网络无法获取IP地址；
    - Sheet8行 369（CS20240912-4119905）：【故障】光交换机上配置option 43字段，刚开启阶段默认全部vlan 1会导致下发造成A[切换macc默认

### DS-L2-01　协议VLAN/IP子网VLAN/superVLAN 功能不生效（9 条）

- **机理定义**：协议VLAN（基于协议/IP子网划分VLAN）、superVLAN/subVLAN、普通业务VLAN 因版本BUG、配置未生效，或与其他二层特性（protocol-vlan 走 ACL 匹配、supervlan 走 SCL 匹配）叠加冲突，导致 VLAN 功能不生效、对应网段不通。
- **归类判据**：满足以下之一：① 配置 protocol-vlan/IP子网VLAN 后接口不按预期打标签或终端无法通信；② supervlan/subvlan 互通异常或与 protocol-vlan 优先级冲突；③ 仅 vlan1 通而其他业务 VLAN 不通且定位为版本问题；④ VLAN 接口 IPv6 地址因掩码等配置错误报错。且不归属标签解析错误（DS-L2-02）或 QINQ 资源（DS-L2-10）。
- **典型现象**：协议VLAN不生效、只有vlan1能通、supervlan与protocol-vlan叠加导致subvlan间不通、基于IP划分vlan不生效、协议vlan与友商设备不互通、VLAN接口IPv6掩码配置报错。
- **排查动作**：1) show vlan / show vlan private-map 确认 VLAN 与 subVLAN/superVLAN 关系；2) show protocol-vlan / show running-config | include protocol-vlan 确认协议VLAN绑定；3) show vlan internal 与 ACL/SCL 匹配优先级核对功能叠加冲突；4) 检查版本，升级至修复版本（如 B0702P4、最新正式版）；5) 核对 IPv6 地址掩码等配置合法性。
- **记录抽样**：
    - Sheet8行 173（CS20230519-1808462）：RG-S2910V2-24GT4XS-L 协议vlan不生效
    - Sheet8行 252（CS20230215-1327510）：【故障】RG-S5310-48GT4XS-E 协议vlan不生效
    - Sheet8行 655（CS20250612-5283740）：RG-S5300-48GT4XS-P-L只有vlan1能通，其他vlan都不通

### DS-L2-06　链路聚合（LACP/AP）协商/显示/震荡异常（7 条）

- **机理定义**：聚合口因软件显示 BUG、LACP 协商/选举逻辑、线程冲突误自愈、速率下发顺序、堆叠分裂或切换逻辑等，表现为速率显示错误、单端口 susp、LACP 震荡、聚合口失效或影响其他聚合口。
- **归类判据**：满足：① 聚合口速率显示异常（软件显示 BUG，不影响业务）；② LACP 单端口 susp 因千兆模块降速触发 MMU；③ 带外检测与 DMA 线程冲突误自愈致 LACP 震荡；④ 主备聚合口手动 shutdown 不切换需接口优先级；⑤ 内存高致 ssc 进程反复拉起 LACP 异常；⑥ 成员口速率下发顺序异常影响其他聚合口；⑦ 堆叠/VSU 分裂 LACP 未协商。机理为 LACP/聚合口层面（非纯芯片寄存器，寄存器类已归 DS-L2-08）。
- **典型现象**：聚合口速率显示异常、LACP 单端口 susp、LACP 震荡、聚合口失效、聚合口重启影响其他口、主备聚合口不切换。
- **排查动作**：1) show lacp summary / show lacp neighbor 看 LACP 协商与成员口状态；2) show aggregatePort summary 看聚合口速率/成员/状态；3) show interface counters 与 show logging | include LACP 看震荡与丢包；4) show memory / show process 看内存与进程（ssc）；5) 检查成员口速率配置、升级版本、必要时主备切换。
- **记录抽样**：
    - Sheet8行 131（CS20230706-2058516）：S6120 聚合口速率显示异常，客户质疑产品
    - Sheet8行 132（CS20230705-2054841）：RG-N18012 聚合口速率显示异常，客户质疑产品
    - Sheet8行 257（CS20230210-1302982）：N18007 2个10G的接口聚合之后聚合口的速率只有10G

### DS-L2-02　万兆光口降速千兆 VLAN 标签解析错误（5 条）

- **机理定义**：5300-L 等定制版本在万兆光口降速为千兆（使用千兆模块）工作时，MAC 芯片将报文自带的 outer vlan tag 错误识别为 inner vlan tag，导致非 vlan1（如管理 VLAN、native VLAN≠1）网段无法 Ping 通/通信；同类还有收包单层标签被快转打印为双层的解析错误。
- **归类判据**：满足：设备为 5300-L/53-L 系列，万兆光口接千兆模块降速工作，非 vlan1 网段不通/管理网段不通，且根因定位为 outer/inner vlan tag 识别错误或收包标签解析错误（同一机理出现在 row=530/685/831/878/296）。
- **典型现象**：native vlan1 时 VLAN310 不通、除 vlan1 外网段无法通信、核心串接不通、直连核心无法通信、收包单层标签被快转打印为双层。
- **排查动作**：1) show interface GigabitEthernet 0/1 确认光口速率（是否为千兆降速）；2) show vlan 确认业务 VLAN 与 native VLAN；3) 确认是否万兆口使用千兆模块；4) 升级定制版本（如 S5300-L_RGOS 12.6(3)B0702P2）；规避：将光口配置为万兆速率或空配启机后不再重启。
- **记录抽样**：
    - Sheet8行 530（CS20251223-6088190）：RG-S5300-48GT4XS-P-L同型号设备互联端口配置native vlan 1时，VLAN 310管理地址通信不通，必须打VLAN 310标签才可通信；
    - Sheet8行 685（CS20250428-5098876）：【故障】53-L设备直连核心无法通信，影响客户项目交付
    - Sheet8行 831（CS20260415-6461090）：核心交换机串接不通

### DS-L2-04　生成树/环路检测/环网保护（STP/MSTP/RLDP/ERPS）异常（5 条）

- **机理定义**：生成树（STP/MSTP）阻塞端口状态、环路检测（RLDP）、环网保护（ERPS）因软件逻辑缺陷、配置冲突、堆叠分裂未收到 BPDU、或启机同步超时而失效，导致环路、误报环路或保护不生效。
- **归类判据**：满足：① 配置 DAD 未关闭 LLDP 导致环路日志误报；② BRIDGE 模块整合 STP Block 与 RLDP Forward 状态逻辑缺陷形成环路；③ RLDP 接口加入 AP 被强制 shutdown 致主从切换配置变化；④ 堆叠分裂后聚合下连口未收到 BPDU 被 block；⑤ ERPS 启机向 BRIDGE 申请 VLAN 超时致配置丢失。机理明确为 STP/RLDP/ERPS 状态或保护失效。
- **典型现象**：LLDP 告警 DAD 端口环路、环路引发全网中断、RLDP 配置变化、VSU 切换下连口 block、ERPS 配置丢失。
- **排查动作**：1) show spanning-tree 看端口角色/状态（是否 Block）；2) show rldp 看环路检测状态与防护动作；3) show erps 看环网保护状态；4) show logging 看 BPDU/环路/ERPS 日志；5) 检查 DAD/LLDP 配置冲突、堆叠分裂与 BPDU 收发；6) 升级版本。
- **记录抽样**：
    - Sheet8行 46（CS20231031-2639976）：设备：S5700V2-l，11.4（1）B74，LLDP告警DAD端口存在环路
    - Sheet8行 575（CS20251017-5809946）：【运行维护】顺丰 572W场地S5310E环路引发全网中断
    - Sheet8行 582（CS20250925-5732834）：中国建设银行四川省分行S7808C-X执行主从切换后RLDP配置变化故障处理

### DS-L2-05　二层 ACL / VLAN CLASS 匹配与残留异常（5 条）

- **机理定义**：SVI 下 ACL（router-acl）、VLAN CLASS（acl_label/classid）因芯片硬件限制、acl_label mask 问题、或 ACL 调用残留（残留 ACL 的 classid 与另一 VLAN 的 classid 一致），导致 ACL 跨卡不生效、业务叠加失败或跨 VLAN 误生效。
- **归类判据**：满足：① SVI router-acl 跨卡三层流不生效（芯片硬件限制）；② IPv6 fpem 表项 acl_label mask 问题致业务叠加失败；③ vlanif ACL 调用残留，classid 一致导致 ACL 在另一 VLAN 同步误生效；④ svi router-acls enable 重启后上下层不一致致 ACL 过滤二三层流量。机理为 ACL/VLAN CLASS 表项匹配或残留。
- **典型现象**：VRRP 下 ACL 时通时不通、IPv6 业务叠加失败、vlanif ACL 残留致其他 VLAN 也生效、svi router-acl 重启后上下层不一致过滤流量。
- **排查动作**：1) show access-list 看 ACL 定义与调用；2) show vlan class / show vlan class-id 看 classid 映射；3) 诊断命令确认 svi router-acl 实际生效状态（上下层一致）；4) 核对各 VLAN 调用的 ACL 的 classid 是否冲突；5) 同线卡聚合/规避跨卡、重新配置或升级。
- **记录抽样**：
    - Sheet8行 12（CS20231218-2889357）：设备：N18E_RGOS 12.6(2)B0302T1, Release(10162813)，VRRP下调用ACL异常问题
    - Sheet8行 55（CS20231021-2592229）：阿里办公网飞天园区57X设备新增VLAN403网段V6业务不通
    - Sheet8行 792（CS20260609-6666263）：建行S7808C出现调用acl导致业务异常

### DS-L2-08　接口 LINK 状态通告 / 芯片寄存器中断异常（5 条）

- **机理定义**：接口 LINK 状态在 CLI 与底层（SSA/驱动）不一致、内联口未通告无成员口、或线卡芯片中断掩码寄存器异常，导致接口状态错误、收发包中断、协议（LACP/VSL/ARP/ICMP）异常。
- **归类判据**：满足：① 未插模块接口仍 UP，LINK 通告丢失，CLI 与底层 LINK 不一致；② 线卡中断掩码寄存器异常无法收包（LACP/VSL/ARP/ICMP 异常），shutdown 后面板口恢复；③ 内联口软件未通告，无成员口，三层转发异常；④ 线卡芯片寄存器中断掩码异常致接口无法 UP、LACP 震荡（VSU 代理卡场景）。机理为接口/LINK/寄存器层面。
- **典型现象**：未插模块接口 UP、线卡无法收包、内联口无成员口三层转发异常、单板端口故障 LACP 震荡。
- **排查动作**：1) show interface GigabitEthernet 0/1 看 LINK/物理状态；2) 对比 CLI 与底层（diagnose/SSA）LINK 状态一致性；3) 检查内联口成员口是否下发；4) 寄存器层面需诊断命令（diagnose-cmd 查中断掩码）或 shutdown/no shutdown 恢复；5) 升级版本。
- **记录抽样**：
    - Sheet8行 58（CS20231013-2549213）：RG-S7810C-X 接口状态异常，未插入模块依旧UP，影响对应整网流量负载
    - Sheet8行 110（CS20230803-2194281）：广东移动彩铃网络S7910E交换机下挂文件服务器IP地址ping不通网关故障
    - Sheet8行 415（CS20240701-3757970）：【故障】S7808C 三层流量转发异常

### DS-L2-10　MMU/内存/表项资源耗尽异常（5 条）

- **机理定义**：芯片 MMU（队头阻塞 holdrop）、系统内存泄漏、或 VLAN 映射 range 资源（芯片资源总数 64）耗尽，导致端口丢包、业务中断或 QINQ 不生效。
- **归类判据**：满足：① 万兆口用千兆模块重启触发 MMU 异常，报文残留致 HOLDROP/队头阻塞；② 内存利用率持续增长（命中泄漏预警）致性能劣化；③ VLAN 映射（灵活 QINQ/vlan mapping）range 资源超过 64 致资源不足。机理为资源耗尽。
- **典型现象**：LACP 单端口 susp/生成树异常伴 holdrop、上传网速慢内存高、QINQ 一对多不生效。
- **排查动作**：1) show mmu（待实机核对）/ 芯片诊断看 MMU 拥塞与 holdrop 计数；2) show memory / show process memory 看内存趋势；3) show l2-table resource（待实机核对）/ 相关 range 资源计数看 VLAN 映射资源占用，或改用 show mac-address-table count 看表项占用；4) 升级版本、避免千兆模块降速、减少 range 资源占用。
- **记录抽样**：
    - Sheet8行 141（CS20230625-1994716）：29与5760组件LACP出现单端口susp问题
    - Sheet8行 395（CS20240814-3960549）：S7620 qinq一对多不生效
    - Sheet8行 539（CS20251211-6038886）：RG-S6120-20XS4VS2QXS 设备下联终端测试上传网速慢

### DS-L2-03　MAC 表项学习/老化/漂移异常（4 条）

- **机理定义**：MAC 地址表因 share-vlan 复制机制、软件表项残留、MLAG peer-link 同步未裁剪 VLAN、或环路等原因，出现 MAC 残留、表项沾满、MAC 漂移，导致转发异常。
- **归类判据**：满足：① 已关闭/迁移接口仍残留或异常复制 MAC（share vlan 复制过多致表沾满）；② 软件表项残留导致 AP 出口终端流量异常；③ MLAG 同步 MAC 未对 peer-link 裁剪 VLAN 导致单归口 MAC 漂移；④ 上联口出现 MAC 漂移且怀疑环路。机理为 MAC 学习/老化/漂移，非纯 STP 环路。
- **典型现象**：已关闭接口学习到正常接口 MAC、share vlan 复制 MAC 致表满、软件表项残留、MLAG 同步 MAC 漂移、MAC 漂移至上联口。
- **排查动作**：1) show mac-address-table count 看表项是否沾满；2) show mac-address-table dynamic <vlan> 看 MAC 与接口对应；3) show logging | include MAC 看 MAC 学习/漂移日志；4) 检查 share vlan 配置（show vlan private-map）并评估去留；5) MLAG 场景检查 peer-link VLAN 裁剪；6) 检查是否环路。
- **记录抽样**：
    - Sheet8行 119（CS20230723-2137962）：已关闭的接口学习到正常打开接口的mac地址导致转发异常 现网环境，影响范围较大 M8606-CM III
    - Sheet8行 328（CS20241025-4325216）：宁波大学 N18E 下联一个终端无法访问服务器
    - Sheet8行 614（CS20250810-5527553）：RG-S6150-48VS8CQ-XMAC地址漂移至上联口

---

## 四、RCA 根因分析怎么做（本场景）

### 4.1 技术链

现象（不通/丢包/环路/显示异常）→ 触发路径（版本 BUG/配置变更/降速模块/重启/资源增长）→ 失效点（表项未下发或残留 / 芯片寄存器或 MMU / 协议状态不一致 / 资源耗尽）→ 直接根因（软件缺陷/配置未生效/硬件限制/资源不足）

### 4.2 失效点分类

| 失效点 | 说明 | 典型记录（Sheet8行） |
|---|---|---|
| 二层表项未下发/残留（TCAM/VLAN CLASS/fpem/my_station_tcam） | CLI 配置未在 SSA/SDK 层落地或残留，导致 VLAN/ACL/ARP 行为异常 | 94、289、683、792、863、883 |
| 芯片寄存器/驱动中断异常（中断掩码、LINK 通告） | 线卡中断掩码寄存器或 LINK 通告丢失，导致收发包中断、接口状态错误 | 58、110、591、851、415 |
| 协议状态不一致（STP/RLDP/BPDU/上下层） | 控制面协议状态在模块间或上下层不一致，导致阻塞失效/环路/误 block | 46、575、582、793、885 |
| 资源耗尽（MMU/内存/range） | MMU 拥塞、内存泄漏、VLAN 映射 range 资源超 64，导致丢包/不生效 | 141、539、637、776、395 |
| 配置丢失/未持久化/管理面逻辑 | 重启/EMB/ZCM/模块混用导致配置丢失或 WEB/EMB/SNMP 逻辑错误 | 153、416、725、619、762、772、833、746 |
| 标签解析/转发面处理错误 | 降速千兆 outer/inner tag 识别错误、收包解析错误、芯片丢弃分片 | 530、685、831、878、296、40 |

### 4.3 排查动作步骤（按序执行）

> 标注「待实机核对」的命令，表示该写法尚未在真机/模拟器上确认，使用前请先验证。

| 步 | 动作 | 命令 / 观测点 | 判读 |
|---:|---|---|---|
| 1 | 确认故障 VLAN/接口/聚合口范围与状态 | `show vlan / show interface GigabitEthernet 0/1 / show aggregatePort summary / show lacp summary` | 定位是哪个二层对象异常，区分 VLAN/聚合/接口 |
| 2 | 检查二层表项与上下层一致性 | `show mac-address-table / show arp / show l2-table（待实机核对） / diagnose 查 TCAM(my_station_tcam、fpem、vlan class)` | 表项是否存在、接口是否正确、是否残留或未下发 |
| 3 | 检查协议状态（STP/RLDP/ERPS/LACP/上送） | `show spanning-tree / show rldp / show erps / show lacp / show cpu-protect` | 阻塞端口是否真阻塞、BPDU 是否收发、LACP 是否协商、控制报文是否上送 |
| 4 | 检查接口 LINK 与芯片寄存器/MMU | `show interface GigabitEthernet 0/1(对比 CLI 与底层 LINK) / diagnose-cmd 查中断掩码 / show mmu（待实机核对）` | LINK 上下层是否一致、中断掩码是否异常、是否 holdrop |
| 5 | 检查资源与内存 | `show memory / show process / show l2-table resource（待实机核对）或 show mac-address-table count` | 内存趋势、range 资源占用是否超阈值(64) |
| 6 | 核对配置持久化与管理面 | `show running-config / show version / EMB 数据库 native vlan / SNMP OID / sFlow 配置` | 配置是否丢失、版本是否命中已知 BUG、管理面是否异常 |
| 7 | 确认版本与规避/升级 | `show version / 已知 BUG 列表` | 是否命中已知版本缺陷，决定升级或规避（如千兆模块改万兆速率） |

### 4.4 所需可观测点

| 观测点 | 数据源 | 现状 |
|---|---|---|
| MAC 表/ARP 表 | 表项(show mac-address-table/arp) | 现有（CLI 可查），但底层 TCAM 详情需诊断权限 |
| VLAN/协议VLAN/superVLAN 配置与内部态 | 配置/表项(show vlan / protocol-vlan / private-map) | 现有，但功能叠加冲突(ACL vs SCL 优先级)无现成视图 |
| STP/RLDP/ERPS 状态与 BPDU | 协议状态/日志 | 现有(show spanning-tree/rldp/erps)，BPDU 收发计数视图弱 |
| LACP/聚合口状态 | 协议状态(show lacp/agg) | 现有 |
| 接口 LINK/计数器/寄存器 | 接口/诊断(show interface GigabitEthernet 0/1 / diagnose 中断掩码 / rdbgc) | 部分缺失：底层寄存器需 diagnose，LINK 上下层一致性无自动比对 |
| CPU 上送与控制面报文 | cpu-protect/日志 | 现有但粒度粗，ARP/RS/ICMP 上送失败难细分 |
| 内存/进程/MMU/range 资源 | 指标(show memory / show process / show l2-table resource（待实机核对）或 show mac-address-table count) | 现有但缺历史趋势与阈值告警 |
| 配置持久化/EMB/SNMP/sFlow | 配置/管理面 | 配置丢失难回溯(无配置变更审计)，sFlow vlan_id 等解析缺陷需版本修复 |

### 4.5 常见根因模式

| 根因模式 | 普遍度 | 典型记录（Sheet8行） |
|---|---|---|
| 版本 BUG 导致 VLAN/协议VLAN/ACL 功能不生效或配置未下发 | 高 | 173、252、655、839、872、289、94 |
| 万兆口降速千兆 outer/inner vlan tag 识别错误（5300-L） | 中 | 530、685、831、878、296 |
| 软硬件表项不一致（TCAM/VLAN CLASS 残留或未下发） | 高 | 683、792、863、883、94、289 |
| 芯片寄存器/MMU 异常（中断掩码、holdrop） | 中 | 110、591、851、141、637 |
| 配置丢失/未持久化（重启/EMB/ZCM/模块混用） | 中 | 153、416、725、619、762、772 |
| 内存/资源耗尽（泄漏、range 超 64） | 低 | 539、776、395 |
| STP/RLDP/ERPS 环路保护状态失效 | 中 | 46、575、582、793、888 |

### 4.6 成功 / 失败对比要点

成功定位的工单均具备『明确版本 BUG ID 或底层诊断证据（TCAM/寄存器/MMU）』，且能从 CLI/SSA/SDK 三层比对确认表项或状态不一致；失败/未定性工单多为仅描述症状（环路、不通、DHCP 失败）而缺底层抓包、诊断命令输出与版本 BUG 对照，导致无法区分是配置、表项还是芯片层问题。关键差异在于是否采集了『上下层一致性 + 表项/寄存器原始态』。

### 4.7 易混子场景判定表

> 用于把本场景内相近的故障模式、以及与相邻大场景的边界区分开。按「现象 → 关键观测点 → 命中即归 → 否则下钻」的顺序判读。

| 现象 | 关键观测点 | 命中即归 | 否则下钻 | 判读依据 |
|---|---|---|---|---|
| 非 vlan1 网段不通，万兆光口接千兆模块降速工作 | show interface GigabitEthernet 0/1 看光口速率是否为千兆降速；show vlan 看不通网段 | `DS-L2-02` | 若速率正常且无 tag 识别错误则查 DS-L2-01（协议VLAN/superVLAN）或 EXT-FWD 大场景（纯转发不通） | 5300-L 等机型万兆口降速千兆导致 outer/inner vlan tag 误识别，属标签解析机理，归 DS-L2-02；无降速则排除 |
| MAC 漂移 / 已关闭接口残留 MAC / 表项沾满 | show mac-address-table count 看占用；show mac-address-table dynamic <vlan> 看 MAC 与接口是否一致；show logging ／ include MAC | `DS-L2-03` | 若无 MAC 残留证据、仅表项未命中的纯转发丢包，下钻 EXT-FWD-01；若由接入端口上线/认证触发，下钻 EXT-ACC-03 | 失效点落在 MAC 学习/老化/漂移机制则归本场景，与『跨场景同机理说明』口径一致 |
| 聚合口速率显示异常 / 单端口 susp / LACP 震荡 | show aggregatePort summary 看速率与成员；show memory / show process 看 ssc；show interface GigabitEthernet 0/1 看是否千兆降速 | `DS-L2-06` | 若 susp 伴 MMU holdrop 且为千兆降速模块，归 DS-L2-10；若震荡来自中断掩码致收发包中断，归 DS-L2-08；若主备不切换属 VSU 切换逻辑，下钻 DS-STACK 大场景 | 聚合口 LACP/显示/协商机理归 DS-L2-06；同源千兆降速 MMU 与寄存器异常分别归 DS-L2-10/DS-L2-08 |
| 环路 / STP 端口 block 失效 / RLDP 误报环路 | show spanning-tree 看端口角色/状态；show rldp 看防护动作；show logging 看 BPDU/环路日志 | `DS-L2-04` | 若仅描述环路症状、无 STP/RLDP 状态证据则留未归类待补诊断；若由 VSU 分裂触发则下钻 DS-STACK 大场景 | 机理明确为 STP/RLDP/ERPS 状态或保护失效归 DS-L2-04；缺机理证据不下钻他场景 |

### 4.8 对 APM 产品的能力缺口

| 缺口 | 观测对象 | 数据源 | 采集方式 | 阈值 / 触发条件 | 优先级 |
|---|---|---|---|---|---|
| 缺少「二层表项上下层（CLI/SSA/SDK）一致性」的持续可观测能力 | 二层表项上下层（CLI/SSA/SDK）一致性 | 设备命令（show mac-address-table / show arp / diagnose 查 TCAM my_station_tcam、fpem、vlan class）及 telemetry | 周期执行 show 命令并与 CLI running-config 比对，或通过 telemetry 订阅表项变更事件做增量 diff | 发现表项缺失/残留/上下层不一致（如 VLAN CLASS 残留、my_station_tcam 未下发）即告警 | P0 |
| 缺少「5300-L 降速千兆 vlan tag 识别错误模式」的持续可观测能力 | 5300-L 降速千兆 vlan tag 识别错误模式 | 设备命令（show interface GigabitEthernet 0/1 看速率 / show vlan）/telemetry | 对 5300-L 机型监控接口实际速率与业务 VLAN 连通性，关联已知 BUG 列表（B0702P2 前版本） | 万兆口运行于千兆速率且非 vlan1 网段不通，命中已知 BUG 即告警 | P0 |
| 缺少「接口 LINK/芯片寄存器/MMU 底层态」的持续可观测能力 | 接口 LINK/芯片寄存器/MMU 底层态 | 设备命令（show interface GigabitEthernet 0/1 / diagnose-cmd 查中断掩码 / show mmu（待实机核对）） | 定时采集接口 LINK 并与底层 diagnose 态比对；采集 MMU 拥塞/holdrop 计数 | CLI 显示 LINK UP 但底层 DOWN，或 holdrop 计数持续增长即告警 | P1 |
| 缺少「内存/进程/range 资源趋势」的持续可观测能力 | 内存/进程/range 资源趋势 | 设备命令（show memory / show process / show l2-table resource（待实机核对）或 show mac-address-table count） | 定时采集并保存历史趋势，关联内存泄漏预警（如 WN20250513373） | 内存利用率超 70% 且持续上升，或 range 资源占用超 64 即告警 | P1 |
| 缺少「配置变更与丢失回溯」的持续可观测能力 | 配置变更与丢失回溯 | 设备命令（show running-config / show startup-config）/ 配置管理外部系统接口 | 在重启/升级/EMB 操作前后采集 running-config 快照并 diff；订阅配置变更日志 | 重启前后 running-config 存在差异或 EMB 模板缺 native vlan 即告警 | P1 |
| 缺少「控制面报文上送细分」的持续可观测能力 | 控制面报文上送细分 | 设备命令（show cpu-protect / debug 上送报文计数）/日志 | 采集 cpu-protect 上送失败计数并按报文类型（ARP/RS/ICMP/DHCP）细分 | 某类控制报文上送失败计数突增即告警 | P1 |

---

## 五、跨场景同机理说明（1 组）

> 同一技术机理在多个大场景各出现一次。这里主动登记并给出建议主归属，避免统计口径打架、RCA 路径分歧。

| 机理 | 本场景记录 | 其他场景同名机理 | 建议主归属 | 说明 |
|---|---|---|---|---|
| MAC/ARP 表项学习、老化与漂移（含软件表项残留、share-vlan 复制、MLAG peer-link 同步未裁剪 VLAN 导致的 MAC 漂移） | 119、328、614、615 | EXT-FWD-01／EXT-ACC-03 | DS-L2-03（二层 MAC 表项学习/老化/漂移机理，属本大场景核心机理）；若表现为纯转发不通/丢包且无可佐证 MAC 残留，归 EXT-FWD-01；若由接入端口上线/认证触发 MAC 学习异常，归 EXT-ACC-03 | 同一 MAC/ARP 表项机理在三个大场景各出现一次：DS-L2-03 关注 MAC 学习/老化/漂移本身（残留、复制、同步），EXT-FWD-01 关注表项未命中导致的转发丢包，EXT-ACC-03 关注接入侧（端口/认证）引发的 MAC 学习异常。统计口径以『失效点是否落在 MAC 表项学习/老化机制』为准，本场景为主归属，避免三处重复计数。 |

---

## 六、未归类记录（11 条）

> 这里区分两种性质完全不同的情况：**① 机理缺失**——工单的「根因」「方案」都没有可判定的技术机理，属工单质量问题；**② 机理属他场景待外归**——记录本身有机理，但原表「领域」列把它划到了本大场景，实际应归别处。这两类都不是"没价值"，而是需要补数据 / 修归类口径的清单。

### 6.1 机理缺失（11 条）

| Sheet8行 | case编号 | 年份 | 主题 | 缺失情况 |
|---:|---|---|---|---|
| 6 | CS20231221-2904638 | 2023 | RG-S7810C-X GAB 个别接口插光模块无发光 | 主题（光模块无发光）与根因（零配置防环组件不支持 VSU 状态信息丢失）机理不一致，且原『转发缓存与ASIC表项不一致』旧归类线索被推翻，缺可信失效机理，无法归入环路或接口场景。 |
| 358 | CS20240918-4145021 | 2024 | S8605E，DHCPv6 confirm流程异常。终端在接入上access vlan 1043接口获取V6地址后，再拔线换到access vlan 1044， | DHCPv6 confirm 流程异常，根因与方案均为空，无失效机理。 |
| 406 | CS20240731-3903321 | 2024 | 2台S7805C ipv6 vrrp +MSTP组网，vrrp抢主后终端出现10个左右业务丢包，不符合客户切换预期 | IPv6 VRRP 抢主后业务丢包，根因与方案均为空，无失效机理。 |
| 596 | CS20250828-5606694 | 2025 | 【项目实施】532Y场地核心环路引发全网中断 | 核心环路引发全网中断，根因与方案为空，仅症状描述，缺机理。 |
| 700 | CS20250407-5011615 | 2025 | 武汉纺织大学 N18014 QINQ场景内层vlan封装错误 | QINQ 内层 vlan 封装错误，根因与方案为空，缺机理（其余 QINQ 资源问题已归 DS-L2-10）。 |
| 794 | CS20260603-6644197 | 2026 | 【基础质保】青海联通分公司彩光S2920U设备当前B3版本无法防止环路，需要升级到B8版本。 | 设备无法防止环路需升级，仅提版本升级，无失效机理。 |
| 845 | CS20260321-6371679 | 2026 | 北京移动网管通用基础S7810C-X 生成树超时和VSU异常主备切换 | 生成树超时和 VSU 异常主备切换，根因与方案为空，缺机理。 |
| 846 | CS20260318-6360386 | 2026 | RG-S5760C-24SFP/8GT8XS-X设备设备报rldp环路 | 设备报 RLDP 环路（无配置），根因与方案为空（仅版本升级），缺机理。 |
| 859 | CS20260209-6261680 | 2026 | 东吴证券--MSTP接口被阻塞情况下仍转发数据流量，导致环路 | MSTP 接口 block 仍转发数据导致环路，根因与方案为空，缺机理。 |
| 858 | CS20260212-6275302 | 2026 | N18012 UNC下发业务vlan，18K出现CLI卡，持续30-40min | UNC 下发业务 vlan CLI 卡 30-40min，根因与方案为空，缺机理。 |
| 595 | CS20250902-5625001 | 2025 | 【故障】DHCP无法下发地址 | DHCP 无法下发地址（直连 vlan121 获取失败其他正常），无明确根因，缺机理。 |

### 6.2 机理属他场景待外归（0 条）

（无）

---

## 七、需业务核对的问题（6 条）

**Q-L2-01　5300-L 降速千兆 outer/inner vlan tag 识别错误是否已在通用版本 B0702P2 彻底修复，还是仍依赖规避（万兆速率/空配启机）？**

- 缘由：row=530/685/831/878/296 同因反复出现，需确认根治状态以避免 APM 误判为配置问题
- 建议问谁：交换机产品线/版本负责人
- 关联记录：530、685、831、878、296

**Q-L2-02　share vlan 复制 MAC 致表沾满（row=119）在现网是否仍有非客户自建的 share vlan 配置，默认是否开启？**

- 缘由：该配置非客户自建却引发大面积故障，需确认默认行为与防控
- 建议问谁：产品默认配置负责人
- 关联记录：119

**Q-L2-03　VLAN CLASS/ACL classid 冲突导致跨 VLAN 误生效（row=792/863），ACL 调用残留的根因是配置删除时序还是 classid 分配机制？**

- 缘由：确定是否需在 APM 增加 classid 冲突检测
- 建议问谁：L2 转发/ACL 模块研发
- 关联记录：792、863、883

**Q-L2-04　千兆模块插万兆口触发 MMU holdrop（row=141/637）是否仅限特定机型与版本，是否有硬件兼容清单？**

- 缘由：决定 APM 是否对『降速模块』做专项告警
- 建议问谁：硬件兼容/驱动团队
- 关联记录：141、637

**Q-L2-05　未归类 11 条（环路/DHCP/生成树无机理）中，哪些其实可归结为已知表项/STP 根因但需要现场补诊断？**

- 缘由：降低未归类率，明确现场必须采集的诊断命令
- 建议问谁：TAC/二线定位团队
- 关联记录：6、358、406、596、700、794、845、846、859、858、595

**Q-L2-06　EMB/WEB 配置清空接口或卡下发（row=619/762/772）的根因是 EMB 逻辑还是模板缺 native vlan，是否在新版 EMB 修复？**

- 缘由：管理面配置丢失类需明确修复版本以便 APM 关联
- 建议问谁：EMS/EMB 管理面研发
- 关联记录：619、762、772

---

## 八、本场景关键结论

DS-L2 领域 80 条工单显示，二层故障高度集中在『版本 BUG 导致功能不生效/配置未下发』与『软硬件表项（TCAM/VLAN CLASS/SDK）不一致』两类根因，二者合计占比过半。VLAN 相关（协议 VLAN/superVLAN/降速标签解析/配置丢失）是最庞大子类，且 5300-L 系列『万兆口降速千兆导致 outer/inner vlan tag 识别错误』是反复出现的同因故障，应作为 APM 重点监测模式。MAC 表项残留/漂移、STP/RLDP/ERPS 环路保护失效、LACP 聚合异常、芯片寄存器中断与 MMU/内存资源耗尽分别由不同失效点驱动，需用不同命令与可观测点区分定位。大量工单缺机理（11 条未归类）集中在 DHCP/环路/生成树类，说明现场根因定性能力是 RCA 底座的关键缺口。APM 应优先补齐『VLAN/表项上下层一致性』『接口 LINK 与寄存器』『资源（MMU/内存/range）』三类可观测点。


*（本文档经 2 位交换机专家交叉评审 2 轮修订，评审记录见《评审记录》文档。）*