---
title: ManageEngine 功能体系与痛点解法（2023–2026）
company: ManageEngine（Zoho Corporation 企业 IT 管理事业部，manageengine.com / zoho.com）
category: 业界分析 / IT 运维管理与安全运营（ITOM / ITSM / UEM / SIEM / PAM）
period: 2023-01 ~ 2026-10
created: 2026-10-14
tags:
  - IT运维管理
  - 网络可观测性
  - APM
  - AIOps
  - AgenticAI
  - Zia
  - ITSM
  - SIEM
  - UEM
  - PAM
  - 竞品分析
  - 痛点解法
---

# ManageEngine 功能体系与痛点解法（2023–2026）

> **调研对象**：ManageEngine —— Zoho Corporation 旗下的企业 IT 管理事业部，产品线横跨网络与设备监控（OpManager / OpUtils / NetFlow Analyzer）、应用性能与数字体验监测（Applications Manager / Site24x7）、IT 服务管理（ServiceDesk Plus）、SIEM 与安全运营（Log360 / EventLog Analyzer）、统一终端管理与数字员工体验（Endpoint Central / DEX）、特权访问与身份治理（PAM360 / ADManager Plus）、IT 数据分析（Analytics Plus）与云成本治理（CloudSpend）。
> **调研范围**：2023-01 ~ 2026-10 公开发布的产品功能与能力增强，核心覆盖 ITOM 产品 12.6 → 12.9 分支、Applications Manager 17.x → 18、ServiceDesk Plus 本地 14xxx → 15200 与云版迭代、Log360 12xxx → 13000、Zia LLM 与 Zia Agents 全平台铺开。
> **交付内容**：① 按大功能点分组、标注时间与来源等级的小功能点清单（表格）；② 每个大功能点的「用户痛点 → 如何解决」详解，痛点编号 P1…Pn 与解法编号 S1…Sn 一一对应。

## 信源与局限（先看这一段）

采用**三级信源交叉验证**：

| 等级 | 信源 | 覆盖时段 | 用途 |
| --- | --- | --- | --- |
| A | 官方 **release notes / read-me / changelog / 官方产品文档 / 官方定价页 / 官方新闻稿**（manageengine.com、zoho.com/press、pitstop.manageengine.com 官方社区、store.manageengine.com） | 2023-01 ~ 2026-10 | 功能颗粒度（功能名 + build + 日期）与财务、定价事实的主依据 |
| B | 官方博客与区域站文章、ITOM/Site24x7 月度 Newsletter、主流行业媒体（CRN / TechTarget / The Hindu BusinessLine / financialcontent 等）、研究机构公开稿（Gartner / IDC / Forrester / KuppingerCole 转载页） | 2023-01 ~ 2026-10 | 平台级发布的主题与日期、分析师位置、机制细节 |
| C | 第三方评价平台与社区：G2、Gartner Peer Insights、PeerSpot、TrustRadius、Reddit r/sysadmin、cloo.ai / desk365 / siit.io 等评论聚合 | 2023-01 ~ 2026-10 | **客户真实体感与吐槽**、横评与交叉验证 |

**已知局限（务必先读）**：

1. **颗粒度上限分产品不齐**。ManageEngine 的 release notes 质量差异极大：`it-operations-management/read-me.html`（OpManager / OpManager Nexus / OpUtils / NetFlow Analyzer）可按 **build 号 + 日期**逐条提取；`site24x7.com/whats-new-in-site24x7.html` 可到**日**；ServiceDesk Plus / Log360 / Endpoint Central 有分产品 release notes。但**OpManager 与 Applications Manager 的 AI 相关功能在官方 consolidated 列表中多数不标日期**（如 Adaptive Thresholds、RCA、Zia Insights dashboard、Forecast Alerts），本文一律标注「**2025（约）**」并说明依据，**不编造日期**。**Firewall Analyzer 在窗口内未采到 A 级逐条 release notes**，其功能事实主要落在 B 级 ITOM Newsletter。
2. **厂商自述收益与第三方验证严格区分**。ManageEngine 大量使用营销口径（如「带宽预测准确率 >92%」「故障率下降 47%」「年省云成本 280 万元」「Forrester TEI 442% ROI」「MTTR 降低 60%」）。本文对**所有量化收益一律标注来源与口径**，凡为厂商自述或厂商委托研究，**不得当作第三方验证引用**。
3. **免费版额度与定价在官方站内自相冲突**。Site24x7 免费版在三个官方页分别写「50 个网站」「最多 50 个资源」「5 Websites/Servers」；OpManager Standard 的 $95 / $245 在不同第三方文里被错配到不同设备档位；ServiceDesk Plus 本地版两个官方 pricing 页价格互不相同。**本文并列列出并给出判定，不取平均**（详见附四）。
4. **「ManageEngine 是否触及设备内部」是本报告的关键边界问题**。经逐条核对官方文档，OpUtils / OpManager 的交换机侧采集**止步于标准 MIB**（Bridge MIB、Interface MIB、Q-BRIDGE-MIB）+ ARP 表 + LLDP/CDP；**未见任何官方文档描述读取 ACL 命中计数、FIB/路由表内部表项、ASIC/TCAM 表**的能力。凡无官方佐证者，本文一律标注「**未证实**」，不写入功能清单。
5. **资料截止 2026-10-14**。Zoho FY26（截至 2026-03）完整财报未获取到；OpManager / Applications Manager 部分 AI 功能的 GA 时点仍为「约」；Desktop Central 更名为 Endpoint Central 的官方公告日期未采到。

**本报告使用的核心 A 级信源**（按产品线）：

| 产品线 | A 级 release notes / 一手入口 |
| --- | --- |
| OpManager / OpUtils / NetFlow / Firewall Analyzer | `manageengine.com/it-operations-management/read-me.html`、`opmanager-release-notes.html`、`products/oputils/read-me.html`、`products/netflow/readme.html`、`uk/network-monitoring/eol.html` |
| Applications Manager | `products/applications_manager/release-notes.html`、`eu/applications_manager/eol.html`、`help/rbm-release-notes.html` |
| Site24x7 | `site24x7.com/whats-new-in-site24x7.html`、`site24x7.com/site24x7-pricing.html` |
| ServiceDesk Plus | `products/service-desk/readme-9.0.html`、`products/service-desk/cloud/whats-new.html`、`products/service-desk/pre-release-notes.html`、`itsm/2026-half-yearly-releases.html` |
| Log360 / EventLog Analyzer | `log-management/release-notes.html`、`log-management/features-new.html`、`log-management/cloud/features-new.html`、`products/active-directory-audit/adaudit-plus-release-notes.html` |
| Endpoint Central / DEX | `products/desktop-central/release-notes`、`products/desktop-central/ai/`、`autonomous-endpoint-management.html` |
| PAM / IAM | `privileged-access-management/release-notes.html`、`products/ad-manager/release-notes.html`、`products/self-service-password/release-notes.html` |
| 平台与 AI | `zoho.com/news/*`（OpenAI 集成 2023-05-04、Zia Agents 2025-02-04、Zia LLM 2025-07-17）、`manageengine.com/news/autonomous-ai-capabilities-manageengine-suite.html`（2026-05-21） |
| 定价与免费版 | 各产品 `pricing.html`、`store.manageengine.com`、`products/free-windows-tools/` |

---

## 公司速览

| 维度 | 内容 |
| --- | --- |
| 公司 / 成立 / 总部 | **Zoho Corporation**（原 AdventNet Inc.），1996 年由 Sridhar Vembu 与 Tony Thomas 创立；更名 Zoho 于 2009。国际总部印度金奈（Chennai），美国总部 Austin / 德州 Del Valle（原 Pleasanton, CA）。**ManageEngine 事业部成立于 2002 年**，是 Zoho 面向企业 IT 管理软件的品牌（A） |
| 上市 / 融资 | **私有、完全自力更生（bootstrapped）**：30 年从未接受 VC/PE 融资、无债务、未 IPO。股权高度集中在 Vembu 家族（第三方披露口径）（A / C） |
| 定位 | 「以可负担的价格交付企业级 IT 管理」——用**自研全套产品 + 农村研发中心低成本 + 直营与渠道并举**，在 SolarWinds / ServiceNow / Splunk / Datadog 的价格缝隙中做规模化替代（A / B） |
| 技术栈 | 探针-中心（Probe-Central）分布式采集架构、**SNMP / WMI / CLI（Telnet-SSH）/ WinRM / Flow（NetFlow·sFlow·IPFIX·NetStream）/ DPI / SNMP Trap（300 条/秒）/ Syslog / Agent** 全通道；APM 侧 **bytecode instrumentation**；AI 侧 **Zia LLM**（自研 1.3B / 2.6B / 7B，2025-11 起 Zia 底层切到 `Zia-zlabs-qwen3-30B-instruct-v1`）+ **MCP server**（A） |
| 部署形态 | **on-prem 自托管 + cloud SaaS 双轨**（几乎所有主力产品两者皆有）；Zia LLM 部署在 Zoho 自有数据中心（美 / 印 / 欧；中国为北京 + 上海），支持 on-prem、cloud、private cloud、闭网（A） |
| 关键指标（Zoho FY25，截至 2025-03） | 营业收入 **₹12,313 亿卢比（约 14.8 亿美元），同比 +17.8%**；净利 ₹3,191 亿卢比（同比 -3%）；总营收（含其他收入）₹13,544 亿卢比（B） |
| ManageEngine 收入占比 | FY25 ManageEngine 贡献 **₹4,863 亿卢比，占 Zoho 总收入 39%**（Zoho 套件 57%、其余服务 3%）。**ManageEngine 无独立于 Zoho 财报之外的单独营收披露**（B / C） |
| 客户与规模 | ManageEngine：**280,000 家组织 / 近 190 个国家**、**60+ 付费产品**（含免费工具则 120+）、20 处办公、18 个数据中心、5,000+ 员工（官方 fact sheet）；Zoho 集团 2026-02 宣布突破 **100 万付费用户 / 1.5 亿用户**，2025 自然年营收 +20%、客户 +32%（A / B） |
| 员工 | Zoho 官网 2026 年列 **19K+**；ManageEngine 事业部 5,000+（官方 fact sheet）；中国区另称研发与服务团队 6,000+（口径不一致，见附四）（A / B） |
| 权威背书 | **Gartner MQ**：PAM 挑战者（2023 与 2025-10）、UEM 挑战者（2026-01）、SIEM 2024 Major Player（2025 仅称「named in」）、DEM Niche Player（2024 首次入选 / 2025）、ITSM 中的 AI 应用 Niche Player（2025-09）、ITSM 挑战者（2026-08，**仅见中文站自述，待原文核实**）；**IDC MarketScape**：UEM 全球 Leader（2025-12，第三次）、ITSM Leader（2024）、SIEM Major Player（2026-06）；**Forrester Wave ESM Q4 2025 Strong Performer**；**KuppingerCole** PAM Market Leader（2026）、身份治理 Market Leader（2024）（A / B） |
| 第三方评分 | Endpoint Central G2 **4.5/5（1,142 评）**；Applications Manager G2 4.7/5（74 评）；OpManager G2 4.5/5（104 评）；Password Manager Pro Gartner Peer Insights 4.4（337 评）（C） |
| 代表客户 | **Samsung SDS**（Applications Manager，官方称 MTTR/MTTI 降低 60%，**厂商自述**）、Atlanta Hawks / State Farm Arena、5B（BFSI，PAM360）、Aerostar Airport Holdings、Kingspan、Lakeland Dairies；官方 awards 页列 AT&T / Barclays / Sony / GE / NASA / Siemens 等（**均属厂商自述，未见客户方公开确认**）（A / B） |
| 成本结构（解释其低价） | 官方称「超过一半营收投入 R&D」（另有 40% / 60% 两种口径，见附四）；不靠并购补产品线、几乎不打广告、农村研发中心压低人力成本；官方明确「我们唯一的赚钱方式就是你付的软件许可费」（A / B） |

**一句话看懂四年演进**：

> 2023–2024 **把 AI 接进来**（Zia 集成 OpenAI，生成式能力逐产品嵌入，仍是「帮你看」的助手）→ 2024–2025 **把模型换成自己的**（自研 Zia LLM 上线、Zia Insights 铺满 ITOM / ITSM / SIEM 三条线，模型可自选、可 BYOK、可本地）→ 2025–2026 **把动作交出去**（Zia Agents 全线 GA + 自主终端管理 + 原生 SOAR + MCP 开放，AI 从「答得上」变成「做得动、且留痕」）。

---

## 读法：9 个大功能点全景

| # | 大功能点 | 口号 | 小功能点数 | 时间跨度 |
| --- | --- | --- | --- | --- |
| 1 | AI 与自主智能体（Zia） | 从答得上到做得动 | 34 | 2023-05 ~ 2026-09 |
| 2 | 网络与设备监控（OpManager / OpUtils / NetFlow / Firewall） | 看得全 | 31 | 2023-04 ~ 2026-10 |
| 3 | 应用性能与数字体验监测（Applications Manager / Site24x7） | 追得透 | 36 | 2023-01 ~ 2026-09 |
| 4 | IT 服务管理（ServiceDesk Plus） | 管得住 | 22 | 2023 ~ 2026-09 |
| 5 | SIEM 与安全运营（Log360 / EventLog Analyzer） | 查得清 | 26 | 2024-02 ~ 2026-09 |
| 6 | 统一终端管理与数字员工体验（Endpoint Central） | 护得稳 | 18 | 2023-10 ~ 2026 |
| 7 | 特权访问与身份治理（PAM360 / ADManager Plus） | 守得住 | 19 | 2024-11 ~ 2026 |
| 8 | IT 数据分析与 FinOps（Analytics Plus / CloudSpend） | 算得明 | 14 | 2024 ~ 2026 |
| 9 | 商业化、交付与市场位置 | 买得起 | 16 | 2023-01 ~ 2026-10 |

> **合计 216 个小功能点**（时间窗内可溯源条目；官方未标日期者已显式注明「约」）。

> **读法提示**：**第 1 组是全部的叙事重心**——ManageEngine 2023 年后的核心动作不是「多加几个监控项」，而是把 AI 从各产品里的一个「功能」提炼成一个**跨产品的能力层**（Zia → Zia LLM → Zia Agents → MCP）。第 2、3 组是它的**传统主场**（网络运维 + 应用监控），也是与锐捷 APM 正面交锋的地方，**采数机制的边界**（能读到什么 / 读不到什么）比功能清单更有决策价值。第 4、5、6、7 组是「服务台 / 安全 / 终端 / 特权」四张侧翼，用**同一套 Zia 叙事**横向复用。第 8 组是把前七组的数据汇到一张报表上。第 9 组回答「为什么在价格敏感的客户群里它总能赢」。

---

# 大功能点 1：AI 与自主智能体（Zia）—— 从答得上到做得动

## 1.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 1.1 | Zia 集成 OpenAI（13 款应用 GenAI 扩展） | 2023-05-04 | A | Zoho 宣布把 ChatGPT 生成能力以扩展形式嵌入 13 个应用；同期明确「正在开发自有 LLM」 |
| 1.2 | ServiceDesk Plus Cloud：Zia 自动关闭 / 重开请求 | 2023-12 | A | Zia 解析用户回信，判断问题是否已解决并自动关闭；未确认则重开工单 |
| 1.3 | ServiceDesk Plus Cloud：Zia 请求自动审批 | 2024-01 | A | 依据审批人回信内容预测 Approve/Reject 并自动套用 |
| 1.4 | Log360 UEBA 实时异常检测 | 2024-02-08 | A | 为 EventLog Analyzer 报表配置实时异常检测，行为威胁发生即告警 |
| 1.5 | ServiceDesk Plus Cloud：Zia 聊天机器人新增 Ask ChatGPT 动作 | 2024-02 | A | 对话框内直接调用 ChatGPT 知识库作答，并统计调用次数与 token 消耗 |
| 1.6 | ServiceDesk Plus Cloud：Zia 预测式工单分诊 | 2024-07 | A | 建单 / 改单时预测类别、子类、模板、技术员与优先级 |
| 1.7 | ServiceDesk Plus Cloud：Zia 资产签收识别 + Deluge 低代码生成 | 2024-09 | A | 解析签收回执邮件判断资产签收；用一句提示词生成 Deluge 自定义函数 |
| 1.8 | Analytics Plus 6.0 Spotlight（AI 推荐引擎）+ RCA + 无代码 AutoML | 2024-10（约） | B | AI 引擎监控常见 IT 流程、识别瓶颈并给纠正策略建议 |
| 1.9 | ServiceDesk Plus Cloud：Zia 情绪分析 | 2024-11 | A | 预测请求人对话情绪基调，工单页展示分数 |
| 1.10 | ServiceDesk Plus Cloud：智能组 / 技术员 / 变更风险预测 + RAG 方案提取 + 会话摘要 + 事后复盘（PIR） | 2024-12 | A | 把工单路由到前三名技术员组；RAG 从知识库检索带引用生成方案；从最近 5 封邮件 + 笔记生成 PIR |
| 1.11 | Log360 Zia Insights（AI 安全分析） | 2024-12 | A | LLM 对日志做推理分类（error/security/operational）并自动映射 MITRE ATT&CK 战术/技术/子技术 |
| 1.12 | **Zia Agents + Zia Agent Studio + Agent Marketplace 公布（预览）** | 2025-02-04 | A | 自主智能体平台：预置 Agent（SDR / HR / 客服 / IT Help Desk 等）+ 无代码 Studio + 市场分发 |
| 1.13 | Site24x7 Ask Zia（AIOps 分析助手） | 2025-03-10 | A | 自然语言分析告警、报表与宕机记录，识别模式并生成摘要 |
| 1.14 | PAM360 特权任务自动化（PTA，Qntrl Circuits 驱动） | 2025-04-08 | A | 按需 / 定时在目标端点执行特权任务，凭据即时下发、任务结束自动回收 |
| 1.15 | PAM360 AI-Powered Insights（OpenAI / BYOK） | 2025-04-17 | A | 生成最小权限策略、云权限风险修复摘要、SSH/Telnet 会话录制摘要 |
| 1.16 | Log360 Cloud Zia Insights + UEBA | 2025-06-26 | A | Zia Insights 用 LLM（Azure OpenAI / BYOK）做告警摘要、ATT&CK 映射、时间线与修复建议；UEBA 用无监督学习检测行为偏移 |
| 1.17 | **Zia LLM（1.3B / 2.6B / 7B）+ 2 个 ASR 模型 + 25+ 预置 Agent + Agent Studio + MCP server** | 2025-07-17 | A | 自研 LLM 在自有 DC 推理；Agent Studio 全提示词化、开放 700+ 动作；MCP 把动作库开放给第三方 Agent |
| 1.18 | Site24x7 Zia + OpenAI / Azure OpenAI 集成（BYOK） | 2025-07-18 | A | 客户自配 OpenAI 或 Azure OpenAI，Zia 输出针对告警与指标的上下文回答 |
| 1.19 | Analytics Plus Ask Zia 智能体化 + MCP Server（Beta） | 2025-08-11 ~ 08-12 | A | Agentic AI 覆盖取数→转换→可视化→行动；Pipeline Builder 建管道、自然语言生成仪表板、诊断与处方式分析 |
| 1.20 | Endpoint Central DEX 数字员工体验 | 2025-08-26 | A | 持续监测 CPU/内存/磁盘异常 → 关联硬件老化等根因 → 一键或自动化修复 → 体验评分与基线对比 |
| 1.21 | **ServiceDesk Plus「史上最大 GenAI 版本」**：Ask Zia / Ask Zia Workflow Assist / Checklist·Script·Resolution·Solution Generator | 2025-09-10（发布）/ 2025-09-23（官宣） | A | Ask Zia 升级为多轮多模态（文本 / 语音 / 图像）虚拟坐席；Workflow Assist 读描述或**图片**生成可视化工作流并修复断点 |
| 1.22 | Analytics Plus Ask Zia Action Skills | 2025-10-24 | A | 在 Ask Zia 界面内直接导出数据、共享报表、调度邮件、生成洞察（Zoho LLM 驱动） |
| 1.23 | ADManager Plus Zia + Zia Insights | 2025-10-30 | A | 自然语言执行 AD 管理任务与报表；AD Explorer 做组成员异常检测、特权组识别与对等比较评分 |
| 1.24 | Zia 底层模型更新为 `Zia-zlabs-qwen3-30B-instruct-v1` | 2025-11-04 起 | A | Zia 切换到 30B 指令微调模型并宣称支持全部语言 |
| 1.25 | **集成 DeepSeek（面向中国）** | 2025-11-19 | A | ServiceDesk Plus 用中文 NL 做工单分类与解决；Site24x7 用 DeepSeek 做告警自动分组与根因下钻；与 Zia 形成「双 AI」选择 |
| 1.26 | ServiceDesk Plus 本地 v15200：Ask Zia（ChatGPT + MCP Tools） | 2025-12 | A | 本地版引入对话式 Ask Zia，由 ChatGPT 与 MCP 工具驱动；管理员可按工具 / 用户 / 组 / 角色逐项授权 |
| 1.27 | ServiceDesk Plus Cloud：RCA by Zia（根因分析报告） | 2025-12-12 | A | 依据相关事件与会话数据生成结构化 RCA（根因、促成因素、纠正与预防措施），以 Marketplace 扩展安装 |
| 1.28 | OpManager：Anomaly 仪表盘 + Anomaly Summary | 2026-01-20（Build 12.8.634） | A | 在 Zia 分支下新增异常聚合视图与摘要 |
| 1.29 | Endpoint Central EDR + Secure Private Access（AI 威胁检测与调查） | 2026-03-17 | B | 关联进程 / 文件 / 注册表 / 网络遥测并映射 MITRE ATT&CK；AI 行为分析检测无文件威胁 |
| 1.30 | NetFlow Analyzer MCP 服务器支持 | 2026-04-13（Build 12.8.719） | A | Claude Desktop / VS Code / Cursor 可经 MCP 访问 NFA 运行数据 |
| 1.31 | OpManager v12.8：OpenAI 集成 | 2026-04-21 | A | 集成 OpenAI 生成告警 / 设备摘要与自然语言脚本 |
| 1.32 | **Zia Agents 全产品线 GA** | 2026-05-21 | A | 预置 Agent 一键部署 + Zia Agent Studio 自然语言建 Agent + 多 Agent 编排 + 内置可观测审计 + MCP 对接第三方 LLM / Agent；**明确「客户数据不用于训练任何 AI 模型」** |
| 1.33 | ManageEngine 开发者生态：Marketplace 分发 Zia 智能体 | 2026-06-30 | A / B | 17+ 合作伙伴开发者发布 170+ 扩展，Zia Agent 成为 Marketplace 的分发入口 |
| 1.34 | ServiceDesk Plus Cloud：SLA 违约预测（by Zia）+ AI Insights + 自定义 Guardrails + 本地版接入 SiliconFlow | 2026-09-10 / 2026-09-23 | A / B | 依据历史工单主题 / 描述 / 平均耗时预测 SLA 违约概率与置信度；可对全部 GenAI 特性施加自定义 guardrails；本地版接入国产合规大模型 |

> **口径说明**：Applications Manager 的 `AI Alarm Summary`（四种摘要模式）与 `Monitor AI Insight`、OpManager 的 `Zia Insights dashboard / Zia Chatbot / Zia Metric Insights / Adaptive Thresholds / Forecast Alerts` 均已见于官方页面，但**官方未标注发布日期**（consolidated features 列表），本文不编造日期，统一在正文以「2025（约）」引用。

## 1.2 它对应的用户痛点

> **口径**：本节只写**客户侧可感知的痛**（时间 / 钱 / 人 / 合规 / 组织），不写架构层问题（如「日志格式杂乱」「查询语言门槛高」「schema 设计」）。痛点编号 P1…Pn 与下节解法 S1…Sn 一一对应。

- **P1｜出事的时候，懂的人往往不在**。排障能力高度绑定在少数老专家身上——他们知道这个错误码意味着什么、上次是怎么修的。这些知识留在个人记忆、过期的 Confluence 页面和聊天记录里；老专家一休假或离职，值班的人就只剩「重启和回滚」两招。（**人 / 时间**）
- **P2｜告警与工单的量已经超过人力上限**。而且大量告警「看起来都重要」，没有明确的优先级；值班人被噪声淹没，真信号被淹没在噪声里。客户能感受到的是：**值班人数不涨、告警量在涨**。（**时间 / 人**）
- **P3｜排障时间有大半花在「找信息」而不是「做判断」**。要判断一个故障，得在监控、日志、工单、知识库、聊天工具之间来回跳，每跳一次都要重建上下文。（**时间**）
- **P4｜把数据交给第三方大模型，安全与合规团队不放行**；而且「用哪个模型、谁来付钱、数据发到哪里、会不会被拿去训练」这些问题**被推给客户自己去做工程与合规决策**，AI 能力因此卡在安全评审而不是技术上。（**合规 / 钱**）
- **P5｜AI 说了什么、做了什么，没有痕迹，也没进既有流程**。结论留在个人浏览器会话里，不能分享、不能审计、不能进工单——等于**没有产生组织价值**；而让 AI 直接改生产环境，又因为没有审批与留痕而不被安全团队接受。（**合规 / 组织**）
- **P6｜AI 能力被锁在厂商自己的界面里**。客户团队已经在用 Cursor / Claude Desktop / VS Code 等工具，却无法让这些工具看到平台里的数据、更不能触发平台的动作。（**人 / 组织**）

## 1.3 它是如何解决的

先明确**架构约束**——它们不是客户痛点，而是由 1.2 的客户问题倒推出的设计约束，决定了「解必须长成这样」：

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| 助手必须出现在排障者已经在的地方，不能要求他再开一个窗口 | P1、P3 | Ask Zia 内嵌各产品、Zia Chatbot、OpManager / Site24x7 / AM 内嵌助手 |
| 「哪些告警值得看」必须由平台先筛一遍，不能全推给人 | P2 | 预测式 ML 分诊、自适应阈值、异常检测、告警关联、告警摘要 |
| 模型必须可替换、可不外发、可 BYOK、可本地 | P4 | 自研 Zia LLM、OpenAI / Azure / DeepSeek / Ollama / SiliconFlow 多路径、BYOK、闭网部署 |
| 数据出厂前必须可控，训练用途必须写死 | P4 | PII 匿名化与遮蔽、guardrails、官方「不用于训练」声明 |
| AI 的动作必须有审计链，且必须能被闸门拦住 | P5 | 代理会话全量记录、按工具 / 角色逐项授权、自定义 guardrails、动作经工作流与工单落地 |
| 平台能力必须能被外部 agent 生态调用 | P6 | MCP server（多产品）、Agent Marketplace、开发者生态 |

在上述约束下，逐条对应 P1–P6 的解法是：

- **S1｜Ask Zia：对话式助手内嵌到每一个产品里**（→ 解 P1、P3）。Ask Zia 不是独立门户，而是嵌进 ServiceDesk Plus（请求人默认落地页）、Site24x7（2025-03-10 起分析告警 / 报表 / 宕机）、Analytics Plus（自然语言取数→建管道→生成仪表板→执行动作）、Log360 / Log360 Cloud（自然语言转结构化日志查询）、ADManager Plus（自然语言执行 AD 任务）、Applications Manager / OpManager（告警与指标摘要）。2025-09 起，Ask Zia 从「问答框」升级为**多轮多模态虚拟坐席**（文本 / 语音 / 图像输入），并在 2025-12 随本地版 v15200 落地。**P1 的关键在于它把「查老手」换成了「问平台」，P3 的关键在于查询入口就长在排障界面里。**
- **S2｜预测式 ML + 零配置异常检测 + 自适应阈值**（→ 解 P2、P1）。ManageEngine 明确把 AI 分三档：**预测式 ML**（Zia Prediction Engine：工单分派、变更风险预测、相似事件聚类、情绪分析、SLA 违约预测）、**生成式 / 对话式 LLM**（Ask Zia、Resolution Assist、Workflow Assist）、**自主代理**（Zia Agents）。监控侧对应的是 **Adaptive Thresholds**（用 ML 每小时重算阈值，替代人工设阈值）、**Forecast Alerts / 容量规划**（预测资源耗尽时点）、**Alarm Correlation**（2024-07 起按预定义条件关联指标降噪）、**Anomaly 仪表盘与 Anomaly Summary**（2026-01-20）。**这些能力的意义不在「更准」，而在「客户不需要数据科学家、也不需要天天调阈值」。**
- **S3｜自研 Zia LLM + 多模型可替换路径**（→ 解 P4）。2023-05 先接 OpenAI；2025-07-17 自研 **Zia LLM（1.3B / 2.6B / 7B）** 在自有数据中心推理；2025-11-04 Zia 底层切到 `Zia-zlabs-qwen3-30B-instruct-v1`。客户侧同时有多条路径可选：**Zoho 托管**、**BYOK（OpenAI / Azure OpenAI / Google AI Studio）**、**本地模型（Ollama）**、**区域化模型（中国区 DeepSeek / SiliconFlow）**。对客户的意义是：**「换模型」不再等于「换平台」，而「数据不出境」也有一条现成的路。**
- **S4｜数据治理与 guardrails：把「能不能用」变成可配置项**（→ 解 P4）。官方明确「**客户数据绝不用于训练任何 AI 模型**」；本地版 Ask Zia 的调用可经 Zoho MCP 走**客户自己的 endpoint 与 key**；2026-09-10 起可对全部 GenAI 特性与 Ask Zia 施加**自定义 guardrails**（例如让设施部门实例只答设施类问题、排除 IT 话题）；国产路径上宣称 PII 匿名化与遮蔽。**这直接决定了 AI 能力能否通过客户的安全评审**。
- **S5｜Zia Agents + Agent Studio + Marketplace：把「答」升级为「做」**（→ 解 P2、P5）。2025-02-04 公布预览 → **2026-05-21 全产品线 GA**。机制是三层：**预置 Agent 一键部署**（ServiceDesk Plus Cloud Enterprise 内置 5 个，含 L1 支持代理、事件后回顾生成、请求解决代理）+ **Zia Agent Studio 用自然语言建自定义 Agent**（全提示词化、开放 700+ 动作）+ **多 Agent 编排**（master agent 调度 subagents 完成「员工入职」这类跨系统流程）。配套 Marketplace 分发（2026-06-30，17+ 伙伴 / 170+ 扩展）。**P5 的解法在这里才完整**：Agent 的每一次查询、调用的工具、执行的动作被完整记录，可审计；且 Agent 只能访问明确授权的数据与工具。**边界**：Zia Agents 仅归 ServiceDesk Plus Cloud **Enterprise 版**；跨产品的 Zoho 侧 Agent 平台按 token 计费（托管模型每月免费 10M token，超出 $1–$3 / 百万 token），与「产品内嵌 Zia 免费」不是同一层面。
- **S6｜MCP server：把平台开放给外部 agent 生态**（→ 解 P6）。ManageEngine 在多个产品上暴露 MCP：**NetFlow Analyzer（2026-04-13）**、**Analytics Plus（2025-08-12 Beta）**、**Log360 Cloud（2026-05-20，可从 Claude / Copilot / Cursor 调用）**、**ServiceDesk Plus Cloud（2026-10 Headless ITSM via Zoho MCP）**。**客户已有的 AI 工具因此可以直接读到平台数据并触发受支持的动作**——平台的边界从「厂商自己的 UI」扩展为「客户的 agent 生态」。

> **边界**：① 生成式 AI 的连接器与模型额度是外部依赖，跨区域可用性不一致（SLA Breach Prediction 仅 US / EU / IN 数据中心）；② OpManager / Applications Manager 的部分 AI 能力官方未标日期，成熟度难以核实；③ 第三方与客户反馈指出 **OpManager 的 AI 准确率自评仅 60%–70%**（PeerSpot 用户原话），「AI 未达可放心托付程度」，且官方客户案例中客户仍希望「接口利用率也能自适应」——**AI 兜底场景仍有残留**；④ Zia Agents 的跨产品 token 计费与「AI 免费」的营销口径容易混淆，采购时须逐项确认。

> **配套演进（找不到痛点归宿，单列于此）**：Zoho 领导层变动（Sridhar Vembu 2025-01-27 卸任 CEO 转任首席科学家，专注 AI / 深科技）属**公司治理沿革**；Zia LLM 从 7B 向 32B 的参数扩张计划（**未获官方确认发货**）属**技术路线**；「Zia」品牌名本身来自 Zoho 早期 AI 助手，属**命名沿革**。以上均不构成客户痛点，故不进 S 列表。

---

---

# 大功能点 2：网络与设备监控 —— 看得全

## 2.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 2.1 | OpManager 12.7 版本发布 | 2023-04-26 | A | 官方 EOL 页登记的版本发布日期 |
| 2.2 | NetFlow Pattern Analysis（ML 网络模式分析） | 2023-11 | B | 用 ML/AI 对关键性能指标自动做异常检测与阈值告警 |
| 2.3 | OpUtils：Switch Port Mapper Tree View 显示交换机 Sys Name、导出可排除 trunk 端口 | 2023-11 | B | 交换机端口映射可用性增强 |
| 2.4 | OpManager：Alarm correlation rule（告警关联规则） | 2024-07 | B | 按预定义关联条件在监控项之间关联指标，降噪并优先处理 |
| 2.5 | OpUtils：计划报表加入位置信息（Subnet / IP Usage Summary） | 2024-07 | B | 计划报表中含位置字段 |
| 2.6 | OpManager 12.8 首发 | 2024-09（约） | C | 仅第三方条目，**需 A 级复核** |
| 2.7 | NetFlow Analyzer 12.8.509：SNMP 接口名自定义（ifName/ifDesc/ifAlias/ifIndex 组合） | 2025-01-10 | A | 用 SNMP 属性自由组合命名接口 |
| 2.8 | NetFlow Analyzer 12.8.511：Enterprise Edition 取消 100 collector 上限 | 2025-01-30 | A | 分布式采集扩展性提升（支持无限 collector） |
| 2.9 | NetFlow Analyzer 12.8.552：高级报表、搜索报表 IP 映射过滤（AD/DHCP/手动/云服务）、DPI 支持合并 TLS Hello 解析 | 2025-04-16 | A | DPI 可解析加密流量中的合并 TLS Hello |
| 2.10 | NetFlow Analyzer 12.8.582：Splunk（UDP）与任意 SIEM（UDP）转发、PagerDuty 集成 | 2025-06-30 | A | 通过 UDP 转发审计 / 访问日志到 SIEM；告警自动创建 PagerDuty 事件 |
| 2.11 | NetFlow Analyzer 12.8.611：ML-based Security Analytics（对齐 MITRE ATT&CK）+ DHCP syslog profile | 2025-08-25 | A | 基于流数据的 ML 安全分析；从 DHCP syslog 提取「用户名–IP」映射 |
| 2.12 | NetFlow Analyzer 12.8.628：「Network Packet Sensor」agent 更名「Remote Collector」并扩展能力 | 2025-10-10 | A | 命名与能力统一 |
| 2.13 | OpUtils：MAC 地址过滤的 DHCP 保留 | 2025-10 | B | 持续扫描交换机 / DHCP / 路由器 / 子网，自动标记并记录新 MAC |
| 2.14 | Firewall Analyzer：VPN 标签页（VPN Overview 报表、活动 / 流量 / 在线用户） | 2025-10 | B | 集中呈现 VPN 流量与使用情况 |
| 2.15 | OpManager：Adaptive Thresholds / Root Cause Analysis / Network Path Analysis / Forecast Alerts / Zia Insights 仪表板 / Zia Chatbot / Zia Metric Insights | 2025（约，官方未标日期） | A | 官方 consolidated 列表条目，日期未标注，本文不编造 |
| 2.16 | NetFlow Analyzer 12.8.665：Smart Upgrade / 应急补丁、移动端推送与 Business Hour 排除周末 | 2026-01-09 | A | EE 支持智能升级与应急补丁 |
| 2.17 | OpManager / Nexus / OpUtils Build 12.8.634：Jira SM(Cloud) 转工单、Splunk SIEM 转发、Remote Collector 轻量 agent、Proxmox VE 监控、Aruba Silver Peak SD-WAN 监控、ilert 集成、Lenovo DS 存储监控 | 2026-01-20 | A | 一批集成与监控对象扩展 |
| 2.18 | OpUtils：IPAM/DNS/DHCP 增强（微软 DHCP/DNS 走 agentless WinRM）、Cisco Meraki DHCP 控制器、约 1000 新设备模板、Connected Interface Discovery、Custom CLI Device Templates | 2026-01-20 / 2026-04 系列 | A | 无代理 WinRM 管理微软 DHCP scope/policy 与 DNS 区域 / 记录；支持按 CLI 响应识别设备的模板 |
| 2.19 | OpManager Build 12.8.635（修复版） | 2026-02-06 | A | 修复升级托盘图标未停、EE 数据库恢复 ID 不一致等 |
| 2.20 | OpUtils 12.8.707：Cisco Meraki 交换机终端 MAC 采集 REST API（`/devices/{serialNumber}/clients`） | 2026-04-03 | A | 新增 API 从 Meraki 交换机采集终端 MAC |
| 2.21 | **OpManager v12.8**：KingbaseES（人大金仓）数据库、OpenAI 集成、WCAG 无障碍、约 300 设备模板、Business View 重构、MTTR/MTBF/MTTF/MTTA/Flap Count 可靠性指标、Info 级告警 | 2026-04-21 | A | 信创数据库适配与运维 KPI 体系补齐 |
| 2.22 | OpUtils 12.8.720：IPAM 授权分层（Management 授权解锁 DNS/DHCP 配置写入）、微软 DHCP superscope | 2026-04-22 | A | IPAM 许可 = 监控；Management 许可 = 可写配置 |
| 2.23 | NetFlow Analyzer 12.8.735：安全事件转发 SIEM（Splunk / UDP-Syslog）、接口利用率热力图 | 2026-05-22 | A | — |
| 2.24 | OpUtils 12.9.105：Rogue DHCP Discovery、AWS Route 53 区域 / 记录管理、Microsoft DNS 记录增改删、BIND 区文件导入（A/AAAA/CNAME/PTR/SRV）、PTR 记录创建 | 2026-06-30 | A | 定期自动发现 DHCP 服务器并识别伪造；云 / 本地 DNS 记录统一管理 |
| 2.25 | NetFlow Analyzer 12.9.102：AI Traffic Visibility 报表 + DPI 的 AI Service Mapping、Flow Deduplication、GenAI（OpenAI / Ollama / DeepSeek）、Zia 聊天机器人、Log360 转发 | 2026-06-18 | A | 识别 AI 服务流量；同一 flow 多设备导出时去重；支持本地 LLM 摘要 |
| 2.26 | NetFlow Analyzer 12.9.121：Security Analytics 告警通知（按 Problems/Assets 配置、多模板） | 2026-07-31 | A | ML 安全分析模块可配告警 |
| 2.27 | NetFlow Analyzer 12.9.133：TOPdesk 集成（告警转事件） | 2026-08-12 | A | — |
| 2.28 | OpUtils 12.9.134：**PoE 监控**（交换机端口供电功耗与状态）；Cisco Small Business 系列 VLAN 改用 Q-BRIDGE-MIB | 2026-08-20 | A | VLAN 采集从 CISCO-VTP-MIB / CISCO-MEMBERSHIP-MIB 切到标准 Q-BRIDGE-MIB |
| 2.29 | NetFlow Analyzer 12.9.147：Security Analytics 支持 Microsoft SQL Server | 2026-09-10 | A | 安全分析模块数据库支持扩展 |
| 2.30 | OpUtils 12.9.149：Switch Port Mapper 权限修复（受限子网 IP、受限交换机 PoE） | 2026-10-06 | A | 修复低权用户越权查看 |
| 2.31 | Firewall Analyzer：防火墙规则变更历史报表（Rule Change History） | 2023-11；Task Audit 2024-07 | B | 记录「谁在何时改了什么规则」；记录软件内任务级变更 |

> **采集缺口（诚实声明）**：Firewall Analyzer 官方 release notes 最新条目仍停留在 8.x 系列，2023–2026 的功能更新主要出现在 B 级 ITOM Newsletter，**窗口内无 A 级逐条 release notes**。

## 2.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织），不写架构层问题。痛点编号 P1…Pn 与下节解法 S1…Sn 一一对应。

- **P1｜网络里什么牌子都有，「接一台新设备」仍要人配对模板与凭证**。设备型号、厂商、OS 版本混杂，每加一类设备就要有人确定用 SNMP 还是 CLI、用哪个 MIB、凭证怎么配；更糟的是**排障时才发现某台设备压根没被接上**。（**人 / 时间**）
- **P2｜阈值全靠人设，且会随业务漂移失效**。设紧了误报把人淹掉，设松了漏报；用了一段时间之后，值班人对这个工具的告警就「脱敏」了——**没人再信告警**。（**人 / 时间**）
- **P3｜从「这个 IP 有问题」到「是哪个交换机、哪个端口、插着哪台终端」要人工反查**。要在 IP 表、ARP 表、MAC 表、端口表之间来回对，定位一次少则十几分钟；对规模大的网络，**这个动作每天要重复很多次**。（**时间**）
- **P4｜拓扑与路径靠猜，网络团队与应用团队互相推责**。「慢在哪一跳」没有共享证据，两边看的是各自屏幕上的不同数字，讨论变成扯皮。（**组织 / 时间**）
- **P5｜网络改动没有留痕，审计与复盘拿不出「谁在何时改了什么」**。配置备份、规则变更、任务审计这些记录不产生业务价值，却是事故复盘与合规举证的必需品。（**合规 / 组织**）
- **P6｜许可按接口 / 传感器逐项计费，账单随网络规模失控**。网络越大，接口数越多，账单涨得越快；等到续费时报价翻倍，**更换厂商的直接动因往往就是这张账单**。（**钱**）

## 2.3 它是如何解决的

**架构约束（由痛点倒推）**

| 架构约束 | 由哪条痛点倒推 | 落到了哪些功能 |
| --- | --- | --- |
| 采集必须覆盖异构设备的全部可达通道，且尽量免适配代码 | P1 | SNMP / WMI / CLI / WinRM / Flow / Trap / Syslog / ICMP / Agent 全通道 + 18500+ 设备模板 + Custom CLI 模板 |
| 阈值不能要求客户手工设定与持续调优 | P2 | Adaptive Thresholds、Forecast Alerts、异常检测、Alarm Correlation |
| 「端口 ↔ 终端」的对应关系必须由平台自动算出来 | P3 | Switch Port Mapper（Bridge MIB + ARP）、Connected Interface Discovery、Rogue DHCP Discovery |
| 路径与层级拓扑必须是可共享的客观证据 | P4 | Network Path Analysis、Layer 2 Map、AI 网络拓扑、Business View |
| 变更与配置必须有版本化留痕 | P5 | NCM 配置备份、Firewall Analyzer 规则变更历史 + Task Audit |
| 计费单位必须与客户的真实资产形态对齐，而非与厂商的计量方便对齐 | P6 | 按设备（含该设备全部接口）授权、永久许可 + 20% AMS、OpManager Nexus 打包 |

在上述约束下，逐条对应 P1–P6 的解法是：

- **S1｜全通道采集 + 大规模设备模板**（→ 解 P1）。OpManager 官方明示的采集协议包括：**SNMP 轮询**（默认通道，v1/v2c/v3，SNMPv3 可配 SHA-2）、**WMI**（Windows 服务器 / Hyper-V / Exchange / AD / SQL，前提是 OpManager 装在 Windows 且本地远端均启用 WMI/RPC/DCOM）、**CLI（Telnet / SSH）**（非 SNMP 的 Linux/Unix）、**WinRM 无代理**（OpUtils 管理微软 DHCP/DNS）、**SNMP Trap（300 条 / 秒）**、**Syslog**、**ICMP**（Ping / Trace Route）、**流数据**（NetFlow / sFlow / J-Flow / IPFIX / NetStream / AppFlow，经 NFA add-on）、**DPI**（插件抓包）、**可选轻量 Agent**（近实时告警、降低网络开销）。官方称 **18500+ 设备模板、53K 厂商模板**。**P1 的解法是「模板库够大 + 通道够多」，而不是让客户写适配器。**
- **S2｜自适应阈值 + 预测 + 异常检测 + 告警关联**（→ 解 P2）。**Adaptive Thresholds** 用 ML 预测算法动态调整监控项阈值并**每小时重算**；**Forecast Alerts / 容量规划**预测资源耗尽时点并提前告警；**Alarm Correlation**（2024-07 起）按预定义条件在监控项之间关联指标；**Anomaly 仪表盘与 Anomaly Summary**（2026-01-20）做异常聚合。官方客户案例（南京泉峰）称自适应阈值「从历史数据自动算限值省了很多时间，告警准确率明显提升」。**边界**：**同一条客户案例里，客户明确表示希望「接口利用率也能支持自适应」——说明该能力仍有场景覆盖不到，需要人工兜底**。
- **S3｜Switch Port Mapper：标准 MIB + ARP 表把端口反解到终端**（→ 解 P3）。机制拆开看：向交换机发 **SNMP** 查询，从 **Bridge MIB（`dot1dTpFdbTable`）** 取 MAC 表、从 **Interface MIB** 取端口索引 / 名称 / 运行状态；再用**路由器 / 三层设备的 ARP 表**把 MAC 反解成 IP（ARP 表可经 SNMP 或 CLI 采集）；**LLDP / CDP** 提供邻居与端口角色提升准确率；**SNMP Sweep** 先扫子网逼交换机学习到设备 MAC，缓解 MAC 表老化导致的漏解；2026-08 起 Cisco Small Business 系列 VLAN 采集改用标准 **Q-BRIDGE-MIB**，2026-04 起 Meraki 走 **REST API** 取客户端 MAC。**读得到什么**：端口索引 / 名称 / 管理状态与运行状态、端口上学习到的 MAC、**PoE 供电功耗与状态（2026-08 起）**、VLAN、交换机 Sys Name、ARP 中的 MAC–IP 映射、rogue 设备发现。**读不到什么（官方文档明确记载的三类限制）**：① 交换机未配置从 `dot1dTpFdbTable` 返回值（如 Extreme Summit 需 `Enable snmp dot1dTpFdbTable`）时，**不显示任何 MAC**；② 未指定路由器或路由器与设备不在同一子网时，**只能拿到 MAC 拿不到 IP**；③ 端口在 Bridge MIB 中无匹配条目（MAC 老化）时，**即使端口 UP 也不显示 MAC**；④ Cisco 交换机用 SNMPv3 且未启用 `context vlan-match prefix` 时，**常规 SNMP 查询取不到端口与 MAC**，需在交换机侧配置并在 OpManager `CiscoSwitches.properties` 登记。
- **S4｜路径分析与分层拓扑**（→ 解 P4）。**Network Path Analysis** 可视化并持续监测源到目的的路径性能、路由形态与历史；**Layer 2 Map** 呈现二层拓扑并支持「从拓扑图批量添加设备」；官方另宣称 AI 网络拓扑能力（`.cn` 站点，**营销文中「92% 准确率 / 故障率降 47%」无第三方复核，不可作为论据**）。**这是把「扯皮」换成「一起看一张图」的解法**。
- **S5｜配置与变更留痕**（→ 解 P5）。**NCM（Network Configuration Manager）** 承担配置备份（支持 tgz 备份、CLI 设备凭证报表）与合规策略复制 / 导入 / 下载、配置偏差用 configlet 修复；**Firewall Analyzer** 提供**防火墙规则变更历史报表**（2023-11）与**任务级审计 Task Audit**（2024-07）；Firewall Analyzer 侧策略 / 配置抓取走 **TFTP / SCP**。2026-04-21 版更进一步补齐 **MTTR / MTBF / MTTF / MTTA / Flap Count** 可靠性指标。**边界**：客户侧反馈明确点出「**OpManager 缺少配置的自动备份**」是审计与恢复准备的障碍——说明 NCM 能力与客户「备份要自动」的期待之间仍有落差。
- **S6｜按设备授权 + 永久许可 + Nexus 打包**（→ 解 P6）。官方定价页明文：**Standard 10 设备 = $95、25 = $245、50 = $445、100 = $795、250 = $1,845、500 = $2,895、1000 = $4,095**；Professional 对应为 $145 / $345 / $645 / $1,145 / $2,645 / $3,845 / $5,995；Enterprise 起 **$11,545 / 250 设备**，Standard 与 Professional 单机上限 1,000 设备，Enterprise **开箱 10,000 设备 / 50,000 接口**并采用 probe-central 分布式架构。关键规则是：**一个设备许可包含该设备的全部接口，接口与传感器不额外计费（无 sensor creep）**。官方还以 **OpManager Nexus（订阅制，50 设备 $1,233 / 500 设备 $7,667 / 1000 设备 $12,000）** 打包网络 + 流 + AP + IP 与端口 + 服务器 + 应用 + 存储，并称同等需求下「OpManager + 各 add-on」合计 $13,748 而 Nexus 为 $7,667，**省约 44%**；官网同时宣称「自 2018 年以来未涨价」、OpManager 比 SolarWinds NPM 便宜 50%、Nexus 便宜 80%（**均为厂商自述口径**）。**P6 的解法核心是「计费锚点客户能理解、涨幅客户能预期」。**

> **边界**：① 无代理模式需开放协议并持有凭证，安全团队可能有异议；② DPI / RUM / NCM / Flow 均为 **add-on，按接口 / PV / 日志量 / 设备数单独计费**——「按设备授权」的低价叙事只在基础监控范围内成立；③ 客户侧反馈指出**模块化许可在 add-on 多的时候总成本会上升、许可结构复杂**；④ **AI 准确率自评仅 60%–70%**（PeerSpot 用户）。

> **配套演进（不进 S 列表）**：ManageEngine 官方在 PitStop 社区公开发文攻击竞品「续费涨价 3 倍、取消永久许可、强制订阅」（部分客户续费报价**涨至 300%**），并以「透明定价 + 永久许可」作为迁移钩子——这是**营销战法**，属竞品博弈而非客户痛点；Vulnerability Manager Plus 弃用旧版补丁库同步、Zulu OpenJRE 版本升级、PostgreSQL 17 迁移等属**技术沿革**。

> **⚠️ 关于「设备侧」的一条关键边界结论**（对自研对标极重要）：在上述全部官方文档中，**第三方采集一律止步于标准 MIB 线**。ARP / MAC-FDB / VLAN / 接口状态**本身在标准 MIB 里、能读**，但读它们的目的是**推断拓扑与终端位置**，而不是回答「这张表对不对」。**读得到「表的内容」，读不到「表的行为」**——ACL 命中计数、policymap 命中率、TCAM 容量与溢出、FIB 内部表项、ASIC 转发行为，**在 OpManager / OpUtils 官方文档中均无任何采集描述**（本文标注为「未证实」，不写入功能清单）。而且「能不能看到」取决于**profile / 扩展写没写**：反例是 OSPF 邻居状态比 BGP 更容易采到，Cisco 交换机的 SNMPv3 甚至需要设备侧额外配置才能返回端口 MAC。**这解释了为什么原厂（L1 层）永远是「设备内部真相」的独占者**——第三方能做的，是把 MIB 线上的信息做到极致。

---

# 大功能点 3：应用性能与数字体验监测 —— 追得透

## 3.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 3.1 | Applications Manager 17 主版本发布 | 2024-02-27 | A | 官方 EOL 页登记的版本发布日期 |
| 3.2 | Applications Manager RBM：Firefox 111→128、Geckodriver 0.32.2→0.34.0、Selenium 4.5.3→4.22.0 | 2024-09-16（AM v172700 / EUM Agent v22.0） | A | 真实浏览器监控内核与驱动升级 |
| 3.3 | Applications Manager RBM：支持 Two-factor（TOTP） | 2024-10-21（AM v173200） | A | RBM 可过双因素登录 |
| 3.4 | Applications Manager 17.7：TongWeb 监控、AWS Direct Connect-VI、Route 53 Resolver、VPC Lattice、Elastic IP、Step Function、Network Firewall、Custom Integration、Heartbeat、WebSocket 监控 | 17.7 版本（官方分组，未标具体日） | A | 覆盖国产中间件、云网络与自定义集成 |
| 3.5 | Applications Manager 17.8：Amazon Redshift、Amazon SES 监控 | 17.8 版本（官方分组） | A | 数仓与邮件服务监控 |
| 3.6 | Site24x7 Server：Disk Read Latency 监控 | 2025-01-29 | A | 磁盘读延迟指标 |
| 3.7 | Site24x7 GCP：Managed Instance Group 监控 | 2025-01-30 | A | MIG 健康 / 性能 / 伸缩可见性 |
| 3.8 | Site24x7 Azure：Load Balancer 增强 + Zia Forecast | 2025-01-31 | A | 后端健康与容量预测 |
| 3.9 | Site24x7：On-Premise Poller 健康仪表盘 / 清单报表 | 2025-02-01 | A | 本地探针资源与性能可视化 |
| 3.10 | Site24x7 APM Insight：Java Agent 用 Ansible role 批量安装 | 2025-02-04 | A | 支持 Tomcat / JBoss / WebLogic / WildFly 批量部署 |
| 3.11 | Site24x7 Network：VMware SD-WAN 监控 | 2025-02-05 | A | 边缘设备与网关性能指标与告警 |
| 3.12 | Site24x7 Kubernetes：容量规划 | 2025-02-05 | A | K8s 资源容量利用率跟踪 |
| 3.13 | Site24x7 Database：MSSQL Expensive Queries 分析 | 2025-02-07 | A | 定位高资源消耗 SQL |
| 3.14 | Site24x7 MSP：客户账号 MFA | 2025-02-13 | A | MSP 可对客户账号强制 MFA |
| 3.15 | Site24x7 Kubernetes：PVC 容量监控 | 2025-02-15 | A | PVC 使用率 / 上限 / 趋势告警 |
| 3.16 | Site24x7 StatusIQ：移动 App（iOS / Android） | 2025-02-18 | A | 移动端管理状态页、发布事件 |
| 3.17 | Site24x7 AWS：Delegated Admin 集成 / Organizations 支持 | 2025-02-19 / 2025-03-10 | A | 多账号与全组织集中监控 |
| 3.18 | Site24x7：从 Layer 2 Map 批量添加设备；Digital Risk Analyzer 处置建议 | 2025-02-21 / 2025-02-25 | A | 二层拓扑内直接加监控；给出风险修复建议 |
| 3.19 | Site24x7 AWS：Amazon Cognito 用户池监控 | 2025-03-05 | A | 认证 / 身份指标与异常告警 |
| 3.20 | Site24x7：移动 App UI 重构 | 2025-03-06 | A | 多账号切换、实时组件 |
| 3.21 | Site24x7 Platform：容量规划集中管理、Advanced Threshold Configuration（AND/OR 多条件）、容量规划支持插件监控 | 2025-03-12 / 03-13 / 03-17 | A | 用 `&&` / `||` 组合多属性条件；插件类监控纳入容量规划 |
| 3.22 | Site24x7 Server：Top Processes Report | 2025-03-13 | A | 按进程 CPU / 内存可视化 |
| 3.23 | Site24x7 Network：Unsolicited Traps 视图重构；Azure Service Quota 监控 | 2025-03-14 | A | 管理未关联监控项的 SNMP trap；配额使用率告警 |
| 3.24 | Site24x7 Kubernetes：Namespace 监控 | 2025-03-16 | A | 识别 terminating 卡死命名空间 |
| 3.25 | Site24x7 Database：MariaDB 监控；Amazon S3 新指标 | 2025-03-24 / 03-25 | A | 慢查询与实例健康；S3 查询效率与跨区复制失败 |
| 3.26 | Site24x7 CloudSpend：Azure 最佳实践检查 | 2025-03-26 | A | Azure VM / LB / VMSS 成本优化检查 |
| 3.27 | Site24x7 APM Insight：IIS 应用自动发现与批量添加（Discover Applications） | 2025-03-20 | A | 自动发现 IIS 应用并批量启监控 |
| 3.28 | Applications Manager RBM：可在 AM UI 内直接录制与添加 RBM 脚本 | 2025-03-03（AM v174900） | A | 脚本录制体验 |
| 3.29 | **Site24x7 RUM Session Replay（会话回放）** | 2025-04-01 | A | 可视化回放真实用户会话（点击 / 滚动 / 表单 / 错误） |
| 3.30 | **Site24x7 RUM Events**（rage click / quick back / excessive scrolling / custom event） | 2025-04-04 | A | 捕获用户行为摩擦信号，含 Events Query 高级过滤 |
| 3.31 | Site24x7 Kubernetes：Change Tracker；APM Insight PHP Agent 支持 Azure Web Apps；AWS VPC Flow Log 支持 Athena | 2025-04-01 / 04-03 | A | YAML 变更追踪与版本对比；PHP 代码级可见性；降低 flow log 查询成本 |
| 3.32 | Site24x7：ilert 集成、Google Cloud Pub/Sub 集成、Pacemaker 集群插件、Azure Key Vault 组件自动发现 | 2025-04-07 ~ 04-24 | A | 告警集中与值班编排、告警外推、集群监控、自动发现 |
| 3.33 | Applications Manager RBM：编辑页重构（带自动建议的高级网页脚本） | 2025-10-22（AM v178200） | A | 脚本编辑体验增强 |
| 3.34 | Applications Manager：FSO Agent v21.0.3 | 2025-11-04 | A | 全栈可观测 Agent 版本 |
| 3.35 | Applications Manager Build 179300：Podman 监控、SIEM/Splunk 集成、Amazon MSK、Azure Data Factory、MySQL InnoDB ClusterSet、Nutanix 多集群 | 2026-01-09 | A | 容器 / 云数据服务 / 数据库集群监控扩展 |
| 3.36 | Applications Manager 18 主版本发布；Build 182400：**AI Summary for Alarms**、Docker Swarm 监控、AppLogs 日志监控 | 2026-03-06（AM 18）/ 2026-09-21（182400） | A | GenAI 为合并 / 分组 / 单条告警生成结构化摘要；集中采集分析应用与服务器日志 |
| 3.37 | Site24x7：Full-Stack agent 单一 Agent 覆盖、SLO（错误预算与 burn rate）、Geo Map、Application Cluster 监控、Synthetic Mobile（Android）、45+ SaaS 应用合成监控、NCM 合规与配置备份、K8s 控制面监控、备份监控、MSP 治理能力 | 2025（约，年度回顾） | B | 官方年度回顾汇总，未标具体日期 |
| 3.38 | Site24x7 免费版永久免费（50 网站监控 / 5 分钟间隔 / 邮件告警） | 现行（未标起始日） | A | 另一官方页口径为「最多 50 个资源」或「5 个」，见附四冲突 #5 |

> **口径说明**：3.1–3.36 为可到日的 A 级条目；3.37 组为官方年度回顾（B 级）汇总条目，**未标具体日期**，本文不拆分编造日期。

## 3.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织）。痛点编号 P1…Pn 与下节解法 S1…Sn 一一对应。

- **P1｜应用出问题，定位要「跨层拼证据」**。一个响应慢的问题，可能出在应用代码、中间件、数据库、云服务或主机上，而这些证据分散在不同的工具与不同的团队手里；**排障时间大量消耗在「把信息凑齐」而不是「做出判断」**。（**时间 / 组织**）
- **P2｜要拿到代码级证据就得改应用代码，团队排期排不上**。插桩改造要动应用、要过发版流程、要测试回归；现实路径是「**先上线、后监控**」，等事故发生时手上根本没有追踪数据。（**人 / 时间**）
- **P3｜用户体验变差，往往是最后才知道的**。页面卡、表单提交失败、慢启动这类问题，通常要等客户投诉或员工提工单才被发现，**期间已经有人流失或效率受损**；而且说不清「有多差、从什么时候开始差」。（**时间 / 钱**）
- **P4｜无代理采集需开放协议与凭证，安全团队不放行**。要监控内网服务器，无代理模式得开 SSH / WMI / SNMP，还要拿到管理员凭证；在受监管环境里，**这一条常常直接卡死监控方案**。（**合规 / 组织**）
- **P5｜监控改造的窗口与业务上线的窗口对不上**。新服务上线有窗口，监控改造没有排期，结果是**监控覆盖落后于业务上线**；资产一变，监控配置还得人工跟着改。（**时间 / 人**）

## 3.3 它是如何解决的

**架构约束（由痛点倒推）**

| 架构约束 | 由哪条痛点倒推 | 落到了哪些功能 |
| --- | --- | --- |
| 采集必须同时支持「有代理」与「无代理」两条路，由客户按合规条件选 | P2、P4 | FSO Agent（出站 HTTPS）、agentless（SSH/WMI/SNMP/REST/JMX/DB）、Site24x7 Full-Stack agent + On-Premise Poller |
| 代码级可见性不能依赖客户改代码与重发版 | P2 | APM Insight bytecode instrumentation、AutoProfiler 自动发现、OTel 接入 |
| 体验质量必须有客观量化基线，且要能定位到具体用户会话 | P3 | RUM + Session Replay + RUM Events、Synthetic + RBM、Geo Map |
| 一个采集件要能覆盖尽可能多的监控对象 | P5 | 单一 Full-Stack agent 覆盖服务器 / VM / 云 / 应用 / 日志 / 数据库 |
| 监控对象的增加不能靠人工逐项配置 | P5 | IIS 应用自动发现、Layer 2 Map 批量添加、Azure Key Vault 组件自动发现、约 300 新设备模板 |

在上述约束下，逐条对应 P1–P5 的解法是：

- **S1｜无代理 + 有代理双模式**（→ 解 P2、P4）。**无代理（agentless）**：AM 用 SSH、WMI、SNMP、REST API、JMX、数据库连接直接轮询目标——免装软件、部署快，但需管理员凭证与远端协议开放，且**AM 宕机期间无数据**。**有代理（agent-based）**：目标机装 **FSO（Full Stack Observability）Agent**（Windows / Linux），本地采集 CPU / 内存 / 磁盘 / 文件系统与应用日志，数据经**出站 HTTPS** 回传——**无需暴露端口、无需共享凭证、AM 暂不可用时 agent 本地缓存续采**。Site24x7 侧的对应形态是 **On-Premise Poller**（无代理，需 SNMP/WMI 凭证，每台 Poller 最多 500 台服务器，WMI 要求 Poller 装在 Windows）与 **Full-Stack agent**（有代理，单向 HTTPS 回传）。**P4 的解法是「给出一个不碰凭证的选项」，而不是说服客户接受凭证外发。**
- **S2｜bytecode instrumentation + AutoProfiler + OTel**（→ 解 P2）。**APM Insight** 在**每个应用服务器**装 agent，**每分钟**经**单向 HTTPS** 把数据推给 AM 的 Data Collector；agent 采用 **bytecode instrumentation** 采集，不改业务代码；支持 **Java（≥8）/ .NET（≥4.0，IIS≥7）/ Ruby / PHP（≥7.0）/ Node.js（≥16.20.2）/ Python（≥3.7）**；**AutoProfiler** 随 Full-Stack Agent 安装时**自动发现** Java / .NET 应用并开始监控；同时支持 **OpenTelemetry** 接入与 **Java Agent 用 Ansible role 批量安装**（Tomcat / JBoss / WebLogic / WildFly）。**「上线即带证据」由此成立。**
- **S3｜RUM + Session Replay + RUM Events + Synthetic 组合**（→ 解 P3）。Site24x7 在 **2025-04-01 上线 RUM Session Replay**（可视化回放真实用户会话，含点击 / 滚动 / 表单 / 错误），**2025-04-04 上线 RUM Events**（rage click / quick back / excessive scrolling / custom event，配 Events Query 高级过滤）；**Synthetic** 侧提供 **RBM（真实浏览器，Firefox + Selenium + Geckodriver，可截图与留 HTML，支持 TOTP 双因素）**、**Synthetic Mobile（Android）**、**45+ SaaS 应用合成监控**（Zoom / GitHub / Jira / ServiceNow / Dynamics / Power BI 等）、**Geo Map** 把合成数据与 RUM 统一到一张地理视图。配套 **SLO（错误预算与 burn rate）**。**P3 从「等投诉」变成「有基线、能回放到具体会话」。**
- **S4｜全栈对象覆盖**（→ 解 P1）。监控对象从应用扩到中间件（**TongWeb** 等国产中间件）、数据库（**MSSQL / MariaDB / MySQL InnoDB ClusterSet**）、容器与编排（**Podman / Docker Swarm / K8s** 含 PVC、Namespace、Change Tracker、控制面组件）、云 PaaS（**AWS 50+ 服务、Azure、GCP**，含 Route 53 Resolver、VPC Lattice、Amazon MSK、Azure Data Factory、Nutanix 多集群）、存储与备份（**Commvault / Veeam / Lenovo DS**）。**P1 的解法是「把证据集中到同一平台」，让下钻不需要换工具。**
- **S5｜单一 Agent + 自动发现 + 批量纳管**（→ 解 P5）。**Full-Stack agent** 用一个 agent 覆盖物理 / 虚拟 / 云主机、文件 / 目录 / 事件日志 / 端口、补丁与备份、IIS / AD / M365，以及 Java / .NET / Ruby / Python 应用日志；**IIS 应用自动发现批量添加**（2025-03-20）、**Layer 2 Map 批量添加设备**（2025-02-21）、**Azure Key Vault 组件自动发现**（2025-04-24）把「人工逐项配置」替换为「自动发现 + 批量纳管」。**边界**：无代理模式下**不能取应用日志**，AppLogs agent 才可访问应用日志——这是「合规便利」与「证据完整」之间的取舍点，客户需自行权衡。

> **边界**：① **Applications Manager 无 SaaS 版**（SaaS 形态对应 Site24x7），选型时须先确认部署偏好；② 免费版与试用额度在各官方页口径不一（见附四）；③ Site24x7 数据保留期按档位分部（Lite 6 个月 / Professional 1 年 / Enterprise 3 年，截至 2026-09）——**保留期即证据存续期**，是合规客户的隐性约束；④ RBM 依赖浏览器内核与 Selenium / Geckodriver 版本矩阵，需跟随升级。

> **配套演进（不进 S 列表）**：Applications Manager 16 → 17 → 18 的版本节奏、AM 16 于 2025-05-30 EOS、RBM 浏览器内核升级（Firefox 111→128）等属**技术沿革**；MSP 客户账号 MFA、StatusIQ 移动 App 等属**交付形态扩展**，不在本组痛点范围内。

---

---

# 大功能点 4：IT 服务管理（ServiceDesk Plus）—— 管得住

## 4.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 4.1 | ServiceDesk Plus 本地 14000：Timer Actions、Maintenance 模块、Advanced Filter、UEM 产品集成、Problem 自定义触发器、CMDB Release-CI 关系、Security Meter | 2023（约，官方社区帖未标日期） | A | 引入「定时动作」做时间延迟型自动化；Security Meter 按百分比给出内置安全特性配置评分 |
| 4.2 | ServiceDesk Plus 本地：MFA 支持、Change 模块新增 UAT 与 Release 阶段（构建 14500 起） | 2023-09（约） | A | 本地认证账号可启 MFA；变更流程新增用户验收测试与发布阶段 |
| 4.3 | ServiceDesk Plus 本地 14600：变更附加字段贯穿全部阶段、变更全阶段支持任务与注释（@提及） | 2024（约） | A | 变更字段可映射到变更模板的所有阶段 |
| 4.4 | ServiceDesk Plus MSP：Zia Chat Bot 可嵌入外部网站、ChatGPT 集成（构建 14900 起） | 2024（约） | A | 在客户端网站内嵌 Zia 机器人受理工单 |
| 4.5 | ServiceDesk Plus 本地 14900 / 14970 / 14980 / 15000 系列：问题模块、Release 审批、采购单审批流 | 2025 | A | 移动端 6.4 起支持问题管理、采购申请与采购单审批流 |
| 4.6 | ServiceDesk Plus Cloud 预测式 AI 套件：智能分派 / 派单、变更风险预测、相似事件聚类、解决方案推荐 | 2025 Q1 | A | 以预测式 ML 对工单做分类、路由与指派，并按历史相似事件聚类预判问题 |
| 4.7 | ServiceDesk Plus Cloud GenAI 套件：解决方案文章生成、富文本生成、终端用户回复生成、会话摘要、邮件解析自动批准 | 2025 Q1 | A | 邮件正文解析后由模型判断可否跳过人工审批 |
| 4.8 | ServiceDesk Plus Cloud：Zia 仪表板（AI 采纳趋势 / token 消耗度量） | 2025 Q2 | A | 按 AI 特性维度统计调用量与 token 消耗 |
| 4.9 | ServiceDesk Plus Cloud：ITIL 认证 14 项实践、PinkVERIFY 认证 10 项流程（新增 Knowledge Management / ServiceDesk / AI） | 2025 | A | 认证覆盖面对外可作合规采购依据 |
| 4.10 | **ServiceDesk Plus Cloud「最大 GenAI 版本」**：Ask Zia（LLM 风格多模态）、Ask Zia Workflow Assist、Checklist Generator、Custom Script Generator、Resolution Assist（RAG）、Enhanced Solution Generator | 2025-09-23（功能发布 2025-09-10） | A | Workflow Assist 以自然语言或图片生成可视化工作流；Resolution Assist 用 RAG 在提 / 改单时给方案摘要 |
| 4.11 | ServiceDesk Plus Cloud：WhatsApp 集成、SaaS Manager Plus 集成、CI States（配置项生命周期含 EOL） | 2025-11 | A | 用 WhatsApp Business 模板推送工单通知（需在 Zoho Store 购买 IM credits） |
| 4.12 | ServiceDesk Plus Cloud：请求详情页布局定制、技术人员不可用告警、自助门户行业模板 | 2025-11-04 起 | A | 门户与派单可用性增强 |
| 4.13 | ServiceDesk Plus Cloud：RCA by Zia（Marketplace 免费扩展） | 2025-12 | A | 依据相关事件与会话数据定位最可能根因，输出含促成因素与纠正预防措施的结构化 RCA |
| 4.14 | **ServiceDesk Plus 本地 v15200**：Ask Zia（ChatGPT + MCP Tools）、Request Workflows、User Defined Actions、Child Requests、Approval Level Actions、Operational Hours、Checklist 增强、MS Teams Message Extension、Zoho Canvas 门户定制、Custom Module 重构 | **2025-12** | A | 拖拽节点把工单从提交到关闭的序列动作编排为 Request Workflow；Ask Zia 按工具 / 用户 / 组 / 角色逐项授权 |
| 4.15 | ServiceDesk Plus 本地 v15200 破坏性变更：Web RDP 停止支持 Windows 工作站、Space 模块 API 去 `/spaces` 前缀、Zulu OpenJRE 11→17、MSSQL 兼容级别需 ≥130 | 2025-12 | A | 升级前置约束，直接影响既有集成与远程运维方案 |
| 4.16 | ServiceDesk Plus MSP 云端：时工表（Timesheets）+ 计费（Billings） | 2025 | A | 按技术人员工时向客户账户出账 |
| 4.17 | ServiceDesk Plus MSP 本地：集成 ChatGPT 与 EventLog Analyzer | 2025 | A | 工单系统与日志审计数据打通 |
| 4.18 | ServiceDesk Plus MSP 15110 / 15120：Account 模块重构、账户删除与归档支持 2FA、Dynamic throttle URL 速率限制、从 Microsoft Entra ID 同步用户 | 2026-01-22 / 2026-02-16 | A | 多租户账号治理与企业身份源对接 |
| 4.19 | ServiceDesk Plus Cloud：Workflow Assist 全版本可用、Zia 支持附件（直接从附图生成工作流） | 2026-05-29 | A | 工作流可由图片输入生成 |
| 4.20 | **ServiceDesk Plus Cloud：SLA 违约预测（by Zia）、AI Insights（情感 + SLA 预测）、SharePoint 接入 Ask Zia、自定义 Guardrails** | 2026-09-10 | A | 依主题 / 描述 / 平均耗时预测 SLA 违约概率与置信度；SharePoint 支持 PDF/DOCX/DOC/MD/TXT/HTML，单文件 ≤5MB |
| 4.21 | ServiceDesk Plus Cloud：Custom Module Workflow、Focus Mode、自定义模块动作节点（Field Update / Action Sequence / Zoho Circuit / Zoho Flow） | 2026-09-16 | A | 每个自定义模块最多 10 条工作流 |
| 4.22 | ServiceDesk Plus Cloud：全新体验（beta）——常驻 Ask Zia、Custom Pages（vibecode）、Headless ITSM（Zoho MCP） | 2026-10（Webinar 2026-10-15） | A | 经 Zoho MCP 把 SDP Cloud 接入兼容 MCP 的 AI 客户端，可在外部 AI 工具内读上下文并执行受支持动作 |

> **注**：SupportCenter Plus、AssetExplorer 在窗口内的功能级事实以补丁与 CMDB 重构为主（AssetExplorer 本地版 CMDB 重构：CI 类型上限提升至 300、每类型附加 CI 属性上限 50、层级上限 5；云版新增资产盘点、合同到期通知、OAuth SSO），本文并入本组叙述，不单列条目。

## 4.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织）。痛点编号 P1…Pn 与下节解法 S1…Sn 一一对应。

- **P1｜分类与派单靠人工，人手被低价值劳动占满**。每张工单都要人判断「这是哪个类别、该给谁」，L2 员工常被迫做 L1 的活；工单量一涨，**服务台的响应时间就直接恶化**。（**人 / 时间**）
- **P2｜SLA 违约往往在事后才知道**。等到 SLA 报红时，惩罚已经发生、客户已经投诉；而「这张单大概率会超时」这个判断，本来在开单时就能做出来。（**钱 / 时间**）
- **P3｜多部门、多法人实体各建一套服务台，员工入口分散**。集团里每个实体一套实例，员工要在多个门户之间找入口、在聊天工具里切来切去；**跨团队协作没有共享工单视图，责任划分靠开会**。（**组织**）
- **P4｜ITIL 流程落地靠文档和人工，审计时要自证「流程真的被遵守了」**。变更、发布、问题管理这些流程，口头说有、系统里散落各处；**审计时拿不出闭环证据**。（**合规**）
- **P5｜本地部署的客户被落在后面**。新功能先上云、本地版后跟，本地客户的团队与云端团队长期不同步；升级本地版还常常伴随破坏性变更（远程功能失效、JRE 与数据库兼容级别抬升）。（**钱 / 组织**）
- **P6｜最终账单不可预期**。永久许可之外每年还要付约 20% 的年度维护与支持（AMS），服务器与终端分开计价，若干安全与高级能力单独报价——**采购时算得清，用起来算不清**。（**钱**）

## 4.3 它是如何解决的

**架构约束（由痛点倒推）**

| 架构约束 | 由哪条痛点倒推 | 落到了哪些功能 |
| --- | --- | --- |
| 工单的「类别 / 优先级 / 归属」必须由平台预测并预填 | P1 | Zia 预测式分诊、智能组 / 技术员预测、相似事件聚类 |
| 「会不会违约」必须在开单时就能算出概率 | P2 | SLA 违约预测（by Zia）、技术人员不可用告警、Operational Hours |
| 多实体 / 多部门必须在同一套系统内共用一套流程 | P3 | ESM 门户、自定义模块、多实例、Custom Module Workflow、行业门户模板 |
| 流程必须可被第三方认证背书，而不是自我声明 | P4 | ITIL 14 项实践认证、PinkVERIFY 10 项流程认证、Internal ITIL 资产认证 |
| 本地与云必须共享同一能力集，升级代价要可控 | P5 | 本地 v15200 引入 Ask Zia / Request Workflows；破坏性变更前置公告 |
| AI 能力不能成为额外采购门槛 | P6 | 预测 / 生成 / 对话式 AI 全版本不加价；Zia Agents 归 Enterprise |

在上述约束下，逐条对应 P1–P6 的解法是：

- **S1｜预测式 ML 做分类、路由与审批判断**（→ 解 P1）。**Zia Prediction Engine**（Zoho 自研 ML，非 LLM）承担四类判断：**工单预测式分诊**（2024-07 起，建单 / 改单时预测类别、子类、模板、技术员、优先级）、**智能组 / 技术员预测**（2024-12 起，把工单路由到前三名技术员组）、**变更风险预测**、**相似事件聚类**（预测潜在问题）。审批侧做得更彻底：**Zia 解析请示邮件正文后自动套用 Approve/Reject**（2024-01 起），把「等人点一下」从流程里去掉。**P1 的解法不是「让 AI 干活」，而是「让 AI 先填好，人只做例外处理」。**
- **S2｜SLA 违约预测与运营时段建模**（→ 解 P2）。**2026-09-10 上线 SLA 违约预测（by Zia）**：依据工单主题、描述、站点、SLA 与**历史相似工单的平均耗时**，预测新工单或字段变更后的**违约概率与置信度**，可按阈值通知；同时请求详情页给出 **AI Insights**（情感分析 + SLA 违约预测）。配套 **Operational Hours / Special Operational Hours**（本地 v15200）把「什么时段算履约」显式建模。**边界**：该能力**当前仅 US / EU / IN 数据中心**，2026-09 前 Resolution assist 也仅 US / EU——区域可用性不一致。
- **S3｜ESM 与自定义模块把多实体收回一套系统**（→ 解 P3）。本地 v15200 引入 **Child Requests**、**Approval Level Actions**、**Request Workflows**（拖拽节点编排从提交到关闭的序列动作），云版引入 **Custom Module Workflow**（每个自定义模块最多 10 条工作流）、**Focus Mode**、**自定义模块动作节点**（Field Update / Action Sequence / Zoho Circuit / Zoho Flow）与**自助门户行业模板**；AssetExplorer 侧 **CMDB 重构**（CI 类型上限 300、每类型附加属性 50、层级 5）与 **CI States（Active/EOL 生命周期，EOL 的 CI 在所有模块中隐藏且不可新建关系）**。**P3 的解法是「一套实例 + 可定制的部门视图」，而不是让每个部门各买一套。**
- **S4｜第三方流程认证**（→ 解 P4）。官方披露 **ITIL 认证 14 项实践**、**PinkVERIFY 认证 10 项流程**（含新增的 Knowledge Management、ServiceDesk 与 AI），并在 2025-09 的 Gartner MQ for AI Applications in ITSM 中列为 **Niche Player**（评估 10 家厂商）、2025 Q4 Forrester Wave ESM 为 **Strong Performer**、2026-08 中文站自述入选 Gartner ITSM 魔力象限 **Challenger**（**仅见中文站，待原文核实**）。**对客户的意义是「审计时可以引用第三方报告」，而不是自己画流程图自证。**
- **S5｜本地版补齐 GenAI 能力，压缩云-本地代差**（→ 解 P5）。**本地 v15200（2025-12）**把 Ask Zia（**ChatGPT LLM + MCP Tools**）、Request Workflows、User Defined Actions 落进本地部署，管理员可按**工具 / 用户 / 组 / 角色逐项开关**；代价是**破坏性变更**：Web RDP 停止支持 Windows 工作站（仅保留 UEM 代理远程）、Space 模块 API 去掉 `/spaces` 前缀、Zulu OpenJRE 11.0.24→17.0.17、MSSQL 兼容级别需 ≥130。**这是「本地客户不被落下」与「升级必须动基础设施」之间的取舍**，客户侧反馈中点名的「BitLocker 磁盘加密策略、远程控制连接在版本间失效」正是这类代价。
- **S6｜AI 全版本免费 + 自主 Agent 归 Enterprise**（→ 解 P6）。官方定价页原文明确：**「预测式、生成式与对话式 AI 能力在所有版本可用且不额外收费；Zia Agents 包含在 Enterprise 版中」**。计费维度是**按技术人员数**，Standard 版只按技术员、Professional / Enterprise 叠加 IT 资产数，**终端用户不限量也不收费**。**边界**：ServiceDesk Plus 本地版两个官方 pricing 页价格互不相同（2 技术员 + 250 资产专业版一处 $645/年、另一处 $495/年），**采购前必须以报价单为准**。

> **边界**：① **Zia Agents 仅 ServiceDesk Plus Cloud Enterprise 版**；② 生成式与多语言能力依赖所选模型与数据中心，区域差异明显；③ 第三方评价明确指出**接口（API）能力与字段数量上限**仍限制自动化落地——有用户因字段上限不得不保留旧系统并自建连接器；④ 客户社区反映 AI 生成的结单说明存在「看起来修好了但步骤并未真正执行」的情况，**AI 结论仍需人工核验**。

> **配套演进（不进 S 列表）**：CVE-2025-8309（SupportCenter Plus 权限提升）与 AssetExplorer 同源漏洞修复属**安全维护**；MSP 账户模块重构、Entra ID 同步、Jasper Reports 漏洞修复属**工程治理**；Zoho Store 采购 WhatsApp IM credits 属**生态配套**。

---

# 大功能点 5：SIEM 与安全运营（Log360 / EventLog Analyzer）—— 查得清

## 5.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 5.1 | **Log360 UEBA 实时异常检测** | 2024-02-08 | A | 为 EventLog Analyzer 报表配置实时异常检测，行为威胁发生时即刻告警 |
| 5.2 | Log360：Incident Workbench（专用威胁调查控制台，含进程搜寻树、VirusTotal 外部威胁源） | 2024-02 | A | 面向用户 / 设备 / 进程 / 外部威胁源的核心数字实体分析台 |
| 5.3 | Log360：暗网监控（集成 Constella Intelligence） | 2024-05 | A | 持续扫描深网 / 暗网中与本组织、员工、第三方相关的泄露凭据与个人信息 |
| 5.4 | Log360：Endpoint Central（EDR）集成、Salesforce 云监控、Global Search、**Sigma 规则导入** | 2024-05 | A | 引入 Sigma 规则格式以复用社区检测内容 |
| 5.5 | Log360：PAM360 集成 | 2024-07 | A | 与特权访问管理打通 |
| 5.6 | Log360：开箱合规报表 PCI DSS 4.0、ISO 27001:2022 | 2024-09 | A | — |
| 5.7 | Log360：开箱合规报表 NIS2（欧盟） | 2024-10 | A | — |
| 5.8 | **Log360 Zia Insights**（自动日志分类 + MITRE ATT&CK 自动映射 + 自然语言告警摘要 + 影响面与处置建议） | 2024-12 | A | 由 LLM 对日志内容做推理（非纯正则）后分类为 error/security/operational |
| 5.9 | **Log360 / EventLog Analyzer 构建 13000 检测架构重构**：集中式检测控制台、统一安全仪表盘、对象级过滤（用户 / 组 / OU）、规则调优洞察、交互式规则构建（Standard/Anomaly/Advanced）、水平扩展（processor cluster + 角色分工）、M365 日志源 | **2025-09-16** | A | 单面板统管 MITRE 映射规则、UEBA、关联与威胁情报；云端下发 2,000+ 预置 MITRE ATT&CK 规则、200+ M365 报表、51 条 M365 检测规则 |
| 5.10 | EventLog Analyzer：关联索引流程优化；修正 John the Ripper / Certutil / PMP 会话关联规则条件以降误报 | 2025-05-21 | A | — |
| 5.11 | EventLog Analyzer：JSON 解析支持（可为预定义与新 / 既有自定义日志格式定义 JSON 字段提取规则） | 2025-06-27 | A | — |
| 5.12 | EventLog Analyzer：事件手动开工单、事件与工单状态 / 严重度自动同步、工单集成开关与高级属性预设 | 2025-07（约） | A | 最低信誉分阈值调整为 40 以降误报 |
| 5.13 | EventLog Analyzer：**Zia Insights**（基于 Azure OpenAI，BYOK） | 2025-09 前（约） | A | 检测后工作流中的上下文 AI 洞察 |
| 5.14 | EventLog Analyzer：预置扩展（Marketplace）、自定义 Widget（HTML/JS/CSS + Zoho Extension Toolkit）、REST API V2、报表注解 / 导出 HTML+XLSX / 定时导出 | 2025-09-04 | A | — |
| 5.15 | Log360：新增合规框架 NIS2、FADP；playbook 按事件类型与历史执行智能推荐 | 2025-09 | A | — |
| 5.16 | Log360：SSO 支持（SAML：Okta / OneLogin / Ping Identity / ADFS / Azure AD；NTLM 集成 Windows 认证） | 2025-11-11 | A | — |
| 5.17 | Log360 / EventLog Analyzer：**不可能旅行（Impossible Travel）检测** | 2025-11-11 | A | 识别短时间内从不同国家的登录 |
| 5.18 | **Log360 原生 SOAR**（内置于统一安全平台核心数据模型、可视化低代码剧本构建器、CDN 下发预置响应模板、7 个 Marketplace 扩展、300+ 响应动作、Python/Deluge 自定义函数、基于 Zoho Qntrl Circuit） | **2026-05-12** | A | 单条剧本可经 EDR 隔离终端、经 IAM 撤销会话、威胁情报富化、开工单并通知 SOC |
| 5.19 | **Log360 Cloud：许可改为按基础设施组件计费**（日志源 / 域控 / 文件服务器 / 云账户 / 端点分别独立购买） | **2026-05-16** | A | 例如 10 日志源专业版 $1,095/年；检索存储 $10/GB/年、归档 $0.25/GB/年 |
| 5.20 | **Log360 Cloud：Ask Zia + Zia Agent Studio + Zoho MCP 集成**（Ask Zia 自然语言查询日志 / 告警 / 技术员审计记录；2 个预置代理：用户活动审查、告警关联） | **2026-05-20** | A | Ask Zia 把自然语言转结构化查询；告警关联代理按时间窗内共享实体（主机 / 用户 / IP）串成带 MITRE 阶段标注的攻击链 |
| 5.21 | Log360 Cloud：日志采集失败告警；上线 UAE 数据中心（数据驻留 / 合规） | 2026-05-08 / 2026-06-16 | A | 覆盖近 190 个国家 |
| 5.22 | Log360：迁移兼容 Unified Log360（构建 5570）；ADManager Plus 与 Exchange 审计插件自 13000 起从 Log360 移除 | 2026-06-30 | A | 独立版 Log360 与 ELA 集成部署可将受支持配置迁移到统一架构 |
| 5.23 | Log360：Marketplace 扩展 Bitdefender GravityZone、CrowdStrike Falcon Event Streams、Okta、MikroTik 集成 | 2026-08-17 | A | — |
| 5.24 | ADAudit Plus 构建 8500 / 8520：Attack Surface Analyzer（GPO 错误配置分析）、Azure Intune 审计、Windows LAPS 审计、代理集中管理与自升级；Security Hardening 页、工单集成新增 Kayako / Freshservice / Jira SM、SAML SSO | 2025-01-31 / 2025-09-10 | A | PostgreSQL 升至 17.5，代理升级无需管理员权限或 RPC 端口 |
| 5.25 | ADAudit Plus：**非人类身份（NHI）审计**（服务主体 / 托管标识登录及其权限与凭据增删改）、Data Access Analyzer、Group removal simulator、Platform Activity Explorer | 2026（未标具体日） | A | 端到端 Entra ID 加入设备审计、云文件传输监控（OneDrive / Google Drive / Dropbox / SharePoint / 任意 HTTPS 目标） |
| 5.26 | DataSecurity Plus：构建 6300–6330 —— Incident Management Console、Device Groups、**Email DLP**（body/附件/预分类文件，Allow/Warn/Block + 策略优先级）、TAA 合规构建、Cloud Protection 审计 GenAI 提示词 | 2026-07 ~ 2026-10 | A | 最严格响应自动优先；2026-09 新增条件级置信度与接近匹配（proximity matching） |

## 5.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织）。痛点编号 P1…Pn 与下节解法 S1…Sn 一一对应。

- **P1｜日志来源杂、格式乱，「接一个新源」要人写解析规则**。一个组织里几十种设备与应用各说各话，每接一类就要有人写正则与提取规则；**排障时才发现某类日志根本没接上或解析错了**。（**人 / 时间**）
- **P2｜告警疲劳：规则误报把人淹掉**。SOC 被大量误报占据，真事件淹没在噪声里；规则越加越多，调优却越来越靠经验，**最后没人认真看告警**。（**时间 / 人**）
- **P3｜同一批日志要按多套合规框架重复出报表**。等保、GDPR、PCI DSS、NIS2、HIPAA 各有各的控制项与格式要求，**安全团队在「做报表」上花的时间超过「做安全」**。（**合规 / 人**）
- **P4｜审计举证要人工筛日志、整截图，周期以周计**。被审计方要证明「谁在何时访问了什么」，只能人工从日志里捞、截图、拼成材料；**一次合规审计的准备周期常常是 2–3 周**。（**合规 / 时间**）
- **P5｜发现了告警，但没有处置动作链**。告警出来之后是「通知人 → 人去查 → 人去做」，隔离终端、撤销会话、封禁账号都要跨系统手工操作，**MTTR 被拉长**。（**时间 / 钱**）
- **P6｜日志量增长直接推高客户自己的账单**。合规要求留存越久、来源越多，检索与归档容量就越贵；**「留不住证据」与「付不起存储」之间被迫取舍**。（**钱**）

## 5.3 它是如何解决的

**架构约束（由痛点倒推）**

| 架构约束 | 由哪条痛点倒推 | 落到了哪些功能 |
| --- | --- | --- |
| 日志接入必须覆盖尽可能多的源类型，且支持客户自定义解析 | P1 | 官方称 750+ 日志源类型、JSON 解析规则、自定义 Widget、Marketplace 扩展 |
| 检测规则必须可复用、可调优、可下推更新 | P2 | 构建 13000 集中式检测控制台、2,000+ 预置 MITRE 规则云端下发、规则调优洞察、Sigma 导入 |
| 合规报表必须开箱即用且覆盖多框架 | P3 | PCI DSS 4.0 / ISO 27001:2022 / NIS2 / FADP / SAMA / CJDN / SOC 2 / QCF / TISAX / LGPD / ISLP 等 |
| 「谁做了什么」必须能被组织成可直接出证的形态 | P4 | Zia Insights 告警摘要、用户活动审查代理（汇成单一摘要）、Incident Workbench、Data Access Analyzer |
| 告警必须能直接触发处置动作 | P5 | 原生 SOAR（300+ 响应动作、低代码剧本）、事件与工单自动同步、EDR / IAM / 工单联动 |
| 计费锚点必须与客户的真实日志结构对齐 | P6 | 按组件（日志源 / 域控 / 文件服务器 / 云账户 / 端点）计费、归档 $0.25/GB·年、50GB 免费额度 |

在上述约束下，逐条对应 P1–P6 的解法是：

- **S1｜大规模日志源覆盖 + 客户自定义解析**（→ 解 P1）。Log360 官方 datasheet 称覆盖 **750+ 日志源类型**（另一处口径为「700+」，见附四）；**EventLog Analyzer 2025-06-27 起支持 JSON 解析**，可为预定义与既有自定义格式定义 JSON 字段提取规则；**Zoho Extension Toolkit** 允许用 HTML/JS/CSS 做自定义 Widget；**Marketplace 扩展**（2026-08-17 新增 Bitdefender、CrowdStrike Falcon Event Streams、Okta、MikroTik）补齐长尾源。**边界**：「750+」这个数字是**源类型数**而非「开箱即用的解析完整度」，长尾自定义源仍需人工配置。
- **S2｜检测架构重构 + 规则治理 + UEBA**（→ 解 P2）。**构建 13000（2025-09-16）是窗口内最重要的一次架构动作**：把 MITRE 映射规则、UEBA、关联与威胁情报收进**单一集中式检测控制台**；提供**对象级过滤**（按用户 / 组 / OU 缩小检测范围）、**规则调优洞察**、**交互式规则构建**（Standard / Anomaly / Advanced 三档）、**水平扩展**（processor cluster + 角色分工）；云端下发 **2,000+ 预置 MITRE ATT&CK 规则**、200+ M365 报表、51 条 M365 检测规则。配套检测能力包括 **UEBA**（无监督学习检测行为偏移，2024-02 起实时异常检测）、**不可能旅行检测**（2025-11-11）、**Sigma 规则导入**（复用社区内容）。**边界**：官方明确「Zia 并非替代安全分析师的专业判断，而是通过快速输出高价值上下文信息赋能人员聚焦决策研判」——**定位是减负而非替代**。
- **S3｜开箱合规报表矩阵**（→ 解 P3）。Log360 / Log360 Cloud 在窗口内持续扩充开箱报表：**PCI DSS 4.0、ISO 27001:2022（2024-09）、NIS2（2024-10）、FADP（2025-09）、SAMA / CJDN / SOC 2 / QCF / TISAX / ECC / PDPL / UAE-NESA / LGPD（2023-12）、ISLP（中国等保）**。**对客户的意义是「同一批日志，切框架出报表」**，而不是每个框架重做一遍。
- **S4｜Zia Insights + 用户活动审查代理 + 调查工作台**（→ 解 P4、P2）。**Zia Insights** 由 LLM 对日志内容做**推理性分类**（error / security / operational）并自动映射 MITRE 战术 / 技术 / 子技术，给出自然语言告警摘要、影响面与处置建议；**Log360 Cloud 的「用户活动审查代理」（2026-05-20）**把指定用户的登录、文件访问、系统触碰、触发告警**汇成单一摘要**（用于离职前审查与合规审计）；**Incident Workbench**（2024-02）提供面向用户 / 设备 / 进程 / 外部威胁源的分析台；**ADAudit Plus 的 Platform Activity Explorer** 把 AD / 文件 / 云统一检索。**这直接对应 P4「审计举证周期以周计」——把「翻日志」变成「读摘要」。**
- **S5｜原生 SOAR：把处置做成可选剧本**（→ 解 P5）。**2026-05-12 上线原生 SOAR**，内置于统一安全平台的核心数据模型：**可视化低代码剧本构建器**（基于 Zoho Qntrl Circuit）、**CDN 下发预置响应模板**、**300+ 响应动作**、**Python / Deluge 自定义函数**、7 个 Marketplace 扩展。官方示例：**单条剧本可完成「经 EDR 隔离终端 → 经 IAM 撤销会话 → 威胁情报富化 → 开工单并通知 SOC」**。配套侧：EventLog Analyzer **事件与工单状态 / 严重度自动同步**（2025-07 起），ADAudit Plus 工单集成扩到 Kayako / Freshservice / Jira SM。**边界**：SOAR 的响应动作依赖已接入的第三方产品（EDR / PAM / IAM），**跨产品联动的完备度取决于客户已购模块**。
- **S6｜按组件的计费模型 + 归档低价位**（→ 解 P6）。**Log360 Cloud 在 2026-05-16 把许可从「按存储 GB」改为「按基础设施组件」**：日志源、域控、文件服务器、云账户、端点**分别独立购买**（例：10 日志源专业版 $1,095 / 年；2 域控 $1,345 / $1,745；100 端点 $995 / 年）；**检索存储 $10–$13/GB·年、归档 $0.25/GB·年**，**每购 1 单位检索存储自动附赠 3 倍归档存储**；提供 **50GB 免费额度**（50GB 检索 + 150GB 归档，无需信用卡）；超过 20TB 需联系销售。**P6 的解法是「把贵的检索和便宜的归档分开计价」，让客户按证据价值分层留存。** **边界**：官网同时在线两套计费模型（旧的「按存储 GB」页与新的组件化页并存），**采购前必须以报价单确认适用哪一套**。

> **边界**：① **CISA 已知被利用漏洞（KEV）目录中有 9 个 ManageEngine / Zoho 漏洞**（CVE-2021-40539 ADSelfService Plus 曾遭国家关联攻击者利用），安全记录是安全导向客户的首要筛选条件，也是这套产品线自我要求「持续打补丁」的原因；② 窗口内 Log360 / EventLog Analyzer / ADAudit Plus / DataSecurity Plus 修复了大量 CVE（含 CVE-2026-2740、CVE-2026-8923 日志转发用户 RCE、CVE-2026-16900 未授权本地采集器注册绕过、CVE-2026-12263 认证绕过等）——**产品的安全维护成本要计入 TCO**；③ 分析师位置：2025 Gartner MQ for SIEM 官方仅称「named in」**未披露象限**（2024 年为 Major Player），IDC MarketScape Worldwide SIEM 2026 为 **Major Player**。

> **配套演进（不进 S 列表）**：SSO（SAML / NTLM）支持、UAE 数据中心上线、存储合规框架扩展、JRE / PostgreSQL / Tomcat 版本升级、Unified Log360 配置迁移等属**工程与合规配套**；Exchange Reporter Plus 在窗口内未采到独立 release notes，**不写入**。

---

# 大功能点 6：统一终端管理与数字员工体验（Endpoint Central）—— 护得稳

## 6.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 6.1 | **NGAV 原生杀毒**（深度学习 + 行为检测，使产品成为 EPP） | 2023-10-17 | A | 用神经网络模型 + 行为检测识别已知 / 未知威胁，支持边缘 AI 实时防护与离线处置 |
| 6.2 | Endpoint Central MSP Cloud 云版发布（原 Desktop Central MSP） | 2023-11-08 | C | UEM + 安全平台面向 MSP 的多租户云端版本 |
| 6.3 | 全功能免费版（永久 25 端点，无功能阉割；OS 部署限 4 工作站 + 1 服务器） | 2023 起长期 | A | 30 天全功能试用无设备上限 |
| 6.4 | 自动补丁（Windows / macOS / Linux + 第三方应用） | 2025（现行） | A | 扫描 → 测试 → 审批 → 按策略自动部署，含合规报表 |
| 6.5 | Patch Manager Plus / Remote Access Plus / OS Deployer / MDM Plus 等产品的免费档 | 2025（现行） | A | Patch Manager Plus 免费版 20 计算机 + 5 服务器（另称 25 设备）；Remote Access Plus 10 台；MDM Plus 25 台；OS Deployer 25 设备 |
| 6.6 | Mobile Device Manager Plus：Apple 声明式管理（DDM）+ 非破坏式跨 MDM 迁移 + Return to Service 增强 | 2025（WWDC 2025 跟进） | B | 支持 iOS / iPadOS / macOS 26 |
| 6.7 | Mobile Device Manager Plus：Android 16 支持、BYOD 注册、Kiosk 刷新 | 2025-05 / 2025-06 | A | Agent 25.05.02 加入 Android 16 兼容；25.06.02 支持 BYOD 注册与 RTL 语言 |
| 6.8 | **Endpoint Central DEX（数字员工体验）**：20+ 体验指标、1,000+ 遥测点 | 2025-08-26 | A | 持续采集 CPU / 内存 / 磁盘 / GPU / 电池 / 登录延迟 / 崩溃，阈值告警 + 根因诊断 + 自动修复 + 体验评分与基线对比 |
| 6.9 | DEX 独立 SaaS 产品 **DEX Manager Plus** | 2025-08-26 | A | 不采用完整 UEM 的组织可单独订阅的云原生 DEX 方案 |
| 6.10 | DEX 可扩展动作库 / 原生工作流构建器 | 2025-08-26 | A | 预置脚本 + 自定义脚本 + 数据采集器，支持「检测 → 修复」端到端自动化 |
| 6.11 | 补丁当天覆盖率与第三方补丁规模（官方称 Patch Tuesday 后 24 小时内多数端点完成安装、750–1,100+ 第三方应用） | 2025 | C | 口径见附四 |
| 6.12 | 信创原生适配（UOS / 麒麟原生 Agent） | 2025 | B / C | 原生覆盖 Windows / macOS / Linux / iOS / Android / ChromeOS / tvOS / iPadOS |
| 6.13 | **Endpoint Central EDR + Secure Private Access**（AI 威胁检测与调查、零信任内部应用访问） | 2026-03-17 | B | 关联进程 / 文件 / 注册表 / 网络遥测并映射 MITRE ATT&CK；AI 行为分析检测无文件威胁 |
| 6.14 | **自主终端管理（AEM）**：自愈漂移纠正 + 预测硬件故障 + Zia Agent 生成自动化 | 2026（约） | A | 持续比对合规基线，检测到配置漂移即自动恢复；遥测模型预测电池 / 硬盘失效 |
| 6.15 | Endpoint Central AI：脚本 / 工作流生成、自主打补丁、JIT 提权评估、DEX 异常检测、KB 自动生成 | 2026（约） | A | AI 风险分 / 可靠性分给补丁自动放行；AI 评估 JIT 提权请求自动批准或提交复核；已解决工单自动沉淀为知识草稿 |
| 6.16 | Forrester TEI 委托研究：统一平台三年 442% ROI、<$6 个月回本、$3.7M 节省 | 2025（厂商委托） | A（厂商委托） | 10,000 人复合组织；节省项含整合工具 $1.1M+、自动化补丁 $913K、自助服务 $922K、资产可见性 $820K+ |
| 6.17 | Browser Security Plus：macOS 15 / 26 支持、50+ 浏览器策略（对齐 CIS / STIG）、Ulaa 浏览器支持、Syslog 日志转发 | 2024 ~ 2026 | A | 多浏览器统一管控（Chrome / Edge / Firefox / IE），CIS/STIG 合规评分四档制 |
| 6.18 | Vulnerability Manager Plus：Splunk add-on 1.0.6、CIS 基准配置管理、250+ 第三方应用补丁、服务包升级路径至 11.5.2600.01 | 2025-11-14 等 | A | 与 Endpoint Central 共用模块；官方公告明确「Endpoint Central 的哪些模块将被弃用」 |

## 6.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织）。痛点编号 P1…Pn 与下节解法 S1…Sn 一一对应。

- **P1｜终端体验问题总是「员工先知道、IT 后知道」**。慢启动、应用崩溃、登录延迟往往要等员工提工单才被发现；而且**员工只能说「我的电脑很慢」，说不清是哪一环**，IT 需要重新复现与定位。（**时间 / 人**）
- **P2｜补丁靠人工推进，覆盖不全，成为被利用的入口**。补丁发布后要人盯着装、跟进失败终端；覆盖不到的那几台，就是下一个被攻破的入口；**漏洞来自「别人的已知问题」，罚则却落在自己头上**。（**合规 / 时间**）
- **P3｜终端工具蔓延，同一批端点买了五份许可**。打补丁、远程访问、资产管理、杀毒、MDM 各买一套，还要各配一套管理流程与报表；**同一台设备的信息在五个控制台里各存一份**。（**钱 / 组织**）
- **P4｜配置漂移没人发现，直到出事**。终端或应用配置被改动（或未按基线部署），没有持续比对机制；**出问题时才知道「它早就不合规了」**，也无法回溯是谁改的。（**合规 / 时间**）
- **P5｜要榨出自动化价值就得会写脚本，能力绑在少数人身上**。批量操作、自定义修复、复杂策略都要脚本；会写脚本的人一休假，这套平台就只剩默认功能。（**人**）

## 6.3 它是如何解决的

**架构约束（由痛点倒推）**

| 架构约束 | 由哪条痛点倒推 | 落到了哪些功能 |
| --- | --- | --- |
| 体验必须被持续量化，而不是等投诉 | P1 | DEX：20+ 指标 / 1,000+ 遥测点 + 体验评分 + 基线对比 + 根因关联 |
| 补丁决策必须由平台按风险自动放行 | P2 | AI 风险分 / 可靠性分自动放行补丁、补丁当天覆盖率、750–1,100+ 第三方补丁 |
| 终端管理必须收敛到一个平台面 | P3 | UEM 单平台整合（补丁 / 远程 / 资产 / OS 部署 / EDR / NAP / 浏览器安全） |
| 配置必须与基线持续比对并可自愈 | P4 | AEM 漂移检测与自动恢复、Security Hardening 页、CIS/STIG 基线对齐 |
| 自动化不能依赖脚本能力 | P5 | Zia 自然语言生成脚本 / 工作流、预置脚本与动作库、自助服务门户 |

在上述约束下，逐条对应 P1–P5 的解法是：

- **S1｜DEX：把「体验」变成可持续测量的对象**（→ 解 P1）。**2025-08-26 发布 DEX**，机制是**持续采集 20+ 体验指标 / 1,000+ 遥测点**（CPU、内存、磁盘、GPU、电池、登录延迟、崩溃等）→ **阈值告警 + 根因诊断**（关联硬件老化等因素）→ **按严重度排序并一键或自动化修复** → **设备与应用体验评分与基线对比**。同时提供**独立 SaaS 形态 DEX Manager Plus**，供不采用完整 UEM 的组织单独订阅。**P1 的解法是「在员工提工单之前就知道」**。
- **S2｜AI 风险分驱动的补丁自动放行**（→ 解 P2）。Endpoint Central 的 **AI 风险分 / 可靠性分**为补丁自动放行并逐环推进；第三方补丁覆盖从 **750** 到 **1,100+** 应用（口径见附四）；官方称 **Patch Tuesday 后 24 小时内多数端点完成安装**（**客户侧转述，未经第三方复核**）。配套的 **NGAV**（2023-10-17）用**深度学习 + 行为检测**识别已知 / 未知威胁，支持**边缘 AI 实时防护与离线处置**——**监控、分析、修复在设备本地完成**，不依赖云端连通性。**边界**：补丁覆盖率的量化数字来自厂商与第三方转述，**未见独立机构复核**。
- **S3｜UEM 单平台整合**（→ 解 P3）。一个平台覆盖**补丁、远程支持（无人值守 + 会话录制 + 语音视频 + HIPAA 加密）、资产管理、OS 部署（硬件无关镜像、在线 / 离线镜像）、MDM（Apple DDM / Android 16 / BYOD / Kiosk）、浏览器安全、漏洞管理、EDR 与零信任访问（Secure Private Access）**；**2026-03-17 补齐 EDR 与 Secure Private Access**，使平台从「管理」扩展到「检测 + 响应 + 访问控制」。**P3 的解法是「把五份许可并成一份」，Forrester TEI 委托研究把它量化为三年 442% ROI / $3.7M 节省（厂商委托口径）**。
- **S4｜AEM 自主终端管理：漂移自愈 + 硬件故障预测**（→ 解 P4）。**AEM** 持续把终端配置与合规基线比对，**检测到漂移即自动恢复**；同时用遥测模型**预测电池 / 硬盘失效**；自然语言可让 Zia 转成多步自动化。配套的 **Security Hardening 页**（ADAudit Plus 2025-09-10）、**CIS / STIG 基线对齐**（Browser Security Plus 提供四档合规评分）、**Attack Surface Analyzer**（ADAudit Plus，GPO 错误配置分析）把「合规」从一次性检查变成持续比对。**边界**：自愈动作本身需要有明确基线定义，**基线不准则自愈会放大错误**——这是 AEM 类能力的固有风险。
- **S5｜自然语言生成脚本与工作流**（→ 解 P5）。Endpoint Central AI 支持**用自然语言生成脚本与工作流**、**JIT 提权请求的 AI 评估**（自动批准或提交复核）、**DEX 异常检测**、**KB 自动生成**（每个已解决工单自动沉淀为知识草稿）。**P5 的解法是「把写脚本这件事从人身上摘下来」**——从「你得会写」变成「你把意图说清楚」。

> **边界**：① **免费版额度在各官方页口径不一**（Patch Manager Plus 20+5 vs 25 设备；Endpoint Central 25 端点 vs 25 台式机 + 25 移动端；Endpoint Central MSP 被第三方称「免费 250 端点 1 年」，**与其余口径严重冲突且未获官方证实**）；② **EDR / Malware / Ransomware / DEX Manager / OS Deployment / Private Access 均是付费附加模块**（第三方定价分析：50 工作站年费 $195–$995 不等，额外技术员另计）——「一份许可搞定」与实际账单有落差；③ 客户侧反馈指出 UI 学习门槛与自动化协作损耗仍在（官方以 AEM 统一五层作为回应）。

> **配套演进（不进 S 列表）**：Android Enterprise Gold 合作伙伴身份、信创（UOS / 麒麟）原生适配、Vulnerability Manager Plus 与 Endpoint Central 的模块边界调整（官方弃用公告）、Browser Security Plus 的 JRE / Tomcat / Nginx 版本跟随升级等，属**生态与工程配套**。

---

---

# 大功能点 7：特权访问与身份治理 —— 守得住

## 7.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 7.1 | PAM360 原生 CIEM（云基础设施权限管理） | 2024-11-26（博客披露 beta 完成） | A / B | 自动发现云权限、风险暴露图、一键收敛多余权限 |
| 7.2 | Key Manager Plus 7.0（Build 7000）：emSign CA 集成 + 全新 UI | 2024-11 | A | 请求 / 获取 / 导入 / 部署 / 吊销 emSign 证书；新增域名白名单 |
| 7.3 | ADSelfService Plus：macOS 15 Sequoia 登录 MFA（Apple 芯片） | 2025-01-02（Build 6510） | A | macOS 登录界面自助改密 / 解锁 |
| 7.4 | **PAM360 7.5（Build 7500）：特权任务自动化 PTA（Qntrl Circuits 驱动）** | 2025-04-08 | A | 无凭证执行特权任务、按需 / 排程自动化、任务上下文 JIT 授权、任务结束自动回收 |
| 7.5 | PAM360 Build 7510：AI 洞察（BYOK 接入 OpenAI）—— AWS 内联策略生成、SSH/Telnet 会话录制 AI 摘要；特权提权（Windows 本地安全策略集成） | 2025-04-17 | A | 分析用户行为模式、检出错权风险并生成摘要 |
| 7.6 | Access Manager Plus 4.4（Build 4400）：共享连接可用自身或共享备用凭据发起远程会话、计划性访问申请（Later）、域连接访问控制 | 2025-04-02 | A | 连接所有者可审阅、修改、批准申请 |
| 7.7 | ADSelfService Plus：Red Hat / Rocky Linux MFA + 短信告警；1Kosmos 作为 SSO/SAML MFA 身份提供方；Windows 本地用户 MFA（含 UAC/RDP） | 2025-04-22 / 05-29 / 06-24 | A | 支持 Entra ID 中国区租户密码同步（中国 / 美国 / 全球区域） |
| 7.8 | **PAM360 AI 治理的最小权限策略 + 影子管理员风险自动修复** | 2025-05-11（发布公告） | B | CIEM 模块生成 AI 最小权限策略、自动修复 shadow admin 风险、实时访问 / 会话摘要 |
| 7.9 | ADManager Plus：**风险暴露管理（攻击路径映射）**、动态组成员资格 | 2025-06 | A | 映射潜在攻击路径与分析提权路线并给收敛建议；按规则自动更新安全 / 分发组 |
| 7.10 | Key Manager Plus 7040 / 7050 / 7060：ACME 自动续期（Let's Encrypt / Buypass / ZeroSSL）、Azure 应用证书与客户端密钥发现、AWS-ACM 自动部署审计 | 2025-06 ~ 2025-09 | A | 第三方 CA 自动续期后自动部署到目标服务器 |
| 7.11 | ADSelfService Plus：FIDO Passkey 注册与 MFA 注册审计报表 | 2025 | A | TOTP 一次性使用防重放；Passkey 注册数据纳入审计 |
| 7.12 | **ADManager Plus Build 8030：内置 AI 助手 Zia + Zia Insights** | 2025-10-30 | A | 自然语言执行 AD 管理操作与生成报表；AD Explorer 做组成员异常检测、特权组识别与对等比较评分 |
| 7.13 | ADManager Plus：AD / Entra ID 对象时间点回滚 | 2025-10-30 | A | 高级恢复选项卡 + 细粒度筛选，撤销修改或恢复丢失数据 |
| 7.14 | Access Manager Plus Build 4401 / 4402：修复 CVE-2025-11669（未授权访问，可对任意受管资源发起远程会话）、修复管理员可自批自建角色的授权缺陷 | 2025-10-15 / 2025-12-22 | A | 同批影响 PAM360（8202）与 Password Manager Pro（13221） |
| 7.15 | Password Manager Pro：80+ 资源类型模板、请求-放行工作流、FIPS 140-2 合规模式、PCI DSS / ISO 27001 / NERC-CIP / GDPR 合规就绪 | 2025（现行） | A | 集中密码保险库、定期轮转、应用间密码管理、SSH/RDP/Telnet 会话录制；无用户数上限 |
| 7.16 | ADManager Plus Marketplace 扩展 | 2026-01 | A | 从 ManageEngine Marketplace 安装第三方扩展并管理其中身份 |
| 7.17 | **Key Manager Plus：零触控证书生命周期管理**（面向 47 天 TLS 证书有效期新规） | 2026-07-14 | B | 推证书到目标服务器 + 运行配置脚本 + 重启依赖服务 + 通知，全流程无人干预 |
| 7.18 | RecoveryManager Plus：备份不可变性（Azure Blob / AWS S3 / Wasabi）防勒索、Microsoft Teams 备份、BitLocker 恢复密钥检索、SIEM 集成（syslog 转发备份 / 恢复审计日志） | 2025-01-30 ~ 2025-11-10 | A | 备份动作可被 SIEM 关联与审计；因 Azure AD Graph 2025-02 退役改用 Microsoft Graph API |
| 7.19 | 分析师位置：2023 Gartner MQ for PAM **Challenger**（当年唯一从 Niche 跨越到 Challenger 的厂商）；2025-10 再次 **Challenger**；KuppingerCole PAM **Market Leader（2026）**、身份治理 **Market Leader（2024）** | 2023 / 2024 / 2025-10 / 2026 | A | — |

## 7.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织）。痛点编号 P1…Pn 与下节解法 S1…Sn 一一对应。

- **P1｜特权账号与凭据散落在个人手上，离职就是风险敞口**。共享管理员口令、跳板机上的明文配置、前任留下的服务账号——**没人能完整说清「谁掌握着哪些特权」**；一次人员变动就要做一轮清理，而清理往往做不干净。（**合规 / 人**）
- **P2｜云上权限过度授予，没人看得清，也没人敢收**。云原生环境里权限靠 IAM 策略堆出来，日积月累留下大量多余授权与「影子管理员」；**收权限怕停业务，不收怕出事**。（**合规 / 钱**）
- **P3｜证书到期导致业务中断，续期靠人记**。TLS 证书有效期持续缩短（新规趋向 47 天），靠人工记台账续期的模式已经不可持续；**一次忘记续期就是一次对外服务中断**。（**时间 / 钱**）
- **P4｜审计要证明「谁在何时访问了什么」，而会话录像人工看不过来**。特权会话录像动辄数百小时，审计时既没人看得完，也无法快速定位到可疑片段；**「有录像」与「能举证」是两件事**。（**合规 / 人**）
- **P5｜AD 组权限异常与横向移动没有痕迹**。成员被悄悄加进特权组、服务账号权限被提升，这些动作在 AD 日志里淹没在日常噪声中；**等到发现时，攻击者已经横向移动很久了**。（**合规 / 组织**）

## 7.3 它是如何解决的

**架构约束（由痛点倒推）**

| 架构约束 | 由哪条痛点倒推 | 落到了哪些功能 |
| --- | --- | --- |
| 凭据必须集中、可轮转、可即时下发与回收 | P1 | Password Manager Pro 保险库、PAM360 PTA（JIT 授权 + 任务结束自动回收） |
| 云权限必须被持续发现、可视化并可自动收敛 | P2 | 原生 CIEM、AI 最小权限策略、影子管理员自动修复、风险暴露图 |
| 证书全生命周期必须无人干预 | P3 | CLM（请求 / 获取 / 导入 / 部署 / 吊销）、ACME 自动续期、零触控推送 + 服务重启 |
| 会话记录必须可被机器摘要与检索 | P4 | AI 会话录制摘要（SSH/Telnet）、实时访问摘要、会话录制与检索 |
| 身份层异常必须与攻击路径关联起来看 | P5 | ADManager Plus 风险暴露管理（攻击路径映射）、Zia Insights 组成员异常检测、ADAudit Plus NHI 审计与 Attack Surface Analyzer |

在上述约束下，逐条对应 P1–P5 的解法是：

- **S1｜集中保险库 + 即时授权 + 自动回收**（→ 解 P1）。**Password Manager Pro** 提供集中密码保险库、定期轮转、应用间密码管理与请求-放行工作流（80+ 资源类型模板，**无用户数上限**）；**PAM360 7.5（2025-04-08）的特权任务自动化（PTA）** 由 Qntrl Circuits 驱动，做到**无凭证执行特权任务**——凭据**即时下发**、**任务上下文 JIT 授权**、**任务结束自动回收**；Access Manager Plus 4.4 增加**计划性访问申请（Later）**与**域连接访问控制**。**P1 的解法是「特权不再属于人，而属于被批准的会话」。**
- **S2｜原生 CIEM + AI 最小权限 + 影子管理员自动修复**（→ 解 P2）。**2024-11 完成 CIEM beta**：自动发现云权限、生成风险暴露图、一键收敛多余权限；**2025-05-11** 进一步由 **AI 生成最小权限策略**、**自动修复 shadow admin 风险**，并给出实时访问与会话摘要。**边界**：自动收敛权限属高风险动作，实践中需与业务方确认影响面——**「能收」与「敢收」之间仍需人工决策**。
- **S3｜证书生命周期管理做到无人干预**（→ 解 P3）。**Key Manager Plus 7.0（2024-11）** 集成 emSign CA 并重构 UI；**7040（2025-06）** 支持 **ACME 自动续期**（Let's Encrypt / Buypass / ZeroSSL）并在续期后自动部署到目标服务器；**7050（2025-07）** 发现并集中管理 **Azure 应用证书与客户端密钥**；**7060（2025-09）** 审计 AWS-ACM 自动部署状态；**2026-07-14** 推出**零触控证书生命周期管理**（推证书 → 运行配置脚本 → 重启依赖服务 → 通知），明确针对 **47 天证书有效期新规**。**P3 的解法是把「记台账」这项人工职责整体取消。**
- **S4｜会话与访问的 AI 摘要**（→ 解 P4）。**PAM360 Build 7510（2025-04-17）** 引入 **AI 洞察（BYOK 接入 OpenAI）**：生成最小权限策略、云权限风险修复摘要，以及 **SSH / Telnet 会话录制的 AI 摘要**；2025-05 的公告补充实时访问与会话摘要。**这把「几百小时录像」压缩成「可读的访问叙事」**——审计时先读摘要定位可疑片段，再回看录像举证。**边界**：摘要由模型生成，**不能替代原始录像的举证能力**；且 BYOK 意味着客户需自行承担 token 成本与数据出境评估。
- **S5｜身份层异常与攻击路径关联**（→ 解 P5）。**ADManager Plus** 在 2025-06 引入**风险暴露管理（攻击路径映射）**——映射潜在攻击路径、分析提权路线并给出收敛建议；**动态组成员资格**按规则自动更新组；**2025-10-30 Build 8030** 引入 **Zia Insights**：在 AD Explorer 中做**组成员异常检测、特权组识别与对等比较评分**；配套**对象时间点回滚**（撤销修改或恢复丢失数据）。**ADAudit Plus** 侧补齐 **非人类身份（NHI）审计**（服务主体 / 托管标识登录及其权限与凭据的增删改）、**Data Access Analyzer**、**Group removal simulator**、**Platform Activity Explorer**。**P5 的解法是「把身份层的异常与它可能通向哪里放在同一张图上」。**

> **边界**：① **窗口内 PAM / IAM 产品线修复了大量高危 CVE**（CVE-2025-11669 未授权远程会话、CVE-2026-6213 第三方包 RCE、CVE-2026-12263 认证绕过、CVE-2026-2740 等），**这批产品的补丁纪律本身就是安全风险的一部分**；② Access Manager Plus 与 RecoveryManager Plus 未找到官方定价页，价格需询价；③ CIEM 与最小权限自动收敛在实际落地中依赖云端权限模型的完整覆盖，多云异构场景覆盖度需逐云验证。

> **配套演进（不进 S 列表）**：ADSelfService Plus 的 macOS / Linux / Windows 本地用户 MFA 扩展、1Kosmos 身份源集成、FIDO Passkey 支持属**认证方式跟随**；RecoveryManager Plus 的 S3 兼容存储、门户品牌定制属**交付配套**；Microsoft Graph API 迁移属**依赖变更应对**。

---

# 大功能点 8：IT 数据分析与 FinOps —— 算得明

## 8.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 8.1 | **Analytics Plus 6.0**（AI 驱动、无代码 ML、17+ IT 集成、AutoML、异常检测、多变量预测） | 2024 | A / B | 定位为「上下文决策智能平台」，作为 ManageEngine 各产品的分析底座 |
| 8.2 | Zoho Analytics 6.0（DSML Studio、统一指标层、流分析、250+/500+ 数据连接器、AutoML + Python Code Studio、OpenAI BYOK） | 2024 | A / B | 与 Analytics Plus 同源，覆盖更广的商业分析场景 |
| 8.3 | Analytics Plus：Ask Zia AI 驱动分析（可配置洞察 + 复杂查询） | 2024-11-27（Build 6100） | A | 选择列生成 Zia Insights；对话模式处理复杂数学 / 相关性查询 |
| 8.4 | Analytics Plus：Linked Workspaces（跨工作区视图同步） | 2025-01-16（Build 6110） | A | 一键把主工作区视图变更同步到次工作区 |
| 8.5 | Analytics Plus：RingCentral / Mosyle 集成 | 2025-02-11（Build 6120） | A | 呼叫中心预置洞察；Mosyle 管理 Apple 设备的数据分析 |
| 8.6 | Analytics Plus：Gantt 图 + **MCP Server（Beta）** | 2025-08-12 | A | 经 Model Context Protocol 让 AI 模型与 Analytics Plus 交互 |
| 8.7 | Analytics Plus：**智能体 AI**（Ask Zia Pipeline Builder / Transform by Example） | 2025-08-11 | A | 自然语言构建 / 清洗 / 自动化 ETL 数据管道，人机协同 |
| 8.8 | **Analytics Plus：Ask Zia Action Skills**（Zoho LLM 驱动） | 2025-10-24 | A | 在对话内导出数据、共享报表、调度邮件、生成洞察 |
| 8.9 | **CloudSpend 多门户 FinOps 架构** | 2025-11-24 | A | 为 MSP / CSP / 多租户企业提供独立门户 + 统一治理；含 AI 异常检测与预测 |
| 8.10 | CloudSpend：免费跟踪每月至 $3,000 的 GCP / AWS / Azure 支出，付费自超出部分 1% 起 | 2025 | A | 计费锚点与免费额度 |
| 8.11 | **MSP Central 统一平台**（RMM + PSA + 服务器监控，模块化云原生多租户） | 2025-06-24 | A | AI 工单摘要 / 情绪检测 / 告警关联；20+ 工具集成 |
| 8.12 | 各产品线的「AI 摘要 / 洞察」横向铺开（OpManager Zia Insights、AM Monitor AI Insight、Site24x7 Zia 跨平台助手、SDP Zia 仪表板） | 2025（约，部分未标日期） | A / B | 自然语言提问获取洞察；自动生成日志解析模式与脚本 |
| 8.13 | Analytics Plus 2026：**Ask Zia 2.0 / Key Driver Analysis** | 2026（约） | A | 由 Zoho LLM 驱动的上下文智能；Key Driver Analysis 识别影响特定趋势 / 指标的关键因子 |
| 8.14 | ServiceDesk Plus / Log360 / OpManager 的数据可统一汇入 Analytics Plus 做跨产品报表 | 2024 ~ 2026（持续） | A | 「17+ IT 集成」即指把 ManageEngine 自家产品数据作为原生数据源 |

## 8.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织）。痛点编号 P1…Pn 与下节解法 S1…Sn 一一对应。

- **P1｜运维数据散在多个产品里，跨产品报表要人工导表拼接**。工单、监控、日志、终端的数据各在一套系统，做一份「本月 IT 运营报告」要人工导出、对齐字段、拼 Excel；**同一个数字在不同部门手里还有不同版本**。（**人 / 时间**）
- **P2｜要做预测与异常检测，得先请个数据科学家**。客户侧 IT 团队通常没有数据科学能力；要建模型就得买工具、招人、写代码，**「想做」与「做得了」之间隔着人**。（**人 / 钱**）
- **P3｜多云支出失控，账单与资源归属说不清**。云成本按月疯涨，但「哪个业务、哪个团队、哪个项目花掉的」说不清；**成本优化只能靠事后拍脑袋砍资源**。（**钱 / 组织**）
- **P4｜MSP 在多客户、多控制台之间来回切**。一个客户事件要在多个控制台之间跳转，登录、查、再切回；**时间被切成碎片，规模一上来就撑不住**。（**时间 / 组织**）
- **P5｜数据管道要工程师写 ETL，需求一变就得重做**。「想要这个报表」的需求到 IT 手里要排期、写脚本、测试；**等报表做出来，业务已经换了问题**。（**人 / 时间**）

## 8.3 它是如何解决的

**架构约束（由痛点倒推）**

| 架构约束 | 由哪条痛点倒推 | 落到了哪些功能 |
| --- | --- | --- |
| 各产品数据必须能作为原生数据源直接汇入分析层 | P1 | Analytics Plus 的 17+ IT 集成、统一指标层、Linked Workspaces |
| 建模必须无代码，且要能自动推荐 | P2 | AutoML、无代码 ML、Spotlight AI 推荐引擎、异常检测与多变量预测 |
| 云成本必须能按多租户维度切分与治理 | P3 | CloudSpend 多门户 FinOps、AI 异常检测与预测 |
| MSP 的多客户视角必须收进一个平台 | P4 | MSP Central（RMM + PSA + 服务器监控）、20+ 工具集成 |
| 数据管道必须能用自然语言搭建与清洗 | P5 | Ask Zia Pipeline Builder、Transform by Example |

在上述约束下，逐条对应 P1–P5 的解法是：

- **S1｜Analytics Plus 作为统一分析底座**（→ 解 P1）。**Analytics Plus 6.0（2024）** 以「17+ IT 集成」把 ManageEngine 自家产品的数据作为**原生数据源**直接汇入，并提供统一指标层；**Linked Workspaces（2025-01-16）** 让主工作区视图变更一键同步到次工作区，避免同一指标多处维护。对客户的意义是**「一份报表跨产品，不需要人工导表」**。**边界**：跨产品关联的完备度取决于各产品数据模型的字段对齐程度，**并非所有维度都能自动互通**。
- **S2｜无代码 ML + 自动推荐**（→ 解 P2）。**Analytics Plus 6.0** 提供 **AutoML、异常检测、多变量预测**，并配 **Spotlight AI 推荐引擎**（监控常见 IT 流程、识别瓶颈并给纠正策略建议），使客户**不需数据科学背景即可建模**。**边界**：AutoML 出来的是「可用模型」而非「可解释结论」；在需要业务方采信的场合，仍需人工补充解释（这一点与 Elastic 的 p_value / 变化点检测路线不同，ManageEngine 更偏「自动出结论」）。
- **S3｜CloudSpend 多门户 FinOps**（→ 解 P3）。**2025-11-24 发布多门户架构**：为 MSP / CSP / 多租户企业提供**独立门户 + 统一治理**，并内置 **AI 异常检测与预测**。免费额度为**每月跟踪至 $3,000 的 GCP / AWS / Azure 支出**，付费自超出部分 **1%** 起。官方引用 Gartner 预测「2025 全球公有云终端支出超 $723.4B」作为多云成本治理的市场论据。**P3 的解法是「先让每一笔钱能落到人头上」。**
- **S4｜MSP Central 统一多租户平台**（→ 解 P4）。**2025-06-24 发布 MSP Central**，把 **RMM + PSA + 服务器监控**做成**模块化云原生多租户**平台，内置 **AI 工单摘要、情绪检测、告警关联**，并提供 **20+ 工具集成**；配套 CloudSpend 多门户。**P4 的解法是「把 N 个控制台收成 1 个，把 N 个客户视角收进一个治理面」。** **边界**：MSP 场景的复杂度在于**客户间严格隔离与统一治理的平衡**——这一点官方只给出能力描述，缺少量化隔离验证。
- **S5｜自然语言建数据管道**（→ 解 P5）。**2025-08-11 引入智能体 AI**：**Ask Zia Pipeline Builder** 用自然语言构建 / 清洗 / 自动化 ETL 管道，**Transform by Example** 按示例驱动转换；**2025-10-24 引入 Action Skills**，可在对话内直接导出数据、共享报表、调度邮件、生成洞察；**2026 年 Ask Zia 2.0 + Key Driver Analysis** 进一步识别影响特定趋势 / 指标的关键因子。**P5 的解法是「把排期写脚本变成当场描述需求」。**

> **边界**：① **Analytics Plus 与 Zoho Analytics 的关系需澄清**：前者是 ManageEngine 侧的 IT 分析产品，后者是 Zoho 的通用 BI 平台，**两者同源但定位与连接器范围不同**，采购时须确认目标版本；② 分析层的能力上限受限于各产品数据模型，**跨产品「同名字段不同口径」问题不会被工具自动解决**；③ CloudSpend / MSP Central 属 2025 年后的新形态，**市场验证度尚低**。

> **配套演进（不进 S 列表）**：Zoho Analytics 250+/500+ 数据连接器扩张、DSML Studio、Python Code Studio 属**平台能力沿革**；RingCentral / Mosyle 集成属**生态配套**。

---

# 大功能点 9：商业化、交付与市场位置 —— 买得起

## 9.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 9.1 | 「永久许可 + 20% 年度维护与支持（AMS）」与「年度订阅」「云端按月」三轨并存 | 2023-01 ~ 2026-10（持续） | A / C | 永久许可 AMS 费率为发票金额 20%（第三方口径）；评估授权自下载 / 安装起 30 天 |
| 9.2 | 全产品线永久免费版 + 30 天全功能试用 | 2023-01 ~ 2026-10（持续） | A | OpManager 3 设备（B 级待确认）、Endpoint Central 25 端点、ServiceDesk Plus 5 技术员、Site24x7 50 网站、Log360 Cloud 50GB、17 个 Windows 工具完全免费 |
| 9.3 | OpManager 按设备授权（含该设备全部接口） | 2023-01 ~ 2026-10 | A | Standard 10 设备 $95 / 100 设备 $795 / 1000 设备 $4,095 |
| 9.4 | OpManager Nexus 订阅打包（网络 + 流 + AP + IP 与端口 + 服务器 + 应用 + 存储） | 2023-01 ~ 2026-10 | A | 50 设备 $1,233 / 500 设备 $7,667 / 1000 设备 $12,000；官方称比「OpManager + add-on」省 44% |
| 9.5 | ServiceDesk Plus 按技术人员数（+ 资产数）计费，终端用户不限量不收费 | 2023-01 ~ 2026-10 | A | Cloud Standard 起 $13 / Pro $27 / Enterprise $67 每技术员每月；Standard 单实例最多 5 技术员永久免费 |
| 9.6 | **AI 能力全版本不加价；Zia Agents 归 Enterprise 版** | 2025 ~ 2026 | A | 官方定价页明文；Zoho 侧跨产品 Zia Agents 平台按 token 计费（免费 10M token/月，超出 $1–$3 / 百万 token） |
| 9.7 | Log360 Cloud 计费从「按存储 GB」改为「按基础设施组件」 | 2026-05-16 | A | 日志源 / 域控 / 文件服务器 / 云账户 / 端点分别独立购买；检索 $10–13/GB·年、归档 $0.25/GB·年 |
| 9.8 | 中国区部署与合规：北京 + 上海数据中心、信创适配、国产模型（DeepSeek / SiliconFlow） | 2025-11 ~ 2026-09 | A / B | 支持本地部署与数据不出境；Log360 Cloud 合规报表含 ISLP（信息安全等级保护） |
| 9.9 | 海外数据驻留：Log360 Cloud 上线 UAE 数据中心 | 2026-06-16 | A | 官方称服务覆盖近 190 个国家 |
| 9.10 | Gartner MQ for PAM：2023 与 2025 **Challenger** | 2023 / 2025-10 | A | 2023 年唯一从 Niche 跨越到 Challenger |
| 9.11 | Gartner MQ for UEM / Endpoint Management Tools：**Challenger**（2026-01，4 个用例评分均 >4/5） | 2026-01 | B | 自主端点管理 4.40、UEM 4.10、安全中心管理 4.36、一线设备管理 4.25 |
| 9.12 | Gartner MQ for SIEM：2024 Major Player；2025 仅称「named in」未披露象限 | 2024 / 2025 | A | 官方徽章页自述「2025 年第八次入选」 |
| 9.13 | Gartner MQ for DEM：2024 首次入选 / 2025 **Niche Player**（Site24x7、OpManager Nexus、Applications Manager） | 2024-10-21 / 2025-10-27 | B | — |
| 9.14 | IDC MarketScape：UEM 全球 **Leader**（2025-12，第三次）、ITSM **Leader**（2024）、SIEM **Major Player**（2026-06）、Observability Platforms 2025 **Major Player** | 2024 ~ 2026 | A / B | — |
| 9.15 | Forrester Wave ESM Q4 2025 **Strong Performer**；KuppingerCole PAM **Market Leader（2026）**、身份治理 **Market Leader（2024）** | 2024 ~ 2026 | A | — |
| 9.16 | 客户案例与厂商自述收益（Samsung SDS MTTR/MTTI -60%、Atlanta Hawks 战略合作、5B / Aerostar / Kingspan 用 PAM360、UK 制造业客户称切换省 £400,000） | 2023 ~ 2026 | A（厂商自述）/ C（用户自述） | **均属厂商自述或单个用户自述，未经第三方独立验证** |

## 9.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织）。痛点编号 P1…Pn 与下节解法 S1…Sn 一一对应。

- **P1｜预算有限，但要覆盖的能力越来越多**。一个中小 IT 团队要同时管网络、服务器、应用、终端、工单、日志，**按企业级报价逐项买，预算在第一轮就被打穿**。（**钱**）
- **P2｜既有厂商续费暴涨、强制从永久许可转订阅，退出成本高**。客户已经付了多年永久许可，续费时被要求按订阅重买；**想换厂商，又要重做采集与集成**——这是一笔两边都要出血的账。（**钱 / 组织**）
- **P3｜等保 / 信创 / 数据驻留要求本地化与数据不出境**。受监管行业要求数据留在境内、要求信创适配；**而 AI 能力天然想调云端模型**，两者直接冲突。（**合规**）
- **P4｜采购要第三方背书，不能只听厂商说**。选型要走评审流程，需要分析师报告、同行评分、认证清单做依据；**没有第三方位置的厂商在第一轮筛选中就被排除**。（**组织**）

## 9.3 它是如何解决的

**架构约束（由痛点倒推）**

| 架构约束 | 由哪条痛点倒推 | 落到了哪些功能 |
| --- | --- | --- |
| 计费锚点必须与客户能理解的资产形态对齐 | P1、P2 | 按设备（含全部接口）/ 按技术员 / 按端点 / 按组件 |
| 必须存在一个「不花钱也能用起来」的入口 | P1 | 全产品线永久免费版 + 30 天全功能试用（第 9.2 条） |
| 许可模式必须允许客户按资金模型选择 | P2 | 永久许可 + AMS、年度订阅、云端按月三轨 |
| AI 不能成为额外采购门槛 | P1、P3 | AI 全版本不加价；本地 / 国产模型可选 |
| 数据驻留与信创必须可满足 | P3 | on-prem 部署、北京 / 上海 / UAE DC、KingbaseES 与 UOS / 麒麟适配、DeepSeek / SiliconFlow |
| 必须有可被采购流程引用的第三方背书 | P4 | Gartner MQ / IDC MarketScape / Forrester Wave / KuppingerCole / ITIL 与 PinkVERIFY 认证 / G2 评分 |

在上述约束下，逐条对应 P1–P4 的解法是：

- **S1｜全产品线永久免费版 + 30 天全功能试用**（→ 解 P1）。官方首页明确「Free, 30-day trials with access to all premium features」：**Endpoint Central 永久免费 25 端点（无功能阉割，仅 OS 部署限 4 工作站 + 1 服务器）、ServiceDesk Plus 单实例最多 5 技术员永久免费、Site24x7 50 个网站监控永久免费（5 分钟频率 / 邮件告警 / 无需信用卡）、Log360 Cloud 50GB 免费、OpManager 免费版 3 台设备（B 级，待官方页确认）、17 个 Windows 管理工具完全免费且无端点上限**。**免费版通常不含高级 AI / 安全能力**（如 Endpoint Central 免费版不含 EDR / DEX 附加模块）。**P1 的解法是「让客户先零成本把基础监控跑起来」。**
- **S2｜三轨许可 + 明确不涨价承诺**（→ 解 P2）。**永久许可 + 20% AMS**、**年度订阅**、**云端按月 / 按年**三条路并存，客户按自身资金模型选择；官方宣称 **OpManager 自 2018 年以来未涨价**，并在 PitStop 社区公开以「竞品续费涨价 3 倍、取消永久许可、强制订阅」为对照做迁移营销（**厂商营销口径**）。**边界**：客户侧反馈明确点出「**最终账单难以预测**——永久许可每年加 20% 维护费，服务器与笔记本分开计价，多个安全能力单独报价」，说明**低起价 ≠ 可预期的 TCO**；第三方定价分析也指出 Endpoint Central 的 EDR / Malware / Ransomware / DEX Manager / OS Deployment / Private Access **全部是付费附加模块**（50 工作站年费 $195–$995 不等）。
- **S3｜AI 不加价 + 本地 / 国产模型路径**（→ 解 P3）。官方定价页明文「预测式、生成式与对话式 AI 能力在所有版本可用且不额外收费」（**Zia Agents 归 Enterprise**）；**本地版 Ask Zia 可由客户选择 Zia LLM / ChatGPT / Azure OpenAI**；**中国区 2025-11-19 接入 DeepSeek、2026-09-23 接入 SiliconFlow**，配合 PII 匿名化与遮蔽；**OpManager v12.8 支持人大金仓 KingbaseES**，Endpoint Central 信创原生适配 UOS / 麒麟。**P3 的解法是「让 AI 能力有一条不出境的路」。** **边界**：跨产品 Zoho 侧 Zia Agents 平台按 token 计费（免费 10M token/月，超出 $1–$3 / 百万 token），与「产品内嵌 Zia 免费」不是同一层面，**采购时必须分开确认**。
- **S4｜第三方分析师位置与认证矩阵**（→ 解 P4）。窗口内的位置包括：**Gartner MQ** PAM Challenger（2023、2025-10）、UEM Challenger（2026-01）、ITSM 挑战者（2026-08，**仅见中文站自述，待原文核实**）、DEM Niche Player（2024 / 2025）、SIEM 2024 Major Player、ITSM 中的 AI 应用 Niche Player（2025-09）；**IDC MarketScape** UEM Leader（2025-12，第三次）、ITSM Leader（2024）、SIEM Major Player（2026-06）、Observability Platforms 2025 Major Player；**Forrester Wave ESM Q4 2025 Strong Performer**；**KuppingerCole** PAM Market Leader（2026）与身份治理 Market Leader（2024）；**ITIL 14 项实践认证 + PinkVERIFY 10 项流程认证**；第三方评分侧 Endpoint Central G2 **4.5/5（1,142 评）**、Applications Manager G2 **4.7/5**、OpManager G2 **4.5/5**、Password Manager Pro Gartner Peer Insights **4.4（337 评）**。**P4 的解法是「给采购流程提供足够可引用的外部依据」。**

> **边界**：① **「一个价格覆盖全部」不成立**——Monitor（按设备含全部接口）之外的 Flow / DPI / NCM / RUM / 存储 / 应用日志 / 附加安全模块都是按接口、PV、日志量、磁盘数、端点数分别计费的 add-on；② 区域定价差异明显（同一产品中文站、台湾站、德国站价格不同，ServiceDesk Plus 本地版两个官方 pricing 页价格互不相同）；③ 厂商委托研究（Forrester TEI 442% ROI、KuppingerCole 219% ROI）**属厂商委托，不能当作第三方独立验证**。

> **配套演进（不进 S 列表）**：Zoho 的农村研发中心战略、19K+ 员工规模、无外部融资的股权结构属**公司治理**；官方 awards 页所列 AT&T / Barclays / Sony / GE / NASA 等客户名单**未见客户方公开确认**，属**营销材料**；「超过一半营收投入 R&D」存在 40% / 60% 等多种口径，属**未证实的公司自述**。

---

# 附一：完整时间线（倒序）

> **口径**：只列本报告各组中作为「解法」的关键事件；日期取官方发布日或 build 日期；官方未标日期者标注「约」并说明依据。

| 日期 | 产品 / 平台 | 事件 | 组 |
| --- | --- | --- | --- |
| 2026-10-06 | OpUtils 12.9.149 | Switch Port Mapper 权限修复（受限子网 IP / PoE） | 2 |
| 2026-10（Webinar 2026-10-15） | ServiceDesk Plus Cloud | 全新体验 beta：常驻 Ask Zia、Custom Pages、Headless ITSM（Zoho MCP） | 4 |
| 2026-09-23 | ServiceDesk Plus 本地 | 接入 SiliconFlow（国产合规大模型） | 1 |
| 2026-09-21 | Applications Manager Build 182400 | AI Summary for Alarms、Docker Swarm 监控、AppLogs | 3 |
| 2026-09-16 | ServiceDesk Plus Cloud | Custom Module Workflow、Focus Mode、自定义模块动作节点 | 4 |
| 2026-09-10 | ServiceDesk Plus Cloud | **SLA 违约预测（by Zia）**、AI Insights、SharePoint 接入、自定义 Guardrails | 1 / 4 |
| 2026-09-10 | NetFlow Analyzer 12.9.147 | Security Analytics 支持 Microsoft SQL Server | 2 |
| 2026-08-25 | Log360 / ELA | 安全修复 CVE-2026-16900、CVE-2026-12263 | 5 |
| 2026-08-20 | OpUtils 12.9.134 | **PoE 监控**；Cisco Small Business VLAN 改用 Q-BRIDGE-MIB | 2 |
| 2026-08-17 | Log360 | Marketplace 扩展：Bitdefender / CrowdStrike Falcon / Okta / MikroTik | 5 |
| 2026-08-12 | NetFlow Analyzer 12.9.133 | TOPdesk 集成（告警转事件） | 2 |
| 2026-08-07 | ServiceDesk Plus | 官方（中文站）自述入选 2026 Gartner ITSM 魔力象限 Challenger | 9 |
| 2026-07-31 | NetFlow Analyzer 12.9.121 | Security Analytics 告警通知 | 2 |
| 2026-07-14 | Key Manager Plus | 零触控证书生命周期（面向 47 天有效期新规） | 7 |
| 2026-07-06 | Log360 | 安全修复 CVE-2026-2740 / CVE-2026-8923 / CVE-2026-13594 | 5 |
| 2026-06-30 | ManageEngine 全平台 | 开发者生态：17+ 伙伴 / 170+ 扩展，Zia Agent 经 Marketplace 分发 | 1 |
| 2026-06-30 | Log360 | 迁移兼容 Unified Log360（构建 5570） | 5 |
| 2026-06-30 | OpUtils 12.9.105 | Rogue DHCP Discovery、Route 53、Microsoft DNS、BIND 导入 | 2 |
| 2026-06-24 | Access Manager Plus 4404 | 修复认证绕过 CVE-2026-12263 | 7 |
| 2026-06-18 | NetFlow Analyzer 12.9.102 | AI Traffic Visibility、AI Service Mapping、GenAI（OpenAI/Ollama/DeepSeek）、Zia | 2 |
| 2026-06-16 | Log360 Cloud | 上线 UAE 数据中心 | 5 / 9 |
| 2026-05-29 | ServiceDesk Plus Cloud | Workflow Assist 全版本可用；Zia 支持附件生成工作流 | 4 |
| 2026-05-22 | NetFlow Analyzer 12.8.735 | 安全事件转发 SIEM；接口利用率热力图 | 2 |
| 2026-05-21 | ManageEngine 全产品线 | **Zia Agents 全线 GA**（多 Agent 编排 + 审计 + MCP；数据不用于训练） | 1 |
| 2026-05-20 | Log360 Cloud | **Ask Zia + Zia Agent Studio + Zoho MCP**（用户活动审查 / 告警关联代理） | 5 |
| 2026-05-16 | Log360 Cloud | **许可改为按基础设施组件计费** | 5 / 9 |
| 2026-05-12 | Log360 | **原生 SOAR**（300+ 响应动作、低代码剧本） | 5 |
| 2026-05-08 | Log360 Cloud | 日志采集失败告警 | 5 |
| 2026-04-22 | OpUtils 12.8.720 | IPAM 授权分层（Management 解锁 DNS/DHCP 配置写入） | 2 |
| 2026-04-21 | OpManager v12.8 | KingbaseES、**OpenAI 集成**、WCAG、约 300 设备模板、MTTR/MTBF/MTTF/MTTA/Flap Count | 1 / 2 |
| 2026-04-13 | NetFlow Analyzer 12.8.719 | **MCP 服务器支持**（Claude Desktop / VS Code / Cursor） | 1 / 2 |
| 2026-04-03 | OpUtils 12.8.707 | Cisco Meraki 交换机终端 MAC 采集 REST API | 2 |
| 2026-03-17 | Endpoint Central | **EDR + Secure Private Access** 附带模块 | 1 / 6 |
| 2026-03-06 | Applications Manager 18 | 主版本发布 | 3 |
| 2026-02-16 | ServiceDesk Plus MSP 15120 | 从 Microsoft Entra ID 同步用户 | 4 |
| 2026-02-06 | OpManager 12.8.635 | 修复版 | 2 |
| 2026-01-22 | ServiceDesk Plus MSP 15110 | Account 模块重构、2FA、Dynamic throttle | 4 |
| 2026-01-20 | OpManager / Nexus / OpUtils 12.8.634 | Jira SM(Cloud)、Splunk SIEM 转发、Remote Collector、Proxmox VE、Aruba SD-WAN、ilert；**Anomaly 仪表盘 + Anomaly Summary**；OpUtils IPAM/DNS/DHCP 增强 | 1 / 2 |
| 2026-01-09 | NetFlow Analyzer 12.8.665 | Smart Upgrade / 应急补丁、移动端推送 | 2 |
| 2026-01-09 | Applications Manager Build 179300 | Podman、SIEM/Splunk、Amazon MSK、Azure Data Factory、MySQL InnoDB ClusterSet | 3 |
| 2026-01 | ADManager Plus | Marketplace 扩展 | 7 |
| 2026（约） | Endpoint Central | **自主终端管理（AEM）**：漂移自愈 + 硬件故障预测 + Zia 生成自动化 | 1 / 6 |
| 2026（约） | Endpoint Central AI | 脚本 / 工作流生成、自主打补丁、JIT 提权评估、KB 自动生成 | 6 |
| 2026（约） | Analytics Plus | Ask Zia 2.0 / Key Driver Analysis | 1 / 8 |
| 2026 | KMP / Browser Security / Vulnerability Manager | macOS 26、Syslog 转发、Windows Server 2025、Splunk add-on 1.0.6 | 6 / 7 |
| 2025-12-22 | Access Manager Plus 4402 | 修复管理员自批自建角色授权缺陷 | 7 |
| 2025-12-12 | ServiceDesk Plus Cloud | RCA by Zia（根因分析报告） | 1 / 4 |
| 2025-12 | ServiceDesk Plus 本地 v15200 | **Ask Zia（ChatGPT + MCP）**、Request Workflows、破坏性变更一批 | 1 / 4 |
| 2025-11-24 | CloudSpend | 多门户 FinOps 架构 | 8 |
| 2025-11-19 | ServiceDesk Plus + Site24x7 | **集成 DeepSeek（面向中国）** | 1 / 9 |
| 2025-11-11 | Log360 / ELA | SSO（SAML / NTLM）；**不可能旅行检测** | 5 |
| 2025-11-10 | RecoveryManager Plus 6311 | SIEM 集成（syslog 转发备份 / 恢复审计） | 7 |
| 2025-11-04 | ServiceDesk Plus Cloud | Zia 模型更新为 `Zia-zlabs-qwen3-30B-instruct-v1`；RBM 编辑页重构 | 1 / 3 |
| 2025-11 | ServiceDesk Plus Cloud | WhatsApp 集成、SaaS Manager Plus、CI States | 4 |
| 2025-10-30 | ADManager Plus 8030 | **Zia + Zia Insights**、AD / Entra ID 对象时间点回滚 | 1 / 7 |
| 2025-10-24 | Analytics Plus | **Ask Zia Action Skills** | 1 / 8 |
| 2025-10-15 | Access Manager Plus 4401 | 修复 CVE-2025-11669 | 7 |
| 2025-10-13 | PAM | Gartner MQ for PAM 2025 **Challenger** | 9 |
| 2025-10-10 | NetFlow Analyzer 12.8.628 | Network Packet Sensor → Remote Collector | 2 |
| 2025-10 | OpUtils / Firewall Analyzer | MAC 过滤 DHCP 保留；VPN 标签页 | 2 |
| 2025-09-23 | ServiceDesk Plus Cloud | **「最大 GenAI 版本」**：Ask Zia 多模态、Workflow Assist、各类 Generator | 1 / 4 |
| 2025-09-16 | Log360 / ELA 构建 13000 | **检测架构重构**：集中控制台、2,000+ MITRE 规则、规则调优、水平扩展 | 5 |
| 2025-09-10 | ADAudit Plus 8520 | Security Hardening 页、PostgreSQL 17.5、工单集成扩展 | 5 |
| 2025-09-04 | EventLog Analyzer | 预置扩展、自定义 Widget、REST API V2 | 5 |
| 2025-09 | Log360 | NIS2 / FADP 合规框架；playbook 智能推荐 | 5 |
| 2025-08-26 | Endpoint Central / DEX Manager Plus | **DEX 数字员工体验**（20+ 指标 / 1,000+ 遥测点） | 1 / 6 |
| 2025-08-25 | NetFlow Analyzer 12.8.611 | ML-based Security Analytics（MITRE ATT&CK） | 2 |
| 2025-08-12 | Analytics Plus | Gantt 图 + **MCP Server（Beta）** | 8 |
| 2025-08-11 | Analytics Plus | **智能体 AI**：Pipeline Builder、Transform by Example | 1 / 8 |
| 2025-07-18 | Site24x7 | Zia + OpenAI / Azure OpenAI（BYOK） | 1 |
| 2025-07-17 | Zoho 平台 | **Zia LLM（1.3B/2.6B/7B）+ ASR + 25+ Agent + Agent Studio + MCP server** | 1 |
| 2025-06-30 | NetFlow Analyzer 12.8.582 | Splunk / SIEM（UDP）转发、PagerDuty | 2 |
| 2025-06-27 | EventLog Analyzer | JSON 解析支持 | 5 |
| 2025-06-26 | Log360 Cloud | Zia Insights + UEBA | 1 |
| 2025-06-24 | MSP Central | 统一 RMM + PSA + 服务器监控平台 | 8 |
| 2025-06 | ADManager Plus | 风险暴露管理（攻击路径映射）、动态组成员资格 | 7 |
| 2025-05-21 | EventLog Analyzer | 关联索引优化、规则条件降误报 | 5 |
| 2025-05-11 | PAM360 | AI 最小权限策略 + 影子管理员风险自动修复 | 7 |
| 2025-04-22 | NetFlow Analyzer 12.8.552 | 高级报表、IP 映射过滤、DPI 合并 TLS Hello | 2 |
| 2025-04-17 | PAM360 7510 | **AI 洞察（BYOK）**、特权提权 | 1 / 7 |
| 2025-04-08 | PAM360 7.5 | **特权任务自动化 PTA** | 1 / 7 |
| 2025-04-04 | Site24x7 RUM | **RUM Events**（rage click / quick back / excessive scrolling） | 3 |
| 2025-04-01 | Site24x7 RUM | **Session Replay（会话回放）** | 3 |
| 2025-04-02 | Access Manager Plus 4.4 | 计划性访问申请、域连接访问控制 | 7 |
| 2025-03-10 | Site24x7 | **Ask Zia（AIOps 分析助手）** | 1 / 3 |
| 2025-03-03 | Applications Manager RBM | AM UI 内录制 RBM 脚本 | 3 |
| 2025-02-04 | Zoho 平台 | **Zia Agents + Agent Studio + Agent Marketplace 公布（预览）** | 1 |
| 2025-01-31 | ADAudit Plus 8500 | Attack Surface Analyzer、Azure Intune 审计、Windows LAPS 审计 | 5 |
| 2025-01-30 | NetFlow Analyzer 12.8.511 | EE 取消 100 collector 上限 | 2 |
| 2025-01-30 | RecoveryManager Plus 6220 | 备份不可变性、S3 / Wasabi 备份仓库、Microsoft Graph API | 7 |
| 2025-01-16 | Analytics Plus 6110 | Linked Workspaces | 8 |
| 2025-01-10 | NetFlow Analyzer 12.8.509 | SNMP 接口名自定义 | 2 |
| 2025-01-02 | ADSelfService Plus 6510 | macOS 15 Sequoia 登录 MFA | 7 |
| 2024-12-13 | Log360 | **Zia Insights**（日志分类 + ATT&CK 映射 + 告警摘要） | 1 / 5 |
| 2024-11-27 | Analytics Plus 6100 | Ask Zia AI 驱动分析 | 8 |
| 2024-11-26 | PAM360 | 原生 **CIEM**（云基础设施权限管理） | 7 |
| 2024-11 | Key Manager Plus 7.0 | emSign CA 集成 + 全新 UI | 7 |
| 2024-10-21 | Applications Manager RBM | 支持 TOTP 双因素 | 3 |
| 2024-10-21 | ManageEngine | 首次入选 Gartner MQ for DEM（Niche Player） | 9 |
| 2024-10 | Log360 | NIS2 合规报表 | 5 |
| 2024-09-16 | AM RBM / EUM Agent | Firefox 111→128、Selenium 4.5.3→4.22.0 | 3 |
| 2024-09 | Log360 | PCI DSS 4.0、ISO 27001:2022 开箱报表 | 5 |
| 2024-07 | OpManager / OpUtils / Firewall Analyzer | Alarm correlation rule；报表位置信息；Task Audit | 2 |
| 2024-07 | Log360 | PAM360 集成 | 5 |
| 2024-05 | Log360 | 暗网监控、EDR 集成、Sigma 规则导入、Salesforce 云监控 | 5 |
| 2024-02-27 | Applications Manager 17 | 主版本发布 | 3 |
| 2024-02-08 | Log360 UEBA | **实时异常检测** | 1 / 5 |
| 2024-02 | Log360 | Incident Workbench | 5 |
| 2024 | Analytics Plus 6.0 / Zoho Analytics 6.0 | AI 驱动、无代码 ML、17+ IT 集成、DSML Studio | 1 / 8 |
| 2023-11-08 | Endpoint Central MSP | 云版发布 | 6 |
| 2023-11 | OpManager / OpUtils / Firewall Analyzer | NetFlow Pattern Analysis；SPM Tree View；规则变更历史报表 | 2 |
| 2023-10-17 | Endpoint Central | **NGAV 原生杀毒**（深度学习 + 行为检测，边缘 AI） | 6 |
| 2023-09 | ServiceDesk Plus 本地 14500 | MFA、Change 模块 UAT 与 Release 阶段 | 4 |
| 2023-05-04 | Zoho 平台 | **Zia 集成 OpenAI**（13 款应用 GenAI 扩展）；宣布自研 LLM 路线 | 1 |
| 2023-04-26 | OpManager 12.7 | 版本发布 | 2 |
| 2023（约） | ServiceDesk Plus 本地 14000 | Timer Actions、Maintenance 模块、Security Meter | 4 |

---

# 附二：演进规律与对自研的启示

## 规律 1：ManageEngine 的四年是「AI 三次形态跃迁」，不是功能叠加

**2023-05（集成 OpenAI）** Zia 只是各产品里的一个「生成式扩展」；**2024-12（Zia Insights 铺开）** AI 变成横跨 ITOM / ITSM / SIEM 三条线的能力层，但模型仍是第三方的；**2025-07（自研 Zia LLM + Agent Studio + MCP）** 把模型与动作库都收回自己手里；**2026-05（Zia Agents 全线 GA）** AI 从「答得上」变成「做得动」。**值得注意的是四个阶段都伴随同一个关键词：数据不用于训练**——这不是技术选择，是**面向受监管客户的产品定位**。

> **对自研的启示**：AI 助手的形态每跃迁一次，「客户敢不敢用」的门槛就换一次。从「答」到「做」的那一步，真正的门槛不是模型能力，而是 **guardrails + 审计留痕 + 逐工具授权** 三件套。我方若要从 Read 类能力走向 Write 类能力，**审批门与审计必须先于动作能力上线**，否则会在安全评审阶段被整体否决。

## 规律 2：它的「降本」叙事建立在计费锚点上，而不是技术压缩上

与 Elastic（LogsDB / TSDB / pattern_text 把存储成本压下来）不同，ManageEngine 的成本叙事是**计费单位对齐**：**OpManager 按设备计费且包含该设备全部接口（无 sensor creep）**、**ServiceDesk Plus 按技术员计费且终端用户不限量**、**Log360 Cloud 按组件而非按 GB 计费**、**自 2018 年未涨价**。**这是商业模式的差异化，不是技术的差异化。**

> **对自研的启示**：客户感知到的「贵」有两层——**技术层（存不起、查不动）与商业层（账单不可预期、涨价不可控）**。我方在监控类产品上的定价单位若与客户的资产形态错位（比如按接口、按指标数），**客户的第一句抱怨就会落在账单上，而不是功能上**。定价锚点的选择优先级不低于功能开发。

## 规律 3：第三方一律止步标准 MIB 线——这是「设备侧」定位最硬的边界

本报告逐条核对官方文档后的结论是：OpUtils / OpManager 对交换机侧的全部采集**止步于标准 MIB（Bridge MIB / Interface MIB / Q-BRIDGE-MIB）+ ARP 表 + LLDP/CDP + 设备 REST API（Meraki）**。**读得到「表的内容」（MAC 表、ARP 表、端口状态、PoE 功耗、VLAN），读不到「表的行为」**（ACL 命中计数、policymap 命中率、TCAM 容量与溢出、FIB 内部表项、ASIC 转发行为）。而且「能不能看到」取决于 **profile / 扩展写没写**：Cisco 交换机的 SNMPv3 甚至需要设备侧额外配置（`context vlan-match prefix`）才能返回端口 MAC；Extreme Summit 需要显式开启 `dot1dTpFdbTable`。

> **⚠️ 对自研的最重要启示**：**这不是 ManageEngine 的能力上限，而是所有第三方厂商的共同天花板**。原厂（L1 层）之所以是「设备内部真相」的独占者，原因是 ASIC / 表项 / 芯片 drop reason / 协议状态机 / core dump 这些信息**根本不在标准 MIB 里，也无法从 CLI 稳定取出**。**我方作为设备原厂，在这一层有结构性、不可复制的优势**——锐捷 APM 的价值不该被定义为「也能做第三方监控」，而应该是「**回答第三方永远回答不了的那部分问题**」：表项是否正确、转发行为是否符合预期、TCAM 是否溢出、协议状态机是否卡在某一步。**第三方能做的（拓扑推断、端口定位、流量分析、阈值告警）应当被视为「必须对齐的基线」，而不是「可以差异化的战场」。**

## 规律 4：它的 AI 走「小模型 + 多路径 + 可替换」，而不是「一个大模型通吃」

Zia LLM 是 **1.3B / 2.6B / 7B 的小模型**（2025-11 起切到 30B 指令微调模型），部署在自有 DC；同时开放 **BYOK（OpenAI / Azure / Google AI Studio）**、**本地模型（Ollama）**、**区域化模型（DeepSeek / SiliconFlow）**。**同一租户内不同 Agent 可以跑不同模型**（便宜模型跑低优先分析、贵模型跑合规报表）。官方给的量化参考是 2025 年 Zia 处理 **275M+ tokens**、全平台 LLM 合计 **325M+ tokens**、GenAI 调用 **15 万+ 次**、Zia 预测 **15M+ 次**。

> **对自研的启示**：**「用哪家模型」不应该是产品的一次性架构决策，而应该是客户可配置的运行时参数。** 与商用大模型 API 对接时，建议把模型抽象成一层可切换的 provider，并把「按 Agent / 按任务用不同模型」做成能力——这既降低单点依赖风险，也让价格敏感型客户能自己压成本。

## 规律 5：本地版永远是「二等公民」，这是双形态交付的固有代价

官方承认云端先上新功能、本地版跟进：ServiceDesk Plus 的 Ask Zia 先上云（2025-09），本地版到 v15200（2025-12）才有；Gartner Peer Insights 的差评直接点名「**on-prem 落后于 cloud 更新**」。而且本地版升级常伴随破坏性变更（Web RDP 停止支持 Windows 工作站、JRE 11→17、MSSQL 兼容级别抬升、PostgreSQL 9.4 不再兼容），客户侧反馈点名「BitLocker 策略与远程控制连接在版本间失效」。

> **对自研的启示**：若我方同时提供本地部署与云端形态，**必须提前规划「能力对齐的时间差」与「升级的破坏性半径」**。中国客户里本地部署占比高，**「本地版 AI 能力是否与云版一致」会成为选型时的必答题**，而不是加分项。

## 规律 6：它的短板清单比优势清单更有决策价值

**结构性缺口（2023–2026 持续存在）**：① **OpManager 缺配置的自动备份**（客户侧点名，对审计与恢复准备构成障碍）；② **无内置 on-call 排班与事件时间线产品**（靠 ilert / PagerDuty / TOPdesk 集成）；③ **Applications Manager 无 SaaS 形态**（SaaS 侧只有 Site24x7）；④ **AI 准确率自评仅 60%–70%**（PeerSpot 用户），且官方客户案例中客户仍希望更多场景支持自适应；⑤ **安全记录是它自己最大的准入门槛**（CISA KEV 目录中有 9 个 ManageEngine / Zoho 漏洞）。

> **对自研的启示**：**竞品的短板比优势更值得投入。** 我方在**设备内部可见性（原厂独占）** 与**中文场景的语义与知识库**两处有结构性位置；而**「配置自动备份要开箱即用」「AI 结论要可举证」这两条是客户已经在抱怨、且技术门槛不高的点**，属于可以正面进攻的位置。

## 附二·引述框

> **一句话规律**：ManageEngine 2023–2026 的四年，可以概括为 **「先把 AI 接进来（别人的模型）→ 再把模型换成自己的（Zia LLM）→ 最后把动作交出去（Zia Agents）」**。它的每一次跃迁都不是加功能，而是**改变 AI 与产品的关系**：从「AI 解释数据」→「AI 召回知识」→「AI 触发动作」。而它从头到尾**没有改变的一件事**是：**在设备内部可见性上，它和所有第三方厂商一样，止步于标准 MIB 线。**

---

# 附三：对自研 APM AI 助手的对标启示

> **前提**：本文的对照对象是锐捷 APM 产品的 Web 端 AI 助手（开源多 Agent 框架 + 商用大模型 API），目标是在认证（802.1X / Portal / MAC 无感知）等方向做根因分析。下表按「能否直接照搬 / 需要改造 / 应避免」分类。

| # | 启示 | 来源（本报告章节 / 功能） | 为什么重要 |
| --- | --- | --- | --- |
| 1 | **AI 的三件套顺序不能颠倒：guardrails → 审计留痕 → 动作能力**。先让 AI 只能读、并把每次工具调用完整记录，再逐工具按角色授权，最后才开放写动作 | 大功能点 1（S4 自定义 Guardrails、S7 代理可观测性、S6 按工具 / 用户 / 组 / 角色逐项授权） | 认证类场景常涉及跨团队与安全部门，**直接开放写操作会被安全团队拦下**。ManageEngine 用「逐工具授权 + 全量会话记录」换取了自主 Agent 的放行，这个顺序可直接照搬 |
| 2 | **MCP 是「平台能力外溢」的最低成本方式**。把我方取数能力封装成 MCP server，让客户已有的 Cursor / Claude Desktop / VS Code 直接调用 | 大功能点 1（S6：NetFlow Analyzer 2026-04-13、Analytics Plus 2025-08-12、Log360 Cloud 2026-05-20、SDP Cloud 2026-10） | 这让平台的边界从「我方 UI」扩展为「客户的 agent 生态」，**投入小、传播快**，且能显著降低「又要学一个新界面」的阻力 |
| 3 | **把「设备内部可见性」做成不可替代的护城河，而不是把「也能采 SNMP」当卖点** | 大功能点 2（S3 的边界分析：第三方止步 Bridge MIB / Interface MIB / Q-BRIDGE-MIB + ARP；ACL 命中、FIB 表项、TCAM、ASIC 行为**无官方采集描述**） | **这是原厂对第三方的结构性优势，且不可复制。** 第三方能做的（拓扑推断、端口定位、阈值告警、流量分析）应视为**必须对齐的基线**；我方的差异化必须落在「表项是否正确、转发行为是否符合预期、状态机是否卡住」这些**第三方永远回答不了**的问题上 |
| 4 | **「零配置」能力比「强配置」能力更容易落地**：先给开箱即用的基线（自适应阈值、异常检测、自动发现），再提供可调参数 | 大功能点 2（S2 Adaptive Thresholds / Forecast）、大功能点 3（S5 IIS 应用自动发现、Layer 2 Map 批量添加、Key Vault 自动发现）、大功能点 6（S1 DEX 客户侧反馈「自适应阈值省了很多时间」） | 客户侧普遍没有数据科学能力；**要求客户配检测规则等于把成本转嫁给客户**。认证场景可先在「认证失败率 / 认证耗时分布 / 各认证方式的成功率」上做基线 |
| 5 | **AI 结论必须带可举证的证据形态**：不是「检测到异常」，而是「哪条证据、多显著、影响面多大」 | 大功能点 5（S4 Zia Insights 给出影响面与处置建议、用户活动审查代理汇成单一摘要、Incident Workbench）；大功能点 1（S8 RCA 输出含促成因素与纠正预防措施） | 认证故障的结论要能进工单、能被审计引用。**「结论 + 证据 + 建议」的结构，比「对话式回答」更接近客户真正要的东西** |
| 6 | **模型层要做成可替换的运行时参数，而不是一次性架构决策**：支持 BYOK、本地模型与区域化模型 | 大功能点 1（S3：Zia LLM 自研 + OpenAI / Azure / DeepSeek / Ollama / SiliconFlow 多路径）、大功能点 9（S3） | 这直接决定「数据能不能不出境」与「成本能不能自己压」。**建议把模型抽象成 provider 层，并支持「按 Agent / 按任务用不同模型」** |
| 7 | **知识库（RAG）是「把老专家能力组织化」的最低成本手段，优先级高于多 Agent 编排** | 大功能点 1（S1 Ask Zia 内嵌各产品、S5 Resolution Assist 用 RAG）、大功能点 4（S1 相似事件聚类） | 认证类故障的处置知识高度依赖老专家。**先把 runbook / 历史工单 / 认证故障处置手册灌进检索，成本低、见效快**，且它是后续 Agent 编排的知识底座 |
| 8 | **AI 必须落到「动作」才算产生组织价值，但动作要有闸门**：把结论标准化成「事件 + 证据 + 建议」并支持向既有工单系统输出 | 大功能点 1（S5 Agent 编排 + Marketplace）、大功能点 2（S6 / 大功能点 5 S5 原生 SOAR 300+ 响应动作与低代码剧本） | 客户的结论进不了工单，就等于没有产生组织价值；**但 SOAR 类能力的落地程度取决于客户已购模块**——我方应优先做「能进工单」，而不是「能自动执行」 |
| 9 | **计费锚点要与客户的资产形态对齐**：设备类按设备（含全部接口 / 端口）而非按接口或指标数 | 大功能点 2（S6：一个设备许可包含该设备全部接口，无 sensor creep）、大功能点 9（S2 / S3） | 客户对「贵」的第一感知来自账单。**按接口 / 按指标计费会让客户在规模扩大时立刻质疑成本**，这与 AI 能力好坏无关 |
| 10 | **AI 准确率要诚实披露，并设计人工兜底路径** | 大功能点 1 / 2 边界（PeerSpot 用户称 OpManager AI「大约 60%–70% 准确率」；官方客户案例中客户仍希望接口利用率支持自适应） | 过度承诺会在一线被迅速证伪。**在 UI 上显式标注置信度、给出「人工复核」入口**，比宣称高准确率更能建立信任 |
| 11 | **本地部署与云端的能力对齐必须提前规划** | 大功能点 5（附二规律 5：Ask Zia 云端 2025-09、本地 2025-12；本地升级伴随破坏性变更；Gartner 差评点名 on-prem 落后） | 中国客户本地部署占比高，**「本地版 AI 能力是否与云版一致」会是选型必答题**；同时要评估升级的破坏性半径 |
| 12 | **中文语义与国产模型是可主动验证的结构性优势位** | 大功能点 1（S3 中国区 DeepSeek / SiliconFlow 接入）、大功能点 9（S3 北京 / 上海 DC、KingbaseES、UOS / 麒麟） | 中文 runbook、中文日志、中文认证报文的语义检索效果，是我方相对国际厂商的结构性位置；**应主动建立评测集验证，而不是假设可用** |

---

# 附四：待补充与后续跟踪

## 多源冲突与本报告判定

| 冲突项 | 各源口径 | 本文判定 |
| --- | --- | --- |
| **OpManager Standard 起始设备数与价格** | 官方定价页：Standard **10 设备 = $95**、25 设备 = $245；第三方多处写「Starts at $245 for 10 devices」 | **取 A 级**：$95 对应 10 设备、$245 对应 25 设备。第三方普遍把 25 设备的 $245 误标为 10 设备 |
| **OpManager Professional 档位** | 官方定价页 $145 / 10 设备；G2 显示 $345 / 10 设备 | G2 的 $345 实为 **25 设备**价，属设备档位错标；以官方为准 |
| **OpManager 免费版限制** | 第三方（inferse / itechfaqs / itechguides，2026）一致称 **3 台设备永久免费**；官方定价页未在本次抓取中直接标出 | 三方口径一致但**缺 A 级直证**，标注为「**B 级、待官方页确认**」 |
| **OpManager 可扩展设备上限** | 官方 datasheet：Enterprise「开箱 10,000 设备 / 50,000 接口」；第三方称 30,000 设备或 50,000 设备 / 100,000 接口 | **取 A 级（10,000 / 50,000）**，其余标为「未见官方佐证」 |
| **OpManager 12.8 首发时间** | 官方 EOL 页仅登记 12.7 = 2023-04-26；第三方（FileEagle）称 Free 12.8 = 2024-09-27 | 12.7 用 A 级；12.8 标注「**约 2024-09，依据 C 级条目，需 A 级复核**」 |
| **OpManager 官方 readme 排序非时间序** | OpUtils / NetFlow readme 中 12.8.x 与 12.9.x 日期交错（如 12.8.590 标 2026-03-13 晚于 12.8.635） | 官方页存在**后补条目**。引用时**以条目自带日期字段为准，不按页面顺序推断** |
| **Site24x7 免费版额度** | 官方免费监控页：**50 个网站**；同一厂商定价页 FAQ：「最多 50 个资源」；packs 对比页：**5 Websites/Servers** | **同厂三处口径不一致**。判定为 **50**（免费监控页与定价页 FAQ 同向），但「5」出现在 packs 对比表，**须以注册页实测为准** |
| **Site24x7 套餐命名** | 官方页面同时存在 FREE/STARTER/PRO/CLASSIC/ELITE/ENTERPRISE 与 Web Uptime/Web Perf/Lite/Professional 两套命名 | 属**产品页结构历史遗留**，非矛盾。**引用时必须注明具体页面** |
| **Endpoint Central / Patch Manager Plus 免费版额度** | Endpoint Central：25 端点（EULA）vs 25 台式机 + 25 移动端；Patch Manager Plus：20 计算机 + 5 服务器 vs 25 设备；Endpoint Central MSP 被第三方称「免费 250 端点 1 年」 | **以 EULA 与官方 UEMS 页为准**；MSP 250 端点口径**未获官方证实，存疑** |
| **ServiceDesk Plus 本地版定价** | 同一官网两个 pricing 页，**均标注「current as of September 2026」**，但 2 技术员 + 250 资产专业版一处 $645/年、另一处 $495/年；10 技术员 + 500 资产标准版一处 $1,545、另一处 $1,195 | **并列列出**。属官方页维护不一致，**采购前必须以报价单确认** |
| **区域定价差异** | 中文页本地版标准版 ¥108/技术员/月；台湾页云版 $10 但本地版 $120/技术员/月；德国页 Standard 10 技术员 $1,445（美元页 $1,195–$1,545） | **并列列出**，属区域定价策略，引用时须注明区域 |
| **Log360 Cloud 计费模型并存** | 存储型（Basic $120 / Standard $540 / Professional $840，官网 cloud-siem 页与订阅帮助页仍在）**与**组件型（2026-05-16 release note 官宣按日志源 / 域控 / 文件服务器 / 云账户 / 端点购买）**两个模型同时在线** | **两者都写**。2026-05-16 之后的 release notes 口径为组件型；**采购前必须确认适用哪一套** |
| **Log360 Cloud 历史价** | 2023-11-14 release note 称「专业版起价 $1,995、标准版起价 $995」；现网页为 Professional $840 / Standard $540 | 取**现价**；旧价属历史快照 |
| **Log360 日志源数量** | 官方 datasheet 称「over 750 log sources」；中文技术博客称「700+」 | 取 **750+（A 级）**，博客口径属转述 |
| **Gartner MQ for SIEM 2025 象限** | 官方徽章页自述「named in 2025 Gartner MQ for SIEM」（**未披露象限**）、2024 为 Major Player | **象限未披露**，只写「入选」；2024 位置按 Major Player 写 |
| **Gartner MQ for ITSM 2026「挑战者」** | 仅见 ManageEngine 中文站自行披露（2026-08-07），英文站未直接采到报告标题 | 标为「**厂商自述，待 Gartner 原报告核实**」 |
| **Zoho 营收时间口径混用** | FY25（截至 2025-03）营业收入 ₹12,313 亿卢比（+17.8%）；另有把 **calendar 2025 +20%** 与 FY25 +17.8% 混用；teksands 称「FY25 +21% 至 ₹13,544 亿卢比」（实为含其他收入的总收入） | **引用时必须写明财年口径**，不得把 20% 与 17.8% 当同一指标 |
| **Zoho 员工数** | 官网 19K+（2026）；Forbes 18,000（2024）；QKS 约 19,000（2026）；历史新闻稿 4,500–7,000 | 取 2026 年 **19K+**，注明口径时间 |
| **ManageEngine 产品数** | 官方 fact sheet **60+**；MAKE IN INDIA 页 **120+ 产品与免费工具**（含免费工具） | 写为「**60+ 付费产品（含免费工具则 120+）**」 |
| **R&D 投入比例** | 「超过一半营收」（PAM MQ 页）、「40% 营收」（PAM360 客户页）、「60% 营收」（第三方）**三种口径并存** | **未证实**，三种口径并列 |
| **ManageEngine 中国区客户数** | 官方文章称 5,000+ 家；全球 280,000 家 | 属**区域口径**，勿等同于全球 |
| **Zia LLM 是否已扩到 32B** | 2025-07 官方称「2025 年底先扩一波参数规模」；第三方称 **32B 未被公开确认发货** | **未证实**。2026-10 前无一手证据证明 32B 已 GA |
| **OpManager AI 量化收益** | `.cn` 官方文章称带宽预测准确率 >92%、故障率降 47%、年省云成本 280 万元 | 属**厂商自述营销内容，无第三方复核**，**不可作为竞品分析论据引用** |
| **OpManager AI 功能首发日期** | 官方 consolidated features 列表有条目但**不标日期** | 统一写「**2025（约）**」，**不编造日期** |
| **ServiceDesk Plus GenAI 版本日期** | 官方社区帖「launched on September 10」；新闻稿日期 2025-09-23 | **不矛盾，系两件事**：功能发布日 09-10、官宣日 09-23。写为「2025-09」 |
| **Zia Agents「发布」时点** | 官方 2025-02-04 公布预览、2025-07-17 正式发布、ManageEngine 侧 **2026-05-21** 全线 GA；C 级称「2026-03」 | 以 A 级为准；C 级 2026-03 系 Zoho CRM 生态口径，**不适用于 ManageEngine** |
| **AI 是否额外收费** | ManageEngine 多处称 AI「随产品许可免费、无按次计费」；Zoho 侧 Zia Agents 页面显示托管 LLM 每月免费 10M token、超出 $1–$3 / 百万 token | **面向不同主体**：ManageEngine 产品内嵌 Zia 免费；**跨产品自主 Agent 的 token 用量存在超额计费机制**。报告已分开表述 |
| **Forrester TEI 442% ROI / KuppingerCole 219% ROI** | 均为**厂商委托研究** | 标注为「**厂商委托**」，不得当作第三方独立验证 |
| **ACL 命中计数 / 路由表 / ASIC 表读取能力** | 官方文档中**均无采集描述** | **未证实**，不写入功能清单 |
| **Desktop Central → Endpoint Central 更名日期** | 多来源仅称「2023 年前后」，未采到官方更名公告 | **未获取到精确日期** |
| **Exchange Reporter Plus 窗口内功能** | 未检索到独立官方 release notes | **不写入**，避免以猜测充数 |
| **Firewall Analyzer 窗口内 A 级 release notes** | 官方页最新条目停留在 8.x 系列 | **声明缺口**；功能事实主要依赖 B 级 ITOM Newsletter |
| **Zoho 2025 全年净利润 / FY26 完整财报** | 未获取到 | **未获取到** |
| **Zoho 公司成立年份** | 官方新闻稿一处写「Founded in 2005 (Zoho)」，实为 Zoho 品牌 / Suite 起点 | 公司 **1996（AdventNet）**、Zoho 品牌 2005、更名 2009、**ManageEngine 2002** |
| **本报告大功能点总数** | 全景表列 216 条，正文分组小计与之存在 ±2 条差异（部分条目在两组间共用引用） | 以**全景表为计数口径**；共用条目在正文中按主归属计一次 |

## 待补充的信息缺口

1. **Zoho FY26（截至 2026-03）完整财报**——截至目前仅有 2025 自然年「营收 +20%」口径。
2. **OpManager / Applications Manager 的 AI 功能精确首发日期**——官方 consolidated 列表不标日期；需通过历史 release notes 快照逐版本回溯。
3. **OpManager 免费版「3 台设备」的 A 级直证**——目前仅第三方口径一致。
4. **Endpoint Central MSP「免费 250 端点 1 年」的真伪**——与其余免费额度口径严重冲突。
5. **Zia Agents 在 ManageEngine 侧的具体计费与额度边界**——官方定价页与 Zoho 侧 Agent 页口径不同，需以合同确认。
6. **Log360 Cloud 两套计费模型的正式切换时点与旧客户的迁移条款**。
7. **Applications Manager 的定价页**——本轮未采集到官方标准价目。
8. **Firewall Analyzer 2023–2026 的官方逐条 release notes**——官方页停留在 8.x。
9. **Desktop Central → Endpoint Central 更名的官方公告日期**。
10. **ManageEngine 中国区的独立营收与客户结构**——目前只有全球口径与「5,000+ 家」的模糊表述。
11. **Zia LLM 的实际效果评测**（无公开第三方基准）——「支持全部语言」等宣称缺少可核验材料。
12. **RMM Central、MDM Plus 与「监控方向」直接相关的功能级 A 级条目**——本轮未找到可引用内容，未写入。

## 后续跟踪建议

1. **Watch：Zia Agents 的采纳率与误动作率**——它是 ManageEngine 从「AI 辅助」走向「自主执行」的关键一步。若一线出现「Agent 自动执行的错误动作」，会影响整个自主 Agent 叙事的可信度。
2. **Watch：跨产品 Zia Agents 的计费模型是否收敛到 ManageEngine 产品许可内**——这决定客户对「AI 不额外收费」这句话的信任度。
3. **Watch：OpManager / Applications Manager 的 AI 功能是否补齐日期标注与第三方评测**——目前「无日期 + 无第三方验证」是这套产品 AI 叙事的最大弱点。
4. **Watch：设备侧采集是否向上突破 MIB 线**——若 ManageEngine 通过设备厂商插件（如 Cisco Meraki REST API、Cisco 的 `vlan-match prefix` 配合）逐步加深设备内部可见性，第三方与原厂之间的边界会被移动。**这是最值得持续观察的一条结构性变量。**
5. **Watch：DeepSeek / SiliconFlow 等国产模型路径在中国区的实际能力对齐度**——「接入」不等于「效果对齐」，需要实地验证中文工单与中文日志的处理质量。
6. **Watch：本地版与云版的能力代差是否收窄**——ServiceDesk Plus 本地 v15200 是一个信号，但破坏性变更的代价也在同步上升。
7. **待补：把本报告与既有《可观测性公司总览-网络与 SRE 运维方向-TOP20》做横向归一**——本文的 9 个大功能点可直接映射进「可视化三侧 / 设备侧分层」两套既有本体，补齐 ManageEngine 在矩阵中的位置（当前按附二规律 3 的判据，其定位为 **L3 管设备**，并在应用与云可观测层有覆盖，但**不满足设备侧三判据**）。


