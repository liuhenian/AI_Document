# Kentik NMS 深度解析：用户痛点 → 功能用法 → 技术原理

> 定位：Kentik NMS（Network Monitoring System）是 Kentik 于 2024 年 2 月发布的"AI 辅助型现代网络监控系统"，嵌入 Kentik 网络智能平台，与 Flow（流量分析）、Synthetics（合成测试）、云遥测同库关联。
> 资料口径：以 Kentik 官方知识库（kb.kentik.com）、官方博客与产品页为主，第三方分析为辅。标注"（推断）"处为基于公开架构信息的合理推理，非官方原话。

---

## 第 0 章 结论速览

传统 NMS 的核心缺陷不是"看不见设备"，而是**回答不了"为什么"和"什么变了"**。Kentik NMS 用三件事回应：

1. **采集范式升级**：从分钟级轮询升级到秒级流式遥测，同时保留 SNMP 以兼容存量设备，二者归一化为同一数据模型。
2. **数据不再分家**：设备指标、流量、路由、合成测试、云侧日志在同一时间窗与维度下可比，消除"换工具换时间轴"的关联成本。
3. **把 AI 放在"证据汇合点"而非"每个工具各配一个聊天框"**：AI Advisor 同时读取告警、指标、配置差异、连通性测试结果与实时 CLI 输出，形成单一调查线程。

---

## 第 1 章 谁在用，各自的痛点是什么

Kentik 官方对用户范围的表述是：不只是网络团队，还包括 **SRE、安全团队、云工程师、应用团队**。这一点决定了它的痛点描述不是单一角色视角。

| 角色 | 主要痛点 | 典型诉求 |
|---|---|---|
| **网络工程师 / NetOps** | 排障要在 NMS、流量分析、配置管理、跳板机 CLI 之间反复横跳；微突发看不到；厂商私有 MIB 无法扩展 | 一个界面定位根因，别再跳工具 |
| **网络管理 / 技术负责人** | 自建监控平台硬件、虚拟化、人力成本高；老平台升级周期以年计 | 降 TCO，别让我养平台 |
| **SRE / 应用与云团队** | 出问题时无法证明"是不是网络的问题"，与应用 APM 团队互相推责 | 能拿出可交接的网络侧证据 |
| **安全团队** | 威胁调查缺流量上下文，只能看到点位告警看不到爆炸半径 | 把设备事件与流量行为串起来 |
| **非网络专家 / 值班人员** | 不懂 CLI 语法，看不懂指标含义，只能转派 | 用自然语言问出答案 |
| **服务提供商 / 大型网络运营者** | 设备规模导致轮询架构撑不住，采集器自身成为瓶颈 | 线性扩展且不影响被管设备 |

官方对传统 NMS 的批评清单（来自 Kentik 官方博客原文归纳），可视为它要解决的痛点集合：

- 轮询慢，实时性不足
- 数据孤岛（siloed data），相关性分析与洞察能力有限
- 缺乏可扩展性（extensibility），加个自定义指标就要改产品
- 人工维护负担重（manual upkeep）
- 不支持新的遥测方式（流式遥测、OpenTelemetry）
- 部分用户"距上一次有意义的版本更新已过去数月甚至数年"

---

## 第 2 章 功能 → 痛点 → 详细用法

每个模块按统一模板展开：**痛点 → 功能 → 怎么用 → 效果**。

---

### 2.1 设备发现与批量纳管

**痛点**
新上架一批交换机，手工登记 IP、型号、SNMP 团体字，几百台要花几天；漏登记的设备就在监控盲区里。纳管完还要逐个决定"采集哪些指标、监控哪些接口"，重复劳动。

**功能**
NMS Setup Wizard（三步：部署 Agent → 配置网段与凭据 → 发现并导入）+ NMS Discoveries 页面（进度可视、结果实时刷新、可批量勾选导入）。

**怎么用（详细步骤）**

1. **部署采集器**：在 NMS Setup 页选择 Docker 或 Linux 安装方式，复制生成的安装命令到目标主机执行。若走代理，按界面提示设置 `https_proxy`。Agent 出现在"Select an Agent"列表后点击 **Use this Agent**。SNMP/ST 能力由向导自动安装。
2. **配置扫描范围与凭据**：在 **IP Range** 字段填入逗号分隔的网段列表；在 **Credentials** 下拉里选择已有 SNMP 凭据，或点击 **New Credential** 新建——需指定 SNMP 版本（v1 / v2c / v3）、凭据名称（不能含空格）、团体字（community）。确认采集 Agent 后点击 **Start Discovery**。
3. **审阅并导入**：Agent 扫描网段，结果**实时**填充到"Discovered Devices"列表。列表可按需自定义显示列，列中包含 `sysObjectID`、厂商、型号、IP、Kentik 分配的 Device ID。默认所有发现设备都勾选，取消不想纳管的，点击 **Add Devices** 开始采集。
4. **逐个套用监控模板**：在同一列表的 **Monitoring Template** 下拉中为设备选择采集模板（内置 `Everything`、`Minimal` 预设，或自定义模板）。这一步决定"采哪些指标、监控哪些接口"。
5. **跟踪进度**：发现过程可能耗时（取决于网段规模），可在导航栏状态指示器或 **Manage Discoveries** 查看，卡片显示已扫描 IP 数、发现设备数、完成百分比与预计剩余时间。

**效果**
纳管从"逐台手工配置"变为"扫网段 + 勾选 + 套模板"。一个新环境从部署采集器到看到第一台设备，官方口径约 5 分钟。

---

### 2.2 设备可用性、健康与容量监控

**痛点**
"设备是否还活着"是基础需求，但传统做法只能看到 up/down 状态灯，看不到"活着的设备里谁快撑不住了"。容量规划靠手工导 Excel 按月比对。

**功能**
NMS Devices 页面 + 设备详情页 + 设备级 KPI（CPU、内存、接口统计、硬件组件如电源/风扇/光模块温度）。

**怎么用**

- 在 NMS Devices 列表按可用性、CPU、内存等排序，直接锁定问题设备；点击设备名进入详情页，查看该项设备全部遥测 KPI 与历史曲线。
- 关注设备可用率：Dashboard 的 **Device Availability** 组件给出设备在最近 **7 / 14 / 30 天**的可用率百分比；对图表区域拖拽框选可查看**任意自定义时间段**内的可用率。
- 容量视角：Dashboard 内置 **Devices with Highest CPU**（Top 50）与 **Devices with Highest Memory**（Top 10）两张榜，长期挂在首页即可发现缓慢劣化的设备。

**效果**
把"事后救火"部分前移为"事前发现趋势"。官方宣称的价值表述是"自动识别低效、未充分利用与过度配置的资源"。

---

### 2.3 接口监控与故障定位

**痛点**
排障最耗时的往往不是"某条链路断了"，而是"某条链路时好时坏"。丢包、CRC 错误、discard 通常只在接口计数器里，而计数器分散在几十台设备上，靠人工逐个 `show interface` 效率极低。

**功能**
NMS Interfaces 页面：全量接口清单 + 自定义列 + 多维筛选 + 接口详情抽屉（含连接关系与流量可视化）。

**怎么用（详细）**

1. 从主导航进入 **Network Monitoring System → Interfaces**。列表每行一个接口，默认列包含 **Admin**（管理态）、**Oper**（运行态）、**Name**、**Description**、**Device**、**Bit Rate**、**Utilization**、**Errors**（近 1 小时进出向错误数）、**Discards**（近 1 小时进出向丢弃数）、**Capacity**。可点 **Customize** 调整显示列与顺序，最多同时显示 12 列。
2. 用 **Group by** 按 Device 或 Type 分组；用左侧 **Filters** 面板按 Type、OperStatus、AdminStatus、Capacity、MTU、Index 过滤。过滤规则要注意：**同类条件之间是 OR，不同类之间是 AND**。
3. **OperStatus 的取值有讲究**，`Lower Layer Down`（灰色）表示该接口自身没配置问题，是它所依赖的下层接口挂了——这一条能直接把"谁是真凶"指出来，避免误判为上层接口故障。
4. 点击任意行打开详情抽屉：除状态与静态属性（MTU、MAC、Capacity、Type、是否逻辑接口）外，还有两个关键区块——
   - **Connections**：列出直连对端设备名称、描述与分类（Connectivity / Network Boundary），可据此判断故障影响面；
   - **Traffic Visualization Panes**：**In / Out Utilization** 与 **In / Out Errors** 四条近 24 小时曲线。
5. 曲线右上角有 **View in Metrics Explorer**，一键把图表对应的查询条件带到 Metrics Explorer，继续做分组、对比、扩大时间窗。
6. 需要离线分析可点 **Actions → Export** 导出 CSV。

**效果**
接口层排障从"逐个设备登 CLI"变成"一张表排序 + 一眼看错误/丢弃列 + 详情页看曲线"。官方把这一页的收益直接写成"加速排障（Speed troubleshooting）"。

---

### 2.4 路由协议监控

**痛点**
"网络通不通" 和 "路由对不对" 是两个问题。BGP 邻居一次性抖动、前缀数异常涨落，用传统 SNMP 很难看出趋势——只看当下的 established/idle 状态会漏掉震荡。

**功能**
BGP / ISIS 邻居健康监控 + 收发前缀数随时间变化曲线。

**怎么用**

- 在 Metrics Explorer 中按 BGP 邻居维度查看状态与前缀数时间序列，观察前缀数是否出现台阶式变化（可能意味着一整段路由被撤销或被误注入）。
- 配合告警：NMS 告警策略的实体类型支持 **BGP Neighborship**，可配置"状态从 established 变为 active/idle"这类**状态变化**告警，而不是只能对静态状态告警。
- 与流量数据交叉验证：BGP 前缀数变化与流量突降落在同一时间窗，基本可确认是一次路由事件而非链路故障。

**效果**
把"路由事件"从"事后翻日志"变为"实时可见 + 可告警"。

---

### 2.5 Trap 与 Syslog 事件采集

**痛点**
设备侧最能说明问题的往往是那一条 syslog 或 trap，但它躺在日志服务器里，与指标、流量各占一个系统，排障时无法对齐时间轴。

**功能**
Universal Agent 的 `ksnmptrap`（SNMP Trap 接收）与 `ksyslog`（Syslog 服务）能力，事件进入同一平台，可在 Data Explorer 中检索并与其它遥测同图展示。

**怎么用**

- 在 Universal Agent 上启用 Trap Receiver / Syslog Server 能力，把设备的事件输出指向该 Agent。
- 按 Trap 名称或 OID 过滤检索；按 Syslog 名称、严重级别、消息内容过滤检索。
- 直接基于事件创建告警，或用 Data Explorer 把事件与设备指标、流量叠加在同一时间轴上做根因分析。

**效果**
"设备说了什么" 与 "设备发生了什么" 落在同一份证据里。这是官方宣称"跨遥测类型更快根因分析"的具体落点。

---

### 2.6 遥测数据探索（Metrics Explorer）

**痛点**
监控工具的通病是"能看的都是它预置好的图"。一旦要回答一个它没预置的问题（比如"某个厂商型号的所有光模块温度按月对比"），就只能提需求等排期。

**功能**
Metrics Explorer：基于完整 OpenConfig 风格数据模型的自助查询，任意维度分组（pivot）、任意筛选、可控聚合。

**怎么用**

- 在 Query 侧边栏选择测量项（measurement）、分组维度（group by）、筛选条件与聚合方式，生成图表或表格。数据模型是 OpenConfig 启发的，因此可下钻到设备、接口、组件、路由邻居等实体及各自指标。
- 任何 Dashboard 组件或接口详情图表都能 **View in Metrics Explorer**，把图形一键转为可编辑查询——这是它"从看图到问问题"的桥梁。
- 需要嵌入自有系统时，用 **Actions → Show API Call**：选择 **For Data** 得到 cURL 命令，或选择 **JSON Input** 得到请求体 JSON，直接对接 Kentik Query API 的 Query Data 方法。返回体形如：

```json
{
  "data": [
    {
      "timeseries": [
        { "timestampMillis": 1719497880000, "in-utilization": 0, "out-utilization": 0 },
        { "timestampMillis": 1719497940000, "in-utilization": 2354, "out-utilization": 2420 }
      ],
      "device_name": "qfx_iad2_kentik_com",
      "name": "irb.130",
      "ifindex": 687
    }
  ]
}
```

**效果**
用户不再受限于产品预置视图。官方口径：查询在秒级返回，全用户平均查询响应小于 1 秒。

---

### 2.7 自然语言取数（Query Assistant）

**痛点**
数据模型完整不等于人人会用。一个不懂"measurement / dimension / aggregation"术语的值班人员、SRE 或管理者，面对侧边栏的下拉框依然无从下手。这是"可观测性无法民主化"的真正瓶颈。

**功能**
Query Assistant：用自然语言描述你要看什么，Kentik 把它转成查询。

**怎么用（详细）**

1. 前提：需先启用 Kentik AI。
2. 进入 **Query Assistant** 页面，在顶部查询框直接输入自然语言，例如：
   - `show me interface utilization using line chart with "PEER" in the description`
   - （页面内还提供设备、接口、路由、硬件组件四类示例卡片，每张卡片含示例图表与一组可直接点击填入的示例查询）
3. 按回车或点右侧 **Send**。
4. 系统跳转到 **Metrics Explorer**：查询框保留了你的原话，主显示区给出结果，同时 **Query 侧边栏**已按 Kentik 的理解填好各字段。此时你可以在侧边栏微调后点 **Run** 精修查询。
5. 注意两点：该功能当前仍是 **Beta**；官方说明它主要为英语开发，同时也能理解部分其他语言。

**效果**
非网络专家也能直接问出答案。Kentik 对这一能力的官方表述是"让每个人都成为明星网络工程师"。

---

### 2.8 仪表盘与站点健康总览

**痛点**
管理者需要的不是曲线，而是"现在有没有事、在哪"。传统做法是等值班人员汇报，或者自己开一堆图找。

**功能**
NMS Dashboard：用户级可自定义的组件化总览页。首次访问的默认组件包括：

| 组件 | 作用 |
|---|---|
| **Health Map by Sites** | 地图上每个站点一个点，**红点=有告警、绿点=无告警**；点击站点名跳转到已按该站点过滤的告警列表 |
| **Device Availability** | 设备可用率，支持 7/14/30 天窗口与拖拽框选自定义时段 |
| **Traffic Overview** | 总流量与分流量画像 |
| **Active Alerts** | 环形图（可按策略名或严重级别拆分）+ 明细表（策略、触发维度、触发指标、持续时长） |
| **Interfaces with Highest Utilization** | 利用率最高的接口排行 |
| **Devices with Highest CPU** | CPU 最高的 Top 50 设备 |
| **Devices with Highest Memory** | 内存占用最高的 Top 10 设备 |

**怎么用**

- 点 **Add Visualizations** 打开抽屉，按 **Alerting / Cloud / Core / Edge / Insights / NMS / Protect / Service Provider / Synthetics** 分类选项卡挑选组件。
- 拖拽组件标题栏移动位置、拖拽角部手柄调整大小，点 **Save Changes** 保存。**所有布局改动是用户级的，不影响组织内其他用户**。
- 每个组件的右上角 Action 菜单支持 **Configure**（改标题、回溯窗口、分组方式）、**View in Metrics Explorer**、**View in Data Explorer**、**Remove**。
- 注意 Health Map by Sites 生效有两个前置条件：策略需把 **Site 指定为 Policy Dimension**，且策略覆盖的每台设备必须已**分配站点**。

**效果**
"整个网络现在健康吗" 从需要汇总多份报告变成一屏回答，且可下钻。

---

### 2.9 告警

**痛点**
传统 up/down 告警只能对"当前状态"告警，无法表达"状态发生了不该发生的变化"。而真实故障常常是多个指标同时越界（例如光模块温度高**且**风扇转速高），单指标阈值会产生大量噪音。

**功能**
NMS 设备中心化告警策略（已完全取代旧的 Up/Down 策略类型）+ Alert Manager。

**怎么用（详细）**

1. 从 **Alert Policies Management** 页新建策略时选择 **NMS** 类型。
2. **General**：设置策略名称、描述、是否启用。
3. **Target & Filter Settings**：选择目标实体类型——支持 **BGP Neighborship、Components、Devices、Interfaces** 四类。选定的 Target Type 决定后续可选的测量项。点 **Edit Devices** 指定策略适用的设备范围。
4. **Alert Conditions**：用"句子式条件"构造触发逻辑。可对**状态变化**告警（如 BGP 从 established 变为 active 或 idle），也可对**多测量组合阈值**告警（如激光器温度高 且 风扇转速高，且接口描述为 X）。阈值条件与状态条件可以叠加。
5. **Activate & Clear Settings**：当前版本每个策略只支持**单一严重级别**（官方表示后续会扩展）；可开启"需确认/需人工清除"，选择通知渠道，并调整激活延迟与清除延迟以抑制抖动。
6. 告警产生后统一在 **Alerting** 页管理：查看明细、抑制（suppress）、静默（silence）、确认（acknowledge）、评论、清除（clear）。

**效果**
告警从"状态灯"升级为"意图表达"。用户能写出"我关心的是这个变化，且需同时满足几个条件"，显著降低误报噪音。

---

### 2.10 采集能力可扩展（Collection Profile / Starlark）

**痛点**
客户网络里总有产品没覆盖的设备或指标。传统 NMS 的处理方式是"提需求 → 排期 → 等下个版本"，用户被迫接受"数据缺失"或"自己再搭一套 Prometheus + Grafana"。

**功能**
Collection Profile：通过配置声明即可新增采集点，无需改产品代码。基础换算用内建 transformer，复杂逻辑用 **Starlark**（类 Python 的受限脚本语言）扩展。

**怎么用（详细）**

在 Agent 所在主机的配置目录（示例路径 `/opt/kentik/components/ranger/local/config`）下维护三组声明文件：

1. **`/sources`** —— 定义要采集的源，例如一个自定义 OID：

```yaml
version: 1
metadata:
  name: local-linux
  kind: sources
sources:
  CPUTemp: !snmp
    value: 1.3.6.1.4.1.2021.13.16.2.1.3.1
    interval: 60s
```

2. **`/reports`** —— 把源归入数据模型中的某一类（决定它在门户里出现在哪个测量树下），并挂 Starlark 脚本做改写：

```yaml
version: 1
metadata:
  name: local-temp
  kind: reports
reports:
  /device/linux/temp:
    script: !starlark |
      def process(n, indexes):
          n['CPUTemp'].value = n['CPUTemp'].value // 1000
    fields:
      CPUTemp: !snmp
        value: 1.3.6.1.4.1.2021.13.16.2.1.3.1
        metric: true
    interval: 60s
```

这里的脚本解决了一个非常实际的坑：某些 OID 返回的是微摄氏度（33000），直接上屏会显示成"比太阳表面还热 6 倍"，除以 1000 才是真实摄氏度。

3. **`/profiles`** —— 按设备类型（以 `sysObjectID` 匹配）关联上述 report：

```yaml
version: 1
metadata:
  name: local-net-snmp
  kind: profile
profile:
  match:
    sysobjectid:
      - 1.3.6.1.4.1.8072.*
  reports:
    - local-temp
  include:
    - device_name_ip
```

4. 文件属主需为 Kentik 用户与组（`chown -R kentik:kentik`）。采集到的数据可直接用于仪表盘与告警。

此外还有 **Custom Device Profiles**：如果某型号设备的专属数据点在模型里缺失，可自行补充。

**效果**
扩展从"排期等版本"变为"写几十行 YAML 加一段脚本"。这是官方把"可扩展性"列为独立卖点的落地方式。

---

### 2.11 AI 诊断三件套（本轮体验提升最大的部分）

**痛点**
官方对这块的痛点描述最直白：**"问题容易发现，证明根因才难，而 MTTR 大部分消耗在这里。"** 工程师必须同时看指标、看配置、还要登 CLI——而这些动作分散在不同系统里，且需要准备跳板机、双因素认证、复制粘贴命令输出。

**功能**（2026 年新增，三者共同构成"AI 诊断"）

#### （1）按需连通性测试

- **痛点**：怀疑路径问题但手上没有现成的探针。
- **用法**：由 AI Advisor 自动从合适的观测点发起 ping / traceroute，把可达性、时延、丢包与路径行为的结果直接纳入当前调查线程，与遥测同图分析。

#### （2）Config Context：配置备份与差异

- **痛点**：**配置错误是中断与故障的主要原因之一**，但"什么时候改的、改了什么、谁改的"经常无从追溯，MTTI/MTTR 被拉长。
- **用法（详细）**：进入 **Device Settings → SSH** 标签页配置：
  1. **Enable SSH command access** 打开（总开关）；
  2. **Credential** 选择 Credentials Vault 中预置的 SSH 密钥或密码；
  3. **Collection Agent** 选择对该设备网络可达的 Agent（如 `nomad-0`）；
  4. **Device Platform** 推荐保持 **Autodetect**；
  5. **SSH Hostname (or IP)** 填写 Agent 连接用的 FQDN 或 IP；
  6. **Enable device configuration sync and backup** 打开，之后 Kentik 会周期性抓取 running-config；
  7. **Fetch Interval** 设置抓取频率，官方建议高可见性环境用 **5 分钟**。
- **安全设计**：密钥在 **Agent 侧脱敏**，不会离开设备。连接失败时优先检查 Agent 是否已接受设备 SSH host key，以及防火墙是否放行 TCP/22 初始握手。
- **怎么问**：可以直接让 AI Advisor 回答这类问题——
  - "When was the last successful backup for [Device Name], and were there any errors?"
  - "Summarize the impact of the configuration changes made to [Device Name] during last night's maintenance window."
  - "Locate the last known working configuration snippet for VLAN 100 on any device in the branch office."
- **返回形态**：给出配置版本表（版本号、时间戳、字节数、状态），并附自然语言解读。官方示例中，AI 还从"配置大小每 5 分钟在 42780 与 42408 字节之间来回变化"推断出**存在周期性下发后回退的模式**——这类模式靠人工翻 diff 很难发现。

#### （3）SSH Command Access：只读 show 命令

- **痛点**：登录设备跑 CLI"繁琐、易错，且受知识缺口阻碍"（官方原话）；不同厂商语法不同，值班人员不一定记得住。
- **用法（详细）**：同样在 **Device Settings → SSH** 标签页，在已完成前 5 项配置的基础上，打开 **Enable Read-Only Diagnostic Commands** 开关，AI Advisor 即可在权限范围内选择、执行并解读 `show` 命令。
  - 命令示例场景："Check the BGP summary on [Device Name] and tell me if any peers are currently down."、"Show me the interface counters for eth0 on [Device Name] and highlight any recent input errors."、"Run a routing table check for [IP Address] on [Device Name] and explain the next hop."
  - **权限模型**：严格只读、命令受控、执行前需用户确认；**命令结果不在用户之间共享**。已支持平台包括 Cisco、Juniper、Arista 以及 Nokia SR-OS Classic。

**组合效果（官方演示场景）**
一台 Cisco Catalyst 8000V 上 QoS 策略的 CIR 少写了一个零，10 Mbps 电路被静默压到 1 Mbps，约 90% 流量被丢弃。AI Advisor 先发现流量失衡，再定位到 policy map 与 CIR，给出三个候选修复并解释为什么只有一个正确，最后**在同一调查线程内**执行一条获批的 show 命令验证修复——不切跳板机、不重做双因素认证、不复制粘贴 CLI 输出回工单。

**这三件事的共同设计意图**：让告警、指标、配置、连通性证据、实时设备输出成为**同一份证据体**，使"到底哪里坏了"的答案与原告警出现在同一个工作流里。

---

### 2.12 跨域关联：NMS 数据与流量/合成/云数据同库

**痛点**
最经典的推责场景：应用方说"网络有问题"，网络方说"网络没问题"。双方各自的数据在两个系统里，时间轴对不齐、维度不一致，争论没有终局。官方把这个痛点表述为"无法证明网络是原因、是参与方，还是无辜旁观者"。

**功能**
NMS 的设备指标与 Flow（含 VPC Flow、eBPF）、Synthetics、Cloud 数据在同一平台、同一时间窗、同一维度体系下可比。

**怎么用**

- 在 Data Explorer / Metrics Explorer 中，把设备接口指标曲线与同一接口/同一时间窗的流量曲线叠加——判断"丢包是发生在链路拥塞期还是与流量无关"。
- 用合成测试验证路径，把路径证据与设备侧指标对照。
- 需要把数据交给外部系统时，用 **Kentik Firehose** 把富化后的记录推送到数据湖或分析工具；也可通过告警与工单系统集成自动开工单。
- 分析结论的跨角色交接：官方明确这一能力的价值是"把干净的证据交给应用方与 APM 团队"。

**效果**
排障从"互相举证"变为"共享同一份证据"。

---

### 2.13 运维负担与成本

**痛点**
自建监控要买物理/虚拟基础设施、要养工程团队维护、平台升级周期以年计。

**功能与用法**

- **SaaS 化交付**：无自建基础设施，门户更新对用户透明。
- **单一 Agent 二进制**：Universal Agent（容器镜像约 50 MB，并有 Helm Chart）以"能力插件"方式扩展，从本质上消除了历史上"NMS 采集器"与"流量采集器"分别轮询同一设备造成的**双重轮询**问题（官方称这一合并"显著降低网络设备 CPU 负载"）。Agent 自动更新，自带唯一密码学身份。
- **Agent 自身可观测**：Agent 的宿主指标与各 Capability 指标会送入 Metrics 子系统，出现在 Metrics Explorer 的 `/kentik/agent` 测量树下，因此**采集器本身也能被监控和告警**——包括"NMS 能力当前处理的 MPS"与"正在轮询的设备数"。
- **凭据集中管理**：Credentials Vault 统一管理 SNMP 团体字、SSH 凭据、流遥测凭据、BGP MD5 等，凭据轮换不必逐个编辑测试项。
- **计费方式**：**2026 年 2 月起已全面迁移到按设备计费，MPS 不再作为 NMS 计费指标。**

> **一处需要留意的资料不一致**：知识库的 NMS 概览页仍保留按 MPS 分档的容量表（Platform Essentials 100 MPS≈3–10 台设备；Pro / Premier 250 MPS≈8–25 台设备），而 2026 年 2 月的发布说明明确宣布已改为按设备计费、不再使用 MPS。选型时应以商务合同与最新发布说明为准。（推断：概览页表格为迁移前的存量内容，尚未刷新。）

---

## 第 3 章 技术原理

### 3.1 采集范式：为什么必须从 pull 转向 push

| 维度 | SNMP 轮询 | 流式遥测（gNMI / ST） |
|---|---|---|
| 采集模型 | 拉（采集器主动轮询） | 推（设备向订阅方发布） |
| 典型粒度 | 30 秒 – 5 分钟 | 秒级，部分指标更快 |
| 时间戳 | 采集端收到时打 | **设备源头打**，消除传输抖动 |
| 数据结构 | MIB/OID，厂商不一致 | YANG 模型，OpenConfig 之处厂商中立 |
| 设备开销 | 随"采集器数 × 接口数 × 指标数 × 频率"增长 | 为低开销设计，一份流服务多个消费方 |
| 事件处理 | Trap（阈值型、MIB 定义） | 事件驱动订阅（值越界、链路状态变化即导出） |
| 传输安全 | v1/v2c 明文；仅 v3 加密 | gRPC over TLS |
| 厂商支持 | 事实上通用 | 主流厂商现代平台支持，存量与接入层普遍不支持 |

**关键推论**：粒度与时间戳精度是"能不能看见微突发"的分水岭。传统 5 分钟轮询会把毫秒到秒级的队列拥塞完全平滑掉，这正是"网络时好时坏但监控一切正常"这类争议的技术根源。

**Kentik 的具体实现约束**（官方明示）：

- 传输：支持 **gRPC**，不支持 TCP / UDP
- 会话方向：支持 **Dial-in**（采集器连设备订阅），**不支持 Dial-out**
- 编码：支持 **JSON** 与 **Protobuf（GPB）**，不支持 XML

**默认采集间隔**（SNMP 路径）：

| 指标类型 | 轮询间隔 |
|---|---|
| 设备状态、CPU、内存、接口 | **1 分钟** |
| 其他所有指标 | **5 分钟** |

**SNMP → ST 的两阶段切换**：

1. 设备**必须先经 NMS Setup Wizard 完成 SNMP 发现**（用于映射其 SNMP 组件）；
2. 在设备侧配置 gNMI Dial-in（Kentik 在 GitHub 提供了 Cisco / Juniper / Arista 的配置示例），然后在门户 **Device Settings → Streaming Telemetry** 中打开 **Dial-In from Universal Agent**。

切换后：Universal Agent **停止**对 CPU、内存、接口统计的 SNMP 轮询，改为 ST 采集——默认指标 30 秒，**CPU 指标 2 秒**（在 NMS Devices 页表现为近乎实时的刷新）。但**非遥测数据仍继续走 SNMP**，例如硬件厂商/型号、BGP 监控。

> 工程含义：这不是"一次性替换"而是"长期双协议并存"。官方明确建议把双协议运行视为以**年**为单位的稳态，而非短暂过渡。

### 3.2 Agent 架构：一个二进制 + 能力插件

核心组件是 **Kentik Universal Agent（`kagent`）**。它的设计哲学被官方描述为"宿主治理模块"：本身只管四件事——与 SaaS 平台通信、下载并启用其他"能力"、管理自身与各能力的更新节奏、上报宿主级与各能力级指标。

各 Capability 与职责：

| Capability | 标识 | 职责 |
|---|---|---|
| SNMP / Streaming Telemetry | `ranger` | 发现并采集 NMS 设备数据（SNMP 或 ST） |
| SNMP Trap Receiver | `ksnmptrap` | 接收设备实时事件 |
| Syslog Server | `ksyslog` | 接收设备日志 |
| Flow Proxy（边缘处理） | `kproxy` | 转发并可在本地富化 NetFlow / sFlow / IPFIX |
| Flow Proxy（纯转发） | `ktraffic` | 仅转发流量数据，解码在 SaaS 集群完成 |
| DNS OTT Tap | `kdns` | 把 DNS 查询转为流记录 |
| Connectivity Test | `ksynth` | 按需 ping / traceroute |

**架构意义**（这是最值得借鉴的一点）：把"采集什么"从"装哪个 Agent 二进制"解耦为"启用哪个 Capability"。历史包袱也因此被清理——过去 SNMP 轮询由 Kproxy 与 NMS 能力**各自独立执行**，同一设备被轮询两次，既浪费设备 CPU 又让配置逻辑混乱；合并为统一 SNMP/ST 能力后，双击轮询被消除。

**部署与运维要点**：Docker 或 Linux 包部署；镜像约 50 MB；提供 Kubernetes Helm Chart（支持 StatefulSet 与 DaemonSet）；**必须挂载持久化存储**，因为 Agent 身份与配置需要跨重启保持——按官方警告，不要把它当无状态临时容器跑。

**采集策略分层**：Monitoring Template 决定"这台设备采哪些指标、监控哪些接口"，接口可**静态或动态**选择（配合 Interface Classification 做动态筛选）；模板还包含 ST 间隔设置。每台设备同一时间只能绑定一个模板，新设备默认套用 `Everything` 预设。

### 3.3 归一化：跨协议可比的前提

设备遥测进入系统时统一映射到 **OpenConfig 启发（OpenConfig-inspired）的 schema**。这是整个产品最被低估的一层：

- 它使得"仪表盘、查询、告警不关心数据是怎么来的"——同一套视图对 SNMP 轮询来的值和 gNMI 流来的值一视同仁；
- 它是**跨域关联**的前提：只有维度与时间语义统一，设备指标才能与 Flow、Synthetics 数据直接叠加；
- 它也是 **AI 取数的前提**：LLM 面对多套异构命名体系无法自主关联，归一化把"AI 能不能用"变成"数据模型够不够好"的问题。

### 3.4 存储与查询：Kentik Data Engine（KDE）

KDE 是 Kentik **自研的专有分布式列式存储**，是整个平台的分析底座（非开源数据库，也非独立公司）。

公开可确认的机制要点：

- 接收流记录与相关遥测，做异构字段映射，并用路由、地理、接口、站点、威胁与业务上下文**富化**记录；
- 维护 **full 与 fast 两套数据序列**，分别服务高保真回溯与交互式快速查询；
- 时间片**复制到多个 worker**，由 master 节点负责拆分与重组分布式查询；
- 官方口径：全用户**平均查询响应小于 1 秒**；遥测从设备到浏览器为秒级。

**必须承认的边界**：KDE 的物理实现未公开，以上为官方口径与第三方分析的综合；且任何查询结果都继承底层遥测的局限——采样、缺失导出器、厂商特定的云语义、过期的接口标签、不完美的 GeoIP、不完整的 BGP 上下文，都会"藏在看起来很精确的查询结果里"。这一点在评估任何遥测平台时都适用。

### 3.5 AI 层的两个阶段

**阶段一：自然语言 → 查询（NL2Query）**

Query Assistant 与 Dashboard/Metrics Explorer 内置的 Metrics Query Assistant 属于此类。技术上是把自然语言映射到"测量项 + 分组维度 + 筛选 + 聚合 + 图表类型"的结构化查询，再交由 KDE 执行。**它的能力上限由数据模型的规整程度决定**，而不是由模型参数量决定。

**阶段二：AI Advisor —— 从"回答问题"到"执行取证"**

这是它与"给监控工具加个对话框"的本质区别。AI Advisor 的设计要点是**证据统一**：

- 输入侧包含告警上下文、指标时序、配置版本与 diff、连通性测试结果、实时 show 命令输出；
- 输出侧不只给结论，还要给候选修复方案及**为什么不选其他方案**的推理；
- 执行侧严格限定在只读、白名单、需用户逐条确认的边界内。

配套的 **Journeys** 概念进一步把这类多步操作固化为可重复的工作流，官方表述是"用自然语言 runbook 把组织知识固化为可重复流程"。

### 3.6 安全模型（容易被忽略，但决定能否上生产）

| 面向 | 机制 |
|---|---|
| 凭据 | Credentials Vault 集中管理 SNMP / SSH / 流遥测 / BGP MD5 凭据 |
| 配置采集 | 抓取前在 **Agent 侧脱敏**，密钥不出设备 |
| 设备命令 | 严格只读、命令受控、逐条人工确认；**结果不在用户间共享** |
| 遥测传输 | ST 走 gRPC over TLS；SNMP 建议用 v3 |
| 网络准入 | Agent 需接受设备 SSH host key，防火墙放行 TCP/22 |
| 审计 | 平台提供 SSO 与 Audit Log（Enterprise 计划特性） |

---

## 第 4 章 功能—痛点对照总表

| # | 功能 | 解决的痛点 | 主要用户 | 关键用法入口 |
|---|---|---|---|---|
| 1 | NMS Setup Wizard / Discovery | 批量纳管靠手工，容易漏设备 | 网络工程师 | NMS Devices → Manage → Discoveries |
| 2 | 设备可用性与 KPI 监控 | 只知死没死，不知快撑不住 | 网络工程师 / 管理者 | NMS Devices、Device Availability |
| 3 | 接口监控与详情 | 丢包/CRC/discard 分散在几十台设备 | 网络工程师 | NMS Interfaces + Details 抽屉 |
| 4 | BGP / ISIS 邻居与前缀监控 | 只能看当前状态，看不出震荡 | 网络工程师 | Metrics Explorer + NMS 策略 |
| 5 | Trap / Syslog 采集 | 事件与指标分处两个系统 | 网络工程师 / 安全 | Agent `ksnmptrap` / `ksyslog` |
| 6 | Metrics Explorer | 只能看产品预置的图 | 网络工程师 / SRE | Metrics Explorer Query 侧边栏 |
| 7 | Query Assistant | 不会写查询、不懂术语 | 非专家 / SRE / 值班 | Query Assistant 页 |
| 8 | NMS Dashboard / Health Map | 管理者无法一眼看全局 | 管理者 | Network Monitoring System 首页 |
| 9 | NMS 告警策略 + Alert Manager | 只能对状态告警、噪音大 | 网络工程师 | Alert Policies → NMS 类型 |
| 10 | Collection Profile / Starlark | 自定义指标要等产品排期 | 网络工程师 | Agent 配置目录 YAML + Starlark |
| 11 | 按需连通性测试 | 手上没有现成探针 | 网络工程师 | AI Advisor 调查线程 |
| 12 | Config Context | 配置错误是主要故障源，改动不可追溯 | 网络工程师 / 安全 | Device Settings → SSH |
| 13 | SSH Command Access | 登 CLI 繁琐易错、受知识缺口阻碍 | 网络工程师 / 值班 | Device Settings → SSH |
| 14 | 跨域关联（Flow / Synthetics / Cloud） | 网络与应用方互相推责 | SRE / 应用团队 | Data Explorer、Dashboard 叠加 |
| 15 | Query API / Firehose / 工单集成 | 数据出不去，自动化接不上 | 平台工程 / SRE | Actions → Show API Call |
| 16 | SaaS + 单 Agent + 按设备计费 | 自建成本高、升级慢、双重轮询 | 管理者 / 网络工程师 | Settings → Universal Agents |

---

## 第 5 章 局限与风险

1. **闭源 SaaS，实现不透明**：KDE 为专有引擎，物理实现未公开。适合"用能力"的组织，不适合需要完全掌控数据平面的组织。
2. **存量设备长期依赖 SNMP**：ST 支持取决于厂商与平台，老硬件、接入层、专用设备基本不会支持。因此官方建议把双协议并存按"年"规划。
3. **ST 会话方向受限**：仅支持 Dial-in，不支持 Dial-out。这对防火墙策略与配置责任划分有实际影响。
4. **资料存在不一致**：知识库概览页仍列 MPS 容量表，而 2026 年 2 月发布说明已宣布改为按设备计费。选型须以商务合同为准。
5. **公司归属变更带来不确定性**：Infoblox 于 2026-07-08 宣布收购 Kentik，**2026-08-06 完成交割**。整合方向是把 DNS/DHCP/IPAM 的"网络里有什么"与 Kentik 的"谁在和谁通信"合并以服务 AgenticOps。产品整合路线图尚未完全公布，长期命名与形态存在不确定性。
6. **AI 能力有前置条件**：Query Assistant 需先启用 Kentik AI；Command Access / Config Context 需 TCP/22 可达、Agent 已信任设备 host key、平台已 Autodetect。网络分段严格的环境需要额外打点。

---

## 第 6 章 对 APM 产品 AI 助手的技术借鉴

结合"开源多 Agent 框架 + 商用大模型 API"的既定路线，有六条可直接迁移。

### 6.1 采集端：先做去重，再谈扩容

Kentik 的专业做法是在**架构层消除重复采集**（Kproxy 与 NMS 能力合并），而不是靠加机器扛住双倍轮询。对应到 VictoriaMetrics / Loki / Pyroscope 多采集端并存的现状，应优先梳理"同一目标是否被多个采集器重复抓取"，再考虑横向扩容。

### 6.2 语义层：统一模型是 AI 取数的硬前提

Kentik 的价值链条是：**归一化 → 跨域关联 → AI 取数**，三者顺序不可颠倒。如果指标、日志、链路数据仍各自一套命名，LLM 无法自主关联——这是"Agent 自主分析"落地的最大隐性成本，也是最容易被低估的工程量。

### 6.3 工具层：Agent 的工具边界必须是"只读 + 白名单 + 人工确认"

Kentik 敢让 AI 直接触碰生产设备的唯一原因是这套约束：只读、命令受控、逐条确认、结果不跨用户共享、敏感信息在采集端脱敏。APM 场景虽不直接改配置，但"查数据库 / 拉日志 / 执行诊断脚本"同样需要等价的权限设计。

### 6.4 交互层：AI 应站在"证据汇合点"，而非每个子系统各配一个对话框

Kentik 的关键设计不是"给 NMS 加个问答框"，而是让告警、指标、配置、连通性、CLI 输出成为**同一份证据体**。APM 的对应做法是：不要让用户分别和"指标助手""日志助手""链路助手"对话，而应让一个调查线程同时持有全部证据。

### 6.5 扩展层：把"加指标"从产品排期降级为配置动作

Collection Profile 的思路是：新指标 = 一段 YAML + 一段脚本，无需改产品。APM 若采用固定插件开发模式，前线需求会持续排队；若内建等价的声明式采集 + 脚本改写能力，则边际成本大幅下降。

### 6.6 商业层：计费单位反映价值感知

从 MPS 转向按设备/按纳管对象计数，说明客户**不愿为"采集速率"付费，只愿为"被纳管对象的可观测性"付费**。这对 APM 的定价设计有直接参考意义。

---

## 附录：信息来源

- Kentik 官方博客：《Kentik NMS Now Available》《Introducing Kentik NMS / Reinventing Network Monitoring with Kentik AI》《How to Maximize the Value of Streaming Telemetry》《Universal Agent: Redesigning our Agents ecosystem》《Unify Your Collection Pipeline with the New SNMP/ST Capability》
- Kentik 产品页：《Kentik Network Monitoring System》《Troubleshoot Any Network》《AI Diagnostics in Kentik NMS》《Network Monitoring Architecture》
- Kentik 知识库（kb.kentik.com）：NMS Overview、NMS Setup、NMS Dashboard、NMS Interfaces、Metrics Explorer、Query Assistant、Universal Agents、Agents Overview、Config Context、Command Access、NMS Supported Devices
- DZone：《Adjusting Data Before Sending It to Kentik NMS》（Starlark 与 Collection Profile 实操示例）
- 第三方：BTW Media（KDE 架构分析）、Network World / Infoblox 新闻稿（收购与整合方向）、Microsoft Marketplace 与 ToolRadar（定价量级）
