# 1 GitHub 设备开发/排障/工具抱怨清单（第五货架：开发者 issue 货架）

> 采集日期：2026-10-26 ｜ 采集方式：GitHub Search API（`/search/issues`，未登录，10 次/分钟）
> 读取程度：**全部 55 条均为 API 返回的 issue 正文全文**（search 接口 body 字段完整返回）；**评论未读**（读评论需 `core` 配额，本次已耗尽）。
> 链接校验：本机 `github.com` 网页版经代理返回 502（仅 `api.github.com` 通），无法直接开页验证。改用反向核对——文档内 **57 个链接全部命中 GitHub Search API 原始返回的 `html_url` 字段，0 处未匹配**，链接本身由 API 生成，不存在手抄错号。
> 用途定位：作为《方法论03-业界新方向调研》A2 步骤「四货架」之外的**第五个货架**——开发者 issue 货架。它补的正是前四个货架补不上的那一块：**设备本身的行为在别人手里已经踩过哪些坑**。
> 上游文档：`方法论03-业界新方向调研-跨赛道寻找新工具与新技术.md`、`A1-A3-执行结果-问题名册与货架与能力卡.md`

---

## 1.1 体例说明（沿用方法论 03 的 0.0 节）

1. 英文一律保留，并同时给中文：首现写「中文（English）」，之后可单用。
2. 不翻译：命令、代码、路径、URL、型号、版本号、issue 编号。
3. 每条抱怨标三个字段：**原话（verbatim）**、**抱怨类型**、**对你意味着什么**。
4. 「抱怨类型」用方法论 03 的困难分类：D1 状态无法重现（state not reproducible）／D2 数据取不到（data unavailable）／D3 数据不可信（data untrustworthy）／D4 边界无人管（nobody owns the boundary）／D5 只有现场那一刻（only-at-that-moment）／D6 处置动作毁证据（remediation destroys evidence）。

---

## 1.2 结论先行：能不能用，用在哪一层

**能用，而且这是目前找到的最接近你需求的一手材料。但必须接受三个硬前提，否则采到的全是噪声。**

### 1.2.1 前提一：只能用「仓库白名单 + 定向检索」，裸关键词完全不可用

实测对照（同一天、同一接口、同一排序）：

| 检索方式 | 查询语句 | 命中总数 | 前 5 条相关性 | 判断 |
|---|---|---|---|---|
| 裸关键词（英文） | `"campus switch" in:title,body is:issue` | 567 | 0 / 5 | 命中 SuiteCRM 数据库字段、Arista radius 特性请求、elastic 地理字段，**一条设备问题都没有** |
| 裸关键词（中文） | `交换机 in:title,body is:issue` | 190,886 | 0 / 5 | 命中 Minecraft 模组测评、手淘 H5 适配方案、VSCode 插件推荐 |
| 厂商名（中文/英文） | `ruijie OR 锐捷 is:issue` | 11,372 | 0 / 5 | 命中 VSCode 无关帖、腾讯云 SDK 体积投诉、xxl-job 公司接龙，**没有一条是锐捷设备问题** |
| 仓库限定 + 关键词 | `repo:ktbyers/netmiko is:issue dot1x OR "802.1X" OR radius` | 30 | 5 / 5 | 全部是真实设备认证/登录失败 |
| 仓库限定 + 关键词 | `repo:ytti/oxidized is:issue more OR comware OR procurve in:title` | 73 | 5 / 5 | 全部是 ProCurve/Comware 设备取配置失败 |

**判断依据**：GitHub 的 issue 全文检索会把中文技术博客类仓库（`amfe/article`、`varHarrie/varharrie.github.io`）的 issue 评论区一起捞进来——这些仓库的 issue 被当成留言板用，几万条无关内容稀释了信号。**一旦加上 `repo:` 限定，信噪比立刻反转。**

### 1.2.2 前提二：拿不到厂商内部 bug 库，拿到的是「设备驱动层 + 协议栈层」

| 想要的信号 | GitHub 上有没有 | 说明 |
|---|---|---|
| 锐捷/华为/H3C 内部缺陷单 | **没有** | 三家均无公开 issue tracker。`ruijie`/`锐捷` 检索 1.1 万条全为噪声 |
| 厂商产品缺陷（对外可见部分） | 极少 | 只有 Arista（`aristanetworks/avd`）、Cisco（`CiscoTestAutomation/pyats`）等少数有公开仓库，且是「配置生成」与「测试框架」，不是设备固件缺陷 |
| **设备被外部工具访问时的行为差异** | **大量** | netmiko/oxidized/napalm 的 issue 全部是这一类。**这是你采集数据时必然踩的同一批坑** |
| **协议栈在真实拓扑下的行为失配** | **大量** | FRR/SONiC/OpenWrt 的 issue。这是「设备内部进程」层，正好是你说的「可以动设备内部进程」的范围 |
| **第三方采集管道拿不到数据** | **大量** | librenms/telegraf/gnmic/snmp_exporter。这是你的 VictoriaMetrics / SNMP 采集链路的同构问题 |

**结论**：你要的「园区交换机开发同学的抱怨」，GitHub 上真实存在的是**三层人**的抱怨——写设备驱动的人、写协议栈的人、写采集管道的人。这三层恰好包住了你从设备取数到判障的全链路。缺的那一层（厂商产品经理和一线服务的抱怨）在 GitHub 上没有，得靠方法论 01 的内部渠道和方法论 02 的标书渠道去拿。

### 1.2.3 前提三：issue 是「抱怨」，不是「事故」

| 维度 | 事故报告（方法论 03 的 E 货架） | 开发者 issue（本货架） |
|---|---|---|
| 时间 | 有明确故障窗口 | 无，可能拖几年 |
| 影响面 | 有客户损失 | 无，只有一个人卡住 |
| 复现 | 事后复盘 | **多数带可复现步骤**（这是它的最大优势） |
| 根因 | 常常不明 | 常被维护者定位到具体代码行 |
| 对你的价值 | 知道「哪里会坏」 | 知道「为什么取不到、为什么判不了」 |

**所以这个货架不能替代事故货架，它回答的是另一个问题：如果我要做这个能力，会在哪一步卡死。**

---

## 1.3 清单

以下 55 条，按「抱怨什么」分六组。所有链接可直接点开核对。

### 1.3.1 A 组｜设备命令行（CLI）不标准：同一句命令，每个型号一种脾气

这是全部数据里密度最高的一类。**核心事实：不存在「通用的交换机 CLI」。**

| # | 链接 | 设备/型号 | 原话（verbatim 摘录） | 类型 | 对你意味着什么 |
|---|---|---|---|---|---|
| A01 | [netmiko#3125](https://github.com/ktbyers/netmiko/issues/3125) | TP-Link JetStream | `tplink "Pattern not detected: '[>#]' in output." in version 4.0.0 and above` — 3.4.0 正常，4.0.0 起报错 | D2 | 同一型号换工具版本就取不到数 |
| A02 | [netmiko#3344](https://github.com/ktbyers/netmiko/issues/3344) | Extreme ERS 4950 | `pattern > is not found, but it is there`（日志里明明回显了 `4950GTS-415-C>`） | D2 | 提示符就在屏幕上却识别不到，采集层盲区 |
| A03 | [netmiko#1782](https://github.com/ktbyers/netmiko/issues/1782) | Dell PowerConnect 7048 | `Dell PowerConnect failed on connection because of NONE auth not supported` | D2 | 老接入交换机不支持标准认证流程 |
| A04 | [netmiko#2611](https://github.com/ktbyers/netmiko/issues/2611) | Dell OS6 | `DEll os6 not supported in AutoDetect`（返回 None） | D2 | 自动识别厂商失败，静默返回空 |
| A05 | [netmiko#1605](https://github.com/ktbyers/netmiko/issues/1605) | 中兴 ZTE | `pattern not found in output: terminal\ length\ 0`，用户用抓包发现设备回了 `Don't Echo` | D2 | 设备行为与标准不一致，需抓包才能看清 |
| A06 | [netmiko#3770](https://github.com/ktbyers/netmiko/issues/3770) | Aruba OS | `Unsupported SCP device_type`，支持列表里无 aruba | D2 | 传文件（取 coredump/日志）这条路对某些厂商直接不通 |
| A07 | [netmiko#3644](https://github.com/ktbyers/netmiko/issues/3644) | Cisco IOS-XE | `cisco_xe returning "Pattern not detected: 'terminal width 511' in output` | D2 | 终端宽度自适应导致回显被截断 |
| A08 | [netmiko#854](https://github.com/ktbyers/netmiko/issues/854) | HP ProCurve（新版本） | `We now have a new switch on our network with a newer version and the tool times out`（人工 SSH 登录看起来一模一样） | D5 | **人工看正常、程序拿不到——最难查的一类** |
| A09 | [netmiko#3256](https://github.com/ktbyers/netmiko/issues/3256) | HP ProCurve | `enable authentication failes. It works when i use local Login`（RADIUS 登录后进不了 enable） | D4 | 认证通过 ≠ 拿到权限，权限边界无人记录 |
| A10 | [netmiko#3238](https://github.com/ktbyers/netmiko/issues/3238) | HP ProCurve | SSH 用 RADIUS 账号、enable 用本地 `manager` 账号，两者不同即失败 | D4 | 双账号体系，工具默认假设不成立 |
| A11 | [netmiko#3498](https://github.com/ktbyers/netmiko/issues/3498) | MikroTik | `Netmiko dont detect mikrotik prompt but in session log it persist` | D2 | 回显里有、程序看不到 |
| A12 | [netmiko#3405](https://github.com/ktbyers/netmiko/issues/3405) | MikroTik >6.48 | `Mikrotik version > 6.48 = 'export' command incomplete`（23 条讨论） | D3 | **取回来的配置是残的，但不报错** |
| A13 | [netmiko#3006](https://github.com/ktbyers/netmiko/issues/3006) | Palo Alto | 配置导出再导入，`Everything was working fine` 后系统升级即坏 | D1 | 版本漂移导致可复现性丢失 |
| A14 | [netmiko#364](https://github.com/ktbyers/netmiko/issues/364) | Cisco 2960X/S、3560V2 | `ValueError "Failed to exit configuration mode"`，在 2960X/3560V2 上复现 | D6 | 配置到一半退不出来，设备停在中间态 |
| A15 | [oxidized#1705](https://github.com/ytti/oxidized/issues/1705) | HP ProCurve | `Some of my HP ProCurve switches are failing to backup`，日志只见登录横幅 `HP J...` 后接 `ESC[1;15rESC[1;1H` | D2 | 终端控制字符把提示符淹掉 |
| A16 | [oxidized#2871](https://github.com/ytti/oxidized/issues/2871) | ProCurve 5412zl 机箱、2610 | 新提示符正则加入大量 VT100 控制字符匹配，`break config fetching for certain older procurve models`；作者称 `nonprinting characters coupled with such a complicated regex gave me a headache` | D2 | **同一厂商不同代产品，一套规则不能通吃**（其列出的在役型号：2930F/2510/2530/2540/3810M/2920/2810/2610/2620/5412R） |
| A17 | [oxidized#236](https://github.com/ytti/oxidized/issues/236) | HP V1910-24G（Comware SMB） | `it seems that it's not using the '_cmdline-mode on' command`，取回的配置是 `% Unrecognized command` | D3 | 取到的配置看着像配置，其实是报错文本 |
| A18 | [oxidized#794](https://github.com/ytti/oxidized/issues/794) | Dell X 系列 | 卡在 `--More--` 分页提示上直到超时 | D2 | 老设备分页机制使长输出取不全 |
| A19 | [oxidized#3733](https://github.com/ytti/oxidized/issues/3733) | HP Comware 7 | `even though nothing has been changed on the switch, there is always new diff file`，差异只是 `#` 和空格的位置 | D3 | **无变更却报变更——配置漂移检测不可信** |
| A20 | [oxidized#3406](https://github.com/ytti/oxidized/issues/3406) | Cisco IOS-XE（0.31.0） | 升级工具版本后全部 IOS-XE 设备 `execution timeout` | D1 | 工具升级引发全体失联 |

**A 组读出来的东西**：
- 抱怨的落点**没有一条是「设备功能坏了」**，全是「设备的行为拿不到 / 拿到了但不可信」。
- 覆盖型号高度集中在**园区接入层**：ProCurve、Comware、Dell PowerConnect/OS6、Extreme ERS、TP-Link JetStream、MikroTik、ZTE、Aruba。这些正是锐捷园区交换机的同级竞品。
- A15/A16 是最值钱的一对：**同一个 ProCurve 品牌，机箱式（5412zl）和盒式（2610/2930F）要用两套提示符规则**。这直接说明「按厂商分类」不够，得按「厂商 × 代际 × 形态」分类。

---

### 1.3.2 B 组｜数据取不到 / 计数器不可信：最要命的一类

| # | 链接 | 设备/型号 | 原话（verbatim 摘录） | 类型 | 对你意味着什么 |
|---|---|---|---|---|---|
| B01 | [napalm#1006](https://github.com/napalm-automation/napalm/issues/1006) | Cisco IOS 系列 | `Drivers do not have last_flap attribute calculated for get_interfaces()`；建议改用 `last_input / last_output / last_output_hang` | **D5** | **端口闪断（flap）次数在公开数据模型里根本没有字段。** 你想做的「端口级时间线」撞的正是这堵墙 |
| B02 | [sonic#729](https://github.com/sonic-net/SONiC/issues/729) | SONiC 白盒交换机 | `When config one router interface, its rif counters is working. And then, I remove this router interface and configure it again, its counter can not works`（Counter DB 与 Flex Counter DB 的 objectid 不一致） | **D3** | **接口删了重建，计数器就永久失效**。静默失效，不报错 |
| B03 | [librenms#7756](https://github.com/librenms/librenms/issues/7756) | Cisco SG300 系列 | `reads only 32-bit counters on (some) Cisco SG300 series small business switches, since they have bad_ifXEntry set` | D3 | 32 位计数器几分钟就回绕，速率算出来是错的 |
| B04 | [librenms#2376](https://github.com/librenms/librenms/issues/2376) | Cisco SMB | `we use the HC counters for multicast+broadcast if numeric values are returned, but in my case they are never updated` | D3 | 高容量计数器存在但恒为 0，看起来正常 |
| B05 | [librenms#3084](https://github.com/librenms/librenms/issues/3084) | Cisco 4500X | `the ipv6 traffic on VLAN ifs, can not be measured with the classic counters that are used for ipv4 traffic` | D3 | VLAN 接口计数器只含 IPv4，IPv6 流量看不到 |

**B 组读出来的东西**：
这五条全部指向同一个结构性问题：**你从设备取到的「端口/接口指标」，在三种情况下会静默变错——闪断语义缺失（B01）、对象重建后失效（B02）、计数器位宽或类型不匹配（B03/B04/B05）。而且三种都不报错。**

对照你现有的采集链路（SNMP → VictoriaMetrics）：这意味着**指标能写进去、能画出来，但数值在某一刻起就是错的，而监控面板上看不出任何异常**。这比采不到数据危险得多。

---

### 1.3.3 C 组｜无线 AP / AC：故障寿命以天计，日志只有一行

| # | 链接 | 设备/型号 | 原话（verbatim 摘录） | 类型 | 对你意味着什么 |
|---|---|---|---|---|---|
| C01 | [librenms#16221](https://github.com/librenms/librenms/issues/16221) | **Cisco Catalyst 9800 系列 AC** | `The Cisco Catalyst 9800 Series Wireless Controllers doesn't get detected as WLC because of PR#13563` | D2 | **AC 检测不到 AP**——无线侧最基础的数据源直接断掉 |
| C02 | [librenms#18152](https://github.com/librenms/librenms/issues/18152) | MikroTik（RouterOS 7.19.4） | 厂商把 `wireless` 包换成 `wifi-qcom` 新包后，`I've got a problem to get any wireless data` | **D3** | **厂商换一个软件包，采集端全部无线指标变空。** 升级是常态，这类断层必然反复发生 |
| C03 | [openwrt#6937](https://github.com/openwrt/openwrt/issues/6937) | Ubiquiti UniFi-AC-LITE（ath10k） | `Periodically (every 4-12 hours) the AP apparently resets its firmware and drops all clients`，日志仅 `SWBA overrun on vdev 0, skipped old beacon` | **D5** | **故障每 4–12 小时一次、瞬间自愈、日志只有一行。** 不埋点就永远抓不到 |
| C04 | [openwrt#9555](https://github.com/openwrt/openwrt/issues/9555) | TP-Link WR802n v4 | `after some time, rarely a few hours, sometimes a day, mainly after a few days Wifi devices aren't reachable anymore`（186 条评论，至今 open） | **D5** | **有 186 个工程师参与、跨 4 年仍未定位。** 这是「状态无法重现」的教科书案例 |
| C05 | [openwrt#9071](https://github.com/openwrt/openwrt/issues/9071) | TP-Link C6 / Netgear R7800 | 开 802.11r 后 `nl80211: kernel reports: key add failed` | D2 | 漫游（roaming）配置直接导致关联失败 |
| C06 | [openwrt#16680](https://github.com/openwrt/openwrt/issues/16680) | Banana Pi R3 Mini | `daemon.err hostapd: nl80211: kernel reports: integer out of range` | D3 | 报错文本本身不含任何可定位信息 |
| C07 | [openwrt#21337](https://github.com/openwrt/openwrt/issues/21337) | TP-Link Archer C7 v2 | 升级后 802.1X 客户端无法加入，全部线索只有 `daemon.info hostapd: phy0-ap0: RADIUS No authentication server configured`（配置与上一版完全相同） | **D5** | **同一份配置，上个版本能用、这个版本不行，日志给的是误导性原因** |
| C08 | [openwrt#9233](https://github.com/openwrt/openwrt/issues/9233) | 通用（802.1X 动态 VLAN） | RADIUS 下发动态 VLAN 后，`mdns messages are correctly sniffed on the wlan vlan, but they seem to never reach the devices` | D4 | **认证、VLAN 下发、二层转发三个模块的交界处**，谁都认为自己没问题 |
| C09 | [librenms#19232](https://github.com/librenms/librenms/issues/19232) | 全部无线设备 | `after the latest update the Wireless page is no longer working and does not load no matter what device I click on` | D3 | 无线数据聚合视图整体失效 |

**C 组读出来的东西**：
1. **无线故障的时间尺度是「小时到天」，不是「分钟」。** C03 是 4–12 小时一次，C04 是几天一次。你现有的「分钟级定位」在这些场景里没有采样点——**不是精度不够，是采样窗口根本没覆盖到**。
2. **日志给的原因经常是错的。** C07 说「没有配置认证服务器」，但配置与上一版完全相同；C06 说「整数超范围」，等于什么都没说。
3. **C02 是通用规律不是个例**：厂商升级内部实现（换包、换 MIB、换计数器命名），采集端就静默断层。锐捷自己的版本升级也会重复这个模式。

---

### 1.3.4 D 组｜链路闪断之后：协议自己认为「还活着」

| # | 链接 | 设备/协议 | 原话（verbatim 摘录） | 类型 | 对你意味着什么 |
|---|---|---|---|---|---|
| D01 | [frr#7299](https://github.com/FRRouting/frr/issues/7299) | FRR / 内核路由 | `Kernel routes go missing after interface flaps` | D3 | 闪断一次，路由就丢，且不会自动恢复 |
| D02 | [frr#15505](https://github.com/FRRouting/frr/issues/15505) | FRR + ECMP + RFC5549 | `If an interface flaps (even one not used by frr), the routes previously configured into the kernel are lost; I can only reproduce this using ECMP` | **D1** | **一个与本协议无关的接口闪断，把别处的路由带走了**；且只在 ECMP 下复现 |
| D03 | [frr#16658](https://github.com/FRRouting/frr/issues/16658) | FRR VRRP | `When the lower layer interface on which a macvlan interface is created goes down, VRRP-specific macvlan interfaces remain active ... this leads to discarded traffic` | **D3** | **底层接口已 down，上层虚拟接口仍报 up。** 状态机自己骗自己 |
| D04 | [frr#10298](https://github.com/FRRouting/frr/issues/10298) | FRR BGP EVPN | `remote mac addresses disappear from host's neighbor table when BGP session` 中断 | D3 | 控制面抖一下，数据面 MAC 表被清空 |
| D05 | [frr#12391](https://github.com/FRRouting/frr/issues/12391) | FRR EVPN 冗余 | `whenever a session flaps in BGP and an update of the chosen route happens, the RMAC gets lost in Zebra` | D3 | 冗余设计反而制造了新的丢失点 |
| D06 | [frr#23030](https://github.com/FRRouting/frr/issues/23030) | FRR bgpd | `redistribute` + `allowas-in origin` 组合导致 `self-reinforcing route flap`（路由在 installed 与 withdrawn 之间持续翻转） | **D1** | **配置本身制造了永不停止的振荡**，看起来像硬件问题 |
| D07 | [batfish#783](https://github.com/batfish/batfish/issues/783) | 通用（配置分析） | `Reachability does not take VLANs into account` | D4 | **配置静态分析的根本盲区：VLAN 维度没算进去** |
| D08 | [batfish#7289](https://github.com/batfish/batfish/issues/7289) | Junos | `VLAN parsing issues on Junos`，无法确定接口属于哪个 VLAN | D4 | 跨厂商配置语义解析不一致 |
| D09 | [batfish#5867](https://github.com/batfish/batfish/issues/5867) | Cisco（VTP transparent） | `implicit VLANs should be ignored if the switch contains the 'vtp mode transparent'` | D4 | 隐式 VLAN 的存在与否依赖 VTP 模式，静态分析算不准 |
| D10 | [batfish#6306](https://github.com/batfish/batfish/issues/6306) | Junos + VXLAN | VLAN 被错误标记为 `orphan structure`（用户怀疑与 `vni` 有关） | D4 | 分析工具的判定与实际转发不一致 |

**D 组读出来的东西，与你之前从事故分析里得到的结论完全对上了**：
- 你在事故分析里已经得出「根因多为两段各自正常、合起来不通」。D03 是最干净的形式化证据：**底层接口 down、上层接口 up，两个模块各自都"正常"**。
- D07 更进一步：**连静态配置分析工具都不算 VLAN 维度**。这意味着「两段各自正常合起来不通」这件事，业界连一个能算的工具都还不成熟。
- D01/D02 说明：**端口闪断的代价不是丢几秒包，而是把控制面状态永久带偏**。B01 说闪断次数拿不到，D01–D06 说闪断的后果没人能追——两件事合起来就是：**你最想解决的 MTTR，卡在一个既采不到、又追不上的量上。**

---

### 1.3.5 E 组｜采集与遥测管道：远端一抖，本地静默

| # | 链接 | 组件 | 原话（verbatim 摘录） | 类型 | 对你意味着什么 |
|---|---|---|---|---|---|
| E01 | [telegraf#995](https://github.com/influxdata/telegraf/issues/995) | Telegraf SNMP | `Telegraf SNMP multiple hosts stops after timeout` | **D2** | **一台设备超时，整个多主机采集任务停摆**。故障扩散且不区分对象 |
| E02 | [telegraf#13122](https://github.com/influxdata/telegraf/issues/13122) | Telegraf SNMP | `performing bulk walk for field field-name: request timeout (after 3 retries)` | D2 | 大表遍历超时，字段级静默缺失 |
| E03 | [gnmic#82](https://github.com/openconfig/gnmic/issues/82) | gNMIc | `when devices become unavailable, or an unexpected RPC error occurs, there is no attempt to continually re-attempt the subscriptions` | **D2** | **设备恢复后采集不会自动重连**，数据永久断在那个时间点 |
| E04 | [gnmic#961](https://github.com/openconfig/gnmic/issues/961) | gNMIc | `Unfortunately the logs don't mention which one of the target is showing which issue` | **D2** | **日志里没有 target 名字——排障时连是哪台设备都不知道** |
| E05 | [gnmic#573](https://github.com/openconfig/gnmic/issues/573) | gNMIc 集群 | 升级或迁移节点时 `I will loose every connected target` | D2 | 采集器自身运维动作导致数据中断 |
| E06 | [snmp_exporter#762](https://github.com/prometheus/snmp_exporter/issues/762) | snmp_exporter | SNMP 版本与凭据绑在 `module` 里，`if you want to scrape 2 devices but they have a different SNMP community` 就做不到 | D4 | 不同批次设备凭据不同，配置模型不支持 |
| E07 | [snmp_exporter#625](https://github.com/prometheus/snmp_exporter/issues/625) | snmp_exporter | `Each class of devices should be managed in its own directory`，否则要维护 `a single monster snmp.yml` | D4 | 设备类别越多，配置越不可维护 |

**E 组读出来的东西**：
这七条全部是**同一类失效模式**：采集端把「远端设备不可达」和「本地采集逻辑」混为一谈，于是一台设备的抖动变成整条管道的问题，而且**日志里没有对象标识（E04）**。你做 APM 采集（SNMP → VictoriaMetrics），这套坑是原封不动存在的。

---

### 1.3.6 F 组｜现场无法复现：实验室里造不出客户那一幕

| # | 链接 | 组件 | 原话（verbatim 摘录） | 类型 | 对你意味着什么 |
|---|---|---|---|---|---|
| F01 | [napalm#2023](https://github.com/napalm-automation/napalm/issues/2023) | Catalyst 大堆叠 | 配置预览正常，`discard_config()` 时 `runs in a kind of internal napalm/netmiko-timeout`，异常为 `Pattern not detected: 'HOSTNAME#'`；用户从 Wireshark 看到 `TCP FIN is sent by my` 客户端 | **D6** | **想回滚以保全现场，回滚动作本身把会话断开、现场随之消失** |
| F02 | [containerlab#2741](https://github.com/srl-labs/containerlab/issues/2741) | 容器化仿真 | `SR-SIM packet capture on veth interface works on Ingress only` | **D2** | **仿真环境只能抓到一个方向的包**——在实验室里复现「单向不通」直接不可能 |
| F03 | [containerlab#2865](https://github.com/srl-labs/containerlab/issues/2865) | MikroTik RouterOS CHR | CHR 与 macvlan 组合异常 | D1 | 仿真环境与真机行为仍有差异 |
| F04 | [containerlab#3464](https://github.com/srl-labs/containerlab/issues/3464) | MikroTik CHR 官方镜像 | 官方镜像 `start.sh` 存在三处启动缺口 | D1 | 厂商镜像本身不可直接仿真 |
| F05 | [pyats#216](https://github.com/CiscoTestAutomation/pyats/issues/216) | Cisco pyATS/genie | `Unable to learn BGP - UnboundLocalError: local variable 'session_state' referenced before assignment` | D2 | **连厂商自家的状态采集框架在 BGP 上都崩** |
| F06 | [freeradius#5288](https://github.com/FreeRADIUS/freeradius-server/issues/5288) | FreeRADIUS 3.x | `session-state is saved and restored in the wrong place, leading to missing attributes` | D3 | 认证会话属性丢失，直接表现为「用户莫名认证失败」 |

**F 组读出来的东西**：
F01 和 F02 合起来是一句很重的话：**你现在能想到的两条退路——「回滚到故障前」和「在实验室复现」——都在工具层面被堵死了。** 回滚会断会话（F01），仿真的抓包只有单向（F02）。这解释了为什么园区的疑难故障寿命以天计：**不是没人努力，是验证手段本身不完整。**

---

## 1.4 从 55 条里能读出的六条结构性结论

**结论一：这些抱怨的落点，没有一条是「设备坏了」。**
55 条逐条看过，抱怨对象全部是「设备行为取不到 / 取到了不可信 / 取到了但晚了 / 回滚会毁掉现场」。**这说明在设备侧做可观测，真正的对手不是设备故障，是设备行为的不可观测性。** 你要做的方向没错，但卖点不该是「更好的图」，而是「把这一刻的状态取出来」。

**结论二：厂商 × 代际 × 形态，是三层分类，只按厂商分不够。**
A16 一条就够说明问题：同一个 ProCurve 品牌，机箱式 5412zl 和盒式 2610 需要两套提示符规则；作者列出的在役型号有 2930F/2510/2530/2540/3810M/2920/2810/2610/2620/5412R 共 10 款。**锐捷自己的园区产品线同样是这个复杂度。** 任何「按厂商适配一次」的设计都会在第二次型号扩展时崩掉。

**结论三：静默失效比采不到更危险，而且有三条固定路径。**
B 组给出了完整的三条路径：① 语义缺失（B01 闪断次数无字段）② 对象重建后计数器永久失效（B02）③ 位宽/类型不匹配导致数值错但不报错（B03/B04/B05）。**三条都不产生告警。** 如果你的采集链路没有「指标新鲜度 + 数值合理性」的自检，你会长期在给客户看错的数。

**结论四：无线侧的时间尺度是小时到天，分钟级定位在这里没有采样点。**
C03 每 4–12 小时一次，C04 几天一次且 186 条评论跨 4 年未定位。**这不是精度问题，是覆盖率问题**——故障发生在你两次采集之间，且发生时没有留下任何可回看的东西。

**结论五：闪断（flap）是目前找到的最值得押注的单点。**
理由是一条完整的因果链：B01 说闪断次数拿不到 → D01–D06 说闪断会导致路由丢失、虚拟接口状态失真、MAC 表清空、跨模块牵连 → F01/F02 说回滚和复现都不行。**一个既采不到、又追不上、又复现不了的量，正是「季度硬产出」最好的切口**——因为它的价值不依赖一个漂亮的新功能，而依赖一个别人没有的事实：这一刻端口上到底发生了什么。

**结论六：这一类 issue 有天然的「可执行性」。**
和方法论 03 里的事故货架相比，这个货架的条目**多数带可复现步骤和维护者定位**（例如 A19 直接指出差异只是 `#` 和空格的位置，B02 直接指出 `objectid` 不一致）。这意味着它可以直接转成**测试用例和验收标准**，而不只是「知道有这个问题」。

---

## 1.5 复用配方：这套检索怎么自己跑

### 1.5.1 仓库白名单（按四层，共 20 个）

| 层 | 仓库 | 为什么是它 |
|---|---|---|
| 设备交互层 | `ktbyers/netmiko`、`scrapli/scrapli`、`napalm-automation/napalm`、`ytti/oxidized`、`CiscoTestAutomation/pyats` | 外部工具访问设备时的行为差异，等价于你的采集器会踩的坑 |
| 设备 OS / 协议栈 | `FRRouting/frr`、`sonic-net/SONiC`、`openwrt/openwrt`、`openvswitch/ovs` | 「设备内部进程」层的真实缺陷 |
| 采集与遥测 | `librenms/librenms`、`prometheus/snmp_exporter`、`influxdata/telegraf`、`openconfig/gnmic`、`zabbix/zabbix` | 与你 SNMP→VictoriaMetrics 链路同构 |
| 验证与仿真 | `batfish/batfish`、`srl-labs/containerlab`、`netbox-community/netbox`、`FreeRADIUS/freeradius-server` | 配置分析、仿真、认证边界的盲区 |

### 1.5.2 查询模板（直接替换即可）

```
repo:<owner>/<name> is:issue <关键词> in:title
```

常用关键词（按抱怨类型选）：

| 想找什么 | 关键词 |
|---|---|
| 取不到数据 | `"pattern not detected"`、`timeout`、`"not supported"`、`cannot` |
| 取到了但不对 | `wrong`、`incorrect`、`missing`、`"not updated"`、`counters` |
| 设备行为差异 | 直接写型号：`procurve`、`comware`、`catalyst`、`aruba`、`dell`、`zte`、`extreme`、`tplink` |
| 复现困难 | `"cannot reproduce"`、`intermittent`、`flap`、`"after some time"` |
| 回滚/证据被毁 | `rollback`、`discard`、`"lost"`、`"no longer"` |
| 无线 | `dot1x`、`802.1X`、`roam`、`deauth`、`hostapd`、`"access point"` |

排序用 `sort=reactions`（看共振）或 `sort=comments`（看讨论深度）。**`comments` 数是最可靠的价值代理**——186 条评论的问题（C04）一定是真问题。

### 1.5.3 采样纪律

1. **必须仓库限定**：无 `repo:` 的查询噪声率 >90%（见 1.1 实测）。
2. **配额**：未登录 `search` 10 次/分钟，`core` 60 次/小时。**只用 search 拿 body，不要逐条打 core 读详情**，否则一小时只能读 60 条。
3. **读评论要另算**：评论需 `core` 配额，且是最贵的部分。建议只对 `comments > 20` 的条目补读评论。
4. **每季度重跑一次**，用 `created:>上次日期` 增量过滤，只看新增。
5. **必须标注读取程度**：全文 / 部分 / 仅摘要。不标就是推断，不是证据。

---

## 1.6 这份资料的局限（必须写清，否则会被当成全量结论）

| 局限 | 说明 |
|---|---|
| **没有锐捷的一手信息** | 锐捷无公开 issue tracker，`ruijie` 检索 11,372 条全为噪声。**锐捷自己的问题必须走方法论 01 的内部渠道** |
| **没有一线服务/客户的抱怨** | GitHub 上抱怨的是写工具的工程师，不是买设备的客户。客户侧要靠方法论 02 的标书与渠道 |
| **评论未读** | 本次 55 条只读了 issue 正文。维护者的定位结论、其他人的复现确认都在评论里，属于未采 |
| **样本偏向开源生态** | 用开源工具管锐捷/华为/H3C 设备的人，本身就是少数派。这批 issue 反映的是「愿意写代码的人遇到的问题」，不代表全部现场 |
| **时间跨度大** | 最早 2015 年（A17），部分问题可能已修复。引用时须看 `state` 与关闭时间，不能当现状 |
| **不含厂商固件缺陷** | 设备内部 bug（如内存泄漏、转发芯片异常）在三家国内厂商的公开渠道上不可见 |
| **不是事故，是抱怨** | 无影响面、无损失金额、无时间窗口，不能直接用于优先级排序，只能用于「可行性判断」和「测试用例来源」 |

---

## 1.7 建议的下一步（三件事，按性价比排序）

1. **把 E01/E03/E04 拿去对照现有采集链路**（半天工作量）：一台设备超时是否拖垮整个任务？设备恢复后是否自动重连？日志里有没有设备标识？这三条是现成的自检清单。
2. **把 B 组五条变成指标自检规则**（1–2 天）：指标新鲜度、计数器单调性、位宽回绕、对象重建后归零——四条规则能挡住大部分静默错数。
3. **把结论五（闪断）做成一个可验证的小闭环**（2 周）：选一类设备，验证「闪断次数 + 闪断前后的接口状态快照」能否取到。**如果能取到，这就是一个别人没有的差异化数据源；如果取不到，也立刻知道卡在 B01 那一层**——两种情况都比继续调研更有价值。

---

*本文档为方法论 03 的第五货架（开发者 issue 货架）执行结果。所有链接采集于 2026-10-26，可逐条复核。*
