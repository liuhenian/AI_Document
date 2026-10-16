---
title: Elastic Observability 功能体系与痛点解法（2023–2026）
company: Elastic N.V.（NYSE: ESTC，elastic.co）
category: 业界分析 / 可观测性平台与 AIOps
period: 2023-01 ~ 2026-10
created: 2026-10-14
tags:
  - 可观测性平台
  - Observability
  - AIOps
  - AgenticAI
  - ES|QL
  - 竞品分析
  - 痛点解法
---

# Elastic Observability 功能体系与痛点解法（2023–2026）

> **调研对象**：Elastic Observability —— Elastic N.V. 的可观测性解决方案，横跨日志（Logs）、指标（Metrics）、追踪（APM/Tracing）、持续剖析（Profiling）、合成监控（Synthetics）、SLO、AI Assistant 与 Serverless 交付形态。
> **调研范围**：2023-01 ~ 2026-10 公开发布的产品功能与能力增强，覆盖 Elastic Stack **8.7 → 9.5** 及 Elastic Cloud Serverless。
> **交付内容**：① 按大功能点分组、标注时间的小功能点清单（表格）；② 每个大功能点的「用户痛点 → 如何解决」详解（P/S 编号一一对应）。

## 信源与局限（先看这一段）

采用**三级信源交叉验证**：

| 等级 | 信源 | 覆盖时段 | 用途 |
| --- | --- | --- | --- |
| A | 官方 Release Notes / 官方文档（docs.elastic.co、elastic.co/guide、Kibana release notes 逐条 PR）/ 官方定价页 / SEC 文件（10-K、8-K EX-99.1） | 2023-01 ~ 2026-10 | 功能颗粒度与财务事实的主依据 |
| B | 官方博客（版本 what's new、Observability Labs、Search Labs）/ 官方新闻稿与 IR / 官方论坛（discuss.elastic.co） | 2023-01 ~ 2026-10 | 平台级发布的主题、日期与机制细节 |
| C | 第三方媒体、分析机构与评价平台（Gartner Peer Insights、G2、Better Stack、Dash0、TechTarget、CSDN/掘金等） | 2023-01 ~ 2026-10 | 客户真实体感、横评与交叉验证 |

**已知局限**：

1. **Elastic 不提供统一的"版本 GA 日期表"**。本文绝大多数功能日期取"该功能所在版本 **GA 的官方博客/文档发布日**"，与二进制实际发布日期通常相差 0–21 天；**官方 Python 客户端的发布时间不等于 Stack GA 日**，不可混用。8.11–8.15 的精确日在官方博客作者页、discuss 公告与第三方之间存在 1–3 天差异；9.1 之后的 GA 日部分依赖 C 级佐证，标注为"约"。
2. **Observability 的收入分项与 ARR 从未披露**。公司仅在季度电话会以 **ACV（年度合同价值）口径**给出混合比例（约 Observability 40%+ / Security 约 25% / Search 其余）。**这是 ACV 口径而非收入口径，报告正文一律不得当作收入引用**。
3. **功能可用性存在"版本号 — Serverless"错位**。Elastic 的 Observability release notes 已并入 Kibana release notes（颗粒度可达单 PR 级），但 9.2 之后部分条目迁移到 Serverless/versionless 文档，出现"功能已在 Serverless 可用、Stack 版本号未同步"的情况。
4. **厂商自述收益 ≠ 第三方验证**。Elastic 大量使用实验室基准与营销口径（如"存储 -65%""查询快 30x""MTTR 降低 34%"）。本文对**所有量化收益一律标注"量级参考"**，第三方验证单独标注来源。
5. **资料截止 2026-10-14**。9.5 之后的路线图（含 nightshift 由私募预览转技术预览）未发布，Q1 FY2027 实际财务结果未采集到。

**版本节奏对照表**（用于把功能对齐到时间窗）：

| 版本 | 发布窗口 | 版本 | 发布窗口 |
| --- | --- | --- | --- |
| 8.7 | 2023-04 | 8.18 / 9.0 | 2025-04-15 |
| 8.9 | 2023-08-10 | 9.1 / 8.19 | 2025-07 |
| 8.10 | 2023-09-22 | 9.2 | 2025-10-29 |
| 8.11 | 2023-11-13 | 9.3 | 2026-02 |
| 8.12 | 2024-01-19 | 9.4 | 2026-05 |
| 8.13 | 2024-03 | 9.5 | 2026-08 |
| 8.14 | 2024-06-06 | — | — |
| 8.15 | 2024-08 | — | — |
| 8.16 | 2024-11-12 | — | — |
| 8.17 | 2024-12-13 | — | — |

> **源冲突提示**：9.2 的 GA 日存在 **2025-10-29**（官方 discuss 帖与 what's new，A/B）与 **2025-11**（第三方口径）两说，本文取 2025-10-29 为主线，并标注 9.4/9.5 的精确日依赖 C 级佐证；Search AI Lake 的"发布时间"存在"架构发布 2024-05"与"商用 GA 2024-12-02"两个不同事件，本文并列处理（见大功能点 3）。

## 公司速览

| 维度 | 内容 |
| --- | --- |
| 公司 / 成立 / 总部 | Elastic N.V.，2012 年成立于荷兰阿姆斯特丹（核心项目 Elasticsearch 于 2010 年由 Shay Banon 开源）；注册总部荷兰阿姆斯特丹，美国主要运营总部旧金山湾区 |
| 上市 | 2018-10-05 于纽约证券交易所上市，代码 **ESTC** |
| 定位 | 搜索驱动的平台公司，三大解决方案：Search / **Observability** / Security；Observability 长期为**最大单一解决方案**（ACV 口径约 40%+） |
| 技术栈 | Elasticsearch（Lucene）+ Kibana + Elastic Cloud；**LogsDB / TSDB / Columnar** 专用索引模式、**ES\|QL** 管道式查询语言、**Search AI Lake** 存算分离架构、**EDOT**（OpenTelemetry 分发版）采集栈、ELSER / E5 / Jina 嵌入模型、EIS 推理服务 |
| 部署形态 | Elastic Cloud **Serverless**（按用量）/ Elastic Cloud **Hosted**（按资源）/ **Self-managed**（含 ECE / ECK） |
| 关键指标（FY2026，截至 2026-04-30） | 营收 **$1.739B（+17%）**；订阅占 94%；Elastic Cloud **$837M（+22%，占总营收 48%）**；Non-GAAP 营业利润率 **16.4%**；调整后自由现金流 $346M（20%）；Rule of 40 = 37%；**ACV>$100K 客户 1,720+**、>$1M 客户 240+；净扩张率约 112%；>50% 的财富 500 强为付费客户 |
| 融资与并购 | 已上市。窗口内收购 **Opster**（2023-11-30 完成，约 $23M，即 AutoOps 技术来源）与 **Jina AI**（2025-10-09 完成，金额未披露）。**注意：Elastic 不披露 ARR，也不披露 Observability 的收入分项** |
| 权威背书 | Gartner MQ for Observability Platforms **2026 连续第三年 Leader**（2026-07-15 发布，配套 Critical Capabilities 在 7 个用例中 3 个第一）；**2024 年首次由 Visionary 跃升 Leader**；Forrester Wave Security Analytics Q2 2025 Leader；G2 4.2/5（90 评）、Gartner Peer Insights 4.5/5（285 评） |
| 代表客户 | Oney Bank（用 Elastic 替换 5 个监控工具、年成本 -30%、MTTD 20 分钟→1 分钟）、Telefónica Germany（根因分析时间 -80%）、Oi（巴西电信）、Wells Fargo、Bank Leumi；覆盖电信、金融、制造、公共部门 |

**一句话看懂四年演进**：

> 2023–2024 **存得起**（LogsDB / TSDB 把日志与指标的存储成本打下来，补齐 SLO 与 APM 能力拼图）→ 2024–2025 **问得懂**（AI Assistant 从预览转 GA，Knowledge Base 把组织私有知识接进模型）→ 2025–2026 **做得动**（Streams / Agent Builder / Workflows / nightshift 把 AI 从"聊天助手"重构成"受治理的自动化"）。

---

## 读法：12 个大功能点全景

| # | 大功能点 | 口号 | 小功能点数 | 时间跨度 |
| --- | --- | --- | --- | --- |
| 1 | 数据采集与集成 | 采得开 | 23 | 2023-09 ~ 2026-08 |
| 2 | 存储、查询与检索引擎 | 存得起·查得动 | 34 | 2023-04 ~ 2026-08 |
| 3 | Serverless 与 Search AI Lake | 用得不设限 | 13 | 2024-05 ~ 2026-09 |
| 4 | 日志结构化与 Streams | 理得清 | 12 | 2023-09 ~ 2026-02 |
| 5 | AI Assistant 与知识库 | 问得懂 | 30 | 2023-08 ~ 2026-09 |
| 6 | 根因分析、Significant Events 与 AIOps | 找得准 | 15 | 2022-08 ~ 2026-09 |
| 7 | Agentic 自动化与 AI SRE | 做得动 | 18 | 2025-10 ~ 2026-09 |
| 8 | APM 与分布式追踪 | 追得透 | 16 | 2023-11 ~ 2026-09 |
| 9 | 统一体验、可视化与迁移 | 看得顺 | 14 | 2023-11 ~ 2026-09 |
| 10 | SLO、Synthetics 与数字体验监测 | 量得住 | 24 | 2023-05 ~ 2026-09 |
| 11 | 告警、Cases 与事件响应 | 报得通 | 12 | 2023-01 ~ 2026-09 |
| 12 | 许可、定价与商用交付 | 买得值 | 15 | 2023-01 ~ 2026-10 |

> **合计约 226 个小功能点。** 其中 **第 5 组（AI Assistant，30 条）** 与 **第 2 组（存储/查询，34 条）** 数量最多——前者说明 2023 年后 Elastic 的产品叙事重心明显向 AI 倾斜，后者说明"把成本打下来"始终是它与 Datadog/Splunk 竞争的主战场。**第 7 组（Agentic，18 条）全部集中在 2025-10 之后**，是最新且变化最快的一组。

> **读法提示**：第 1、2、3 组是"平台底座"，客户不易直接感知但决定成本与规模上限；第 4–7 组是"AI 能力线"，是 2024 年后 Elastic 差异化叙事的核心；第 8–11 组是"可观测性应用层"，与传统 APM/监控竞品正面交锋；第 12 组是"能不能买、怎么买"。

---

# 大功能点 1：数据采集与集成 —— 采得开

## 1.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 1.1 | Universal Profiling GA（持续 Profiling） | 2023-09-22（8.10） | B | 基于 eBPF 的全系统、常开、**零埋点**持续 Profiling；覆盖 PHP/Python/Java/Go/Rust/C/C++/Node.js/Ruby/Perl |
| 1.2 | Universal Profiling 与 APM 集成 | 2023-11-13（8.11） | B | 在 APM 服务视图内直接下钻到 Profiling，无需切换上下文 |
| 1.3 | Elastic Agent 支持 Kafka 输出 GA | 2024-03（8.13） | B | Agent 可将数据流式写入 Kafka |
| 1.4 | Logstash Integration Filter | 2024-03（8.13） | B | 把集成专用转换从 Elasticsearch 迁到 Logstash 执行，降低摄取链复杂度 |
| 1.5 | Logstash on ECK GA | 2024-06-05（8.14） | A/B | 在 Kubernetes 上以 ECK 方式部署/管理 Logstash 的官方路径 GA |
| 1.6 | Universal Profiling 支持 .NET | 2024-06（8.14） | B | 扩展语言运行时覆盖 |
| 1.7 | **Automatic Import 技术预览** | 2024-08（8.15） | A | 用生成式 AI 把样本数据映射到 ECS 与自定义字段，**自动生成 ingest pipeline 与集成**；官方口径"数天→数分钟"（量级参考） |
| 1.8 | Universal Profiling 原生 OTLP Profiling | 2024-08（8.15） | B | 通过 OTLP 提交 Profiling 数据 |
| 1.9 | EDOT 计划公布 | 2024-04（DevRel） | B | 官方宣布推出 Elastic 分发的 OpenTelemetry 语言 SDK + Collector |
| 1.10 | **EDOT（Elastic Distribution of OpenTelemetry）GA** | **2025-04-15（9.0 / 8.18）** | A/B | EDOT Collector + Java/.NET/Node.js/PHP/Python/iOS/Android SDK 全部 GA；保持 OTel 标准语义、**无 schema 转换** |
| 1.11 | **Automatic Import GA** | 2025-04（9.0 / 8.18） | A | 扩展至 400+/470+ 开箱集成之外的长尾自定义用例 |
| 1.12 | **Managed OTLP Endpoint（mOTLP）** | 2025（Serverless 先 GA） | B | 托管 OTLP 入口（OTel Collector + Kafka 缓冲），原生支持 traces/metrics/logs 写入 |
| 1.13 | Elasticsearch 原生 OTLP/HTTP **metrics** 端点 | 2025-10-29（9.2） | A | 直接暴露 `/_otlp/v1/metrics`，按 OTLP 元数据动态生成数据流/模板/维度；官方称吞吐最高 +60%（量级参考） |
| 1.14 | Fleet 10 万级 Agent + 470+ 集成 | 2025（OTel 路线博文） | B | Fleet 支持 10 万+ Agent 生命周期管理、分级升级与诊断包 |
| 1.15 | Elastic Agent 转向 OTel 架构 | 2025–2026 | B | 官方路线：以 OTel receiver 逐步替代 Beats receiver，最终淡化独立 Beats receiver |
| 1.16 | EDOT Cloud Forwarder（ECF） | 2025–2026 | A | Serverless 版 OTel Collector，从 AWS/GCP/Azure 采集云日志/指标直转 Elastic |
| 1.17 | mOTLP 扩展到 Elastic Cloud Hosted（GA） | 2026 | B | 仅需两个环境变量即可接入，跨越 SDK / Collector / EDOT / 自定义 forwarder |
| 1.18 | Elasticsearch 原生 OTLP/HTTP **logs / traces** 端点 | 2026-08（9.5，Preview） | A | 新增 `/_otlp/v1/logs` 与 `/_otlp/v1/traces`；**仅支持 OTLP/HTTP，不支持 gRPC** |
| 1.19 | **Prometheus remote write 端点 + 原生 PromQL GA** | 2026-08-04（9.5） | A/B | 内置 Prometheus remote write 与 Prometheus HTTP API（range/instant/metadata）；真实语料 >80% PromQL 可无修改运行（量级参考） |
| 1.20 | EDOT Collector 内嵌进 Elastic Agent | 2026-08（9.5+） | A | OTel Collector 能力内置进 Elastic Agent，不再作为独立产品 |
| 1.21 | Kubernetes「AI-ready 完整集成」 | 2026-08-04（9.5） | B | 官方称可数分钟内从零到全面监控 Kubernetes；含托管集成与 Observability MCP |
| 1.22 | Elastic Agent AWS EKS 支持增强 | 2025-04-15（9.0） | B | 面向 EKS 的部署与管理增强 |
| 1.23 | 集成数量增长（350+ → 470+） | 2024-05 ~ 2025 | B | Serverless 发布时 350+，OTel 路线博文称 470+（口径随时间增长，量级参考） |

## 1.2 它对应的用户痛点

> **口径**：本节只写**客户侧可感知的痛**（时间 / 钱 / 人 / 合规 / 组织），不写架构层问题。痛点编号 P1…Pn 与下节解法 S1…Sn 一一对应。

- **P1｜遥测来源与格式高度异构，每接一个新源就要重新做一次适配**。客户侧通常有几十到上百个数据源（多云、K8s、中间件、数据库、自研应用），每接一个新源就要有人写采集配置、解析规则与字段映射；更糟的是**排障时才发现某个源根本没接上**，或者字段口径与其他源对不上。（人 / 时间）
- **P2｜采集侧一旦绑定某家专有实现，迁移成本就成了对方的议价筹码**。厂商换 Agent、改许可、调价或停止维护某个组件，客户只能被动接受；已有的采集脚本与解析规则无法搬运。（钱 / 组织）
- **P3｜"接一个新源"的时间成本是周级的，业务侧等不起**。上线窗口与监控改造窗口对不上，新服务的普遍路径是"先上线、后监控"，事故发生时手上根本没有数据。（时间）
- **P4｜采集侧的配置能力绑在少数人身上**。Grok / 正则 / pipeline 只有少数人写得出，人一休假或离职，这条链路就没人敢改也不敢碰。（人）
- **P5｜采集代理的规模运维会失控**。成千上万台 Agent 的部署、升级、排障、版本漂移，是"不产生业务价值但必须有人做"的纯人力消耗。（人 / 时间）

## 1.3 它是如何解决的

先明确**架构约束**——它们不是客户痛点，而是由 1.2 的客户问题倒推出的设计约束，决定了"解必须长成这样"：

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| 采集层必须覆盖任意来源，且尽量不要求客户写适配代码 | P1、P3、P4 | EDOT 全组件、Automatic Import、Universal Profiling |
| 传输协议必须标准化、可替换，避免绑定单一厂商实现 | P2 | EDOT / OTel-native、mOTLP、ES 原生 OTLP 端点、Prometheus remote write |
| 接入新源不能依赖人工写解析规则 | P3、P4 | Automatic Import（AI 生成 pipeline）、470+ 开箱集成 |
| 采集代理必须可集中纳管、可自动化升级 | P5 | Fleet 集中纳管、EDOT Collector 内嵌进 Elastic Agent |
| 采集对应用必须尽量无侵入 | P3 | Universal Profiling（eBPF 零埋点）、零代码插桩 |

在上述约束下，逐条对应 P1–P5 的解法是：

- **S1｜OTel-native 采集栈 + 托管入口**（→ 解 P1、P2）。EDOT 于 2025-04-15（9.0/8.18）全线 GA，覆盖 Collector 与 7 种语言 SDK，**保持 OTel 语义约定、不做 schema 转换**——客户用的是标准 OTel 工具链，随时可以换回去。传输侧提供三层入口：**mOTLP** 托管 OTLP 入口（Serverless 先 GA，2026 扩展到 ECH）、**Elasticsearch 原生 OTLP/HTTP 端点**（metrics 于 9.2、logs/traces 于 9.5 preview）、以及官方强调的"无 vendor lock-in、所有修复回流上游 OTel"。这意味着 **P2 的锁定问题从根上被削弱**：协议是标准的，采集件是开源的，替换成本不再由厂商单方面决定。
- **S2｜Automatic Import 用 AI 生成采集管道**（→ 解 P1、P3、P4）。2024-08（8.15）技术预览 → 2025-04 GA。客户把样本数据贴进去，生成式 AI 自动完成"映射到 ECS 与自定义字段 → 生成 ingest pipeline → 生成集成"这一整条链路，官方口径"数天→数分钟"（量级参考）。它解决的是**长尾源**问题：470+ 开箱集成覆盖不了的自研/私有系统，过去必须有人写解析规则，现在由 AI 起草、人工复核即可。**P4 的能力垄断由此被打破**——写 Grok 不再是少数人的特权。
- **S3｜Fleet 集中纳管 + 采集代理架构统一**（→ 解 P5）。Fleet 支持 **10 万+ Agent** 的生命周期管理、分级升级与诊断包；**EDOT Collector 自 9.5 起内嵌进 Elastic Agent**，不再作为独立产品；Elastic Agent 逐步以 OTel receiver 替代 Beats receiver。对客户的意义是：**采集侧只需要维护一个代理面**，升级与排障从"逐台核对"变成集中下发。
- **S4｜Prometheus 生态原生兼容**（→ 解 P2）。2026-08-04（9.5）GA：Elasticsearch 内置 **Prometheus remote write 端点 + Prometheus HTTP API**（range/instant/metadata），并可用 ES|QL 的 `PROMQL` 命令直接查询。官方称基于 2000+ 公开仓库的差分测试中，真实语料 **>80% 的 PromQL 查询可无修改运行**（量级参考）。对客户的现实价值是：**存量 Prometheus/Grafana 采集与查询资产不必推倒重来**，这直接降低了"换平台"的沉没成本。
- **S5｜零埋点持续 Profiling**（→ 解 P3、P4）。Universal Profiling 2023-09 GA，基于 eBPF 实现全系统、常开、**无需插桩 / 重编译 / 符号表 / 重启**；8.11 与 APM 集成、8.14 支持 .NET、8.15 支持 OTLP Profiling。它把"要拿代码级证据就必须改应用"这一前提取消了——**上线即带证据**，无需排期改造。

> **边界**：Automatic Import 依赖生成式 AI 连接器与模型额度可用；OTLP logs/traces 端点仍为 preview 且仅支持 OTLP/HTTP（不支持 gRPC）；Enrich/字段映射的长期维护成本随集成数增长。

> **配套演进（找不到痛点归宿，单列于此）**：Beats 无官方"停更"公告，其能力被逐步并入 Agent，属**技术沿革**而非客户痛点；ECS（Elastic Common Schema）与 Profiling Agent 捐献 OTel 社区、EDOT 修复回流上游，属**生态配套**。

---

# 大功能点 2：存储、查询与检索引擎 —— 存得起·查得动

## 2.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 2.1 | TSDB / TSDS GA（时序索引模式） | 2023 上半年（8.7） | B | Time Series Data Stream 正式 GA，含 Downsampling、Synthetic _source；指标存储最高降约 70%（量级参考） |
| 2.2 | 指标侧 Synthetic _source + 索引排序 | 2023（8.7） | B | 不写原始 `_source` blob，读时由 doc_values 重建 |
| 2.3 | **ES\|QL 技术预览** | 2023-11-13（8.11） | B | 管道式语法，支持 ES\|QL 告警规则类型与 ENRICH |
| 2.4 | Data Stream Lifecycle（DSL）技术预览 | 2023-11-13（8.11） | A/B | 直接在数据流上配置保留与降采样，无需 ILM 策略 |
| 2.5 | TSDS 成为常用集成默认 | 2023-07 ~ 08（8.9） | B | Kubernetes/Nginx/System/AWS/Azure/RabbitMQ/Redis 等默认启用 TSDS；省约 70% 磁盘（量级参考） |
| 2.6 | ES\|QL in Java Client（beta） | 2024-03（8.13） | A/B | Java 客户端可直接执行 ES\|QL 并投影为域对象 |
| 2.7 | TSDB 专用 doc values 编解码器 | 2024（8.13–8.14） | B | 游程编码 + PFOR-delta + 循环序数编码；单基准中 `kubernetes.pod.name` doc values 由 110MB→7.25MB（量级参考） |
| 2.8 | **DSL GA** | 2024-06-05（8.14） | A/B | 数据流生命周期正式可用（保留 + 降采样） |
| 2.9 | **ES\|QL GA** | **2024-06-05（8.14）** | A/B | 由独立并发查询引擎驱动（不翻译为 Query DSL）；Kibana Discover 单屏完成搜索/聚合/可视化 |
| 2.10 | ES\|QL `TS` 时序源命令 | 2024-08（8.15） | A | `TS` 成为 time_series 模式索引的源命令，支持 RATE 等按序列时间维度的函数 |
| 2.11 | **LogsDB 索引模式技术预览** | 2024-08（8.15） | B | `index.mode: logsdb` 组合主机优先排序 + Synthetic _source + ZSTD + TSDB 编解码；主机优先排序可降约 40% 存储 |
| 2.12 | `best_compression` 由 DEFLATE 切 ZSTD | 2024-11-12（8.16） | A/B | 约 -12% 存储、+14% 索引吞吐（量级参考） |
| 2.13 | ES\|QL `INLINE STATS` | 2024-11-12（8.16） | A | 内联统计，保留行级数据的同时做聚合 |
| 2.14 | DSL 全局保留（global retention） | 2024-11-12（8.16） | A | 集群级 `data_streams.lifecycle.retention.default` 与 `.max` |
| 2.15 | ES\|QL `MATCH` / `QSTR` 全文检索（预览） | 2024-12-12（8.17） | A/B | 在 WHERE 中引入 Lucene match 与 query string；官方称较等价 RLIKE 快 50x–1000x（量级参考） |
| 2.16 | **LogsDB GA** | **2024-12-12（8.17）** | A/B | 日志存储**最高减少 65%**（量级参考） |
| 2.17 | `index.logsdb.route_on_sort_fields` 路由优化 | 2025-04-15（8.18） | B | 按排序字段值路由分片，额外约 20% 存储节省、1–4% 摄取损耗（量级参考） |
| 2.18 | logs-*-* 数据流默认 LogsDB | 2025-04-15（9.0） | A/B | 新建 `logs-*-*` 数据流默认 `index.mode: logsdb`（既有数据流不变） |
| 2.19 | synthetic recovery source 默认启用 | 2025-04-15（9.0） | A/B | 跳过 recovery source 写入、改动态重建（单基准写入索引体积 -39%） |
| 2.20 | ES\|QL `LOOKUP JOIN` / `CHANGE_POINT`（预览） | 2025-04-15（9.0） | B | 类 SQL LEFT OUTER JOIN 的查询时关联；变化点聚合 |
| 2.21 | **ES\|QL `LOOKUP JOIN` GA + CCS（ES\|QL）GA** | 2025-07（9.1） | B | LOOKUP JOIN 转 GA；跨集群搜索在 ES\|QL 中作为 Enterprise 功能 GA |
| 2.22 | ES\|QL `FORK` / `SAMPLE` / `COMPLETION`（预览） | 2025-07（9.1） | A/B | FORK 同输入多分支（最多 8 支）；SAMPLE 随机采样；COMPLETION 在查询内调用 LLM |
| 2.23 | ES\|QL 全文函数 GA + `MATCH_PHRASE` | 2025-07（9.1） | B | MATCH/QSTR/KQL 转 GA，新增短语匹配 |
| 2.24 | 合并/恢复大改（merge & recovery overhaul） | 2025-07（9.1） | B | 彻底移除 recovery source：写 I/O -50%、中位索引吞吐 +19%、后台合并 CPU 最高 -40%（对 8.17 基线，量级参考） |
| 2.25 | ES\|QL `FUSE`（多分支融合） | 2025-10-29（9.2） | C | 合并 FORK 分支并重算 `_score`，支持 rrf/linear 策略 |
| 2.26 | ES\|QL Smart Lookup Joins | 2025-10-29（9.2） | B | 支持多字段/表达式匹配并跨远程集群 enrich |
| 2.27 | ES\|QL 原生时序分析进 Discover | 2025-10-29（9.2） | B | RATE / `*_OVER_TIME` / TBUCKET / TS 与 lookup join 就地 enrich |
| 2.28 | `pattern_text` 字段类型（预览） | 2025-10（9.2） | B | 日志消息拆为"模板 + 变量"，模板只存一次；高重复日志 message 字段存储最高 -50%（量级参考） |
| 2.29 | **`pattern_text` GA + Failure Store 默认启用** | 2026-02（9.3） | B | `logs-*-*` 默认启用 Failure Store，失败文档落入 `::failures` 索引 |
| 2.30 | ES\|QL 逻辑视图 / 子查询 / 读时模式（预览） | 2026-02（9.3） | B | 视图作为虚拟索引、FROM 子查询组合异构 schema、查询未映射字段 |
| 2.31 | ES\|QL `timezone` GA / `LIMIT BY` | 2026-02（9.3） | B | timezone 转 GA；LIMIT BY 支持分组 Top-N |
| 2.32 | ES\|QL `RERANK` GA | 2026-05（9.4） | A/B | 对已检索行应用 inference endpoint 重排 |
| 2.33 | **Columnar 索引模式 / Columnar Logs** | 2026-08-04（9.5） | A/B | Elasticsearch 可作为原生列式数据库，`logsdb_columnar` 为首个专用 profile |
| 2.34 | **ES\|QL `PROMQL` 命令 GA** | 2026-08-04（9.5） | A/B | ES\|QL 内原生 PromQL（可与 STATS 等管道组合） |

## 2.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织）。**不要**把"压缩编码器怎么做""查询语言门槛高不高"这类架构层问题当痛点——它们是设计约束，写在本节之后的"架构约束"表里。痛点编号 P1…Pn 与解法 S1…Sn 一一对应。

- **P1｜日志与指标量的增长速度远快于预算增长速度**。合规保留期越拉越长（90 天 → 一年 → 更久），可观测数据预算却不涨；客户的现实动作是**主动少采、缩短保留期、丢掉维度**。结果是"该看的证据被自己删掉了"，可见性缺口最终反噬平台价值本身。（钱）
- **P2｜"存得起的查不动，查得动的存不起"**。客户要在两种方案里二选一：用高压缩的廉价存储，查询就慢到没法排障；用查询快的方案，账单就失控。**成本与可用性被迫对立**。（钱 / 时间）
- **P3｜日志里大量字段是重复冗余的，但客户没法在不改应用的前提下把存储降下来**。同一条模板的消息被重复存 N 遍，客户看着账单却动不了数据源头。（钱）
- **P4｜保留、降采样、滚动、合并这些生命周期动作要靠人手工写策略并持续维护**。策略写错就是丢数据或爆盘，而这件事不产生任何业务价值。（人 / 时间）
- **P5｜查询能力只属于少数专家，且沉淀不下来**。会写查询的老手是团队里唯一的知识库，他一休假，值班的人就只剩"重启和回滚"两招。（人）
- **P6｜跨数据源、跨集群、跨历史版本做关联，要么搬数据、要么人工拼，而且既有资产无法复用**。日志与指标、本地与远程集群对不上；已经沉淀的 PromQL 仪表盘与告警在换平台时等于重做一遍。（时间 / 钱 / 人）

## 2.3 它是如何解决的

先明确**架构约束**——由 2.2 的客户问题倒推出来的设计约束：

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| 压缩必须在不牺牲查询能力的前提下完成（不能只做"冷存档"） | P1、P2 | LogsDB / TSDS 专属索引模式、Synthetic _source、ZSTD、TSDB 编解码器 |
| 压缩必须对应用与查询透明（不改查询、不丢字段） | P2、P3 | Synthetic _source、pattern_text、Columnar、读时重建 |
| 生命周期必须声明式、自动化，且能在数据流维度区分 | P4 | DSL、全局保留、Downsampling、Failure Store |
| 查询语言必须能被非专家使用，且可从自然语言生成 | P5 | ES\|QL、AI Assistant 生成 / 编辑 / 可视化 ES\|QL |
| 关联与富化必须发生在查询时而非索引时 | P6 | LOOKUP JOIN、Smart Lookup Joins、子查询、schema-on-read |
| 必须能跨集群/跨项目联邦查询，且兼容既有查询生态 | P6 | CCS / CPS、原生 PromQL 与 Prometheus 兼容层 |

在上述约束下，逐条对应 P1–P6 的解法是：

- **S1｜专属索引模式（LogsDB / TSDB / Columnar）+ 读时重建 _source**（→ 解 P1、P2、P3）。这是 Elastic 把"成本"从客户账单上打下来的主体手段，分三层：**TSDS** 2023 GA、8.9 起常用集成默认启用（官方"最高 70%"，量级参考）；**LogsDB** 2024-08 技术预览 → 2024-12 GA（官方"最高 65%"，量级参考），2025-04 起 `logs-*-*` 默认启用；**Columnar** 2026-08（9.5）把 Elasticsearch 变成原生列式数据库，首个 profile 即 `logsdb_columnar`。机制是三种压缩叠加：**Synthetic _source**（不写原始 blob，读时由 doc_values 重建）、**主机优先 / 按模板排序**（提高压缩率）、**ZSTD 替代 DEFLATE**（8.16，-12% 存储 +14% 吞吐）。关键在于**查询侧完全透明**——客户不需要改任何查询或仪表板。官方两年回顾称索引体积可缩小 **50%–75%** 且吞吐与启用前持平（量级参考）。
- **S2｜pattern_text 字段类型**（→ 解 P3）。2025-10 技术预览 → 2026-02 GA。把日志消息拆成"**模板 + 变量**"，模板只存一次，官方称高重复日志的 message 字段存储**最高 -50%**（量级参考）。它针对的正是 P3 的"重复冗余"——而且是**平台侧解决，不需要客户改应用**。
- **S3｜声明式生命周期（DSL）+ 降采样 + merge/recovery 改造**（→ 解 P4、P1）。DSL 2023-11 技术预览 → 2024-06 GA，把"保留多少、什么时候降采样"从**手写 ILM 策略**变成**数据流上的属性**，rollover 与 force merge 自动执行；8.16（2024-11）新增集群级全局默认保留与强制上限（`retention.default` / `retention.max`）。同时 9.0 起 synthetic recovery source 默认启用、9.1 彻底移除 recovery source（对 8.17 基线：写 I/O -50%、中位索引吞吐 +19%、后台合并 CPU 最高 -40%，量级参考）——**让压缩不再以写入性能为代价**。
- **S4｜ES|QL 统一管道式查询语言**（→ 解 P5、P6）。2023-11 技术预览 → 2024-06 GA（8.14），由**独立并发查询引擎**驱动（不翻译为 Query DSL）。此后四年持续扩展：`TS`（8.15）、`INLINE STATS`（8.16）、`MATCH`/`QSTR` 全文检索（8.17）、`LOOKUP JOIN` + CCS GA（9.1）、`FUSE` / Smart Lookup Joins（9.2）、逻辑视图/子查询/schema-on-read（9.3）、`RERANK`（9.4）、`PROMQL`（9.5）。**一门语言同时覆盖搜索、聚合、时序与关联**，把"学一次用不到别处"的问题压缩掉一半。
- **S5｜自然语言生成与解释 ES|QL**（→ 解 P5）。AI Assistant 自 8.13 起可在对话中编辑、可视化并解释 ES|QL 查询，把"写查询"降级为"问问题"。**P5 的能力垄断由此从"专家写查询"转向"业务方描述意图"**。
- **S6｜查询时关联（LOOKUP JOIN / CCS / CPS）+ 原生 PromQL 兼容层**（→ 解 P6）。关联侧：`LOOKUP JOIN` 在查询时做类 SQL LEFT OUTER JOIN，Smart Lookup Joins（9.2）支持多字段/表达式/跨远程集群，9.3 的逻辑视图 + FROM 子查询 + 读时模式让**未映射字段也能查**——逻辑一改不必重灌数据。联邦侧：CCS 在 ES|QL 中 9.1 GA（Enterprise），Serverless 侧 CPS 2026-04 预览 → 2026-09 GA（默认支持 100 个关联项目，跨区域/云/项目类型）。生态兼容侧：9.5 GA 的 Prometheus remote write + Prometheus HTTP API + ES|QL `PROMQL` 命令，**让存量 PromQL/Grafana 资产可无修改迁移**（官方称 >80%，量级参考）。

> **边界**：
> - LogsDB 与 TSDS 的压缩收益**高度依赖数据重复度与排序字段选择**，官方 65%/70%/75% 均为特定基准的实验室数字，不宜外推为承诺；启用严格 synthetic source 时，**映射冲突或管道失败的文档可能静默丢弃**——9.3 起 `logs-*-*` 默认启用 Failure Store（落入 `::failures` 索引）是对该风险的补丁，**9.3 之前需客户自行确认**。
> - ES|QL 与 Query DSL **不是一一对应**，部分能力在 ES|QL 中仍受限；CCS 为 Enterprise 功能；CPS 仅 Serverless 可用。
> - `FORK`/`FUSE` 的起始版本存在官方博文与文档表口径冲突（见附四）。
>
> **配套演进**：可搜索快照（对象存储直查）与分层存储的组合，官方与第三方多次以"完整保真保留成为现实"描述（**属营销口径，无对应精确功能条目**，不写进 S 列表）。

---

# 大功能点 3：Serverless 与 Search AI Lake —— 用得不设限

## 3.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 3.1 | Search AI Lake + Elastic Cloud Serverless 首次发布（技术预览） | 2024-05 | B | 官方提出"业界首个 Search AI Lake"：无状态、**存算分离、索引与检索分离**、对象存储 + 低延迟查询；Serverless 同期技术预览 |
| 3.2 | **Serverless GA（AWS）** | **2024-12-02** | B（IR） | 含 Observability / Security / Elasticsearch 三类项目；引入按用量的分层定价 |
| 3.3 | VCU 计费模型与单价 | 2024-12-01 起生效 | A（定价页） | 1 VCU = 1GB RAM + 对应 vCPU/本地缓存；Ingest $0.14 / Search $0.09 / ML $0.07（per VCU-hour，as low as） |
| 3.4 | Observability Serverless 摄取 / 保留价 | 2024-12-01 起生效 | A（定价页） | Logs Essentials 摄取低至 $0.07/GB、保留低至 $0.017/GB·月；Complete 摄取低至 $0.09/GB |
| 3.5 | Serverless 定价与打包（解决方案级 + 用量计费） | 2024-12 起 | A/B | Observability/Security 按摄取量 + 保留量，Elasticsearch 按 VCU；含卷阶定价 |
| 3.6 | Serverless GA（Google Cloud） | 2025-04（Marketplace 稿 2025-04-24） | B/C | 用 Google Cloud Storage；官方路线回顾称"GCP in April 2025" |
| 3.7 | Serverless GA（Microsoft Azure，EastUS） | 2025-06-26 | B | 基于 Azure Blob Storage 的 Search AI Lake |
| 3.8 | 无状态架构技术细节披露 | 2025-06-26 | B | 持久化状态卸载到云原生对象存储；每节点 translog 缓冲合并以抑制对象存储 API 成本 |
| 3.9 | Serverless 自动扩缩（Ingest/Search/ML 三档 VCU） | 2025 | A | 各 tier 随负载自动伸缩；Search 设 baseline 保证数据即时可查，提供 Search Power 调节 |
| 3.10 | AutoOps for Serverless | 2025–2026 | A | 所有支持区域自动启用，暴露 VCU、摄取率、保留量等计费维度与项目/索引级性能指标 |
| 3.11 | Serverless 区域扩展至 18 个区域 | 2026-02（9.3） | B | AWS 侧基础设施升级，搜索延迟最高 -35%、写入吞吐 +26%（量级参考） |
| 3.12 | Serverless 跨项目搜索（CPS）技术预览 | 2026-04-16 | B | 无需移动数据即可跨关联项目查询 |
| 3.13 | **Serverless 跨项目搜索（CPS）GA** | **2026-09** | A/B | 三次点击关联、默认支持 100 个关联项目、跨区域/云/项目类型，覆盖 Observability / Security / Search / 向量库 |

## 3.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织），不写"存算是否耦合""对象存储 API 成本"这类架构问题。

- **P1｜自建 / 自管集群的容量规划与扩缩容，持续吃掉运维人力**。峰值要预留、低谷不敢退、集群版本升级要停服窗口；这些工作不产生业务价值，却必须有人做。（人 / 时间）
- **P2｜保留期与成本的对立，让客户在"留证据"和"控账单"之间二选一**。想留全量证据就得付全额热存储费，于是客户缩短保留期；等到事故复盘时，数据已经过期。（钱）
- **P3｜跨集群 / 跨区域查询的拓扑与鉴权复杂度高**。要维护证书、逐连接鉴权、配置跨集群搜索，跨团队共享数据时尤其难。（人 / 时间）
- **P4｜按节点或按 RAM 预留的计费方式与真实用量脱节，预算不可预期**。买多了浪费、买少了降级，客户无法向财务解释"下个月多少钱"。（钱）
- **P5｜功能与套餐强绑定，客户只想用一项能力却必须整档升级**。日志分析与 APM/SLO/机器学习被绑在不同价位里，"只想多要一点"就等于"多付一档"。（钱）

## 3.3 它是如何解决的

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| 计算与存储必须解耦，容量随用量自动伸缩 | P1、P4 | Search AI Lake 无状态架构、三档 VCU 自动扩缩 |
| 冷数据必须能以低成本对象存储承载，且保持可搜索 | P2 | Search AI Lake 对象存储层、低成本保留价 |
| 查询联邦必须抽象掉部署拓扑与逐连接鉴权 | P3 | CPS（跨项目搜索） |
| 计费单位必须与真实用量对齐，且可被观测 | P4 | 按 GB / 按 VCU 计费、AutoOps for Serverless |
| 套餐分层必须让客户按"证据价值"选择，而非按功能被卡 | P2、P4 | Logs Essentials / Observability Complete 两级 |

- **S1｜Search AI Lake 无状态架构**（→ 解 P1、P2）。2024-05 技术预览发布 → **2024-12-02 随 Serverless 在 AWS 商用 GA**（GCP 2025-04、Azure 2025-06-26）。计算与存储解耦、索引与检索解耦，持久化状态卸载到云原生对象存储；为抑制对象存储 API 成本，官方采用每节点 translog 缓冲合并等工程手段。对客户的直接意义是**保留成本被压到对象存储量级**：Search AI Lake Retention 低至 **$0.047/GB·月**。**P2 的对立因此被解开**——客户可以在成本可接受的条件下延长保留期。
- **S2｜按用量计费 + 自动扩缩**（→ 解 P4）。Observability Serverless 按 **GB 摄取 + GB·月 保留**计费；Elasticsearch Serverless 按 **VCU** 计费（Ingest $0.14 / Search $0.09 / ML $0.07 per VCU·hr）；Ingest / Search / ML 三档 VCU **随负载自动伸缩**，Search 设 baseline 保证数据即时可查。客户不再需要"提前猜容量"。
- **S3｜CPS 跨项目搜索**（→ 解 P3）。2026-04-16 技术预览 → **2026-09 GA**：三次点击完成项目关联、默认支持 100 个关联项目、跨区域/跨云/跨项目类型。它把部署拓扑、证书与逐连接鉴权**抽象掉**，跨团队共享数据不再需要运维介入。
- **S4｜AutoOps for Serverless**（→ 解 P1、P4）。所有支持区域自动启用，把 **VCU 用量、摄取率、保留量**等计费维度与项目/索引级性能指标放在同一视图里。对客户的意义是"**账单能解释**"——用量、成本、性能三者在同一处可见，避免月末才发现超支。
- **S5｜Observability Serverless 两级套餐**（→ 解 P2、P4）。**Logs Essentials**（$0.07/GB 采集 + $0.017/GB·月 保留）与 **Observability Complete**（$0.09/GB logs/traces、$0.023/GB metrics 采集 + $0.019 / $0.005 保留）；Egress 每月 50GB 免费、之后 $0.05/GB；指标保存于 TSDS 的新定价自 2026-07-01 生效。客户按"证据价值"选档，而不是被功能名单卡住。

> **边界**：
> - 官方营销页反复出现的"**无限保留 / 全保真保留（full-fidelity retention）**"**属营销口径，无对应精确功能条目**，不应作为已交付能力的承诺。
> - **升级单向不可逆**（Logs Essentials → Complete 后不能回退），选档需谨慎。
> - CPS 按 **$0.0023/GB·月（保留）+ $0.05/GB（传输）**另行计费（2026-09-16 生效）。
> - Search AI Lake 的"发布时间"存在两个不同事件：**架构发布 2024-05** 与 **商用 GA 2024-12-02**；任务背景提示的"2025-04 发布 Search AI Lake"未找到对应官方博文，应是 GCP 上线或对外传播节奏，列为待核实。
>
> **配套演进**：Google Cloud Partner of the Year 2026（Marketplace – Data Management & AI）；三云 Marketplace 上架并支持合并计费与 ECU 预购。

---

# 大功能点 4：日志结构化与 Streams —— 理得清

## 4.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 4.1 | Log Pattern Analysis UX 重做 | 2023-09（8.10）/ 8.15 再优化 | A | 8.10 加入字段适用性校验；8.15 在 Discover 内重做用户流，一键发现 message 字段模式 |
| 4.2 | Logs Explorer → Discover 融合 | 2024-12-13（8.17） | B | 官方宣布把 Discover 打造为日志分析唯一入口 |
| 4.3 | Log Rate Analysis 自然语言洞察 | 2024-08（8.15） | A | 以自然语言给出日志率变化/阈值告警的根因 |
| 4.4 | **Streams GA**（AI 驱动的日志解析 / 分区 / 富化 / 保留 / 数据质量） | **2025-10-29（9.2）** | A | 自动解析原始日志、用有意义字段富化、识别 Significant Events；支持"已索引数据"与"直投原始日志"两种模式 |
| 4.5 | **AI 驱动分区（AI-driven Partitioning）** | 2025-10（9.2） | A | 父 stream 日志自动切到子 stream（如 `logs.otel.firewall` / `logs.otel.application`），子继承父的 mapping/lifecycle/processor；"Suggest partitions with AI"需生成式连接器 |
| 4.6 | **AI 驱动解析（Suggest a pipeline，自动生成 Grok 规则）** | 2025-10（9.2） | A | AI 检测日志格式并生成完整 processor pipeline，"无需写一条 Grok 表达式" |
| 4.7 | Wired streams 父子继承 | 2025-10 起（9.2+） | A | 分区仅在 wired streams 上可用；子 stream 独立配置 retention/processing/mapping，父级变更自动级联；官方建议"数十个分区而非数百个" |
| 4.8 | Streams Retention Management（含 failure store） | 2025-10（9.2） | B | Data lifecycle 标签管理保留期，查看摄取量与 tier 分布 |
| 4.9 | Streams Data Quality（Good / Degraded / Poor） | 2025-10（9.2） | A | 主页面 Data quality 列按健康度过滤；failure store 捕获并暴露失败文档 |
| 4.10 | Logs Streams 直投 `/logs` 端点（预览） | 2025-10（9.2） | B | 任意 forwarder（OTel Collector、Fluentd、Fluent Bit）直投 `/logs`，AI 自动分区与解析，无需部署 Agent |
| 4.11 | Streams 与 ML 解耦 | 2025-10 起（9.2+） | A | 官方明确"不需要 ML 节点，Streams 的 AI 特性走生成式 AI 连接器" |
| 4.12 | Streams 从 message 字段"一键解析"（agentic workflow） | 2026-02（9.3） | A | 点击一次即从 log document 的 message 字段解析日志（tech preview） |

## 4.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织），不写"日志格式杂乱"这一架构层表述本身，而是写它给客户带来的可感知后果。

- **P1｜日志"进得来、用不起来"**。原始文本堆在索引里，没有字段就没法过滤、聚合、告警，排障只能全文瞎搜；数据在库里，但等于没有。（时间）
- **P2｜解析规则只有少数人写得出，而且一改格式就断**。日志格式一变（升级、改配置、换框架），pipeline 就废，只有原作者知道怎么修。（人 / 时间）
- **P3｜日志里大量是低价值噪声，却被同价存储、同价告警**。没有"哪条流重要"的区分，真信号被噪声淹没，值班人只能靠经验挑。（钱 / 时间）
- **P4｜数据质量不可见，丢数要等出问题才发现**。映射冲突或管道失败的文档静默丢失，等到需要在事故复盘里引用时，才知道"数据早就不全了"，此时已无法补证。（合规 / 时间）
- **P5｜想用 AI 自动解析日志，却被告知要额外购买 ML 能力**。"省人力"的收益被新增的采购成本吃掉，财务上算不过来。（钱）

## 4.3 它是如何解决的

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| 日志必须在入库路径上被自动结构化，不依赖人写规则 | P1、P2 | AI 驱动解析（Suggest a pipeline）、AI 驱动分区 |
| 结构化后的流必须能被独立配置保留 / 降采样 / 丢弃 | P3 | Wired streams 父子继承、Retention Management |
| 失败文档必须可见、可回捞 | P4 | Data Quality 视图、Failure Store（9.3 起默认） |
| 结构化能力不能额外要求客户买 ML 容量 | P2、P3 | Streams 与 ML 解耦（走生成式连接器） |

- **S1｜Streams 的 AI 驱动分区与解析**（→ 解 P1、P2）。2025-10-29（9.2）**GA**。AI 检测日志格式并生成完整 processor pipeline，"**无需写一条 Grok 表达式**"；"Suggest partitions with AI" 把父 stream 自动切到子 stream（如 `logs.otel.firewall` / `logs.otel.application`），子流继承父级 mapping/lifecycle/processor。9.3（2026-02）起进一步用 agentic workflow 支持从 message 字段"**点击一次**"完成解析。**P2 的能力垄断由此被取消**——解析从"某个人会写 Grok"变成"平台自动起草、人工确认"。
- **S2｜Wired streams 父子继承与逐流生命周期**（→ 解 P3）。分区仅在 wired streams 上可用；子 stream **独立配置 retention / processing / mapping**，父级变更自动级联；官方建议"**数十个分区而非数百个**"。客户由此可以按证据价值给不同流设不同保留与丢弃策略，而不是让所有日志同价同命。
- **S3｜Streams Data Quality + Failure Store**（→ 解 P4）。主页面 Data quality 列按 **Good / Degraded / Poor** 过滤；failure store 捕获并暴露失败文档；**9.3 起 `logs-*-*` 默认启用 Failure Store**，失败文档落入专用 `::failures` 索引。**静默丢数变成可见告警**——这正是合规场景最在意的一点：能证明"数据没丢"，而不是等审计时才发现缺口。
- **S4｜直投 `/logs` 端点 + OTel 用法**（→ 解 P1）。2025-10 技术预览：任意 forwarder（OTel Collector、Fluentd、Fluent Bit）可直投 `/logs`，AI 自动分区与解析，**无需部署 Elastic Agent**。对已有采集栈的客户而言，接入门槛从"改造采集"降到"改一个 exporter 地址"。
- **S5｜与 ML 解耦**（→ 解 P2、P3）。官方明确："**不需要 ML 节点，Streams 的 AI 特性使用生成式 AI 连接器**"。客户不必为 AI 日志处理单独购买 ML 容量，AI 能力与 ML 许可解耦。

> **边界**：Streams 的 AI 解析与分区依赖生成式连接器与模型额度的可用性；官方"团队平均减少 20%–40% 日志量"为量级参考；**过度分区会反噬**（官方建议控制在数十级），分区越多继承与检索开销越大。
>
> **配套演进**：Log Rate Analysis 与 Log Pattern Analysis 在 Discover 内的体验重做（8.15）属体验整合，与 Streams 的结构化主线互补。

---

# 大功能点 5：AI Assistant 与知识库 —— 问得懂

## 5.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 5.1 | **AI Assistant 首次技术预览**（log message / APM errors / log alerts / host processes / profiling 五类用例） | 2023-08（8.9） | A | 初始仅支持 **OpenAI / Azure OpenAI**，需在 `kibana.yml` 配置；log alerts 用例因 ML 许可限制未在 8.9 提供 |
| 5.2 | AI Assistant 对话式 Chat（function calling 检索/分析/可视化） | 2023-11（8.10） | B | 支持 `get_apm_timeseries`、`get_apm_service_summary`、`get_apm_error_documents`、`get_apm_correlations` 等 APM 专用 function |
| 5.3 | **AI Assistant GA** | 2024-01-19（8.12） | A | 从 Tech Preview 升级为 GA（Enterprise 客户） |
| 5.4 | **Knowledge Base（知识库）+ RAG** | 2024-01-19（8.12） | A | 把 runbook / GitHub issue / 内部文档 / Slack 消息写入 ES 索引，用 ELSER 语义检索做 RAG；KB 从 ELSER v1 迁移到 **ELSER v2** |
| 5.5 | Knowledge Base Settings 页面（UI 管理） | 2024-01-19（8.12） | A | 支持单条新增 / 文件批量导入 / 编辑删除；可用 Elasticsearch Connectors（GitHub/Confluence/ServiceNow 等）灌入应用文档 |
| 5.6 | KB 每次 prompt 都检索 + LLM 相关性打分降噪 | 2024-01-19（8.12） | A | 8.12 前仅在会话首个 prompt 注入；改为每次 user prompt 注入，且先做 relevance 打分以降低 token 用量 |
| 5.7 | AI Assistant Amazon Bedrock 支持 GA | 2024-03（8.13） | A | 面向 Anthropic Claude 模型；8.14 支持 Claude 3 |
| 5.8 | AI Assistant 编辑与可视化 ES\|QL 查询（预览） | 2024-03（8.13） | A | 可在对话中编辑/渲染 ES\|QL 结果并用 Lens 继续编辑、保存到 Dashboard |
| 5.9 | context-based starter prompts GA | 2024-06（8.14） | A | 按应用与数据上下文给出起始提示；Alert Details 页面加入 contextual insights |
| 5.10 | AI Assistant API 交互（experimental API） | 2024-06（8.14） | A | 可通过 API 编程式与 Assistant 交互、定义指令与客户端动作 |
| 5.11 | AI Assistant Google Vertex / Gemini 连接器 GA | 2024-08（8.15） | A | 推荐 Gemini 1.5 Pro（大上下文窗口） |
| 5.12 | 自定义索引作为 KB | 2024-08（8.15） | A | 任意 ELSER 向量化索引可被检索，不再限定 Elastic 管理连接器索引 |
| 5.13 | 自定义知识源 + 会话中 "remember this" | 2024-11-12（8.16） | B | 可加入 text/markdown 条目或 semantic_text 索引；对话中"记住"内容成为后续知识源 |
| 5.14 | KB 改用 `semantic_text` 字段类型 | 2025-01（8.17） | A | 引入架构；**同时引入已知缺陷**：空 text 的 KB 文档致 Kibana OOM（#220339，见边界） |
| 5.15 | AI Assistant 原生 function calling 默认启用 | 2025-04（8.18） | A | `Defaults to "native" function calling (#210455)`；改进 tool choice 处理（#203928） |
| 5.16 | 可从设置页安装 KB | 2025-04（8.18） | A | `Adds ability to install a Knowledge Base from the AI Assistant settings (#206408)` |
| 5.17 | AI Assistant 内嵌进 Discover 日志详情 flyout | 2025-04（8.18 / 9.0） | A | 在 Discover 日志详情中直接给 AI highlights |
| 5.18 | KB 模型可选 ELSER / E5（非英语）+ KB on EIS | 2025-07（8.19） | A | `Allows users to specify a Knowledge Base model to support non-English languages (#218448)`；E5 自 Stack 9.1+ |
| 5.19 | 会话归档 / 分享 / 导出 | 2025-07（8.19） | A | `archive conversations (#216012)`、`share AI Assistant conversations (#211854)` |
| 5.20 | **隐名化（Anonymization）高级设置** | 2025-07（8.19） | A | 规则化掩盖 PII（如 `EMAIL_ee4587…`）后再离开 Kibana 送往第三方 LLM；默认全部规则关闭 |
| 5.21 | **Elastic Inference Service（EIS）发布** | 2025（9.2 语境） | A | GPU 加速、多 CSP、多 region、多模态的推理即服务；提供 embedding / reranking / LLM / SLM；**无冷启动、免自管 ML 节点**；官方称 GPU 推理下摄取吞吐最高 10x（量级参考） |
| 5.22 | ELSER on EIS（首个 EIS 文本嵌入模型，预览） | 2025-10（9.2） | A | ELSER 成为 EIS 上第一个文本嵌入模型 |
| 5.23 | **Elastic Managed LLM（默认托管 LLM，免自带 Key）** | 2025–2026 | A | EIS 默认提供，驱动 Agent Builder / AI Assistant / Attack Discovery / Automatic Import / Playground；**使用会产生额外费用** |
| 5.24 | GenAI 设置页（统一开关 + 连接器可见性） | 2025-10（9.2+） | A | 可管理哪些 AI 连接器可用、启用/禁用 AI Assistant 及其他 AI 功能、指定在哪些 solution 出现 |
| 5.25 | LLM 性能矩阵（Observability） | 2025–2026（9.x） | A | 官方按模型 × 用例给性能参考，把"用哪个模型"从经验变为可查表格 |
| 5.26 | EIS 支持 Jina 三模型 GA | 2026-02（9.3） | A | jina-embeddings-v3、jina-reranker-v2-base-multilingual、jina-reranker-v3；**今后所有新 Jina 模型经 EIS 提供** |
| 5.27 | EIS 经 Cloud Connect 支持自管集群 GA | 2026-02（9.3） | A | 自管集群可把推理卸载到 Elastic Cloud 托管 GPU，数据/存储/索引留在本地（含气隙/受监管场景） |
| 5.28 | AI Assistant 支持本地 LLM（LM Studio） | 2025–2026（9.x / Serverless） | A | 文档新增"Connect to a custom local LLM"；**早期（8.16 之前）官方明确"不支持私有 LLM"，属能力反转** |
| 5.29 | AI Assistant 嵌入式 contextual insights | 2023-08 起持续 | A | 覆盖 Universal Profiling / APM / Infra / Logs / Alerting 五处上下文提示 |
| 5.30 | AI Assistant 告警工作流连接器 | 2024 起 | A | 告警触发时把上下文发给 Assistant 生成报告/召回 KB/给修复建议，并可经 Slack/email/Jira/PagerDuty/webhook 外发 |

## 5.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织），不写"模型上下文窗口多大""RAG 检索精度"这类架构问题。

- **P1｜能力绑在少数专家身上，知识散落在个人和文档里**。只有少数人知道"这个错误码意味着什么、上次怎么修的"；这些知识留在老手脑子里、陈旧的 Confluence 页面、Slack 历史与 GitHub issue 里，新人只能靠问人。（人）
- **P2｜排障时的上下文切换成本极高**。要在 APM、日志、指标、Profiling、告警、Confluence、Slack 之间来回跳，每次跳转都要重新建立上下文；时间不是花在分析上，而是花在"把信息拼起来"。（时间）
- **P3｜数据不能随便送去第三方 LLM，安全团队不放行**。日志与 trace 里可能含 PII 与客户数据，直接送第三方模型在合规上过不去，AI 能力往往卡在安全评审而不是技术上。（合规）
- **P4｜"用哪个模型、谁来付钱、数据去哪里"这些问题，被推给客户自己做工程决策**。自购 API Key、跨区域数据合规、不同模型效果不可预期，客户要为供应商的选择承担成本与风险。（钱 / 组织）
- **P5｜AI 给出的结论无法沉淀到团队与工单里**。会话留在个人浏览器，结论不能被分享、不能被审计、不能进 Jira/Case，等于没产生组织价值。（组织 / 合规）

## 5.3 它是如何解决的

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| 组织私有知识必须能进入模型上下文，且可更新可管理 | P1、P2 | Knowledge Base + RAG、Elasticsearch Connectors 灌入、KB Settings 页 |
| AI 必须在用户已有界面内原地工作，而非另开聊天窗 | P2 | embedded contextual insights、starter prompts、Discover 内嵌、告警详情页集成 |
| 敏感数据出厂前必须可脱敏；模型不得用客户数据训练 | P3 | Anonymization（8.19）、官方"不使用客户数据训练模型"声明、本地 LLM 支持 |
| 模型接入必须可切换、可托管，避免客户自建推理 | P4 | 多连接器路线（OpenAI/Azure/Bedrock/Gemini）、EIS、Elastic Managed LLM、Cloud Connect |
| 会话与结论必须可归档、可分享、可外发 | P5 | 会话归档/分享/导出（8.19）、AI Assistant 告警连接器 |

- **S1｜Knowledge Base + RAG**（→ 解 P1、P2）。8.12（2024-01）随 AI Assistant GA 一同提供：把 **runbook、GitHub issue、内部文档、Slack 消息**写入 Elasticsearch 索引，通过 **Elasticsearch Connectors**（GitHub/Confluence/ServiceNow 等）批量灌入，用 **ELSER 语义检索**做 RAG；KB 提供 UI 管理（单条新增 / 文件批量导入 / 编辑删除）。8.12 起**每次 user prompt 都检索**，并先让 LLM 对文档做相关性打分以降 token；8.15 支持任意 ELSER 向量化索引、8.16 支持 text/markdown 条目与对话中"remember this"、8.18 可从设置页一键安装。**P1 的知识垄断由此被打破**——老手的经验从"个人记忆"变成"平台可检索的知识源"。
- **S2｜嵌入各应用的上下文提示与对话**（→ 解 P2）。embedded contextual insights 覆盖 **Universal Profiling / APM / Infra / Logs / Alerting 五处**；8.14 GA context-based starter prompts（按当前应用与数据给出问法）；8.18/9.0 把 AI Assistant **内嵌到 Discover 日志详情 flyout**；9.1 在告警详情页增加 View in Discover、Add to case 与调查指南。**AI 出现在排障者已经在的地方**，而不是要求他再开一个窗口。
- **S3｜隐名化与数据治理声明**（→ 解 P3）。8.19 引入 **Anonymization 高级设置**：用规则把 PII 掩盖成 `EMAIL_ee4587…` 之类的占位符后，数据才离开 Kibana 送往第三方 LLM（默认全部规则关闭，由客户自行开启）；官方明确声明"**Elastic 不使用客户数据训练模型**"。同时提供从"早期明确不支持私有 LLM"到"9.x 支持本地 LLM（LM Studio）"的路径——**受监管客户可以把模型完全留在本地**。
- **S4｜托管推理（EIS + Elastic Managed LLM）与多连接器**（→ 解 P4）。连接器路线清晰：8.9 OpenAI/Azure → 8.13 Bedrock（Claude）→ 8.15 Gemini/Vertex → 8.16 本地模型 → **9.2 EIS + Elastic Managed LLM（默认托管、免自带 API Key）** → 9.3 Jina 三模型 GA + EIS 经 Cloud Connect 支持自管集群。官方还发布 **LLM performance matrix**，按模型 × 用例给出性能参考——**把"选哪个模型"从客户的试错变成厂商给出的对照表**。
- **S5｜会话归档、分享与告警工作流连接器**（→ 解 P5）。8.19 支持会话**归档 / 分享 / 导出**；**AI Assistant connector** 在告警触发时把上下文发给 Assistant 生成报告、召回 KB、给出修复建议，并可经 **Slack / email / Jira / PagerDuty / webhook** 外发。结论由此进入工单系统，可留痕、可交接、可审计。

> **边界**：
> - **许可门**：官方 8.9/8.10 口径为"仅 Enterprise 许可可用"，后续文档改为"an appropriate Elastic subscription"（无硬版本号）。第三方测评称"Platinum 起含 Full AI Assistant"属**整理推断**，需以官方 pricing 页复核（见附四冲突表）。
> - **成本门**：KB 需 **4GB ML 节点**；Cloud/ECE 若开启 ML autoscaling，使用 KB 与 AI Assistant 会**启动 ML 节点并产生额外成本**。**Elastic Managed LLM 为付费 add-on**（$4.50 / 百万输入 token、$21 / 百万输出 token）。
> - **两个已确认缺陷**：8.17 引入 `semantic_text` 后，**空 text 的 KB 文档会引发无限更新 → Kibana OOM**（#220339/#220342）；**9.0.0–9.0.2 的 `execute_connector` 死循环**（tool call 参数解析缺陷，9.0.3+ 修复）。做能力评估时须列为版本风险。
> - **能力反转**：官方文档从"明确不支持私有 LLM"变为"Connect to a custom local LLM"，报告中必须以"早期不支持 → 后期支持"表述，**不可取单一口径**。
>
> **配套演进**：token limit / function call limit 的额度限制属**计费与配额机制**，不构成客户痛点，单列于此。

---

# 大功能点 6：根因分析、Significant Events 与 AIOps —— 找得准

## 6.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 6.1 | Explain log rate spikes（技术预览） | 2022-08（8.4） | B | Log Rate Analysis 前身 |
| 6.2 | Log rate dips（日志率下降分析，预览） | 2023-09（8.10） | A | 从"只分析 spike"扩展到"也分析 dip"；此版起更名 **log rate analysis** |
| 6.3 | Change Point Detection 图表可挂到 Dashboard / Cases（预览） | 2023-09（8.10） | A | Machine Learning > AIOps Labs > Change Point Detection |
| 6.4 | Log Pattern Analysis UX 重做 | 2023-09（8.10） | A | 加入字段适用性校验 |
| 6.5 | Data Comparison view（数据漂移检测，预览） | 2023-09（8.10） | A | 选 reference/comparison 时间范围比较数值与分类字段的显著变化（给 p 值） |
| 6.6 | Anomaly Detection（零配置 ML） | 2020 起持续 | A | 自动对主机/K8s pod 的内存、网络等做异常检测；异常显示在基础设施地图 |
| 6.7 | **Log Rate Analysis GA** | 2024-01-19（8.12） | B | 基于 significant terms 的 p_value 打分 + frequent_item_sets + random_sampler 聚合 |
| 6.8 | Log Rate Analysis 的 AI Assistant 集成 | 2024-01-19（8.12） | B | 在 threshold alert 详情页自动执行分析，结果作为 pre-built prompt 上下文送给 LLM |
| 6.9 | Log Rate Analysis 自然语言洞察（Serverless） | 2024-08（8.15） | A | 以自然语言给出日志率变化/阈值告警的根因 |
| 6.10 | Log Rate Analysis 可加入 Cases | 2025-04（8.18） | A | `Adds action to add log rate analysis to a case (#201549)` |
| 6.11 | **Significant Events（技术预览）** | 2025-10-29（9.2） | B | 基于 agentic AI 自动标记 startup/shutdown、OOM、internal server failure、证书过期等信号，在 Kibana 中表现为可点击 **marker**，作为调查起点 |
| 6.12 | Significant Events 随 Streams 一并发布 | 2025-10-29（9.2） | A | 9.2 版本亮点中列为 Observability 主推能力（与 Streams 并列 GA 叙事；文档状态仍为 tech preview） |
| 6.13 | 对话式 RCA（Streams 流程内给根因） | 2025-10（9.2） | B | 官方演示：Java OOM → AI Assistant 判定"Spark 内存不足"→ 给出精确根因；厂商自述"数小时→数分钟"（量级参考） |
| 6.14 | APM 异常列（Anomalies column）替代 Health 列 | 2026（9.5+） | A | `Replaces the Health column with an Anomalies column … surfacing ML anomaly detection data directly in the service list (#266194)` |
| 6.15 | AI 驱动告警分类 + 告警内联依赖分析 | 2026（9.5 约） | A | 独立 alert analysis workflow 把告警分类为 true/false positive；在 alert 详情页/仪表板直接呈现 service map |

## 6.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织），不写"告警规则怎么写""统计成因分析的算法"这类技术问题。

- **P1｜告警多而杂，"哪个是真问题"要靠人判断，而且没有共享证据**。跨团队协作时各方看的是各自屏幕上的不同数字，讨论变成扯皮，责任难以划分。（组织 / 时间）
- **P2｜根因定位慢，从"指标异常"到"哪台机器、哪个服务、哪个版本"要人工一层层下钻**。MTTR 被拉长，直接对应到营收损失与 SLA 罚金。（时间 / 钱）
- **P3｜传统异常检测的配置成本高**：要么手写阈值（误报淹人、且阈值随业务漂移失效），要么训练 ML 作业（需要数据科学能力，客户没有）。（人 / 时间）
- **P4｜事后没有可回溯的证据链**。告警与工单之间没有记录"当时判断是为什么"，复盘时讲不清，也拿不出审计需要的举证材料。（合规 / 组织）
- **P5｜分析结论与告警是两套东西，得人工把结论搬回告警系统，而且告警本身不分真假**。做完根因分析还要手工转述；值班者无法分辨哪些告警已经可判定为噪声。（时间 / 组织）

## 6.3 它是如何解决的

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| 根因必须由平台给出**可解释的统计证据**，而非只给"异常"标记 | P1、P4 | Log Rate Analysis、Change Point Detection、Data Comparison、Significant Events |
| 检测必须零配置、开箱即用 | P3 | 零配置 ML 异常检测、K8s 预配置 ML 作业、Significant Events 零配置检测 |
| 检测结果必须自动落到"可行动的事件流 / 工单" | P2、P4 | Significant Events marker、Log Rate Analysis 入 Case、AI 驱动告警分类 |
| 根因必须能跨 signals 验证（logs/metrics/traces/profiles） | P2 | 对话式 RCA、nightshift 并行假设验证（见大功能点 7） |

- **S1｜Log Rate Analysis / Change Point Detection / Data Comparison**（→ 解 P1、P2）。**Log Rate Analysis** 2024-01（8.12）GA：基于 significant terms 的 **p_value 打分** + frequent_item_sets + random_sampler 聚合，能定位"**是哪个服务、哪个地区、哪个用户群**"导致日志率变化；8.15 在 Serverless Observability 提供**自然语言洞察**；8.18 可一键加入 Case。**Change Point Detection**（8.10）与 **Data Comparison**（8.10）分别提供变化点与数据漂移的显著性判定。这些能力输出的是**带统计显著性的归因**，而不是"某个数字超了阈值"。
- **S2｜Significant Events**（→ 解 P1、P2、P4）。2025-10-29（9.2）技术预览，随 Streams 推出。基于 agentic AI **自动标记**"值得关注的信号"：startup/shutdown 消息、OOM、internal server failure、证书过期等，在 Kibana 中表现为**可点击的 marker**，作为调查起点；支持 AI 推荐监控查询。**平台先替客户圈出"哪些证据值得看"**——这直接对应 P1 的"哪个是真问题"。
- **S3｜对话式 RCA**（→ 解 P2）。AI Assistant 在 Streams 流程内给出根因判定（官方演示：Streams 识别 Java OOM → AI Assistant 判定"Spark 内存不足" → 给出精确根因），厂商自述"数小时→数分钟"（量级参考）。**从"看数据"到"听结论"**的第一步。
- **S4｜零配置 ML 异常检测**（→ 解 P3）。主机/K8s 内存与网络异常检测**零配置**（7.10 起），异常直接显示在基础设施地图；9.5 起 APM Service Inventory 用 **Anomalies 列**直接呈现 ML 异常检测数据；K8s 监测 GA 版随附 **100+ 预配置 ML 作业**与告警、SLO。**客户不需要数据科学家，也不需要调阈值**——开箱即有基线。
- **S5｜告警内联证据与 AI 分类**（→ 解 P1、P4）。9.5 在 **alert 详情页与自定义仪表板直接呈现 service map**（dependency analysis），减少上下文切换；独立的 **alert analysis workflow** 把告警分类为 true / false positive；ML 异常检测告警与 Stack 告警统一显示在 Observability Alerts 页（#269718）。**告警自带证据，且被预先筛过一遍**。

> **边界**：
> - **Significant Events 的官方状态为 tech preview**，但 9.2 版本亮点博客把它与 Streams 并列作为 GA 叙事——**写报告时必须注明"GA 叙事 ≠ GA 状态"**，两者都要体现。
> - AIOps 的自然语言洞察与 Significant Events 的 AI 推荐查询依赖生成式连接器可用性。
> - 厂商自述的 MTTR 改善（"数小时→数分钟"）为**量级参考**，未见第三方复现。
>
> **配套演进**：Log Rate Analysis 由 8.4 的 "explain log rate spikes" 演进而来、APM correlations（7.12→7.15 GA）的 significant terms 归因属**技术沿革**，不单独作为解法列出。

---

# 大功能点 7：Agentic 自动化与 AI SRE —— 做得动

## 7.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 7.1 | **Elastic Agent Builder 技术预览** | 2025-10-29（9.2） | B | Kibana 内建对话式 agent；可建自定义 tool（ES\|QL / 语义检索）、自定义 agent、内置可视化、全链路 agent tracing；支持 API / MCP / A2A |
| 7.2 | Agent Builder API（tools / agents / converse） | 2025-10（9.2） | A | `POST kbn://api/agent_builder/tools`、`/agents`、`/converse`；部分特性 tech preview 且有 feature flag |
| 7.3 | **Elastic Agent Builder GA** | 2026-02（9.3） | A | 与 Elastic Workflows 打通，让 agent 能"可靠地采取行动" |
| 7.4 | **Elastic MCP Server**（Agent Builder 内置） | 2026-02 起（9.2+ / Serverless） | B | 原生暴露 MCP server（`{KIBANA_URL}/api/agent_builder/mcp`），可接入 Cursor / VS Code / Claude Desktop；用 Elastic API Key 鉴权，工具按用户权限执行 |
| 7.5 | 独立 MCP server（`mcp-server-elasticsearch`）状态 | 2025 首版 / v0.4.x | C | **v0.4.x 起标记 deprecated（仅关键安全更新）**，官方后继为 Agent Builder MCP endpoint |
| 7.6 | Elastic MCP Server 上架 Microsoft Foundry Tool Catalog | 2025（Ignite 2025 前后） | C | 作为 remote MCP server 上架，支持 RAG / 多 agent（A2A）场景 |
| 7.7 | **Elastic Workflows 技术预览** | 2026-02（9.3） | A | 原生编排层，可由规则/告警/agent 触发；支持基于规则与 agentic 自动化 |
| 7.8 | **Elastic Workflows GA** | 2026-05（9.4） | A | 脚本化自动化 + agentic reasoning 合并；对 Security 客户原生自动化 triage/enrichment/response/case |
| 7.9 | Agent Builder 新增原语：Skills / Attachments / Connectors / Plugins | 2026-05（9.4） | A | 控制 agent 如何收集/使用/基于上下文行动；含 query result offloading、compaction、summarization 等上下文管理 |
| 7.10 | Agent Skills（可观测性开源技能包） | 2026-05（9.4） | A | 5 个核心工作流：OTel 应用插桩、搜索日志、管理 SLO、评估服务健康、监控 LLM 应用 |
| 7.11 | Observability MCP App（K8s 调查，预览） | 2026-05（9.4） | B | 提供 6 个视图（cluster health rollup、service dependency graph、anomaly details、observe、blast radius、alert management），在内联 React UI 中渲染；支持 Claude / Cursor |
| 7.12 | Agentic 驱动 Kubernetes 可观测性 | 2026-05（9.4） | A | Kibana 内告警触发，工程师打开仪表板前就返回"含证据与后续步骤"的结构化根因假设 |
| 7.13 | MCP server 工具调用可被 OTel 追踪 | 2026（9.3+） | B | 用 EDOT Node.js 给 MCP server 加 OTel tracing，再通过 Agent Builder MCP 从 Claude Desktop 反查 trace（"agent 用自身遥测自我分析"） |
| 7.14 | A2A Protocol 支持（Agent Builder ↔ Gemini Enterprise） | 2025–2026（9.2+） | B | MCP 用于"带工具"，A2A 用于"agent 对 agent" |
| 7.15 | Agent Builder 扩展：Agent Observability & Monitoring + human-in-the-loop 审批 | 2026-08（9.5 约） | A | Agent Observability 以 OTel 追踪 LLM 调用/工具调用/推理步骤；human-in-the-loop 审批门控敏感动作并留审计 |
| 7.16 | Elastic Workflows 自然语言编写 GA + 版本化 | 2026-08（9.5 约） | A | 自然语言描述即生成自动化（默认开启）；内置版本管理与回滚 |
| 7.17 | Observability 默认聊天体验切换为 AI Agent | 2026-08（9.5 约） | A | `Adds AI Agent as the default Observability chat experience (#260570)`；加入 `observability.investigation` 调查技能与 Service Map 技能 |
| 7.18 | **Elastic nightshift AI SRE（私募预览）** | 约 2026 | B | 内置 Observability 的 AI SRE agent；四大引擎 **Context / Detection / Investigation / Remediation**；零配置检测 + 并行假设验证 RCA + 透明推理链；Serverless 私募预览期免费 |

## 7.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织），不写"agent 框架怎么设计""工具调用怎么实现"这类技术问题。

- **P1｜"看见了"不等于"修好了"**。平台能发现异常，但修复动作仍靠人执行；从"知道问题在哪"到"问题被解决"之间的等待时间，就是停机时间。（时间 / 钱）
- **P2｜自动化脚本与 runbook 难以复用、难以治理**。写好的 runbook 只是文档，跑起来靠人；谁在什么时候执行了什么改动，没有统一记录。（组织 / 合规）
- **P3｜AI 能力被锁在厂商自己的聊天窗里**。客户已经在用 Cursor、Claude Desktop、VS Code 等工具，却无法让它们访问平台里的可观测数据。（人 / 组织）
- **P4｜让 AI 直接改生产环境，安全团队不放行**。缺少审批门与审计链，自动执行的收益无法兑现。（合规 / 组织）
- **P5｜夜间与非工作时段是响应能力的真空**。值守人力有限，多数事故恰恰在无人时段被延长；而"没有告警触发的事故"更是完全没有入口。（人 / 时间）

## 7.3 它是如何解决的

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| 必须能把"调查结论"接上"可执行动作" | P1 | Agent Builder + Workflows 打通、Agent Actions |
| 自动化必须可版本化、可审计、可复用 | P2 | Workflows 版本管理与回滚、Agent Skills 打包 |
| 平台能力必须能作为标准工具暴露给外部 agent | P3 | Elastic MCP Server、A2A |
| 敏感动作必须有人工审批门与审计链 | P4 | human-in-the-loop 审批、Agent Observability（OTel tracing） |
| agent 必须能自主持续运行并覆盖无告警场景 | P5 | nightshift AI SRE（零配置检测 + 持续巡查） |

- **S1｜Elastic Agent Builder**（→ 解 P1、P3）。2025-10-29（9.2）技术预览 → **2026-02（9.3）GA**。在 Kibana 内建对话式 agent：可建**自定义 tool**（ES|QL / 语义检索）、自定义 agent、内置可视化与**全链路 agent tracing**；提供 API（`/tools`、`/agents`、`/converse`）；9.4 新增 **Skills / Attachments / Connectors / Plugins** 原语与上下文管理（query result offloading、compaction、summarization）；9.5 起可从 chat 直接创建 skill/query/workflow，并把 Observability 的**默认聊天体验切换为 AI Agent**。**P1 的关键在于它把"查"和"做"放在同一个 agent 框架里**——调查结论可以直接触发工作流。
- **S2｜Elastic Workflows**（→ 解 P2）。2026-02（9.3）技术预览 → **2026-05（9.4）GA**。原生编排层，可由**规则 / 告警 / agent** 触发，把脚本化自动化与 agentic reasoning 合并；9.5 支持**自然语言编写**（默认开启）并内置**版本管理与回滚**。**runbook 从"文档"变成"可版本化的可执行资产"**，这正是 P2 的解法。
- **S3｜Elastic MCP Server / A2A**（→ 解 P3）。Agent Builder **原生暴露 MCP server**（`{KIBANA_URL}/api/agent_builder/mcp`），可接入 **Cursor / VS Code / Claude Desktop**，工具**按用户权限执行**；支持 **A2A** 与 Google Gemini Enterprise 等 agent 互操作；已上架 **Microsoft Foundry Tool Catalog**。9.5 与 Agent Skills 一起，把健康监测、异常检测、事件调查、修复能力开放给"**任何支持 MCP 的 AI 工具**"。**平台的边界从"厂商自己的 UI"扩展为"客户的 agent 生态"**。
- **S4｜Human-in-the-loop 审批门与审计**（→ 解 P4）。9.5 Agent Builder 新增 **human-in-the-loop 审批门**：敏感动作必须经人工批准，并可"每步复核"或"自动执行"；**Agent Observability** 以 OTel 追踪 LLM 调用、工具调用与推理步骤。**自动执行的风险被审批门与追踪双向约束**——这通常是安全团队放行的前提。
- **S5｜Elastic nightshift AI SRE**（→ 解 P5）。私募预览（Serverless，期间免费）。内置 Observability 的 AI SRE agent，四大引擎 **Context / Detection / Investigation / Remediation**：持续评估遥测（**无需写告警规则**），并行对 logs/metrics/traces/profiles **验证假设**，输出"证据 + 建议修复"，可 review 后再自动执行；Remediation Engine 复用现有 workflow / connector 并自动填参，计划支持 Slack 集成与第三方遥测存储。官方引用 NeuBird（2026-04）数据"**78% 的组织至少经历过一次没有任何告警触发的事故**"——这正是 P5 中"无入口事故"的直接论据。

> **边界**：
> - Agent Builder 部分特性带 **feature flag** 且为 tech preview；**nightshift 为私募预览，尚未 GA**，不应作为已交付能力承诺。
> - 独立开源 `mcp-server-elasticsearch` 自 **v0.4.x 起 deprecated**（仅关键安全更新），官方后继为 Agent Builder MCP endpoint——**报告不得把两者混为一谈**。
> - MCP/A2A 的能力受**用户权限**约束，跨权限边界的调查仍需人工介入。
>
> **配套演进**：Workflows 与 Agent Builder 按次计费（10,000 次免费，之后低至 $0.0108 / $0.025 每次，2026-05-01 生效）属**定价机制**；Agent Skills 打包 5 个可观测性工作流供外部 AI 编码 agent 使用属**生态配套**。

---

# 大功能点 8：APM 与分布式追踪 —— 追得透

## 8.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 8.1 | APM Attacher for Kubernetes GA | 2024-01-19（8.12） | A | 通过 webhook receiver + 用户注解，无需改源码/配置即可自动注入 Java 与 Node.js APM Agent |
| 8.2 | Mobile APM（iOS / Android）GA | 2024-01-19（8.12） | A | 含服务依赖、端到端 trace 瀑布、按应用版本/OS/设备/地理的性能分析、错误与崩溃分析 |
| 8.3 | Universal Profiling 与 APM 集成 | 2023-11-13（8.11） | B | 在 APM 服务视图内把性能问题关联到底层系统函数（含内核/第三方库） |
| 8.4 | 部署标注（Deployment Annotations / Markers） | 8.x 持续能力 | A | 交易图上叠加部署标注；默认在 `service.version` 变化时自动生成，也可经 annotation API 由 CI/CD 推送 |
| 8.5 | Tail-based sampling 存储层重写（Pebble 替代 BadgerDB） | 2025-04-15（9.0） | A | 吞吐提升、内存与磁盘占用下降（#15235）；9.3/9.4 继续分页化以约束内存 |
| 8.6 | Tail-based sampling 配置 TTL 与 discard-on-write | 2025-07（9.1） | A | 新增 `apm-server.sampling.tail.ttl`、`discard_on_write_failure`（#13950 / #16579） |
| 8.7 | **Direct tracing to Elasticsearch via EDOT Collector（绕过 APM Server）** | 2024-11-12（8.16） | B | 官方明确"EDOT Collector eliminates the need for an APM server"，trace 经 ES exporter 直写 |
| 8.8 | **EDOT（Collector + 7 语言 SDK）全线 GA** | 2025-04-15（9.0 / 8.18） | B | 保留 OTel 语义约定与 resource attributes，官方提供企业级支持 |
| 8.9 | 官方承认的 OTel 集成局限 | docs 持续 | A | 见边界（6 条） |
| 8.10 | APM Server 生命周期终止（EOL）政策 | 9.x EOM 2027-10-15 | A | APM Server 9.x 维护期至 2027-10-15（或 10.0 GA 后 18 个月）；8.x 至 2027-01-15 |
| 8.11 | APM Service Map 前端重建（Canvas → React DOM） | 2025–2026 | B | 官方称 500 服务规模下"6x faster"（量级参考） |
| 8.12 | Service Map 增强（嵌入式面板 / 全屏 / RED 边指标 / 迷你地图 / 节点浮出） | 9.4–9.5（2026） | A | 服务图可作为 Dashboard 面板嵌入并支持 KQL；连接边显示 RED；节点浮出预览 RED/异常/SLO 状态 |
| 8.13 | Service Inventory / Service Map 隐藏非 trace 服务 | 9.1.7–9.2.1 | A | 过滤掉非 trace 来源的"服务"，减少噪音（#241080/#240104） |
| 8.14 | APM 渐进式加载（progressive loading） | 9.1+（2025-07） | A | `observability:apmProgressiveLoading`：先低采样快速返回，再后台加载全量 |
| 8.15 | APM Server 状态自检上报 | 9.4（2026-06 约） | A | Report APM Server status on major health issues（#20166） |
| 8.16 | APM 高级 UI 设置移除（向统一形态收敛） | 9.1（2025-07） | A | Trace Explorer / Agent Explorer / Service Metrics 等高级设置被 Removed |

## 8.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织），不写"采样器存什么数据结构""Agent 与 SDK 的语义差异"这类技术问题。

- **P1｜分布式系统的故障跨服务、跨语言，缺少端到端证据**。慢在哪一跳、是应用问题还是基础设施问题，只能靠猜；相邻服务的团队互相推责，因为没有共享的调用链证据。（时间 / 组织）
- **P2｜采样策略两难：全采样成本高，头部采样丢关键证据**。按请求开头决定采不采，等发现这条 trace 重要时已经来不及补；客户被迫在成本与证据完整性之间二选一。（钱 / 时间）
- **P3｜插桩改造要动应用代码，团队排期难**。新服务"先上线、后监控"是普遍路径；改造窗口遥遥无期，故障发生时没有追踪数据。（人 / 时间）
- **P4｜专有 Agent 造成锁定：语言覆盖率不全、Agent 版本与应用版本耦合**。要升级 Agent 往往得连带升级应用或依赖库，团队被迫接受。（钱 / 组织）
- **P5｜服务规模一上来，追踪视图本身就卡**。几百上千个服务、百万级 trace 时，拓扑渲染与查询响应退化，"能看"变成"等它转圈"，排障窗口被页面加载吃掉。（时间）

## 8.3 它是如何解决的

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| 追踪必须覆盖多语言/多运行时，且对应用侵入最小 | P3、P4 | EDOT 7 语言 SDK、APM Attacher、OTel Operator 零代码插桩 |
| 采样决策必须能基于完整 trace 内容而非只看开头 | P2 | Tail-based sampling（Pebble 重写、TTL、discard-on-write） |
| 追踪语义必须标准化，可与其他 OTel 生态互通 | P4 | EDOT / OTel-native、无 schema 转换、ECS 捐献 OTel |
| 拓扑与依赖必须可视化到"一眼看出影响面" | P1 | Service Map 重构、RED 边指标、Service Inventory |

- **S1｜EDOT / OTel-native 全组件**（→ 解 P3、P4）。**EDOT Collector + Java/.NET/Node.js/PHP/Python/iOS/Android SDK** 于 2025-04-15（9.0/8.18）全线 GA，保持 OTel 语义约定与 resource attributes、**不做 schema 转换**，官方提供企业级支持。更关键的是 **8.16（2024-11）官方明确"EDOT Collector 可完全替代 APM Server"**——trace 可经 Elasticsearch exporter 直写。**客户因此可以使用标准 OTel 工具链，避免被专有 Agent 锁定**，这直接对应 P4。
- **S2｜Tail-based sampling 重写**（→ 解 P2）。9.0 用 **Pebble 替代 BadgerDB** 承载尾采样缓冲（吞吐提升、内存与磁盘占用下降，更稳定）；9.1 新增 `ttl` 与 `discard_on_write_failure` 配置；9.3/9.4 继续分页化以约束内存。**采样决策基于完整 trace 的内容**，因此可以在"低流量但高价值（如错误、慢请求）"的 trace 上保留全量，普通流量降采样——**P2 的两难由此被解开**。
- **S3｜Service Map / Service Inventory 重构**（→ 解 P1）。Service Map 前端由 Canvas 重建为 React DOM（官方称 500 服务规模下快 6x，量级参考）；9.4–9.5 增强为可**嵌入 Dashboard 面板**（含 KQL 过滤）、连接边显示 **RED（rate / errors / duration）**并可一键跳 Discover Traces、节点浮出预览 RED/异常/SLO 状态、含告警与 SLO 徽章与迷你地图；Service Inventory 过滤掉非 trace 来源的"服务"以减少噪音。**影响面从"要人拼"变成"一眼可见"**——这是 P1 的共享证据来源。
- **S4｜APM Attacher 与零代码插桩**（→ 解 P3）。8.12（2024-01）**APM Attacher for Kubernetes GA**：通过 webhook + 注解自动注入 Java/Node.js Agent，**无需改源码**；8.16 经 OpenTelemetry Operator 自动部署配置 OTel Collector，含**零代码插桩**。**新服务上线即带证据**，不必等改造窗口。
- **S5｜统一 APM 体验与渐进式加载**（→ 解 P1）。9.1 起 APM 渐进式加载（先以低采样率快速返回、再后台加载全量），提升大集群 APM 视图响应；同期多项 APM 高级 UI 设置（Trace Explorer / Agent Explorer / Service Metrics）被移除，**APM 应用层向统一形态收敛**；部署标注在 `service.version` 变化时自动生成，把"版本变更"与"性能拐点"绑定在同一时间轴上。

> **边界**：
> - **APM Server 非立即废弃**：官方 EOL 页将 9.x 维护期定到 **2027-10-15**、8.x 到 2027-01-15。报告中须区分"技术路线（向 OTel intake / EDOT 迁移）"与"产品支持承诺"。
> - 官方**已承认的 OTel 集成的六项局限**（A 级文档）：① OTel 消息语义的 trace 可能被误显示为 transaction；② span 无法看堆栈；③ OTLP 日志摄入为 technical preview；④ 用 OTel Collector 的 `tailsamplingprocessor` 做尾采样时，**派生吞吐/计数指标会不准确**（建议改用 Elastic Agent 原生尾采样）；⑤ 旧 `elastic` exporter 已废弃，改用 `otlp` exporter；⑥ **EDOT SDK 仅支持 Elastic Agent Gateway 或托管 OTel intake，不支持直连 APM Server 的 OTel intake**。
>
> **配套演进**：APM 专有 Agent → OTel 采集的路线变化属**技术沿革**；Mobile APM（8.12 GA）为能力补齐。

---

# 大功能点 9：统一体验、可视化与迁移 —— 看得顺

## 9.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 9.1 | Lens 内联编辑 / 颜色映射 / 跨仪表板链接面板 | 2023-11-13（8.11） | B | 仪表板编辑体验的基础增强 |
| 9.2 | SLO Overview / SLO Alerts 仪表板面板 | 2024-01-19（8.12） | A | SLO 数据以 Dashboard 面板提供，可直接在面板上配置告警或创建 Case |
| 9.3 | Discover 上下文感知 / 自适应展示 | 2024-11-12（8.16） | A | 按内容类型自动调整数据表呈现；`log.level` 按严重度高亮，`service.name` 直链跳转 APM UI |
| 9.4 | Discover 自定义视图 + 摘要列（GA） | 2024-11-12（8.16） | B | 提供可定制数据视图与"摘要列"，便于一览式、上下文日志探索 |
| 9.5 | **Logs Explorer → Discover 融合** | 2024-12-13（8.17） | B | 官方宣布把 Discover 打造为日志分析唯一入口 |
| 9.6 | Discover 自定义格式化与图表格式化 | 2025-04-15（8.18 / 9.0） | A | ES\|QL 图表自定义格式化与单元格复制等（#201540/#204744） |
| 9.7 | APM trace 瀑布图可添加到其他解决方案 | 2025-07（9.1） | A | `Allows users to add the APM trace waterfall to other solutions (#216098)` |
| 9.8 | **Discover 指标体验（ES\|QL TS + METRICS_INFO）** | 2025-10-29（9.2） | B | 在 Discover 中运行 `TS metrics-*`，自动生成每个指标的面板；counter 用 `SUM(RATE())`、gauge 用 `AVG`、histogram 用百分位；支持按维度拆分与"加入仪表盘" |
| 9.9 | Discover 支持 ES\|QL 时序命令与就地富化 | 2025-07 ~ 10（9.1–9.2） | B | RATE / `*_OVER_TIME` / TBUCKET / TS 与 LOOKUP JOIN 就地 enrich 嵌入 Discover |
| 9.10 | Observability 导航菜单更新 | 2025-10（9.2） | A | 更新导航菜单（#233784/#236808），配合应用整合 |
| 9.11 | **Dashboard 自动迁移（从 Splunk，预览）** | 2025-10（9.2） | B | Automatic Migration for Dashboards 帮助把自定义仪表盘从 Splunk 迁移到 Elastic |
| 9.12 | Service Map 作为 Dashboard 可嵌入面板 | 2026（9.4–9.5） | A | 含 KQL 过滤、交互浮出、Copy to dashboard、最大化视图（#261195/#272277/#274551） |
| 9.13 | **Grafana / Datadog 仪表盘与告警迁移工具 GA** | 2026-08（9.5 约） | B | 可把 Grafana 与 Datadog 的仪表盘、告警自动引入 Elastic |
| 9.14 | 代码化仪表板 + 聊天中生成仪表板 | 2026-08（9.5 约） | B | 结合 code-based dashboards 与"聊天中生成仪表盘"，统一指标/日志/trace 并建立关联 |

## 9.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织）。**注意**："两种查询语言不互通""可视化配置复杂"本身是设计约束，不写进本节的痛点。

- **P1｜日志、指标、追踪各有一套界面与查询方式，跨信号排障要人在多屏间对齐（工具墙）**。同一个事故要在三个地方各自翻一遍，时间花在对齐上而不是分析上；跨团队协作时各方看到的是不同界面里的不同画面。（时间 / 组织）
- **P2｜仪表板只能由少数人维护，业务侧改不动**。自定义视图要写查询或写代码，业务方想加一个面板得排队等工程团队。（人）
- **P3｜换平台的沉没成本高，既有仪表盘与告警是资产**。已经沉淀在 Splunk / Grafana / Datadog 的仪表盘与告警规则，重建一遍等于重做一次项目，是"换不换"决策里最硬的一块成本。（钱 / 时间）
- **P4｜指标与日志/trace 割裂，看到指标异常时不知道对应哪条日志或哪个 trace**。反之亦然，关联全靠人脑记忆与手工搜索。（时间）
- **P5｜应用入口分散、导航层级深，功能找不着**。同一个能力散在多个应用里，新人要记住"哪个功能在哪个菜单"，上手成本高。（人 / 时间）

## 9.3 它是如何解决的

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| 同一份数据必须能被日志 / 指标 / 追踪三种视角在同一界面查看 | P1、P4 | Discover 统一入口、Discover 指标体验、APM 瀑布图跨解决方案复用 |
| 可视化必须支持非专家直接使用（对话 / 拖拽） | P2 | Lens、SLO 面板、code-based dashboards、聊天中生成仪表盘 |
| 必须提供从竞品的资产搬迁路径 | P3 | Splunk / Grafana / Datadog 迁移工具 |
| 拓扑与依赖视图必须能在任意界面内复用 | P1、P4 | Service Map 作为可嵌入面板 |

- **S1｜Discover 作为统一数据探索入口**（→ 解 P1、P4）。8.17（2024-12）**Logs Explorer 并入 Discover**；8.16 起 Discover **上下文感知**（按内容类型自适应用户视图、`log.level` 按严重度高亮、`service.name` 直链 APM UI）；**9.2 起 Discover 原生指标体验**——一条 `TS metrics-* | METRICS_INFO` 即枚举指标并自动选聚合方式（counter 用 `SUM(RATE())`、gauge 用 `AVG`、histogram 取百分位），支持按时序命令与 LOOKUP JOIN 就地富化。**日志、指标、追踪在同一处被查看**，工具墙被拆掉一层。
- **S2｜Lens / 仪表板 / 代码化仪表板**（→ 解 P2）。Lens 支持仪表板内联编辑、颜色映射、跨仪表板链接面板（8.11）；**SLO 数据以 SLO Overview / SLO Alerts 面板提供**，可在面板上直接配置告警或创建 Case（8.12）；9.5 把 **code-based dashboards 与"聊天中生成仪表盘"**结合，业务方可以用自然语言描述想要的视图。
- **S3｜竞品资产迁移工具**（→ 解 P3）。9.2 推出 **Automatic Migration for Dashboards（从 Splunk，技术预览）**；9.5 新增 **Grafana / Datadog 仪表盘与告警迁移工具 GA**。这是对 P3 这种"换平台最硬成本"的直接回应——**把迁移从"重新做一遍"降为"跑一次工具再复核"**。
- **S4｜跨解决方案的可视化复用**（→ 解 P1、P4）。9.1 起 **APM trace 瀑布图可添加到其他解决方案**；9.4–9.5 **Service Map 可作为 Dashboard 面板嵌入**（含 KQL 过滤、交互浮出、Copy to dashboard、最大化视图）。**同一张拓扑图可以在任意仪表板里出现**，跨团队共享同一份证据。
- **S5｜导航与信息架构整合**（→ 解 P1、P4）。9.2 更新 Observability 导航菜单（#233784/#236808），配合 APM / SLO / Synthetics 在统一壳内收敛；9.1 移除部分 APM 高级 UI 设置，把能力归并到统一形态而非保留独立入口。

> **边界**：Discover 指标体验与部分可视化能力在 Serverless 与 Hosted 的可用时间点不同；迁移工具是"**迁移**"而非"等价替换"，脚本逻辑与面板语义仍需人工复核。
>
> **配套演进**：可视化与仪表板的多数改动属**体验演进**（持续打磨而非解决新痛点），本组解法只保留能指回 P1–P4 的部分。

---

# 大功能点 10：SLO、Synthetics 与数字体验监测 —— 量得住

## 10.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 10.1 | SLO 技术预览 | 2023-11-13（8.11） | A | SLO 能力的 Beta 起点 |
| 10.2 | **SLO GA** | 2024-01-19（8.12） | A | 对 Platinum / Enterprise 正式可用；Beta 定义需迁移为新格式 |
| 10.3 | SLO 燃尽率"预算消耗模式" | 2024-01-19（8.12） | A | 燃尽率窗口可按"已消耗预算"定义，并与 burn rate 模式切换 |
| 10.4 | Time Slice SLI（统计聚合型 SLI） | 2024-01-19（8.12） | A | 支持 avg/max/min/sum/std_deviation/last_value/percentile/doc_count 及自定义方程与阈值 |
| 10.5 | SLO 分组与过滤 + 燃尽率告警 triage 页 | 2024-03（8.13） | A | 按 tag、SLI 类型、状态分组；新增燃尽率告警 triage 页 |
| 10.6 | **Federated SLOs（基于 CCS）** | 2024-06-06（8.14） | A | 本地集群定义 SLO，在单一只读集群经跨集群搜索统一查看 |
| 10.7 | Grouped SLO embeddable | 2024-06-06（8.14） | A | SLO Overview 图可展示一组 SLO，按状态/标签/SLI 类型分组嵌入 Dashboard |
| 10.8 | **SLO 燃尽率告警依赖通知（根因抑制）** | 2024-06-06（8.14） | A | 对存在依赖的服务，挂起依赖方的燃尽率告警通知，只发给根因服务 |
| 10.9 | Synthetics Availability SLI | 2024-06-06（8.14） | A | 专用合成可用性 SLI，可把合成监控直接转成可用性 SLO |
| 10.10 | SLO History 标签页 + Stale / No Data 状态 | 2024-08（8.15） | A | 可回看任一时段状态；新增 Stale/No Data 便于清理失效 SLO |
| 10.11 | Find SLO API 游标分页 | 2025-04-15（9.0 / 8.18） | A | `Introduces cursor pagination in Find SLO API (#203712)` |
| 10.12 | SLO Definition 标签页 / 单页管理 / 日历型 SLO History | 2025-07（9.1） | A | 单页内查看定义、删除 SLO、清除 SLI 数据（#222238/#212826/#223825） |
| 10.13 | **Synthetic Monitoring GA** | 2023-05（8.8） | A | Synthetics app / Project monitors / 全局托管测试基础设施 / 私有位置 四项均在 8.8.0 起 GA |
| 10.14 | GitOps 化合成监控（Playwright / Project monitors） | 2023-05（8.8） | B | Playwright 脚本可用于 CI/CD（GitHub Actions、GitLab 等），Project monitors 以代码方式管理 |
| 10.15 | 合成监控自动重试 | 2023-11（8.11） | B | Synthetics 自动重测能力 |
| 10.16 | **Synthetics 告警增强（多条件 / 多位置 / 标签 / 多规则）** | 2024-11-12（8.16） | A | 可按监视器宕机次数、测试位置、标签设灵活条件；支持为同一监视器配置多条规则 |
| 10.17 | Synthetics 支持 MFA | 2024-11-12（8.16） | B | 可在 journey 中调用 `mfa.totp(params.MFA_TOKEN)` 完成两步验证 |
| 10.18 | **Uptime 应用弃用** | 2024-08（8.15） | A | Uptime 弃用，官方指引迁往 Synthetics；Serverless 中不可用 |
| 10.19 | Synthetics 私有位置与全局托管基础设施计费 | GA 8.8 起 | A | 私有位置以 `elastic-agent-complete` Docker 镜像交付，需直连 ES；全局托管基础设施按"浏览器每次运行 / 轻量按区域"计费 |
| 10.20 | Synthetics 跨集群搜索（CCS）远程监视器视图 | 9.x（2026） | A | 内置 CCS 集成，只读查看远程集群的 `synthetics-*` 数据（#267849 增加远程集群筛选） |
| 10.21 | Synthetics TLS 证书覆盖浏览器监视器 | 9.4–9.5（2026） | A | TLS 证书过期规则可选覆盖浏览器监视器证书（#272325）；证书页展示浏览器监视器观测到的证书 |
| 10.22 | RUM JavaScript Agent（浏览器真实用户监控） | 长期能力 | A | 采集页面浏览、加载时间、后端时间、FCP、TBT、LCP、FID、CLS 等；可"Open in Lens" |
| 10.23 | RUM 与 APM 后端 trace 关联 | 长期能力 | C | RUM agent 支持出站请求的分布式追踪，浏览器活动可并入后端 APM trace |
| 10.24 | **会话回放（Session Replay）—— 官方明确"不支持"** | 2023-03 / 2026 复核 | B/C | 官方论坛 2023-03 明确"Session playback isn't currently available with Elastic RUM"；2025-11 再次确认；第三方横评（Better Stack ×3、Dash0、middleware.io，2026）一致标注 No / Limited |

## 10.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织），不写"SLI 怎么定义""采样口径怎么算"这类技术问题。

- **P1｜"系统好不好"没有与业务挂钩的量化口径，SLA 争议没有共享证据**。可用性只有技术人员自己定，业务方不认；事后追责各说各话。（组织 / 合规）
- **P2｜用户侧体验问题在监控里看不见**。后端全绿但用户打不开页面、前端慢、某个地区的用户加载失败——等到投诉才发现。（时间 / 钱）
- **P3｜合成监控的维护成本高、误报多**。脚本随页面改版失效，单次失败就告警淹人，维护它是纯人力消耗。（人 / 时间）
- **P4｜依赖关系未建模时，上游故障导致下游 SLO 集体报警，值班人被噪音淹没**。真正该看的人反而在告警堆里找不到根因。（人 / 时间）
- **P5｜SLO 数量一多就管不动**。几十个还能手工维护，上百上千个之后没人清理失效项与重复定义，SLO 逐渐变成"没人看的摆设"，量化口径重新失效。（人 / 组织）

## 10.3 它是如何解决的

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| SLO 必须能定义在任意 SLI 上，并与告警 / 仪表板联动 | P1 | SLO GA、Time Slice SLI、燃尽率告警、SLO 面板、Find SLO API |
| 必须同时具备"后端追踪 + 合成测活 + 真实用户"三层证据 | P2 | APM、Synthetics、RUM 三层并行，且互相可关联 |
| 合成监控的脚本必须可版本化（GitOps）且可重试 / 降噪 | P3 | Project monitors + Playwright、自动重试、多条件告警 |
| 依赖关系必须以数据建模，用于告警抑制 | P4 | Federated SLOs（CCS）、燃尽率告警依赖通知 |

- **S1｜SLO**（→ 解 P1、P4）。8.11 技术预览 → **8.12（2024-01）GA**（Platinum/Enterprise）。支持 **燃尽率"预算消耗模式"与 burn rate 模式切换**、**Time Slice SLI**（avg/max/min/sum/std_deviation/last_value/percentile/doc_count 及自定义方程与阈值）；8.13 分组/过滤 + 燃尽率告警 triage 页；8.14 **Federated SLOs（基于 CCS 在单一只读集群统一查看）+ Grouped SLO embeddable**，以及**燃尽率告警依赖通知**——对存在依赖的服务，挂起依赖方通知、只发给根因服务；8.15 History 标签 + Stale/No Data 状态。**P1 的"业务方不认"由此有了统一口径**（可自定义 SLI + 面板共享），**P4 的告警噪音由依赖建模直接压制**。
- **S2｜Synthetics**（→ 解 P2、P3）。8.8（2023-05）**GA**（app / Project monitors / 全局托管测试基础设施 / 私有位置）。**Playwright 脚本可直接用于 CI/CD**（GitHub Actions、GitLab），Project monitors 以代码方式管理（**GitOps**）；8.11 自动重试；**8.16 多条件/多位置/标签/多规则告警与 MFA**（`mfa.totp()`）；9.x 支持 CCS 远程监视器视图与 TLS 证书覆盖浏览器监视器；8.15 起 Uptime 弃用，能力统一到 Synthetics。**P3 的"误报淹人"由多条件 + 自动重试 + 标签抑制共同缓解**，脚本资产由 Git 管理而非散落。
- **S3｜RUM**（→ 解 P2）。RUM JavaScript Agent 采集页面浏览 / 加载时间 / FCP / TBT / LCP / FID / CLS 等 **Core Web Vitals**，可在 User Experience → Dashboard 做 KPI / 性能分布可视化并 Open in Lens；**RUM agent 支持出站请求的分布式追踪**，浏览器活动可并入后端 APM trace。8.12 **Mobile APM（iOS/Android）GA**。**P2 的"后端全绿但用户打不开"由此有了前端与移动侧的证据**。
- **S4｜合成可用性 SLI + SLO 联动**（→ 解 P1、P2）。8.14 新增 **Synthetics Availability SLI**，可把合成监控直接转成可用性 SLO。**合成测活的结果能进入 SLO 口径**，而不是两张互不相干的报表。
- **S5｜SLO 工程化与规模化**（→ 解 P1）。9.0 Find SLO API 游标分页（#203712）、9.1 SLO Definition 标签页与单页管理、日历型 SLO History。**SLO 从"几十个能手管"走向"上千个可运维"**，这是它能在企业里被真正用起来的前提。

> **边界（明确短板）**：
> - **Elastic RUM 在 2023–2026 期间不具备会话回放（Session Replay）能力**。官方论坛 2023-03 与 2025-11 明确回复无 session playback、无独立用户会话分析；第三方横评（Better Stack《New Relic vs Elastic》《Datadog vs Elastic》《Dynatrace vs Elastic》2026、Dash0、middleware.io）一致标注 "Session replay: No / Limited"。**Elastic 的数字体验监测强在"前后端 trace 关联 + Synthetics"，弱在"会话回放与产品分析/漏斗"**，这是选型时最需要预警的一条。
> - 第三方（Dash0，2026）指出 **RUM agent 因依赖集中式 APM Server，当前不兼容 Elastic Cloud Serverless**，与官方"EDOT 直写、去 APM Server"路线存在张力，**待以官方文档核实**（见附四）。
>
> **配套演进**：Mobile APM / 移动侧 RUM 属能力补齐；全局托管测试基础设施的用量计费属定价机制。

---

# 大功能点 11：告警、Cases 与事件响应 —— 报得通

## 11.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 11.1 | Opsgenie connector GA | 2023-01（8.6） | B | Elastic 触发时自动创建/关闭 Opsgenie 告警，可精细控制告警内容 |
| 11.2 | 条件动作（conditional actions in alerting rules） | 2023-11-13（8.11） | B | 告警规则支持条件动作 |
| 11.3 | ES\|QL 告警规则类型 | 2023-11-13（8.11） | B | 新增 ES\|QL 规则类型，支持复杂告警场景，可先预览查询结果再保存 |
| 11.4 | Connectors 全清单（30+ 集成） | docs 持续 | A | PagerDuty、Opsgenie、Slack、Teams、Email、xMatters、Jira/JSM、ServiceNow ITSM/ITOM/SecOps、IBM Resilient、Swimlane、TheHive、Tines、Torq、CrowdStrike、SentinelOne、Cortex XSOAR、Microsoft Defender for Endpoint、Webhook 等 |
| 11.5 | Cases 外部连接器（工单联动） | docs 持续 | A | 可推送至 ServiceNow ITSM/SecOps、Jira（含 JSM）、IBM Resilient、Swimlane、Webhook - Case Management；支持"推送时自动关闭" |
| 11.6 | **Cases 模板 GA** | 2025-04-15（9.0 / 8.18） | A | `Case templates are now generally available (#205940)`；ServiceNow 连接器支持通过 Additional fields 发送 JSON payload（#201948） |
| 11.7 | **面向 SRE 的告警增强 GA**（分组 / 调查指南 / 恢复信息） | 2025-07（9.1） | B | 更智能的告警分组、内置 investigation guide、更丰富的恢复消息 |
| 11.8 | 告警详情页增强（View in Discover / 建议仪表盘 / Add to case） | 2025-07（9.1） | A | 为 Synthetics Monitor Status/TLS、SLO 燃尽率、ES query 等规则增加入口（#223424/#223184/#217106） |
| 11.9 | ML 异常检测告警与 Stack 告警统一显示 | 2026（9.5+） | A | `Makes ML anomaly detection alerts and Stack alerts visible on the Observability Alerts page (#269718)` |
| 11.10 | 告警详情页内联 service map（dependency analysis） | 2026-08（9.5 约） | A | 在 alert 详情页/自定义仪表板直接呈现 service map，减少上下文切换 |
| 11.11 | Alerting V2 权限（实验性） | 2026-08（9.5 约） | A | 把顶层 Alerting 权限重命名为 "Alerting V2"，子权限标记为 experimental（#288163） |
| 11.12 | 无内置 on-call 排班 / 事件时间线（第三方口径） | 2026 | C | 第三方指出 Elastic（及 Datadog）"都没有从根因假设直达 on-call 通知、事件时间线、状态页更新的路径"；on-call 依赖 xMatters / Opsgenie / PagerDuty |

## 11.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织），不写"连接器怎么写、告警规则引擎怎么实现"这类技术问题。

- **P1｜告警落到人之前没有闭环**：从告警到"谁负责、怎么处理、处理记录在哪"缺一条链路，事件时间线靠人手工记，交接时丢信息。（组织 / 合规）
- **P2｜告警通知方式与工单系统五花八门，每接一个都要单独开发集成**。已有 PagerDuty、ServiceNow、Jira、Slack 等多套系统，接入成本重复付。（人 / 时间）
- **P3｜值班者拿到的只有一行标题，上下文要自己去翻**。在多个界面之间找证据，时间花在"找"而不是"判断"上。（时间）
- **P4｜事件响应流程散落在外部工具，审计时举证困难**。谁在何时做了什么改动、依据是什么，没有统一记录。（合规）

## 11.3 它是如何解决的

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| 告警必须能驱动外部系统动作，且集成面足够宽 | P2 | 30+ 连接器、Cases 外部连接器 |
| 告警必须自带上下文与调查路径 | P1、P3 | 告警详情页增强、内联 service map、investigation guide |
| 事件处理过程必须可留痕、可审计 | P4 | Cases 模板、Alerting V2 权限模型、AI Assistant connector 外发留痕 |

- **S1｜"规则 + 连接器 + Cases"的开放集成模式**（→ 解 P1、P2）。官方连接器覆盖 **PagerDuty、Opsgenie、Slack、Teams、Email、xMatters、Jira/JSM、ServiceNow ITSM/ITOM/SecOps、IBM Resilient、Swimlane、TheHive、Tines、Torq、CrowdStrike、SentinelOne、Cortex XSOAR、Microsoft Defender for Endpoint、Webhook 等 30+**；Cases 可通过连接器推送至 ServiceNow / Jira / Resilient / Swimlane，支持"**推送时自动关闭**"；**Cases 模板 9.0 GA**。**客户已有的事件管理系统不必替换**，集成成本从"每接一个开发一次"降为"选一个连接器"。
- **S2｜告警规则能力扩展**（→ 解 P1、P3）。8.11 引入**条件动作**与 **ES|QL 告警规则类型**（可先预览查询结果再保存规则，降低写错规则的风险）；9.1 **面向 SRE 的告警增强 GA**——更智能的告警分组、内置 **investigation guide**、更丰富的恢复消息。
- **S3｜告警详情页内置证据与调查入口**（→ 解 P3）。9.1 为 Synthetics Monitor Status/TLS、SLO 燃尽率、ES query 等规则在告警详情页增加 **View in Discover**、**Add to case** 按钮、建议仪表盘链接与调查指南（#223424/#223184/#217106）；9.5 在 alert 详情页**直接呈现 service map**（dependency analysis），并统一显示 ML 异常检测告警与 Stack 告警。**值班者不再需要自己去找上下文**——证据随告警一起到达。
- **S4｜审计与权限模型**（→ 解 P4）。9.5 在 Roles 中把顶层 Alerting 权限重命名为 **"Alerting V2"** 并将子权限标记为 experimental（#288163），**暗示告警权限模型正在重构**；**AI Assistant connector** 外发的报告与建议可经 Slack / email / Jira / PagerDuty 留痕。事件处理过程由此具备可追溯性。

> **边界（明确短板）**：Elastic **无内置 on-call 排班、事件时间线与状态页**。第三方指出其（及 Datadog）"都没有从根因假设直达 on-call 通知、事件时间线、状态页更新的路径"；on-call 完全依赖 **xMatters / Opsgenie / PagerDuty** 等外部连接器实现。**若客户期望"一个平台闭环到 on-call"，Elastic 需要外部工具补齐**——这是与 PagerDuty 等专业厂商的能力边界。
>
> **配套演进**：Watcher（结构化 watch API）作为底层能力长期保留；Alerting V2 为权限模型重构，属**治理演进**。

---

# 大功能点 12：许可、定价与商用交付 —— 买得值

## 12.1 小功能点清单

| # | 小功能点 | 发布时间 | 来源等级 | 说明 |
| --- | --- | --- | --- | --- |
| 12.1 | AGPLv3 许可选项新增 | 2024-08-29 | B | 在 SSPL 1.0 与 ELv2 之外新增 OSI 认可的 AGPLv3；**客户端库仍为 Apache 2.0，二进制分发不变** |
| 12.2 | Shay Banon《Elasticsearch Is Open Source. Again!》 | 2024-08-29/30 | B | 官方口径：三许可并存、"不删除任何既有选项" |
| 12.3 | 与 AWS 商标诉讼状态 | 2022-02 和解（窗口外） | B/C | **商标诉讼已于 2022-02 和解**；2023–2026 窗口内是生态定型（2024-09 OpenSearch 移交 Linux 基金会） |
| 12.4 | ECS 与 Profiling Agent 捐献 OTel 社区 | 2024–2025 | B | 官方称已成为 OTel 前三大贡献者之一 |
| 12.5 | **AutoOps 面向自建用户免费** | 2025-10-02 | B/C | 云连接式 AutoOps 免费提供（含 ECE / ECK / 私有云）：实时问题检测、成本/资源优化、只读诊断；**仅上传运维元数据，业务数据不出本地** |
| 12.6 | AutoOps 对 Elastic Cloud 客户免费 | 2025–2026 | B | 官网宣称"free for Elastic Cloud customers" |
| 12.7 | Elastic Cloud Hosted 四档定价 | 现价（2026-10 采集） | A | Standard $99 / Gold $114 / Platinum $131 / Enterprise $184 每月起（120GB / 2 zones 基础配置） |
| 12.8 | 支持包按消费比例加收 | 现价 | A | Gold 5% / Platinum 10% / Enterprise 15%；Platinum 与 Enterprise 含 **99.95% 月度可用性 SLA** |
| 12.9 | **Observability Serverless 两级套餐** | 2024-12 起 | A | Logs Essentials $0.07/GB 采集 + $0.017/GB·月 保留；Observability Complete $0.09/GB（logs/traces）、$0.023/GB（metrics）+ $0.019 / $0.005 保留 |
| 12.10 | Egress 与试用 | 现价 | A | Egress 每月 50GB 免费后 $0.05/GB；**14 天免费试用**（无需信用卡） |
| 12.11 | 附加组件定价 | 2024-12 起 / 2026-05-01 起 | A | Synthetics 浏览器 $0.0123 / test run、轻量 $28 / location·月；Elastic Managed LLM $4.50/M 输入、$21/M 输出；Workflows 与 Agent Builder 各 10,000 次免费后 $0.0108 / $0.025 每次 |
| 12.12 | 三云 Marketplace 上架与合并计费 | 长期 | B | AWS / Azure / Google Cloud Marketplace 订阅并合并计费，支持 ECUs 预购折扣 |
| 12.13 | Opster 收购完成 | 2023-11-30 | A/B | 约 $23M 现金；即 AutoOps 技术来源 |
| 12.14 | Jina AI 收购完成 | 2025-10-09 | B | 金额未披露；创始人 Han Xiao 出任 Elastic VP of AI |
| 12.15 | Gartner MQ for Observability Platforms 2026 | 2026-07-15 | B | **连续第三年 Leader**，配套 Critical Capabilities 在 7 个用例中 3 个第一；共评估 17 家厂商 |

## 12.2 它对应的用户痛点

> **口径**：本节只写客户侧可感知的痛（时间 / 钱 / 人 / 合规 / 组织）。**注意："供应商自己的成本"不构成客户问题**；只有出现在**客户自己账单上**的成本才写进本节。

- **P1｜账单与预算不可预期，无法向财务解释下个季度花多少**。按节点或按 RAM 预留的计费方式与真实用量脱节，买多了浪费、买少了降级；可观测数据的量又是波动的。（钱）
- **P2｜采购与合规门槛卡在流程上**：许可条款、加密与认证基线、可用性承诺（SLA）不达标，产品能力再强也进不了采购清单。（合规 / 组织）
- **P3｜部署形态选型困难，且迁移风险高**。自建、托管、Serverless 各有取舍，选错一次就要付一次迁移代价；受监管行业还要考虑数据出境与气隙部署。（组织 / 钱）
- **P4｜开源许可的不确定性影响长期技术选型**。许可曾从 Apache 2.0 改为 SSPL+ELv2，客户担心同类事情再次发生，于是要么被锁定、要么不敢深度投入。（组织 / 钱）
- **P5｜跨团队与多设备的权限治理与运维可见性不足**。谁能看什么数据、集群为什么慢、成本为什么涨，缺少统一视图。（组织 / 合规）

## 12.3 它是如何解决的

| 架构约束 | 由哪条痛点倒推出来 | 落到了哪些功能 |
| --- | --- | --- |
| 计费单位必须与真实用量对齐，且有多档可选 | P1 | 双计费模型（GB / VCU）、卷阶定价、14 天试用 |
| 能力必须按档分层，且合规基线内建 | P1、P2 | Hosted 四档 + Serverless 两级、SLA 99.95%、三许可选项 |
| 交付形态必须覆盖自建到全托管的全谱系 | P3 | Serverless / Hosted / Self-managed（含 ECE/ECK）、三云 Marketplace |
| 许可必须包含 OSI 认可的开源选项，且生态中立 | P4 | AGPLv3（2024-08）、客户端库 Apache 2.0、ECS 捐献 OTel |
| 运维与成本必须可观测、可自助 | P5 | AutoOps（自建版免费、Cloud 免费、Serverless 自动启用） |

- **S1｜双计费模型 + 卷阶定价**（→ 解 P1）。**Elastic Cloud Hosted** 按资源订阅（Standard $99 / Gold $114 / Platinum $131 / Enterprise $184 每月起，120GB / 2 zones 基础配置）；**Serverless** 按用量（Observability 按 GB 摄取 + GB·月 保留；Elasticsearch 按 VCU）。同时提供**卷阶定价**与 **14 天免费试用**（无需信用卡）、Egress 每月 50GB 免费。**客户可以先试后买、可以按量付费**，不必提前猜容量。
- **S2｜能力分层与 SLA 承诺**（→ 解 P1、P2）。Hosted 四档逐级解锁：Platinum 含高级安全、机器学习、CCS、服务地图、尾采样、SLO；Enterprise 含可搜索快照、GPU 推理（EIS）、Agent Builder、Workflows、SAML SSO；**Platinum 与 Enterprise 含 99.95% 月度可用性 SLA**。Serverless 侧为 **Logs Essentials / Observability Complete 两级**。**客户按需选档，且能拿到可写进合同的可用性承诺**。
- **S3｜三部署形态 + 三云 Marketplace**（→ 解 P3）。**Serverless / Hosted / Self-managed（含 ECE / ECK）**全谱系覆盖；Elastic Cloud 可在 **AWS / Azure / Google Cloud Marketplace** 订阅并**合并计费**，支持 ECUs 预购折扣；官方另有 GDC air-gapped 合作与 CISA SIEM as a Service。**从气隙到全托管，客户能在同一套技术栈上选形态**。
- **S4｜AGPLv3 回归与生态中立**（→ 解 P4）。**2024-08-29 新增 AGPLv3**，与 ELv2、SSPL 1.0 **三选一**，Elasticsearch / Kibana 重新被正式视为开源软件；**客户端库仍为 Apache 2.0，二进制分发不变，对既有 SSPL/ELv2 用户无影响**；ECS 与 Profiling Agent 捐献 OTel 社区，EDOT 强调"无 vendor lock-in、修复回流上游"。**"会不会被锁定"的顾虑被结构性削弱**——这也是恢复社区信任的关键一步。
- **S5｜AutoOps 免费开放**（→ 解 P1、P5）。**2025-10-02 起面向自建用户免费**（含 ECE / ECK / 私有云）：实时问题检测（摄入瓶颈、分片不均、映射错误）、成本与资源优化建议、只读诊断用于加速支持；**仅上传运维元数据，业务数据不出本地**。AutoOps 同样**对 Elastic Cloud 客户免费**，并在 Serverless 上**自动启用**，暴露 VCU、摄取率、保留量等计费维度。**集群慢与成本涨的原因，客户可自助定位**。

> **边界**：
> - **Observability 的收入分项与 ARR 从未披露**。公司只以 **ACV 口径**给出电话会比例（Observability 约 40%+、Security 约 25%）。**约四成 ACV ≠ 收入占比**，报告中不得当作收入引用。
> - **Observability Serverless 实为两级（Logs Essentials / Observability Complete），并非三级**；"Logs Complete / Logs Performance"**未在官方页面出现**。
> - Serverless 价格随云厂商与区域变化，页面上的 `$` 为 **as-low-as 最低价**；Hosted（按 RAM）与 Serverless（按 GB/VCU）**是两套计费模型，不可混用价格**。
> - AGPL 加入日期存在官方 2024-08-29/30 与 10-K 转述"2024-11-12"的口径冲突，以**官方公告为准**。
> - FY2026 GAAP 净利润中**含约 434.9 百万美元一次性递延所得税估值备抵释放**，引用时必须注明。
>
> **配套演进**：收购 Opster（2023-11，约 $23M）与 Jina AI（2025-10-09，金额未披露）；Google Cloud Partner of the Year 2026；CISA SIEM as a Service——均属**生态与资本配套**，非客户痛点归属。

---

# 附一：完整时间线（倒序）

> **口径**：只列本报告"大功能点"中作为解法的关键事件；日期取官方发布日或所在版本 GA 博客日；跨版本同发布（8.18=9.0、8.19=9.1）标注主版本。

| 日期 | 版本 | 事件 | 组 |
| --- | --- | --- | --- |
| 2026-09 | Serverless | 跨项目搜索（CPS）GA | 3 |
| 2026-08-04 | 9.5 | Columnar / Columnar Logs；ES\|QL `PROMQL` GA；Prometheus remote write + Prometheus HTTP API GA；ES 原生 OTLP logs/traces 端点（preview）；Kubernetes AI-ready 集成；EDOT Collector 内嵌进 Elastic Agent | 1/2 |
| 2026-08（约） | 9.5 | Agent Observability & Monitoring；human-in-the-loop 审批门；Workflows 自然语言编写 GA + 版本化；Observability 默认聊天体验切为 AI Agent；Grafana / Datadog 迁移工具 GA | 7/9 |
| 2026-08（约） | 9.5 | AI 驱动告警分类；告警内联 service map；Alerting V2 权限（实验性） | 6/11 |
| 2026-07-15 | — | Gartner MQ for Observability Platforms 2026：连续第三年 Leader | 12 |
| 2026-06（约） | 9.4（补丁至 6-30） | APM Server 状态自检上报 | 8 |
| 2026-05-05 | 9.4 | ES\|QL `RERANK` GA；PromQL 技术预览 | 2 |
| 2026-05（约） | 9.4 | **Workflows GA**；Agent Builder 原语扩至 Skills/Attachments/Connectors/Plugins；Agent Skills 5 工作流；Observability MCP App（K8s 调查） | 7 |
| 2026-04-16 | Serverless | 跨项目搜索（CPS）技术预览 | 3 |
| 2026-02 | 9.3 | **Streams 从 message 字段一键解析**；`pattern_text` GA；Failure Store 默认启用；EIS 支持 Jina 三模型 GA；EIS 经 Cloud Connect 支持自管集群；`timezone` GA / `LIMIT BY`；ES\|QL 逻辑视图/子查询/读时模式（预览） | 1/2/4/5 |
| 2026-02 | 9.3 | **Agent Builder GA**；**Workflows 技术预览**；Elastic MCP Server | 7 |
| 2026-02 | 9.3 | Serverless 扩展至 18 个区域；AutoOps 面向自建用户免费（2026-02-25 博客口径，另有 2025-10-02 新闻稿口径） | 3/12 |
| 2025-10-29 | 9.2 | **Streams GA**（AI 分区/解析/富化/保留/数据质量）；**Significant Events 技术预览**；Logs Streams 直投 `/logs`（预览）；`pattern_text` 技术预览 | 4/6 |
| 2025-10-29 | 9.2 | **Agent Builder 技术预览**；ES\|QL `FUSE` / Smart Lookup Joins；Discover 指标体验；ES 原生 OTLP metrics 端点；Observability 导航更新 | 2/3/7/9 |
| 2025-10-09 | — | Jina AI 收购完成（金额未披露） | 12 |
| 2025-10-02 | — | AutoOps 面向自建 Elasticsearch 免费（云连接式） | 12 |
| 2025-07 | 9.1 / 8.19 | **AI Assistant 会话归档/分享/导出**；**隐名化（Anonymization）**；KB 模型可选 ELSER / E5 + KB on EIS | 5 |
| 2025-07 | 9.1 / 8.19 | ES\|QL `LOOKUP JOIN` GA + CCS GA；`FORK`/`SAMPLE`/`COMPLETION`（预览）；全文函数 GA；merge/recovery 大改 | 2 |
| 2025-07 | 9.1 / 8.19 | **面向 SRE 的告警增强 GA**；告警详情页增强；SLO Definition/单页管理；APM 渐进式加载；APM 高级 UI 设置移除；Tail sampling TTL | 8/10/11 |
| 2025-06-26 | Serverless | Serverless GA（Azure EastUS）；无状态架构技术细节披露 | 3 |
| 2025-04-24 | Serverless | Serverless 上线 Google Cloud Marketplace | 3 |
| 2025-04-15 | 9.0 / 8.18 | **EDOT 全组件 GA**；**Automatic Import GA**；logs-*-* 默认 LogsDB；synthetic recovery source 默认；ES\|QL `LOOKUP JOIN`/`CHANGE_POINT`（预览）；`route_on_sort_fields` | 1/2 |
| 2025-04-15 | 9.0 / 8.18 | Cases 模板 GA；Find SLO API 游标分页；Discover 自定义格式化；AI Assistant 原生 function calling 默认启用；可从设置页安装 KB；AI Assistant 内嵌 Discover | 5/9/11 |
| 2025-01 | 8.17 | KB 引入 `semantic_text`（同时引入空文档 OOM 缺陷） | 5 |
| 2024-12-13 | 8.17 | **LogsDB GA**（日志存储最高 -65%）；ES\|QL `MATCH`/`QSTR`；**Logs Explorer → Discover 融合** | 2/9 |
| 2024-12-02 | Serverless | **Search AI Lake / Elastic Cloud Serverless GA（AWS）** | 3 |
| 2024-11-12 | 8.16 | `best_compression` 切 ZSTD；DSL 全局保留；ES\|QL `INLINE STATS` | 2 |
| 2024-11-12 | 8.16 | **Synthetics 告警增强 + MFA**；**Direct tracing 到 ES（EDOT 可替代 APM Server）**；Discover 上下文感知/自定义视图；主机监控 streamlined onboarding | 4/8/9/10 |
| 2024-08-29 | — | **AGPLv3 许可选项新增**（与 ELv2、SSPL 三选一） | 12 |
| 2024-08（8.15） | 8.15 | **LogsDB 技术预览**；**Automatic Import 技术预览**；Universal Profiling OTLP；Log Rate Analysis 自然语言洞察；**Uptime 弃用**；SLO History 标签 | 1/2/4/6/10 |
| 2024-06-06 | 8.14 | **ES\|QL GA**；**DSL GA**；Logstash on ECK GA；Universal Profiling 支持 .NET | 1/2 |
| 2024-06-06 | 8.14 | **Federated SLOs**；Grouped SLO embeddable；**SLO 燃尽率告警依赖通知**；Synthetics Availability SLI；AI Assistant API / starter prompts GA / Claude 3 | 5/10 |
| 2024-05 | Serverless | **Search AI Lake + Serverless 首次发布（技术预览）** | 3 |
| 2024-03 | 8.13 | **AI Assistant Bedrock GA**；ES\|QL 编辑与可视化（预览）；SLO 分组/过滤 + triage 页 | 5/10 |
| 2024-01-19 | 8.12 | **AI Assistant GA + Knowledge Base + RAG**；**SLO GA**；燃尽率预算消耗模式；Time Slice SLI；APM Attacher for K8s GA；Mobile APM GA；**Log Rate Analysis GA** | 5/6/8/10 |
| 2023-11-13 | 8.11 | **ES\|QL 技术预览**；**DSL 技术预览**；SLO 技术预览；Lens 内联编辑；ES\|QL 告警规则类型；条件动作；Universal Profiling 与 APM 集成；合成监控自动重试 | 2/8/9/10/11 |
| 2023-09-22 | 8.10 | **Universal Profiling GA**；Log rate dips；Change Point Detection；Data Comparison；Log Pattern Analysis UX | 1/6 |
| 2023-08-10 | 8.9 | **AI Assistant 首次技术预览**（仅 OpenAI/Azure）；TSDS 成为常用集成默认 | 1/5 |
| 2023-05-25 | 8.8 | **Synthetic Monitoring GA**（app / Project monitors / 全局托管基础设施 / 私有位置）；GitOps 化合成监控 | 10 |
| 2023-04 | 8.7 | **TSDB / TSDS GA**（含 Downsampling、Synthetic _source） | 2 |
| 2023-01 | 8.6 | Opsgenie connector GA | 11 |

---

# 附二：演进规律与对自研的启示

## 规律 1：Elastic 的 AI 路线是"三次形态跃迁"，不是"功能叠加"

2023-08（8.9）AI Assistant 只是**五类"解释型"用例**；2024-01（8.12）带 **Knowledge Base + RAG** 转 GA，成为"会引用你公司文档的助手"；到 **2025-10（9.2）**，Streams + Significant Events + Agent Builder **三件套同版本登场**，Elastic 把 AI 从"聊天助手"**重构为"日志结构化 + 事件流 + agent 框架"**；2026 年 Workflows / Agent Observability / nightshift 进一步推向"**受治理的自动化**"。

> **对自研的启示**：AI 助手的能力边界不由模型决定，而由"**能否把结论接回可执行的动作**"决定。只做问答的助手，天花板是"省一点查资料的时间"；能触发工作流并留审计的助手，才进入 MTTR 与人力预算。

**规律 2：成本是 Elastic 对 Datadog/Splunk 的主战场，且是"客户账单上"的成本**

LogsDB（-65%）、TSDS（-70%）、ZSTD（-12%）、pattern_text（-50%）、Columnar、Search AI Lake（$0.047/GB·月 保留）、AutoOps 免费——这些是**出现在客户自己账单上**的数字，因此构成客户问题；而"压缩编码器怎么做""存储与计算是否耦合"只是设计约束。

> **对自研的启示**：写竞品分析的痛点段时，**必须区分"客户的成本"与"供应商的成本"**。前者可写进 P 列表，后者只能写进架构约束表。

**规律 3：Elastic 用"标准协议 + 开放生态"消解锁定，而非用功能墙**

OTel-native（EDOT）、无 schema 转换、Prometheus remote write / PromQL 原生、MCP server、A2A、AGPLv3、ECS 捐献 OTel、AutoOps 只上传运维元数据——**方向一致的"降低客户退出成本"**。

> **对自研的启示**：在采集与查询这两个客户最容易感到被绑定的层面，**采用标准协议能显著降低采购阻力**；把"可替换性"做成卖点，比把"功能独占"做成卖点（在这些层面）更有效。

**规律 4：Elastic 的"统一体验"是**减法**——把多个入口收成一个**

Logs Explorer 并入 Discover（8.17）、APM 高级 UI 设置移除（9.1）、Uptime 弃用并入 Synthetics（8.15）、导航菜单整合（9.2）、APM 应用层向统一形态收敛。**方向是"少几个入口"，而非"多几个应用"**。

> **对自研的启示**：界面数量的增长是产品债而不是产品力。整合动作通常伴随短期用户抱怨，但长期降低学习成本。

**规律 5：Elastic 在 DEM 侧有明确短板，且在"事件响应闭环"上依赖外部工具**

**RUM 无会话回放**（2023–2026 官方与第三方一致确认）、**无内置 on-call 排班 / 事件时间线 / 状态页**（依赖 PagerDuty、Opsgenie、xMatters）。二者是**结构性缺口**而非尚未排期。

> **对自研的启示**：竞品的短板清单比优势清单更有决策价值——**若我方在"会话回放/用户旅程"或"on-call 闭环"上有积累，这两处是可正面进攻的位置**；反之，若目标客户以"一个平台闭环"为决策标准，则需评估与专业厂商的合作而非自建。

## 附二·引述框

> **一句话规律**：Elastic 2023–2026 的四年，可以概括为 **"先把成本打下来（存得起）→ 再把知识接进来（问得懂）→ 最后把动作接上去（做得动）"**。它的每一次形态跃迁，都不是加功能，而是**改变 AI 与平台的关系**：从"AI 解释数据"→"AI 召回知识"→"AI 结构化数据"→"AI 触发动作"。

---

# 附三：对自研 APM AI 助手的对标启示

> **前提**：本文的对照对象是锐捷 APM 产品的 Web 端 AI 助手（开源多 Agent 框架 + 商用大模型 API），目标是在认证（802.1X / Portal / MAC 无感知）等方向做根因分析。下表按"能否直接照搬 / 需要改造 / 应避免"分类。

| # | 启示 | 来源（本报告章节 / 功能） | 为什么重要 |
| --- | --- | --- | --- |
| 1 | **AI 助手的价值要在"接上动作"时才兑现**：先把 Read 类能力（查日志/查指标/查拓扑）做扎实，再逐步开放 Write 类动作，并用 human-in-the-loop 审批门隔离 | 大功能点 7（Agent Builder + Workflows + HITL 审批门） | 只做问答的助手无法进入客户的 MTTR 与人力预算；但直接开放写操作会被安全团队拦下。**审批门是 Write 能力的前置条件**，不是可选项 |
| 2 | **知识库（RAG）是"专家能力组织化"的最低成本手段**：把 runbook、历史工单、认证故障处置手册灌入检索，成本低、见效快 | 大功能点 5（Knowledge Base + RAG，8.12 GA） | 与我方"根因分析"目标直接相关——认证类故障的处置知识高度依赖老专家，KB 是把它变成团队资产的捷径。**优先级建议：高于多 Agent 编排** |
| 3 | **"零配置检测"比"可配置检测"更容易落地**：先给出开箱即用的异常基线（无需客户调阈值、无需数据科学家），再提供可调参数 | 大功能点 6（零配置 ML 异常检测、K8s 100+ 预置 ML 作业、Significant Events 零配置检测） | 客户侧普遍没有数据科学能力；要求客户配检测规则等于把成本转嫁给客户。**认证场景可在"认证失败率/耗时分布"上先做基线** |
| 4 | **AI 输出的"可解释性"是合规场景的入场券**：输出带统计显著性的归因（p 值、变化点、对比基线），而不只是"检测到异常" | 大功能点 6（Log Rate Analysis 的 p_value 打分、Change Point Detection、Data Comparison） | 认证故障常涉及跨团队与安全部门，**"为什么这么判断"必须可举证**。可解释性直接影响结论能否被采信 |
| 5 | **AI 能力与 ML 许可解耦，能显著降低客户的采购阻力** | 大功能点 4（Streams 与 ML 解耦："不需要 ML 节点，AI 特性走生成式连接器"） | 若 AI 功能要求客户额外购买 ML 容量，采购流程会多一道审批。**把我方 AI 助手的算力依赖设计为"复用既有商用大模型 API"而非新增专用资源** |
| 6 | **敏感数据出厂前必须可脱敏，且默认关闭**：提供规则化掩盖（PII/账号名），并把"是否使用客户数据训练"写进明确声明 | 大功能点 5（Anonymization，8.19；"不使用客户数据训练模型"声明） | 认证日志里常见用户名、MAC、IP 与设备标识，属于严格意义上的个人/设备敏感数据。**这是能否通过客户安全评审的关键项** |
| 7 | **把"调查结论"标准化成可外发的结构（事件 + 证据 + 建议），并支持向既有工单系统输出** | 大功能点 11（Cases 模板、Excel 之外的 30+ 连接器、告警详情页内置证据）、大功能点 6（Significant Events marker） | 客户已有 ITSM/工单体系。**结论进不了工单，就等于没有产生组织价值**；反之，能进工单的结论会被反复引用 |
| 8 | **标准协议能显著降低采购阻力**：采集与查询层优先走标准（OTel、PromQL 等），把"可替换性"作为卖点 | 大功能点 1（EDOT / OTel-native、Prometheus remote write）、大功能点 2（ES\|QL） | 客户对"AI 助手 + 专用数据格式"的组合最敏感；**标准协议是打消锁定顾虑的最直接手段** |
| 9 | **需要正面评估的竞品短板**：会话回放 / 用户旅程、on-call 闭环 | 大功能点 10（RUM 无会话回放）、大功能点 11（无内置 on-call） | 若我方在这两处有积累，是**可进攻的位置**；若没有，则应明确写入"不做清单"，避免资源分散 |
| 10 | **知识库与语言的适配需要提前规划**：中文/多语言场景需要适配的嵌入模型（Elastic 提供 ELSER 与 E5 两条路径） | 大功能点 5（KB 模型可选 ELSER / E5 以支持非英语） | 中文 runbook 与中文日志的语义检索效果，是本土产品相对国际厂商的**结构性优势位**，应主动验证而非默认可用 |

---

# 附四：待补充与后续跟踪

## 多源冲突与本报告判定

| 冲突项 | 各源口径 | 本文判定 |
| --- | --- | --- |
| **ES\|QL GA 版本** | 任务背景提示"8.13/8.14"；官方 8.14 博文与 Search Labs GA 专文（2024-06-05）明确 GA | 取 **8.14**。8.13 仅达"Java Client beta / AI Assistant 生成 ES\|QL 技术预览"，无 GA 表述 |
| **LogsDB 起点** | 部分二手称 8.13/8.14 已有；官方回顾称 8.15 技术预览 → 8.17 GA（2024-12-12） | 取 **8.15 预览 → 8.17 GA**；8.13/8.14 是底层 TSDB 编解码器工作，非 logsdb 索引模式本身 |
| **Streams 引入版本** | 任务背景提示"8.18 / 9.0"；官方 9.2 博文、Streams 文档与 Observability Labs 一致指向 **9.2（2025-10-29）GA** | 取 **9.2**。8.18/9.0 只有 LogsDB index mode 与 Discover 日志体验，**无 Streams** |
| **Search AI Lake 发布时间** | 架构首发博文 2024-05；商用 GA 绑定 Serverless AWS 2024-12-02；任务背景提示"2025-04" | **并列**：架构发布 2024-05 / 商用 GA 2024-12-02。未找到 2025-04 专门发布博文，列为待核实 |
| **Serverless GA 日期** | AWS 2024-12-02（博客 + IR 新闻稿一致）；GCP 2025-04（Marketplace 稿 2025-04-24）；Azure 2025-06-26 | 三云分别取 **2024-12-02 / 2025-04 / 2025-06-26**，非单一口径 |
| **Significant Events 成熟度** | 9.2 版本亮点博客将其与 Streams 并列 GA 语境；Observability Labs 与文档明确标注 **tech preview** | **准 GA 叙事、功能状态为 tech preview**，两者都写 |
| **是否支持私有 / 本地 LLM** | 8.14/8.16 文档明确"不支持私有 LLM、不推荐"；2025–2026 文档出现"Connect to a custom local LLM（LM Studio）" | **能力发生反转**，以"早期不支持 → 后期支持"表述，勿取单一口径 |
| **AI Assistant 许可分级** | 官方只说"需适当订阅"（8.9/8.10 明确 Enterprise），从未发布 Standard/Platinum/Enterprise 功能对照表；第三方测评称"Platinum 起含 Full AI Assistant" | 官方口径为准（"需适当订阅"）；第三方分级属**整理推断**，标注为待核实 |
| **Observability 套餐层数** | 任务背景提示"Logs Essentials / Logs Complete / Logs Performance"三级；官方定价页与文档只有 **Logs Essentials / Observability Complete 两级** | 取**两级**；"Logs Complete / Logs Performance"未在官方页面出现 |
| **Observability 收入占比** | 电话会 ACV 口径约 40%+；第三方推算一致 | **ACV 口径，非收入**；收入分项从未披露，不可当收入引用 |
| **AGPL 加入日期** | 官方公告 2024-08-29 / 博客 2024-08-30；10-K 转述"2024-11-12" | 取 **2024-08-29/30**（官方一手）；11-12 疑为技术生效或转述误引 |
| **ES\|QL `FORK` / `FUSE` 起始版本** | Search Labs 博文称 FORK 为 9.1 技术预览；官方 JS DSL 文档表记 FORK 最低 9.0；FUSE 记为 9.1 而第三方记为 9.2 | 主线取**博文口径**（FORK 9.1），并标注文档表差异；存疑 |
| **CPS GA 日期** | 官方博客"Available from September 1, 2026"；Serverless changelog 标 GA 于 2026-09-16 | **并列**：营销可用日 2026-09-01 / changelog GA 标记 2026-09-16 |
| **AutoOps 自建版免费日期** | 新闻稿口径 2025-10-02；官方博客口径 2026-02-25 | **并列**（宣发与博客两个节点） |
| **9.2 / 9.4 / 9.5 精确 GA 日** | 9.2 = 2025-10-29（官方 discuss + what's new）；9.4 = 2026-05-05；9.5 = 2026-08-04（C 级佐证，9.4.3 补丁 = 2026-06-30 已证实） | 取上述日期，标注 9.4/9.5 依赖 C 级佐证 |
| **8.15 发布时间** | 8.15.0 = 2024-08-09（客户端口径）；官方博客 2024-08-08；任务背景 2024-08 | 属 0–1 天差异，统一写 **2024-08** |

## 待补充的信息缺口

1. **Observability 的收入与 ARR 分项**（公司从未披露，只有 ACV 口径）。
2. **Q1 FY2027（截至 2026-07-31）实际财务结果**——截至本文采集日未获取到，仅有 FY2026 财报给出的指引。
3. **9.1 及以后各小版本的精确 GA 日期与逐条 release notes**（部分依赖 C 级佐证，颗粒度未到单 PR 级）。
4. **RUM 与 Elastic Cloud Serverless 的兼容性结论**——第三方向称不兼容（依赖集中式 APM Server），与官方"EDOT 直写、去 APM Server"路线存在张力，需以最新官方文档核实。
5. **nightshift AI SRE 的 GA 时点与定价**——目前为私募预览（Serverless，期间免费）；官方称计划"later this year"转技术预览。
6. **Elastic Managed LLM 与 EIS 的具体单价**（官方仅给"按 model 按百万 token 计费"的口径，Serverless 定价页要求登录/报价）。
7. **`FORK` / `FUSE` 等 ES|QL 命令的权威版本对照表**（官方博文与文档表存在口径差）。
8. **APM Server 的最终 EOL 决策**——官方 EOL 页给 9.x 维护期至 2027-10-15（或 10.0 GA 后 18 个月），但"技术路线已转向 EDOT"与"产品支持承诺"需持续区分跟踪。
9. **Beats 的官方退役时点**——无官方"停更"公告，能力并入 Agent 属推断，需跟踪。
10. **Streams 直投 `/logs` 端点的 GA 时点**（当前为 tech preview）。

## 后续跟踪建议

1. **Watch：nightshift AI SRE 是否在 2026 年内转 GA**——它决定 Elastic 的 AI 叙事能否从"助手"晋级为"无人值守的 SRE"，也决定 Agentic 组是否会成为下一个核心功能点组。
2. **Watch：Streams 的采纳率与分区治理实践**——官方建议"数十个分区而非数百个"，若客户实践中普遍超分区，该能力的成本收益会反转。
3. **Watch：Significant Events 的 GA 时点与准确率披露**——当前是 tech preview，其"自动圈出值得看的证据"的准确率若无法量化，会被真实环境中的误报反噬。
4. **Watch：RUM 是否会补齐会话回放**——这是 Elastic 在 DEM 侧最明确的结构性缺口，也是其与 LogRocket/Datadog 竞争的短板；若补齐，DEM 竞争格局会变化。
5. **Watch：原生 PromQL / Prometheus remote write 的落地效果**——它直接对准 Grafana 生态与"本地 Prometheus 替代"叙事，是 9.5 之后最具攻击性的动作之一。
6. **Watch：Jina AI 并入后的模型路线**（Jina v5 omni 多模态、EIS 模型目录扩展）与其对搜索/可观测两条线的影响。
7. **待补：12 组大功能点之外的"搜索侧"能力**（如 Vector / BBQ / 混合检索）——本报告按可观测性边界做了裁剪，与 Search 解决方案的交叉部分未展开。
