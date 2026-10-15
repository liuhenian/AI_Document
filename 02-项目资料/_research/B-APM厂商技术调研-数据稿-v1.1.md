# B - APM/可观测厂商近10年技术调研（数据稿 v1.1）

- 文档编号：APM-SW-RESEARCH-2025 / B
- 编制：数据AI-B（APM/可观测性厂商数据收集与分析专家）
- 调研时间窗：2015-01-01 ~ 2025-12-31（个别 2013-2014 奠基性技术标注"前瞻"；2026 年信息仅作"延伸注记"）
- 执行基线：`00-任务规范与格式标准.md` v1.0 + `01-Leader-任务规划书.md` + `review/B-评审报告-第1轮.md`（15 条问题）+ Leader 本轮硬性裁决 A/B/C/D/E/F
- 版本语义：**v1.0 初稿 → v1.1 = 第1轮评审修订版（本文件）→ v1.2 = 第2轮评审修订版 → v1.3 = 终稿**
- 状态：**第1轮评审修订版（v1.1）**。本轮逐条闭环 `B-R1-01 … B-R1-15`，闭环台账见新增加的 **附录B**。

> **🔴 版本阅读须知（三处必须先行理解的重大变更）**
> 1. **§2.6 Broadcom 已按 Leader 裁决 A「方案A + 硬性截止线」的第 2 分支降级**为「**证据不足的对照性附录**」（见 2.6 章首声明）：本轮经 9 条官方路径实测后**仍未取得任何支撑 DX APM 产品事实的 S/A 级官方来源**，故该章**不计入有效技术条目数与覆盖率分母**，§4/§5 中一切依赖 Broadcom 的论断已逐处改写为「因证据不足不予采信」。
> 2. **§6.1 的全部数字已重算并公开口径与算法**（条目计数规则、9 字段逐字段判定规则、案例五要素定义），并附**可逐条复算的缺失字段清单表**。第 1 轮评审指出的「33/36/37 互斥」问题已消除，全稿只保留**一个**条目数。
> 3. **案例字段（字段 8）已从 0 补到 13 个五要素齐备案例**（客户名+场景+结果+时间+官方来源 URL；见 §6.5 表 A，其中窗口内 10 个、窗口外 3 个），另有 **21 个「有客户名与量化结果但官方页面未标注日期」的次级案例**（§6.5 表 B）如实单列、**不计入 13**。**第 1 轮评审判定 v1.0 的"约 3 个案例"属口径失真，v1.1 已彻底改为两级口径并允许评审逐条复算。**
>
> **检索环境诚实声明（v1.1 更新，供评审AI核验）**：`web_search`（modsearch/firecrawl）触发 429；`browser_*`（Playwright）在本会话未注册可用 provider；`web_search_pro(engines=ddg,bing)` 对厂商域名召回极差——本轮以两个真实查询复现了该缺陷：查询 `Dynatrace press release July 25 2023 hypermodal artificial intelligence Davis` 返回的是 **Apple 中国官网 iPhone 页面**，查询 `IBM Instana AutoTrace official documentation ibm.com docs` 返回的是 **IBM 中文首页与百度百科词条**（与第 1 轮评审 AI 的复现结果一致）。
> 因此 v1.1 全面改用**「官方 sitemap 挖掘 + 单页 HTTP 直取」**策略（Leader 已探明并建议），并对**新闻稿/官方博客/官方案例页**这三类**在页面内自带日期**的来源做定向抓取。凡未成功抓取者一律登记 `官方来源缺失：<原因>`，**无一条链接为推测或编造**。

---

## 0. 摘要（≤600字）

近10年（2015-2025）APM/可观测厂商的技术演进可归纳为**三条主线**：

**主线一：采集侧「无侵入化」——eBPF 成为事实标准。** 2015 年前后 APM 依赖字节码注入/Agent 埋点（AppDynamics、New Relic、Dynatrace 各自私有 Agent）。2017-2021 年，内核态采集成熟：Datadog Universal Service Monitoring（2021-10）用 eBPF 直接解析内核网络栈，无需改动一行代码即可获得 RED 指标；Pixie（CNCF）用 eBPF 采集 full-body request 与 CPU flame graph；Cilium Hubble/Tetragon 用 eBPF 做 L3-L7 流级与服务依赖图；Coroot 用 eBPF 实现"零埋点"服务地图；OpenTelemetry eBPF Profiler 把 whole-system profiler 做成非侵入式。**这条主线与用户在 Linux 交换机内做 eBPF/C++ 采集的路线完全同构。**

**主线二：分析侧「因果化」——从阈值告警到拓扑因果 RCA。** Dynatrace Davis 以 Smartscape 依赖图 + 确定性因果推理（而非纯统计 ML）定位根因；Instana 以 Dynamic Graph 做秒级变化感知；Datadog Watchdog 做自动异常关联；Coroot 内置 80%+ 问题的 inspection 规则。**这是"信噪比"问题的核心解**。

**主线三：交互侧「LLM 化」——2023 年起生成式 AI 全面入场。** Datadog Bits AI（2023-08）、Dynatrace Davis CoPilot、New Relic AI、Elastic AI Assistant、Splunk AI Assistant、Grafana Assistant、SolarWinds AI、IBM Instana GenAI Observability（2025-10）密集发布，形态高度一致：**自然语言查询 → 自动关联多源遥测 → 生成根因假设 → 建议/执行修复**。

**对用户APM场景的启示**：① 采集侧可直接对标 USM/Pixie 的 eBPF 解析路径与 Coroot 的零埋点服务地图，但必须镜像 OTel eBPF Profiler 的**内核版本门槛（5.10+/5.4+）与开销上界（1% CPU / 250MB 内存）**做容量设计；② Server 端 AI 助手应对标 Davis 的**"因果 + 拓扑"而非纯时序异常检测**，否则告警收敛会变成误报搬家；③ 交换机场景的差异化机会在**流级遥测（NetFlow/INT/Streaming Telemetry）与 APM 的语义打通**，这是纯云厂商的弱项。

---

## 1. 厂商总览表

| # | 厂商 | 定位/份额依据 | 核心产品线 | 技术路线一句话 | 近10年关键动作时间 |
|---|---|---|---|---|---|
| 1 | **Datadog** | 云原生可观测头部 SaaS；2026 Gartner MQ Observability Platforms 领导者（Datadog 官网横幅）【2026延伸·窗口外】 | APM、USM、Continuous Profiler、Log Management、RUM/Session Replay、Network Monitoring、Bits AI | 全栈 SaaS 统一平台 + Agent 侧 eBPF 无侵入采集 + Watchdog 自动异常检测 + LLM Copilot | 2021-10-26 USM GA；**2020-08-11 Continuous Profiler GA（官方新闻稿，本轮修正）**；2023-08-03 Bits AI |
| 2 | **Dynatrace** | 企业级全栈可观测领导者；Gartner MQ 长期领导者；SEC 上市（NYSE: DT） | OneAgent、Smartscape、PurePath、Grail、Davis AI / Dynatrace Intelligence | 单 Agent 自动发现 + Smartscape 拓扑 + Davis 确定性因果 AI + Grail 数据湖仓 | 2015-2016 Smartscape/OneAgent 架构成型【待核验：无官方发布页】；2019 Davis 品牌化叙事【待核验】；**2023-07-25 Davis 扩展为"超模态 AI"并命名 Davis CoPilot（官方 IR 新闻稿，本轮修正；v1.0 误置于 2024）**；2022-2023 Grail【待核验】；2024+ 统一为 Dynatrace Intelligence |
| 3 | **New Relic** | 老牌 APM SaaS；2023-2024 起全面转向用量制与 AI 可观测 | New Relic Platform、APM 360、AI Monitoring、NRQL、OpenTelemetry 原生接入 | 统一 Telemetry Data Platform + 无埋点 AI/MCP 观测 + NRQL 查询 + 生成式 AI 助手 | 2020 统一平台重构【待核验：v1.0 依据的 sitemap lastmod 已按 B-R1-08 废止】；**2020-12 Pixie 被 New Relic 收购【据公开报道，官方新闻稿未取证，两处年份已统一】**；2023 New Relic AI【待核验】；2024 AI Monitoring/MCP【待核验】；**2024-10-01 官方案例 CareerVillage（官方新闻稿，S 级）** |
| 4 | **Cisco（AppDynamics + Splunk 整合）** | **2024-03 Cisco 完成收购 Splunk（约 280 亿美元）【待核验：Cisco IR 站点本轮实测被 Cloudflare 拦截，未取得官方新闻稿】**，形成"网络 + 安全 + 可观测"组合 | AppDynamics APM、Cognition Engine、Splunk ITSI、Splunk Observability Cloud、AppDynamics On-Premises | 网络设备数据与 APM 业务上下文交叉 + ITSI 事件智能与告警收敛 + AI Assistant | **2017-03 Cisco 完成收购 AppDynamics【待核验】**；2021 AppDynamics Cognition Engine【待核验，本轮已改用"官方未取证的背景性表述"】；**2024-03 Cisco 完成收购 Splunk【待核验】**；2024-2025 Splunk AI Assistant / ITSI |
| 5 | **Elastic（Elastic Observability）** | 开源搜索/分析栈起家，Observability 为三大解决方案之一；2026 Gartner MQ Observability Platforms 领导者（Elastic 官网）【2026延伸·窗口外】 | Elastic Observability、Elasticsearch/ES\|QL、Logs/Metrics/APM/Tracing、AI Assistant、Streams | 以日志为中心的统一数据平台 + 列式指标引擎 + ES\|QL 查询语言 + Agentic 调查 | 2019-2021 Elastic Observability 成形【待核验】；2022-2023 APM/Profiling；2023-2024 AI Assistant【待核验】；2025 ES\|QL / Streams / Agentic；**2025-08-28 官方案例 Burgan Bank Türkiye（本地部署 AI 助手，90% 事件响应提速，S 级官方博客）** |
| 6 | **Broadcom（CA Technologies / DX APM）** | ⛔ **本轮降级为「证据不足的对照性附录」（Leader 裁决 A 第 2 分支）**：2018-11 Broadcom 完成收购 CA Technologies **【待核验：未取得官方新闻稿】**，DX APM 属其企业软件部门 | DX APM（原 CA APM）、DX OI（Operational Intelligence）、DX Dashboards | 传统私有化 APM 为主，强调本地部署与大型机/金融行业合规，AI 能力以 DX OI 关联分析为主——**以上全部为 C 级推断，不作为事实依据** | **不可作为时间线依据**（见 2.6 章首降级声明与附录B B-R1-03） |
| 7 | **IBM（Instana）** | 2020-11 IBM 宣布收购 Instana【待核验：未取得 IBM 官方公告原件】；IBM 为 2026 Gartner MQ Observability Platforms 领导者（IBM 官网）【2026延伸·窗口外】 | IBM Instana Observability、Dynamic Graph、AutoTrace、GenAI/LLM Observability、IBM Concert | 自动发现 + Dynamic Graph 秒级变化感知 + AutoTrace 无重启追踪 + 2025 起 GenAI 可观测 | 2020-11 IBM 收购 Instana【待核验】；2021-2024 Dynamic Graph/AutoTrace 演进；**2025-10-06 GenAI Observability GA（官方公告，S 级）**；**2026-05-05 AI Agent & LLM Observability（官方公告）【2026延伸·窗口外】**；**官方案例 State of Oregon OIS（Instana，MTTD −50%/MTTR −30%；官方 case study，页面未标注发布日期）** |
| 8 | **Grafana Labs** | 开源 LGTM 栈主导者；2026 Gartner MQ Observability Platforms 领导者且"Completeness of Vision 最靠前"；2026-08-26 官网宣布突破 10,000 客户【2026延伸·窗口外】 | Grafana、Loki、Tempo、Mimir、Pyroscope、Adaptive Metrics/Profiles、Asserts、Sift、Grafana Assistant | 开源可组合栈 + 大数据量降本（Adaptive Telemetry）+ ML/LLM 助手 | 2020 Loki / 2021 Mimir(Cortex) / 2021 Tempo 加入【待核验】；2022 Phlare（官方产品页原文）；**2023-03 收购 Pyroscope【据公开报道，官方产品页无此表述，v1.0 的"明确可考"归因已按 B-R1-09 撤回】**；2023 Adaptive Metrics【待核验】；2024 Asserts/Sift；2025-2026 Grafana Assistant |
| 9 | **SolarWinds** | 传统 IT 运维/网络管理厂商，混合云转向 | SolarWinds Observability（SaaS + Self-Hosted）、Hybrid Cloud Observability、Network Performance Monitor、NetFlow Traffic Analyzer、Database | "监控家族统一化 + AIOps 异常检测"，强调本地/混合部署与网络设备覆盖 | 2021-2022 推出 Hybrid Cloud Observability【待核验】；2022-2023 SolarWinds Observability SaaS【待核验】；**NPM/NTA 官方产品页本轮已取证（NetPath hop-by-hop、NetFlow/sFlow/J-Flow/IPFIX）**；**官方案例 Charter（事件确认时间 −93%，Publish Date 2026-09-09）【2026延伸·窗口外】** |
| 10 | **OpenTelemetry 生态（CNCF）** | CNCF 毕业项目；OTel 为可观测数据模型事实标准；Prometheus 为云原生指标事实标准 | OpenTelemetry（API/SDK/Spec/Collector/SemConv）、Prometheus、W3C Trace Context、eBPF 系（Pixie、Cilium Hubble/Tetragon、Coroot、opentelemetry-ebpf-profiler、groundcover） | 厂商中立标准 + 可组合开源组件；eBPF 系负责"无埋点采集"，OTel 负责"统一数据模型与传输" | 2016 Prometheus 加入 CNCF【待核验】；2019-05 OTel 合并成立【待核验】；2021-11-23 W3C Trace Context 成为正式推荐标准【**w3.org 正文本轮仍被 Cloudflare 拦截，未能页面内取证；已按 B-R1-07 增设 OpenTelemetry Context Propagation 官方文档作为佐证来源**】；2022-2023 OTel Logs/Profiles；2024-2025 eBPF Profiler 与 eBPF 生态爆发 |

> **总览表来源**：各家官网/官方新闻室（见第2章逐条来源与第7章清单）。市占率类表述本稿统一标注为「厂商自述/Gartner MQ 引用」，**未采用第三方份额机构数据**（本环境下无法核验）。
>
> **⚠️ 本表时间列的证据等级标注规则（v1.1 新增，响应 B-R1-10）**：凡**有 S/A 级官方页面内日期**支撑的时间点，直接书写；凡**仅有"据公开报道/行业共识"、未取得 S/A 级官方来源**的时间点，一律加 `【待核验】`；凡**超出 2015-2025 调研窗口**的时间点，一律加 `【2026延伸·窗口外】`。**本表的确定度与 §2.x 条目、§3 时间线三处必须一致**（v1.0 中"总览表确定语气、条目内自认无来源"的层级互斥已在本版消除）。

---

## 2. 厂商逐一分析

### 2.1 Datadog

#### 2.1.0 厂商近10年战略与技术主线（≤500字）

Datadog 的技术主线可概括为「**先做全栈统一，再做无侵入采集，最后叠加 AI 收敛**」。2015-2018 年以 SaaS 化基础设施监控 + APM Agent 埋点切入，靠"一个平台看所有数据（Metrics/Logs/Traces）"打破监控工具孤岛。2019-2021 年是关键技术拐点：Agent 内置 **eBPF 传感器**，在 2021-10 推出 **Universal Service Monitoring（USM）**——不修改任何代码、仅凭 Agent 与 Unified Service Tagging 即获得全部服务的 RED 指标与 Service Map，这直接把"埋点覆盖率"从组织问题降级为技术问题。同期推出 **Continuous Profiler**，把 profile 变成与 trace 关联的第四类信号。2022-2024 年叠加 **Watchdog**（自动异常检测与关联）与 **Bits AI**（2023-08 生成式 AI DevOps Copilot），把"检测"与"对话式排障"补齐。2025 年起把 LLM 自身作为被观测对象（LLM Observability / Agent Observability）。

对用户的意义：Datadog 是**"Agent 侧 eBPF + Server 侧 AI 收敛"最完整的商业参照系**，其 USM 的内核解析思路与 Continuous Profiler 的开销控制模型，可直接映射到交换机内嵌采集 Agent 的设计。

#### 2.1.1 Datadog - Universal Service Monitoring（USM，通用服务监控）

1. **技术类别**：传统技术（eBPF 无侵入采集）+ AI技术（AI增强：输出供 Watchdog/Bits AI 消费的 RED 指标基线）
2. **首次发布/关键版本时间**：2021-10（官方博客发布日期 2021-10-26；页面 Updated 2022-11-29）
3. **推出背景**：2019-2021 年 Kubernetes 与微服务大规模普及，服务数量从几十个膨胀到成百上千，且大量服务是第三方组件、遗留系统或团队不愿改动的库。传统 APM 依赖代码埋点，导致"未被埋点的服务"成为监控盲区；SRE 无法回答"我到底漏了哪些服务"，服务依赖图（Service Map）永远不完整。同时容器化环境的服务生命周期以分钟计，人工登记服务清单不可行。
4. **解决的问题**：
   - 消除未埋点服务造成的可观测性盲区（第三方/遗留/库服务）
   - 在不改动代码、不重启进程的前提下补齐服务级 RED 指标
   - 自动生成与维护完整的服务目录（Catalog）与服务依赖图
   - 让未埋点服务也能配置 Monitor / Dashboard / SLO
   - 缩短 MTTD/MTTR（未埋点服务此前无法告警）
5. **技术原理**：USM 完全依赖已部署的 Datadog Agent 与 Unified Service Tagging，无需代码插桩。Agent 内的 **eBPF 程序挂载到内核网络栈**，对 HTTP(S) 等协议的请求/响应流量做**协议解析**（而非抓包全文），在**内核态**直接统计出 request、error、duration（RED）三类黄金信号，再以 `universal.http.server` / `universal.http.client` 两个 operation 名上报。Agent 同时根据容器标签（`app`、`short_image`、`kube_container_name`、`container_name`、`kube_deployment`、`kube_service`）**自动推导服务名**，若已有 unified service tags 则沿用，从而实现"零登记的自动服务发现"。这些指标被写入 Catalog 与 Service Map：Catalog 负责服务所有权与元数据集中化，Service Map 负责上下游依赖可视化；配合 Deployment Tracking（取 CI/CD 的 version tag）可把服务性能变化与版本发布对齐。指标同样可用于 Monitor、Dashboard 与 metric-based SLO。**推断边界**：官方文档明确"通过 eBPF 从内核网络栈自动解析 HTTP(S) 流量"，但**未公开**具体 eBPF hook 类型（kprobe/tracepoint/TC/XDP）、是否使用 ring buffer、单 Agent 吞吐上限与 CPU 占用曲线；这些属实现细节，本稿不作断言。另有部分协议与流量加密方式处于 **Preview**（Cloud Service Discovery 与 Additional Protocols）。
6. **技术效果**：官方定性描述为"数秒内（Within seconds）获得基础设施中每个服务的 RED 指标"、"服务出现约 5 分钟后可在 Catalog 中看到"（官方文档：configure the Agent, wait about five minutes）。**官方未给出量化开销数据**（CPU%/内存占用绝对值）与覆盖率百分比。
7. **落地情况**：已商用（Datadog 平台内 GA 功能，含 Helm/Operator 部署方式；部分高级协议解析为 Preview）。规模数据官方未公开。
8. **案例**：**仍然缺失（如实登记，不凑数）**。本轮已实测 `https://www.datadoghq.com/customers/`（HTTP 200，可抓取列表页），但该列表页为卡片式渲染、**未暴露"客户名+场景+结果+时间"四要素正文**，且 Datadog 官方新闻室首页子路径清单不含按产品过滤的客户条目；本条目（USM）**未能定位到一个五要素齐备的具名 USM 客户案例**。本稿**不使用无客户名的证言充数**（第 1 轮评审判定 v1.0 的"约 3 个案例"即为口径失真，v1.1 不再重复该错误）。Datadog 的唯一五要素案例（Cvent）归属其 Continuous Profiler 条目（§2.1.2），**不重复计入本条目**。→ `官方来源缺失：Datadog 客户案例页未提供可核验的四要素正文，未取得 USM 专属具名案例`。全稿案例口径与逐条清单见 §6.5。
9. **来源**：
   - 官方来源（必须）：
     - [Automatically discover, map, and monitor all your services in seconds with Universal Service Monitoring](https://www.datadoghq.com/blog/universal-service-monitoring-datadog/) — 发布 2021-10-26（更新 2022-11-29）— 官方博客
     - [Universal Service Monitoring（文档）](https://docs.datadoghq.com/universal_service_monitoring/) — 日期：官方未标注（页面快照于 2026-09-12 确认）— 官方文档
     - [Universal Service Monitoring（产品页）](https://www.datadoghq.com/product/universal-service-monitoring/) — 日期：官方未标注（2026-09-12 确认）— 产品页
   - 非官方来源（可选，仅用于原理补充）：
     - 无（本条目原理全部来自上述官方博客/文档原文表述）

#### 2.1.2 Datadog - Continuous Profiler（持续性能剖析）

1. **技术类别**：传统技术（生产环境持续 profiling）+ AI技术（AI增强：guided insights 自动给出性能发现与修复建议）
2. **首次发布/关键版本时间**：**2020-08-11（GA，官方 S 级新闻稿正文日期 "August 11, 2020"，原文："Datadog... today announced the **general availability** of Continuous Profiler, a **low-overhead 24x7** code profiler"；定价 $12 per host per month）**。**本轮修正说明（B-R1-02）**：v1.0 曾写"官方未明确单一 GA 月份…推断为 2021-2022 年商用"，且 §1 总览表写"2023 Continuous Profiler"——**两处均与官方页面内逐字可读的 2020-08-11 冲突，v1.1 已全部改为 2020-08-11，消除跨章节互斥**。
3. **推出背景**：微服务与容器化让单机性能问题难以复现——pre-production 环境表现良好、生产环境在高负载下劣化（锁竞争、GC、I/O）。传统做法是事故发生后在生产临时启动 profiler，既有开销风险又错过现场；同时分布式追踪的 span 粒度不足以解释"为什么这 200ms 花在了哪里"。工程师需要一个**始终在线、可回溯历史版本对比**的代码级视角。
4. **解决的问题**：
   - 定位拖慢请求的具体函数与线程（span 粒度不足的补充）
   - 加速内存泄漏诊断（持续对比而非事后采样）
   - 识别生产负载下才暴露的低效方法与代码行
   - 追踪每次部署带来的性能回归（canary / blue-green / shadow 对比）
   - 降低 profiling 的专业门槛（guided insights 自动给结论）
5. **技术原理**：Continuous Profiler 采取"**始终在线、低开销、按代码行聚合**"的采样式剖析路线：Agent 在进程内周期性采集调用栈样本（CPU、内存分配、锁、I/O、GC 等维度分别归因），把十万级原始样本**在边缘侧聚合成可长期存储的 profile 时间序列**（而非上传原始样本），因此可以保留长周期历史用于跨版本、跨主机、跨时间窗对比。产品提供三类核心能力：① **span↔profile 关联**——在 APM trace 详情页的 Profiles 标签中直接看到该 span 活跃期间线程级 CPU 活动，从而在 trace 信息不足时补上代码级根因；② **thread-level 可见性**——用于排查并行化问题、死锁、低效 GC、锁竞争；③ **guided insights**——平台自动把发现（如 "GC Pauses"）按严重度汇总并给出分步修复选项，让不具备 profiling 经验的工程师也能行动。**推断边界**：官方产品页未公开采样频率、单进程 CPU 开销百分比、支持的语言/运行时矩阵细节与聚合算法（是否按栈指纹做哈希归并），这些为私有实现，本稿不作断言；"低开销（low overhead）"为官方定性表述。
6. **技术效果**：官方定性表述"complete, always-on visibility"、"low overhead and minimal setup"、"continuously profiling every line across all hosts and containers"。**官方未在该产品页给出量化开销数字**（如 <1% CPU）。可验证的关联能力：APM trace 详情页 Profiles 标签中的 thread-level CPU 活动与 span 对齐（官方页面截图与描述）。
7. **落地情况**：已商用。覆盖"所有主机与容器"的持续剖析为核心卖点；典型客户与规模数据官方产品页未列。
8. **案例**（**v1.1 新增，响应 B-R1-01/B-R1-02，五要素齐备**）：
   - **客户名**：Cvent（虚拟活动平台，官方新闻稿自述"has more than 30,000 customers"）
   - **场景**：Cvent 在其**测试与生产环境的每一个服务上**运行 Datadog Continuous Profiler（原文："we run Datadog Continuous Profiler on **every service** in our testing and production environment"）
   - **结果**：获得对应用前所未有的洞察，**大幅降低诊断潜在问题所需的时间**并修复性能瓶颈（原文："grants us unprecedented insight into our applications, **vastly lowering the time it takes to diagnose potential issues** and fixing performance bottlenecks"）——**客户证言级定性结果，官方未给出该客户的量化百分比**
   - **时间**：2020-08-11（官方新闻稿发布日期）
   - **官方来源 URL**：https://www.datadoghq.com/about/latest-news/press-releases/continuous-profiler/
   - **证言人**：Ian Schell, Site Reliability Architect at Cvent
   - **备注**：该案例是第 1 轮评审 AI 明确指定"可立即补齐"的 S 级官方案例；本轮实测该新闻稿 HTTP 直取成功、正文逐字命中（含 GA 日期、$12/host/月定价与 Cvent 证言）。
9. **来源**：
   - 官方来源（必须）：
     - [Datadog Releases Continuous Profiler for Low-Overhead Application Code Profiling（官方新闻稿，S 级）](https://www.datadoghq.com/about/latest-news/press-releases/continuous-profiler/) — **发布 2020-08-11**（宣布 GA；含 $12/host/月定价与 Cvent 客户证言）— 官方新闻稿
     - [Continuous Profiler（产品页）](https://www.datadoghq.com/product/code-profiling/) — 日期：官方未标注（2026-09-12 确认）— 产品页
     - [Continuous Profiler（文档）](https://docs.datadoghq.com/profiler/) — 日期：官方未标注（2026-09-12 确认）— 官方文档
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.1.3 Datadog - Bits AI（生成式 AI DevOps Copilot）

1. **技术类别**：AI技术（AI增强／生成式 AI 运维助手）
2. **首次发布/关键版本时间**：2023-08（官方博客发布日期 2023-08-03）
3. **推出背景**：2023 年大模型能力跃升，同时可观测性数据量爆炸——"关键基础设施产生海量、异构的可观测数据，把这些数据综合成可行动洞察非常困难，尤其在事故响应的紧张时刻"。运维人员被迫在多个工具与上下文之间反复切换（Datadog App、移动 App、Slack、Confluence、云成本控制台），每次切换都损失响应时间。行业需要一个"对话式统一入口"，把已有平台的检测结果暴露给自然语言交互。
4. **解决的问题**：
   - 事故响应中跨工具切换导致的上下文丢失与响应延迟
   - 海量遥测难以人工综合（无法快速判断影响范围与是否升级为事故）
   - 缺乏查询语言专业知识的成员无法自助取数
   - 处置动作（创建合成测试、触发 workflow、代码修复建议）与调查脱节
   - 同类问题重复发生，缺少事后沉淀
5. **技术原理**：Bits AI 是构建在 Datadog 平台之上的**生成式 AI 对话层**，其技术要点有三：① **单一对话界面覆盖多端**——同一助手可在 Datadog Web App、移动 App 与 Slack 中调用，使工程师在深夜被呼叫时可先在手机上完成初步研判；② **平台内数据检索与关联**——助手不是独立数据源，而是去检索并关联 Datadog 平台已有的结构化检测结果，包括 **Watchdog 检测到的日志/追踪异常**、指标、事件、真实用户事务（RUM）、安全信号（Security Signals）与云成本，因此回答自带可信锚点（例如指出上游服务 `event-intake` 的错误率上升与已有 incident）；③ **自然语言 → 查询语法翻译**——助手理解组织对服务与基础设施的 tag 体系，把口语化提问翻译为正确的查询，从而让不懂查询语言的成员也能取数；④ **动作闭环**——除诊断外，还能建议自动化代码修复、创建合成测试、查找并触发相关 Datadog Workflows，并召回 dashboards 与 Confluence 文档等资产。**推断边界**：官方博客未披露底层模型供应商、是否使用 RAG 检索增强、上下文窗口与幻觉抑制机制、以及是否走 Datadog 自有数据边界；这些为私有实现，本稿不作断言。
6. **技术效果**：官方博客以具体交互示例给出能力描述（如从 `event-processor` 报错自动关联到上游 `event-intake`、发现已存在 incident、按自然语言拉取 dashboard）。**官方未给出量化效果**（如 MTTR 降低百分比、告警收敛率、准确率）。
7. **落地情况**：已商用（Datadog 平台内功能，覆盖 Web/移动/Slack 三端）。规模数据官方未公开。
8. **案例**：**仍然缺失（如实登记）**。Bits AI 属 2023-08 之后的能力，本轮在 Datadog 官方新闻室与博客中**未定位到具名客户的 Bits AI 使用案例**（官方博客 `datadog-bits-generative-ai` 为产品发布稿，仅含产品负责人引语，无客户名）。→ `官方来源缺失：未取得 Bits AI 的具名客户案例`。全稿案例口径见 §6.5。
9. **来源**：
   - 官方来源（必须）：
     - [Introducing Bits AI, your new DevOps copilot](https://www.datadoghq.com/blog/datadog-bits-generative-ai/) — 发布 2023-08-03 — 官方博客
   - 非官方来源（可选，仅用于原理补充）：
     - 无

---

### 2.2 Dynatrace

#### 2.2.0 厂商近10年战略与技术主线（≤500字）

Dynatrace 是**"因果 AI 原教旨主义"**路线的代表，也是本稿中与用户 Server 端 AI 助手最可比对的参照系。其技术主线的骨架是三层：**OneAgent（采集）→ Smartscape（拓扑）→ Davis（因果推理）**。2015-2018 年 Dynatrace 完成从传统 APM 向"全自动全栈可观测"迁移，核心差异化是 OneAgent 单进程自动发现（进程、服务、主机、网络、云）与 **PurePath** 分布式追踪（无需人工埋点配置）；同期建立 **Smartscape** —— 一个持续维护的、包含"谁依赖谁、谁运行在哪"的实时依赖图，这是后续一切 AI 分析的地基。2019 年起 **Davis AI** 正式成为产品核心叙事：它不是统计异常检测，而是**确定性（deterministic）+ 因果（causal）**推理——先在拓扑上做基线建模与异常检测，再沿依赖图做因果传播判定，从而区分"根因"与"受害者"，这是其"无假阳性"宣称的技术来源。2022-2023 年推出 **Grail** 数据湖仓，把日志/追踪/指标统一存储并支持超大规模即席查询，解决传统日志方案的成本与延迟问题。2023-2024 年叠加 **Davis CoPilot**（生成式 AI）与自然语言调查。2024 年后统一为 **Dynatrace Intelligence** 叙事，并加入受策略护栏约束的 **agentic workflows（Preview）**。

对用户的意义：Davis 的"确定性因果 + 拓扑上下文"是 Server 端 AI 助手的**正确性范式**，而非营销词；Smartscape 则是交换机场景最容易迁移的建模思路（把"端口↔链路↔服务↔业务"建成持续维护的图）。

#### 2.2.1 Dynatrace - OneAgent 自动发现与 Smartscape 拓扑建模

1. **技术类别**：传统技术（单 Agent 自动发现 + 实时拓扑图）
2. **首次发布/关键版本时间**：官方未明确单一月份。Smartscape 作为 Dynatrace 平台核心概念在 2015-2016 年已随 OneAgent 架构成型（**前瞻/早期**：其技术前身可回溯至 2013-2014 年的 Dynatrace 6 时代，属奠基性技术，标注"前瞻"）。本稿以官方文档现行状态为准。
3. **推出背景**：**官方来源缺失。** 以下为推断（属 C 级推断，仅供上下文，不构成条目事实）：2015 年前后企业进入混合云与容器化过渡期，应用架构从单体走向分布式，组件数量按数量级增长，且频繁弹性伸缩、动态调度。此时"人工维护 CMDB/依赖清单"彻底失效：没人知道当前跑着哪些进程、谁调用了谁、某个服务部署在哪个主机/容器上。监控工具若不能自动回答"系统长什么样"，所有后续分析（告警、根因、容量）都失去上下文基础。
4. **解决的问题**：
   - 消除对人工配置的依赖，实现进程/服务/主机/网络/云资源自动发现
   - 持续维护实时依赖图，支撑混合云与多云的跨层关联
   - 为根因分析提供"谁依赖谁、谁运行在哪"的拓扑上下文
   - 统一跨技术栈（应用、基础设施、云服务、用户旅程）的实体建模
   - 让新上线服务在无人工登记的情况下自动纳入观测
5. **技术原理**：Dynatrace 采用**"单 Agent + 平台侧自动建模"**架构，区别于"每个技术栈一个 Agent"的拼装方案。采集侧：**OneAgent** 以单一进程部署在主机（含容器/主机两种注入形态），自动发现该主机上的进程、服务、主机资源、网络连接与云元数据，并自动完成应用/服务/进程层级的插桩（不依赖人工逐个配置）。其分布式追踪能力 **PurePath** 提供应用行为的代码级视图。分析侧：**Smartscape** 是一个持续更新的**实时依赖拓扑图**，把自动发现的实体与它们之间的依赖关系（服务调用、主机承载、进程归属、云资源包含）显式建模为图结构，并与日志、追踪、事件打通。官方描述 Smartscape 的作用是"自动发现并映射应用、基础设施、云服务、依赖关系与用户旅程，覆盖混合云与多云环境"。**推断边界**：官方文档未公开 OneAgent 的注入机制细节（是否使用字节码增强/内核模块/二者结合）、图谱存储引擎与更新频率、实体消歧算法；本稿不作断言。需注意 Dynatrace 亦有基于 eBPF 的采集能力，但其官方披露以 OneAgent 自动发现叙事为主，本稿未取得 eBPF 专属官方文档，故不展开。
6. **技术效果**：官方文档定性表述为重点能力（"Automatically discover and map applications, infrastructure, cloud services, dependencies, and user journeys across hybrid and multi-cloud environments"）。**官方未在该文档给出量化数值**（如自动发现覆盖率、发现时延）。
7. **落地情况**：已商用（Dynatrace 平台核心能力，其"agentic AI platform for unified observability, security, and automation"定位的采集与建模基座）。
8. **案例**：本条目（OneAgent 自动发现 + Smartscape 拓扑）为 Dynatrace 平台的采集与建模基座，其客户证据与 §2.2.2 完全同源；按 §6.1 的计数规则（**同一客户案例只在最相关条目计入字段 8，避免重复计入完整率**），**本条目不重复登记案例**，请参见 §2.2.2 的五要素案例清单（Park 'N Fly / ERT / M&B / Temenos / VA）与 §6.5 全稿案例总表。→ 本条目字段 8 按"未独立登记"处理，**计为不齐**。
9. **来源**：
   - 官方来源（必须）：
     - [What is Dynatrace（官方文档）](https://docs.dynatrace.com/docs/discover-dynatrace/what-is-dynatrace) — 日期：官方未标注（2026-09-12 确认，页面标注 5-min read）— 官方文档
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.2.2 Dynatrace - Davis AI 确定性因果分析与根因定位（现统一为 Dynatrace Intelligence）

1. **技术类别**：AI技术（AI原生：确定性因果 AI + 预测 + 生成式）
2. **首次发布/关键版本时间**：**关键版本时间锚点：2023-07-25** —— Dynatrace 官方 IR 新闻稿《Dynatrace Expanding Davis to Deliver the Observability and Security Industry's First Hypermodal Artificial Intelligence, Converging Predictive, Causal, and Generative AI》（页面正文日期 `July 25, 2023 8:00 am EDT`）宣布将 **Davis® AI 引擎**扩展为业界首个**超模态 AI（hypermodal AI）**，并在该稿中首次命名 **Davis CoPilot™**（生成式 AI 组件）。**本轮修正（B-R1-10 ④ / B-R1-08 ③）**：v1.0 把"Davis CoPilot"放进 §3.1 的 **2024** 行，与官方 2023-07-25 冲突，v1.1 已归入 **2023**。**另：v1.0 称"Davis 品牌化 AI 引擎于 2019 年成为核心叙事"——该 2019 时点本轮仍未取得 S/A 级官方发布页，故按 B-R1-10 要求降级标注为 `2019【待核验：无官方发布页】`，不再以确定语气使用**。2024 年后产品叙事统一收敛为 **Dynatrace Intelligence**（官方文档标题已变更）。
3. **推出背景**：2019 年前后 AIOps 概念泛滥，市面上大量"AI 告警"实为**单指标统计阈值/季节性基线**，产生两个后果：① 多指标同时越界时无法判断谁是根因，运维收到"告警风暴"却仍需人工拼图；② 误报率高，团队逐渐不信任 AI 告警。行业真实痛点不是"能不能检测异常"，而是**"能不能指出唯一根因，并解释为什么"**。这要求把拓扑依赖关系与因果关系（而非相关性）引入推理。
4. **解决的问题**：
   - 告警风暴：多组件同时异常时无法分辨根因与受害者
   - 误报：纯统计基线在动态环境中假阳性高，导致告警疲劳
   - 缺少解释：AI 给出结论但不给依据，运维无法采信
   - 变更关联：需要自动把"配置/代码/部署/策略变更"与问题发生对齐，回答"是什么变了"
   - 从技术事件到业务影响：需要说明技术故障如何影响用户与业务结果
5. **技术原理**：Dynatrace Intelligence 的核心是**确定性、基于因果（deterministic, causation-based）的分析**，而非黑盒统计。其推理链条可分四步：① **基线建模**——基于 **Smartscape 实时依赖图**（见 2.2.1）与 **Grail 数据湖仓**中的历史遥测，为每个实体建立多维基线，覆盖应用、服务、基础设施、日志与追踪；② **异常检测**——在基线上检测异常（官方设有独立的 Anomaly Detection 概念页与 App，供用户查看与配置检测范围）；③ **因果推理与根因定位**——把检测到的异常放回拓扑图中，依据依赖方向与时间先后做因果传播判定，从而区分"根因实体"与"被波及实体"，官方描述为"identifies root cause with topology and dependency context"；④ **变更归因**——关联代码变更、部署、配置与策略更新，输出"what changed and why a problem occurred"；⑤ **动作与交互**——通过**agentic workflows 与内置 agents 在策略护栏（policy guardrails）下**提出并运行已批准的动作（官方标注 **Preview**），同时提供**上下文内自然语言**调查与引导式下一步（复查发现、开工单、通知 owner、执行经审核的 runbook）。官方另设有"AI models"文档说明其使用的 AI 模型类别。**推断边界**：官方文档明确"确定性因果"与"基于拓扑依赖"这两个定性机制，但**未公开**具体因果判定算法（如是否使用 Granger 因果、贝叶斯网络、拓扑偏序约束）、基线模型族与灵敏度参数；本稿不作算法级断言，仅复述官方定性路径。
6. **技术效果**：Dynatrace 官网首页引用客户原话："Dynatrace's AI engine provides us with insights for early detection of potential system issues **without false alarms**, reducing the time required to identify root causes **from hours to minutes**。"（客户名未在该页面文摘中给出，来源为客户证言）。**注意：该量化为客户证言（官方页面引用），非厂商受控实验数据**；且"from hours to minutes"为相对表述，缺少基线定义。本稿如实标注其证据等级。
7. **落地情况**：已商用（Davis/Dynatrace Intelligence 为平台核心；agentic workflows 与内置 agents 官方标注为 **Preview**）。规模数据官方未在该文档给出。
8. **案例**（**v1.1 新增：5 个五要素齐备的 Dynatrace 官方案例，全部来自官方新闻稿；响应 B-R1-01**）。逐条格式 `客户 | 行业 | 场景 | 结果 | 时间 | 官方来源URL`：
   - **Park 'N Fly | 机场停车/交通 | 迁移至基于 Kubernetes 与 Microsoft Azure 的云原生架构后，用 Dynatrace 自动可观测管理数字渠道（移动端/Web/机场自助终端） | 开发周期平均加快 29%，最繁忙的两周冲刺期加快 43% | 2021-03-23 | https://www.dynatrace.com/news/press-release/park-n-fly-speeds-up-development-cycles-by-29-with-dynatrace/
   - **ERT | 医疗/生命科学（2019 年 FDA 批准临床试验中 75% 使用其软件与设备）| 用 Davis 监控 DevOps 流程与应用交付管道，并以 Keptn 触发自动自愈 | 新应用交付从平均 6 周缩短到 4 周 | 2020-05-28 | https://www.dynatrace.com/news/press-release/ert-helps-medical-researchers-accelerate-clinical-trials-with-ai-assistance-from-dynatrace/
   - **Mitchells & Butlers（M&B）| 餐饮/酒吧连锁（英国最大之一）| 把数字渠道性能数据与业务指标（桌位预订、收入）打通 | 桌边点单移动应用的客单价比吧台点单高 20% | 2019-12-19 | https://www.dynatrace.com/news/press-release/mitchells-butlers-serves-better-business-results-with-dynatrace/
   - **Temenos | 金融软件 SaaS | 以 Dynatrace 覆盖其基于 Azure + AWS + 本地部署的混合多云 SaaS 平台 | 客户证言级：显著缩短实现价值时间、把团队从人工配置中解放（官方未给出量化百分比）| 2020-10-01 | https://www.dynatrace.com/news/press-release/temenos-enables-seamless-banking-experiences-with-dynatrace/
   - **U.S. Department of Veterans Affairs（VA）| 美国联邦公共部门 | 在 VA Enterprise Cloud 多云环境（本地遗留 + AWS/Azure 容器与微服务）中建立端到端可观测，支撑 350 个关键应用上云 | 更快、更有信心的云迁移（官方未给出量化数字）| 2020-02-11 | https://www.dynatrace.com/news/press-release/dynatrace-enables-speed-and-confidence-in-us-government-agencys-migration-to-the-cloud/
   - **⚠️ 方法论实证（本轮新增，直接支撑 B-R1-08 ①的判定）**：上述 4 条 2019-2021 年新闻稿在 Dynatrace 官方 `press-release-sitemap.xml` 中的 `lastmod` **被统一写成 2020-12-04（M&B/Temenos/ERT）与 2020-08-06（VA）**，而**页面正文日期分别是 2019-12-19 / 2020-10-01 / 2020-05-28 / 2020-02-11**。这**逐字证实了第 1 轮评审的判断：sitemap lastmod 是页面最后修改时间，不能充当"首次发布/公告时间"**。本稿一律采用**页面正文日期**。
   - 说明：v1.0 曾用作"弱案例"的官网首页证言（"hours → minutes，without false alarms"）**因无客户名无时间，已按第 1 轮评审意见从案例计数中剔除**（改列入字段 6 技术效果作为客户证言证据）。
9. **来源**：
   - 官方来源（必须）：
     - [Dynatrace Intelligence（官方文档，原 Davis AI 概念页）](https://docs.dynatrace.com/docs/dynatrace-intelligence) — 日期：官方未标注（2026-09-12 确认）— 官方文档
     - [What is Dynatrace（官方文档）](https://docs.dynatrace.com/docs/discover-dynatrace/what-is-dynatrace) — 日期：官方未标注（2026-09-12 确认）— 官方文档
     - [Dynatrace 官网首页（客户证言引用）](https://www.dynatrace.com/) — 日期：官方未标注（2026-09-12 确认）— 产品页/官网
     - [Dynatrace 投资者关系新闻稿列表](https://ir.dynatrace.com/news-events/press-releases) — 日期：列表页最新条目 2026-08-25（2026-09-12 确认）— 官方新闻稿（IR）
     - **[Dynatrace Expanding Davis to Deliver the Observability and Security Industry's First Hypermodal Artificial Intelligence, Converging Predictive, Causal, and Generative AI（官方 IR 新闻稿，S 级）](https://ir.dynatrace.com/news-events/press-releases/detail/302/dynatrace-expanding-davis-to-deliver-the-observability-and-security-industrys-first-hypermodal-artificial-intelligence-converging-predictive-causal-and-generative-ai)** — **发布 2023-07-25 8:00 am EDT** — 官方新闻稿（IR）。原文逐字命中："expanding its **Davis® AI engine** to create the industry's first **hypermodal artificial intelligence (AI)**, converging fact-based, **predictive- and causal-AI** insights with new **generative-AI** capabilities"、**Davis CoPilot™** 首次命名、以及 "Davis causal AI analyzes real-time and context-rich observability, security, and business data within the **Grail™ data lakehouse** and causal dependencies from **Smartscape® topology**"
     - [Dynatrace 官方新闻稿 sitemap（本轮用于挖掘客户案例 URL）](https://www.dynatrace.com/news/press-release-sitemap.xml) — 抓取于 2026-09-12（**注意：其 lastmod 与页面正文日期不一致，见字段 8 的方法论实证**）— 官方站点地图
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.2.3 Dynatrace - Grail 数据湖仓与 Log Analytics（统一遥测存储与即席查询）

1. **技术类别**：传统技术（数据平台）+ AI技术（AI增强：作为 Davis 因果推理的数据基座）
2. **首次发布/关键版本时间**：**2022-2023 年**。官方未在本稿取得的页面标注精确 GA 月份；据官方文档"Powered by Grail™"表述与产品线（Log Analytics）推断为 2022 年发布、2023 年大规模商用。标注"官方未明确，据官方文档与产品线推断"。
3. **推出背景**：2020-2023 年可观测数据量（尤其日志）爆炸式增长，传统日志方案（全量索引 + 按摄入计费）导致成本失控；同时"日志在 A 工具、指标在 B 工具、追踪在 C 工具"的割裂使跨信号关联需要人工拼接。Dynatrace 需要自己的**统一存储与查询引擎**，既能把 Logs/Metrics/Traces/Events 放进同一语义层以支撑 Davis 的因果推理，又能把海量日志的查询延迟压到"即时回答"级别；其官方宣传点之一是"移除传统日志管理的开销"。
4. **解决的问题**：
   - 日志成本失控与存储膨胀（传统全量索引方案）
   - 跨信号（日志↔指标↔追踪↔事件）关联需人工拼接、上下文丢失
   - 大规模数据下即席查询延迟高，排障时"等查询"
   - 为因果 AI 提供统一、可关联的数据底座（否则 AI 只能在单信号内做判断）
   - 统一多租户与长期留存的经济性
5. **技术原理**：Grail 是 Dynatrace 自研的**数据湖仓（data lakehouse）**，官方定位为"把日志与指标、追踪、事件相关联，提供即时答案，并移除传统日志管理的开销"。其架构要点（据官方表述）：① **统一存储与语义层**——不同信号进入同一平台而非各自独立索引，因此跨信号关联是"存储层内建"而非事后 join；② **按需/延迟物化查询**——官方强调"instant answers"，指向以对象存储为底、按查询需求计算的设计取向（对比传统"写入即全量索引"）；③ **面向 AI 的数据基座**——Dynatrace Intelligence 明确声明其分析"使用 Grail 数据湖仓与 Smartscape 实时依赖图来建立基线、检测异常并识别根因"，即 Grail 提供**数据**、Smartscape 提供**拓扑**，两者共同喂给因果推理；④ **开放摄取**——支持原生 OpenTelemetry，使 OTel 数据进入后即可被平台 AI 能力增强。**推断边界**：官方文档仅给出定性定位（"data lakehouse"、"instant answers"、"removes the overhead of traditional log management"），**未公开**存储格式、索引策略、查询引擎类型（是否基于自有 DQL）、压缩率与成本对比数字；本稿不作断言。注意：官方在 Log Analytics 描述中使用 "Grail™"，本稿未取得 Grail 独立产品页，故以官方文档表述为准。
6. **技术效果**：官方定性表述为"analyze massive volumes of log data with context and speed"、"instant answers"、"reduce costs"。**官方未在本稿取得的页面给出量化数据**（如查询延迟 ms 级、成本下降百分比、压缩比）。
7. **落地情况**：已商用（Dynatrace 平台数据基座，支撑 Log Analytics 与 Dynatrace Intelligence）。
8. **案例**：**未能定位 Grail 专属的具名客户案例**（Dynatrace 官方案例库列表页在本环境不可枚举；官方新闻稿中 Grail 主要作为 Davis 的数据基座被提及，未单独作为客户案例叙事）。按 §6.1 计数规则不重复计入 §2.2.2 的案例 → 本条目字段 8 **计为不齐**。→ `官方来源缺失：未取得 Grail 专属五要素案例`。
9. **来源**（**v1.1 补充：Grail 与 Davis 的关系已由 2023-07-25 官方 IR 新闻稿原文佐证**）：
   - 官方来源（必须）：
     - [What is Dynatrace（官方文档，含 Grail 定位与 Log Analytics 描述）](https://docs.dynatrace.com/docs/discover-dynatrace/what-is-dynatrace) — 日期：官方未标注（2026-09-12 确认）— 官方文档
     - [Dynatrace Intelligence（官方文档，Grail 作为分析数据基座的说明）](https://docs.dynatrace.com/docs/dynatrace-intelligence) — 日期：官方未标注（2026-09-12 确认）— 官方文档
     - [Dynatrace 扩展 Davis 为超模态 AI（官方 IR 新闻稿，明载 Davis causal AI 在 Grail™ data lakehouse 与 Smartscape® topology 上分析）](https://ir.dynatrace.com/news-events/press-releases/detail/302/dynatrace-expanding-davis-to-deliver-the-observability-and-security-industrys-first-hypermodal-artificial-intelligence-converging-predictive-causal-and-generative-ai) — **发布 2023-07-25** — 官方新闻稿（IR）
   - 非官方来源（可选，仅用于原理补充）：
     - 无

---

### 2.3 New Relic

#### 2.3.0 厂商近10年战略与技术主线（≤500字）

New Relic 是**"老牌 APM 向统一数据平台 + AI 可观测转型"**的典型案例，对用户 Server 端 AI 助手有两点独特参考价值：**用量制商业模式驱动的数据架构**，以及**"AI 应用本身成为被观测对象"的最早产品化**。2015-2019 年 New Relic 以 APM + Browser/Mobile（RUM）+ Infrastructure 的多产品矩阵为主，Agent 生态以各语言独立 Agent 为核心。2020 年进行平台级重构，提出 **Telemetry Data Platform**，打破"APM/Browser/Infra/Logs 各自独立后端"的割裂，统一到同一数据平面并提出 **NRQL**（类 SQL 查询语言）作为统一取数入口——这一点与用户"采集端统一上送、Server 端统一分析"的架构取向直接同构。2022 年起接入 OpenTelemetry 优先策略，成为 OTel 的早期商业支持者。2023 年推出 **New Relic AI**（生成式 AI 助手，NRQL 自然语言化是核心）。2024 年起把 **AI Monitoring** 产品化：监测 LLM 调用、token 与成本、质量指标，并把 **MCP（Model Context Protocol）** 调用链路纳入分布式追踪——这是"AI 助手本身也需要被观测"的先声，与用户正在开发的 Server 端 AI 助手高度相关。2025-2026 年叙事进一步转为 Agentic AI 与 agent 工作流观测。

#### 2.3.1 New Relic - 统一可观测平台与 NRQL 查询语言

1. **技术类别**：传统技术（统一遥测数据平台 + 查询语言）
2. **首次发布/关键版本时间**：**官方未明确（本稿未能取得"平台统一/Telemetry Data Platform 发布"的官方新闻稿或博客）**。**本轮修正（B-R1-08 ①）**：v1.0 以"官方 sitemap 的 lastmod"作为该年份依据，**该证据类型不成立**——sitemap lastmod 是**页面最后修改时间**，不是发布时间；且本轮在 Dynatrace 侧已用 4 条新闻稿**实证 lastmod 与页面正文日期相差 8-14 个月**（见 §2.2.2 字段 8）。故本字段改标：`2020【待核验：原依据 sitemap lastmod，该证据已废止；未取得官方发布页】`。可验证的官方时间证据：New Relic 官方新闻稿 URL 规则 `newrelic.com/press-release/YYYYMMDD` **本轮实测有效**（示例 `20240911` 正文日期 `September 11, 2024`、`20241001` 正文日期 `October 1, 2024`）。
3. **推出背景**：2015-2020 年 New Relic 的产品矩阵（APM、Browser、Mobile、Infrastructure、Logs、Synthetics）各自有独立数据模型与独立 UI，客户遭遇"同一故障在 4 个产品里各看一半"的困境；同时 SaaS 按时长/主机计费模式在容器化、Serverless 普及后失真（主机数不再等于用量）。行业要求可观测厂商提供**单一数据平面 + 统一查询语义 + 与用量对齐的计费**。NRQL 的价值在于把"会不会用某个产品的 UI"降级为"会不会写一条查询"，从而让排障不再依赖工具熟练度。
4. **解决的问题**：
   - 多产品数据孤岛，跨信号关联需人工切换与拼接
   - 查询语言互不通用，学习成本高、知识无法跨产品迁移
   - 计费模型与容器化/Serverless 实际用量脱节
   - 缺少统一取数入口，导致自动化/报表/告警各写一套
   - 为上层 AI 能力提供统一、可编程的数据访问面（否则 AI 无法跨信号取数）
5. **技术原理**：New Relic 的技术路线是**"统一数据平面 + 统一查询层"**。① **统一摄取**：各语言 Agent、基础设施集成、日志转发器与 OpenTelemetry 数据统一汇入同一数据平面（官方文档将其描述为 single intelligent platform，把 telemetry、operational context、AI 与业务数据汇聚）。② **统一查询语义**：**NRQL**（New Relic Query Language）是类 SQL 的查询语言，官方定义为"访问 New Relic 中详细数据的强大类 SQL 工具，可获取应用、主机与业务运营的具体信息"；其关键设计是**同一语言跨信号查询**（APM、基础设施、日志、业务数据），使告警条件、Dashboard、API 取数共用同一表达方式，也让"自然语言 → NRQL"成为可行的 AI 接口（见 2.3.3）。③ **统一上下文**：平台把 telemetry 与 operational context（部署、变更、事件）以及业务数据拼装在同一视图，官方宣称目标是"isolate the root cause and reduce MTTR"。④ **用量对齐**：计费与数据用量（而非主机数）挂钩，配合**基数管理**（cardinality management）与数据管道可观测（data pipeline observability）等官方最佳实践主题，控制高基数成本。**推断边界**：官方页面未公开底层存储引擎（是否自研时序/列存）、NRQL 执行引擎与跨信号 join 的实现机制、基数上限；本稿不作断言。
6. **技术效果**：官方定性表述为统一平台可"correlate your telemetry across your entire stack, so you can isolate the root cause and reduce MTTR"。**官方未在该页面给出量化数据**（如 MTTR 降低百分比、查询延迟）。
7. **落地情况**：已商用（New Relic 全线产品的基础平台；官方同时提供 OpenTelemetry 接入路径作为厂商中立替代）。
8. **案例**（**v1.1 新增，五要素齐备；响应 B-R1-01**）：`客户 | 行业 | 场景 | 结果 | 时间 | 官方来源URL`
   - **CareerVillage | 教育科技（EdTech）非营利 | 把可观测实践标准化到 New Relic 统一平台，用 APM 跟踪延迟趋势与代码级瓶颈、用告警管理在用户受影响前发现并解决问题；并用于监控其 AI 职业教练应用 "Coach" | 页面加载时间**下降 67%**（从 300ms 降至 100ms 以内）；支撑峰值 **700 名学生并发登录**、高峰月 **6,000+ 学生提问**；工程团队生产力**提升 133%** | **2024-10-01** | https://newrelic.com/press-release/20241001
   - **配套说明**：该案例来自 **New Relic 官方新闻稿**（S 级），页面正文日期逐字可读。它同时证明：① New Relic 官网**确有具名客户 + 量化结果的官方案例**，v1.0 "官方案例库不可枚举"的结论需要修正（`newrelic.com/customers` **本轮实测 HTTP 200 且可抓取**，另有 Verisk/BlackLine/Kurt Geiger/Shutterstock/Statista/Watch Duty 等具名客户与量化结果的次级案例，见 §6.5 表 B）；② 该案例不重复计入 §2.3.2/2.3.3。
9. **来源**：
   - 官方来源（必须）：
     - [New Relic 官网首页（平台定位与 MTTR 表述）](https://newrelic.com/) — 日期：官方未标注（2026-09-12 确认）— 产品页/官网
     - [New Relic Observability Platform](https://newrelic.com/platform) — 日期：官方未标注（2026-09-12 确认）— 产品页
     - [Get started with New Relic（官方文档，NRQL 定义）](https://docs.newrelic.com/docs/new-relic-solutions/get-started/intro-new-relic/) — 日期：官方未标注（2026-09-12 确认）— 官方文档
     - **[CareerVillage and New Relic Transform EdTech with AI-Powered Career Coaching（官方新闻稿，S 级）](https://newrelic.com/press-release/20241001)** — **发布 2024-10-01**（含 67% 页面加载时间下降、133% 工程效率提升等量化结果）— 官方新闻稿
     - [New Relic 官方案例库（Our Customers）](https://newrelic.com/customers) — 日期：官方未标注（2026-09-12 确认；列表页含具名客户与量化结果）— 官方案例库
     - [New Relic 站点 sitemap](https://newrelic.com/sitemap.xml) — 抓取于 2026-09-12（**仅用于发现 URL，其 lastmod 已按 B-R1-08 从"首次发布时间"用途中废止**）— 官方站点地图
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.3.2 New Relic - AI Monitoring（LLM / MCP / Agent 可观测）——AI技术

1. **技术类别**：AI技术（AI增强：把 AI 应用与 LLM 调用链纳入可观测范围）
2. **首次发布/关键版本时间**：**官方未明确（本轮未取得 AI Monitoring 的官方发布新闻稿/博客）**。**本轮修正（B-R1-08 ①）**：v1.0 以"官方 sitemap 中若干 `newrelic.com/blog/ai/*` 页面的 lastmod（2024-09-17、2024-12-13）"推断为 2024 年——**该证据类型不成立**（lastmod ≠ 发布日期，且这些页面的 lastmod 在 sitemap 中大量被统一写成同一时刻，明显是批量重建时间戳）。故改标：`2024【待核验：原依据 sitemap lastmod，已废止】`。可确证的官方时间事实：产品页 `newrelic.com/platform/ai-observability` 已上线（日期官方未标注）。
3. **推出背景**：2023-2024 年生成式 AI 应用从试验走向生产，出现一类**传统监控无法捕捉的故障模式**：服务返回 HTTP 200、基础设施指标全绿、Dashboard 毫无异常，但**模型准确率悄悄从 95% 掉到 70%**——即"AI 系统会在看起来没坏的情况下失败"。原因是 AI 的失效发生在数据漂移（data drift）、概念漂移（concept drift）与静默劣化上，而非 CPU/内存/延迟/错误率这四类黄金信号。同时 LLM 引入新的成本维度（token）与质量维度（幻觉、偏见、毒性），需要专门的观测面。
4. **解决的问题**：
   - 静默劣化：模型质量下降但不触发任何传统告警
   - 成本不可控：token 消耗与多模型成本无法按应用归因
   - AI 调用链不可见：无法回答"45 秒的响应里，是模型慢、工具调用慢，还是重试循环"
   - 多 Agent / MCP 生态：工具（tool）与函数调用分散在多 Agent 之间，缺少端到端调用流视图
   - 质量与安全：幻觉、偏见、毒性以及 MCP 服务的滥用/恶意攻击缺少可见性
5. **技术原理**：New Relic AI Monitoring 的技术设计核心是**"复用既有分布式追踪骨架，把 AI 语义注入 span"**，而非另建一套监控。① **零新增埋点**——官方宣称"no new instrumentation needed"，即 AI 层观测复用平台已有的追踪能力与集成；② **自动捕获 AI 调用**——通过内置集成（官方列举 OpenAI 等模型、Pinecone 等向量数据、LangChain 等框架）自动采集模型调用、响应时间、token 用量与错误；③ **MCP 全生命周期追踪**——官方强调可"see details of every MCP server call"、"monitor the entire Model Context Protocol (MCP) request lifecycle automatically"，即把 MCP 服务调用作为一种被追踪的调用类型，识别每次工具/函数调用并定位瓶颈；④ **多 Agent 拓扑可视化**——通过分布式追踪中的 agent 与 tool 调用把"哪个 agent 调用了哪个 tool"显式建模，官方描述为"move beyond individual LLM tracking by automatically capturing and visualizing complex call flows"；⑤ **质量维度**——记录模型响应以识别离群值，并提供从 prompt 到 response 的完整 trace（含用户反馈），以发现幻觉/偏见/毒性；⑥ **成本维度**——跟踪请求 token 用量并支持自定义告警，跨模型比较成本/性能/质量以指导选型。**推断边界**：官方产品页为能力清单式描述，**未公开**具体 SDK 注入方式（OpenTelemetry GenAI 语义约定 / 自定义属性）、采样策略、token 计量精度与多 Agent 图谱的构建算法；本稿不作断言。另需说明：OpenTelemetry 侧正在推进 **GenAI 语义约定**（官方 OTel 博客 2026-09 “Inside the LLM Call: GenAI Observability with OpenTelemetry”），New Relic 的实现与之关系本稿未取证。
6. **技术效果**：官方产品页给出能力与收益的定性表述（"Find and fix issues faster"、"Optimize your AI workloads"、"Keep your AI app performance high and costs low"），并列出可采集的具体指标类型（response time、quality、tokens、APM golden signals、infrastructure）。**官方在该页面未给出量化效果**（如劣化检出提前量、成本下降百分比）。
7. **落地情况**：已商用（New Relic 平台在售产品页 `newrelic.com/platform/ai-observability`）。规模数据官方未公开。
8. **案例**：**未能取得 AI Monitoring（LLM/MCP/Agent 观测）的具名客户 + 量化结果案例**；本轮已抓取 `newrelic.com/customers`（HTTP 200，含 Verisk −59% 告警量、BlackLine 年省 $1,600 万、Statista 延迟 −95% 等具名量化案例）与官方新闻稿 `20241001`（CareerVillage，含 AI 职业教练监控），但**这些案例的官方页面均未标注发布日期**，故五要素中"时间"要素缺失，**不计入 §6.5 表 A 的 13 个五要素案例，只计入表 B 次级案例**。CareerVillage 案例已按"同一案例只在最相关条目计入"的规则归入 §2.3.1。→ 本条目字段 8 **计为不齐**。`官方来源缺失：未取得 AI Monitoring 专属且带官方日期的五要素客户案例`。
9. **来源**：
   - 官方来源（必须）：
     - [AI Observability for Modern Applications（产品页）](https://newrelic.com/platform/ai-observability) — 日期：官方未标注（2026-09-12 确认；页面标题返回为 "AI Observability for Modern Applications"）— 产品页
     - [Guide to AI Observability: Core Components, Tools, and Best Practices（官方博客/指南）](https://newrelic.com/blog/ai/ai-in-observability) — **日期：官方页面正文未标注发布日期（2026-09-12 确认；v1.0 引用的"lastmod 2026-07-20"已按 B-R1-08 废止）** — 官方博客
     - [New Relic 官方案例库（Our Customers）](https://newrelic.com/customers) — 日期：官方未标注（2026-09-12 确认）— 官方案例库
     - [New Relic 站点 sitemap（仅用于发现 URL）](https://newrelic.com/sitemap.xml) — 抓取于 2026-09-12 — 官方站点地图
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.3.3 New Relic - New Relic AI（生成式 AI 助手 / 自然语言排障）

1. **技术类别**：AI技术（AI增强：生成式 AI 运维助手）
2. **首次发布/关键版本时间**：**官方未明确（本轮未取得 New Relic AI 的官方发布新闻稿）**。**本轮修正（B-R1-08 ①）**：v1.0 以"官方 sitemap 中已存在 `newrelic.com/blog/ai/*` 主题群"推断为 2023 年——**该证据类型不成立**，已废止。故改标：`2023【待核验：无官方发布页】`。
3. **推出背景**：与 Datadog Bits AI 同期（2023 年大模型浪潮）面对同类痛点，但 New Relic 的切入角度不同：其平台以 **NRQL** 为统一取数入口，因此"自然语言 → NRQL"成为其 AI 助手最自然、也最可验证的落地形式。真实痛点是：NRQL 虽比多套 UI 更统一，但仍是一门查询语言，测试/研发/值班同学在没有查询语言训练的情况下无法自助取数；而排障时"取不到数"就等于"定位不了"。
4. **解决的问题**：
   - 非查询专家无法自助从统一平台取数
   - 排障时的多轮人工试错（改查询、换维度、换个时间窗）
   - 将零散查询结果综合为可读结论仍需人工
   - 把平台已有的 AI 观测能力（AI Monitoring）与运维助手体验打通
   - 降低测试同学"发现异常"与开发同学"定位异常"之间的协作摩擦
5. **技术原理**：技术路线为**"统一查询层之上的自然语言层"**。① **语义映射到 NRQL**——助手把自然语言意图翻译为 NRQL 查询，复用平台已有的查询执行引擎与数据平面，因此回答基于真实遥测而非模型记忆，这是可控性（可审计、可复现）的关键；② **上下文感知**——助手需要理解组织的实体命名（应用、主机、服务、业务实体）与既有 Dashboard/告警定义，才能把"我的支付服务为什么慢"映射到正确的实体与信号；③ **跨信号取数**——依托 2.3.1 的统一平台，单次提问可横跨 APM、基础设施、日志与业务数据；④ **与 AI Monitoring 协同**——当被观测对象本身是 AI 应用时，助手可查询 LLM/MCP/agent 的专有信号（token、质量、工具调用链），形成"用 AI 观测 AI、用 AI 排障 AI"的闭环。**推断边界**：官方产品页为营销式能力描述，**未公开**助手底层模型、是否使用 RAG、工具调用（function calling）清单、NRQL 生成的校验机制与幻觉抑制策略；本稿不作断言。**注意：本条目的技术原理推断成分高于 2.1.3（Bits AI）**，因为 Datadog 官方博客提供了可引用的具体交互示例，而 New Relic 侧本稿仅取得产品页与文档定义，评审时请优先补充官方博客原文。
6. **技术效果**：**官方未给出量化数据**（本稿取得的官方页面未提供 MTTR 降低、查询准确率等指标）。
7. **落地情况**：已商用（New Relic 平台 AI 能力组成部分，2024-2026 年随 Agentic AI 叙事持续扩展）。
8. **案例**：**未能取得 New Relic AI（生成式助手）专属的具名客户 + 量化结果案例**（同 2.3.2：官方 customers 页与本轮抓取的新闻稿中无该助手专属案例）。→ 字段 8 **计为不齐**。
9. **来源**：
   - 官方来源（必须）：
     - [New Relic Observability Platform（AI 能力定位）](https://newrelic.com/platform) — 日期：官方未标注（2026-09-12 确认）— 产品页
     - [New Relic 官网首页](https://newrelic.com/) — 日期：官方未标注（2026-09-12 确认）— 产品页/官网
     - [New Relic 新闻稿样例（2024-09-11，用于确认 URL 规则 `press-release/YYYYMMDD` 有效）](https://newrelic.com/press-release/20240911) — **发布 2024-09-11** — 官方新闻稿
   - 非官方来源（可选，仅用于原理补充）：
     - 无

---

### 2.4 Cisco（AppDynamics + Splunk 整合）

#### 2.4.0 厂商近10年战略与技术主线（≤500字）

Cisco 在可观测领域的技术主线是**"两次收购 + 一次网络与应用的合流"**。第一次收购是 **2017-03 完成对 AppDynamics 的收购【待核验：未取得 Cisco 官方新闻稿，Cisco IR 站点被 Cloudflare 拦截】**，Cisco 由此直接获得企业级 APM 能力（AppDynamics 在被收购前是 APM 市场头部玩家之一，以字节码注入式 Agent、Business Transaction 建模与 .NET/Java 深度诊断见长）。**2021 年前后 AppDynamics 推出 Cognition Engine【待核验：本轮未取得任何 S/A 级来源；v1.0 曾在 §1、§2.4.0、§2.4.1 三处以确定语气使用该时点，已按 B-R1-10 ②统一降级为"未取证的背景性表述"】**，把"基线学习 + 动态基线 + 异常关联"产品化，是其在 AIOps 方向的关键动作。第二次收购是 **2024-03 Cisco 完成对 Splunk 的收购（约 280 亿美元）【待核验：未取得 Cisco/Splunk 官方新闻稿原件】**，这是 Cisco 历史上最大并购，战略意图是把"网络与安全数据"（Cisco 的本业，掌握海量设备与流量侧数据）与"机器数据分析平台"（Splunk 的本业）合并，形成"网络 + 安全 + 可观测"三位一体。整合后的产品叙事是：AppDynamics（应用侧 APM）+ Splunk Observability Cloud（基础设施/APM/RUM/日志）+ **Splunk ITSI**（服务智能与事件关联，负责把告警噪声收敛为业务服务健康度）+ **Splunk AI Assistant**（生成式 AI，把 SPL 查询自然语言化）。

> **⚠️ 本节时点的证据状态（v1.1 新增，响应 B-R1-10）**：本节三个时间点（2017-03、2021 前后、2024-03）**均无 S/A 级官方来源**，已全部加 `【待核验】`。Cisco 官方 IR（`investor.cisco.com/news-releases`）本轮实测返回 **Cloudflare "Just a moment..."** 人机校验页；`newsroom.cisco.com` 新闻稿列表返回 **"No articles found"**（JS 渲染）；Cisco 新闻室索引页虽可访问但不暴露新闻稿正文。**因此本稿对 Cisco 的两次收购与 Cognition Engine 一律不作已证实事实使用**，§3.1 时间线与 §5 建议中凡引用处均已同步加注。

对用户的意义有两点特别值得注意：① **Cisco 是"网络设备厂商做可观测"的最大样本**，其"设备侧数据 + 应用侧上下文"的合流路径，正是用户在交换机内部做 APM 时最直接的竞品/参照；② **Splunk ITSI 的"服务健康度评分 + 事件关联 + 告警收敛"建模**，是 Server 端 AI 助手做告警收敛时可直接借鉴的既有范式（早于 LLM 时代，且已被大规模部署验证）。

#### 2.4.1 Cisco/Splunk - Splunk IT Service Intelligence（ITSI，服务智能与告警收敛）

1. **技术类别**：传统技术（服务健康度建模与事件关联）+ AI技术（AI增强：异常检测与事件智能，2024-2026 叠加 AI Assistant）
2. **首次发布/关键版本时间**：`官方未明确【待核验】`。v1.0 的"据 Splunk 产品线演进为 2014-2016 年推出"属**无来源推断**，按 B-R1-10 的要求**不得以确定语气使用**；本轮实测 `https://www.splunk.com/en_us/newsroom/press-releases.html`（HTTP 可抓取，列表自 2020 年起按年分组）与 Splunk ITSI 产品页，**均未取得 ITSI 首次发布公告**。故保留"官方未明确（产品页现行版本为 2026 年前后的在售版本）"，并显式标注 `【待核验】`。
3. **推出背景**：**官方来源缺失：未能取得官方背景陈述。** 以下为基于行业公开事实的推断（属 C 级推断，仅供上下文，不构成条目事实）：2015 年前后企业 IT 已完成工具化监控（每个系统都有自己的告警），但产生了新的结构性问题：**告警与业务影响脱节**。一次数据库抖动可能触发 200 条来自不同工具的告警，值班人员无法判断"这 200 条告警对应哪一项业务服务、影响到哪些用户、该不该叫醒更多人"。行业需求从"能监控"升级为"能判断影响面"——即需要把技术指标聚合成**业务服务级健康度**，并把相关告警合并为一个可处置的事件。
4. **解决的问题**：
   - 告警噪声：多源告警风暴，人工无法逐条研判
   - 技术与业务割裂：无法把技术指标映射到业务服务的健康度
   - 缺少统一影响面视图：不清楚故障影响到哪些业务与用户
   - 事件关联缺失：同一根因产生的多条告警未自动合并
   - 处置流程不闭环：缺少从事件到工单/通知/复盘的结构化流转
5. **技术原理**：ITSI 的核心抽象是**"服务（Service）由 KPI 组成，KPI 由指标/事件计算"**。① **服务树建模**——用户先定义业务服务（如"网银转账"），把该服务的健康度拆解为若干 KPI（如交易成功率、平均响应时间、依赖组件可用性），每个 KPI 绑定具体的数据源（指标、日志、事件）。② **健康度评分（Health Score）**——把各 KPI 的当前值与阈值/基线比较，加权聚合为服务的数值化健康分与颜色状态，使"业务服务现在好不好"成为一个可告警的标量。③ **事件关联与聚合**——ITSI 的 Episode 机制把同一时间窗内、具备相关性（相同服务/相同实体/时间邻近）的多条告警聚合为一个 Episode，显著压缩告警条数。④ **异常检测与动态基线**——ITSI 内置针对 KPI 的异常检测能力，用历史模式建立动态基线以替代静态阈值（对应其在 AIOps 方向的定位）。⑤ **与 ITSI/AI Assistant 协同**——2024 年后 Splunk 把生成式 AI Assistant 接入（见 2.4.3 与 Splunk Observability Cloud 页面中列出的 "AI Assistant" 与 "AI SRE" 能力），使运维可用自然语言对 ITSI 事件与 SPL 数据提问。**推断边界**：官方产品页为营销式描述，**未公开**健康度评分的加权算法、异常检测所用模型族、Episode 关联规则的具体判据与规模上限。本条目中"Health Score / KPI / Episode"的机制描述基于 ITSI 产品公开定位的通用理解，**属推断，需在第2轮修订时以官方文档（`help.splunk.com/en/splunk-it-service-intelligence`）原文逐条替换**。
6. **技术效果**：官方产品页定性表述为"Turn alert noise into actionable event intelligence, connecting technical performance to the business impact of service health"。**官方未在该页面给出量化数据**（如告警压缩比、MTTR 改善）。
7. **落地情况**：已商用（Splunk 在售产品，具备独立文档站与定价页；Splunk 官网在产品页下方列有 "More customers" 客户入口）。规模数据本稿未取证。
8. **案例**（**v1.1 部分补齐，但仍计为不齐**）：本轮实测 `https://www.splunk.com/en_us/customers.html` **HTTP 200 且正文可抓取**，取得下列**具名客户 + 量化结果**的官方客户故事：**Specsavers（MTTR 快 10 倍、单月预防 100+ 关键与 500+ 重大事件、自动化每月节省 25,000 小时）**、**Singapore Airlines（问题发现快 75%+、后端问题减少 90%）**、**Children's National Hospital（威胁检出 +40%、分析师效率 +25%）**、**Progressive Insurance（保护 1200 亿美元市值、采集 8M traces/50M spans）**、**Carrefour（威胁响应快 3 倍）**。**但这些官方客户故事页面在抓取到的正文中未暴露发布日期**，五要素中的"时间"要素无法在官方页面内确认，故**不计入 §6.5 表 A 的 13 个五要素案例，只登记于表 B 次级案例**。→ 本条目字段 8 **计为不齐**（`官方来源缺失：Splunk 客户故事页未标注发布日期，缺"时间"要素`）。
9. **来源**：
   - 官方来源（必须）：
     - [Splunk IT Service Intelligence（产品页）](https://www.splunk.com/en_us/products/it-service-intelligence.html) — 日期：官方未标注（2026-09-12 确认；页面含 2026-09-14~15 .conf26 直播提示）【2026延伸·窗口外】— 产品页
     - [Splunk IT Service Intelligence 官方文档入口](https://help.splunk.com/en/splunk-it-service-intelligence) — 日期：官方未标注（链接由产品页给出，2026-09-12 确认）— 官方文档
     - [Splunk 官方案例库（Customer Stories）](https://www.splunk.com/en_us/customers.html) — 日期：官方未标注（2026-09-12 确认；含 Specsavers / Singapore Airlines / Children's National Hospital / Progressive / Carrefour 等具名量化案例）— 官方案例库
     - [Splunk 官方新闻室新闻稿列表](https://www.splunk.com/en_us/newsroom/press-releases.html) — 列表自 2020 年起按年分组至 2026（2026-09-12 确认）— 官方新闻稿列表
   - 非官方来源（可选，仅用于原理补充）：
     - 无（Health Score/KPI/Episode 机制描述已在字段5标注为推断，需以官方文档替换）

#### 2.4.2 Cisco/Splunk - Splunk AppDynamics（应用性能监控与混合/本地部署）

1. **技术类别**：传统技术（字节码注入式 APM）+ AI技术（AI增强：Cognition Engine 动态基线与根因关联）
2. **首次发布/关键版本时间**：AppDynamics 产品本身早于调研窗口（公司成立于 2008 年，产品在 2010 年代已成 APM 头部）；**Cisco 于 2017-03 完成收购【待核验：Cisco IR 站点本轮实测被 Cloudflare 人机校验拦截（返回 "Just a moment..."），官方新闻稿未能取得；`newsroom.cisco.com` 新闻稿列表为 JS 渲染、返回 "No articles found"】**，产品在其后持续迭代至 24.x/25.x 版本线。**本轮修正（B-R1-10 ①②）**：v1.0 在 §1 总览表与 §3.1 以**确定语气**写"2017-03 Cisco 收购 AppDynamics"，同时在本条目字段 9 自认"官方新闻稿 URL 本环境未能取得"——**同一文档层级间确定度互斥**。v1.1 已在 §1/§2.4.x/§3.1 三处统一加 `【待核验】` 标记，禁止以确定语气使用。
3. **推出背景**：**官方来源缺失：未能取得官方背景陈述。** 以下为基于行业公开事实的推断（属 C 级推断，仅供上下文，不构成条目事实）：2015-2020 年企业应用架构分裂为两半：一半跑在公有云/容器（云原生 APM 的主场），另一半仍跑在私有数据中心与大型机上（金融、电信、政企的核心交易系统）。纯 SaaS APM 厂商对**混合与本地部署（hybrid and on-prem）**支持不足，而这类客户恰恰是交易类业务、合规敏感行业，不能把生产遥测上公有云。需求是"既不放弃云原生，又能覆盖本地老系统的全栈可观测"。
4. **解决的问题**：
   - 混合架构下云侧与本地侧观测割裂
   - 本地/合规环境无法采用纯 SaaS 遥测上云方案
   - 应用性能指标与业务表现（Business Transaction）脱节，无法量化"慢了多少收入"
   - 复杂调用链（含大型机、ESB、数据库）缺少端到端业务事务视角
   - 从"发现慢"到"定位到具体代码/DB 语句"的路径过长
5. **技术原理**：AppDynamics 的技术路线是**"Business Transaction 为中心 + Agent 深度注入"**。① **业务事务建模**——先进之处在于不以"服务器/进程"为第一视角，而以**业务事务（Business Transaction，如"下单""转账"）**为一等公民：Agent 识别进入系统的请求并按规则归类为业务事务，所有下游调用、DB 语句、外部服务与消息队列都被归属到该事务下，从而能回答"这个业务现在每分钟成功多少笔、慢在哪里"。② **Agent 注入**——Java/.NET 等通过字节码增强（agent 挂载）自动插桩，无需逐方法埋点；同时提供机器代理（Machine Agent）采集主机与 JVM/CLR 指标。③ **业务影响量化**——官方产品页强调"Correlate performance metrics with business performance"，即把性能与业务指标关联，用于评估性能问题对业务的冲击。④ **部署形态**——官方明确支持 hybrid 与 on-prem 部署（AppDynamics On-Premises 版本线），这是其相对纯 SaaS 竞品的结构性差异。⑤ **AI 增强**——Cognition Engine 在其上叠加动态基线学习与跨层异常关联（本稿未取得该功能的官方文档原文，机制细节标注为推断边界）。**推断边界**：官方产品页为价值陈述式描述（"Optimize hybrid and on-prem application performance with full-stack observability linked to business performance"），本文中关于字节码注入、Business Transaction 归类规则、Machine Agent 的技术描述**基于 APM 领域通用原理与产品公开定位，属推断**，需在第2轮以 `help.splunk.com/en/appdynamics-saas` 与 AppDynamics 官方文档原文替换。
6. **技术效果**：官方产品页定性表述为"full-stack observability linked to business performance"、"Correlate performance metrics with business performance"。**官方未在该页面给出量化数据**。
7. **落地情况**：已商用（Splunk 在售产品，官网提供 30 天免费试用与 guided tour；文档站 `help.splunk.com/en/appdynamics-saas`）。收购后品牌调整为 "Splunk AppDynamics"（官网 301 跳转自 `appdynamics.com`）。
8. **案例**：**未能取得 AppDynamics 专属的具名客户 + 量化结果 + 官方日期案例**。本轮已实测 Splunk 官方案例库（`splunk.com/en_us/customers.html`，HTTP 200，含 5 个具名量化客户）与 Splunk 新闻室列表（2020-2026），但**无 AppDynamics 专属案例、且客户故事页未标注发布日期**。按 §6.1 规则，Splunk 客户案例归入 §2.4.1 登记（并因缺"时间"要素仅列入 §6.5 表 B），本条目不重复计入。→ 字段 8 **计为不齐**。
9. **来源**：
   - 官方来源（必须）：
     - [Splunk AppDynamics（产品页，由 appdynamics.com 301 跳转）](https://www.splunk.com/en_us/products/splunk-appdynamics.html) — 日期：官方未标注（2026-09-12 确认；原 `https://www.appdynamics.com/product/how-it-works` 301 至此）— 产品页
     - [Splunk AppDynamics 官方文档入口](https://help.splunk.com/en/appdynamics-saas) — 日期：官方未标注（链接由产品页给出，2026-09-12 确认）— 官方文档
     - [Splunk Observability Cloud（产品页，含 APM/AI SRE/AI Assistant/Agent Observability 能力清单）](https://www.splunk.com/en_us/products/observability-cloud.html) — 日期：官方未标注（2026-09-12 确认）— 产品页
   - 非官方来源（可选，仅用于原理补充）：
     - 无
   - **缺口登记**：Cisco 收购 AppDynamics（2017-03）与 Cisco 完成收购 Splunk（2024-03）的**官方新闻稿 URL 本环境未能取得**（Cisco IR 站点与 newsroom 未成功抓取），故本条目时间字段未引用 S 级来源，已登记为缺口。

#### 2.4.3 Cisco/Splunk - Splunk Observability Cloud 与 AI Assistant / AI SRE

1. **技术类别**：AI技术（AI增强：生成式 AI 助手 + AI SRE）
2. **首次发布/关键版本时间**：`官方未明确【待核验】`。据 Splunk 产品线公开演进，Splunk AI Assistant 于 **2023-2024 年**推出（大模型浪潮下的行业普遍节奏）；**本稿未取得 S 级发布页**，v1.0 的"据官方产品页能力清单与行业节奏推断为 2023-2024 年"属无来源推断，v1.1 保留但显式加 `【待核验】` 标记。
3. **推出背景**：Splunk 的技术优势建立在 **SPL（Search Processing Language）** 之上，但 SPL 学习曲线陡峭，形成"数据都在里面、能取出来的人很少"的能力瓶颈；同时 Observability Cloud 已覆盖 APM、基础设施、RUM、合成监控、日志、数据库、数字体验分析、运行时应用安全、**AI SRE** 与 **Agent Observability** 等十余条能力线，界面复杂度与数据量同步上升。2023 年 LLM 能力成熟后，"把 SPL 与多产品操作自然语言化"成为降低使用门槛的直接路径。
4. **解决的问题**：
   - SPL 门槛高，非专家无法自助取数与排障
   - 多能力线（APM/Infra/RUM/Log/Security）之间的操作路径长
   - 复杂查询的构造与语法错误消耗排障时间
   - AI SRE / Agentic 能力缺少统一交互入口
   - 把"AI 应用自身"（Agent）纳入观测范围（Agent Observability）
5. **技术原理**：其技术路线与 New Relic AI（2.3.3）、Datadog Bits AI（2.1.3）同构，属**"平台查询层 + 生成式 AI 对话层"**范式：① **自然语言 → SPL 转换**——把用户意图翻译为 Splunk 查询，复用既有索引与搜索能力（相比让模型直接回答，该路径可审计、可复现、不易幻觉）；② **多产品能力编排**——AI Assistant 作为统一入口调用 Observability Cloud 各能力线，减少界面跳转；③ **AI SRE**——官方产品页把 "AI SRE" 单列为一项能力，指向自动化调查/建议的独立产品面；④ **Agent Observability**——官方产品页同时列出 "Agent Observability"，即把 AI Agent 的运行纳入被观测范围（与 New Relic AI Monitoring、IBM Instana GenAI Observability 同方向）；⑤ 与 ITSI 事件智能（2.4.1）结合，可把自然语言提问落到具体服务健康度与 Episode 上。**推断边界**：官方产品页仅为能力清单（列出 "AI Assistant"、"AI SRE"、"Agent Observability" 三个条目），**未公开**任何实现细节（模型、RAG、SPL 生成校验、权限与数据边界）、发布时间与量化效果。本条目**推断比例较高**，第1轮修订需补齐官方文档 `help.splunk.com/en/splunk-observability-cloud` 中 AI Assistant 的原文描述。
6. **技术效果**：**官方未给出量化数据**（产品页仅列能力名）。
7. **落地情况**：已商用（Splunk Observability Cloud 在售产品页中的能力项）。规模数据未取证。
8. **案例**：**未能取得 Splunk AI Assistant / AI SRE 专属的具名客户案例**（Splunk 官方案例库中的 5 个具名量化案例均属安全与 ITSI/可观测范畴，未涉及 AI Assistant 本身，且无发布日期）。按 §6.1 规则不重复计入 §2.4.1 → 字段 8 **计为不齐**。
9. **来源**：
   - 官方来源（必须）：
     - [Splunk Observability Cloud（产品页，能力清单含 AI Assistant / AI SRE / Agent Observability）](https://www.splunk.com/en_us/products/observability-cloud.html) — 日期：官方未标注（2026-09-12 确认）— 产品页
     - [Splunk Observability Cloud 官方文档入口](https://help.splunk.com/en/splunk-observability-cloud) — 日期：官方未标注（链接由产品页给出，2026-09-12 确认）— 官方文档
     - [Splunk 官方案例库（Customer Stories）](https://www.splunk.com/en_us/customers.html) — 日期：官方未标注（2026-09-12 确认）— 官方案例库
     - [Splunk 官方新闻室新闻稿列表](https://www.splunk.com/en_us/newsroom/press-releases.html) — 列表自 2020 年起（2026-09-12 确认）— 官方新闻稿列表
   - 非官方来源（可选，仅用于原理补充）：
     - 无

---

### 2.5 Elastic（Elastic Observability）

#### 2.5.0 厂商近10年战略与技术主线（≤500字）

Elastic 的技术主线是**"用自己的搜索与分析内核做可观测"**——这条路线的独特性在于：Elasticsearch 本身就是为"海量非结构化数据的检索与聚合"而生，因此它在可观测领域天然强于**日志与分析**、弱于**时序高基数指标**，这决定了其后十年的技术投入方向。2015-2018 年 ELK（Elasticsearch/Logstash/Kibana）是事实上的日志分析标准；2019 年前后 Elastic 正式推出 **Observability** 解决方案，把 APM（含分布式追踪）、Metrics、Uptime、Logs 纳入统一产品线，并提出"schema on read"与统一字段模型。2021-2023 年重点补短板：APM Agent 生态与 OpenTelemetry 集成（官方推荐用 Elastic OTel 采集应用遥测）、持续剖析（Profiling）与指标存储效率。2023-2024 年推出 **AI Assistant**（生成式 AI，做自然语言查询、错误解释、威胁调查），并把 **ES|QL** 作为新一代管道查询语言——这是其"查询语言统一"的关键动作，与 New Relic NRQL、Splunk SPL 形成三方对标。2025-2026 年主打**列式指标引擎**（官方博客宣称 Prometheus 场景快 30 倍）、**Streams**（日志到指标的自动结构化）与 **Agentic 调查**（AI Agent 主导调查、给出根因并自动化修复流程）。

对用户的意义：Elastic 是**"数据平台厂商跨界做可观测"**的样本，其"日志为中心 + 查询语言统一 + 用 AI 降低取数门槛"的路径，与用户 Server 端 AI 助手的"自然语言取数"需求高度契合；其**ES|QL 与 Streams 的"采集即结构化"思路**，对交换机侧做边缘预处理（把原始流数据先结构化再上送）有直接参考价值。

#### 2.5.1 Elastic - Elastic APM 与 OpenTelemetry 优先接入

1. **技术类别**：传统技术（分布式追踪 APM）
2. **首次发布/关键版本时间**：官方文档未标注首次发布日期；Elastic APM 于 **2019 年前后**随 Elastic Observability 解决方案成形（Elastic 7.x 周期），现行版本为 Elastic Stack 9.x（官方博客 2026-09-03 发布 Elastic Stack 9.5.3）。标注"官方未明确精确首发月份，据官方文档现行状态（GA）与 Elastic Stack 版本线推断"。
3. **推出背景**：2019 年前后微服务与容器让"一次用户请求横跨十几个服务"成为常态，日志分析的"事后 grep"模式无法回答"这 800ms 花在哪个服务/哪条 DB 语句"。同时 APM 市场被专有厂商（AppDynamics、New Relic、Dynatrace）把持，其 Agent 与数据格式封闭，企业希望有一个**基于开源栈、数据自己掌握**的追踪方案。Elastic 的切入点是"追踪数据就存在你自己的 Elasticsearch 里"。
4. **解决的问题**：
   - 微服务调用链不可见，响应时间无法归因到具体服务/查询/外部调用
   - 未处理错误与异常缺少自动聚合，新错误无法被识别
   - 追踪数据与日志、指标割裂，排障需跨系统
   - 专有 APM Agent 造成厂商锁定
   - 缺少与服务端主机/JVM/运行时指标的关联
5. **技术原理**：Elastic APM 的架构是**"各语言 Agent + APM Server + Elasticsearch 存储 + Kibana Applications UI"**四层：① **Agent 层**——官方定义为"automatically collects unhandled errors and exceptions"以及收集**响应时间、数据库查询、缓存调用、外部 HTTP 请求**等详细性能信息，用于快速定位并修复性能问题；同时 Agent 自动采集**主机级指标与 Agent 特定指标**（如 Java Agent 的 JVM 指标、Go Agent 的 Go runtime 指标），实现追踪与运行时指标的天然关联。② **APM Server 层**——接收 Agent 数据并写入 Elasticsearch（官方文档提供 `Set up APM Server` 自托管路径）。③ **错误分组**——官方明确错误"primarily based on the stack trace"进行分组，目的是识别**新出现的错误**并跟踪特定错误的出现次数——这是"从噪声中识别新问题"的关键机制。④ **存储与查询层**——因为落地在 Elasticsearch，追踪数据可直接与日志、指标在同一查询语义下关联（Elastic 强调 "Elastic APM is an application performance monitoring system **built on the Elastic Stack**"）。⑤ **OpenTelemetry 优先**——官方在 APM 文档中明确建议"**We recommend using Elastic OpenTelemetry to collect application telemetry data**"，即 OTel 已成为其首选接入方式（Agent 路线与 OTel 路线并存，见 2.10.1/2.10.2）。**推断边界**：官方文档片段未公开 APM Server 的吞吐模型、采样策略（头部/尾部采样）、是否使用 tail-based sampling 与 span 存储结构；本稿不作断言。
6. **技术效果**：官方文档定性表述为"monitor software services and applications in real time"、"easy to pinpoint and fix performance problems quickly"，并明确列出可采集的信号类型（response time for incoming requests, database queries, cache calls, external HTTP requests）。**官方未在该文档给出量化效果**（如追踪开销百分比、MTTR 改善）。
7. **落地情况**：已商用（Elastic Cloud Serverless 与 Elastic Stack 双形态均标注 **Generally available**，见官方文档 front-matter）。规模数据：Elastic 官网 Observability 页面称其被"**50% 的财富 500 强**"使用（厂商自述）。
8. **案例**（**v1.1 新增，五要素齐备**）：`客户 | 行业 | 场景 | 结果 | 时间 | 官方来源URL`
   - **SWIFT | 金融基础设施（全球支付报文网络）| 全球支付快速演进下的可观测现代化：用 Elastic 解决可观测性挑战、缩短延迟，支撑面向未来的 AI 驱动金融服务 | 克服可观测性挑战并减少延迟（官方概述为定性表述，未给量化数字）| **2025-05-05** | https://www.elastic.co/blog/category/customers **（Elastic 官方博客 "Customers" 分类页，HTTP 200 实抓；该页逐条列出标题、日期与摘要原文）**
   - **⚠️ 未编造 URL 的说明**：该案例的独立详情页 URL 本轮**未能确证**——按标题推测的 slug（`/blog/how-burgan-bank-turkiye-...` 等同级形态）实测返回 **Next.js 404**，故本稿**只登记已验证可达的分类页 URL**，不写入任何未验证的详情页链接（遵守 00 规范"禁止编造 URL"）。
9. **来源**：
   - 官方来源（必须）：
     - [Application performance monitoring (APM)（官方文档）](https://www.elastic.co/docs/solutions/observability/apm) — 日期：官方未标注（2026-09-12 确认；front-matter 标注 GA）— 官方文档
     - [Elastic Observability platform（产品页）](https://www.elastic.co/observability) — 日期：官方未标注（2026-09-12 确认）— 产品页
     - [Elastic 官方博客 Customers 分类页（含带日期的具名客户案例：SWIFT 2025-05-05、KPMG 2025-11-07、Burgan Bank Türkiye 2025-08-28 等）](https://www.elastic.co/blog/category/customers) — 抓取于 2026-09-12（页面逐条标注发布日期）— 官方博客
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.5.2 Elastic - AI Assistant（Kibana 内的生成式 AI 助手）——AI技术

1. **技术类别**：AI技术（AI增强：生成式 AI 助手 / 自然语言查询与运维）
2. **首次发布/关键版本时间**：官方文档未标注发布日期；据 Elastic 产品线公开演进，**2023-2024 年**推出（Elastic 8.x 后期至 9.x）。标注"官方未明确，据官方文档现行状态（GA）推断为 2023-2024 年"。
3. **推出背景**：与同业一致的痛点，但 Elastic 多了一层独特难度：**其可观测产品的取数语言从 KQL/Lucene 演进到 ES|QL**，用户需要跨越两代查询语义；同时 Kibana 承载 Elasticsearch、Observability、Security 三条解决方案，操作面极广。企业最痛的不是"没有数据"，而是"数据在 Elasticsearch 里，但只有少数专家能把答案查出来"。此外，Elastic 的部署形态包含**气隙（air-gapped）环境**，对 AI 助手的知识库分发方式提出特殊要求。
4. **解决的问题**：
   - 查询语言门槛：需要把自然语言与其他语言的查询转换为 ES|QL
   - 数据接入门槛：不知道如何把数据索引进 Elasticsearch
   - API 操作门槛：需要助手代为调用 Elasticsearch API 执行具体操作
   - 排障门槛：需要解释错误与消息并给出修复建议
   - 安全调查门槛：需要辅助分析潜在攻击、提供威胁研究、协助告警分流
   - 测试数据构造成本（需生成样例数据）
   - 气隙环境下的 AI 知识库可用性
5. **技术原理**：Elastic 官方文档对 AI Assistant 的定位是**"chat-based interactive tool"**，并给出了明确的**能力清单**（这是本稿中证据最扎实的 AI 助手描述之一，因为它来自官方文档正文而非产品页营销文案）：① **构造查询**——协助构建查询，**包括把其他语言的查询转换为 ES|QL**；② **索引数据**——指导如何把数据索引进 Elasticsearch；③ **调用 API**——在需要执行特定操作时**代用户调用 Elasticsearch API**（即具备工具调用/函数调用能力，而非纯对话）；④ **生成样例数据**——为测试与开发创建样例数据；⑤ **可视化与分析**——协助在 Kibana 中创建可视化并分析数据；⑥ **排障**——解释错误与消息并建议修复方案；⑦ **威胁调查**——分析潜在攻击、提供威胁研究、协助告警分流。**接入与前置条件**：官方明确 AI Assistant **要求特定权限与一个 LLM connector**（即模型可插拔，而非绑定单一供应商），且**不同解决方案（Observability/Security/Search）中的能力与交互方式不同**。**知识库分发**：官方文档专门给出气隙场景的处理方式——若 Kibana 无法访问 Elastic 的公共制品 URL（air-gapped 部署常见），需把知识库制品镜像到 Kibana 可达的基础设施（`Host a knowledge base artifact repo for AI Assistant`）。**推断边界**：官方文档**未公开**具体 LLM 选择、是否使用 RAG、ES|QL 生成的校验/回滚机制、API 调用的权限收敛模型；本稿不作断言。**强相关提示**：Elastic 官方文档中"明确列出 7 项能力 + 明确要求 LLM connector + 明确规定权限 + 专门处理气隙知识库"这一完整度，是用户在开发交换机内嵌/Server 端 AI 助手时**最可直接借鉴的产品规格模板**。
6. **技术效果**：**官方文档未给出量化数据**（无准确率、耗时或成本指标）。可验证的事实是能力范围与前置条件（LLM connector、权限、知识库制品镜像）。
7. **落地情况**：已商用（官方文档 front-matter 标注：Elastic Cloud Serverless **Generally available**；Elastic Stack **Generally available**；覆盖 Elastic Observability、Elastic Security、Kibana）。
8. **案例**（**v1.1 新增，五要素齐备；本条为全稿与用户"本地部署 AI 助手"场景最贴合的案例**）：`客户 | 行业 | 场景 | 结果 | 时间 | 官方来源URL`
   - **Burgan Bank Türkiye | 银行 | 以 Elastic 现代化其 IT：从 OpenShift 迁移到裸金属，使用 ML 与**本地部署（on-prem）的 AI 助手**，并把可观测与安全统一到同一平台 | 事件响应速度**提升 90%**；实现全系统统一可观测与安全 | **2025-08-28** | https://www.elastic.co/blog/category/customers **（Elastic 官方博客 Customers 分类页；标题与摘要逐字命中："How Burgan Bank Türkiye transformed observability and security with Elastic… used ML and an on-prem AI assistant to achieve 90% faster incident response"）**
   - **相关性提示**：该案例证明"**AI 助手在客户本地/私有环境内部署**"已是官方可公开引用的商业实践，直接支撑 §5 P2-1 中"气隙/内网环境下 AI 助手交付边界"的建议。
9. **来源**：
   - 官方来源（必须）：
     - [AI assistants in Kibana（官方文档）](https://www.elastic.co/docs/explore-analyze/ai-features/ai-chat-experiences/ai-assistant) — 日期：官方未标注（2026-09-12 确认；front-matter 标注 GA）— 官方文档
     - [Elastic AI Assistant for Observability and Search（官方文档，由上文引用）](https://www.elastic.co/docs/solutions/observability/ai/observability-ai-assistant) — 日期：官方未标注（链接由官方文档正文给出）— 官方文档
     - [Elastic Observability platform（产品页，含 LLM observability / Agentic investigations 能力项）](https://www.elastic.co/observability) — 日期：官方未标注（2026-09-12 确认）— 产品页
     - [Elastic 官方博客 Customers 分类页（含 Burgan Bank Türkiye 本地部署 AI 助手案例，2025-08-28）](https://www.elastic.co/blog/category/customers) — 抓取于 2026-09-12 — 官方博客
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.5.3 Elastic - ES|QL 与列式指标引擎 / Streams（查询统一与指标效率）

1. **技术类别**：传统技术（查询语言与存储引擎）+ AI技术（AI增强：作为 AI 助手与 Agentic 调查的取数底座）
2. **首次发布/关键版本时间**：ES|QL 于 **2023 年**随 Elastic 8.11 技术预览、**2024 年** GA（据 Elastic 官方博客与版本节奏推断；本稿未取得 8.11 发布博客原文，标注"官方未明确，据官方文档与版本线推断"）。列式指标引擎相关官方博客日期为抓取自 RSS（见来源）。
3. **推出背景**：Elastic 做可观测最大的结构性弱点是**指标（尤其高基数时序指标）的存储与查询效率**不如专有时序数据库（Prometheus/VictoriaMetrics 等），导致在"Prometheus 替代"场景竞争乏力、成本偏高。同时 Elastic 的查询语言长期碎片化（Lucene、KQL、DSL、SQL 并存），用户需按场景切换。2023-2025 年 Elastic 的两个关键投入是：**ES|QL**（统一、管道式的现代查询语言，带查询优化器）与**列式指标存储引擎**（面向 time series 的列式布局与压缩），以及 **Streams**（把原始日志自动结构化为带语义的指标/实体）。
4. **解决的问题**：
   - 指标存储成本高、查询慢，无法对标 Prometheus 生态
   - 高基数场景（K8s 标签爆炸）下性能与成本双失
   - 查询语言碎片化，同一数据要学多套语法
   - 日志转指标需人工写 pipeline，接入即成本
   - 为 AI（自然语言取数、Agentic 调查）提供统一且高效的取数面
5. **技术原理**：① **ES|QL**——官方在 AI Assistant 文档中把 ES|QL 描述为"其他语言可转换为的目标查询语言"，说明其定位是**统一目标语言**：管道式语法（source → 一系列 processing command），带查询规划/优化，使同一语句可同时做搜索与聚合分析，从而成为"自然语言 → 单一目标语言"的理想落点（这是 AI 助手能稳定生成查询的前提）。② **列式指标引擎**——官方博客标题即给出量化主张："Prometheus, without the complexity — and **30x faster**" 与 "Elasticsearch columnar metrics engine 30x faster Prometheus"（Elastic Search Labs 官方博客），说明其技术路线是把时序指标改用**列式存储布局 + 面向指标的压缩与编码**，以换取扫描吞吐与存储效率，同时对外表现为"Prometheus-native"（兼容 Prometheus 数据模型与查询路径）。③ **Streams**——官方 Observability 页面把 "Live logs and prosper" 作为 manifesto，指向把**日志流自动转换为结构化、带语义的实体与指标**（即"采集即结构化"），从而降低日志到指标的转换成本，并让 AI 能在结构化语义上推理（官方表述："turns your logs, metrics, and traces into a live system model that AI can reason on in real time"）。**推断边界**：官方向来以博客宣称量化数字（30x），**未公开**基准测试方法（数据集规模、查询类型、硬件、对比版本）与列式引擎的内部编码方案；本稿**如实引用其"官方宣称 30x"并标注为厂商自述基准，不视为独立验证结果**。
6. **技术效果**：官方宣称"**Up to 30x faster queries than Prometheus and Grafana**"（Elastic 官网 Observability 页面，为厂商自述基准）。**注意：该数字来自厂商营销页面与官方博客标题，缺少可复现的基准测试说明，本稿按"厂商自述"记录，不作为已验证事实。**
7. **落地情况**：已商用（ES|QL 为 Kibana/Elasticsearch 正式查询语言；列式指标引擎随 Elasticsearch 9.x 发布，官方博客提及 Elasticsearch 9.4 为 "Fastest"；Streams 为 Observability 方向的新能力）。
8. **案例**：**未能取得 ES|QL / 列式指标引擎 / Streams 专属的具名客户案例**。Elastic 官方博客 Customers 分类页中带日期的具名案例（SWIFT / KPMG / Burgan Bank Türkiye 等）分别归属可观测与安全场景，非本条目的查询语言与存储引擎；`elastic.co/customers` 列表页含 Tinder（CPU 用量降低 4 倍、scoring 延迟降低 47%、过滤性能提升 60%）、Banco Bradesco、Smart DCC（事件检出时间降低 84%）、Siemens（每年回收约 5,000 分析师小时）等具名量化案例，但**列表页未标注发布日期**，故仅登记于 §6.5 表 B。→ 本条目字段 8 **计为不齐**。
9. **来源**：
   - 官方来源（必须）：
     - [AI assistants in Kibana（官方文档，ES|QL 作为转换目标语言的说明）](https://www.elastic.co/docs/explore-analyze/ai-features/ai-chat-experiences/ai-assistant) — 日期：官方未标注（2026-09-12 确认）— 官方文档
     - [Elastic Observability platform（产品页，含 30x 宣称与 Streams manifesto 链接）](https://www.elastic.co/observability) — 日期：官方未标注（2026-09-12 确认）— 产品页
     - [Elastic 官方博客 Customers 分类页（本轮新增，含带日期的具名客户案例）](https://www.elastic.co/blog/category/customers) — 抓取于 2026-09-12（页面逐条标注发布日期）— 官方博客
     - [Elastic 官方博客 RSS（用于确认官方博客 URL 与发布日期）](https://www.elastic.co/blog/feed) — 抓取于 2026-09-12 — 官方博客 RSS
     - [Elastic Observability: A solution for today's "always-on" world](https://www.elastic.co/blog/observability-powerful-flexible-efficient) — 发布 2023-03-27（据官方 RSS）— 官方博客
   - 非官方来源（可选，仅用于原理补充）：
     - 无

---

### 2.6 Broadcom（CA Technologies / DX APM）— ⛔ **证据不足的对照性附录（本轮降级）**

> # ⛔ 章首显著声明（Leader 裁决 A「方案A + 硬性截止线」第 2 分支，B-R1-03 闭环）
>
> **本章未取得任何 S/A 级官方来源，仅作为传统私有化 APM 对照组的定性说明，不作为事实依据。**
>
> **本轮（v1.1）最后的取证尝试与实际结果（全部实测，2026-09-12）**：
>
> | # | 尝试的官方路径 | 实测结果 |
> |---|---|---|
> | 1 | `https://investors.broadcom.com/`（Leader 指定的官方 IR） | **200（可达）**，返回 Investor Center 与新闻稿列表（09/02/26 财报、08/31/26 VMware Private AI Cloud 等）——**但其全部条目均与 DX APM 无关，无法支撑本章任何字段** |
> | 2 | `https://investors.broadcom.com/news-releases` | **404** |
> | 3 | `https://investors.broadcom.com/news-releases/all` | **404** |
> | 4 | `https://investors.broadcom.com/news-releases/news-release-details/broadcom-completes-acquisition-ca-technologies-inc` | **404**（即第 1 轮评审 AI 与 v1.0 实测的同一结果） |
> | 5 | `https://community.broadcom.com/`（Leader 指定的官方社区） | **200（可达）**，返回社区首页；但社区按 **VMware / Tanzu / Mainframe / Symantec / ANS** 等**当前**产品线组织，**DX APM 不在其中**（本轮实测的社区分区清单里无 APM/OI 条目） |
> | 6 | `https://docs.broadcom.com/` | **200**，但重定向至 `/support/download-search`（JS 外壳，无正文） |
> | 7 | `https://knowledge.broadcom.com/` | **200**，重定向至 `support.broadcom.com` 维护公告页（无产品正文） |
> | 8 | `https://www.broadcom.com/products/software/aiops`（→ `/products/software/aiops-observability`） | **JS 外壳**：正文只有 `window.location.href = '/browser-not-supported'` 与本地化字符串表，无 DX APM/AIOps 正文 |
> | 9 | `https://techdocs.broadcom.com/us/en/ca-enterprise-software/it-operations-management/dx-apm/26-0.html` | **404**（v1.0 已实测 `26-1.html` 亦为 404） |
>
> **结论（决断，不再悬挂）**：Broadcom 的**官方域可达**（IR、社区、support 门户确为真官方站点），但**没有任何一个可达的官方页面记载 DX APM / DX OI 的产品事实、发布时间、架构或客户案例**。因此本章**不满足**"每个条目的发布时间/背景/案例必须有 ≥1 个 S/A 级链接"与"条目含 S/A 级官方来源 100%"两条硬性要求，**按 Leader 裁决的自动画触发条件执行降级**：
> 1. **2.6.1 / 2.6.2 / 2.6.3 三条不计入有效技术条目数（34 条）与覆盖率分母**，其标题一律加 `【降级·对照性附录】` 前缀；
> 2. **§4 对比表与 §5 建议中一切依赖 Broadcom 的论断已逐处改写为"因证据不足不予采信"，或改由其它有证据的厂商支撑**（详见 §4 与 §5.1 的加注）；
> 3. **字段 8 保持 `官方来源缺失` 声明**，且**禁止**用"存量客户多为金融/政府、披露保守"这类行业推断充当案例（v1.0 的该句已删除）；
> 4. **本文所有以确定语气出现的 Broadcom 时间点（2018-11 收购 CA、2019-2020 品牌迁移、26.x 版本线）已全部改为 `【待核验】`**。
>
> **未闭合的残余项（如实登记，供第 2 轮决策）**：若第 2 轮能在**渲染型环境**（非纯 HTTP 抓取）下打开 `techdocs.broadcom.com` 的 DX APM 文档树或 `community.broadcom.com` 的历史 APM 分区，本章可**恢复为正常技术条目**；本稿不预设该结论。

#### 2.6.0 厂商近10年战略与技术主线（≤500字）【降级·对照性附录】

> **本节全部内容为 C 级推断，不作为事实依据。** 保留本节仅用于说明"**为什么传统私有化 APM 路线值得作为对照样本**"这一**分析性问题**，而非陈述已证实事实。

Broadcom 在 APM 领域的存在方式与其他九家**本质不同：它不是"可观测厂商"，而是"企业软件资产运营方"**（**推断**）。据公开报道，2018-11 Broadcom 完成对 CA Technologies 的收购【待核验】，原 CA 的 APM 产品线（CA APM）被纳入 Broadcom 企业软件部门并更名为 **DX APM**（Digital Experience APM）【待核验】，配套 **DX Operational Intelligence（DX OI）** 做跨域关联分析与 **DX Dashboards** 做可视化【待核验】。其技术主线被推断为**"延续 + 私有化"**而非"追赶云原生"：目标客户是金融、保险、政府、大型机（mainframe）等**强合规、强本地部署、生命周期极长**的存量用户群；产品迭代以版本号推进（v1.0 曾称"取证到 26.x 文档线"，**该路径本轮与上轮实测均为 404，故该陈述撤回**）。在 AI 方向，**本稿无法就 DX OI 的 AI 能力作出任何有来源支撑的判断**。

对用户的意义（**仅为分析性假设，非结论**）：若上述推断成立，Broadcom 会是本次调研中**最接近"用户既有形态"的对照组**——同为"采集 Agent（本地部署、C/C++/Java 生态）+ Server 端分析"的传统架构，同样面向私有化交付。其**假设性**可迁移价值有两点：① **存量私有化 APM 的技术债务模式**（Agent 侵入性注入、UI 重、扩展难、云原生适配滞后）值得作为用户在交换机内嵌采集时主动规避的设计参照；② **DX OI 的"跨域关联 + 基线"思路**可作为"没有大模型时代如何做 AIOps"的参照。**⚠️ 上述两点均建立在"Broadcom 确实如此"的推断之上；本稿已按 Leader 裁决将其排除出 §4/§5 的论据集合。**


#### 2.6.1 【降级·对照性附录】Broadcom - DX APM（CA APM 延续的私有化应用性能管理）

1. **技术类别**：传统技术（Agent 注入式 APM + 本地部署）
2. **首次发布/关键版本时间**：官方来源缺失：本环境未能取得 Broadcom 官方页面佐证。据 Broadcom 完成收购 CA Technologies 的 **2018-11** 时点与产品线更名事实，DX APM 品牌形成于 2018-2019 年；**收购日期本身亦未能取得 Broadcom 官方新闻稿/财报原件（见字段9）**，故本字段标注"官方未明确（本环境无 S/A 级来源）"。
3. **推出背景**：**官方来源缺失：未能取得官方背景陈述。** 以下为基于行业公开事实的推断（属 C 级推断，仅供上下文，不构成条目事实）：2018 年前后企业 APM 市场发生结构性分化——云原生新贵（Datadog/Dynatrace/New Relic）以 SaaS 与自动化为卖点快速上量，而传统大型企业（尤其金融、保险、政府、制造）的核心交易系统仍运行在私有数据中心与大型机上，**无法接受把生产遥测送出企业边界**。这类客户需要的不是"最好的 APM"，而是"能过合规、能长期维护、能覆盖大型机的 APM"。Broadcom 收购 CA 后选择继续服务这批存量客户，而非投入云原生红海。
4. **解决的问题**（**推断，非官方来源**）：
   - 私有化/合规环境下应用性能监控无法上公有云
   - 大型机与分布式混合架构的统一监控
   - 存量 APM 投资保护与长期维护承诺
   - 跨域（应用/基础设施/网络）事件关联
   - 企业级权限、审计与本地化部署要求
5. **技术原理**（**推断，非官方来源，明确标注边界**）：传统 CA APM 体系的技术路线可概括为：① **Agent 注入**——通过 Java/.NET/PHP 等语言的 Agent（Java 侧以 JVM 字节码增强为主）采集方法级调用栈与事务数据，采集粒度深但侵入性较高；② **Collector/Enterprise Manager 分层**——Agent 把数据上报到企业内部的 Collector 与管理器（本地部署），再由管理器做聚合、事务追踪与告警；③ **事务追踪（Transaction Tracing）**——以业务事务为线索串起调用链，按响应时间分解定位"慢在哪个组件"；④ **与基础设施/大型机集成**——通过独立监控模块采集主机、数据库、中间件与大型机侧指标；⑤ **DX OI 关联层**——把 APM 与基础设施、网络数据统一到一个分析层做异常检测与关联。**推断边界声明**：上述五点在本次执行中**没有任何一条取得 Broadcom 官方文档原文佐证**，属于 APM 领域通用架构 + 产品公开定位的推断，**证据等级为 C**。评审时应视为待验证内容，而不可当作已证实事实引用。
6. **技术效果**：官方来源缺失：未能取得官方量化或其他效果陈述。
7. **落地情况**：**有限商用/存量维护**（据产品线存续事实推断：DX APM 仍在 Broadcom 产品清单中，主要服务存量客户与本地化交付场景）。**无官方规模数据。**
8. **案例**：`官方来源缺失`。Broadcom 官方案例库在本环境完全不可访问（`broadcom.com` 相关路径为 JS 外壳或 404），无法核验客户名+场景+结果+时间四要素。**本轮按 Leader 裁决 A 与第 1 轮评审意见，删除了 v1.0 中"因其存量客户多为金融/政府类且官方披露习惯保守"这一理由句——该句属行业推断，不得用作案例缺失的解释或替代**。本条目**无案例、且不参与覆盖率分母**。
9. **来源**：
   - 官方来源（必须）：**官方来源缺失**。原因说明：① `https://techdocs.broadcom.com/us/en/ca-enterprise-software/it-operations-management/dx-apm/26-1.html` 返回 404（已实测，2026-09-12）；② `https://www.broadcom.com/products/software/aiops/dx-apm` 返回 404（已实测，2026-09-12，页面内嵌 `window.location.href = '/browser-not-supported'` 与 404 标记）；③ `web_search_pro(engines=ddg,bing)` 对 Broadcom DX APM 相关查询无有效召回。可访问的**官方文档站根域**为 [techdocs.broadcom.com](https://techdocs.broadcom.com/)（域名可达，但本稿未能定位到 DX APM 的有效路径，**因此不将其列为条目的支撑来源，以免虚构路径**）。
   - 非官方来源（可选，仅用于原理补充）：
     - 无
   - **缺口登记**：本条目 9 字段中，字段 2/3/6/7/8 均无 S/A 级来源，**9 字段完整率实质不达标**，已在第6章登记。

#### 2.6.2 【降级·对照性附录】Broadcom - DX Operational Intelligence（DX OI）与 AIOps 关联分析

1. **技术类别**：AI技术（AI增强：AIOps 关联与基线分析）
2. **首次发布/关键版本时间**：官方来源缺失：未能取得 Broadcom 官方页面或新闻稿佐证。据 CA 产品线历史，CA OI（Operational Intelligence）在 2016-2017 年是 CA 的 AIOps 主打产品，Broadcom 收购后更名为 DX OI，**推断品牌化于 2018-2019 年**（C 级推断）。
3. **推出背景**：**官方来源缺失，以下为推断（C 级）**：2016-2018 年是 AIOps 概念的第一波高峰，行业痛点是"监控工具数量增长快于人力增长"——每个域（应用、主机、网络、数据库、存储）都有独立工具与独立告警流，运维团队被跨域关联工作压垮。CA 等传统厂商的应对是把各域数据汇聚到一个"运营智能"层，做统一关联与告警压缩。
4. **解决的问题**（**推断**）：
   - 跨域告警风暴与关联缺失
   - 缺少统一的服务/业务视图
   - 静态阈值在动态环境中误报高，需要基线学习
   - 需要把技术事件映射到业务影响
   - 大型企业内部多团队/多域数据的权限隔离与汇聚
5. **技术原理**（**推断，非官方来源**）：DX OI 的典型技术路径为：**多源数据汇聚（APM/基础设施/网络/日志/事件）→ 统一实体与拓扑模型 → 基线学习与异常检测 → 跨域事件关联与去重 → 服务/业务视图呈现**。其中"关联"依赖拓扑与时间邻近性，"基线"依赖历史统计模型（非生成式 AI）。**推断边界声明**：本条目**未取得任何 Broadcom 官方原文**，全部机制描述为 AIOps 通用范式推断，**证据等级 C**，不可作为已证实事实。
6. **技术效果**：官方来源缺失。
7. **落地情况**：官方来源缺失（据产品线存续推断为有限商用/存量维护）。
8. **案例**：官方来源缺失。
9. **来源**：
   - 官方来源（必须）：**官方来源缺失**。原因：同 2.6.1，Broadcom 官方站点与文档站在本环境下 DX/AIOps 相关路径均不可达或返回 404，且搜索引擎无有效召回。
   - 非官方来源（可选，仅用于原理补充）：
     - 无
   - **缺口登记**：本条目的证据完整度低于 2.6.1，**建议第1轮评审后由正常环境执行者补证或降级处理**。

#### 2.6.3 【降级·对照性附录】Broadcom 章节结构性缺口登记（非技术条目；本轮已按 Leader 裁决完成降级决断）

1. **技术类别**：不适用（缺口登记）
2. **时间**：不适用
3. **背景**：Broadcom 在本次调研的厂商清单中被列入，但在本执行环境下**无法取得任何 S/A 级官方来源**，导致其技术条目无法满足 00 号规范"每个条目的发布时间/背景/案例必须有 ≥1 个 S/A 级链接"的硬性要求。
4. **缺口清单**：
   - 收购日期类：Broadcom 收购 CA Technologies（2018-11）、Broadcom 收购 VMware（2023-11，影响产品线重组）——均无官方新闻稿原件
   - 产品事实类：DX APM 版本线、DX OI 功能清单、DX APM 的 AI 能力命名与边界——均无官方文档
   - 案例类：无任何具名客户案例（客户名+场景+结果+时间）
   - 量化类：无任何官方量化效果数据
5. **建议处置（供 Leader 决策，三选一）**：
   - 方案A（推荐）：第1轮修订时，由检索环境正常的执行者补齐 Broadcom 官方来源（建议路径：Broadcom 投资者关系新闻稿页、Broadcom 官方 PDF 白皮书、`techdocs.broadcom.com` 搜索入口），使 2.6.x 满足 9 字段要求；
   - 方案B：经 Leader 批准，将 Broadcom 的技术条目数量由"≥3 条"下调为"≥1 条有效条目 + 1 条缺口登记"，并在最终报告的数据质量自评中显式说明；
   - 方案C：若 00 号规范不允许降级，则把 Broadcom 从 Top 10 中替换（**不推荐**：会破坏 Leader 锁定的厂商清单，且 Broadcom 作为"传统私有化 APM 对照组"对用户场景有独立价值）。
6. **技术效果**：不适用
7. **落地情况**：不适用
8. **案例**：官方来源缺失（见字段4）
9. **来源**：
   - 官方来源（必须）：**官方来源缺失**（原因见 2.6.1 字段9）
   - 非官方来源（可选，仅用于原理补充）：
     - 无

---

### 2.7 IBM（Instana）

#### 2.7.0 厂商近10年战略与技术主线（≤500字）

Instana 的技术主线可概括为**"自动发现 + 秒级变化感知"**，这是它在被 IBM 收购前就从红海中切出差异化的关键，也是对用户 Server 端 AI 助手最有借鉴价值的**"实时性"范式**。Instana 成立于 2015 年前后，其核心主张是：在高度动态的容器/K8s 环境中，**"变化"本身就是最重要的信号**——服务每一次部署、扩缩容、配置变更都可能在秒级内改变系统行为，传统 APM 的"分钟级采样 + 周期聚合"会错过关键窗口。为此 Instana 构建了三条技术线：① **自动发现与自动插桩**——官方表述为"automatically discovers and instruments applications and infrastructure"，无需人工配置；② **Dynamic Graph**——一个持续更新、反映当前系统实时依赖与拓扑变化的动态图，官方强调交付"real-time, full-stack visibility"；③ **AutoTrace**——面向 JVM 等运行时的按需深度追踪能力，可在不重启进程的前提下提升追踪粒度。**2020-11 IBM 宣布收购 Instana**，将其作为 IBM 可观测战略的核心（与 IBM Concert、Turbonomic 等协同）。2025 年起 IBM 把方向对准 AI 自身：**2025-10 在 IBM TechXchange 宣布 IBM Instana GenAI Observability 正式 GA**（此前为 preview 的 Intelligent Incident Investigation 使用 Agentic AI 做根因识别）；**2026-05 在 IBM Think 2026 进一步宣布 AI Agent and LLM Observability**，把观测对象从"模型调用"扩展到"多 Agent 工作流"。

对用户的意义：① **Dynamic Graph 的"秒级变化感知"**是交换机场景可迁移性最高的思路之一——交换机的端口/链路状态本身就是高频变化信号；② **Instana 把"自动发现"作为第一性能力**（而非事后补齐），与交换机内嵌 Agent"无人工配置即可用"的诉求一致；③ IBM 从 GenAI Observability（2025-10）到 AI Agent & LLM Observability（2026-05）的**半年内快速迭代节奏**，展示了"Server 端 AI 助手"产品的演进路径。

#### 2.7.1 IBM Instana - 自动发现与 Dynamic Graph（实时依赖图）

1. **技术类别**：传统技术（自动发现 + 实时动态拓扑）
2. **首次发布/关键版本时间**：`官方未明确【待核验】`。Instana 产品成立于 2015 年前后（调研窗口内）属**无 S/A 级来源的公开背景**，v1.1 显式加 `【待核验】` 标记；其自动发现与 Dynamic Graph 为其自创立以来的核心能力（官方产品页以现行时态陈述，未给出版本历史）。本稿取证的 IBM 产品页为现行版本。
3. **推出背景**：2015-2020 年容器编排（K8s）普及后，应用拓扑的**变更频率**超过人工维护能力：一个微服务每小时可能扩缩容数次，Pod 名与 IP 持续变化，服务依赖关系随版本发布动态调整。传统 APM 的模型是"先配置、再监控、定期更新拓扑"，在动态环境下表现为"拓扑永远是过期的"。Instana 的立论是：可观测性的第一性问题不是"采集更多数据"，而是**"能否实时知道系统当前长什么样、以及刚刚变了什么"**。
4. **解决的问题**：
   - 动态环境人工配置不可行，监控覆盖率与拓扑准确率随时间衰减
   - 缺少"实时"拓扑，故障时看到的是历史快照
   - 变更（部署/扩缩容/配置）与技术异常之间缺少自动关联
   - 全栈（应用+基础设施）可见性需多工具拼装
   - DevOps/工程团队缺乏易用界面（官方强调 "simplicity at its core" 与 "easy-to-use UI"）
5. **技术原理**：据 IBM 官方产品页表述，Instana 的技术特点是**"automated, AI-powered observability with simplicity at its core"**，并"automatically discovers and instruments applications and infrastructure, delivering **real-time**, full-stack visibility"。据此可归纳其四层机制：① **自动发现**——持续扫描并识别环境中出现的应用、服务、进程、主机、容器与依赖，无需人工登记（"automatically discovers... applications and infrastructure"）；② **自动插桩**——发现即插桩（"discovers **and instruments**"），把"配置"从用户责任转移给产品，这是其与"需人工安装各语言 Agent"路线最大的差异点；③ **Dynamic Graph（动态图）**——官方产品页把 "**Discovery mapping**" 列为独立功能（Features 中与 Unified observability、Incident investigation、Resource optimization、OpenTelemetry 并列），指向一个持续更新的依赖/资源映射模型，官方描述为提供"real-time, full-stack visibility"，即图随环境变化而更新（而非周期重建）；④ **实时性**——"real-time" 被官方反复强调，包括事件调查（Incident investigation）与 GenAI 观测均为实时。**推断边界**：官方产品页为价值陈述，**未公开** Dynamic Graph 的数据结构、更新频率与图规模上限；本稿不作断言。**⚠️ 本轮补正（响应第 1 轮评审 P2 发现）**：v1.0 曾称"官方术语中的'秒级'业界表述本稿未在官方页面取证到，故不使用该数字"，被评审AI 判定为**过度保守**——评审AI 实测 IBM 官方公告页 [IBM named a Leader in the 2026 Gartner® Magic Quadrant™ for Observability Platforms](https://www.ibm.com/new/announcements/ibm-named-a-leader-in-the-2026-gartner-magic-quadrant-for-observability-platforms) **含原文 "one-second metrics, unsampled distributed traces"**（本稿未重复抓取该页正文，此处按评审AI 第 1 轮抽检 #21 的结果登记，并标注该证据来源为评审AI 的实测而非本稿亲验）。因此"**秒级**"不应被表述为"无官方依据"：本稿现按 **"官方在 Gartner MQ 公告中以 'one-second metrics' 表述其指标采集粒度（证据来源：评审AI 第 1 轮抽检；页面 URL 见字段 9）"** 处理。**注意**：2.7.0 中"秒级变化感知"仍属本稿的概括性表述，其**官方锚点**为上述 "one-second metrics" 与产品页的 "real-time"。
6. **技术效果**：官方定性表述为"delivering real-time, full-stack visibility through an easy-to-use UI"、"Proactively solve issues across your application stack"。**官方产品页未给出量化数据**。
7. **落地情况**：已商用（IBM 在售产品，官网提供 Instana Sandbox 试用入口）。**荣誉/规模佐证**：IBM 官方产品页列明 Instana 获 **2026 G2 Best Software IT Infrastructure Product Award**、**2026 TrustRadius Buyer's Choice** 与 **2025 TopRated**；IBM 官网另发布 [IBM named a Leader in the 2026 Gartner® Magic Quadrant™ for Observability Platforms](https://www.ibm.com/new/announcements/ibm-named-a-leader-in-the-2026-gartner-magic-quadrant-for-observability-platforms)。
8. **案例**（**v1.1 新增：1 个 IBM 官方具名客户案例，但缺"时间"要素，故计入 §6.5 表 B 而非表 A**）：`客户 | 行业 | 场景 | 结果 | 时间 | 官方来源URL`
   - **State of Oregon OIS（Oregon Health Authority 的 Office of Information Services，美国州政府公共部门）| 公共部门 | 其支付应用 eXPRS（服务 30,000+ 残障人士）出现性能问题与中断、缺乏可见性导致解决时间过长；改用 IBM Instana 自动可观测，覆盖 Java EE + IBM Power + WebSphere Liberty + DB2 的既有平台，以自动发现与映射快速纳管新增组件 | 平均检测时间（MTTD）**降低 50%**、平均解决时间（MTTR）**降低 30%** | **官方 case study 页面未标注发布日期（2026-09-12 抓取确认）→ 时间要素缺失** | https://www.ibm.com/case-studies/state-of-oregon-ois
   - 说明：该案例的客户名、场景、量化结果、官方来源 URL 四要素齐备且来自 IBM 官方网站，**唯缺"时间"要素**，故本条目字段 8 仍**计为不齐**（不凑数）。另有 **SIXT**（"enables digital transformation with IBM Instana Observability"）同页可查，同样无发布日期。
9. **来源**：
   - 官方来源（必须）：
     - [IBM Instana Observability（官方产品页）](https://www.ibm.com/products/instana) — 日期：官方未标注（2026-09-12 确认）— 产品页
     - [State of Oregon OIS（IBM 官方案例研究，Instana；MTTD −50%、MTTR −30%）](https://www.ibm.com/case-studies/state-of-oregon-ois) — 日期：官方未标注（2026-09-12 确认）— 官方案例
     - [IBM 官方案例库（可按 `?q=Instana` 过滤，本轮 HTTP 直取成功）](https://www.ibm.com/case-studies?q=Instana) — 日期：官方未标注（2026-09-12 确认；返回 1,191 条案例，含 Instana 相关条目）— 官方案例库
     - [IBM named a Leader in the 2026 Gartner® Magic Quadrant™ for Observability Platforms](https://www.ibm.com/new/announcements/ibm-named-a-leader-in-the-2026-gartner-magic-quadrant-for-observability-platforms) — **页面发布时间 2026-07-15（据第 1 轮评审 AI 抽检 #21 实测的页面正文日期；本稿 v1.0 曾仅写"2026 年"，本轮按评审 P2 意见补精确日期）**【2026延伸·窗口外】— 官方新闻/公告
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.7.2 【未取证·C 级推断】IBM Instana - AutoTrace 与无重启按需深度追踪

> **⚠️ 条目级未取证标记（v1.1 新增，响应 B-R1-06）**：本条目**无任何 S/A 级官方来源**，字段 2/3/6/7/8/9 均不达标（9 字段完整度 3/9）。按第 1 轮评审要求，本条目**标题已加 `【未取证·C 级推断】` 前缀**，且**已从 §5 P0-2 与 §5.1 汇总表的"来源厂商/项目"列中移除**（见 §5 对应改写）。**本条目全部机制描述不可作为已证实事实引用。**

1. **技术类别**：传统技术（按需深度追踪 / 运行时诊断）
2. **首次发布/关键版本时间**：官方来源缺失：本环境未能取得 Instana AutoTrace 的官方文档或发布页。据 Instana 产品公开演进推断其在 2019-2021 年间推出（**C 级推断**）。
3. **推出背景**：**官方来源缺失，以下为推断（C 级，基于可观测性领域通用事实）**：常驻的分布式追踪为了控制开销，通常只做**采样**（sampling），且采集粒度固定。这导致两类场景失效：① 偶发、低概率但影响严重的慢请求，采样后恰好没被记录，无法复盘；② 出问题时需要看到**更细的调用栈与线程级细节**，但传统做法要求重启进程并调高追踪级别——在生产环境这是不可接受的（重启即中断业务，且问题现场消失）。行业需求是"**在故障已发生时，对已运行的生产进程临时提升追踪精度，且不重启、不影响业务**"。
4. **解决的问题**（**推断**）：
   - 采样丢失关键慢请求，事故无法复盘
   - 无法在不重启生产进程的前提下提升追踪粒度
   - 事后加日志/改配置需要发版，周期长
   - JVM 等运行时内部细节（线程、锁、GC）观测不足
   - 临时深度诊断工具与常驻监控数据不互通
5. **技术原理**（**推断，非官方来源，明确标注边界**）：AutoTrace 的公开定位是**按需（on-demand）为已有调用链附加更深层追踪**，技术要点推断为：① 常驻侧保留轻量采样追踪（低开销）；② 当需要深挖时，对目标进程以**运行时动态注入/挂载**的方式开启更高精度采集（例如 JVM 场景下利用运行时诊断接口），**不重启进程**；③ 深入采集的数据与常驻追踪数据通过 trace 上下文关联，形成"从服务级到方法/线程级"的连续视图；④ 完成诊断后自动回落至常驻低开销模式。**推断边界声明**：本条目**未取得任何 IBM/Instana 官方原文**，上述机制为基于"AutoTrace"命名与无重启诊断需求的推断，**证据等级 C**。**特别提示**：此推断与用户交换机 eBPF 采集场景的关系值得评审关注——eBPF 本身就是"无需重启、运行时增强观测"的技术路径，因此 AutoTrace 的可迁移本质是"**动态提升观测精度的策略设计**"，而非具体实现。
6. **技术效果**：官方来源缺失（无官方量化数据）。
7. **落地情况**：官方来源缺失（据产品线存续推断为已商用）。
8. **案例**：官方来源缺失。
9. **来源**：
   - 官方来源（必须）：**官方来源缺失**。原因：① v1.0 记录的 `https://www.ibm.com/products/instana/features` 返回与主页相同内容（无 AutoTrace 独立页）——**本轮复测确认该页面 200 且 Features 区仅列 Overview / Incident investigation / Resource optimization / Discovery mapping / OpenTelemetry 等条目，确无 AutoTrace 独立入口**；② 按第 1 轮评审建议本轮尝试 IBM 官方文档站：`https://www.ibm.com/docs/en/instana-observability` **HTTP 200**（返回 IBM Documentation 壳页），但按常见命名试探的专题路径 `.../instana-observability/1.0.0?topic=agents-autotrace` 返回 **IBM "The page you requested cannot be displayed" 错误页**；③ IBM Docs 的站内搜索为 JS 渲染，纯 HTTP 通道无法枚举文档树。故**不虚构路径**，本条目维持"官方来源缺失"。
   - 非官方来源（可选，仅用于原理补充）：
     - 无
   - **缺口登记**：字段 2/3/6/7/8/9 不达标，**计为不齐**；本条目**保留在有效技术条目数（34 条）内**，但**不得作为 §5 任何建议的落地依据**（已改写）。

#### 2.7.3 IBM Instana - GenAI Observability 与 AI Agent & LLM Observability（AI 应用可观测）——AI技术

1. **技术类别**：AI技术（AI增强 + AI原生：面向 GenAI/LLM/Agent 的可观测）
2. **首次发布/关键版本时间**：**2025-10-06**（官方公告《Drive operational efficiency with GenAI observability》发布日期 2025-10-06，页面 Updated 2026-03-23；宣布在 IBM TechXchange Orlando **正式 GA**）。后续版本：**2026-05-05**（官方公告《Advancing AI operations with AI Agent and LLM Observability》，在 IBM Think 2026 发布，页面标注 Published 05 May 2026）。**注**：2026-05 超出 00 号规范 2015-2025 窗口，仅作"延伸注记"记录，用于展示迭代节奏。
3. **推出背景**：2025 年企业在把 LLM 与 agentic workflow 推进生产时遇到**运维能力断层**。官方原文点明了三类痛点：**"debugging opaque AI pipelines, controlling unpredictable token costs and ensuring reliable customer experiences"**（调试不透明的 AI 管道、控制不可预测的 token 成本、保证可靠的客户体验），并指出随着 LLM 与 agentic 工作流规模化进入生产，"operational challenges can multiply"。官方还引用报告称，企业 IT 最重要的可观测性任务中有两项是"让可观测工具适配新架构模式"与"确保合规"，说明传统监控模型与 AI 架构不匹配。
4. **解决的问题**：
   - AI 管道不透明，根因分析跨越传统系统与 AI 决策层两层
   - token 成本不可预测、无法按模型归因
   - 需要追踪跨 AI 服务与传统服务的完整请求
   - 多 Agent 工作流中的动态发现（agent/model/依赖持续变化）
   - AI 输出质量的持续评估（一致性、与业务意图的对齐）
   - AI 行为基线与偏离检测（性能、成本、结果）
   - 治理（governed AI operations）
5. **技术原理**：据两份 IBM 官方公告，其技术路径可分三阶段演进：**第一阶段（2025-10，GenAI Observability GA）**——提供"对 AI 应用的基础可见性"：监控 GenAI 性能、**跨 AI 服务与传统服务追踪请求**、跨模型跟踪 token 与成本。其关键设计是**"AI 信号与传统信号在同一追踪体系内"**，即不把 AI 观测做成孤立工具，而是延续 Instana 的自动发现 + 全栈追踪骨架（这也解释了为何 IBM 强调 "trace requests across AI and traditional services"）。**第二阶段（同期，Intelligent Incident Investigation）**——使用 **Agentic AI 做更快、更全面的根因识别**（官方称其在 GenAI Observability GA 前以 preview 形态提供），即把 AI 用于"调查"而非仅用于"被观测"。**第三阶段（2026-05，AI Agent & LLM Observability）**——官方称这是 GenAI Observability 能力的下一步演进，目标是"deliver deeper intelligence, automation and business context"，具体拆为四项新要求：① **自动发现并跟上持续变化的 agents、models 与依赖**（对应动态图能力在 AI 层的延伸）；② **规模化持续评估 AI 输出**（质量、一致性、与业务意图对齐）；③ **建立 AI 行为基线并检测偏离**（性能、成本、结果三个维度）；④ **理解 agents 如何做决策**（可解释性）。整体定位从"gen AI visibility"转向"**AI system understanding**"。**推断边界**：官方公告**未公开**实现机制（采集方式、与 OpenTelemetry GenAI 语义约定的关系、评估模型/评测方法、基线算法）；本稿仅复述官方明示的能力与目标，不作机制级断言。
6. **技术效果**：官方公告给出的是**能力与目标描述**（"faster, more comprehensive root cause identification"、"from reactive troubleshooting to proactive, governed AI operations"），**未给出量化数据**（如根因定位时间缩短比例、成本下降百分比）。
7. **落地情况**：已商用——GenAI Observability 于 **2025-10 宣布 GA**（IBM TechXchange）；Intelligent Incident Investigation 在此前为 preview；AI Agent & LLM Observability 于 2026-05 宣布。官方产品页 `ibm.com/products/instana/generative-ai-observability` 与 `ibm.com/products/instana/intelligent-incident-investigation` 作为独立产品页存在（详见来源）。
8. **案例**：**未能取得该条目的具名客户案例**。**⚠️ 口径修正（v1.1，响应 B-R1-01）**：v1.0 把"IBM 于 2025-10-06 公告 GenAI Observability GA"这一**产品发布事实**当作"发布案例"写入字段 8，被第 1 轮评审判定为**口径失真**（发布事件无客户名，不构成案例）。v1.1 已将该事实**移回字段 2/7**（时间线与落地情况），字段 8 如实声明缺失。→ `官方来源缺失：未取得 IBM Instana GenAI/LLM Observability 的具名客户案例（客户名+场景+结果+时间）`，本条目不重复计入 §2.7.1 的 State of Oregon OIS 案例。
9. **来源**：
   - 官方来源（必须）：
     - [Drive operational efficiency with GenAI observability](https://www.ibm.com/new/announcements/drive-operational-efficiency-with-gen-ai-observability) — 发布 2025-10-06（更新 2026-03-23）— 官方新闻稿/公告
     - [Advancing AI operations with AI Agent and LLM Observability](https://www.ibm.com/new/announcements/advancing-ai-operations-with-ai-agent-and-llm-observability) — 发布 2026-05-05 — 官方新闻稿/公告
     - [IBM Instana Observability（官方产品页，Features 与新闻条目）](https://www.ibm.com/products/instana) — 日期：官方未标注（2026-09-12 确认）— 产品页
     - [IBM Instana GenAI Observability（官方产品页，由公告正文引用）](https://www.ibm.com/products/instana/generative-ai-observability) — 日期：官方未标注（链接由官方公告给出）— 产品页
     - [IBM Instana Intelligent Incident Investigation（官方产品页，由公告正文引用）](https://www.ibm.com/products/instana/intelligent-incident-investigation) — 日期：官方未标注（链接由官方公告给出）— 产品页
   - 非官方来源（可选，仅用于原理补充）：
     - 无

---

### 2.8 Grafana Labs

#### 2.8.0 厂商近10年战略与技术主线（≤500字）

Grafana Labs 的技术主线可概括为**"开源可组合栈 + 用大数据量降本"**，其独特之处在于它是十家中**唯一以开源项目为产品主体**（而非"开源社区版 + 商业版"）的厂商，也是**唯一明确把"遥测成本"作为核心技术命题**的厂商。其栈被业界称为 **LGTM**：**L**oki（日志，2020 年加入）、**G**rafana（可视化，2014 年起的事实标准）、**T**empo（追踪，2021 年加入）、**M**imir（指标，源自 Cortex，2021 年）、后续补齐 **Pyroscope**（持续剖析，2022 年 Phlare 自研 + 2023-03 收购 Pyroscope 后合并）。其架构哲学与专有 APM 相反：**每个信号用最适合的存储引擎，用统一查询层与 Grafana 面板组合**，用户可自托管也可用 Cloud。2023 年起进入"降本 + AI"双线：**Adaptive Metrics**（2023）用动态聚合/丢弃低价值标签降低指标基数成本，2026-08 前后官方宣布 **Adaptive Profiles GA**，形成 "Adaptive Telemetry" 套件；**Asserts**（2024）做"以服务为中心的断言式检测"，**Sift**（2024-2025）做自动调查与可能原因排序；**Grafana Assistant**（2025-2026）做生成式 AI 助手。官方 2026-08 宣布**突破 10,000 客户**。

对用户的意义：① **Adaptive Metrics / Adaptive Profiles 的"边缘降采样"思路**与用户在交换机内嵌环境做"采样、聚合、边缘预处理"的约束直接冲突/契合——这是本稿中最贴近用户"低开销采集"命题的商业实现；② **Pyroscope 的"持续剖析数据库"架构**（单二进制、对象存储、多租户）对交换机侧做 profile 聚合上送有工程参考价值；③ Grafana 的"开源可组合"路线给了用户一条**不采购即可对标**的路径。

#### 2.8.1 Grafana Labs - Grafana Pyroscope（持续剖析数据库，Phlare + Pyroscope 合并）

1. **技术类别**：传统技术（持续剖析存储与查询）+ AI技术（AI增强：作为 AI 调查（Sift/Assistant）的信号输入）
2. **首次发布/关键版本时间**：**分三段、按证据强度分别标注（v1.1 重写，响应 B-R1-09 ①）**：
   - **Phlare：2022 年** —— **官方产品页原文**："Phlare, which was launched by Grafana Labs in **2022**"（S 级，页面内可读到该句）；
   - **Pyroscope 开源项目：2021 年** —— **官方产品页原文**："Pyroscope, which was founded by Ryan Perry and Dmitry Filimonov in **2021**"（S 级）；
   - **Grafana Labs 收购 Pyroscope：2023-03** —— ⚠️ **据公开报道，未取得官方来源**。**本轮修正说明**：v1.0 把该日期写成"**明确可考**…以上均来自 Grafana 官方产品页原文表述"，属**来源与陈述不符的过度归因**——官方产品页只写两项目"formed by the **merger** of two open source continuous profiling projects"，**页面不含任何收购日期**（第 1 轮评审抽检 #22 已实测确认）。v1.1 已把该日期**与官方产品页解耦**，改为 `【据公开报道，未取得官方来源】`。
   - **两项目合并为 Grafana Pyroscope**：官方产品页原文表述为"merger of two open source continuous profiling projects"，**该表述在本条目字段 5 引用时已限定为"合并"而非"收购"**。
3. **推出背景**：2019-2022 年"三大信号（Metrics/Logs/Traces）"格局确立后，业界发现一个缺口：三类信号能告诉你"**哪里慢**"，但不能告诉你"**为什么慢、慢在代码哪一行**"。传统 profile 是"性能测试阶段的一次性工具"或"出事后临时开启的调试手段"，缺少**长期留存、可横向对比、可与其它信号关联**的生产级存储。同时持续剖析的技术难点不在采集而在**存储与查询规模**：profile 是多维标签 + 栈样本的高基数数据，需要专门的数据模型。Grafana 的切入点是"**给 profile 做一个像 Prometheus 那样易部署、像 Loki 那样用对象存储降本的数据库**"。
4. **解决的问题**：
   - 缺少生产环境长期留存的 profiling 数据（无法做趋势与版本对比）
   - profile 与 metrics/logs/traces 割裂，无法关联定位
   - 高基数 profile 数据的存储成本与查询性能问题
   - 多团队/多租户场景下 profiling 平台难以隔离与共享
   - 部署运维复杂度高（需要外部依赖、集群组件多）
5. **技术原理**：官方产品页给出了相当具体的架构设计，可归纳为五点：① **存储层用对象存储**——官方明确"Because Pyroscope uses object storage, you can store all the history you need without breaking the bank"，支持 AWS S3、Google Cloud Storage、Azure blob storage、OpenStack Swift 及任何 S3 兼容对象存储；这是其把长期留存成本压下来的核心（把热数据与冷历史分离）。② **架构与 Loki/Mimir/Tempo 一致**——官方明确"Consistent architecture with Loki, Mimir, and Tempo, which reduces the learning curve"，即微服务化 + 对象存储 + 多租户的同一套模式，便于已在用 LGTM 的团队复用运维经验。③ **单二进制易部署**——官方描述"Easy to install with just one binary and no additional dependencies — **just like Prometheus**"，这是对比 Mimir/Loki 集群形态的轻量入口。④ **横向扩展与高可用**——官方描述"Horizontally scalable, distributed architecture"，并可"run in a highly available configuration to ensure 100% uptime, even during upgrades and machine failure"。⑤ **多租户隔离**——"Multi-tenancy and isolation make it possible to run one database for multiple independent teams or business units"。⑥ **与 Grafana 原生集成**——官方明确"The project natively integrates with Grafana, making it possible for users to **correlate their profiling data with metrics, logs, and traces** and to use profiles as another key observability signal"，即 profile 成为第四类一等信号并可与其它三类在同一面板关联。**推断边界**：官方页面**未公开** profile 的存储格式与压缩算法、标签索引结构、单节点吞吐上限、采集侧 Agent（Alloy/ebpf profiler）的具体机制；本稿不作断言。
6. **技术效果**：官方定性表述为"fast, scalable, highly available, and efficient storage and querying"、"understand resource usage in your applications **down to the line number**"。**官方未在该页面给出量化数据**（如压缩比、CPU 开销、查询延迟）。可验证的规模信号：官方页面显示 GitHub star 数 **10,473**（页面实时数值，供参考）。
7. **落地情况**：已商用（Grafana Cloud Profiles 官方标注 **GA**，产品页横幅"Announcement: Grafana Cloud Profiles, powered by Pyroscope, is now GA"）。开源项目 Apache-2.0 许可（GitHub `grafana/pyroscope`）。附录：Grafana 官网新闻室列有 [Grafana Labs Gives Every Observability Signal an Intelligent Optimization Layer, Completing Adaptive Telemetry Suite with Adaptive Profiles GA](https://grafana.com/press/) — **2026-08-04**（官方新闻稿，超出 2015-2025 窗口，作延伸注记）。
8. **案例**：**未能取得 Pyroscope 专属的具名客户案例**。Grafana 官方新闻室（`grafana.com/press/`，本轮实测 200）中带日期的具名客户条目仅 **Dabble（2026-08-31）**，其标的为 Grafana Cloud + **Grafana Assistant**（非 Pyroscope），且**超出 2015-2025 调研窗口**，故按"同一案例只在最相关条目计入"的规则归入 §2.8.2。Grafana 官方成功案例页（`grafana.com/success/`，本轮实测 200）含 Salesforce（每分钟处理 7,000 万指标、12 万告警；基础设施监控 FTE 时间减少 66%；CPU 使用下降 50%）、Dell Technologies（每周节省 6 小时）等具名量化结果，**但页面未标注发布日期**，故仅登记于 §6.5 表 B。→ 本条目字段 8 **计为不齐**。
9. **来源**：
   - 官方来源（必须）：
     - [Grafana Pyroscope OSS（官方产品页，含 Phlare/Pyroscope 沿革与架构描述）](https://grafana.com/oss/pyroscope/) — 日期：官方未标注（2026-09-12 确认；页面含 "Phlare… launched by Grafana Labs in 2022" 与 "Pyroscope… founded by Ryan Perry and Dmitry Filimonov in 2021" 原文，**但不含收购日期**）— 产品页
     - [Grafana Pyroscope（官方 GitHub 仓库）](https://github.com/grafana/pyroscope) — 日期：官方未标注（链接由产品页给出）— 官方 GitHub
     - [Grafana Labs Press（官方新闻室，含新闻稿列表与日期）](https://grafana.com/press/) — 日期：页面所列新闻稿日期至 2026-08-31（2026-09-12 确认）— 官方新闻稿列表
     - [Grafana 官方成功案例页（Success stories and case studies）](https://grafana.com/success/) — 日期：官方未标注（2026-09-12 确认；含 Salesforce / Dell Technologies 等具名量化结果）— 官方案例库
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.8.2 Grafana Labs - Grafana Assistant 与 AI 工具链（Machine Learning / Sift / Asserts / MCP）——AI技术

1. **技术类别**：AI技术（AI增强：生成式 AI 助手 + ML 异常检测 + 自动调查）
2. **首次发布/关键版本时间**：ML 与 Sift 的官方文档已上线（`grafana.com/docs/grafana-cloud/ai-tools/`）；Grafana Assistant 于 **2025-2026 年**推出（官方新闻室 2026-08-31 客户案例以 Grafana Assistant 为标的）。标注"官方未明确统一发布日期，据官方文档与新闻室推断为 2024-2026 年间陆续发布"。
3. **推出背景**：Grafana 的开放可组合栈带来一个副作用：**能力多但入口分散**，用户需自行组合面板、告警规则与数据源，学习成本高；同时开源 ML 能力（如异常检测）长期缺位于核心产品，用户需自行搭建。2024-2026 年 Grafana 的策略是给每个信号加一层"**智能优化层**"（官方术语 intelligent optimization layer / Adaptive Telemetry），并把生成式 AI 与 ML 收敛为统一 AI 工具集。
4. **解决的问题**（据官方文档 `ai-tools` 页面）：
   - 阈值告警不适用动态场景，需要**动态阈值**与异常检测
   - 缺少自动化的"可能原因"排序，调查仍需人工
   - 指标预测（容量规划）能力缺位
   - AI Agent 与 Grafana 之间缺少标准化接口
   - LLM 能力无法在 Grafana 内直接使用（缺少插件/连接器）
   - AI 编码/运维 Agent 缺少对 Grafana 资源的结构化访问方式
5. **技术原理**：官方文档把 Grafana Cloud 的 AI 能力定位为 **"Infrastructure-level AI capabilities that enhance your Grafana workflows rather than standing alone as products"**（**增强工作流的基础设施级 AI 能力，而非独立产品**）——这是一个重要的架构取向声明。组件构成（官方原文）：① **Grafana AI 概览**——说明其 AI 能力套件构成；② **MCP servers**——通过**全托管的 Cloud MCP Server 或自托管的开源 MCP Server**把 AI agents 接入 Grafana，即用 Model Context Protocol 作为 Agent 与可观测平台之间的标准接口；③ **Machine learning / Sift**——官方描述为"Forecast metrics, detect anomalies, and run automated investigations with **Sift** to alert on **dynamic thresholds** and surface **likely causes**"，即三件事：指标预测、异常检测、自动调查并给出可能原因排序；④ **LLM plugin**——"Enable large language model features across Grafana Cloud"，即以插件形态在 Grafana 内启用 LLM；⑤ **gcx CLI**——"AI-native CLI that gives you and your AI coding agent structured access to your Grafana stack and resources"，即提供**结构化（而非屏幕抓取）的编排入口**，让 AI 编码 Agent 能可靠操作 Grafana 资源。**推断边界**：官方文档为组件清单式描述，**未公开** Assistant 的底层模型、Sift 的异常检测算法族、MCP Server 的工具清单与权限模型、LLM 数据边界；本稿不作断言。
6. **技术效果**：官方文档给出能力描述（forecast、detect anomalies、dynamic thresholds、surface likely causes）。**官方未在该文档给出量化数据**（如误报率、调查耗时）。**官方新闻室可用量化/结果类表述**：新闻稿 [Grafana Labs Crosses 10,000-Customer Milestone as AI Adoption Accelerates Growth Across the Platform](https://grafana.com/press/) — **2026-08-26**（官方新闻稿，规模数据：10,000 客户；超出窗口，作延伸注记）。
7. **落地情况**：已商用（Grafana Cloud AI 工具集在售；MCP Server 提供托管与开源自托管两种形态；gcx CLI 已发布）。规模数据：官方 2026-08-26 新闻稿宣布突破 **10,000 客户**。
8. **案例**（**v1.1 计为五要素齐备；响应 B-R1-01**）：`客户 | 行业 | 场景 | 结果 | 时间 | 官方来源URL`
   - **Dabble | 在线博彩/游戏（iGaming）| 采用 **Grafana Cloud + Grafana Assistant** 以缩短事件响应时间 | 缩短事件响应时间（官方新闻稿标题原文 "…to **Cut Incident Response Times**"；页面未给出量化百分比）| **2026-08-31** | https://grafana.com/press/
   - **证据完整度说明**：① 客户名、场景、结果、时间四要素**均在 Grafana 官方新闻室页面的标题与日期中逐字可读**，且有官方 URL；② 但新闻室页面以 "Read more" 形式呈现，**本轮仍未取得其独立详情页 URL**（不猜测、不编造）；③ **时间 2026-08 超出 2015-2025 调研窗口**，属"延伸注记"类案例——本稿在 §6.5 表 A 中**分别统计"窗口内/窗口外"两列**，不掩盖该事实。
9. **来源**：
   - 官方来源（必须）：
     - [AI tools（Grafana Cloud 官方文档）](https://grafana.com/docs/grafana-cloud/ai-tools/) — 日期：官方未标注（2026-09-12 确认）— 官方文档
     - [Grafana Labs Press（官方新闻室）](https://grafana.com/press/) — 日期：所列条目至 2026-08-31（2026-09-12 确认）— 官方新闻稿列表
     - [Grafana Cloud Machine Learning / Sift（官方文档）](https://grafana.com/docs/grafana-cloud/machine-learning/) — 日期：官方未标注（2026-09-12 确认；页面重定向至 AI tools 页面）— 官方文档
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.8.3 Grafana Labs - Adaptive Metrics / Adaptive Profiles（自适应遥测：降本与边缘降采样）

1. **技术类别**：传统技术（遥测降采样与聚合优化）+ AI技术（AI增强：2026 官方称其为"Intelligent Optimization Layer"）
2. **首次发布/关键版本时间**：**Adaptive Metrics 于 2023 年**推出（据 Grafana 产品线公开演进与官方新闻室条目推断；**本稿未取得 2023 年官方发布页**）；**Adaptive Profiles 于 2026-08-04 GA**（官方新闻稿 [Grafana Labs Gives Every Observability Signal an Intelligent Optimization Layer, Completing Adaptive Telemetry Suite with Adaptive Profiles GA](https://grafana.com/press/)，**超出 2015-2025 窗口，作延伸注记**）。
3. **推出背景**：2020-2024 年可观测性最大的商业问题是**成本失控**，尤其是指标基数（cardinality）爆炸：K8s 环境中每个 Pod、每个标签组合都产生独立时间序列，导致"数据量增长快于业务增长"、账单增速超过收入增速。行业出现两类应对：一是限制采集（丢数据），二是**智能降采样**（在保留查询能力的前提下减少存储的时间序列数量）。Grafana 选择后者，并把该能力从指标扩展到全信号。
4. **解决的问题**：
   - 指标基数爆炸造成的存储与查询成本失控
   - 一刀切降采样导致关键维度丢失、查询结果失真
   - 无人使用的"废指标"长期占用成本
   - profile 数据量增长带来的存储压力（Adaptive Profiles 对应）
   - 需要在"省成本"与"不丢可观测性"之间做自动化权衡
5. **技术原理**：**v1.1 已用 Grafana 官方文档原文替换 v1.0 的推断段（响应 B-R1-09 ②；该缺口在纯 HTTP 环境下实际可闭合）**。`https://grafana.com/docs/grafana-cloud/adaptive-telemetry/adaptive-metrics/` **本轮实测 HTTP 200 且正文完整**，官方原文为：**"Adaptive Metrics is a metrics management and cardinality optimization feature in Grafana Cloud that enables you to identify and eliminate unused time series data through aggregation."**；机制描述原文：**"By analyzing how your metrics are being used across dashboards, alerts, recording rules and queries, it provides recommendations for aggregating underutilized metrics into lower-cardinality versions. It then continuously reanalyzes your usage, updating its recommendations to reflect changes in your observability needs."**；收益原文：**"Your existing dashboards, alerts, and queries continue to work seamlessly with the aggregated metrics, requiring no manual updates."**；操作面含 Review and manage rules / Create rules（UI、API、Terraform 三通道）/ Create exemptions / Additional configuration。
   据此，Adaptive Metrics 的机制可**按官方原文**归纳为：① **持续分析真实使用模式**（跨 dashboards / alerts / recording rules / queries），而非按标签静态配置；② **把低使用率指标聚合为低基数版本**（"aggregating underutilized metrics into lower-cardinality versions"），而**不是丢弃数据点**；③ **持续重分析并更新建议**（"continuously reanalyzes your usage"）；④ **对既有 Dashboard/Alert/Query 透明**，不需人工改写；⑤ 提供 **exemptions**（豁免）防止特定指标或标签被纳入建议。**Adaptive Profiles**（2026-08-04 GA）把同一思路应用到 profile 信号（官方新闻稿称其"completing Adaptive Telemetry Suite"）。2026-08 官方进一步提出"**Intelligent Optimization Layer**"概念，把 Adaptive Metrics/Profiles/Logs 统一为"给每一类可观测信号加一层智能优化层"。**推断边界（已大幅收缩）**：官方文档**未公开**聚合决策算法（是否含 ML 模型、如何评估维度价值）、恢复机制细节与成本节省模型；**本稿保留的推断仅为"聚合决策算法的具体实现未公开"这一条**，v1.0 中"原理部分推断成分较高"的表述已删除。
6. **技术效果**：官方新闻稿标题表述为"Gives Every Observability Signal an Intelligent Optimization Layer"（定性）。**官方在本稿取得的页面未给出量化成本节省比例**（如"降低 X% 指标量/Y% 成本"），故标注**官方未给出量化数据**。
7. **落地情况**：已商用（Adaptive Metrics 为 Grafana Cloud 在售能力；Adaptive Profiles 官方 2026-08-04 宣布 **GA**，**超出窗口，作延伸注记**）。
8. **案例**：**未能取得 Adaptive Metrics / Adaptive Profiles 专属的具名客户成本节省案例**。Grafana 官方成功案例页（`grafana.com/success/`）含一条**与 Adaptive Metrics 直接相关的量化客户证言**——"Thanks to **50% savings on our telemetry bill with Adaptive Metrics**… **$1.74M in savings revealed with Adaptive Metrics**"（Oren Lion, Director of Software Engineering），以及 "**87% reduction in mean time to detect (MTTD) on S1 & S2 incidents with Grafana IRM**"——**但该证言在页面摘取片段中未出现企业名称，且页面未标注发布日期**，故**缺"客户名"与"时间"两要素**，不计入表 A，仅登记于 §6.5 表 B。→ 本条目字段 8 **计为不齐**。`官方来源缺失：Adaptive Metrics 专属案例缺客户名与日期`。
9. **来源**：
   - 官方来源（必须）：
     - **[Adaptive Metrics（Grafana Cloud 官方文档，本轮实测 HTTP 200 且正文完整）](https://grafana.com/docs/grafana-cloud/adaptive-telemetry/adaptive-metrics/)** — 日期：官方未标注（2026-09-12 确认；含 cardinality optimization 与 "identify and eliminate unused time series data through aggregation" 等机制原文）— 官方文档 **（v1.1 新增：v1.0 曾声明"未能取得该文档"，该缺口本轮闭合）**
     - [Grafana Labs Press（官方新闻室，含 Adaptive Profiles GA 与 Adaptive Telemetry Suite 新闻稿）](https://grafana.com/press/) — 日期：所列条目至 2026-08-31；Adaptive Profiles GA 条目日期 2026-08-04（2026-09-12 确认）【2026延伸·窗口外】— 官方新闻稿列表
     - [AI tools（Grafana Cloud 官方文档，含智能优化层相关能力说明）](https://grafana.com/docs/grafana-cloud/ai-tools/) — 日期：官方未标注（2026-09-12 确认）— 官方文档
     - [Grafana 官方成功案例页（含 Adaptive Metrics 50% 账单节省 / $1.74M 节省的客户证言）](https://grafana.com/success/) — 日期：官方未标注（2026-09-12 确认）— 官方案例库
   - 非官方来源（可选，仅用于原理补充）：
     - 无

---

### 2.9 SolarWinds

#### 2.9.0 厂商近10年战略与技术主线（≤500字）

SolarWinds 是十家中**最"传统 IT 运维"的一家**：其历史根基是网络与系统管理工具（Network Performance Monitor、Server & Application Monitor、Database Performance Analyzer 等数十个独立产品），而非云原生 APM。2015-2021 年其技术主线是**"从工具集合走向统一平台"**：长期被客户诟病的核心问题是"每个工具一套安装、一套界面、一套许可"，运维需要在多个工具之间跳转才能定位一个跨域问题；同时 SolarWinds 的核心客户群（中型企业、政府、传统行业）大量采用**本地部署**，对纯 SaaS 方案接受度有限。因此其推出 **Hybrid Cloud Observability**（自托管统一平台）与 **SolarWinds Observability**（SaaS 版）两条线，官方明确"Deploy in the cloud, self-hosted in your data center, or hybrid"。2022-2025 年的技术重点是**"统一化 + AI/ML 异常检测"**：官方表述为"AI/ML that detects anomalies for faster troubleshooting and remediation"与"Filter out noise with in-depth, AI-powered insights"，即把 AI 用于**降噪**（而非生成式对话）。

对用户的意义：SolarWinds 提供了本调研中**唯一"网络设备监控 + 本地部署 + AIOps 降噪"三合一**的对照样本——这与用户在交换机内部署 Agent 的场景在**部署形态**上最接近（本地、设备侧、客户不愿上云）。其短板也很清晰：**未形成生成式 AI 助手与因果 RCA 的产品化叙事**，说明"传统网络管理厂商转 AIOps"存在能力天花板，这一点对用户评估"Server 端 AI 助手应自研到什么深度"有直接参考价值。

#### 2.9.1 SolarWinds - SolarWinds Observability（统一 SaaS/自托管可观测平台）

1. **技术类别**：传统技术（统一监控平台）
2. **首次发布/关键版本时间**：官方未标注首次发布日期。据 SolarWinds 产品线公开演进，SaaS 形态的 SolarWinds Observability 于 **2022-2023 年**推出，与 Hybrid Cloud Observability（自托管）并行；本稿取证的官方页面为现行版本。标注"官方未明确精确发布日期"。
3. **推出背景**：**官方来源（产品页）给出的背景线索**：其页面明确选址两个部署现实——"Your hybrid IT"（客户环境是本地+混合+云原生混合）与"Your way"（客户要求可云、可自托管、可混合部署）。这反映 2020-2023 年传统 IT 客户的真实约束：既有大量本地遗留系统与网络设备，又新增云原生负载，但没有能力（或合规许可）把所有遥测交给纯 SaaS 厂商。此外，多工具割裂导致"一个故障要在多个工具间跳转"的运维效率问题，是统一平台的直接动机。
4. **解决的问题**：
   - 混合环境（本地+云）缺少统一视图，需多工具拼装
   - 部署形态受限：纯 SaaS 不被合规/本地优先客户接受
   - 服务器、网络设备、VM、主机、容器、数据库等跨域数据割裂
   - 告警噪声大，需要 AI/ML 降噪与异常检测
   - 成本与规模随环境增长而失控
5. **技术原理**：据官方产品页，其技术路径可归纳为四点：① **统一采集与统一视图**——官方描述为"full-stack visibility for your on-prem, hybrid, and cloud-native IT"，覆盖"servers, network devices, VMs, hosts, containers, and infrastructure"，并把网络、基础设施、数据库等域收敛到同一观测面；② **部署形态可选**——官方明确提供两条产品线：[Self-Hosted](https://www.solarwinds.com/hybrid-cloud-observability) 与 [SaaS](https://www.solarwinds.com/solarwinds-observability)，并支持混合；这是其与传统 SaaS 竞品的结构性差异，也是其服务政府/受监管客户的能力基础；③ **按域分层的产品结构**——官方页面明确划分 "For your network"（消除混合网络盲点、可视化复杂混合网络环境、消除运维孤岛）、"For your infrastructure"（从防火墙内外两侧确保本地与云资源性能，统一查看服务器/网络设备/VM/主机/容器）、"For your databases"（深入数据库可见性，并把数据库指标与应用性能、追踪、日志监控**关联**以识别诱因，同时关注基础设施成本节省）；④ **AI/ML 降噪**——官方表述为"AI/ML that detects anomalies for faster troubleshooting and remediation"与"Filter out noise with in-depth, AI-powered insights. Gain actionable intelligence about the health and performance of your entire IT ecosystem"，即 AI 的定位是**检测异常 + 过滤噪声 + 输出可行动情报**，而非对话式助手。**推断边界**：官方产品页为营销式页，**未公开**采集 Agent 架构（是否统一 Agent、是否支持 eBPF/内核态采集）、后端存储与关联模型、异常检测所用算法族、AIOps 定位的具体产品名（页面提到 "AIOps-powered insights" 但未给出独立产品页）；本稿不作断言。
6. **技术效果**：官方定性表述为"Accelerate performance, optimize costs, and deliver superior customer experience with AI/ML that detects anomalies for faster troubleshooting and remediation"。**官方未在该页面给出量化数据**（如告警降噪比例、MTTR 改善）。
7. **落地情况**：已商用（SaaS 与自托管双形态在售，官网提供 Demo 与试用入口）。规模数据官方未在该页面披露。
8. **案例**（**v1.1 新增：2 个五要素齐备的 SolarWinds 官方案例（含 Publish Date）；响应 B-R1-01/B-R1-05**）：`客户 | 行业 | 场景 | 结果 | 时间 | 官方来源URL`
   - **Charter | 托管服务（MSP）| 用 SolarWinds Incident Response 整合其 IT 运营，替代第三方邮件与电话核验，自动化整个事件生命周期并引入电话/SMS/邮件多渠道告警、移动与全球轮班管理、智能去重降噪 | 事件确认时间**降低 93%**；显著降低告警噪声 | **Publish Date 2026-09-09**【2026延伸·窗口外】| https://www.solarwinds.com/resources/case-study/charter-case-study
   - **TV Insight | 媒体/广告测量（实时电视测量与定向广告，峰值约 200 万请求/秒）| 要求 100% 系统可用性，但此前依赖碎片化通知与人工协调；改用 SolarWinds Incident Response 集中告警、自动化 on-call 管理，引入多渠道通知、失效安全升级路径与自动排班 | 加快告警确认时间、降低运营风险（官方未给量化百分比）| **Publish Date 2026-09-09**【2026延伸·窗口外】| https://www.solarwinds.com/resources/case-study/tv-insight-case-study
   - **说明**：两条案例的客户名、场景、结果、时间（官方页面显式标注 `Publish Date`）、官方 URL 五要素齐备，**唯时间超出 2015-2025 窗口**，故在 §6.5 表 A 中计入"窗口外"列。SolarWinds 官方案例 sitemap 中另有 `redis-case-study`（未逐页抓取，故不登记内容）。
9. **来源**：
   - 官方来源（必须）：
     - [Monitoring and Observability（官方产品页）](https://www.solarwinds.com/observability) — 日期：官方未标注（2026-09-12 确认）— 产品页
     - [SolarWinds Hybrid Cloud Observability（自托管，官方产品页，由上文链接给出）](https://www.solarwinds.com/hybrid-cloud-observability) — 日期：官方未标注（链接由官方页面给出）— 产品页
     - [SolarWinds Observability（SaaS，官方产品页，由上文链接给出）](https://www.solarwinds.com/solarwinds-observability) — 日期：官方未标注（链接由官方页面给出）— 产品页
     - **[Charter 官方案例研究（Publish Date 2026-09-09；事件确认时间 −93%）](https://www.solarwinds.com/resources/case-study/charter-case-study)** — **发布 2026-09-09**【2026延伸·窗口外】— 官方案例
     - **[TV Insight 官方案例研究（Publish Date 2026-09-09）](https://www.solarwinds.com/resources/case-study/tv-insight-case-study)** — **发布 2026-09-09**【2026延伸·窗口外】— 官方案例
     - [SolarWinds 官方 sitemap（本轮用于挖掘官方案例 URL 与站点结构）](https://www.solarwinds.com/sitemap.xml) — 抓取于 2026-09-12 — 官方站点地图
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.9.2 SolarWinds - 网络设备监控与 NetFlow 分析能力（NDM/NPM）

1. **技术类别**：传统技术（网络性能与流量监控）
2. **首次发布/关键版本时间**：`官方未明确【待核验】。` **本轮修正（B-R1-05 ①）**：v1.0 声明"未能定位 SolarWinds 具体网络产品官方页面路径"，该缺口**本轮已闭合**——`https://www.solarwinds.com/network-performance-monitor`（NPM）与 `https://www.solarwinds.com/netflow-traffic-analyzer`（NTA）**均实测 HTTP 200 且正文完整**。但**两个产品页均未标注首次发布日期或版本历史**，故时间字段仍为 `官方未明确`。据其产品历史，NPM 与 NTA 属 SolarWinds 十余年的核心产品并在 2015-2025 持续迭代（**此句为 C 级推断，不作事实依据**）。
3. **推出背景**（**v1.1 已从"纯 C 级推断"升级为"官方产品页原文支撑"**）：**官方 NPM 产品页原文**给出的背景是："Network performance monitoring is the practice of tracking availability, traffic, and device health so you can detect and resolve issues affecting network performance"；针对的现实痛点是**多厂商网络环境下的可见性碎片化**——"SolarWinds NPM helps you monitor **multi-vendor** network devices, including routers, switches, firewalls, and wireless controllers"、"Monitor **fault, availability, and performance** across routers, switches, firewalls, and wireless access points in a single console"。**官方 NTA 产品页原文**给出的痛点是**带宽与流量的成分不可见**：需要"Identify bandwidth hogs, understand traffic, and plan network resources"、"uncover which specific endpoints and applications are generating heavy network traffic and creating bottlenecks, which can be tied to problems elsewhere in your IT stack"。**综合（含本稿推断，标注边界）**：其核心客户群以中大型传统企业与政府为主，网络由大量交换机、路由器、防火墙与 WAN 链路构成，痛点是**网络层与应用层割裂**（网络团队看设备指标、应用团队看应用性能，故障时互相推诿）——**前半句有官方产品页原文支撑，"网络层与应用层割裂"这一因果归因仍属本稿推断**。
4. **解决的问题**（**推断**）：
   - 网络设备健康与容量（接口利用率、错误、丢包）监控
   - 跨厂商异构设备统一采集（SNMP/NetFlow/sFlow/IPFIX）
   - 流量成分分析（谁占用了带宽、流向哪里）
   - 应用与网络关联（把应用性能问题定位到网络跳）
   - 本地/混合部署下的网络盲点消除
5. **技术原理**（**v1.1 已用官方产品页原文大幅替换 v1.0 的纯推断段；响应 B-R1-05 ①**）：据 SolarWinds 官方 NPM 与 NTA 产品页原文，其技术路径可归纳为：
   - ① **设备侧采集与多厂商覆盖**（**官方原文**）："Monitor **fault, availability, and performance** across routers, switches, firewalls, and wireless access points in a single console"、"track key metrics like **response time and packet loss**"、"SolarWinds NPM helps you monitor **multi-vendor** network devices… **Automatically discover devices**"；官方同时提供基于**历史基线**的告警（"continuously monitors key metrics and uses **historical baselines**"、"Configure intelligent alerts with **dynamic baselines, dependencies, and thresholds**"）与**容量预测**（"Capacity forecasting reports help you identify saturated links and plan upgrades before performance degrades"）。
   - ② **跳级路径可视化 NetPath™**（**官方原文，与用户"流级遥测"命题直接相关**）："SolarWinds NPM **NetPath™** provides **hop-by-hop path visualization** across on-premises and cloud network infrastructure, helping you see where **latency and packet loss** occur along the route"。
   - ③ **跨域指标同轴关联 PerfStack™**（**官方原文**）："**PerfStack™** lets you **drag and drop network, system, and application metrics onto a single timeline** so you can quickly see relationships, investigate issues, and speed network troubleshooting to reduce MTTR"——这是"应用指标与网络指标同轴对齐"的官方机制表述。
   - ④ **拓扑与依赖**（**官方原文**）："Use **topology maps** to understand connections between network devices, interfaces, and locations. Review **dependencies** alongside availability and performance data to trace the potential impact of an outage"。
   - ⑤ **流级采集协议**（**官方原文，NTA 产品页**）："support for **NetFlow, sFlow, J-Flow, IPFIX, and more**"；提供 **Flow Navigator**（"Create and access personalized network traffic views with the flow navigator… schedule automatic weekly delivery"）、按应用/协议/IP 组的带宽视图、以及 **port 0 monitoring**（"enhance network security with **port 0 monitoring**"）。
   - ⑥ **无线与硬件健康**（**官方原文**）："visibility into wireless controllers, access points, and connected clients… **Wi-Fi heat maps**… monitor hardware health metrics such as **temperature and fan speed**"。
   **推断边界（已大幅收缩）**：官方产品页**未公开**采集 Agent 架构（是否统一 Agent、是否支持 eBPF/内核态采集）、后端存储与关联模型、异常检测所用算法族、单实例吞吐与规模上限。v1.0 中"以 SNMP 轮询、以 SNMP Trap/Syslog 接收设备事件、依据 CDP/LLDP 与路由信息构建拓扑"等具体机制表述**官方产品页未逐字给出**，本稿保留但**明确标注为行业通用范式推断（C 级）**，不得作为已证实机制引用。
6. **技术效果**：**官方未给出量化数据**（NPM/NTA 产品页均无 CPU 开销、采集规模、告警降噪比例等数字；按 00 号规范，此写法本身即满足字段 6 要求）。可验证的能力事实：支持 NetFlow/sFlow/J-Flow/IPFIX 多协议、NetPath™ hop-by-hop 路径、PerfStack™ 跨域同轴、拓扑依赖映射、Wi-Fi 热图与硬件健康指标。
7. **落地情况**：**已商用**（SolarWinds 在售产品线，官方产品页提供 30 天免费试用、互动 Demo 与在线报价；NPM 与 NTA 均为其 Observability Self-Hosted 产品族的组成模块——官方原文："**SolarWinds Observability Self-Hosted, built from the heritage of our Orion® modules and powered by AIOps**"）。**官方未披露客户规模或部署数量。**
8. **案例**：**本条目不独立登记案例**（SolarWinds 的两个五要素案例归入 §2.9.1，按 §6.1"同一案例只计入最相关条目"规则不重复计数）→ 字段 8 **计为不齐**。
9. **来源**（**v1.1 重大补强：v1.0 声明"未能定位具体网络产品官方页面路径"，本轮已实测取得 2 条官方产品页原文；响应 B-R1-05 ①**）：
   - 官方来源（必须）：
     - **[Network Performance Monitor（NPM）官方产品页](https://www.solarwinds.com/network-performance-monitor)** — 日期：官方未标注（2026-09-12 确认；含 multi-vendor 设备监控、NetPath™ hop-by-hop、PerfStack™、动态基线、拓扑映射、无线与硬件健康等原文）— 产品页
     - **[NetFlow Traffic Analyzer（NTA）官方产品页](https://www.solarwinds.com/netflow-traffic-analyzer)** — 日期：官方未标注（2026-09-12 确认；含 NetFlow/sFlow/J-Flow/IPFIX 支持、Flow Navigator、带宽分析、port 0 monitoring 等原文）— 产品页
     - [Monitoring and Observability（官方产品页，厂商层面来源）](https://www.solarwinds.com/observability) — 日期：官方未标注（2026-09-12 确认）— 产品页
     - [SolarWinds 官方 sitemap（本轮用于定位 NPM/NTA 与官方案例 URL）](https://www.solarwinds.com/sitemap.xml) — 抓取于 2026-09-12 — 官方站点地图
   - 非官方来源（可选，仅用于原理补充）：
     - 无
   - **缺口登记（v1.1 更新）**：本条目字段 **2、8** 仍不达标（时间无官方发布日；案例不独立登记），但**字段 3、5 已由"纯 C 级推断"升级为"官方产品页原文支撑"**，v1.0 的 P1 缺口（"未取得任何 SolarWinds 官方原文"）**已闭合**。**§5 P1-5 的对照项已同步改写**（见 §5）。

#### 2.9.3 SolarWinds - AIOps 驱动的异常检测与告警降噪

1. **技术类别**：AI技术（AI增强：AIOps 异常检测与降噪）
2. **首次发布/关键版本时间**：官方未标注具体发布年份。官方产品页仅在现行版本中表述为 "AIOps-powered insights"，并称以 AI/ML 检测异常；据 SolarWinds 产品线公开演进推断为 **2022-2025 年间随统一平台逐步引入**（**C 级推断**）。
3. **推出背景**：**官方来源（产品页）给出的线索**：其产品页把问题表述为"Filter out noise"（过滤噪声）——即传统 IT 运维在统一平台化后遇到的新瓶颈并非"没有数据"，而是"数据太多、告警太多，人工无法分辨哪些需要行动"。同时官方强调要"Gain actionable intelligence about the health and performance of your entire IT ecosystem"，说明需求是把**海量信号压缩为可行动的少量结论**。这与用户在 Server 端做 AI 助手时的"告警收敛"目标完全一致。
4. **解决的问题**（**官方表述 + 推断**）：
   - 告警噪声大，人工无法逐条研判（官方："Filter out noise"）
   - 需要自动发现异常而非依赖静态阈值（官方："AI/ML that detects anomalies"）
   - 需要更快的排障与修复（官方："for faster troubleshooting and remediation"）
   - 需要覆盖"整个 IT 生态系统"的健康与性能情报（官方："health and performance of your entire IT ecosystem"）
   - 混合环境跨域（网络/基础设施/数据库/应用）相关性的自动计算（**推断**）
5. **技术原理**：**官方仅给出定性定位**："AIOps-powered insights you need, wherever you need them"、"AI/ML that detects anomalies for faster troubleshooting and remediation"、"Filter out noise with in-depth, AI-powered insights"。**推断（C 级）**：其技术路径大概率是传统的 AIOps 三件套——① **多源指标汇聚**（把网络/基础设施/数据库/应用指标统一到同一数据层）；② **动态基线/异常检测**（用季节性分解或统计模型替代静态阈值，产出异常列表）；③ **噪声过滤与关联**（按实体与时间近似性合并相关异常，输出少量"可行动情报"）。**推断边界声明**：官方页面**未披露**任何算法、模型、产品模块名称（页面仅出现 "AIOps-powered" 这一形容词，**未出现独立的 AIOps 产品名**），故本条目**证据等级为"官方定性 + C 级推断"**，不可作为已证实的技术事实。**与用户场景的关联**：本条目的价值不在于技术细节，而在于**反面参照**——一家拥有大量网络与系统数据、且已抓住"降噪"这一正确命题的传统厂商，在本稿取证范围内**未形成生成式 AI 助手/因果 RCA 的产品化叙事**（对比 Dynatrace Davis、Datadog Bits AI、New Relic AI、Elastic AI Assistant、Splunk AI Assistant、IBM Instana GenAI）；这提示用户：**"降噪"是必要条件而非充分条件，Server 端 AI 助手的差异化必须落在"因果 + 拓扑 + 可执行动作"上**。
6. **技术效果**：**官方未给出量化数据**（产品页无降噪比例、MTTR 改善、准确率等数字）。
7. **落地情况**：已商用（作为 SolarWinds Observability 平台的能力项，官方表述为平台整体特性）。规模数据未披露。
8. **案例**（**v1.1 新增，五要素齐备**）：`客户 | 行业 | 场景 | 结果 | 时间 | 官方来源URL`
   - **TV Insight | 媒体/广告测量（实时电视测量与定向广告，峰值约 200 万请求/秒）| 此前依赖碎片化通知与跨工具人工协调，导致归属不清、告警确认延迟与响应人员倦怠；改用 SolarWinds Incident Response 集中告警、自动化 on-call 管理，引入多渠道通知（push/SMS/电话）、失效安全升级路径与自动排班，并以统一 Service Catalog 提供实时系统健康可见性 | 加快告警确认时间、消除运营瓶颈（官方未给量化百分比；该案例与"告警噪声与归属"直接相关，故归入本条目的 AIOps 降噪主题）| **Publish Date 2026-09-09**【2026延伸·窗口外】| https://www.solarwinds.com/resources/case-study/tv-insight-case-study
9. **来源**：
   - 官方来源（必须）：
     - [Monitoring and Observability（官方产品页，含 AIOps/异常检测表述）](https://www.solarwinds.com/observability) — 日期：官方未标注（2026-09-12 确认）— 产品页
     - [TV Insight 官方案例研究（Publish Date 2026-09-09）](https://www.solarwinds.com/resources/case-study/tv-insight-case-study) — **发布 2026-09-09**【2026延伸·窗口外】— 官方案例
   - 非官方来源（可选，仅用于原理补充）：
     - 无
   - **缺口登记（v1.1 更新）**：本条目仍缺字段 2（发布时间的 S/A 级来源）；字段 6（量化效果）官方未给量化数据（按规范允许写"官方未给出量化数据"，计为齐）；字段 8 已由 v1.1 补齐。v1.0 登记的"字段 8 缺失"**已闭合**。

---

### 2.10 OpenTelemetry 生态（CNCF：OpenTelemetry / Prometheus / eBPF 系）

> **本章说明（按 Leader 要求单列子章）**：本章覆盖 00 号规范 2.1 节第 10 项的完整范围，分为三部分：**2.10.A OpenTelemetry 规范与 Collector（含 W3C Trace Context）**、**2.10.B Prometheus 与指标生态**、**2.10.C eBPF 系厂商开源项目（Pixie / Cilium-Hubble / Tetragon / Coroot / opentelemetry-ebpf-profiler / groundcover）**。因该生态由多个独立项目组成，本稿按项目拆分条目，条目数高于"每厂商 ≥3 条"的下限。
> **对用户的重要性**：本章是**全部 10 家中与用户场景重合度最高的一章**——用户在交换机内用 C/C++ + eBPF 采集，技术邻域正是 opentelemetry-ebpf-profiler（内核态 profiling）、Pixie（eBPF 无埋点遥测）、Coroot（eBPF 零埋点 + 服务地图）、Cilium Hubble/Tetragon（eBPF 流级可观测）；上送协议则应优先 OTLP（OpenTelemetry Protocol）。

#### 2.10.0 生态近10年战略与技术主线（≤500字）

OpenTelemetry 生态的主线是**"把可观测数据标准化，让采集与后端解耦"**。**Prometheus** 于 2016 年加入 CNCF（第二个托管项目），以拉取式（pull）采集、多维数据模型与 PromQL 成为云原生指标事实标准；**OpenTelemetry** 于 2019-05 由 OpenCensus 与 OpenTracing 合并成立，目标是一统"埋点 API/SDK + 数据模型 + 传输协议（OTLP）"，其规范由 `open-telemetry/opentelemetry-specification` 维护，并明文声明"describes the cross-language requirements and expectations for all OpenTelemetry implementations"。OTel 的关键贡献有三：① **厂商中立**——埋点一次，可发往任意后端，从根本上削弱专有 Agent 的锁定；② **三信号统一**——Traces、Metrics、Logs 用同一套资源/语义约定模型（Profiles 信号后加入，见 2.10.4）；③ **Collector**——agent/collector 双形态统一代理，官方定位为"vendor-agnostic implementation on how to receive, process and export telemetry data"，取代"一个后端一个 Agent"的拼装。传输层的事实标准是 **W3C Trace Context**（2021-11 成为 W3C 正式推荐标准），它定义了 `traceparent`/`tracestate` 头，使跨厂商、跨语言的分布式追踪可以真正串起来。

**eBPF 支线**则是"采集侧的去 Agent 化"：Pixie（CNCF）用 eBPF 自动采集 full-body request 与应用 profile；Cilium Hubble/Tetragon 提供 L3-L7 流级可观测与安全观测；Coroot 把 eBPF 用于零埋点服务地图与 80%+ 问题自动识别；**opentelemetry-ebpf-profiler** 把 whole-system 跨语言 profiler 收入 OTel 官方组织并接入 OTel Profiles 信号。**这条线是用户 Agent 的直接技术同族。**

#### 2.10.1 OpenTelemetry - OpenTelemetry 规范与 SDK（跨语言可观测标准）

1. **技术类别**：传统技术（开放标准 / 数据模型 / 埋点 API）
2. **首次发布/关键版本时间**：**2019-05**（OpenCensus 与 OpenTracing 合并成立 OpenTelemetry）。本稿未取得该合并的官方 OTel 博客原文（`opentelemetry.io/blog/index.xml` 仅回溯至 2026 年文章），故标注"据公开共识的 2019-05；**官方来源缺失：本环境未能取得 OTel 成立公告原文**"。规范版本按 SemVer 管理，现行规范托管于 `opentelemetry.io/docs/specs/otel`（由官方仓库 README 给出）。
3. **推出背景**：2015-2019 年可观测领域出现"埋点标准碎片化"：OpenTracing（侧重分布式追踪 API）与 OpenCensus（Google 主导，含指标与追踪）两套标准并行，加上各 APM 厂商私有 SDK，导致应用代码被单一厂商绑定——换后端就要重写埋点。同时微服务与多语言栈普及，"同一系统用 Go/Java/Python/Node 混写"成为常态，跨语言追踪上下文传递成为刚需。行业需要一个**中立于厂商、跨语言、覆盖多信号**的标准。
4. **解决的问题**：
   - 埋点与后端强耦合，厂商锁定（换后端需重写代码）
   - 多语言栈下 SDK 语义不一致，行为不可预期
   - 追踪/指标/日志三套 API 各自为政
   - 缺少跨语言的资源与语义约定，导致同一概念命名各异、无法关联
   - 采集侧需为每个后端维护一套导出器
5. **技术原理**：OpenTelemetry 规范的技术结构可分四层：① **API 层（跨语言一致）**——官方 README 明确其规范"describes the **cross-language** requirements and expectations for all OpenTelemetry implementations"，这是 OTel 与"某厂商 SDK"的根本差异：API 语义跨语言统一，因此同一份埋点概念在 Java/Go/Python 中行为等价；② **SDK 层**——提供 API 的参考实现（含采样、批处理、资源探测），把"何时采样、如何批量导出"等工程决策标准化；③ **数据模型层（含 Semantic Conventions 语义约定）**——定义 trace/span、metric、log、resource、baggage 的统一结构与属性命名，是"跨信号关联"与"跨厂商互操作"的前提；④ **传输层 OTLP**——标准线协议与编码（gRPC/HTTP），使导出器与后端解耦；规范随发行版管理：官方 README 明确"Changes to the specification are versioned according to **Semantic Versioning 2.0**"，且"Specific implementations of the specification should specify which version they implement"，并提供**各语言实现的一致性矩阵**（Compliance of Implementations with Specification）与里程碑。此外 OTel 提供 **Profiles 信号**（第四类信号，见 2.10.4）。**推断边界**：官方 README 为治理/流程性文本，**未在本稿取证范围内**给出 API/SDK 的详细设计规格（需读 `specification/` 目录 markdown 原文）；本稿对四层结构的归纳基于 README 明示内容 + OTel 通用架构认知，**分层细节属推断**，第2轮修订应以规范正文（`opentelemetry.io/docs/specs/otel`）逐条替换。
6. **技术效果**：**官方 README 未给出量化数据**。可验证的治理事实：规范按 SemVer 版本化；存在各语言实现的一致性矩阵；技术委员会与规范会议每周二 8AM PT 常态化运行。
7. **落地情况**：已商用/广泛落地（CNCF 体系内的行业标准；Datadog、New Relic、Elastic、Dynatrace、IBM Instana、Splunk、Grafana 等 10 家厂商**均提供 OTel 接入路径**，本稿在 2.1/2.3/2.5/2.7/2.10.1 中分别取证到官方 OTel 支持表述）。规范仓库为 Apache-2.0。
8. **案例**：官方来源缺失：本项目为标准/规范类项目，其"案例"形态应为厂商或企业的 OTel 采用案例；本环境未能取得 OTel 官方 adopters 列表页，故本条目案例字段声明缺失。**替代锚点**：Elastic 官方文档明确推荐"use Elastic OpenTelemetry to collect application telemetry data"（见 2.5.1），可作为"OTel 被商业厂商作为首选接入路径"的**厂商侧官方证据**。
9. **来源**：
   - 官方来源（必须）：
     - [OpenTelemetry Specification（官方 GitHub 仓库）](https://github.com/open-telemetry/opentelemetry-specification) — 日期：官方未标注（2026-09-12 确认；仓库为持续更新）— 官方 GitHub
     - [OpenTelemetry 官方规范托管地址](https://opentelemetry.io/docs/specs/otel) — 日期：官方未标注（链接由官方仓库 README 给出）— 官方文档
     - [OpenTelemetry 官方博客 RSS](https://opentelemetry.io/blog/index.xml) — 抓取于 2026-09-12 — 官方博客 RSS
     - [OpenTelemetry 项目状态页](https://opentelemetry.io/status/) — 日期：官方未标注（链接由官方仓库 README 给出）— 官方文档
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.10.2 OpenTelemetry - OpenTelemetry Collector（统一采集与处理管道）

1. **技术类别**：传统技术（采集中间件 / 处理管道）
2. **首次发布/关键版本时间**：官方未在仓库 README 标注首次发布日期。OTel Collector 随 OTel 项目（2019-05 成立）逐步成形，**推断为 2019-2020 年间提供可用的 collector 实现**（C 级推断）。
3. **推出背景**：**官方 README 明确给出的背景**："it removes the need to run, operate and maintain **multiple agents/collectors** in order to support open-source telemetry data formats (e.g. Jaeger, Prometheus, etc.) to multiple open-source or commercial back-ends." 即 2019 年前后企业面对的现实是：一个环境里同时运行 Jaeger Agent、Prometheus Exporter、各厂商专有 Agent，每个都要独立运维、独立升级、独立配置，且数据格式互不兼容——"采集侧"本身成了成本和故障源。
4. **解决的问题**（据官方 README 的 Objectives）：
   - 消除多 Agent/Collector 并存的运维负担
   - **Usable**：合理的默认配置、支持流行协议、开箱即用
   - **Performant**：在不同负载与配置下保持高稳定性与性能
   - **Observable**：自身是可观测服务的范例（自监控）
   - **Extensible**：不修改核心代码即可定制
   - **Unified**：单一代码库，可作为 agent 或 collector 部署，支持 traces、metrics、logs
5. **技术原理**：OTel Collector 的架构是标准的**管道（pipeline）模型**：**Receiver（接收）→ Processor（处理）→ Exporter（导出）**，由 **Service** 段把三者按信号类型（traces/metrics/logs）组装成 pipeline。官方 README 的关键设计声明有四点：① **厂商中立实现**——"offers a **vendor-agnostic** implementation on how to **receive, process and export** telemetry data"，即它不是一个后端，而是后端之上的统一管道；② **双形态部署**——官方明确"Single codebase, deployable as an **agent or collector**"，agent 形态贴近数据源（在节点/设备侧做边缘预处理），collector 形态做集中汇聚与再分发；这一点对用户有直接价值：**交换机内嵌 Agent 可用 OTel Collector 的 agent 形态做边缘聚合与批处理，再由上游 collector 汇聚**；③ **单代码库统一三信号**——官方明确支持 traces, metrics and logs（后续另有 Profiles 信号接入的努力）；④ **可扩展而无需改核心**——通过组件化（自定义 receiver/processor/exporter）扩展；⑤ **自监控**——官方提供 internal telemetry 文档，用于监控 Collector 自身（`Monitoring` 链接指向 `internal-telemetry`）。此外 Collector 有正式的 SIG 治理（每周例会、CNCF Slack `#otel-collector`），说明其工程成熟度。**推断边界**：官方 README 为项目介绍，**未给出**具体组件的完整清单、单实例吞吐、内存模型；本稿不列出未取证的组件名单。
6. **技术效果**：**官方 README 未给出量化数据**（无吞吐/内存/延迟数字）。官方给出的定性目标为"Highly stable and performant under varying loads and configurations"。
7. **落地情况**：已商用/广泛落地（OTel 生态核心组件；Grafana、Elastic、Datadog、New Relic 等均支持 OTLP 接入 Collector 数据）。治理结构完备（SIG + 例会 + Slack）。
8. **案例**：官方来源缺失：本环境未能取得 OTel Collector 的官方采用方案例（客户名+场景+结果+时间），故声明缺失。
9. **来源**：
   - 官方来源（必须）：
     - [OpenTelemetry Collector（官方 GitHub 仓库）](https://github.com/open-telemetry/opentelemetry-collector) — 日期：官方未标注（2026-09-12 确认；仓库持续更新）— 官方 GitHub
     - [OpenTelemetry Collector 官方配置文档](https://opentelemetry.io/docs/collector/configuration/) — 日期：官方未标注（链接由官方仓库 README 给出）— 官方文档
     - [OpenTelemetry Collector 内部遥测（自监控）官方文档](https://opentelemetry.io/docs/collector/internal-telemetry/) — 日期：官方未标注（链接由官方仓库 README 给出）— 官方文档
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.10.3 OpenTelemetry - W3C Trace Context（分布式追踪上下文传播标准）

1. **技术类别**：传统技术（跨厂商追踪上下文协议标准）
2. **首次发布/关键版本时间**：`日期：官方未标注（w3.org 被 Cloudflare 人机校验拦截，正文不可读，2026-09-12 确认）`。**本轮处置（Leader 裁决 F + B-R1-07）**：① **W3C 页面本轮实测仍返回 `Just a moment... / Enable JavaScript and cookies to continue`（cf_chl 反爬页），正文与 Recommendation 日期不可读**；② 按 Leader 裁决，**不得编造日期**——因此本字段**不再写"2021-11"或"2021-11-23"作为已证实日期**，只保留 `官方来源缺失：w3.org 被 Cloudflare 人机校验拦截` 的声明；③ 作为替代与佐证，本轮**已实测取得 OpenTelemetry 官方 Context Propagation 文档（HTTP 200、正文完整）**，该文档逐字给出 W3C Trace Context 的 `traceparent` 头格式，见字段 5 与字段 9。
   - **补充说明（不构成日期证据）**：第 1 轮评审 AI 在其报告中记载"W3C 实际 Rec 日期为 **2021-11-23**"，并注明其**同样未能通过 HTTP 通道读取 w3.org 正文**；本稿**不将该日期作为已证实事实**，仅登记为"评审AI 独立记载、待可达环境下复核"。
3. **推出背景**：分布式追踪的核心机制是**上下文传播**——把 trace ID/span ID 通过 HTTP 头（或消息头）在服务间传递，使跨进程的调用能被串成一条 trace。2015-2020 年各厂商与开源项目各用私有头（如 Zipkin 的 `X-B3-TraceId`、厂商自定义头），导致**跨技术栈的追踪在边界处断裂**：一条链路走经两个不同厂商的组件时 trace 无法拼接，根因分析在最关键的地方失明。行业需要一个 HTTP 层的事实标准头。
4. **解决的问题**：
   - 跨厂商/跨语言追踪在服务边界断裂，无法端到端串联
   - 私有头并存导致同一请求产生多条互不相连的 trace
   - 缺少标准化的追踪状态（如供应商特定数据）携带机制
   - 迷雾（分布式追踪）在网关、代理、消息队列处丢失上下文
   - 使可观测后端可以互换而不破坏链路完整性
5. **技术原理**（**v1.1 重写：机制描述已由"领域常识"升级为 OpenTelemetry 官方文档原文支撑**）：W3C Trace Context 定义两个 HTTP 头：① **`traceparent`**——携带版本号、trace-id（128-bit）、parent-id（即父 span 的 span-id，64-bit）与 trace-flags（如 sampled 标志），使接收方能够**加入同一条 trace** 并决定是否采样；② **`tracestate`**——一个有序的键值列表，用于携带**供应商特定的追踪状态**，允许多个系统在链路上各自附加信息而不互相冲突。
   **官方原文佐证（OpenTelemetry 官方文档，本轮实测 HTTP 200）**：`https://opentelemetry.io/docs/concepts/context-propagation/` 逐字给出：
   - "**OpenTelemetry maintains several official propagators. The default propagator uses the headers specified by the [W3C TraceContext](https://www.w3.org/TR/trace-context/) specification.**"（即 OTel 默认传播器就是 W3C Trace Context 头，**这正是"跨厂商追踪能串起来"的规范基础**）
   - traceparent 字段结构原文：**"`<version>-<trace-id>-<parent-id>-<trace-flags>`"**，并给出示例 **"`00-a0892f3577b34da6a3ce929d0e0e4736-f03067aa0ba902b7-01`"**（版本 00 / 32 位十六进制 trace-id / 16 位十六进制 parent-id / trace-flags 01）——**与本条目字段 5 的结构描述逐字一致**；
   - 传播机制原文："**Propagation is the mechanism that moves context between services and processes. It serializes or deserializes the context object and provides the relevant information to be propagated from one service to another.**"；
   - 该标准带来的能力原文：上下文传播使 traces "build **causal information** about a system across services that are arbitrarily distributed across process and network boundaries"，并使 logs 与 traces 自动关联（"OpenTelemetry SDKs are able to **automatically correlate logs with traces**"）、metrics 可按上下文聚合（例："`POST /cart/add > GET /product` 平均响应时间 130ms" 对比 "`* > GET /product` 300ms"）。
   **工程价值**：它是 **OpenTelemetry 的默认上下文传播格式**，因此 OTel 的跨语言一致性在传输层有了共同锚点；同时因为它被主流网关、代理、Service Mesh 采纳，追踪可以在"未插桩的中间组件"上透传，从而填补链路缺口。规范的非法/畸形头处理行为（忽略无效 traceparent 而不中断请求）**本轮仍未取得 W3C 原文**，故**降级为"待核验"**（见字段 7）。
   **推断边界（v1.1 收缩后）**：**仍未能取证 W3C 规范正文原文**（Cloudflare 拦截），因此 W3C 侧关于 `tracestate` 的有序性规则、畸形头处理的精确定义**属未取证**；但 `traceparent` 的字段结构与"OTel 默认采用 W3C 头"这两点**已由 OTel 官方文档原文支撑**，不再是 C 级领域常识。
6. **技术效果**：`官方来源缺失（W3C 页面被 Cloudflare 拦截）`。**可用的官方佐证（OpenTelemetry 侧）**：OTel 官方文档明确其**默认传播器使用 W3C TraceContext 规范定义的头**，并给出 `traceparent` 的字段结构与示例——这是"该标准被 OTel 实际采用"的官方（A/S 级）证据，但**不等于 W3C 官方的实现状态/采用情况报告**。
7. **落地情况**：**部分取证**：① **OTel 官方文档确证**其为 OTel **默认传播器**（"The default propagator uses the headers specified by the W3C TraceContext specification"）；② 关于"主流 Service Mesh 与网关支持"这一点，**本环境未取得 S/A 级证据**，故**由 v1.0 的"推断为事实标准"降级为"待核验"**：`待核验：未取得 Service Mesh/网关官方支持 W3C Trace Context 的页面证据`。
8. **案例**：`官方来源缺失：w3.org 被 Cloudflare 人机校验拦截（W3C 为标准组织，其"案例"形态应为各实现方的采用声明；本环境未取得任何带客户名的具名采用案例）`。OTel 官方文档中的 `Frontend → Product Catalog` 为**文档示例（example），非客户案例**，不作案例登记。
9. **来源**（**v1.1 更新：按 Leader 裁决 F 与 B-R1-07 增设 OpenTelemetry 官方 Context Propagation 作为佐证来源；同时保留 W3C 标准条目本身，不丢失"W3C 标准"这一标准化事实**）：
   - 官方来源（必须）：
     - **[Context propagation（OpenTelemetry 官方文档，本轮实测 HTTP 200 且正文完整）](https://opentelemetry.io/docs/concepts/context-propagation/)** — 日期：官方未标注（2026-09-12 确认；含 "The default propagator uses the headers specified by the W3C TraceContext specification" 与 `<version>-<trace-id>-<parent-id>-<trace-flags>` 原文）— 官方文档
     - [W3C Trace Context（官方标准页，**正文被 Cloudflare 拦截未能读取**）](https://www.w3.org/TR/trace-context/) — **官方来源缺失：w3.org 被 Cloudflare 人机校验拦截，正文与 Recommendation 日期不可读（2026-09-12 实测；返回 "Just a moment... / Enable JavaScript and cookies to continue"）** — 官方标准（W3C TR）
     - [OpenTelemetry Specification（官方 GitHub 仓库，OTel 侧对上下文传播的规范要求）](https://github.com/open-telemetry/opentelemetry-specification) — 日期：官方未标注（2026-09-12 确认）— 官方 GitHub
   - 非官方来源（可选，仅用于原理补充）：
     - 无
   - **缺口登记（v1.1 更新）**：字段 **2、6、7、8、9（W3C 正文级）** 仍不达标；但**字段 5 已由 C 级领域常识升级为 OTel 官方文档原文支撑**，v1.0 "本条目的证据等级为本稿最低之一"的判断**已部分改善**。**处置：本条目保留（不替换为 OTel 条目），并新增 OTel Context Propagation 为佐证来源**——该做法同时满足 Leader 裁决 F（采用 OTel 文档、保留 W3C 缺失声明、不编造日期）与第 1 轮评审 B-R1-07（不因替换而丢掉"W3C 标准"这一事实）。

#### 2.10.4 OpenTelemetry - opentelemetry-ebpf-profiler（eBPF 无侵入跨语言持续剖析）——AI技术

> **本条为全稿与用户场景最直接相关的技术条目**：用户在 Linux 交换机内以 C/C++ + eBPF 做采集，本项目正是"用 eBPF 做内核态、无侵入、跨语言 profiling"的官方参考实现。

1. **技术类别**：传统技术（内核态 eBPF 采集/剖析）+ AI技术（AI增强：为 AI 调查与根因分析提供代码级信号；且作为 OTel Profiles 信号的采集端）
2. **首次发布/关键版本时间**：官方仓库未标注首次发布日期。本项目源于 **Polar Signals 的 parca-agent**（该技术由 Elastic 收购 Parca 团队后贡献给 OpenTelemetry，成为 `open-telemetry/opentelemetry-ebpf-profiler`）；官方 README 说明其"implements a whole-system, cross-language profiler for Linux via eBPF"。**精确日期官方缺失**，标注"官方未明确（仓库 README 无发布日期；据项目沿革推断为 2023-2024 年进入 OTel 组织）"。
3. **推出背景**：**官方 README 直接给出了硬性工程背景**：该项目明确列出**支持的内核版本门槛随提交演进**——commit `8047150e` 是最后一个支持内核 **5.4** 的提交，之后的改动可能要求**内核 ≥5.10**；commit `7ddc23ea` 是最后一个支持内核 **4.19** 的提交，之后至少要求**≥5.4**。官方同时说明其内核版本策略是"与当前主流发行版（Debian stable、RHEL、Ubuntu LTS、Amazon Linux、SUSE Linux）提供的最低内核版本保持一致"。这**精确印证了用户场景的核心约束**：eBPF 可观测性的能力边界由内核版本决定，在交换机等长期不升级内核的嵌入式环境中，**内核版本是第一设计约束**。此外其背景还包括：生产环境 profiling 需要"不重启、不加载库、不需调试符号"。
4. **解决的问题**（据官方 README 的 Core features）：
   - 需在生产环境做**全系统、跨语言**剖析
   - **极低开销**：官方给出明确上界——"**1% CPU and 250MB memory are our upper limits in testing**"
   - **无 DWARF 调试信息**也能剖析原生 C/C++ 可执行文件（借助 `.eh_frame` 数据）
   - 无帧指针、无调试符号也能剖析系统库
   - **混合栈**：从内核空间穿透未修改的系统库一直 unwind 到高级语言
   - 广泛语言支持：Hotspot JVM、Python、Ruby、PHP、Node.JS、V8、Perl、Erlang、.NET
   - **100% 非侵入**：无需向被剖析进程加载任何 agent 或库
   - **无需重配置/插桩/重启** HLL 解释器与 VM（默认配置下即可 unwind 各语言）
   - **ARM64** 全 unwind 器支持
   - 支持原生 inline frames（洞察编译器优化、提高调用链精度）
5. **技术原理**：该 profiler 的技术路线是**"eBPF 内核态采样 + 用户态符号化/栈展开"**：① **采样点在内核**——通过 eBPF 在内核侧周期性采样（perf event / 定时器触发），采集用户态与内核态栈，因此对目标进程**零侵入**（不注入、不挂钩用户代码）；② **栈展开（unwinding）**——难点在于 unwinding 需要知道每个运行时的栈布局。项目通过**针对各 HLL 的专用 unwind 器**实现默认配置下的多语言栈展开（官方明确"the agent supports unwinding each of the supported languages **in the default configuration**"）；③ **无调试符号路径**——对原生 C/C++ 使用 **`.eh_frame`** 数据代替 DWARF 调试信息来 unwind（官方引用专利 [US11604718B1](https://patents.google.com/patent/US11604718B1/en)），从而**避免在生产环境部署调试符号**；④ **混合栈拼接**——把内核栈、系统库栈与语言运行时栈拼成一条完整调用链（官方："stacktraces go from Kernel space through unmodified system libraries all the way into high-level languages"）；⑤ **inline frames**——支持原生内联帧，提升调用链精度并反映编译器优化；⑥ **信号接入 OTel**——官方明确"Implements the **Alpha OTel Profiles signal**"（引用 `opentelemetry-proto` PR 775），即它把剖析数据以 OTel Profiles 信号表达，从而**与 traces/metrics/logs 在同一数据模型下关联**，这是相对早期私有 profiler 的关键跨越。**推断边界**：官方 README 未给出采样频率、perf 事件类型、ring buffer 设计、符号解析（是否使用 build-id 服务）与多语言 unwind 的完整算法；本稿不作断言。**内核约束的工程含义（本稿推断）**：内核 ≥5.10 的要求意味着**RHEL 8（4.18 内核）/ 老版本嵌入式内核无法使用该项目**，用户在设计交换机侧 Agent 时必须先确认目标内核版本，或为低版本内核准备降级方案（这也是本稿第5章 P0 建议的来源）。
6. **技术效果**：**官方给出明确的量化上界**（本项目是全稿量化数据最硬的一条）："**Very low CPU and memory overhead (1% CPU and 250MB memory are our upper limits in testing and the agent typically manages to stay way below that)**"。同时给出可验证的能力覆盖：支持 Hotspot JVM、Python、Ruby、PHP、Node.JS、V8、Perl、Erlang、.NET 及原生 C/C++/Rust/Zig/Go（无调试符号）；支持 ARM64。
7. **落地情况**：开源项目（OpenTelemetry 官方组织下，`open-telemetry/opentelemetry-ebpf-profiler`）。成熟度标注为 **Alpha**（OTel Profiles 信号为 Alpha）。作为 Grafana Alloy / Pyroscope 生态的 eBPF 采集路径之一被业界采用（此点本稿未取得 Grafana 官方原文佐证，**不作为已证实事实**）。
8. **案例**：官方来源缺失：本项目为开源组件，本环境未能取得 OTel 官方的采用方案例（客户名+场景+结果+时间）。**可用的官方事实锚点**：官方 README 明确给出**量化性能上界（1% CPU / 250MB 内存）**与**内核版本门槛（5.4/5.10）**，属于"技术效果与约束"而非客户案例，故本字段仍声明缺失。
9. **来源**：
   - 官方来源（必须）：
     - [OpenTelemetry eBPF Profiler（官方 GitHub 仓库）](https://github.com/open-telemetry/opentelemetry-ebpf-profiler) — 日期：官方未标注（2026-09-12 确认；README 明确内核版本门槛提交与量化开销上界）— 官方 GitHub
     - [OTel Profiles 信号 proto 定义（官方 PR 775，由 README 引用）](https://github.com/open-telemetry/opentelemetry-proto/pull/775) — 日期：官方未标注（链接由官方 README 给出）— 官方 GitHub
   - 非官方来源（可选，仅用于原理补充）：
     - [US11604718B1 专利（使用 .eh_frame 而非 DWARF 展开原生栈，由官方 README 引用）](https://patents.google.com/patent/US11604718B1/en) — 日期：官方未标注（链接由官方 README 给出）— 专利文献
     - OTel 官方博客：[Inside the LLM Call: GenAI Observability with OpenTelemetry](https://opentelemetry.io/blog/2026/genai-observability/) — 2026-09-07 — 官方博客（用于说明 OTel GenAI 语义约定方向，超出 2015-2025 窗口，作延伸注记）

#### 2.10.5 OpenTelemetry/eBPF 系 - Pixie（Kubernetes 原生 eBPF 无埋点可观测）

1. **技术类别**：传统技术（eBPF 无侵入采集 + 集群内边缘计算）
2. **首次发布/关键版本时间**：`官方未明确精确首次发布日期`（官方仓库 README 未标注）。**收购年份的统一处置（B-R1-15 / B-R1-08 ②）**：本稿**统一采用 `2020-12`** 并标注为 **`据公开报道，未取得官方来源`** —— v1.0 的 §1 总览表曾写"**2022 收购 Pixie** 技术整合"、而 §2.10.5 写"**2020-12** 被 New Relic 收购"，**同一文档两处互斥**；v1.1 已把 §1 总览表与 §2.10.5 **统一为 2020-12【据公开报道，未取得官方来源】**。
   - **本轮反证尝试（实测，如实登记）**：按 New Relic 官方新闻稿 URL 规则 `press-release/YYYYMMDD` 试探 `https://newrelic.com/press-release/20201209` → **404**（与第 1 轮评审 AI 的试探结果一致）；故**该日期无法通过官方发布页证实**，本稿**不作已证实事实使用**，仅作背景性表述并带不确定性标记。
3. **推出背景**：**官方 README 给出明确背景**：Pixie 定位为"open-source observability tool for Kubernetes applications"，解决的痛点是——在 K8s 中要看"集群的高层状态（服务地图、集群资源、应用流量）"又要"下钻到细节（Pod 状态、火焰图、单条完整请求体）"，传统方案要求**改代码埋点**或**旁路抓包 + 集中上传**，前者侵入性高、后者数据出境与成本高。Pixie 的立论是：**用 eBPF 自动采集 + 在集群内就地计算**，从而既无侵入又不把原始数据集中外传。
4. **解决的问题**（官方 README 的 "Why Pixie?" 三点）：
   - **Auto-telemetry**：无需埋点自动采集遥测（full-body requests、资源与网络指标、应用 profiles 等）
   - **In-Cluster Edge Compute**：数据在集群内采集、存储、查询，不外传原始数据
   - **Scriptability**：用 PxL（Pythonic 查询语言）在 UI/CLI/API 中统一查询
   - 网络层可见性：集群内网络流量流向、DNS 请求流与单条 DNS 请求/响应全文、TCP 丢包与重传地图
   - 基础设施健康：Pod/Node/Namespace 资源使用、每 Pod/Node 的 CPU 火焰图
   - 服务性能：服务间流量流、服务与端点延迟、单服务最慢请求抽样
   - 数据库查询剖析：多协议数据库请求的延迟/错误/吞吐（LET）分析
5. **技术原理**：官方 README 明确了三大技术支柱：① **eBPF 自动遥测**——"Pixie uses **eBPF** to automatically collect telemetry data such as **full-body requests**, resource and network metrics, application profiles, and more"。其关键能力是**在内核态解析应用层协议**（官方列出支持多种协议与数据库协议），因此能拿到**完整的请求/响应体**而无需修改应用——这与 Datadog USM（2.1.1，解析 HTTP(S) 得 RED 指标）同族，但 Pixie 的粒度更深（full-body）。② **集群内边缘计算**——"Pixie collects, stores and queries all telemetry data **locally in the cluster**"，这是**边缘预处理范式的商业实现**：数据不集中外传，查询在本地完成；官方给出资源上界"**uses less than 5% of cluster CPU and in most cases less than 2%**"。③ **PxL 可编程查询**——Pythonic 查询语言，可在 UI、CLI 与客户端 API 中复用，使用户能自定义分析逻辑（而非受限于固定面板）。**推断边界**：官方 README **未公开** eBPF 程序的具体挂载点（kprobe/uprobe/tracepoint/TC）、协议解析实现、数据保留窗口与存储引擎；本稿不作断言。**与用户场景的工程映射（本稿推断）**：Pixie 的"**在数据产生地就地计算，只上有价值的结果**"是用户在交换机资源受限环境做**边缘预处理**时最直接的设计参照——交换机侧同样应避免原始数据全量上送，而应在设备内完成协议解析与指标聚合。
6. **技术效果**：**官方给出量化上界**："Pixie uses **less than 5% of cluster CPU and in most cases less than 2%**"（官方 README）。能力覆盖：full-body 请求、资源/网络指标、应用 profile、火焰图、TCP 丢包/重传、DNS 全量请求响应、多协议数据库 LET 分析。
7. **落地情况**：开源项目（CNCF 生态，`pixie-io/pixie`；被 New Relic 收购后持续开源）。规模数据未取证。
8. **案例**：官方来源缺失：本环境未能取得 Pixie 的具名客户案例（客户名+场景+结果+时间），故声明缺失。
9. **来源**：
   - 官方来源（必须）：
     - [Pixie（官方 GitHub 仓库）](https://github.com/pixie-io/pixie) — 日期：官方未标注（2026-09-12 确认；README 给出 <5%/<2% CPU 上界与三大特性）— 官方 GitHub
     - [Pixie 官方数据源文档（由 README 引用）](https://docs.px.dev/about-pixie/data-sources/) — 日期：官方未标注（链接由官方 README 给出）— 官方文档
     - [PxL 官方参考（由 README 引用）](https://docs.px.dev/reference/pxl/) — 日期：官方未标注（链接由官方 README 给出）— 官方文档
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.10.6 OpenTelemetry/eBPF 系 - Cilium Hubble（eBPF L3-L7 网络可观测与服务依赖图）

1. **技术类别**：传统技术（eBPF 网络可观测 / 流级遥测 / 服务地图）
2. **首次发布/关键版本时间**：官方文档未标注首次发布日期（本稿取证的是 Cilium **1.20.1** 文档版本）。Hubble 随 Cilium 演进，**推断为 2019-2020 年间引入**（Cilium 1.8 前后；**C 级推断，官方发布日期缺失**）。
3. **推出背景**：**官方文档给出的技术背景**：Cilium 本身是基于 eBPF 的 K8s 网络/安全/可观测数据平面，Hubble 是其可观测组件。背景痛点是——传统网络可观测（如 tcpdump/NetFlow）只能看到 **L3/L4 的包与流**，无法回答"**是哪个服务的哪个 HTTP/gRPC 端点调用失败了**"；而应用层可观测（APM）又要求每个服务埋点。二者之间的鸿沟导致 K8s 中"网络问题"与"应用问题"难以区分。此外多集群（Cluster Mesh）场景缺少跨集群统一视图。
4. **解决的问题**（官方文档表述）：
   - 对服务通信与网络基础设施提供**完全透明（transparent）**的深度可见性
   - 支持**节点级、集群级、乃至跨集群（Multi-Cluster / Cluster Mesh）**的可见性
   - 自动发现服务依赖图（L3/L4 **乃至 L7** 层）
   - 提供 CLI 与 UI 两种查询方式（含过滤）
   - 支持加密流量过滤、Reply 流量过滤
   - 通过 Hubble exporter 导出指标，并支持性能调优、动态导出配置
   - 支持 Hubble API 的 TLS 与认证
5. **技术原理**：据官方文档，Hubble 的架构分三层：① **数据面（eBPF）**——由 **Cilium agent** 在节点上用 eBPF 采集网络流与协议事件，官方明确"Observability is provided by Hubble which enables deep visibility into the communication and behavior of services as well as the networking infrastructure in a **completely transparent** manner"。② **API 与中继（Relay）**——**默认情况下 Hubble API 的作用域是 Cilium agent 所在节点**，即单节点可见性；Hubble CLI 通过**本地 Unix Domain Socket** 查询 Hubble API，且 Hubble CLI 二进制**默认安装在 Cilium agent Pod 中**。当部署 **Hubble Relay** 后，可见性扩展到**整个集群甚至 Cluster Mesh 多集群**，此时 CLI 指向 Relay Service 或使用 Hubble UI。③ **消费层（UI / 指标导出）**——**Hubble UI** 提供 Web 界面，官方明确其能做"**automatic discovery of the services dependency graph at the L3/L4 and even L7 layer**"，以服务地图形式可视化与过滤数据流；**Hubble exporter** 把流数据导出为指标（支持性能调优与动态导出配置），从而接入 Prometheus/Grafana 体系。此外官方提供 TLS 配置与 API 认证（安全问题在生产部署中不可回避）。**推断边界**：官方文档**未公开** eBPF 程序的具体 hook 类型（TC/XDP/kprobe）、L7 解析支持的协议全集、单节点吞吐上限与资源开销；本稿不作断言。**与用户场景的映射**：Cilium 运行在**节点内核**且以 eBPF 实现 L3-L7 可观测 + 服务依赖图，这与用户"在 Linux 交换机内部用 eBPF（TC/XDP）做流级可观测"在技术栈上**几乎完全同构**，是第5章建议中"流级遥测 + 服务依赖图"的直接技术来源。
6. **技术效果**：官方文档给出的是**能力范围**（节点/集群/多集群三级可见性、L3/L4/L7 服务依赖图、CLI/UI 双入口、指标导出、TLS 认证），**官方未给出量化数据**（如 CPU 开销百分比、可处理流速率）。
7. **落地情况**：已商用/广泛落地（Cilium 为 K8s 网络事实标准之一，Hubble 为其内置可观测组件；官方文档版本 1.20.1）。规模数据未取证。
8. **案例**：官方来源缺失：本环境未能取得 Hubble 的具名客户案例（客户名+场景+结果+时间），故声明缺失。
9. **来源**：
   - 官方来源（必须）：
     - [Network Observability with Hubble — Cilium 1.20.1 documentation](https://docs.cilium.io/en/stable/observability/hubble/) — 日期：官方未标注（2026-09-12 确认；文档版本 1.20.1）— 官方文档
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.10.7 OpenTelemetry/eBPF 系 - Cilium Tetragon（eBPF 安全可观测与运行时策略执行）

1. **技术类别**：传统技术（eBPF 安全可观测 / 运行时事件）
2. **首次发布/关键版本时间**：官方 README 未标注发布日期。Tetragon 是 Cilium 相对较新的组件，**官方 README 称其为"Cilium's new Tetragon component"**，据此推断为 **2021-2022 年间公开**（C 级推断）。
3. **推出背景**：**官方 README 给出的背景**：Cilium 在 L3/L4 网络与 L7 协议可见性之外，需要一个能回答"**这个 Pod 里到底执行了什么进程、做了哪些系统调用、访问了哪些文件**"的组件——即从"网络行为"深入到"**进程与系统调用行为**"。这类信号既是安全可观测的核心（检测异常进程执行、敏感文件访问），也是运行时策略执行的基础。同时该信号必须**具备 K8s 身份感知**（知道事件属于哪个 namespace/pod），否则无法在动态环境中定位责任主体。
4. **解决的问题**（官方 README 表述）：
   - 检测并**响应**安全显著事件：**进程执行事件**、**系统调用活动**、**I/O 活动（含网络与文件访问）**
   - **K8s 身份感知**：理解 namespace、pod 等 K8s 身份，使安全事件检测可**按工作负载（workload）配置**
   - 提供默认事件流：`process_exec` 与 `process_exit` 实现**完整进程生命周期可观测**
   - 提供通用追踪：`process_kprobe`、`process_tracepoint`、`process_uprobe` 事件，支持更高级的自定义场景
   - 支持运行时策略（TracingPolicy）配置，并按用例扩展（如网络可观测）
5. **技术原理**：据官方 README，Tetragon 的技术机制分四层：① **内核 hook 层（sensors）**——"Tetragon is able to observe **critical hooks in the kernel through its sensors** and generates events enriched with Linux and Kubernetes metadata"。官方明确列出的 hook 类型包括 **kprobe、tracepoint、uprobe**（对应 `process_kprobe` / `process_tracepoint` / `process_uprobe` 事件类型），即**覆盖内核函数、内核静态追踪点与用户态函数**三类挂载点。② **事件层**——默认产生 `process_exec` 与 `process_exit`，构成**完整进程生命周期**（谁启动了谁、何时退出）；通用追踪事件用于自定义深度观测。③ **元数据富化层**——事件被自动附加 **Linux 元数据与 Kubernetes 元数据**（因此能回答"这个 exec 属于哪个 pod"）；在 K8s 中 Tetragon 是 **Kubernetes-aware** 的。④ **策略与执行层**——通过 **TracingPolicy** 概念声明要观测什么（官方提供 use cases 如进程生命周期、网络可观测），并具备**运行时策略执行（Runtime Enforcement）** 能力——官方标题即"Security Observability **and Runtime Enforcement**"，即不只是看，还能拦。**推断边界**：官方 README **未公开**传感器实现细节（map 类型、ring/perf buffer、事件丢失处理）、性能开销与执行策略的阻断机制（是否 SIGKILL/deny）；本稿不作断言。**与用户场景的映射**：Tetragon 的 **kprobe/tracepoint/uprobe 三类挂载点**正是用户在交换机内做 eBPF 采集时最基础的选择面；其对"事件 + 元数据富化"的设计（把裸内核事件绑定到业务身份）值得直接借鉴——交换机侧同样需要把内核事件绑定到"端口/VLAN/业务"身份。
6. **技术效果**：官方 README 给出的是**事件类型与覆盖范围**（进程生命周期、系统调用、I/O、网络与文件访问），**未给出量化数据**（开销、事件吞吐、延迟）。
7. **落地情况**：开源项目（Cilium 组织下，`cilium/tetragon`；官方文档站 `tetragon.io`）。支持 K8s 与 Linux/Docker 两种入门路径（官方 getting-started 提供）。
8. **案例**：官方来源缺失：本环境未能取得 Tetragon 的具名客户案例（客户名+场景+结果+时间），故声明缺失。
9. **来源**：
   - 官方来源（必须）：
     - [Cilium Tetragon（官方 GitHub 仓库）](https://github.com/cilium/tetragon) — 日期：官方未标注（2026-09-12 确认）— 官方 GitHub
     - [Tetragon 官方文档](https://tetragon.io/docs/) — 日期：官方未标注（链接由官方 README 给出）— 官方文档
     - [Tetragon TracingPolicy 概念文档（由 README 引用）](https://tetragon.io/docs/concepts/tracing-policy/) — 日期：官方未标注（链接由官方 README 给出）— 官方文档
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.10.8 OpenTelemetry/eBPF 系 - Coroot（eBPF 零埋点可观测 + AI 根因分析）——AI技术

1. **技术类别**：AI技术（AI增强：AI 驱动根因分析 + 自动 inspection 规则）+ 传统技术（eBPF 零埋点采集）
2. **首次发布/关键版本时间**：官方仓库未标注发布日期。Coroot 为开源项目（活跃开发中），**推断为 2022-2023 年间公开**（C 级推断）。
3. **推出背景**：**官方 README 直接给出了立论**："**Collecting metrics, logs, and traces alone doesn't make your applications observable. Coroot turns that data into actionable insights for you!**"——这句话精确定义了 2022-2025 年可观测行业的核心痛点：**数据量与洞察量不成正比**。同时它指出另一个痛点：**遗留与第三方服务无法埋点**（官方："Are you unable to instrument legacy or third-party services? Coroot's eBPF-based instrumentation can capture requests **without requiring any code changes**"）。
4. **解决的问题**（据官方 README 的 Features）：
   - **零埋点可观测**：metrics/logs/traces/profiles 全部用 **eBPF** 自动采集
   - **服务地图覆盖 100% 系统、无盲点**（官方：Service Map covers 100% of your system with no blind spots）
   - **预定义 inspections** 对每个应用零配置审计
   - **应用健康摘要**：数百个服务下仍能快速理解状态；无需逐个人工看日志
   - **SLO 跟踪**与离群请求的分布式追踪探查、一键调查任意异常
   - **厂商中立埋点**：支持 OpenTelemetry（对能埋点的服务）
   - 日志模式（开箱即用的事件聚类）与 logs-to-traces 无缝关联、基于 ClickHouse 的快速搜索
   - 一键 profile 任意应用，把 CPU/内存尖峰分析到**代码行**
   - **Release（部署）追踪**：无需集成 CI/CD 即自动对比每次发布与上一版本的性能
   - **成本监控**：把云成本归因到具体应用
5. **技术原理**：官方 README 揭示了 Coroot 的三层设计：① **采集层：eBPF 全信号零埋点**——"Metrics, logs, traces, and profiles are gathered automatically by **using eBPF**"，并对无法埋点的遗留/第三方服务用 **eBPF-based instrumentation** 捕获请求（无需改代码）。这是"**采集侧去埋点**"的最彻底实现（连 profile 与 logs 也走 eBPF 路径）。② **分析层：预定义 inspection + AI 根因分析**——官方称 Coroot 内置"**Built-in expertise**"，能"**automatically identify over 80% of issues**"；当应用未达成 SLO 时，Coroot 会**发送单一告警，并附上全部相关 inspection 的结果**（这是告警收敛的具体机制：不是压缩条数，而是把结论与证据合并为一条）；inspection 可按应用或整个项目调整（**规则可配置、可解释**，而非黑盒模型）。③ **数据层：ClickHouse**——官方明确日志搜索基于 ClickHouse，说明其把 ClickHouse 作为统一的高性能分析存储。④ **交叉信号关联**——logs-to-traces 关联、SLO 异常一键跳到追踪、profile 到代码行、release 前后对比，构成"从异常到根因"的直线路径。⑤ **成本与发布维度**——把云成本与发布变更也纳入同一上下文，使"性能劣化"能被归因到"某次发布"与"某笔成本"。**推断边界**：官方 README **未公开**"80% 问题自动识别"的统计口径（样本来源、问题定义、评估方法），**该数字为厂商自述**；亦未公开 eBPF 挂载点、ClickHouse schema、inspection 规则全集与 AI 部分所用模型（**"AI-powered Root Cause Analysis"为官方仓库标题表述，未说明是规则引擎还是机器学习模型**）。**本条目是全稿中"用户 Server 端 AI 助手"最直接的对标对象**：它示范了"eBPF 零埋点采集 → 规则化 inspection → 单条告警带证据"的完整链路，且为开源实现可读源码。
6. **技术效果**：**官方给出量化主张**："Coroot can automatically identify **over 80% of issues**"、"Service Map covers **100%** of your system with no blind spots"（官方 README，**厂商自述，未给出评测方法**）。
7. **落地情况**：开源项目（`coroot/coroot`；官方文档 `docs.coroot.com`；提供 live demo 与 **Coroot Enterprise** 商业版）。规模数据未取证。
8. **案例**：官方来源缺失：本环境未能取得 Coroot 的具名客户案例（客户名+场景+结果+时间）；官方 README 提供 live demo 但非客户案例，故声明缺失。
9. **来源**：
   - 官方来源（必须）：
     - [Coroot（官方 GitHub 仓库）](https://github.com/coroot/coroot) — 日期：官方未标注（2026-09-12 确认；README 含 eBPF 采集、80% 问题识别、ClickHouse、SLO 单告警等表述）— 官方 GitHub
     - [Coroot 官方文档](https://docs.coroot.com/) — 日期：官方未标注（链接由官方 README 给出）— 官方文档
     - [Coroot 官方在线演示](https://demo.coroot.com/) — 日期：官方未标注（链接由官方 README 给出）— 官方产品/演示
   - 非官方来源（可选，仅用于原理补充）：
     - 无

#### 2.10.9 【未取证·生态提及】OpenTelemetry/eBPF 系 - groundcover（商用 eBPF K8s 可观测）

> **⚠️ 条目级未取证标记（v1.1 新增）**：本条目**无产品级 S/A 级官方来源**（仅有官方 GitHub 组织页与开源子仓库，属组织级 A 级证据），字段 2/3/4/5/6/8 不达标（9 字段完整度 **3/9**）。**处置**：保留为**生态提及**条目并加 `【未取证·生态提及】` 前缀；因 Leader 已明确允许"OpenTelemetry 生态可按项目拆分"，本条目**保留在有效技术条目数（34 条）内**，但其内容**不得作为任何论断或建议的依据**。

1. **技术类别**：传统技术（eBPF 无埋点采集）+ AI技术（厂商自述 AI/可观测能力，细节未取证）
2. **首次发布/关键版本时间**：`官方未明确【待核验】`。官方来源缺失：本环境未能取得 groundcover 的官方发布时间（`github.com/groundcover-com/groundcover` 返回 404，即**该项目主仓库非公开**；`github.com/groundcover-com` 组织页可达）。
3. **推出背景**：**官方来源缺失**。据其 GitHub 组织页自述"**Level up your k8s observability game with eBPF**"（官方组织页描述）与所在地 Israel，可确认其定位为"以 eBPF 为核心的 K8s 可观测厂商"，但**背景叙述未取得官方原文**，故不展开。
4. **解决的问题**（**仅据官方组织页与可见仓库推断，C 级**）：
   - K8s 环境下以 eBPF 实现无埋点可观测
   - 服务依赖图（据其开源仓库 `caretta`："**Instant K8s service dependency map, right to your Grafana**"）
   - 容器资源指标（据其开源仓库 `murre`："**Murre is an on-demand, scaleable source of container resource metrics for K8s**"）
   - 提供 CLI 工具便于操作（`cli`："groundcover's official CLI tool. Level up your K8s observability game with eBPF."）
   - 与 Grafana 生态集成（caretta 明确输出到 Grafana）、提供 Terraform Provider（`terraform-provider-groundcover`）
5. **技术原理**：**官方来源缺失（无公开主仓库可读）**。仅可确认的官方可见技术事实：① 其技术栈以 **eBPF** 为核心（组织页与多个仓库描述一致）；② 开源了 **caretta**（即时 K8s 服务依赖图，输出到 Grafana）、**murre**（按需可扩展的容器资源指标源）、**cli**、**loki-proxy**（Go 实现）、**terraform-provider-groundcover**；③ 主仓库为闭源商业产品（组织页显示 47 个仓库但主项目不在其中）。**推断边界**：因**无法读取其产品主仓库或官方文档**（`groundcover.com` 未在本轮抓取中确认可达路径），本条目**不能给出架构级原理描述**，仅列可验证的开源组件事实。**本条目的证据等级为本稿最低之一**（与 2.6.x Broadcom 同档）。
6. **技术效果**：官方来源缺失（无量化数据）。
7. **落地情况**：有限商用/闭源商业产品 + 部分组件开源（`caretta` 2.1k stars、`murre` 320 stars、`cli` 42 stars，据官方组织页实时数值，抓取于 2026-09-12）。
8. **案例**：官方来源缺失。
9. **来源**：
   - 官方来源（必须）：**部分可用（A 级，组织级）**：
     - [groundcover（官方 GitHub 组织页）](https://github.com/groundcover-com) — 日期：官方未标注（2026-09-12 确认；含组织自述与仓库清单）— 官方 GitHub
     - [caretta（官方开源仓库，K8s 服务依赖图）](https://github.com/groundcover-com/caretta) — 日期：官方未标注（链接由组织页给出）— 官方 GitHub
   - 非官方来源（可选，仅用于原理补充）：
     - 无
   - **缺口登记**：**官方来源缺失**：`https://github.com/groundcover-com/groundcover` 返回 404（主仓库非公开，已实测 2026-09-12）；未取得 groundcover 产品文档或新闻稿。字段 2/3/4/5/6/8 不达标，**P1 级缺口**。**处置建议**：Leader 在 00 号规范中已明确允许"OpenTelemetry 生态可按项目拆分"，故建议将 groundcover **降级为"生态提及"而非独立条目**，把条目配额补到证据充分的 Pixie / Hubble / Tetragon / Coroot / opentelemetry-ebpf-profiler（本稿 2.10.5-2.10.8 与 2.10.4 已满足）。

#### 2.10.10 Prometheus - 拉取式指标采集、多维数据模型与 PromQL

1. **技术类别**：传统技术（指标监控系统 / 时序数据模型 / 查询语言）
2. **首次发布/关键版本时间**：**2016 年加入 CNCF**（Prometheus 为 CNCF 第二个托管项目）。官方 GitHub README 未标注发布日期；本稿未取得 CNCF 官方公告原文，标注"据公开记录为 2016 年；**官方来源缺失：CNCF 接纳公告未取证**"。
3. **推出背景**：**官方 README 间接给出背景**：Prometheus 是由 SoundCloud 开源的系统与服务监控系统，其设计取向（多维数据模型、PromQL、单节点自治、HTTP 拉取）直接针对 2014-2016 年云原生环境的两大变化：① **实例数量与生命周期剧变**——容器与自动扩缩容使"主机/实例"不再是稳定标识，监控必须按**标签维度**（而非固定主机名）建模；② **服务发现成为必需**——目标由 K8s/Consul 等动态发现而非静态配置。传统监控（Zabbix/Nagios 类）以主机为中心、以插件轮询为机制、以静态阈值告警为输出，在这两点上都失配。
4. **解决的问题**（据官方 README 的 Features 列表）：
   - 需要**多维数据模型**（时间序列由 metric name + 键值维度定义）以支撑动态环境
   - 需要强大的查询语言（**PromQL**）来利用这种维度性
   - **不依赖分布式存储**，单个服务器节点自治（降低运维复杂度）
   - 采用 **HTTP 拉取（pull）模型**采集时序数据
   - 批处理任务（batch jobs）的推送需求通过**中间网关（Pushgateway）**支持
   - 目标通过**服务发现或静态配置**得到
   - 多种图形与仪表盘模式、层级与水平联邦（federation）
5. **技术原理**：Prometheus 的架构设计要点（据官方 README）：① **多维数据模型**——"time series defined by **metric name and set of key/value dimensions**"，这使同一指标可按 service/pod/endpoint 等维度切片，是动态环境可用的前提；② **PromQL**——官方描述为"a powerful and flexible query language to leverage this dimensionality"，用于告警规则、图形与联邦聚合；③ **拉取模型（pull over HTTP）**——由 Prometheus 主动按间隔抓取目标暴露的指标端点，优点是被监控端无状态（无需维护推送队列）、易于发现目标失效；批处理任务的短生命周期指标则通过 Pushgateway 中转；④ **单节点自治**——官方明确"No dependency on distributed storage; single server nodes are autonomous"，这带来极低的运维门槛（对比分布式时序数据库），代价是长期存储与水平扩展需靠远程写入/联邦补足；⑤ **服务发现驱动**——目标由 SD 动态获得，使容器环境无需人工登记；⑥ **联邦（federation）**——支持层级与水平联邦以聚合多实例。**推断边界**：官方 README 未给出存储引擎（TSDB）实现细节、压缩算法、单实例容量；本稿不作断言。**与用户场景的映射**：Prometheus 拉取模型在**交换机内嵌场景会遇到结构性挑战**——设备通常位于网络边缘、难以被中心侧主动拉取，且交换机资源受限不宜运行完整 Prometheus；因此用户更应关注 **Prometheus 生态的"推送/远程写入（remote write）"路径与 OpenMetrics 生态**，以及 **OTLP 作为统一上送协议**（见第5章 P1-1）。**注意**：本条目的"远程写入/OpenMetrics"未在本稿取证到官方页面，仅作为方向性提示，不构成条目事实。
6. **技术效果**：官方 README **未给出量化数据**（吞吐、内存、延迟）。可验证的能力事实：支持联邦、服务发现、多模式图形、Pushgateway 推送路径。
7. **落地情况**：已商用/广泛落地（CNCF 项目；云原生指标事实标准；Grafana Mimir、Thanos、VictoriaMetrics 等均在其生态内；本稿中 Grafana、Elastic 均以"Prometheus 兼容/对标"为卖点，见 2.5.3 与 2.8.x）。
8. **案例**：官方来源缺失：本环境未能取得 Prometheus 官方 adopters 案例（客户名+场景+结果+时间），故声明缺失。
9. **来源**：
   - 官方来源（必须）：
     - [Prometheus（官方 GitHub 仓库）](https://github.com/prometheus/prometheus) — 日期：官方未标注（2026-09-12 确认；README 含 Features 与架构描述）— 官方 GitHub
     - [Prometheus 官方文档站](https://prometheus.io/) — 日期：官方未标注（链接由官方 README 给出）— 官方文档
     - [Prometheus 官方下载页](https://prometheus.io/download/) — 日期：官方未标注（链接由官方 README 给出）— 官方文档
   - 非官方来源（可选，仅用于原理补充）：
     - 无

---

## 3. 横向技术演进时间线（传统 + AI 双轨）

### 3.1 主时间线表

| 年 | 传统技术里程碑 | AI 技术里程碑 | 驱动因素 |
|---|---|---|---|
| **2015** | 云原生监控雏形：Prometheus 生态扩散；传统 APM（AppDynamics/New Relic/Dynatrace）以 Agent 埋点为主流；ELK 成为日志分析事实标准；SolarWinds 以多工具矩阵覆盖网络/系统 | 无产品化 AI（AIOps 概念尚未普及，仅有静态阈值与简单基线） | 容器化与 DevOps 起步；微服务开始替代单体；SaaS 交付被接受 |
| **2016** | **Prometheus 加入 CNCF【待核验：未取得 CNCF/toc 官方接纳公告】**（第二个托管项目）；多维数据模型 + PromQL 被云原生采纳；Splunk ITSI 类"服务健康度"产品成形【待核验】 | CA 推出 Operational Intelligence（后为 Broadcom DX OI）【待核验，且⛔ Broadcom 整章已于 v1.1 降级，本半句不作为结论依据】；AIOps 第一波（关联 + 基线，非生成式）——**该判断现由 SolarWinds 官方产品页的 AIOps 表述与 Dynatrace 的因果 AI 路线共同支撑** | K8s 成为编排事实标准；实例生命周期缩短，传统以主机为中心的监控失配 |
| **2017** | **Cisco 收购 AppDynamics【待核验：未取得 Cisco 官方新闻稿】**（APM 进入网络厂商体系）；Dynatrace OneAgent 全栈自动发现成熟；分布式追踪（私有上下文头）普遍化 | 动态基线/异常检测进入 APM 产品（摆脱静态阈值） | 混合云成形；企业无法承受"一个故障跨多工具拼图" |
| **2018** | ⛔ **Broadcom 收购 CA Technologies（2018-11）【待核验；且该厂商整章已于 v1.1 降级为"证据不足的对照性附录"，见 §2.6 章首声明——本行不再作为结论依据】**；Elastic 从 ELK 向 Observability 演进 | 关联式 AIOps 成熟（跨域事件关联与告警压缩）；无生成式 AI | 云原生新贵上量，传统厂商转向存量客户与合规市场 |
| **2019** | **OpenTelemetry 成立（OpenCensus + OpenTracing 合并，2019-05）【待核验：未取得官方成立公告】**，埋点与后端解耦；Elastic Observability 解决方案成形（APM + Logs + Metrics + Uptime） | **Dynatrace Davis AI 品牌化【待核验：该 2019 时点未取得官方发布页；已由 2023-07-25 官方 IR 新闻稿确证的"Davis 扩展为超模态 AI"取代为可引用的 S 级锚点】**：确定性因果 AI（拓扑 + 因果，而非纯统计）；Instana 自动发现 + Dynamic Graph 差异化 | 厂商锁定引发反弹，行业需要中立标准；AI 告警误报导致信任危机，倒逼"因果"路线 |
| **2020** | **Datadog Continuous Profiler GA（2020-08-11，官方新闻稿，$12/host/月，客户 Cvent）【本轮修正：v1.0 曾误置于 2021-2022 与 2023】**；**New Relic 平台统一（Telemetry Data Platform + NRQL）【待核验：v1.0 依据的 sitemap lastmod 已废止】**；Grafana Loki 加入 LGTM 栈；**IBM 宣布收购 Instana（2020-11）【待核验】**；Pixie 开源（eBPF 自动遥测） | AIOps 与"可观测性（Observability）"术语交替；AI 仍以基线/异常检测为主 | 多产品数据孤岛成本显现；K8s 使"实例"不再是稳定标识；eBPF 内核能力成熟 |
| **2021** | **Datadog USM 发布（2021-10-26，eBPF 解析内核网络栈得 RED 指标）**；**Dynatrace 官方案例：Park 'N Fly 开发周期提速 29%（2021-03-23）**；Grafana Mimir 与 Tempo 加入栈；**W3C Trace Context 成为正式推荐标准（日期：官方未标注——w3.org 被 Cloudflare 拦截，正文不可读；本行不得作为日期证据）**；Cilium Hubble 提供 L3-L7 流级可观测 | **Pixie 集群内边缘计算 + eBPF 自动遥测**（数据就地计算，集群 CPU <5%、多数 <2%）；AI 能力内嵌进平台（Watchdog 类自动异常检测） | 云原生观测成本与覆盖率矛盾爆发；eBPF 让"无埋点"成为可行；跨厂商追踪断裂急需标准 |
| **2022** | **Dynatrace Grail 数据湖仓【待核验：推断】**推出；Grafana Phlare 发布（2022 年，**官方产品页原文**）；持续剖析成为"第四信号"共识；SolarWinds 转向统一平台（Hybrid Cloud Observability / Observability）【待核验】 | **Coroot 以 eBPF 做零埋点 + 预定义 inspection + AI 根因分析**（厂商自述可识别 80%+ 问题）；ML 异常检测产品化 | 日志成本失控；"四个信号统一"成为平台竞争焦点；profile 与 trace 关联需求明确 |
| **2023** | **Grafana 收购 Pyroscope（2023-03）【据公开报道，未取得官方来源；v1.0 曾误称为"官方产品页原文表述"，已按 B-R1-09 撤回】**，Phlare + Pyroscope 合并；**Grafana Adaptive Metrics【待核验：未取得 2023 年官方发布页；但官方文档页本轮已取证，见 §2.8.3】** 用动态聚合降基数成本；Elastic 推进 ES\|QL；Pyroscope 开源项目创立于 2021（**官方产品页原文**） | **Datadog Bits AI（2023-08-03，生成式 AI DevOps Copilot）**；**Dynatrace 于 2023-07-25 宣布 Davis 扩展为业界首个"超模态 AI"并命名 Davis CoPilot（官方 IR 新闻稿，S 级）——本轮修正：v1.0 曾误置于 2024 行**；**New Relic AI【待核验】**；Elastic AI Assistant【待核验】；Splunk AI Assistant【待核验】；**生成式 AI 全面入场，"自然语言 → 查询语言"成为标准落地形式** | 大模型能力跃升（GPT 系列）；指标基数与账单同步爆炸，倒逼降本技术；查询语言门槛成为取数瓶颈 |
| **2024** | **Cisco 完成收购 Splunk（2024-03）【待核验：未取得 Cisco/Splunk 官方新闻稿，Cisco IR 被 Cloudflare 拦截】**，网络 + 安全 + 可观测合流；**Grafana Asserts / Sift**；**Elastic ES\|QL GA【待核验】**；Broadcom 版本线推进（DX APM 26.x）**——⛔ 该行已删除：DX APM 26.x 文档路径实测 404，厂商整章降级，不再计入时间线** | **AI 观测成为新赛道**：**New Relic AI Monitoring【待核验】** 观测 LLM token/质量与 **MCP 调用链**；Elastic AI Assistant GA【官方文档 front-matter 标注 GA，日期官方未标注】；Grafana MCP Server（Agent 接入 Grafana） | LLM 应用进入生产（运维能力断层）；Agentic 架构出现，传统黄金信号无法覆盖"静默劣化"；AI 自身需要被观测 |
| **2025** | **OpenTelemetry eBPF Profiler 生态成熟**（跨语言内核态剖析，官方量化上界 **1% CPU / 250MB 内存**，内核 ≥5.10）；Elastic 列式指标引擎（官方宣称 Prometheus 场景 30x）；**Elastic 官方案例：Burgan Bank Türkiye 用本地部署 AI 助手实现事件响应提速 90%（2025-08-28，官方博客）**；Grafana Adaptive Telemetry 套件推进；SolarWinds 强化 AI/ML 异常检测叙事 | **IBM Instana GenAI Observability 正式 GA（2025-10-06，IBM TechXchange，Orlando）**；Intelligent Incident Investigation 用 Agentic AI 做根因识别；Grafana Assistant 与 gcx CLI（AI 原生 CLI） | AI 应用规模化生产的治理与合规压力；token 成本与输出质量成为运维指标；Agentic AI 从概念进入产品 |

### 3.2 2026 年延伸注记（超出 2015-2025 调研窗口，仅作趋势观察，不计入时间线统计）

| 时间 | 事件 | 来源等级 |
|---|---|---|
| 2026-05-05 | IBM 发布 **AI Agent and LLM Observability**（从 GenAI 可见性走向"AI 系统理解"：自动发现 agents/models、规模化评估输出、AI 行为基线与偏离、理解 agent 决策） | S（官方公告） |
| 2026-08-04 | Grafana Labs 宣布 **Adaptive Profiles GA**，补齐 Adaptive Telemetry 套件（"Intelligent Optimization Layer"） | S（官方新闻室列表） |
| 2026-08-26 | Grafana Labs 宣布突破 **10,000 客户**（AI 采用加速增长） | S（官方新闻室列表） |
| 2026-08-31 | Grafana 官方新闻稿：客户 **Dabble** 采用 Grafana Cloud + Grafana Assistant 以缩短事件响应时间 | S（官方新闻室列表，详情页 URL 未取证） |
| 2026-09-07 | OTel 官方博客《Inside the LLM Call: GenAI Observability with OpenTelemetry》——**GenAI 语义约定**标准化 LLM 调用（模型名、输入输出 token 数、可选 prompt/completion/tool 内容） | S（官方博客 RSS） |
| 2026-09 | 多家厂商统一转向 **"Agentic AI + AI 观测"** 双叙事（Datadog Agent Observability、Dynatrace Intelligence agentic workflows（Preview）、Splunk Agent Observability、New Relic 多 Agent MCP、Elastic Agentic investigations、IBM AI Agent Observability、Grafana MCP Server / gcx CLI） | S（各厂商官方产品页/文档） |

> **时间线的方法论说明（v1.1 重写）**：本表仅纳入**本稿已取证到 S/A 级来源**的事件，并遵守以下三条规则：① **凡无 S/A 级官方来源的时间点一律加 `【待核验】`**（2026 年信息另加 `【2026延伸·窗口外】`）；② **凡被第 1 轮评审判定为"证据类型不成立"的依据（sitemap lastmod）已全部废止**；③ **⛔ Broadcom 相关行已从时间线中移除**——该厂商整章降级为"证据不足的对照性附录"（见 §2.6 章首声明），不得作为任何时间线断言。
> 本表**明确标注为"待核验"的时间点共 16 处**：2017 Cisco 收购 AppDynamics、2018 Broadcom 收购 CA、2019 OTel 成立、2019 Dynatrace Davis 品牌化、2020 New Relic 平台统一、2020 IBM 收购 Instana、2021 W3C Trace Recommendation 日期、2022 Dynatrace Grail、2022 SolarWinds 统一平台、2023 Grafana 收购 Pyroscope、2023 Grafana Adaptive Metrics、2023 New Relic AI、2023 Elastic AI Assistant、2023 Splunk AI Assistant、2024 Cisco 完成收购 Splunk、2024 Elastic ES|QL GA / New Relic AI Monitoring。**"驱动因素"列为本稿分析性判断，非官方来源。**
>
> **本轮新增的 5 条 S/A 级时间锚点（均为页面内正文日期，可直接复核）**：Datadog Continuous Profiler **2020-08-11**（官方新闻稿）；Datadog USM **2021-10-26**（官方博客）；Datadog Bits AI **2023-08-03**（官方博客）；Dynatrace Davis 超模态 AI / Davis CoPilot **2023-07-25**（官方 IR 新闻稿）；IBM Instana GenAI Observability GA **2025-10-06**（官方公告）。

---

## 4. 传统技术 vs AI技术 对比分析

| 维度 | 传统技术（2015-2019 世代） | AI技术（2023-2025 世代） | 对用户 APM 场景的适配性判断 |
|---|---|---|---|
| **数据采集方式** | **侵入式埋点为主**：字节码注入 / SDK 手动埋点 / 各语言专有 Agent；采集粒度深但需改代码或装 Agent（AppDynamics、早期 New Relic/Dynatrace） | **无侵入化为先**：eBPF 内核态解析（Datadog USM、Pixie、Coroot、Cilium Hubble/Tetragon、OTel eBPF Profiler）；AI 观测则要求**新增 AI 语义采集**（token、prompt/completion、tool call、MCP 调用链、Agent 拓扑） | **eBPF 路线与用户完全一致**，是肯定项。用户应把"AI 语义采集"提前设计进 Agent 的扩展点（即使 v1 不实现），否则后期补采需要重新发版（见 P1-3） |
| **分析范式** | **阈值与统计基线**：静态阈值 → 季节性基线 → 异常检测（AIOps 第一波；⚠️ **v1.1 改写**：v1.0 在此处把"Broadcom DX OI"列为 AIOps 第一波证据，该断言**因 Broadcom 整章证据不足已被剔除**；本行现仅由**有官方来源的 SolarWinds AIOps 表述**支撑）→ **因果推理**（Dynatrace Davis 以拓扑 + 因果区分根因与受害者；官方锚点：2023-07-25 IR 新闻稿的 "predictive- and causal-AI"） | **生成式 + 因果混合**：LLM 负责"自然语言 → 查询/结论"（Bits AI、New Relic AI、Elastic AI Assistant、Splunk AI Assistant、Grafana Assistant）与"自动调查"（IBM Intelligent Incident Investigation、Grafana Sift），但**根因正确性仍依赖拓扑与因果结构**（Smartscape / Dynamic Graph / Service Map） | **关键结论：LLM 不能替代拓扑与因果。** 用户 Server 端 AI 助手必须建立在"交换机端口↔链路↔服务↔业务"的持续维护图之上，否则 LLM 只能用相关性编故事（见 P0-3） |
| **交付形态** | 私有化重型部署（SolarWinds 自托管、Splunk 本地部署；⚠️ **v1.1 改写**：v1.0 在此处列出的"Broadcom DX APM"**因证据不足已从论据中剔除**，本行结论改由 SolarWinds 自托管与 Splunk 本地部署两条**有官方产品页来源**的证据支撑）与 SaaS 轻量交付（Datadog、New Relic）两极分化 | **AI 能力几乎全部部署在 Server 云端**，客户端只做采集与预处理；AI 助手以对话界面（Web/移动/Slack/CLI）统一交付；MCP / gcx CLI 等**结构化 Agent 接口**成为新形态 | 用户的"Server 端 AI 助手"与行业方向一致。**注意**：交换机侧不可能承载 LLM 推理，AI 必须全部在 Server 端；交换机侧只应做"为 AI 准备高质量结构化数据"（见 P0-1/P0-2） |
| **资源开销** | Agent 开销以"可接受"为界，普遍**缺少公开量化**（本稿 10 家厂商中，官方给出明确上界的仅 OTel eBPF Profiler 的 **1% CPU / 250MB 内存**与 Pixie 的 **<5%，多数 <2% 集群 CPU**） | AI 侧开销体现在**Server 端**（存储、查询、推理成本），客户端侧因无埋点化反而开销更可控 | **用户必须拿到可验收的开销指标**。可参考的公开基线：OTel eBPF Profiler 的 1% CPU / 250MB 是"官方测试上界"，可作交换机侧 Agent 预算的**乐观参照**（但交换机 CPU 与内存远弱于服务器，须按比例收紧） |
| **成熟度** | 高：十年以上工程验证，能力边界清晰；但**云原生适配滞后**是传统私有化路线的结构性债务（⚠️ **v1.1 改写（响应 B-R1-03）**：v1.0 以"**Broadcom、SolarWinds 在 AI 叙事上的缺位可作证据**"支撑本行结论。经本轮取证：**Broadcom 整章已降级、其"AI 叙事缺位"属无来源推断，不得作为证据 → 本行结论改由 SolarWinds 一条有官方产品页来源的证据支撑**，即 SolarWinds 官方产品页全文仅出现 "AIOps-powered insights" / "AI/ML that detects anomalies" 等**形容词级 AI 表述，未出现任何独立 AI 产品或生成式 AI 助手名称**——这是**可在官方页面内逐字复核**的证据。单一样本的支撑力弱于双样本，故本行结论的强度由"较强"下调为"**中等，仅一条厂商证据**"） | 分化明显：**AI 观测（LLM/MCP/Agent）处于早期**（OTel Profiles 信号仍为 Alpha、GenAI 语义约定仍在演进）；**生成式 AI 助手已商用**但普遍**缺少量化效果披露**（本稿 AI 条目中仅 Dynatrace 给出客户证言级"hours → minutes"，无一家给出受控实验结果） | **用户应把 AI 助手定位为"增强工程师效率"而非"自动定根因"**，并把可量化验收指标（告警压缩比、定位耗时、误报率）写入需求（见 P2-4） |
| **对交换机内嵌采集的适配性** | **Agent 注入类传统 APM 完全不适配**（交换机内无法做字节码注入 Java/托管运行时，且无法重启转发面） | **eBPF 系高度适配**：kprobe/tracepoint/uprobe 三类挂载点（Tetragon）、内核网络栈协议解析（Datadog USM）、内核态 L3-L7 流解析 + 服务依赖图（Cilium Hubble）、内核态跨语言栈展开（OTel eBPF Profiler）均可在设备侧运行 | **这是本调研最重要的适配性结论**：用户的 C/C++ + eBPF 路线是正确的，且**应优先对齐四条内核态实践**：USM 的"协议解析出 RED 指标"、Pixie 的"就地计算不外传原始数据"、Coroot 的"零埋点 + 规则化 inspection"、OTel eBPF Profiler 的"内核版本门槛与开销上界管理" |
| **成本结构** | 以"许可 + 主机数"计费，容器化后失真（New Relic 由此转向用量制）；私有化产品以许可与维护费为主 | 以"用量（数据量/序列数/token）"计费，**成本成为 AI 落地的第一障碍**；由此催生降本技术：Grafana Adaptive Metrics/Profiles（动态聚合降基数）、Elastic 列式指标引擎（官方宣称 30x）、Dynatrace Grail（替代传统日志管理开销） | 用户场景中**带宽与存储成本同样敏感**（交换机上送通道资源有限）。应借鉴"边缘聚合优先"（Grafana Adaptive 思路 + Pixie 就地计算）：**在设备侧完成降维，而不是把原始数据送上服务器再压缩**（见 P0-2） |

### 4.1 一句话结论

**采集侧看 eBPF（内核态、无侵入、边缘聚合），分析侧看拓扑因果（Smartscape/Dynamic Graph/Service Map 而非纯时序模型），交互侧看 LLM（但必须绑定可信数据与可执行动作）。** 这三句话分别对应本稿第 2 章中证据最扎实的三组条目：2.1.1 / 2.10.4-2.10.8（采集）、2.2.2 / 2.7.1（因果与拓扑）、2.1.3 / 2.5.2 / 2.7.3（LLM 交互）。

---

## 5. 对用户APM场景的可落地建议（≥8条，含技术名 / 来源厂商 / 落地方式 / 风险 / 优先级）

> **建议的形成依据**：用户在 Linux 交换机内部署 C/C++ + eBPF 采集 Agent（kprobe/tracepoint/XDP/TC + 基础 Linux 采集），数据上送 Server 端分析，使用者为测试（发现异常）与开发（定位异常）同学，当前正在 Server 端开发 AI 助手。以下建议均来自本稿已取证的厂商技术，并显式标注风险。

### P0（阻断级：不做则方案不成立或存在硬约束风险）

**P0-1｜把"内核版本约束"作为 Agent 的架构第一变量，而非实现细节**
- **技术名**：OTel eBPF Profiler 的内核版本门槛管理策略
- **来源厂商/项目**：OpenTelemetry（`open-telemetry/opentelemetry-ebpf-profiler`，见 2.10.4）
- **落地方式**：① 立即盘点目标交换机的内核版本分布（交换机内核可能长期停留在 4.x/5.4 等旧版本）；② 按官方 README 的实证门槛设计能力矩阵——**4.19 为最后支持点、5.4 为最后支持点、≥5.10 为当前要求**；③ 对低版本内核准备降级方案（如放弃内核态栈展开，改用 tracepoint + 用户态符号化，或仅采集指标不采集栈）；④ 把"最低内核版本"写入产品规格与测试用例，作为准入条件而非事后兼容问题。
- **风险**：① 若交换机内核 <5.10，eBPF Profiler 类深度剖析方案**不可直接移植**，需重新设计采集路径；② 内核版本升级在交换机产品线上通常需要整机固件升级，周期以季度/年计，**不可假设能快速升级**；③ 旧内核上 eBPF 特性缺失（如 BTF、部分 helper）会导致同一份 eBPF 代码需要多套编译目标，显著增加工程复杂度。
- **优先级**：**P0**

**P0-2｜采集侧采用"边缘降维"架构：设备内完成解析与聚合，只上有价值的结构化结果**
- **技术名**：Pixie 的 In-Cluster Edge Compute + Datadog USM 的内核态协议解析 + Grafana Adaptive Metrics 的动态聚合降基数
- **来源厂商/项目**：Pixie（2.10.5）、Datadog（2.1.1）、Grafana Labs（2.8.3）
- **落地方式**：① 在交换机侧 eBPF 程序中**直接完成协议解析与指标计算**（对标 USM：从内核网络栈解析出 request/error/duration 三类 RED 指标，而非上送原始包）；② 明确"**设备内计算、只上结果**"的原则（对标 Pixie："collects, stores and queries all telemetry data **locally in the cluster**"）；③ 对高基数维度实施**动态聚合**（对标 Grafana Adaptive Metrics **官方文档原文**："**identify and eliminate unused time series data through aggregation**"、"aggregating underutilized metrics into **lower-cardinality versions**"，且"**continuously reanalyzes** your usage"），例如把 pod/container 级维度在设备侧聚合成 service 级；④ 采样策略分级：常规流量低频采样、异常流量临时提升精度——**⚠️ v1.1 改写（响应 B-R1-06 ②）**：v1.0 在此处写"（对标 Instana AutoTrace 的'按需提升观测精度'思想，见 2.7.2，该条目标注为推断）"，**而 AutoTrace 是 C 级未取证条目，不应作为 P0 级建议的落地依据**。现改为**去厂商绑定的通用策略表述**："对标'**按需提升观测精度**'这一通用策略设计（**不绑定任何厂商；本稿未取得该策略在任一厂商的官方机制文档**），设备侧应设计可运行时调节的采样/采集深度档位，并在异常窗口自动升档、窗口结束后自动回落。"
- **风险**：① 设备侧计算消耗交换机 CPU，而交换机 CPU 通常为控制面预留，**过载可能影响转发面与管理面**——必须做 CPU 上限硬保护（cgroup/优先级/自动降级）；② 设备内聚合会**丢失原始明细**，导致事后"回溯式调查"能力下降（与 Pixie 的取舍相同）——需在"保留窗口 + 明细抽样"上做明确产品决策；③ 聚合维度一旦设计错误（聚合掉了关键排障维度），需重新发版且历史数据无法弥补。
- **优先级**：**P0**

**P0-3｜Server 端 AI 助手必须建立在"持续维护的拓扑因果图"之上，不能只做时序异常检测**
- **技术名**：Dynatrace Smartscape + Davis 确定性因果分析；IBM Instana Dynamic Graph / Discovery mapping
- **来源厂商**：Dynatrace（2.2.1 / 2.2.2）、IBM Instana（2.7.1）
- **落地方式**：① 先建图再上 AI——把交换机场景的实体与关系显式建模为持续更新的图：**端口 ↔ 链路 ↔ 设备 ↔ 服务 ↔ 业务事务**（对标 Smartscape："谁依赖谁、谁运行在哪"的实时依赖图）；② 异常检测产出**候选异常实体**后，必须沿拓扑做**因果传播判定**以区分"根因实体"与"被波及实体"（对标 Davis："identifies root cause with **topology and dependency context**"，是**确定性、基于因果**而非纯统计）；③ 把"变更"作为一等信息源纳入图（部署、配置变更、策略下发），用于回答"是什么变了"（对标 Davis 的变更归因："correlates code changes, deployments, configuration, and policy updates"）；④ AI 输出必须**附证据链**（哪张图、哪条依赖、哪个时间点），使测试/开发同学可采信。
- **风险**：① 拓扑图的数据质量是**全链路瓶颈**——交换机场景中"服务与端口的映射"往往依赖人工或外部 CMDB，若映射不准，因果推理会把根因指错，**AI 会以高置信度给出错误结论**（比不做 AI 更危险）；② 纯规则/因果引擎需要**领域知识沉淀周期**（Dynatrace 积累了十余年），团队若期望"上模型即见效"会严重低估工期；③ 若跳过建图直接上 LLM，会出现"用相关性编故事"的幻觉型根因，且难以被使用者识别。
- **优先级**：**P0**

### P1（严重：显著影响效果、成本或用户信任，应在 v1.x 内解决）

**P1-1｜明确"上送协议"选择：优先 OTLP，并以 Prometheus 生态兼容作为过渡**
- **技术名**：OpenTelemetry Protocol（OTLP）+ OTel Collector 的 agent/collector 双形态部署；Prometheus 指标生态
- **来源厂商/项目**：OpenTelemetry（2.10.1 / 2.10.2）、Prometheus（2.10.10）
- **落地方式**：① 上送协议**优先选 OTLP**，理由是它是厂商中立的标准（本稿取证到 Datadog、New Relic、Elastic、Dynatrace、IBM Instana、Splunk、Grafana 均提供 OTel 接入路径），可避免用户后端演进时重写设备侧 Agent；② 采用 **Collector 的 agent 形态**在设备/近端做批处理与聚合，再由上游 collector 汇聚（官方明确"Single codebase, deployable as an **agent or collector**"）；③ 若目标客户既有 Prometheus 体系，提供 Prometheus/OpenMetrics 兼容导出——**注意：Prometheus 原生为 HTTP 拉取模型，交换机位于网络边缘、难以被中心侧主动拉取**，因此需评估其远程写入（remote write）路径或由 Collector 代拉，**本稿未取证 remote write 官方页面，此点待第1轮补证**。
- **风险**：① OTLP 的 Profiles 信号仍为 **Alpha**（官方 README 明确），若用户计划上送 profile 数据需准备协议变更；② OTel 生态版本迭代快，**规范按 SemVer 管理且实现需自报所实现的版本**，需建立版本兼容矩阵与回归测试；③ Prometheus 拉取模型与交换机部署形态存在结构性张力，直接套用会失败。
- **优先级**：**P1**

**P1-2｜把"开销上界"写成可验收指标，并公开测量方法**
- **技术名**：OTel eBPF Profiler 的开销管理（官方上界 1% CPU / 250MB 内存）、Pixie 的集群 CPU 上界（<5%，多数 <2%）
- **来源厂商/项目**：OpenTelemetry（2.10.4）、Pixie（2.10.5）
- **落地方式**：① 为交换机侧 Agent 定义**双阈值**：稳态开销上界（如 CPU ≤X%、内存 ≤Y MB）与突发保护阈值（超过即自动降采样/暂停深度采集）；② 对标官方做法，把开销**在测试中验证并公开**（OTel 的表述是"our upper limits **in testing**"，即明确标注为测试上界而非保证值）；③ 建立"能力 ↔ 开销"对照表（例如：只采 RED 指标 vs 加协议解析 vs 加栈展开），让产品可在客户现场按资源裁剪。
- **风险**：① 交换机 CPU/内存远弱于服务器，**OTel 的 1% / 250MB 不能直接套用**（250MB 在资源受限设备上可能已不可接受）；② 过度保守的开销阈值会导致采集覆盖率不足，反而失去排障价值；③ 缺少公开量化正是本稿对 10 家厂商的共同批评（见第4章"成熟度"行），用户若也不公开，将无法在客户侧建立信任。
- **优先级**：**P1**

**P1-3｜为"AI 应用可观测"预留采集扩展点（LLM token / MCP / Agent 调用链）**
- **技术名**：New Relic AI Monitoring（LLM/MCP/多 Agent）、IBM Instana GenAI Observability 与 AI Agent & LLM Observability、OTel GenAI 语义约定、Grafana MCP Server
- **来源厂商/项目**：New Relic（2.3.2）、IBM（2.7.3）、OpenTelemetry（GenAI 语义约定，2026 官方博客，延伸注记）、Grafana Labs（2.8.2）
- **落地方式**：① 在 Agent 的**协议解析框架中预留 AI 协议识别位**——即使 v1 不解析，也要保证架构上可插拔（对标 New Relic "no new instrumentation needed" 的复用思路与 MCP 全生命周期追踪）；② 采用 **OTel GenAI 语义约定**作为字段标准（官方明确其标准化了 model 名、输入/输出 token 数，可选 prompt/completion/tool 调用与结果），避免自造字段；③ 把"AI 应用"作为一类**被观测对象**纳入 Server 端，与其传统服务在同一 trace 中串联（对标 IBM："trace requests across AI and traditional services"）；④ 若用户自身产品要接入外部 AI Agent 生态，考虑实现 **MCP Server**（对标 Grafana 提供托管与自托管两种 MCP Server，gcx CLI 提供结构化访问）。
- **风险**：① **GenAI 语义约定仍在演进**（OTel 相关规范尚未稳定），过早固化字段有返工风险；② prompt/completion 内容涉及**敏感数据与合规**（官方均标注为"opted in"或受权限约束），交换机场景中可能承载客户业务明文，需默认关闭内容采集；③ 若用户产品当前不服务 AI 应用，"预留"可能被视为过度设计——建议以"接口预留、实现延后"的轻量方式落地。
- **优先级**：**P1**

**P1-4｜告警收敛采用"单条告警 + 全证据"模式，而非简单压缩条数**
- **技术名**：Coroot 的"单告警携带全部 inspection 结果"机制；Splunk ITSI 的 Episode 事件聚合
- **来源厂商/项目**：Coroot（2.10.8）、Splunk（2.4.1，机制部分为推断）
- **落地方式**：① 收敛的目标不是"减少告警条数"，而是**让每一条告警自带结论与证据**——Coroot 官方明确：当应用未达成 SLO 时"**sends a single alert that includes the results of all relevant inspections**"；② 采用**可解释的规则化 inspection**（而非纯黑盒模型），使每一条告警能追溯到具体检查项与阈值（Coroot 官方：inspection 可按应用或整个项目调整）；③ 借鉴 ITSI 的**服务健康度**抽象：把技术指标聚合为业务服务级的数值化健康分，使"要不要叫人"成为可判断的量（该机制描述属推断，见 2.4.1 字段5 的推断边界）。
- **风险**：① 规则化 inspection 需要**大量领域知识积累**（Coroot 称可自动识别 80%+ 问题，但该数字为厂商自述、未给出评测方法），团队若期望短期达到同等覆盖率会失望；② "单条告警"模式一旦证据组织不当，会让值班同学**失去下钻的入口**，反而降低可信度（必须同时提供明细展开）；③ 告警收敛过度会掩盖独立的并发故障（多个根因被合并为一条）。
- **优先级**：**P1**

**P1-5｜抓住"流级遥测 + APM 语义打通"这一交换机厂商的差异化机会**
- **技术名**：Cilium Hubble 的 L3-L7 流级可观测与 L7 服务依赖图；Datadog Network Monitoring 的"hop-by-hop 路径 + 应用关联"；SolarWinds NPM 的 NetPath™ hop-by-hop 路径可视化与 PerfStack™ 跨域同轴关联（**v1.1 已由"推断项"升级为"官方产品页原文"**）
- **来源厂商/项目**：Cilium Hubble（2.10.6）、**Datadog Network Monitoring 产品页（引用锚点：§7.1 #7；⚠️ v1.1 修正（响应 B-R1-12）——v1.0 误写为"2.1.1 来源组中的 Network Monitoring 产品页"，但 §2.1.1 字段 9 只列 USM 博客/文档/产品页三条，不含该页。现改为指向 §7.1 第 7 条的独立 URL 并加锚点）**、**SolarWinds NPM（2.9.2，官方产品页原文）**
- **落地方式**：① 在交换机上做**L3-L7 流级可观测**（对标 Hubble 官方文档原文："automatic discovery of the services dependency graph at the L3/L4 **and even L7 layer**"，以服务地图形式可视化数据流），而非仅看接口利用率与丢包；② 把**网络跳级指标与应用性能指标关联**——**两条独立官方证据**：(a) Datadog Network Monitoring 产品页原文："Gain a **hop-by-hop** view of hybrid network traffic in a single pane of glass"、"Correlate **NetFlow traffic** to the infrastructure & applications responsible for the connection"（URL 见 §7.1 #7，本轮与第 1 轮评审均实测 200）；(b) **SolarWinds NPM 官方产品页原文**："**NetPath™** provides **hop-by-hop path visualization** across on-premises and cloud network infrastructure… where **latency and packet loss** occur along the route"，以及 "**PerfStack™** lets you **drag and drop network, system, and application metrics onto a single timeline**"；③ 由此形成**纯云厂商难以复制的优势**：交换机厂商同时掌握"流量物理路径"与"应用调用链"，可回答"应用卡顿发生在哪一跳、由哪条链路/哪个端口引起"。
- **风险**：① L7 解析在交换机上开销显著高于 L3/L4，**资源受限设备的可行性需实测**，可能只能在高端型号提供；② 加密流量（TLS 1.3）会直接削弱 L7 解析能力（Datadog USM 亦将部分加密流量解析列为 Preview），**产品宣传需谨慎**；③ 与既有网络管理产品线（若存在）可能功能重叠，引发内部定位冲突。
- **优先级**：**P1**

### P2（一般：提升竞争力与体验，可排入后续版本）

**P2-1｜借鉴 Elastic AI Assistant 的"能力清单 + 前置条件 + 数据边界"规格模板定义自有 AI 助手**
- **技术名**：Elastic AI Assistant（Kibana）
- **来源厂商**：Elastic（2.5.2）
- **落地方式**：Elastic 官方文档给出了本稿中**最可操作的产品规格模板**，建议逐条对标：① **明确的能力清单**（构造查询 / 把其他语言查询转换为 ES\|QL、指导索引数据、**代调用 Elasticsearch API**、生成样例数据、创建可视化与分析、解释错误并建议修复、威胁调查与告警分流）；② **明确前置条件**（要求特定权限 + 一个 **LLM connector**，即模型可插拔而非绑定单一供应商）；③ **明确能力差异**（不同解决方案中能力与交互方式不同）；④ **明确气隙部署方案**（官方专门提供"把知识库制品镜像到 Kibana 可达基础设施"的流程）——**这一点对交换机/内网部署场景极其重要**，用户的 Server 端 AI 助手很可能面临无法访问公网模型或知识库的环境。
- **风险**：① LLM connector 的可插拔会带来**多模型质量不一致**的测试成本；② "代调用 API"能力需要严格的**权限收敛与审计**（官方明确要求特定权限），否则 AI 助手会成为越权操作通道；③ 气隙环境下若客户无本地模型，功能可能整体不可用，需要在售前明确交付边界。
- **优先级**：**P2**

**P2-2｜评估"持续剖析（Profiling）"作为第四信号在交换机场景的可行性**
- **技术名**：Datadog Continuous Profiler、Grafana Pyroscope、OTel eBPF Profiler
- **来源厂商/项目**：Datadog（2.1.2）、Grafana Labs（2.8.1）、OpenTelemetry（2.10.4）
- **落地方式**：① 明确"是否要采集交换机上用户态进程（如管理面服务、协议栈守护进程）的 CPU 火焰图"——若能采集，则可把"性能异常"从指标层下钻到函数级，直接服务于**开发同学定位异常**的诉求；② 架构参考 **Pyroscope**（单二进制、对象存储后端、多租户、与 metrics/logs/traces 在 Grafana 中原生关联），"profile 作为第四类信号"的存储与查询模型可直接复用；③ 采集端参考 OTel eBPF Profiler（非侵入、无需重配置/重启、支持无调试符号的原生代码，依赖 `.eh_frame` 类方案）。
- **风险**：① 交换机上的用户态进程多为 C/C++ 且可能**无调试符号**——OTel 项目已用专利方案（US11604718B1）解决，但自研成本高；② profiling 在**低频 CPU 设备上开销占比可能被放大**（同等采样频率下，弱 CPU 的相对开销更高）；③ 若交换机主要瓶颈在转发面（硬件 ASIC）而非控制面 CPU，则 CPU profiling 的价值有限，**需先验证目标客户的真实性能问题分布**。
- **优先级**：**P2**

**P2-3｜把"零埋点覆盖率"作为可验证的产品指标，并对标服务地图完整性**
- **技术名**：Datadog USM 的自动服务发现与自动服务命名、Coroot 的服务地图 100% 覆盖主张
- **来源厂商/项目**：Datadog（2.1.1）、Coroot（2.10.8）
- **落地方式**：① 对标 USM 的自动标签推导逻辑（用 `app`/`short_image`/`kube_container_name`/`container_name`/`kube_deployment`/`kube_service` 自动命名服务，已有 unified service tags 则沿用），在交换机场景中设计**自动实体命名规则**（端口/VLAN/邻居/业务标识的自动推导）；② 明确"未纳管实体清单"功能——不仅报告"发现了什么"，还要报告"哪里没有数据"，使覆盖率可被验证（这是"消除盲区"命题成立的前提）；③ 把覆盖率与发现时延写入产品指标（USM 官方描述：配置 Agent 后**约 5 分钟**可在 Catalog 看到服务，"Within seconds"获得 RED 指标）。
- **风险**：① 自动命名规则一旦与实际组织架构冲突，会产生大量"命名正确但语义错误"的实体，**比未发现更难排查**；② 交换机场景缺少 K8s 那样的标准化标签体系，自动发现依赖 LLDP/CDP/SNMP 等**厂商私有实现差异大**的数据源，覆盖率难以做到云原生场景的水平。
- **优先级**：**P2**

**P2-4｜为"AI 助手输出可审计"设计机制（避免走入行业普遍的无量化陷阱）**
- **技术名**：Datadog Bits AI 的"检索平台内已有检测结果"路径、Elastic AI Assistant 的"自然语言 → ES\|QL"路径、New Relic AI 的"自然语言 → NRQL"路径
- **来源厂商**：Datadog（2.1.3）、Elastic（2.5.2 / 2.5.3）、New Relic（2.3.3）
- **落地方式**：① AI 助手**不要独立回答**，而应把自然语言翻译为**可复现的查询**（ES\|QL / NRQL / SPL 模式），使每条结论可被人工复核与重放；② 让助手**优先检索平台内已有的结构化检测结果**（对标 Bits AI："finding and correlating key data from across the Datadog platform, including **Watchdog-detected log and trace anomalies**"），即让 AI 站在已有检测能力之上而非替代它；③ 定义并**公布验收指标**：告警压缩比、平均定位耗时、误报率、用户采纳率——本稿取证到的厂商 AI 条目中**几乎全部缺少量化效果披露**（唯一例外是 Dynatrace 首页引用的客户证言"hours → minutes"），这正是用户可以通过"敢公布数字"建立差异化信任的机会。
- **风险**：① 要求可复现查询会限制助手的自然语言自由度，可能降低"好用感"（需在 UI 上做权衡）；② 公布指标意味着接受长期监督，若指标不达标会成为竞争弱点；③ 依赖"平台内已有检测能力"意味着**检测能力的上限决定 AI 助手的上限**，需先在检测侧投入。
- **优先级**：**P2**

### 5.1 建议优先级汇总表

| 编号 | 建议 | 来源厂商/项目 | 优先级 | 主要风险一句话 |
|---|---|---|---|---|
| P0-1 | 内核版本作为架构第一变量 | OTel eBPF Profiler | **P0** | 交换机内核可能 <5.10，深度剖析方案不可直接移植 |
| P0-2 | 采集侧边缘降维（设备内解析聚合） | Pixie / Datadog USM / Grafana Adaptive Metrics | **P0** | 占用交换机 CPU 可能影响转发面；聚合丢明细 |
| P0-3 | AI 助手必须建在拓扑因果图上 | Dynatrace Smartscape+Davis / IBM Dynamic Graph | **P0** | 拓扑数据质量差会让 AI 高置信度地给出错误根因 |
| P1-1 | 上送协议优先 OTLP，Collector 双形态 | OpenTelemetry / Prometheus | **P1** | Profiles 信号仍 Alpha；Prometheus 拉取模型与交换机形态冲突 |
| P1-2 | 开销上界写成可验收指标 | OTel eBPF Profiler / Pixie | **P1** | 1%/250MB 为服务器基线，不可直接套用弱 CPU 设备 |
| P1-3 | 预留 AI 应用可观测扩展点 | New Relic / IBM / OTel GenAI 语义约定 / Grafana MCP | **P1** | GenAI 语义约定未稳定；prompt 内容涉及合规 |
| P1-4 | 告警收敛 = 单告警 + 全证据 | Coroot / Splunk ITSI | **P1** | 规则库需长期积累；收敛过度会掩盖并发故障 |
| P1-5 | 流级遥测 + APM 语义打通（差异化机会） | Cilium Hubble（2.10.6）/ **Datadog Network Monitoring 产品页（§7.1 #7）** / **SolarWinds NPM（2.9.2，官方产品页原文）** | **P1** | L7 解析开销高；TLS 1.3 削弱解析能力 |
| P2-1 | 对标 Elastic AI Assistant 规格模板 | Elastic | **P2** | 代调用 API 需严格权限收敛；气隙环境可能不可用 |
| P2-2 | 评估 Profiling 作为第四信号 | Datadog / Grafana Pyroscope / OTel | **P2** | 交换机用户态多无调试符号；弱 CPU 上开销占比放大 |
| P2-3 | 零埋点覆盖率可验证 + 未纳管清单 | Datadog USM / Coroot | **P2** | 缺乏 K8s 式标签体系，自动命名易语义错误 |
| P2-4 | AI 输出可审计 + 公布量化指标 | Datadog Bits AI / Elastic / New Relic | **P2** | 限制自然语言自由度；指标公开后长期受监督 |

---

## 6. 数据质量自评

> **🔴 v1.1 重写说明（响应 B-R1-04：统计口径必须可信）**：第 1 轮评审指出 v1.0 存在"条目数 33/36/37、S/A 来源数 45/52/62/70/85、案例数 3/0"三组**互斥且不可复核**的数字。v1.1 的处理方式是**先立口径、再算数字**：6.0 给出**完整计数规则与逐字段判定规则**，6.1–6.3 给出**每一个数字及其逐条清单**，使评审可按同一算法复算。**全稿只保留一个条目数（34），不再出现任何"约 X 条"的模糊表述。**

### 6.0 统计口径与算法说明（v1.1 新增；本节即"分母定义"，建议评审优先阅读）

**A. 有效技术条目数（N）的计数规则**
1. 计数对象为第 2 章中形如 `#### 2.x.N …`（N≥1）的**技术条目标题**；**不计入**形如 `#### 2.x.0 厂商近10年战略与技术主线` 的厂商主线小节。
2. **原始计数**：`^#### ` 标题共 **49** 个，其中 **2 个**是 §6.5 的表格标题（`#### 表 A：…`、`#### 表 B：…`），**10 个**是 `#### 2.x.0 厂商近10年战略与技术主线`；故第 2 章的技术条目标题 = 49 − 2 − 10 = **37 个**。（**复核命令**：`[regex]::Matches($c,'(?m)^#### ')` = 49；`(?m)^#### 2\.\d+\.0` = 10。）
3. **剔除项（3 个）**：① `#### 2.6.3`（标题自述为"结构性缺口登记，**非技术条目**"）；② `#### 2.6.1`、③ `#### 2.6.2`（本轮按 Leader 裁决 A 第 2 分支降级为"**证据不足的对照性附录**"，依裁决**不计入有效技术条目数与覆盖率分母**）。
4. **有效技术条目数 N = 37 − 3 = 34 条**。逐条清单：2.1.1–2.1.3、2.2.1–2.2.3、2.3.1–2.3.3、2.4.1–2.4.3、2.5.1–2.5.3、2.7.1–2.7.3、2.8.1–2.8.3、2.9.1–2.9.3、2.10.1–2.10.10（3×8 + 10 = 34）。
5. **交叉验证**：`^8\. \*\*案例\*\*` 的出现次数为 **37** 次（与 37 个技术条目标题一一对应；被剔除的 3 条其字段 8 亦存在，故两者一致）。

**B. 9 字段完整率的判定规则（逐字段，比 v1.0 更严格且可复现）**

| 字段 | 判定为"齐"的条件 | 判定为"不齐"的条件 |
|---|---|---|
| 1 技术类别 | 已填写 | — |
| 2 首次发布/关键版本时间 | 给出**在官方页面正文/元数据内可读到**的日期（规范允许"官方未标注（快照于 YYYY-MM-DD 确认）"这一写法，但须同时给出 ≥1 条 S/A 级官方来源页） | 仅有"官方未明确，据 X 推断"；依据为 **sitemap lastmod**；或依赖被 Cloudflare 拦截/正文不可读的页面 |
| 3 推出背景 | 背景陈述与条目已取证的官方来源表述一致，或引用了官方页面原文 | **条目在字段 3 内明确写了"官方来源缺失"**（即作者自认该段无官方来源）；**或**该段引用的关键事实在字段 9 中无任何官方来源可对应且未标注推断边界 |
| 4 解决的问题 | 有实质问题陈述 | 空或仅占位 |
| 5 技术原理 | 有实质机制描述（允许标注推断边界） | 明确写"官方来源缺失、无法给出架构级描述" |
| 6 技术效果 | 有量化数据，**或**明确写"官方未给出量化数据"（规范允许） | 仅写"官方来源缺失" |
| 7 落地情况 | 有明确落地状态（已商用/开源/预览…） | 空或明确"官方来源缺失" |
| 8 案例 | 有 ≥1 个**客户名+场景+结果+时间**四要素齐备、且来源为 S/A 级的案例（同一案例只计入**最相关的一个**条目） | 缺任一要素（含"有客户名与量化结果但官方页面未标注日期"→ 只计入 §6.5 表 B） |
| 9 来源 | 条目至少有 1 条**可用**官方来源（S 或 A 级，含官方 GitHub 仓库） | 明确写"官方来源缺失" |

**C. 案例"五要素"定义**：`客户名 + 场景 + 结果 + 时间 + 官方来源URL`；**时间要素须在官方页面内可读到**（新闻稿正文日期 / 官方博客标注日期 / 案例页 Publish Date）。不满足者一律降入 §6.5 表 B，**不冒充表 A**。

**D. S/A 来源条数的计数规则**：以 §7 全量来源清单中**逐条列出的 URL 条目**为单位（按清单行计，**不按去重 URL 计**、不按"引用次数"计）；§7 各分节标题给出小计、末尾给出合计。

**E. "待核验/窗口外"标注规则**：凡时间点无 S/A 级官方来源，正文一律加 `【待核验】`；`【2026延伸·窗口外】` 用于超出 2015-2025 窗口的信息。§3.1 已声明待核验时间点共 **16** 处。

### 6.1 结构与数量指标（全部数字按 §6.0 算法重算）

| 验收项 | 门槛（本任务书 / 00号规范） | 本稿实际（v1.1，可复核） | 达标 |
|---|---|---|---|
| 厂商覆盖（APM） | 10/10 | **10/10**（§2.1–§2.10）。**⚠️ 但 Broadcom 整章（§2.6）已于 v1.1 降级为"证据不足的对照性附录"，实质覆盖 = 9/10 有来源支撑 + 1/10 附录化** | ⚠️ 名义达标 / 实质 9+1 |
| 有效技术条目数 | ≥22（本任务书）；00号规范 ≥35（A+B 合计口径） | **34 条** = 原 `#### 2.x.N` 37 条 − §2.6.1/2.6.2/2.6.3 三条按 Leader 裁决剔除（算法见 §6.0-A） | ✅ 对 ≥22 达标；❌ 对 ≥35 未达标 |
| AI 相关条目 | ≥8（本任务书）；00号规范 ≥12 | **严格口径（条目字段1 以 AI 技术为主要类别，且含 ≥1 条 S/A 级官方 AI 事实来源）= 10 条**：2.1.3、2.2.2、2.3.2、2.3.3、2.4.3、2.5.2、2.7.3、2.8.2、2.9.3、2.10.8（**已按 B-R1-11 剔除无来源的 §2.6.2 Broadcom DX OI**）；**宽口径（含 AI 增强）= 17 条**（另含 2.1.2、2.2.3、2.4.1、2.5.3、2.8.1、2.8.3、2.10.4） | ❌ **严格口径 10 < 12，不达标**；✅ 宽口径 17 ≥ 12 达标。**按 B-R1-11 ②要求，本稿明确以严格口径判定为不达标，不以宽口径掩盖** |
| **案例数（五要素齐备）** | ≥12（本任务书）；≥25（00号规范） | **13 个**（**窗口内（2015-2025）10 个** + 窗口外 3 个）：明细见 §6.5 表 A | ✅ 对 ≥12 达标；❌ 对 ≥25 未达标 |
| 次级案例（有客户名+量化结果，但缺官方日期或超窗口等） | — | **21 个**（见 §6.5 表 B），**不计入上行的 13** | 参考项 |
| **9 字段完整率** | ≥95% | **77.8%** = **238 / 306**（N=34 条 × 9 字段 = 306 格；缺失 **68** 格）。**逐字段缺失清单见 §6.3，可逐格复算** | ❌ **远低于 ≥95%**（如实登记，不凑数） |
| 条目含 ≥1 条 S/A 级官方来源 | 100% | **94.1%** = **32 / 34**（不达标条目仅 **2.7.2 AutoTrace**、**2.10.3 W3C Trace Context**；Broadcom 三条已剔除出分母） | ❌ |
| 链接可访问抽样（每厂商抽 1 条） | ≥95% 可达 | 本轮实际抓取成功并写入来源清单的官方来源 **100% 返回 200**；失败项（Broadcom 各路径、w3.org、investor.cisco.com）**全部如实登记为"官方来源缺失"，未计入来源清单** | ✅ |
| 主观分析章节 | 时间线 + 对比 + 建议(≥8) | **时间线（§3.1 双轨表 + §3.2 2026 延伸注记）+ 对比（§4 七维度 + §4.1 一句话结论）+ 建议（§5 共 12 条，全部带 P0/P1/P2 与风险，另有 §5.1 汇总表）** | ✅ |

### 6.2 来源质量自评

- **链接真实性**：本稿所有链接均经 `web_fetch_pro(mode=http)` **实际抓取验证**（HTTP 200 且正文命中目标内容）后才写入；**未验证成功的路径已从来源清单剔除**并改为"官方来源缺失"声明。**不存在编造 URL**（第 1 轮评审 31 条抽检的"0 编造"结论在本轮继续成立；本轮新增来源全部为当轮实抓）。
- **S/A 级来源条数与分布（按 §6.0-D 口径，逐条计入 §7）**：**共 99 条可用（S 级 88 条 + A 级 11 条）**；另有 **1 条正文不可读**（W3C Trace Context，列示但不可用）。分布：Datadog **10**、Dynatrace **12**、New Relic **10**、Cisco/Splunk **8**、Elastic **11**、**Broadcom 1**（仅 IR 首页，且**不支撑任何 DX APM 字段**）、IBM **8**、Grafana **7**（含 1 条 A 级 GitHub）、SolarWinds **8**、OpenTelemetry 生态 / Prometheus / eBPF 系 **24**（S 14 + A 10）。**复核方式**：§7.12"S/A 分级合计表"逐列相加 = 99（S 88 + A 11）；本段与 §7.12 完全一致。
- **明确给出量化数据的条目占比**：**约 15%（5/34）** ——仅 OTel eBPF Profiler（1% CPU / 250MB 内存）、Pixie（<5%、多数 <2% CPU）、Coroot（80%+ 问题自动识别）、Elastic（30x，厂商自述）、Dynatrace（客户证言 hours → minutes）。**这与 §4 对全行业的批评一致：厂商普遍不披露可验收的量化效果。**
- **本轮新增的最可靠 5 条来源（建议评审优先抽查）**：
  1. [Datadog Continuous Profiler 官方新闻稿](https://www.datadoghq.com/about/latest-news/press-releases/continuous-profiler/) — 发布 **2020-08-11**（GA、$12/host/月、客户 Cvent）— 直接闭环 **B-R1-02**；
  2. [Dynatrace 超模态 AI 官方 IR 新闻稿](https://ir.dynatrace.com/news-events/press-releases/detail/302/dynatrace-expanding-davis-to-deliver-the-observability-and-security-industrys-first-hypermodal-artificial-intelligence-converging-predictive-causal-and-generative-ai) — 发布 **2023-07-25**（Davis CoPilot 首次命名）— 直接闭环 **B-R1-10 ④**；
  3. [New Relic CareerVillage 官方新闻稿](https://newrelic.com/press-release/20241001) — 发布 **2024-10-01**（页面加载时间 −67%）— 直接闭环 **B-R1-01**；
  4. [Grafana Adaptive Metrics 官方文档](https://grafana.com/docs/grafana-cloud/adaptive-telemetry/adaptive-metrics/) — 正文完整（机制原文）— 直接闭环 **B-R1-09 ②**；
  5. [Dynatrace Park 'N Fly 官方案例新闻稿](https://www.dynatrace.com/news/press-release/park-n-fly-speeds-up-development-cycles-by-29-with-dynatrace/) — 发布 **2021-03-23**（开发周期 +29%）— 直接闭环 **B-R1-01**。

### 6.3 9 字段缺失字段清单表（v1.1 新增，供评审逐格复算）

> **算法**：N = 34 条，总字段格 = 34 × 9 = **306**；下表逐字段列出"不齐"的条目编号与条数；**缺失合计 = 68 格**；**完整率 = (306 − 68) / 306 = 238 / 306 = 77.78% ≈ 77.8%**。

| 字段 | 不齐条目数 | 不齐条目编号（逐条可核） |
|---|---|---|
| 1 技术类别 | **0** | — |
| 2 首次发布/关键版本时间 | **29** | 2.2.1、2.2.3、2.3.1、2.3.2、2.3.3、2.4.1、2.4.2、2.4.3、2.5.1、2.5.2、2.5.3、2.7.1、2.7.2、2.8.1、2.8.2、2.8.3、2.9.1、2.9.2、2.9.3、2.10.1、2.10.2、2.10.3、2.10.4、2.10.5、2.10.6、2.10.7、2.10.8、2.10.9、2.10.10 |
| 3 推出背景 | **5** | 2.2.1、2.4.1、2.4.2、2.7.2、2.10.9（**判定依据：该 5 条在字段 3 内明确写了"官方来源缺失"**） |
| 4 解决的问题 | **0** | —（2.10.9 虽为 C 级推断，但仍有 5 条实质问题陈述并标注了证据边界，按 §6.0-B 计为齐） |
| 5 技术原理 | **1** | 2.10.9 |
| 6 技术效果 | **3** | 2.7.2、2.10.3、2.10.9 |
| 7 落地情况 | **2** | 2.7.2、2.10.3 |
| 8 案例 | **26** | 2.1.1、2.1.3、2.2.1、2.2.3、2.3.2、2.3.3、2.4.1、2.4.2、2.4.3、2.5.3、2.7.1、2.7.2、2.7.3、2.8.1、2.8.3、2.9.2、2.10.1、2.10.2、2.10.3、2.10.4、2.10.5、2.10.6、2.10.7、2.10.8、2.10.9、2.10.10 |
| 9 来源 | **2** | 2.7.2、2.10.3 |
| **缺失合计** | **68** | **完整字段 = 306 − 68 = 238 → 完整率 = 77.8%** |

**字段 8（案例）已"齐"的 8 条**：2.1.2、2.2.2、2.3.1、2.5.1、2.5.2、2.8.2、2.9.1、2.9.3。

**补救计划（若要在 v1.2 冲击 ≥95%）**：完整率的最大缺口是**字段 2（29 格）与字段 8（26 格）**。字段 2 的补救路径明确：① 各厂商**官方新闻稿 sitemap / 新闻室**已证明可按日期枚举（Dynatrace / New Relic / Splunk / Grafana 本轮均已验证），可逐条补"产品首次发布"公告；② Splunk / IBM / Elastic / SolarWinds 的产品页**需渲染型环境**才能读到版本历史（本轮纯 HTTP 只能读到价值陈述）。字段 8 的补救路径见 §6.5 表 B——**已有 21 个"有客户名+量化结果"的官方案例，只差官方日期**，一旦在渲染型环境下读到案例页的发布时间戳，字段 8 可一次性从 8/34 提升到 20+/34。**本稿不通过降低判定标准来提高完整率。**

### 6.4 未解决缺口清单（v1.1 更新，标注闭环状态）

| # | 缺口 | 涉及位置 | 严重度 | v1.1 状态 | 说明与建议处置 |
|---|---|---|---|---|---|
| G-01 | 案例字段（字段 8）覆盖率仍低（8/34 条） | 全稿字段 8 | **P0→P1** | **部分闭环** | 已从 0 补到 **13 个五要素齐备案例**（表 A）与 **21 个次级案例**（表 B），达成本任务书 ≥12 门槛；但**"每条目 ≥1 个案例"仍未达成**，根因是**多数厂商的案例页不标注发布日期**（缺"时间"要素）。补证路径：渲染型环境读取案例页时间戳 |
| G-02 | Broadcom 全章无 S/A 级来源 | §2.6 | **P0** | **已闭环（决断已执行）** | 按 Leader 裁决 A 第 2 分支**降级为"证据不足的对照性附录"**，不计入条目数与覆盖率分母，§4/§5 依赖处已逐处改写（见 §2.6 章首 9 条路径实测表） |
| G-03 | W3C Trace Context 正文与日期不可读 | §2.10.3 | **P0** | **部分闭环** | w3.org 仍被 Cloudflare 拦截（本轮复测一致）；已按 Leader 裁决 F 增设 **OpenTelemetry 官方 Context Propagation 文档**作为佐证来源（`traceparent` 结构与"OTel 默认采用 W3C 头"已由官方原文支撑），**日期不编造、保留缺失声明** |
| G-04 | SolarWinds NPM/NetFlow 条目无官方来源 | §2.9.2 | P1 | **已闭环** | 本轮实抓 **NPM 与 NTA 两个官方产品页**（含 NetPath™ hop-by-hop、PerfStack™、NetFlow/sFlow/J-Flow/IPFIX 原文），字段 3/5 由 C 级推断升级为官方原文；字段 2（无官方发布日）仍缺 |
| G-05 | Instana AutoTrace 无官方来源 | §2.7.2 | P1 | **已闭环（处置已执行）** | 本轮复测 `ibm.com/products/instana/features`（确无 AutoTrace）+ 试探 IBM Docs 专题路径（返回错误页）；条目已加 `【未取证·C 级推断】` 前缀，并已从 §5 P0-2 与 §5.1 的落地依据中移除 |
| G-06 | groundcover 主仓库非公开、无产品级官方来源 | §2.10.9 | P1 | **已闭环（处置已执行）** | 条目已加 `【未取证·生态提及】` 前缀，内容不得作为论断依据；因 Leader 允许 OTel 生态按项目拆分，保留在 34 条内 |
| G-07 | 多条目的"原理"为 C 级推断而非官方原文 | §2.4.1、2.4.2、2.4.3、2.8.3、2.9.2、2.9.3、2.10.3 | P1 | **部分闭环** | **已闭环 2 条**：2.8.3（Adaptive Metrics 官方文档原文替换）、2.9.2（SolarWinds NPM/NTA 官方产品页原文替换）；**仍未闭环 5 条**：Splunk 系列（`help.splunk.com` 与 Splunk 文档站仍无法取到 ITSI Health Score/KPI/Episode 与 AppDynamics 注入机制原文）、2.9.3（官方仅形容词级 AIOps 表述）、2.10.3（W3C 正文不可读） |
| G-08 | 若干条目"首次发布时间"精度不足 | 见 §6.3 字段 2 的 29 条 | P1 | **部分闭环** | **已闭环 1 条**（2.1.2 Datadog CP → 2020-08-11）；**新增 1 条 S 级锚点**（2.2.2 Dynatrace Davis CoPilot → 2023-07-25）；**废止 3 条错误依据**（New Relic 2.3.1/2.3.2/2.3.3 的 sitemap lastmod），并统一加 `【待核验】` |
| G-09 | 厂商份额/排名未采用第三方机构数据 | §1 总览表 | P2 | 未闭环（有意保留） | 无法访问 Gartner/IDC 报告正文；总览表"领导者"表述均采自厂商官网自述的 Gartner MQ 引用，且已加 `【2026延伸·窗口外】` |
| G-10 | 行业共识时间点未取得官方公告原文 | §3.1、2.10.1、2.10.10 | P2 | 部分闭环 | OTel 成立（2019-05）与 Prometheus 加入 CNCF（2016）仍无官方公告；**W3C 日期按裁决不编造**；均已加 `【待核验】` |
| G-11 | 检索环境系统性限制 | 全稿（方法论层面） | P1（环境类） | 未闭环（环境类） | 本轮**再次复现**：`web_search_pro(engines=ddg,bing)` 对 `Dynatrace press release July 25 2023 hypermodal artificial intelligence Davis` 返回 **Apple 中国官网 iPhone 页**；对 `IBM Instana AutoTrace official documentation ibm.com docs` 返回 **IBM 中文首页与百度百科**；`investor.cisco.com` 与 `w3.org` 返回 **Cloudflare 人机校验页**。**结论：改用"官方 sitemap 挖掘 + 单页直取"后案例与新闻稿类取证大幅改善（新增 13 个五要素案例、9 条 S/A 来源），但 Cisco 收购与 Broadcom DX APM 两类仍需渲染型环境** |

### 6.5 案例总表（v1.1 新增；响应 B-R1-01）

#### 表 A：五要素齐备案例（13 个 = 窗口内 10 + 窗口外 3）

| # | 客户 | 行业 | 场景 | 结果（量化优先） | 时间 | 归属条目 | 官方来源URL |
|---|---|---|---|---|---|---|---|
| A1 | **Cvent** | 虚拟活动 SaaS | 在测试与生产环境的**每个服务**上运行 Datadog Continuous Profiler；Ian Schell（SRE Architect）证言 | 大幅降低诊断潜在问题耗时、修复性能瓶颈（**客户证言级定性，官方未给量化**） | **2020-08-11** | 2.1.2 | https://www.datadoghq.com/about/latest-news/press-releases/continuous-profiler/ |
| A2 | **Park 'N Fly** | 机场停车/交通 | 迁移至 K8s + Azure 云原生架构后，用 Dynatrace 自动可观测管理移动/Web/机场自助终端 | 开发周期平均 **+29%**（最忙双周 **+43%**） | **2021-03-23** | 2.2.2 | https://www.dynatrace.com/news/press-release/park-n-fly-speeds-up-development-cycles-by-29-with-dynatrace/ |
| A3 | **ERT** | 医疗/生命科学 | 用 Davis 监控 DevOps 流程与交付管道，以 Keptn 触发自动自愈 | 新应用交付 **6 周 → 4 周** | **2020-05-28** | 2.2.2 | https://www.dynatrace.com/news/press-release/ert-helps-medical-researchers-accelerate-clinical-trials-with-ai-assistance-from-dynatrace/ |
| A4 | **Mitchells & Butlers** | 餐饮/酒吧连锁 | 把数字渠道性能数据与业务指标（桌位预订、收入）打通 | 桌边点单 App **客单价高 20%** | **2019-12-19** | 2.2.2 | https://www.dynatrace.com/news/press-release/mitchells-butlers-serves-better-business-results-with-dynatrace/ |
| A5 | **Temenos** | 金融软件 SaaS | 覆盖 Azure + AWS + 本地部署的混合多云 SaaS 平台 | 缩短实现价值时间（**定性**） | **2020-10-01** | 2.2.2 | https://www.dynatrace.com/news/press-release/temenos-enables-seamless-banking-experiences-with-dynatrace/ |
| A6 | **U.S. Dept. of Veterans Affairs** | 美国联邦公共部门 | VA Enterprise Cloud 多云环境端到端可观测，支撑 350 个关键应用上云 | 更快、更有信心的云迁移（**定性**） | **2020-02-11** | 2.2.2 | https://www.dynatrace.com/news/press-release/dynatrace-enables-speed-and-confidence-in-us-government-agencys-migration-to-the-cloud/ |
| A7 | **CareerVillage** | 教育科技非营利 | 标准化到 New Relic 平台：APM 跟踪延迟与代码级瓶颈、告警管理前置发现问题，并监控其 AI 职业教练 "Coach" | 页面加载时间 **−67%**（300ms → <100ms）；峰值 **700** 并发学生；工程生产力 **+133%** | **2024-10-01** | 2.3.1 | https://newrelic.com/press-release/20241001 |
| A8 | **Burgan Bank Türkiye** | 银行 | OpenShift → 裸金属现代化，用 ML 与**本地部署（on-prem）AI 助手**统一可观测与安全 | 事件响应速度 **+90%** | **2025-08-28** | 2.5.2 | https://www.elastic.co/blog/category/customers |
| A9 | **SWIFT** | 金融基础设施 | 全球支付演进下的可观测现代化，减少延迟 | 克服可观测性挑战、减少延迟（**定性**） | **2025-05-05** | 2.5.1 | https://www.elastic.co/blog/category/customers |
| A10 | **KPMG Technology consulting** | 专业服务 | 从传统 SIEM 迁移到 Elastic Security，服务其客户 | 成本 **−75%**、存储 **×10** | **2025-11-07** | §2.5 平台级（不重复计入 2.5.1/2.5.2） | https://www.elastic.co/blog/category/customers |
| A11 | **Charter** | 托管服务（MSP） | 用 SolarWinds Incident Response 自动化事件生命周期、多渠道告警、智能去重降噪 | 事件确认时间 **−93%** | **2026-09-09**（窗口外） | 2.9.1 | https://www.solarwinds.com/resources/case-study/charter-case-study |
| A12 | **TV Insight** | 媒体/广告测量 | 峰值约 200 万请求/秒；集中告警 + 自动化 on-call 管理 | 加快告警确认、降低运营风险（**定性**） | **2026-09-09**（窗口外） | 2.9.3 | https://www.solarwinds.com/resources/case-study/tv-insight-case-study |
| A13 | **Dabble** | 在线博彩 | 采用 Grafana Cloud + Grafana Assistant 缩短事件响应 | 缩短事件响应时间（**定性**） | **2026-08-31**（窗口外） | 2.8.2 | https://grafana.com/press/ |

> **表 A 的诚实标注**：A1/A5/A6/A9/A12/A13 的"结果"为**定性表述**（官方页面未给量化数字），本稿**不为其编造百分比**；A11/A12/A13 的**时间属 2015-2025 窗口外**。**A10（KPMG）虽在窗口内且结果量化，但其场景属 Elastic Security 而非 Observability，故不归属某一 2.5.x 条目。**

#### 表 B：次级案例（21 个；有客户名与量化结果，但**缺官方日期**或**缺客户名**，故不计入表 A）

| # | 客户 | 厂商 | 场景 | 结果 | 时间 | 官方来源URL |
|---|---|---|---|---|---|---|
| B1 | Verisk | New Relic | 集成 New Relic MCP + AWS DevOps Agent，加速事件解决并优化基础设施成本 | 告警量 **−59%** | 官方页面未标注日期 | https://newrelic.com/customers |
| B2 | BlackLine | New Relic | 整合工具、简化监控 | 年节省 **$1,600 万** | 同上 | https://newrelic.com/customers |
| B3 | Kurt Geiger | New Relic | 构建 Dashboard 实时度量用户体验 | Core Web Vitals **+50%** | 同上 | https://newrelic.com/customers |
| B4 | Shutterstock | New Relic | 标准化到 New Relic，降低日志支出同时提升监控能力 | 报表生成时间 **−75%** | 同上 | https://newrelic.com/customers |
| B5 | Statista | New Relic | 用免费额度左移并弹性扩展可观测部署 | 延迟 **−95%** | 同上 | https://newrelic.com/customers |
| B6 | Watch Duty | New Relic | 野火应急实时信息服务；2025-02 加州山火期间支撑 10 倍突发扩容 | 支撑 **150 万+** 并发用户、**300 万** DAU | 页面未标注发布日期（正文记载 2025-02 事件） | https://newrelic.com/customers/watch-duty |
| B7 | State of Oregon OIS | IBM Instana | 支付应用 eXPRS 的性能问题与可见性缺失 | MTTD **−50%**、MTTR **−30%** | 页面未标注发布日期 | https://www.ibm.com/case-studies/state-of-oregon-ois |
| B8 | SIXT | IBM Instana | 出行服务商的数字化转型 | 定性 | 同上 | https://www.ibm.com/case-studies/sixt |
| B9 | Specsavers | Splunk | 可观测与自动化 | MTTR **快 10 倍**；单月预防 100+ 关键 / 500+ 重大事件；每月节省 25,000 小时 | 客户故事页未标注日期 | https://www.splunk.com/en_us/customers.html |
| B10 | Singapore Airlines | Splunk | 统一可观测提升客户体验 | 问题发现 **+75%**；后端问题 **−90%** | 同上 | https://www.splunk.com/en_us/customers.html |
| B11 | Children's National Hospital | Splunk | TDIR（威胁检测、调查与响应） | 威胁检出 **+40%**；分析师效率 **+25%** | 同上 | https://www.splunk.com/en_us/customers.html |
| B12 | Progressive Insurance | Splunk | 保护客户与收入 | 保护 **$1,200 亿**市值；采集 8M traces / 50M spans | 同上 | https://www.splunk.com/en_us/customers.html |
| B13 | Carrefour | Splunk | 安全威胁响应 | 威胁响应 **快 3 倍** | 同上 | https://www.splunk.com/en_us/customers.html |
| B14 | Tinder | Elastic | 基于 Elasticsearch 的大规模实时推荐检索（EKS + Elastic Cloud on K8s） | CPU 用量 **降低 4 倍**；scoring 延迟 **−47%**；过滤性能 **+60%** | 页面未标注发布日期 | https://www.elastic.co/customers/tinder |
| B15 | Siemens | Elastic | 全球网络防御（30 万端点/60 万用户）+ Amberg 灯塔工厂共用 Elastic 平台 | 每年回收 **约 5,000** 分析师小时；检测规则交付从 3–4 周积压降到 **<1 周**；日关联 **60 亿**事件 | 页面未标注发布日期 | https://www.elastic.co/customers/siemens |
| B16 | Banco Bradesco | Elastic | 统一软件交付与可观测 | 70,000+ 仓库 **100%** 管道可见性 | 列表页未标注发布日期 | https://www.elastic.co/customers |
| B17 | Smart DCC | Elastic | 安全运营；保护 1.24 亿设备 | 事件检出时间 **−84%** | 同上 | https://www.elastic.co/customers |
| B18 | Cathay Pacific | Elastic | 在 Elastic Cloud 统一可观测 | 运营噪声 **约 −30%** | 同上 | https://www.elastic.co/customers |
| B19 | UnderDefense | Elastic | 2 人安全团队从 QRadar 迁移到 AWS 上的 Elastic Security | 事件量 **−85%**；MTTR **−61%** | 官方博客列表页未显示其发布日期 | https://www.elastic.co/blog/category/customers |
| B20 | Salesforce | Grafana | Grafana Cloud 指标与日志支撑开发者体验 | FTE 基础设施监控时间 **−66%**；CPU **−50%**；每分钟处理 **7,000 万**指标 | 页面未标注发布日期 | https://grafana.com/success/ |
| B21 | Dell Technologies | Grafana | 指标采集与分析效率 | 每周节省 **6 小时**；团队效率 **+10%** | 同上 | https://grafana.com/success/ |

> **表 B 的用途**：这 21 条证明"官方案例是**可枚举**的"（v1.0 的"官方案例库无法枚举"结论已在 v1.1 被推翻），其唯一系统性缺陷是**厂商不在案例页标注日期**。**本稿不允许把这些缺"时间"的案例计入表 A**——这正是第 1 轮评审判定 v1.0"案例口径失真"的原因。

### 6.6 自评结论

- **结论：v1.1 达到"证据可复核、缺口如实登记"的状态，但按 00 号规范验收标准仍为不合格（需第 2 轮）**。达成的项：案例数 **13 ≥ 12**（表 A）、链接 100% 可达、**0 编造**、统计口径**完全可复核**、Broadcom 处置决断**已执行**、**15 条评审问题全部有处置**。**未达成的项**：① 9 字段完整率 **77.8% < 95%**；② 条目含 S/A 来源 **94.1% < 100%**；③ AI 条目严格口径 **10 < 12**；④ 有效技术条目 **34 < 35**（00 号规范 A+B 合计口径）；⑤ 字段 2（时间）仍有 29 条缺官方发布日——**这是本稿最大的结构性短板，其根因是"厂商官方页面普遍不标注产品首次发布日期 + 本环境为纯 HTTP 通道（无渲染）"**。
- **对第 2 轮的建议**：第 2 轮侧重"技术深度与原理正确性"。本稿已把 **G-07 剩余的 5 条**（Splunk ITSI / AppDynamics / AI Assistant、SolarWinds AIOps、W3C）明确标注为"原理待官方文档替换"，**建议第 2 轮优先核查这 5 条是否讲错**，而非继续追案例数量。

---

## 7. 全量来源清单（按厂商分组，带日期；计数规则见 §6.0-D）

> **清单说明**：① 仅列出**本稿实际抓取成功**的 S/A 级来源（**失败项一律不入清单**，改入 §7.12 官方来源缺失清单）；② 每条链接后附**发布/更新日期**（官方未标注者注明"官方未标注（页面快照于 2026-09-12 确认）"）；③ 标注来源类型与 S/A 等级；④ **计数为"逐条 URL 条目"**，与 §6.2 完全一致；⑤ 末尾给出**分级合计表**（响应 B-R1-13），并单列"官方来源缺失清单"。

### 7.1 Datadog（S 级 10 条 + A 级 0 条 = 10 条）

1. [Automatically discover, map, and monitor all your services in seconds with Universal Service Monitoring](https://www.datadoghq.com/blog/universal-service-monitoring-datadog/) — **发布 2021-10-26**（更新 2022-11-29）— 官方博客 — **S**
2. [Universal Service Monitoring（文档）](https://docs.datadoghq.com/universal_service_monitoring/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
3. [Universal Service Monitoring（产品页）](https://www.datadoghq.com/product/universal-service-monitoring/) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
4. **[Datadog Releases Continuous Profiler for Low-Overhead Application Code Profiling（官方新闻稿）](https://www.datadoghq.com/about/latest-news/press-releases/continuous-profiler/)** — **发布 2020-08-11**（宣布 GA；$12/host/月；客户 Cvent 证言）— 官方新闻稿 — **S** ← **v1.1 新增（闭环 B-R1-02）**
5. [Continuous Profiler（产品页）](https://www.datadoghq.com/product/code-profiling/) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
6. [Continuous Profiler（文档）](https://docs.datadoghq.com/profiler/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
7. [Introducing Bits AI, your new DevOps copilot](https://www.datadoghq.com/blog/datadog-bits-generative-ai/) — **发布 2023-08-03** — 官方博客 — **S**
8. [Network Monitoring（产品页，§5 P1-5 的引用锚点）](https://www.datadoghq.com/product/network-monitoring/) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
9. [Newsroom / 官方新闻室入口](https://www.datadoghq.com/about/latest-news/press-releases/) — 官方未标注（2026-09-12 确认）— 官方新闻室 — **S**
10. **[Our Customers（官方案例库，HTTP 200 实抓）](https://www.datadoghq.com/customers/)** — 官方未标注（2026-09-12 确认）— 官方案例库 — **S** ← **v1.1 新增（推翻 v1.0"案例库不可枚举"的结论）**

### 7.2 Dynatrace（S 级 12 条 + A 级 0 条 = 12 条）

1. [What is Dynatrace（官方文档）](https://docs.dynatrace.com/docs/discover-dynatrace/what-is-dynatrace) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
2. [Dynatrace Intelligence（官方文档，原 Davis AI 概念页）](https://docs.dynatrace.com/docs/dynatrace-intelligence) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
3. [Dynatrace 官网首页（含客户证言）](https://www.dynatrace.com/) — 官方未标注（2026-09-12 确认）— 产品页/官网 — **S**
4. [Dynatrace 投资者关系新闻稿列表](https://ir.dynatrace.com/news-events/press-releases) — 列表页最新条目 2026-08-25（2026-09-12 确认）— 官方新闻稿（IR）— **S**
5. [Dynatrace 新闻室新闻稿列表](https://www.dynatrace.com/news/press-release/) — 列表页最新条目 2026-08-25（2026-09-12 确认）— 官方新闻稿 — **S**
6. **[Dynatrace Expanding Davis to Deliver the Observability and Security Industry's First Hypermodal Artificial Intelligence…（官方 IR 新闻稿）](https://ir.dynatrace.com/news-events/press-releases/detail/302/dynatrace-expanding-davis-to-deliver-the-observability-and-security-industrys-first-hypermodal-artificial-intelligence-converging-predictive-causal-and-generative-ai)** — **发布 2023-07-25 8:00 am EDT** — 官方新闻稿（IR）— **S** ← **v1.1 新增（闭环 B-R1-10 ④）**
7. [Dynatrace 官方新闻稿 sitemap（用于挖掘客户案例 URL；**其 lastmod 与页面正文日期不一致，已从"发布时间"用途废止**）](https://www.dynatrace.com/news/press-release-sitemap.xml) — 抓取于 2026-09-12 — 官方站点地图 — **S**
8. **[Park 'N Fly speeds up development cycles by 29% with Dynatrace](https://www.dynatrace.com/news/press-release/park-n-fly-speeds-up-development-cycles-by-29-with-dynatrace/)** — **发布 2021-03-23** — 官方新闻稿 — **S** ← v1.1 新增
9. **[ERT helps medical researchers accelerate clinical trials with AI-assistance from Dynatrace](https://www.dynatrace.com/news/press-release/ert-helps-medical-researchers-accelerate-clinical-trials-with-ai-assistance-from-dynatrace/)** — **发布 2020-05-28** — 官方新闻稿 — **S** ← v1.1 新增
10. **[Mitchells & Butlers serves better business results with Dynatrace](https://www.dynatrace.com/news/press-release/mitchells-butlers-serves-better-business-results-with-dynatrace/)** — **发布 2019-12-19** — 官方新闻稿 — **S** ← v1.1 新增
11. **[Dynatrace enables speed and confidence in U.S. Government Agency's migration to the cloud](https://www.dynatrace.com/news/press-release/dynatrace-enables-speed-and-confidence-in-us-government-agencys-migration-to-the-cloud/)** — **发布 2020-02-11** — 官方新闻稿 — **S** ← v1.1 新增
12. **[Temenos enables seamless banking experiences with Dynatrace](https://www.dynatrace.com/news/press-release/temenos-enables-seamless-banking-experiences-with-dynatrace/)** — **发布 2020-10-01** — 官方新闻稿 — **S** ← v1.1 新增

### 7.3 New Relic（S 级 10 条 + A 级 0 条 = 10 条）

1. [New Relic 官网首页](https://newrelic.com/) — 官方未标注（2026-09-12 确认）— 产品页/官网 — **S**
2. [New Relic Observability Platform](https://newrelic.com/platform) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
3. [AI Observability for Modern Applications（AI 观测产品页）](https://newrelic.com/platform/ai-observability) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
4. [Guide to AI Observability: Core Components, Tools, and Best Practices](https://newrelic.com/blog/ai/ai-in-observability) — **日期：官方页面正文未标注发布日期**（2026-09-12 确认；⚠️ v1.0 引用的"lastmod 2026-07-20"已按 B-R1-08 废止）— 官方博客 — **S**
5. [New Relic 站点 sitemap（**仅用于发现 URL**，其 lastmod 不作发布时间使用）](https://newrelic.com/sitemap.xml) — 抓取于 2026-09-12 — 官方站点地图 — **S**
6. [Get started with New Relic（NRQL 定义）](https://docs.newrelic.com/docs/new-relic-solutions/get-started/intro-new-relic/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
7. [New Relic 新闻稿样例（确认 URL 规则 `press-release/YYYYMMDD` 有效）](https://newrelic.com/press-release/20240911) — **发布 2024-09-11** — 官方新闻稿 — **S**
8. **[CareerVillage and New Relic Transform EdTech with AI-Powered Career Coaching（官方新闻稿）](https://newrelic.com/press-release/20241001)** — **发布 2024-10-01**（含 67% 页面加载时间下降、133% 工程生产力提升）— 官方新闻稿 — **S** ← **v1.1 新增（闭环 B-R1-01）**
9. **[Our Customers（官方案例库，HTTP 200 实抓；含 Verisk/BlackLine/Kurt Geiger/Shutterstock/Statista 等具名量化案例）](https://newrelic.com/customers)** — 官方未标注（2026-09-12 确认）— 官方案例库 — **S** ← **v1.1 新增**
10. **[Watch Duty's real-time data model in wildfire emergencies（官方案例研究）](https://newrelic.com/customers/watch-duty)** — 页面未标注发布日期（2026-09-12 确认；正文记载 2025-02 加州山火事件）— 官方案例 — **S** ← v1.1 新增

### 7.4 Cisco / AppDynamics / Splunk（S 级 8 条 + A 级 0 条 = 8 条）

1. [Splunk IT Service Intelligence（产品页）](https://www.splunk.com/en_us/products/it-service-intelligence.html) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
2. [Splunk IT Service Intelligence 官方文档入口](https://help.splunk.com/en/splunk-it-service-intelligence) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
3. [Splunk AppDynamics（产品页，由 appdynamics.com 301 跳转）](https://www.splunk.com/en_us/products/splunk-appdynamics.html) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
4. [Splunk AppDynamics 官方文档入口](https://help.splunk.com/en/appdynamics-saas) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
5. [Splunk Observability Cloud（产品页，含 AI Assistant / AI SRE / Agent Observability）](https://www.splunk.com/en_us/products/observability-cloud.html) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
6. [Splunk Observability Cloud 官方文档入口](https://help.splunk.com/en/splunk-observability-cloud) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
7. **[Customer Stories（Splunk 官方案例库，HTTP 200 实抓；含 Specsavers / Singapore Airlines / Children's National Hospital / Progressive / Carrefour 具名量化案例）](https://www.splunk.com/en_us/customers.html)** — 官方未标注（2026-09-12 确认）— 官方案例库 — **S** ← **v1.1 新增（推翻 v1.0"案例库不可抓取"的结论）**
8. **[Press Releases（Splunk 官方新闻室，列表自 2020 年起按年分组至 2026）](https://www.splunk.com/en_us/newsroom/press-releases.html)** — 2026-09-12 确认 — 官方新闻稿列表 — **S** ← v1.1 新增

### 7.5 Elastic（S 级 11 条 + A 级 0 条 = 11 条）

1. [Application performance monitoring (APM)（官方文档）](https://www.elastic.co/docs/solutions/observability/apm) — 官方未标注（GA，2026-09-12 确认）— 官方文档 — **S**
2. [AI assistants in Kibana（官方文档）](https://www.elastic.co/docs/explore-analyze/ai-features/ai-chat-experiences/ai-assistant) — 官方未标注（GA，2026-09-12 确认）— 官方文档 — **S**
3. [Elastic AI Assistant for Observability and Search（官方文档）](https://www.elastic.co/docs/solutions/observability/ai/observability-ai-assistant) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
4. [Elastic Observability platform（产品页）](https://www.elastic.co/observability) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
5. [Elastic 官方博客 RSS](https://www.elastic.co/blog/feed) — 抓取于 2026-09-12 — 官方博客 RSS — **S**
6. [Elastic Observability: A solution for today's "always-on" world](https://www.elastic.co/blog/observability-powerful-flexible-efficient) — **发布 2023-03-27**（据官方 RSS）— 官方博客 — **S**
7. [End-to-end SAP Observability with Elastic, Google Cloud, and Kyndryl: A deep dive](https://www.elastic.co/blog/sap-observability-elastic-google-kyndryl) — **发布 2024-07-08** — 官方博客 — **S**
8. **[Customers（Elastic 官方博客客户分类页，**逐条标注发布日期**；含 SWIFT 2025-05-05、KPMG 2025-11-07、Burgan Bank Türkiye 2025-08-28、UnderDefense、Orange France 等）](https://www.elastic.co/blog/category/customers)** — 抓取于 2026-09-12 — 官方博客 — **S** ← **v1.1 新增（闭环 B-R1-01）**
9. **[Elastic Customers（官方案例库列表页，HTTP 200 实抓；含 Tinder / Siemens / Banco Bradesco / Smart DCC / Cathay Pacific 等具名量化案例）](https://www.elastic.co/customers)** — 官方未标注（2026-09-12 确认）— 官方案例库 — **S** ← v1.1 新增
10. **[Tinder® drives real-time recommendations across 190 countries（官方案例研究）](https://www.elastic.co/customers/tinder)** — 页面未标注发布日期（2026-09-12 确认）— 官方案例 — **S** ← v1.1 新增
11. **[Siemens reclaims ~5,000 SOC analyst hours a year on Elastic Security（官方案例研究）](https://www.elastic.co/customers/siemens)** — 页面未标注发布日期（2026-09-12 确认）— 官方案例 — **S** ← v1.1 新增

### 7.6 Broadcom（**S 级 1 条，且该 1 条不支撑任何 DX APM 字段**）

1. **[Broadcom Investor Center（官方投资者关系首页）](https://investors.broadcom.com/)** — 200 可达（2026-09-12 确认；含 09/02/26 财报、08/31/26 VMware AI 等新闻稿列表）— 官方投资者关系 — **S**
   - **⚠️ 重要限定**：该页面的**全部条目均与 DX APM / DX OI 无关**，因此**不能支撑 §2.6 的任何字段**，仅用于证明"Broadcom 官方域可达但无 DX APM 内容"这一判断。**§2.6 已因此降级为"证据不足的对照性附录"**（详见 §2.6 章首 9 条路径实测表）。
   - 其他实测可达但**无产品正文**的官方站点（**不计入来源清单**，仅记录）：`https://community.broadcom.com/`（200，社区首页；分区为 VMware/Tanzu/Mainframe/Symantec/ANS，**无 APM 分区**）、`https://docs.broadcom.com/`（重定向至 JS 外壳的下载搜索页）、`https://knowledge.broadcom.com/`（重定向至 support.broadcom.com 维护公告）。

### 7.7 IBM（S 级 8 条 + A 级 0 条 = 8 条）

1. [IBM Instana Observability（官方产品页）](https://www.ibm.com/products/instana) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
2. [Drive operational efficiency with GenAI observability](https://www.ibm.com/new/announcements/drive-operational-efficiency-with-gen-ai-observability) — **发布 2025-10-06**（更新 2026-03-23）— 官方新闻稿/公告 — **S**
3. [Advancing AI operations with AI Agent and LLM Observability](https://www.ibm.com/new/announcements/advancing-ai-operations-with-ai-agent-and-llm-observability) — **发布 2026-05-05** — 官方新闻稿/公告 — **S**
4. [IBM Instana GenAI Observability（官方产品页）](https://www.ibm.com/products/instana/generative-ai-observability) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
5. [IBM Instana Intelligent Incident Investigation（官方产品页）](https://www.ibm.com/products/instana/intelligent-incident-investigation) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
6. [IBM named a Leader in the 2026 Gartner® Magic Quadrant™ for Observability Platforms](https://www.ibm.com/new/announcements/ibm-named-a-leader-in-the-2026-gartner-magic-quadrant-for-observability-platforms) — **页面发布时间 2026-07-15**（据第 1 轮评审 AI 抽检 #21 实测的页面正文日期）— 官方新闻/公告 — **S**
7. **[State of Oregon OIS（IBM 官方案例研究，Instana：MTTD −50%、MTTR −30%）](https://www.ibm.com/case-studies/state-of-oregon-ois)** — 页面未标注发布日期（2026-09-12 确认）— 官方案例 — **S** ← **v1.1 新增（闭环 B-R1-01）**
8. **[IBM Case Studies（官方案例库，可按 `?q=Instana` 过滤，HTTP 200 实抓）](https://www.ibm.com/case-studies?q=Instana)** — 官方未标注（2026-09-12 确认）— 官方案例库 — **S** ← v1.1 新增

### 7.8 Grafana Labs（S 级 6 条 + A 级 1 条 = 7 条）

1. [Grafana Pyroscope OSS（产品页）](https://grafana.com/oss/pyroscope/) — 官方未标注（2026-09-12 确认；含 Phlare 2022 / Pyroscope 2021 原文，**不含收购日期**）— 产品页 — **S**
2. [Grafana Pyroscope（官方 GitHub 仓库）](https://github.com/grafana/pyroscope) — 官方未标注（2026-09-12 确认）— 官方 GitHub — **A**
3. [Grafana Labs Press（官方新闻室）](https://grafana.com/press/) — 条目日期至 2026-08-31（2026-09-12 确认）— 官方新闻稿列表 — **S**
4. [AI tools（Grafana Cloud 官方文档）](https://grafana.com/docs/grafana-cloud/ai-tools/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
5. [Grafana Cloud Machine Learning / Sift（官方文档）](https://grafana.com/docs/grafana-cloud/machine-learning/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
6. **[Adaptive Metrics（官方文档，HTTP 200 且正文完整）](https://grafana.com/docs/grafana-cloud/adaptive-telemetry/adaptive-metrics/)** — 官方未标注（2026-09-12 确认）— 官方文档 — **S** ← **v1.1 新增（闭环 B-R1-09 ②；v1.0 曾声明"未能取得"，该缺口本轮闭合）**
7. **[Success stories and case studies（官方成功案例页，HTTP 200 实抓；含 Salesforce / Dell Technologies 具名量化结果）](https://grafana.com/success/)** — 官方未标注（2026-09-12 确认）— 官方案例库 — **S** ← v1.1 新增

### 7.9 SolarWinds（S 级 8 条 + A 级 0 条 = 8 条）

1. [Monitoring and Observability（产品页，含 AIOps 表述）](https://www.solarwinds.com/observability) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
2. [SolarWinds Hybrid Cloud Observability（自托管产品页）](https://www.solarwinds.com/hybrid-cloud-observability) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
3. [SolarWinds Observability（SaaS 产品页）](https://www.solarwinds.com/solarwinds-observability) — 官方未标注（2026-09-12 确认）— 产品页 — **S**
4. **[Network Performance Monitor（NPM）官方产品页](https://www.solarwinds.com/network-performance-monitor)** — 官方未标注（2026-09-12 确认；含 multi-vendor、**NetPath™ hop-by-hop**、**PerfStack™**、动态基线、拓扑映射、无线与硬件健康原文）— 产品页 — **S** ← **v1.1 新增（闭环 B-R1-05）**
5. **[NetFlow Traffic Analyzer（NTA）官方产品页](https://www.solarwinds.com/netflow-traffic-analyzer)** — 官方未标注（2026-09-12 确认；含 NetFlow/sFlow/J-Flow/IPFIX、Flow Navigator、port 0 monitoring 原文）— 产品页 — **S** ← **v1.1 新增（闭环 B-R1-05）**
6. **[Charter automates IT incident response with SolarWinds（官方案例研究）](https://www.solarwinds.com/resources/case-study/charter-case-study)** — **Publish Date 2026-09-09**（事件确认时间 −93%）— 官方案例 — **S** ← v1.1 新增
7. **[TV Insight establishes automated visibility and ownership of alerts（官方案例研究）](https://www.solarwinds.com/resources/case-study/tv-insight-case-study)** — **Publish Date 2026-09-09** — 官方案例 — **S** ← v1.1 新增
8. [SolarWinds 官方 sitemap（用于定位 NPM/NTA 与官方案例 URL）](https://www.solarwinds.com/sitemap.xml) — 抓取于 2026-09-12 — 官方站点地图 — **S**

### 7.10 OpenTelemetry 生态 / Prometheus / eBPF 系（S 级 14 条 + A 级 10 条 = 24 条）

1. [OpenTelemetry Specification（官方 GitHub）](https://github.com/open-telemetry/opentelemetry-specification) — 官方未标注（2026-09-12 确认）— 官方 GitHub — **A**
2. [OpenTelemetry 官方规范](https://opentelemetry.io/docs/specs/otel) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
3. [OpenTelemetry 官方博客 RSS](https://opentelemetry.io/blog/index.xml) — 抓取于 2026-09-12 — 官方博客 RSS — **S**
4. [OpenTelemetry 项目状态页](https://opentelemetry.io/status/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
5. **[Context propagation（OpenTelemetry 官方文档，HTTP 200 且正文完整）](https://opentelemetry.io/docs/concepts/context-propagation/)** — 官方未标注（2026-09-12 确认；含 "The default propagator uses the headers specified by the W3C TraceContext specification" 与 `<version>-<trace-id>-<parent-id>-<trace-flags>` 原文）— 官方文档 — **S** ← **v1.1 新增（Leader 裁决 F / B-R1-07）**
6. [OpenTelemetry Collector（官方 GitHub）](https://github.com/open-telemetry/opentelemetry-collector) — 官方未标注（2026-09-12 确认）— 官方 GitHub — **A**
7. [OpenTelemetry Collector 配置文档](https://opentelemetry.io/docs/collector/configuration/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
8. [OpenTelemetry Collector 内部遥测 / 自监控](https://opentelemetry.io/docs/collector/internal-telemetry/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
9. [OpenTelemetry eBPF Profiler（官方 GitHub）](https://github.com/open-telemetry/opentelemetry-ebpf-profiler) — 官方未标注（2026-09-12 确认；含 **1% CPU / 250MB 内存**上界与内核 **5.4 / 5.10** 门槛）— 官方 GitHub — **A**
10. [OTel Profiles 信号 proto PR #775（官方 GitHub）](https://github.com/open-telemetry/opentelemetry-proto/pull/775) — 官方未标注（2026-09-12 确认）— 官方 GitHub — **A**
11. [Prometheus（官方 GitHub）](https://github.com/prometheus/prometheus) — 官方未标注（2026-09-12 确认）— 官方 GitHub — **A**
12. [Prometheus 官方文档站](https://prometheus.io/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
13. [Prometheus 官方下载页](https://prometheus.io/download/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
14. [Cilium Hubble 网络可观测文档（Cilium 1.20.1）](https://docs.cilium.io/en/stable/observability/hubble/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
15. [Cilium Tetragon（官方 GitHub）](https://github.com/cilium/tetragon) — 官方未标注（2026-09-12 确认）— 官方 GitHub — **A**
16. [Tetragon 官方文档](https://tetragon.io/docs/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
17. [Tetragon TracingPolicy 概念文档](https://tetragon.io/docs/concepts/tracing-policy/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
18. [Pixie（官方 GitHub）](https://github.com/pixie-io/pixie) — 官方未标注（2026-09-12 确认；含 **<5% / 多数 <2%** 集群 CPU 上界）— 官方 GitHub — **A**
19. [Pixie 官方数据源文档](https://docs.px.dev/about-pixie/data-sources/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
20. [PxL 官方参考](https://docs.px.dev/reference/pxl/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
21. [Coroot（官方 GitHub）](https://github.com/coroot/coroot) — 官方未标注（2026-09-12 确认；含 eBPF 采集、**80%+ 问题识别**、ClickHouse、SLO 单告警）— 官方 GitHub — **A**
22. [Coroot 官方文档](https://docs.coroot.com/) — 官方未标注（2026-09-12 确认）— 官方文档 — **S**
23. [groundcover（官方 GitHub 组织页）](https://github.com/groundcover-com) — 官方未标注（2026-09-12 确认）— 官方 GitHub — **A**
24. [caretta（官方开源仓库，K8s 服务依赖图）](https://github.com/groundcover-com/caretta) — 官方未标注（2026-09-12 确认）— 官方 GitHub — **A**

> **单列（不计入上表 24 条）**：[W3C Trace Context（官方标准页，**正文被 Cloudflare 拦截未能读取**）](https://www.w3.org/TR/trace-context/) — **官方来源缺失：w3.org 被 Cloudflare 人机校验拦截，正文与 Recommendation 日期不可读（2026-09-12 实测）** — 官方标准（W3C TR）。

### 7.11 非官方来源（仅用于原理补充，C 级）

1. [US11604718B1 专利（使用 `.eh_frame` 而非 DWARF 展开原生栈；由 OTel eBPF Profiler 官方 README 引用）](https://patents.google.com/patent/US11604718B1/en) — 官方未标注 — 专利文献 — **C**

### 7.12 S/A 分级合计表（v1.1 新增，响应 B-R1-13）

| 分节 | 厂商/项目 | S 级 | A 级 | 小计 |
|---|---|---|---|---|
| 7.1 | Datadog | 10 | 0 | **10** |
| 7.2 | Dynatrace | 12 | 0 | **12** |
| 7.3 | New Relic | 10 | 0 | **10** |
| 7.4 | Cisco / AppDynamics / Splunk | 8 | 0 | **8** |
| 7.5 | Elastic | 11 | 0 | **11** |
| 7.6 | Broadcom（**不支撑 §2.6 任何字段**） | 1 | 0 | **1** |
| 7.7 | IBM | 8 | 0 | **8** |
| 7.8 | Grafana Labs | 6 | 1 | **7** |
| 7.9 | SolarWinds | 8 | 0 | **8** |
| 7.10 | OpenTelemetry 生态 / Prometheus / eBPF 系 | 14 | 10 | **24** |
| — | W3C（正文不可读，**不计入可用来源**） | 0 | 0 | 1（单列） |
| **合计** | — | **88** | **11** | **99 条可用 S/A 来源**（另有 1 条正文不可读，列示但不可用） |

> **复核方式**：本表"小计"逐列相加 = 10+12+10+8+11+1+8+7+8+24 = **99**；S 列相加 = **88**；A 列相加 = **11**；88 + 11 = 99 ✅。**与 §6.2 的数字完全一致。**
> **⚠️ v1.0 的计数错误已修正（B-R1-13）**：v1.0 §7.10 标题写"S 级 10 + A 级 13 = 23 条"，与其逐条标注**正好相反**（实为 S 更多）；本轮已按逐条标注重算并在本节给出合计表。

### 7.13 官方来源缺失清单（v1.1 更新，逐条登记）

| # | 位置 | 缺失的官方来源 | 缺失原因（实测，2026-09-12） | v1.1 处置 |
|---|---|---|---|---|
| M-01 | 2.6.1 Broadcom DX APM | 全部字段（收购日期、产品事实、案例、量化） | `techdocs.broadcom.com/.../dx-apm/26-1.html` 与 `26-0.html` → **404**；`broadcom.com/products/software/aiops/dx-apm` → **404**；`/products/software/aiops` → JS 外壳；`investors.broadcom.com/news-releases` 与 `/news-releases/all` → **404**；`investors.broadcom.com/` → 200 但**内容与 DX APM 无关** | **已闭环**：按 Leader 裁决 A 第 2 分支**降级为对照性附录**，不再悬挂 |
| M-02 | 2.6.2 Broadcom DX OI | 全部字段 | 同 M-01；`community.broadcom.com/` 虽 200，但社区分区**无 APM/DX OI** | **已闭环**：同上 |
| M-03 | 2.10.3 W3C Trace Context | 发布日期与规范正文 | `w3.org` **Cloudflare 人机校验拦截**（本轮复测仍返回 "Just a moment..."）；**不编造日期** | **部分闭环**：按 Leader 裁决 F 增设 **OTel Context Propagation 官方文档**（`traceparent` 结构与"OTel 默认采用 W3C 头"已由官方原文支撑）；W3C 条目保留，缺失声明保留 |
| M-04 | 2.9.2 SolarWinds NPM/NetFlow | 字段 2（首次发布日期） | **本轮已实测取得 NPM 与 NTA 官方产品页**（HTTP 200），但两页**均未标注产品首次发布日期** | **大部分闭环**：字段 3/5 已由官方原文替换；字段 2 仍缺 |
| M-05 | 2.7.2 Instana AutoTrace | 字段 2/3/6/7/8/9 | `ibm.com/products/instana/features` → 200 但 Features 区**确无 AutoTrace 入口**；`ibm.com/docs/en/instana-observability` → 200 但为文档壳页；试探专题路径 `.../1.0.0?topic=agents-autotrace` → **IBM 错误页**；IBM Docs 站内搜索为 JS 渲染 | **已闭环（处置）**：条目加 `【未取证·C 级推断】`，已从 §5 落地依据中移除 |
| M-06 | 2.10.9 groundcover | 字段 2/3/4/5/6/8 | `github.com/groundcover-com/groundcover` → **404**（主项目闭源） | **已闭环（处置）**：条目加 `【未取证·生态提及】` 前缀 |
| M-07 | 全稿"案例"字段 | 部分条目的专属案例（如 USM 专属案例、Bits AI 客户案例、AI Monitoring 客户案例） | **厂商案例页普遍不标注发布日期**（Dynatrace/New Relic/Splunk/IBM/Elastic/Grafana 的案例页与新闻稿已可抓取，但除新闻稿外多数无日期） | **大幅改善**：已补 **13 个五要素齐备案例**（§6.5 表 A）+ **21 个次级案例**（表 B）；剩余缺口为"每条目 1 个"，需渲染型环境读取案例页时间戳 |
| M-08 | 2.4.x Cisco 收购日期 | Cisco 收购 AppDynamics（2017-03）、完成收购 Splunk（2024-03）官方新闻稿 | `investor.cisco.com/news-releases` → **Cloudflare "Just a moment..."**；`newsroom.cisco.com/.../press-releases.html` → JS 渲染，返回 **"No articles found"**；newsroom 索引页可访问但不暴露新闻稿正文 | **未闭环（已按 B-R1-10 加不确定性标记）**：§1/§2.4.x/§3.1 三处统一加 `【待核验】` |
| M-09 | 2.10.1 / 2.10.10 / 3.1 | OTel 成立公告（2019-05）、Prometheus 加入 CNCF 公告（2016） | OTel 官方博客 RSS **仅回溯至 2026 年**；CNCF 官方公告未抓取 | 未闭环：已统一加 `【待核验】` |
| M-10 | 2.3.1 / 2.3.2 / 2.3.3 New Relic 产品年份 | 平台统一 / AI Monitoring / New Relic AI 的官方首次发布页 | `newrelic.com/press-release/*` 规则**已实测有效**，但**未在这批 URL 中找到这三个产品的对应发布稿** | **部分闭环**：**已废止 sitemap lastmod 依据**（B-R1-08 ①），改标 `【待核验】`；新增 `20241001` 作为可验证的官方发布样例 |
| M-11 | 2.6 章（新增） | Broadcom 官方 PDF 白皮书 | 未找到官方 PDF 直链（`docs.broadcom.com` 重定向至 JS 外壳） | 归入 M-01/M-02 的降级处置 |


---

## 附录A 本稿版本与修订记录

| 版本 | 日期 | 说明 |
|---|---|---|
| v1.0 | 2026-09-12（页面快照基准日） | 初稿。10 厂商全覆盖；技术条目约 33 条（口径混乱）；AI 条目 10-16 条（口径见 6.1）；S/A 级来源约 45 条（口径混乱）。**已知主要缺口：案例数不足（约 3 vs ≥12）、Broadcom 整章无官方来源、W3C 条目正文不可读。** |
| **v1.1** | **2026-09-12（第 1 轮评审修订版，页面快照基准日不变）** | **按 `review/B-评审报告-第1轮.md` 的 15 条问题（P0 4 / P1 7 / P2 4）与 Leader 硬性裁决 A–F 完成修订。主要变更**：① **案例 0 → 13 个五要素齐备**（§6.5 表 A）+ 21 个次级案例（表 B）；② **Datadog Continuous Profiler 日期全部改为 2020-08-11**，消除跨章节互斥；③ **§2.6 Broadcom 按 Leader 裁决 A 第 2 分支降级为"证据不足的对照性附录"**（9 条官方路径实测表 + §4/§5 依赖论断逐处改写）；④ **统计口径全面重算并公开算法**：有效技术条目 **34 条**、9 字段完整率 **77.8%（238/306）**、含 S/A 来源 **94.1%（32/34）**、S/A 来源 **99 条（S 88 + A 11）**、案例 **13 个**；⑤ **废止 sitemap lastmod 作为"首次发布时间"依据**（New Relic 三条 + 以 Dynatrace 4 条新闻稿实证 lastmod 与正文日期相差 8–14 个月）；⑥ 新增 **Dynatrace 超模态 AI 官方 IR 新闻稿（2023-07-25）**、**Grafana Adaptive Metrics 官方文档**、**SolarWinds NPM/NTA 官方产品页**、**OpenTelemetry Context Propagation 官方文档** 等来源；⑦ 全部无来源时间点统一加 `【待核验】`，超窗口信息加 `【2026延伸·窗口外】`；⑧ 新增 **附录B 第 1 轮评审问题闭环台账**（B-R1-01…B-R1-15 逐条响应）。 |

> **修订接口预留（v1.1 更新）**：
> - **案例缺口（M-07）** → 已按 Leader 建议的"官方 sitemap 挖掘 + 单页直取"策略补齐 13 个五要素案例；剩余"每条目 1 个"的缺口需渲染型环境读取案例页时间戳；
> - **Broadcom（M-01/M-02）** → **已完成决断**：降级为对照性附录，不计入条目数与分母，§4/§5 依赖处逐处改写；
> - **推断型原理（G-07）** → 各条目字段 5 末尾保留"**推断边界**"段落；v1.1 已闭环 2.8.3 与 2.9.2 两条，剩余 5 条已列出清单供第 2 轮核查；
> - **时间精度（G-08）** → 字段 2 统一采用"官方未明确 + `【待核验】`"格式；有 S 级页面正文日期的直接写精确日期；
> - **新增厂商/条目** → 第 2 章按 `### 2.x {厂商}` + `#### 2.x.N {厂商} - {技术名}` 命名；**降级/未取证条目在标题加 `【降级·对照性附录】` / `【未取证·C 级推断】` / `【未取证·生态提及】` 前缀**；
> - **新增建议** → 第 5 章按 `**P{0|1|2}-N｜标题**` + 5 行格式追加，并同步更新 5.1 汇总表。

---

## 附录B 第 1 轮评审问题闭环台账（B-R1-01 … B-R1-15 逐条响应）

> **说明**：本表逐条对应 `review/B-评审报告-第1轮.md` 的 15 条问题（P0 4 / P1 7 / P2 4），**无漏项**。状态分三档：**已闭环**（问题已被实质解决）、**部分闭环**（主要缺口已解决但仍有残余，残余项已如实登记）、**无法闭环**（受本环境能力限制，已采取替代处置并说明原因）。

| 问题编号 | 严重级别 | 修改内容 | 修改位置 | 状态 |
|---|---|---|---|---|
| **B-R1-01** | **P0** | 案例数从 **0 → 13 个五要素齐备**（客户名+场景+结果+时间+官方来源URL），另登记 **21 个次级案例**；建立"表 A/表 B"两级口径；剔除 v1.0 的三类"伪案例"（无客户名的 IBM 发布事实、无客户名/无时间的 Dynatrace 首页证言、超窗口且无详情页的 Grafana 标题）。13 个案例 = Dynatrace 5（Park 'N Fly 2021-03-23 +29%、ERT 2020-05-28 6周→4周、M&B 2019-12-19 客单价+20%、Temenos 2020-10-01、VA 2020-02-11）+ Datadog 1（Cvent 2020-08-11）+ New Relic 1（CareerVillage 2024-10-01，页面加载−67%）+ Elastic 3（Burgan Bank 2025-08-28 事件响应+90%、SWIFT 2025-05-05、KPMG 2025-11-07 成本−75%）+ SolarWinds 2（Charter 2026-09-09 事件确认−93%、TV Insight 2026-09-09）+ Grafana 1（Dabble 2026-08-31） | **新增 §6.5 表 A / 表 B**；**§2.1.2、§2.2.2、§2.3.1、§2.5.1、§2.5.2、§2.8.2、§2.9.1、§2.9.3 字段 8** 逐一改写；§7.2/7.3/7.5/7.9/7.8 补入案例来源 URL | **已闭环**（13 ≥ 12；窗口内 10 个。残余：字段 8 仅 8/34 条"齐"，因厂商案例页普遍不标注日期——已登记为 G-01/M-07） |
| **B-R1-02** | **P0** | Datadog Continuous Profiler 日期三处统一为 **2020-08-11**；补入官方 S 级新闻稿 URL；字段 8 填入 **Cvent** 五要素案例 | **§2.1.2 字段 2 / 字段 8 / 字段 9**；**§1 总览表 Datadog 行**（"2023 Continuous Profiler" → "2020-08-11 Continuous Profiler GA（官方新闻稿，本轮修正）"）；**§3.1 时间线 2020 行**新增该事件 | **已闭环**（§1 / §2.1.2 / §3.1 三处一致且等于 2020-08-11） |
| **B-R1-03** | **P0** | Broadcom 章按 Leader 裁决 A「方案A + 硬性截止线」**执行第 2 分支降级**：新增章首显著声明 + **9 条官方路径实测结果表**（investors.broadcom.com 首页 200 但内容无关、/news-releases 404、/news-releases/all 404、CA 收购稿 guessed URL 404、community.broadcom.com 200 但无 APM 分区、docs.broadcom.com 重定向 JS 外壳、knowledge.broadcom.com 重定向维护页、/products/software/aiops JS 外壳、techdocs 26-0.html 404）；2.6.1/2.6.2/2.6.3 标题加 `【降级·对照性附录】`；三条**不计入有效条目数与覆盖率分母**；删除"存量客户多为金融/政府故披露保守"的推断句；§4 三处、§5 一处依赖 Broadcom 的论断**逐处改写** | **§2.6 章首 + 2.6.0–2.6.3**；**§4「分析范式」「交付形态」「成熟度」三行**；**§3.1 的 2016/2018/2024 行**；**§6.1/§6.4 G-02**；**§7.6/§7.12 M-01/M-02** | **已闭环**（决断已执行，无悬挂） |
| **B-R1-04** | **P0** | 新增 **§6.0 统计口径与算法说明**（条目计数规则、9 字段逐字段判定规则、案例五要素定义、S/A 计数规则、待核验标注规则）；**全稿只保留一个条目数 34**；重算并统一：条目 34、9 字段完整率 77.8%（238/306，附 §6.3 逐字段缺失清单表）、含 S/A 来源 94.1%（32/34）、S/A 来源 99 条（S 88 + A 11，附 §7.12 分级合计表）、案例 13；**修正 §7.10 标题的 S/A 计数错误**（v1.0 写"S 10 + A 13"，实为相反） | **§6.0（新增）、§6.1、§6.2、§6.3（新增）、§7.12（新增）**；§1 总览表与 §3.1 同步 | **已闭环**（五处口径一致，可逐条复算；与第 1 轮评审独立复核 77.5% 方向一致） |
| **B-R1-05** | P1 | SolarWinds NPM/NTA 条目**从"无任何官方来源"升级**：实抓 **NPM 官方产品页**（multi-vendor 设备监控、NetPath™ hop-by-hop 路径、PerfStack™ 跨域同轴、动态基线、拓扑映射、无线与硬件健康）与 **NTA 官方产品页**（NetFlow/sFlow/J-Flow/IPFIX、Flow Navigator、port 0 monitoring）；字段 3/5 由 C 级推断改为官方原文；新增 2 个官方五要素案例（Charter、TV Insight，Publish Date 2026-09-09）；字段 8 保持"不独立登记"并说明规则；**§5 P1-5 的对照项同步改写**为"SolarWinds NPM（2.9.2，官方产品页原文）" | **§2.9.2 字段 2/3/5/8/9**；**§2.9.1 字段 8/9**；**§2.9.3 字段 8/9**；**§5 P1-5 + §5.1 汇总表**；§7.9 | **部分闭环**（字段 2"官方发布日"仍缺——两产品页均未标注发布日期，已登记 M-04） |
| **B-R1-06** | P1 | ① 按建议复测 IBM 官方文档：`ibm.com/products/instana/features` 确无 AutoTrace 入口；`ibm.com/docs/en/instana-observability` 为文档壳页；试探专题路径返回 IBM 错误页（**已穷尽建议路径**）；② 条目标题加 **`【未取证·C 级推断】`** 并在条首加显著未取证声明；③ **§5 P0-2 第④点改为去厂商绑定的通用表述**（不再"对标 Instana AutoTrace"）；④ **§5.1 汇总表的"来源厂商/项目"列本就不含 2.7.2**（v1.0 仅 P0-2 正文引用），已一并核验确认 | **§2.7.2 标题 + 条首声明 + 字段 9**；**§5 P0-2 ④**；§6.4 G-05；§7.13 M-05 | **已闭环**（按评审的"若仍不可得"分支执行：去除厂商绑定 + 条目标记） |
| **B-R1-07** | P1 | ① W3C 页面本轮复测**仍被 Cloudflare 拦截**（"Just a moment..."），按 Leader 裁决 F **不编造日期**，字段 2 改为 `日期：官方未标注（w3.org 被 Cloudflare 人机校验拦截）`，并**删除了 v1.0 的"2021-11"**；② **不替换** W3C 条目（保留"W3C 标准"这一标准化事实），**改为一并增设 OpenTelemetry 官方 Context Propagation 文档**作为佐证来源——该文档本轮实抓 200 且正文完整，逐字给出 `traceparent` 结构 `<version>-<trace-id>-<parent-id>-<trace-flags>` 与"OTel 默认传播器使用 W3C TraceContext 头"；③ 字段 5 由"C 级领域常识"升级为**官方文档原文支撑**；字段 7 由"推断为事实标准"降级为"部分取证 + 待核验" | **§2.10.3 字段 2/5/6/7/8/9**；**§7.10 第 5 条（新增）**；§3.1 2021 行；§6.4 G-03；§7.13 M-03 | **部分闭环**（W3C 正文仍不可读 → 已按裁决采取替代处置并保留缺失声明，不编造日期） |
| **B-R1-08** | P1 | ① **废止 sitemap lastmod 作为"首次发布时间"**：New Relic 2.3.1/2.3.2/2.3.3 三处改写为 `【待核验：原依据 sitemap lastmod，该证据已废止】`；② **用 Dynatrace 官方数据实证该判定**：4 条 2019-2021 年新闻稿在官方 `press-release-sitemap.xml` 中的 lastmod 被统一写成 2020-12-04/2020-08-06，而正文日期分别为 2019-12-19/2020-10-01/2020-05-28/2020-02-11（相差 8–14 个月）；③ **Pixie 年份两处统一为 2020-12【据公开报道，未取得官方来源】**（§1 从"2022"改为"2020-12"）；④ 字段 2 凡推断者统一加 `【待核验】`，§1 总览表同步加标记；⑤ 新增 New Relic 官方新闻稿 `20241001`（2024-10-01）证明发布页可枚举 | **§2.3.1/2.3.2/2.3.3 字段 2**；**§2.2.2 字段 8 的方法论实证段**；**§2.10.5 字段 2**；**§1 总览表 New Relic 行 + 标注规则**；§6.4 G-08；§7.3/§7.2 | **已闭环**（证据类型错误已消除；Pixie 年份已统一；残余"产品首发日期"仍缺，已登记 G-08/M-10） |
| **B-R1-09** | P1 | ① **撤回"2023-03 收购 Pyroscope 来自 Grafana 官方产品页原文表述"的过度归因**，改为"据公开报道，未取得官方来源"；并把"官方产品页原文"的适用范围**精确限定**为 Phlare 2022 / Pyroscope 2021 两句（该两句确在页面内）；② **用官方文档原文替换 §2.8.3 字段 5 的推断段**（`grafana.com/docs/grafana-cloud/adaptive-telemetry/adaptive-metrics/` 本轮实抓 200，含 "identify and eliminate unused time series data through **aggregation**"、"aggregating underutilized metrics into **lower-cardinality versions**"、"**continuously reanalyzes** your usage"），推断边界段相应收缩为"仅聚合决策算法未公开"；③ 复查同类归因，§2.8.1/§3.1 同步改写 | **§2.8.1 字段 2/字段 8/字段 9**；**§2.8.3 字段 5/字段 8/字段 9**；**§3.1 2023 行**；§7.8 | **已闭环**（归因与陈述一致；Adaptive Metrics 缺口闭合） |
| **B-R1-10** | P1 | ① Cisco 两次收购（2017-03 / 2024-03）与 Cognition Engine（2021 前后）在 **§1 总览表、§2.4.0、§2.4.2、§3.1** 四处**统一加 `【待核验】`**，禁止确定语气；② ITSI 首发（2014-2016）与 Splunk AI Assistant（2023-2024）同样加 `【待核验】`；③ **Davis CoPilot 从 §3.1 的 2024 行移入 2023 行**，并引官方 IR 新闻稿 **2023-07-25**（S 级，本轮实抓，含"industry's first hypermodal artificial intelligence"与 Davis CoPilot™ 首次命名）；④ 2019 Davis 品牌化降级为 `【待核验】` | **§1 总览表 Cisco/Dynatrace 行**；**§2.2.2 字段 2/字段 9**；**§2.4.0/2.4.1/2.4.2/2.4.3 字段 2**；**§3.1 的 2017/2019/2023/2024 行**；§7.2；§7.13 M-08 | **部分闭环**（Davis CoPilot 时间错误**已闭环**、全部待核验标记**已加**；Cisco 收购官方新闻稿仍不可得——`investor.cisco.com` 与 `newsroom.cisco.com` 均被 Cloudflare/JS 阻断，已登记 M-08） |
| **B-R1-11** | P1 | ① **§2.6.2（Broadcom DX OI，无源 AI 条目）已从 AI 条目计数中剔除**（并整章降级）；② **明确两种口径定义与各自达标判定，且明确以严格口径判定为"不达标"**：严格口径 = 10 条（2.1.3、2.2.2、2.3.2、2.3.3、2.4.3、2.5.2、2.7.3、2.8.2、2.9.3、2.10.8）< 12 → **不达标**；宽口径（含 AI 增强）= 17 条 → 达标。**明确禁止以宽口径覆盖严格口径的不达标** | **§6.1「AI 相关条目」行**（重写） | **已闭环**（计数模型可复核；严格口径不达标已如实写出） |
| **B-R1-12** | P2 | §5 P1-5 的"来源厂商/项目"列由错误的"Datadog（2.1.1 来源组中的 Network Monitoring 产品页）"改为"**Datadog Network Monitoring 产品页（引用锚点：§7.1 #7）**"，并在 §7.1 第 8 条明确标注"**§5 P1-5 的引用锚点**"；同时把 SolarWinds 由"推断项"升级为官方产品页原文来源 | **§5 P1-5**；**§7.1 第 8 条**；§5.1 汇总表 P1-5 行 | **已闭环**（建议的"来源厂商/项目"现均可溯源到 §2.x 字段 9 或 §7 清单） |
| **B-R1-13** | P2 | ① 重算 §6.2 与 §7 各分节标题的 S/A 计数：**§7.10 标题由错误的"S 级 10 + A 级 13"修正为"S 级 14 + A 级 10"**；② **新增 §7.12「S/A 分级合计表」**，逐厂商列出 S/A 小计，并给出逐列相加的复核式（10+12+10+8+11+1+8+7+8+24 = 99；S 88 + A 11 = 99）；③ §6.2 的 S/A 条数与分布与 §7.12 完全一致 | **§7 全部小节标题 + §7.12（新增）**；**§6.2** | **已闭环**（§6.2 与 §7 逐项相加等于文中总数） |
| **B-R1-14** | P2 | ① 文档头新增**「版本阅读须知」**并保留"页面快照基准日 2026-09-12"；② **§1 总览表全部 2026 依据统一加 `【2026延伸·窗口外】`**（Datadog/Elastic/IBM/Grafana 的 2026 Gartner MQ、Grafana 10,000 客户等）；③ §3.1 时间线的所有 2026 事实**不加进 2015-2025 表**，保留在 §3.2"2026 延伸注记"；④ **§4 与 §5 中凡以 2026 事实为现状依据处加注**：§4「交付形态」保留了 SolarWinds 自托管/Splunk 本地部署（非 2026 事实），§5 P1-3 的 OTel GenAI 语义约定与 Grafana MCP Server 已标注"延伸注记"；⑤ 新增 **§6.0-E 标注规则**（待核验/窗口外）与 §3.1 的"待核验共 16 处"清单 | **文档头**；**§1 总览表 + 其下的标注规则段**；**§3.1 方法论说明 + §3.2**；**§5 P1-3**；**§6.0-E** | **已闭环**（超窗口事实在正文、表格、结论三处均有统一标注） |
| **B-R1-15** | P2 | Pixie 收购年份在 **§1 总览表**与 **§2.10.5 字段 2** 统一为 **`2020-12【据公开报道，未取得官方来源】`**（§1 原写"2022 收购 Pixie"已删除）；并登记本轮反证尝试 `newrelic.com/press-release/20201209` → **404**，与第 1 轮评审的试探结果一致 | **§1 总览表 New Relic 行**；**§2.10.5 字段 2** | **已闭环**（两处年份一致，证据状态标注明确） |

### 附录B.1 闭环统计

| 状态 | 条数 | 问题编号 |
|---|---|---|
| **已闭环** | **11** | B-R1-01、B-R1-02、B-R1-03、B-R1-04、B-R1-08、B-R1-09、B-R1-11、B-R1-12、B-R1-13、B-R1-14、**B-R1-15**（两处年份已统一，证据状态标注明确） |
| **部分闭环**（残余项已在 M-01…M-11 逐条登记） | **4** | **B-R1-05**（SolarWinds NPM/NTA 字段 2"官方发布日"仍缺 → M-04）、**B-R1-06**（AutoTrace 仍无官方来源，已按评审"若仍不可得"分支处置：去厂商绑定 + 条目标记）、**B-R1-07**（W3C 正文仍不可读，已按 Leader 裁决 F 替代处置且不编造日期）、**B-R1-10**（Cisco 两次收购官方新闻稿仍不可得 → M-08） |
| **无法闭环** | **0** | — |
| **合计** | **15** | **与第 1 轮评审判定的 P0 4 + P1 7 + P2 4 完全对应，无漏项** |

> **口径说明（最终统计）**：**已闭环 11 条 / 部分闭环 4 条 / 无法闭环 0 条 = 15 条**。**15 条全部有明确处置，无漏项。**"部分闭环"的 4 条均属"**受本环境能力限制（Cloudflare 拦截 / JS 渲染 / 官方页面不标注日期）而无法取到唯一缺失证据**"，且全部已按 Leader 裁决或评审给出的替代分支完成处置。
> **本轮未能拿到、且已在 M-01…M-11 逐条登记的官方来源**：Broadcom DX APM/DX OI 全部（M-01/M-02/M-11）、W3C 规范正文（M-03）、SolarWinds NPM/NTA 发布日（M-04）、Instana AutoTrace 文档（M-05）、groundcover 产品文档（M-06）、部分条目专属案例页时间戳（M-07）、Cisco 两次收购新闻稿（M-08）、OTel 成立与 Prometheus CNCF 公告（M-09）、New Relic 三个产品的首发页（M-10）。

<!-- 文件结束标记：本稿 v1.1（第1轮评审修订版） -->

---
