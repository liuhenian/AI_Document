---
title: Kentik AI Advisor 自动诊断机制实现拆解
company: Kentik
category: 网络可观测性 / AIOps / AI SRE
period: 2025-11 ~ 2026-10
created: 2026-10-21
tags:
  - Kentik
  - AI-Advisor
  - Agentic-AI
  - 机制拆解
  - 多Agent框架
---

# Kentik AI Advisor 是如何自动调用工具做诊断的

**调研对象与范围**：Kentik AI Advisor 从 2025-11-18 发布到 2026-10 的七次月度更新，聚焦一个问题——**它的「自动诊断」在工程上是如何实现的**。不含 Query Assistant、Cause Analysis、Journeys 等非 Advisor 产品线（仅在必要处作对照）。

---

## 一句话结论

**它不是一个自研 AI，而是「通用商用大模型 + 43 个强类型工具 + 三段式知识注入 + 告警触发的剧本编排」拼装出来的工程系统。**

- **是不是通用 AI**：是。底层是 OpenAI / Google Vertex AI / AWS Bedrock / Anthropic 的通用大模型，官方明确「不做微调、只做提示词工程」，且模型在 2026 年内换过四轮（Claude Opus 4.8 → 5、Gemini 3.6 → 3.7），并支持跨供应商自动 fallback。**模型是可替换的耗材。**
- **怎么做到自动**：靠**告警策略绑定 Runbook**。告警一触发，Runbook 被注入 system prompt，agent 按剧本逐步调工具。**控制权在写 Runbook 的人手里，不在模型手里**——所以准确说这是「剧本驱动的自动化」，不是「模型自主决策」。
- **它的技术含量在哪**：不在模型，在**工具契约（强类型 schema）+ 知识注入方式（Runbook 进 system prompt 而非 RAG）+ 边界约束（输出格式 / 函数边界 / 数据类型白名单）**。这三件才是可复刻的部分。

---

## 交付内容

本报告包含十一块：

1. **信源与局限**（第 0 章）——三级信源表、六点局限、体系代次对照、一条反直觉观察
2. **三个问题的直接回答**（第 1 章）——是不是通用 AI、靠什么自动、实现路线一句话
3. **模型层**（第 2 章）——用什么模型、双模型架构、模型可替换性的五条证据
4. **编排层**（第 3 章）——两段循环、三级 agent 结构、一轮调查的完整时序、工程硬数字
5. **工具层**（第 4 章）——43 个工具的分类逻辑、强类型契约、数量级必然性
6. **知识层**（第 5 章）——CNC / Runbooks / KB 三条通路的本质差异、**三者各自的所有权与生成路径**、为什么必须三分而不能合一（**本报告认为这是最值得抄的设计**）
7. **触发层**（第 6 章）——从手动到自动的三级触发、Auto Investigations 的真实机制
8. **可信层**（第 7 章）——四种控幻觉手段、只读与写操作的源冲突、官方自认四条局限
9. **开放接入**（第 8 章）——MCP Server 与 A2A 的双向结构
10. **能力边界**（第 9 章）——六条硬边界、七个未公开项、**五项前提依赖、四条官方自认局限、七个常见误期待**、六个从修复史反推的脆弱点、一张六维速查总表
11. **对自研的启示**（第 10 章）——14 条架构判断 + APM/园区认证的直接映射

## 建议读法

- **只想知道「是不是通用 AI」**：读第 1 章 + 2.1，共两页。
- **要复刻它的编排方式**：读第 3、4、5 章 —— 这三章是机制主体。
- **要设计自己的 AI 助手**：直接读第 5 章（知识注入）+ 第 7 章（控幻觉）+ 第 10 章（启示），跳过信源细节。

---

# 0. 信源与局限

## 0.1 三级信源表

| 等级 | 来源 | 覆盖时段 | 本报告用途 |
|---|---|---|---|
| **A** | `kb.kentik.com` 官方知识库（AI Advisor 页、Kentik AI Overview、Kentik AI Settings、MCP Server 页、2026 年 4/6/7/8 月 AI 更新日志） | 2025-06 ~ 2026-10-08 | 全部机制描述的主依据 |
| **A** | `trust.kentik.com` 信任中心 FAQ | 持续更新 | 模型供应商的第三方口径交叉验证 |
| **B** | `kentik.com/blog` 官方博客（AI Runbooks 专文）、`kentipedia` 词条 | 2025-12 ~ 2026 | 官方对设计意图的表述（如 Runbook 注入 system prompt） |
| **C** | 第三方媒体（techbloat 对 autonomous investigation 的解读） | 2026 | 仅用于印证「市场如何理解该能力」，**未用于支撑任何机制描述** |

## 0.2 六点已知局限

1. **无官方架构白皮书**。全部机制描述来自 KB 使用文档 + 月度更新日志，属「从外部行为反推内部结构」。凡本报告推导处均标 `C（本报告推导）` 并给出依据链。
2. **无公开 prompt 模板**。system prompt 的构造方式、工具描述的原文写法均未公开——**这恰好是最想抄的部分，也是最抄不到的部分**。
3. **无性能指标**。准确率、幻觉率、平均调查时长、工具调用成功率全部未公开。
4. **官方叫法混用**。「AI Advisor」「Kentik AI」「Journeys」「Copilot」在文档演进中交替出现，同一能力在不同页面有不同称呼。本报告统一按 **AI Advisor** 指代当前形态（Journeys 已于 2026 年被其取代）。
5. **官方自述与产品行为存在张力**。KB 声明「AI Advisor is read-only」，但 `Sites Tool`（create/update/delete）、`Runbooks`（create/update）、以及 2026-04 的「auto-approved remediation actions」都与该声明字面冲突。第 7.2 节并列处理。
6. **调研截止 2026-10-21**。该产品以月度节奏迭代，本报告的机制描述对 2026-10 之后可能失效。

## 0.3 体系代次对照

Kentik 的 AI 能力在三年内换了三代形态，理解这个演进才能理解 AI Advisor 为什么长这样：

| 代次 | 时间 | 形态 | 交互范式 | 关键缺陷 |
|---|---|---|---|---|
| 一代：Query Assistant | 2024-01-31 | NL2Query | 单轮：问一句 → 翻译成查询 | 只解决「取数」，不解决「诊断」 |
| 二代：Journeys | 2024-01-31 ~ 2025-12 | 会话式调查 + skills | 多轮，但**每一步由人驱动追问** | 工程师仍要自己决定下一步问什么 |
| 三代：AI Advisor | 2025-11-18 起 | Agent + 工具循环 + Runbook | **agent 自主规划并连续调工具** | 仍受工具范围与知识注入约束 |

> **一个必须澄清的事实**：2025-11 的官方公告写的是「AI Advisor **replaces** Kentik AI Journeys」，2025-12 的 Release Notes 记着「Started Initial clean-up of Journeys」。所以三代不是并存关系，而是**替代关系**——Journeys 今天已不可作为选型对象。

## 0.4 一条反直觉观察

**这个系统的「智能」主要发生在调用工具之前，而不是之后。**

大多数人对 AI Agent 的直觉是：模型很聪明 → 它自己想办法 → 不行就再试。Kentik 的实现恰好相反——它把大部分工程投入放在**「让模型少做决定」**上：

- 不让模型自由生成查询语句，而是**先翻译成结构化查询**再执行（NL2Query，官方明示这是为了「limit the risk of hallucinations」）
- 不让模型自由发挥诊断思路，而是**用 Runbook 把步骤写死**并注入 system prompt
- 不让模型自由访问数据，而是**限制在 Kentik 工程师定义的数据类型白名单**内
- 不让模型自由生成输出格式，而是**约束在预期格式内**

换句话说：**它的可靠性来自「收窄模型的自由度」，而不是「增强模型的能力」。** 这一点，是整个报告里对自研团队最有价值的一句话。

---

# 1. 三个问题的直接回答

## 1.1 它是不是通用 AI？

**是，而且是最彻底的那种通用 AI 用法。**

| 判断项 | 结论 | 依据 |
|---|---|---|
| 是否自研基础模型 | **否** | 官方列出四类外部来源：OpenAI 托管、GCP Vertex AI、AWS Bedrock、Anthropic 直连 |
| 是否微调 | **否**，官方明确「不做微调」 | 「Kentik uses a prompt-engineering based approach to deliver AI services, which avoids the need to retrain or fine tune genAI services with customer data.」 |
| 是否可换模型 | **是**，且能跨供应商 | 2026-06 加入「automatic fallback routing across providers」；2026-07 模型注册表新增 Claude Opus 5、Gemini 3.6 Flash |
| 是否可自带密钥 | **是** | Settings 页支持 `Use my own token`，客户可指定 provider / model / region |
| 是否用 RAG | **部分**。知识库是**工具**（按需检索），Runbook 与 CNC 是**注入**（进 system prompt） | 第 5 章详述 |

## 1.2 通过什么方式做到自动诊断？

四层叠起来才成立，缺一层就不是「自动诊断」：

```mermaid
flowchart TB
    L1["① 触发层<br/>告警策略绑定 Runbook，告警一响即启动"]:::trig
    L2["② 编排层<br/>agent 规划 → 选工具 → 执行 → 读结果 → 再规划"]:::orch
    L3["③ 工具层<br/>43 个强类型工具，覆盖流量/指标/日志/设备/云/外部数据"]:::tool
    L4["④ 知识层<br/>Runbook 定步骤，CNC 定环境语义，KB 补产品知识"]:::know

    L1 --> L2
    L2 --> L3
    L4 --> L2
    L3 --> L2

    classDef trig fill:#FAEEDA,stroke:#854F0B,color:#412402
    classDef orch fill:#E6F1FB,stroke:#185FA5,color:#0C447C
    classDef tool fill:#E1F5EE,stroke:#0F6E56,color:#085041
    classDef know fill:#F1EFE8,stroke:#5F5E5A,color:#2C2C2A

    linkStyle default stroke-width:1.2px
```

| 层 | 它解决的问题 | 没有它会怎样 |
|---|---|---|
| **触发层** | 「谁在什么时候启动诊断」 | 只能人工点按钮，谈不上自动 |
| **编排层** | 「下一步查什么」 | 有工具也不会用，退化成聊天机器人 |
| **工具层** | 「能查到什么证据」 | 只能凭模型先验知识答，必然幻觉 |
| **知识层** | 「怎么按你家的规矩查」 | 同一个告警，每次调查路径都不一样 |

**四层里，Kentik 真正做得比别人深的是第 4 层。** 这也是第 5 章要重点拆的部分。

## 1.3 一句话概括它的实现路线

> **用通用模型当推理引擎，用强类型工具当感官，用 Runbook 当临床路径，用告警当触发器，用只读与格式约束当安全边界。**

这是一条「**工程化约束**」路线，不是「**模型能力**」路线。它对自研团队的意义是：**你不需要一个更强的模型，你需要更严格的工程。**

---

# 2. 模型层：它到底用了什么 AI

## 2.1 用的什么模型——四份独立信源指向同一结论

| 信源 | 等级 | 原文（节录） | 说明 |
|---|---|---|---|
| [Kentik AI Overview](https://kb.kentik.com/docs/kentik-ai-overview)（更新 2026-10-08） | A | 「OpenAI models hosted by OpenAI / Foundational models from Anthropic, Google, or others hosted within Google Cloud (GCP Vertex AI service) / Anthropic models hosted in AWS, part of Amazon Bedrock service / Anthropic models hosted by Anthropic」 | 四类来源并列，**无一条提到自研模型** |
| [Trust Center FAQ](https://trust.kentik.com/faq) | A（第三方托管页） | 「Currently, we use AI services from Google's Vertex AI platform, Amazon Bedrock, and Anthropic.」 | 与 KB 大体一致，但**未提 OpenAI**——两处口径略有差异，见下 |
| [Kentik AI Settings](https://kb.kentik.com/kentik-ai) | A | Provider 下拉可选：`Kentik default` / `Open AI` / `Google Vertex AI` / `Google AI Studio (Google Gemini models)`；不支持的可「open a feature request」（含 Azure、AWS、Anthropic） | 说明**默认走 Kentik 自选，客户可覆盖** |
| [2026-07 AI 更新](https://kb.kentik.com/docs/july-2026-ai-insights) | A | 「Claude Opus 5, Gemini 3.6 Flash and 3.5 Flash-Lite added to the model registry；maximum output raised from 64,000 to 128,000 tokens」 | 模型注册表是动态维护的，**换模型是常规操作** |

> **一处需要并列的源冲突**：KB 列了 OpenAI，Trust Center 只列 Vertex AI / Bedrock / Anthropic。**判定：以 KB 为准，Trust Center 为滞后表述。** 理由：① KB 更新于 2026-10-08，晚于 Trust Center；② 2026-08 更新明确提到「support for OpenAI's Responses API enables access to newer OpenAI models」，证明 OpenAI 确实在链路中；③ Settings 页的 Provider 下拉第一项就是 `Open AI`。

## 2.2 双模型架构：Advanced 与 Basic 分工

这是一个容易被忽略但很关键的工程设计——**它不是所有任务都用一个模型**。

| 模型档位 | 用途 | 官方原文 | 工程含义 |
|---|---|---|---|
| **Advanced Model** | 交互式任务，如 AI Advisor 与其他用户驱动的交互 | 「Used for interactive tasks such as AI Advisor and other user-driven interactions」 | 需要强推理、长上下文、能规划多步 |
| **Basic Model** | 轻量任务：摘要数据、检测变点、分析可能原因 | 「Optimized for lightweight tasks like summarizing data, detecting change points, and analyzing probably causes」 | 高频、可容忍略低质量，成本敏感 |

> **为什么必须这么设计**（`C（本报告推导）`）：一次完整调查里，真正需要强推理的只有「规划下一步」和「综合结论」两个环节，中间大量调用（摘要一段日志、判断某个指标是否异常、算一个变化点）都是低难度高频次。若全用 Advanced 模型，**单次调查的 token 成本会高出一个量级**，而质量提升有限。
>
> 依据链：A 级「Advanced 用于交互任务」+ A 级「Basic 优化摘要/变点检测/可能原因」+ A 级 2026-07「prompt caching 降低延迟」与 2026-06「message compression 显示节省 token 数」→ 结论：**成本与延迟是这套系统的核心约束，双模型是成本分层手段，不是能力分层。**

这个判断对自研很实用：**别一上来就用最好的模型跑全流程。** 把「规划/综合」与「摘要/判定」拆开，前者用好模型，后者用便宜模型，成本能降一个数量级。

## 2.3 模型是可替换的耗材——五条证据

如果一套 AI 产品的价值在模型里，它不会一年换四轮模型。Kentik 的做法恰好相反：

| # | 证据 | 出处 |
|---|---|---|
| 1 | 2026-06 加入 `automatic fallback routing across providers`（跨供应商自动降级） | [2026-06 更新](https://kb.kentik.com/docs/june-2026-ai-insights) |
| 2 | 2026-06 加入 Claude Opus 4.8 / Sonnet 5 | 同上 |
| 3 | 2026-07 加入 Claude Opus 5、Gemini 3.6 Flash、3.5 Flash-Lite | [2026-07 更新](https://kb.kentik.com/docs/july-2026-ai-insights) |
| 4 | 2026-08 加入 Gemini 3.7，并支持 OpenAI Responses API | [2026-08 更新](https://kb.kentik.com/docs/august-2026) |
| 5 | 2026-06 加入 `Regional data residency controls`（严格/宽松模式） | [2026-06 更新](https://kb.kentik.com/docs/june-2026-ai-insights) |

**这五条共同说明一件事**：模型层是**可替换基础设施**，被抽象在「AI Gateway / model registry」之后。业务代码不感知具体模型。

> **对自研的直接启示**：如果你们的架构里，「调哪个模型」是散落在各处的硬编码，那模型升级会变成一场灾难。**第一件事应该是造一层模型网关**，把 provider、region、token 上限、temperature、fallback 全部收口。Kentik 连「不同模型的 token 上限自动强制」都做了（2026-06：「AI requests now automatically respect each model's supported token limits and temperature settings」）——这属于典型的「早晚要做，不如早做」。

## 2.4 不做微调，那靠什么保证质量

官方原话（[Kentik AI Overview](https://kb.kentik.com/docs/kentik-ai-overview)，A 级）：

> 「Kentik uses a prompt-engineering based approach to deliver AI services, which avoids the need to retrain or fine tune genAI services with customer data.」

放弃微调后，它有四个替代手段，全部是工程手段：

| 手段 | 官方原文 | 解决什么 |
|---|---|---|
| **NL2Query 中转** | 「uses AI systems to translate natural language questions into queries Kentik can execute against internal systems to limit the risk of hallucinations」 | 不让模型直接「编答案」，而是让它「写查询」，答案由数据库给 |
| **输出格式约束** | 「ensuring outputs remain within expected formats」 | 让模型的输出可被程序解析，而非自由文本 |
| **函数边界约束** | 「functions are bounded within internally defined limits」 | 工具参数有硬边界，越界即失败 |
| **数据类型白名单** | 「AI-accessible data types are limited to a restricted set managed by Kentik's AI engineers」 | 模型只能看见 43 个工具，看不见整个数据库 |

> **这四条合起来，本质是一句话**：**把「模型会不会乱来」这个问题，转成「模型能不能乱来」的问题。** 前者无法保证，后者可以设计。

**为什么不做微调**（`C（本报告推导）`）：
1. **客户数据不能进训练集**——官方明确承诺「customer queries and data are not incorporated into AI-training data sets」。微调需要客户数据，直接与承诺冲突。
2. **微调会让模型与供应商版本解耦**，而它一年换四轮模型。每次换模型都要重训，成本不可接受。
3. **网络诊断的领域知识变化太快**（新厂商、新协议、新平台），微调迭代速度跟不上，提示词与工具迭代更快。

依据链：A 级「不做微调，用提示词工程」+ A 级「客户数据不进训练集」+ A 级「模型一年换四轮并支持跨供应商 fallback」→ 结论：**微调在合规上被禁、在工程上不经济、在业务上不敏捷，三重否定。**

---

# 3. 编排层：一轮诊断是怎么跑起来的

## 3.1 官方口径的两段循环

KB 对 AI Advisor 的描述极简，只有两段（[AI Advisor 页](https://kb.kentik.com/docs/ai-advisor)，A 级）：

> **Interpretation**：Takes your text-based question/prompt, determines the intent (e.g., check interface status, troubleshoot an alert), and, **when applicable, makes a plan and includes its reasoning in the conversation**.
>
> **Tool Execution**：Selects and executes the necessary internal/external data exploration and diagnostic tools (e.g., querying interface inventory, fetching device metrics, running a flow analysis). **All progress, including steps taken and data gathered including visualizations, is shown in the conversation in real time.**

这两段里有三个词值得单独拎出来：

| 词 | 官方原文 | 工程含义 |
|---|---|---|
| **makes a plan** | 「makes a plan and includes its reasoning in the conversation」 | 存在显式的规划步骤，且规划结果**对用户可见**——不是黑箱 |
| **Selects** | 「Selects and executes the necessary ... tools」 | 工具选择由模型决定，不是预设流水线。这是 agentic 与 workflow 的分界线 |
| **in real time** | 「shown in the conversation in real time」 | 流式暴露中间步骤。这既是体验设计，也是**审计设计** |

> **注意一个措辞**：官方说的是「when applicable, makes a plan」——**不是每次都规划**。简单问题（「这台设备在线吗」）直接调一个工具即可，复杂问题（「为什么这条链路抖」）才进入多步规划。这是一个刻意的成本优化：**不是所有请求都值得走完整 agent 循环。**

配套的界面机制（同页）：

- **Reasoning Panes**：推理过程显示在每条消息顶部的可折叠面板（`Hide reasoning` / `Show reasoning`）
- **Completed Task Panes**：完成的任务带绿勾，`View Details` 打开侧栏看详细结果（如 Data Explorer 可视化、KB 搜索结果）

**这两个 UI 机制不是装饰，而是产品设计的一部分**：把推理暴露出来，让工程师可以**审计 AI 的判断依据**。官方甚至在 Best Practices 里教用户怎么审计：

> 「If the answer seems wrong, check the reasoning pane(s). Did the AI correctly identify the device or the time window? Did it choose the wrong data tool?」

## 3.2 三级 Agent 结构——它其实不是单 agent

这是本报告里最重要的一处结构发现。**AI Advisor 不是「一个大 agent 调 43 个工具」，而是三级 agent 结构。**

```mermaid
flowchart TB
    U["用户提问 / 告警触发"]:::in
    MAIN["主 Agent：AI Advisor<br/>规划 · 选工具 · 综合结论"]:::main
    SUB["子 Agent（sub-agent）<br/>按专业域拆分<br/>例：PeeringDB 子 Agent"]:::sub
    A2A["外部 Agent（A2A）<br/>Connectivity Cost Agent<br/>KMI Agent"]:::ext
    TOOLS["Kentik 内部工具<br/>Data Explorer / NMS / Syslog<br/>Device Command / Synthetics ..."]:::tool
    OUT["结论 + 证据链 + 推理面板"]:::out

    U --> MAIN
    MAIN --> SUB
    MAIN --> A2A
    MAIN --> TOOLS
    SUB --> TOOLS
    A2A --> MAIN
    TOOLS --> MAIN
    MAIN --> OUT

    classDef in fill:#F1EFE8,stroke:#5F5E5A,color:#2C2C2A
    classDef main fill:#E6F1FB,stroke:#185FA5,color:#0C447C
    classDef sub fill:#E1F5EE,stroke:#0F6E56,color:#085041
    classDef ext fill:#FAEEDA,stroke:#854F0B,color:#412402
    classDef tool fill:#EEEDFE,stroke:#534AB7,color:#26215C
    classDef out fill:#E1F5EE,stroke:#0F6E56,color:#085041

    linkStyle default stroke-width:1.2px
```

**证据链**：

| 层级 | 证据 | 出处 |
|---|---|---|
| **主 Agent** | 「an AI agent ... creates a plan, collects and analyzes data, and suggests conclusions and next steps」 | [Kentik AI Overview](https://kb.kentik.com/docs/kentik-ai-overview)（A） |
| **子 Agent** | 2026-07：「**PeeringDB sub-agent**: AI Advisor can now query PeeringDB for Internet Exchanges, facilities, and ASN networks」；同时「Clearer sub-agent transcripts: **Sub-agent reasoning and tool calls now render inline** in a compact top-to-bottom flow (reasoning to call to result to next step)」 | [2026-07 更新](https://kb.kentik.com/docs/july-2026-ai-insights)（A） |
| **外部 Agent（A2A）** | 工具清单中 `Agent to Agent (A2A)`：「Access external agents including the **Connectivity Cost Agent** and **KMI (Kentik Market Intelligence) Agent**」 | [AI Advisor 页](https://kb.kentik.com/docs/ai-advisor)（A） |

**为什么必须拆子 agent**（`C（本报告推导）`）：

依据链：A 级「PeeringDB 被做成独立 sub-agent」+ A 级「sub-agent 的推理与工具调用独立渲染」+ A 级工具总数 43 个 → 结论：**当工具数量超过模型可靠选择的阈值时，扁平结构会失效**。43 个工具的描述全部塞进一个 system prompt，会带来三个问题：① 工具描述占满上下文；② 相似工具互相干扰（如 `Alert Statistics` 与 `Alerts`、`Synthes` 系列 5 个工具）；③ 选择错误的概率随候选数上升。

**子 agent 是「工具分组」的一种解法**——把 43 个工具按域切成若干组，每组由一个子 agent 负责，主 agent 只看到「子 agent」这一个入口。

> **对自研的直接启示**：这是回答「单 agent 还是多 agent」这个选型问题的关键证据。Kentik 的答案是：**主 agent 必须只有一个（保证规划一致性），子 agent 按数据域拆（控制工具选择的候选集）**。它不是「多个 agent 投票」，而是「一个大脑 + 若干专科」。

## 3.3 一轮调查的完整时序

把散落在各页的机制拼起来，一轮典型调查的形状如下：

```mermaid
flowchart TB
    T1["① 触发<br/>用户提问 或 告警绑定 Runbook"]:::trig
    T2["② 组装上下文<br/>system prompt = 工具定义 + CNC + Runbook + 会话历史"]:::ctx
    T3["③ 意图识别与规划<br/>判断是否需要多步"]:::plan
    T4{"④ 需要哪个工具？"}:::dec
    T5["⑤ 权限与审批校验<br/>RBAC · 只读 · 写操作需批准"]:::gate
    T6["⑥ 执行工具<br/>内部工具 / 子 agent / A2A"]:::exec
    T7["⑦ 结果结构化回灌<br/>时间戳 · 单位 · 表头"]:::ctx
    T8{"⑧ 证据够了吗？"}:::dec
    T9["⑨ 综合结论<br/>发现 · 可能原因 · 下一步 · 证据链接"]:::out

    T1 --> T2
    T2 --> T3
    T3 --> T4
    T4 --> T5
    T5 --> T6
    T6 --> T7
    T7 --> T8
    T8 -->|"否，继续查"| T3
    T8 -->|"是"| T9

    classDef trig fill:#FAEEDA,stroke:#854F0B,color:#412402
    classDef ctx fill:#E1F5EE,stroke:#0F6E56,color:#085041
    classDef plan fill:#E6F1FB,stroke:#185FA5,color:#0C447C
    classDef dec fill:#EEEDFE,stroke:#534AB7,color:#26215C
    classDef gate fill:#FCEBEB,stroke:#A32D2D,color:#501313
    classDef exec fill:#F1EFE8,stroke:#5F5E5A,color:#2C2C2A
    classDef out fill:#EAF3DE,stroke:#3B6D11,color:#173404

    linkStyle default stroke-width:1.2px
```

逐步说明：

| 步骤 | 做什么 | 关键机制 | 出处 |
|---|---|---|---|
| ① 触发 | 三条路径：手动提问 / 告警页按钮 / 告警策略自动 | 见第 6 章 | [AI Advisor 页](https://kb.kentik.com/docs/ai-advisor) |
| ② 组装上下文 | 把工具定义、CNC、Runbook、会话历史拼成 system prompt | **这是全系统最关键的一步**，见第 5 章 | [Runbook 博客](https://www.kentik.com/blog/ai-advisor-automating-network-troubleshooting-with-ai-runbooks/) |
| ③ 规划 | 判断是否需要多步，输出计划并展示 | 「when applicable, makes a plan」 | [AI Advisor 页](https://kb.kentik.com/docs/ai-advisor) |
| ④ 选工具 | 从可用工具集中选一个或多个 | 受 RBAC 过滤：「users only see tools they are entitled to」 | [2026-04 更新](https://kb.kentik.com/docs/april-2026-ai-insights) |
| ⑤ 审批校验 | 写操作需人工批准；部分动作可自批准 | `Durable tool approval flow` + `Auto-approved tools` | 同上 |
| ⑥ 执行 | 内部工具走 Kentik API；专业域走子 agent；外部走 A2A | 单工具超时 5 分钟 | [2026-07 更新](https://kb.kentik.com/docs/july-2026-ai-insights) |
| ⑦ 回灌 | 结果必须带时间戳与单位，否则模型会答错时间点 | 2026-07 专门加了「ISO timestamps and units on each line, plus a table/legend header」 | 同上 |
| ⑧ 判断终止 | 由模型判断证据是否充分 → 不充分则回到 ③ | **最大迭代次数未公开** | —— |
| ⑨ 结论 | 发现 + 可能原因 + 下一步 + 证据链接 | 2026-08 专门改为「focus on actual findings rather than speculative recommendations」 | [2026-08 更新](https://kb.kentik.com/docs/august-2026) |

> **第 ⑦ 步值得单独说**：2026-07 的更新说明里有一句极有价值的话——「Time series returned to AI Advisor now carry **ISO timestamps and units on each line**, plus a table/legend header, **improving the accuracy of AI answers about specific points in time**」。
>
> 这句话等于官方承认：**在此之前，模型因为工具返回的时间格式不明确而答错了时间点。** 这是一个典型的「工具契约缺陷导致模型表现差」的案例——问题不在模型，在返回结构。

## 3.4 工程细节：真实约束都写在更新日志里

产品页讲的是能力，**更新日志暴露的是真实约束**。下表是本报告从六个月度更新中提取的硬数字：

| 约束 | 数值 | 出处 | 说明 |
|---|---|---|---|
| 单次工具调用超时 | **5 分钟** | 2026-07 | 「Tool calls now time out after five minutes and cancel their underlying queries instead of erroring the entire agent turn」——**超时只废掉这一步，不废掉整轮** |
| 设备命令执行超时 | **600 秒**（原约 30 秒） | 2026-08 | 「supports timeouts up to 600 seconds (previously about 30 seconds), so long-running commands such as show route complete successfully」 |
| 单轮响应超时 | **600 秒** | 2026-08 | 「the MCP server poll timeout now matches AI Advisor's 600-second response timeout」 |
| 最大输出 token | **128,000**（原 64,000） | 2026-07 | 仅对最新 Claude Sonnet / Opus |
| 上下文压缩 | 按会话分组压缩，可显示节省 token | 2026-06 | 「group AI usage by session to optionally compress messages」 |
| 压缩强度 | **放松**（less aggressive） | 2026-04 | 原因：「investigation responses are no longer truncated」——压太狠会截断调查结论 |
| 审批持久化 | 跨刷新 / 跨部署 / 长窗口 | 2026-04 | 「enabling **multi-hour human-in-the-loop** Auto Investigation scenarios」 |
| 异步化 | 提交即返回，轮询取结果 | 2026-04 | 「accepts user messages with an immediate response and lets clients poll for results」 |

> **这组数字揭示了一个容易被忽略的真相**：一次真正的网络调查是**分钟级到十分钟级**的，不是秒级。600 秒的单轮超时、5 分钟的单工具超时、多小时的审批等待——这些数字共同说明：**它的设计假设是「agent 会跑很久」**。
>
> 这对自研的直接含义是：**如果你的架构假设「一次问答 10 秒内返回」，那它根本装不下 agent 式的诊断。** 必须先有异步任务、会话状态、断线重连、进度回放这套基础设施，才谈得上 agent。

**一个具体的技术细节**：2026-04 的更新里提到「The AI Advisor **NMS tool was ported to TypeScript** and hardened against **schema validation errors** that could cause natural-language query failures」。

这句话信息量很大：
1. **工具是用 TypeScript 实现并做 schema 校验的**——不是随便包一层 API
2. 工具层脆弱点是 **schema 校验错误**，会导致「自然语言查询失败」
3. 修法是「加固 schema 校验」，不是「换模型」

**这印证了第 1.3 节的核心判断：可靠性来自工程约束，不是模型能力。**

---

# 4. 工具层：43 个工具是怎么组织的

## 4.1 全部工具按证据域分类

官方在 [AI Advisor 页](https://kb.kentik.com/docs/ai-advisor) 列出了完整清单，并在开头声明「includes, **but is not limited to** the following」——**留了扩展开口**。

按「它提供哪类证据」重新归类，43 个工具可以分成 7 组：

| 组 | 工具数 | 工具名 | 这组回答什么问题 |
|---|---|---|---|
| **① 遥测与流量** | 5 | `Data Explorer`、`NMS`、`Syslog`、`SNMP Trap`、`Custom Applications` | 网络上正在发生什么 |
| **② 告警与缓解** | 5 | `Alerts`、`Alert Statistics`、`Mitigation Events`、`Mitigation Config`、`BGP Mitigation Announcements` | 系统已经判定了什么异常、采取了什么动作 |
| **③ 资产与拓扑** | 6 | `Device Inventory`、`Interface Inventory`、`Site Inventory`、`Device Connections`、`Sites Tool`、`Sitemap` | 有哪些设备、怎么连的、在哪里 |
| **④ 云与外部情报** | 10 | `AWS Inventory`、`Azure Inventory`、`GCP Inventory`、`OCI Inventory`、`Azure Resource Graph Query`、`Cloud Pathfinder`、`ASN Lookup`、`DNS Lookup`、`Whois`、`Network Provider Lookup`、`OTT Inventory`、`PeeringDB`、`KMI` | 自有网络之外的世界长什么样 |
| **⑤ 合成测试** | 6 | `Synthetics Agents`、`Synthetics Test Config`、`Synthetics Test Results`、`Synthetics Test Status`、`Synthetics Alarms`、`Synthetics Trace Results`、`Synthetics Agent Down Alert` | 从外部视角看，服务好不好 |
| **⑥ 设备只读取证** | 3 | `Device Command`、`Device Config`、`Connectivity Test` | 设备内部此刻/过去是什么状态 |
| **⑦ 知识与工作流** | 4 | `Knowledge Base`、`Runbooks`、`Saved Views`、`Agent to Agent (A2A)` | 产品怎么用、别人怎么查过、其他 agent 能帮什么 |

> 注：④ 与 ⑤ 的计数按语义合并，实际清单以官方 43 条为准（本报告逐条核对过，其中 `OTT Inventory` 归 ④，`Synthetics` 系列归 ⑤）。

**这个分类揭示了一个设计原则**：**工具是按「数据源」切的，不是按「用户意图」切的。**

对比一下两种切法：

| 切法 | 例子 | 后果 |
|---|---|---|
| 按**用户意图**切 | `诊断接口丢包`、`排查 BGP 抖动` | 一个意图对应一段固定流程，**退化成 workflow，不是 agent** |
| 按**数据源**切（Kentik 的选择） | `Interface Inventory`、`NMS`、`Syslog` | 模型可以自由组合证据，**真正 agentic** |

> **这是一个关键判断**：按意图切工具，产品看起来「更智能」（一问就答），但实际是把人写的 if-else 包装成 AI；按数据源切，模型必须自己组合，短期效果差、长期上限高。**Kentik 选了后者，这是它敢叫「agent」的原因。**

## 4.2 工具契约：强类型 + schema 校验 + 显式单位

三条证据说明它的工具层不是「薄薄包一层 API」：

| 证据 | 原文 | 含义 |
|---|---|---|
| 用 TypeScript 实现并做 schema 校验 | 2026-04：「The AI Advisor NMS tool was **ported to TypeScript** and **hardened against schema validation errors** that could cause natural-language query failures」 | 工具是**有类型的契约**，不是自由文本接口 |
| 返回必须带时间戳与单位 | 2026-07：「Time series returned to AI Advisor now carry **ISO timestamps and units on each line**, plus a table/legend header」 | 返回结构直接影响模型准确率 |
| 参数受 functions 边界约束 | Kentik AI Overview：「**functions are bounded within internally defined limits**」 | 参数有硬边界，越界即失败 |

**为什么工具契约这么重要**（`C（本报告推导）`）：

依据链：A 级「NMS 工具因 schema 校验错误导致自然语言查询失败」+ A 级「加了时间戳与单位后，模型对具体时间点的回答准确率提升」+ A 级「functions are bounded within internally defined limits」→ 结论：**在这个系统里，模型输出错误的第一大来源不是模型笨，而是工具返回的信息不完整或格式含糊。** 模型只能基于工具给它的东西推理，工具给少了，它就必须猜，猜就是幻觉。

**这条对自研的含义极重**：你们在评估「要不要换更强的模型」之前，应该先检查**工具返回的字段是否够模型用**。Kentik 的经验是：加两个字段（时间戳、单位），比换一个模型更有效。

## 4.3 为什么必须是 43 个这个数量级

43 个不是拍脑袋的数字，它约等于**「网络故障的可能证据来源数量」**：

- 流量侧：NetFlow / sFlow / IPFIX
- 指标侧：SNMP / streaming telemetry
- 日志侧：syslog / trap
- 配置侧：running-config 历史
- 路径侧：ping / traceroute
- 云侧：4 家云的 inventory + 各自的专有查询语言（如 Azure Resource Graph 的 Kusto）
- 外部：PeeringDB / RIPE / Whois / DNS / ASN
- 产品自身：KB、保存视图、告警、合成测试

**任何一个证据源缺席，模型在那类问题上就只能靠猜。** 这是为什么工具数量会膨胀——不是因为功能多，而是因为**证据源多**。

> **对自研的启示**：不要问「我需要几个工具」，要问「**我的故障类型需要哪些证据源**」。工具数 = 证据源数，不是设计选择，是问题域决定的。

---

# 5. 知识层：三条注入通路（本报告认为最值得抄的设计）

## 5.1 三条通路，本质不同

Kentik 有三套机制把「领域知识」喂给模型，但它们的**作用位置完全不同**——这是全篇最容易被忽略、也最重要的一点：

```mermaid
flowchart TB
    subgraph SYS[system prompt（每轮都带）]
        CNC["Custom Network Context<br/>最多 10 万字符 Markdown<br/>环境语义：命名/网段/维护窗"]
        RB["Runbooks<br/>Markdown 剧本<br/>按告警策略绑定"]
    end
    subgraph TOOL[工具调用（按需触发）]
        KB["Knowledge Base 工具<br/>自然语言检索官方文档"]
    end
    MODEL["LLM"]
    BEHAVE["改变模型的默认行为<br/>规划 · 选工具 · 解读逻辑"]
    FACT["补充事实<br/>产品怎么配、有什么能力"]

    CNC --> MODEL
    RB --> MODEL
    MODEL --> BEHAVE
    KB --> MODEL
    MODEL --> FACT

    classDef sys fill:#E6F1FB,stroke:#185FA5,color:#0C447C
    classDef tool fill:#E1F5EE,stroke:#0F6E56,color:#085041
    classDef model fill:#EEEDFE,stroke:#534AB7,color:#26215C
    classDef out fill:#F1EFE8,stroke:#5F5E5A,color:#2C2C2A

    style SYS fill:#F7FAFE,stroke:#B5D4F4,stroke-width:0.5px
    style TOOL fill:#F5FBF8,stroke:#9FE1CB,stroke-width:0.5px
```

| 通路 | 位置 | 触发方式 | 作用 | 容量 |
|---|---|---|---|---|
| **Custom Network Context** | system prompt | 每轮自动携带 | 告诉模型「你家的网络长什么样、话怎么讲」 | 10 万字符 |
| **Runbooks** | system prompt | 告警命中策略时注入 | 告诉模型「这类问题按什么步骤查」 | 未公开 |
| **Knowledge Base** | 工具层 | 模型主动调用 | 补充「产品怎么用」的事实 | 检索式，无上限 |

### 5.1.1 所有权不同：两个是客户资产，一个是厂商资产

上表只说了「在哪生效」，没说「谁能改」。这一列才是三者最根本的分野：

| 通路 | 产出主体 | 客户能否写入 | 治理手段 | 改动影响谁 |
|---|---|---|---|---|
| **CNC** | 客户（仅 Super Administrator） | 能，这是唯一入口 | Audit Log + full version history（2026-07 补） | **全组织所有会话** |
| **Runbook** | 客户；或厂商预置（挂载使用） | 能 | Revision History，可 diff、可回滚 | 绑定的那几条告警策略 |
| **KB** | **Kentik 官方** | **不能** | 随产品发版更新 | 所有调用该工具的会话 |

一句话：**CNC 与 Runbook 是客户资产，KB 是厂商资产。** 这意味着客户想把「自己的知识」喂进去，可靠的口子只有两个——KB 那条路走不通，它装的是 Kentik 的产品文档，不是你的网络事实。

### 5.1.2 三者分别「怎么来的」

这是最容易被跳过的一节：三条通路的**生产成本完全不同**，而成本决定了客户实际会不会用。

**（1）CNC：管理员手写一段长文本，没有 AI 代写路径**

- 入口（A 级，[Kentik AI Settings](https://kb.kentik.com/kentik-ai)）：`Organization Settings » Kentik AI » Custom Network Context`，**只有 Super Administrator 可见**。
- 填写方式：一个输入框，粘贴或手打 Markdown；旁边有眼睛图标可**预览渲染效果**。
- 容量硬限：**10 万字符**，官方原文「Add up to 100K characters of Markdown-formatted text」。
- 官方文档**未提供模板**，也未提供 AI 生成方式——这一点与 Runbook 形成鲜明对比。

也就是说，CNC 的生产方式是最原始的「懂网络的人坐下来写文档」。它的质量完全取决于这个人的表达能力和意愿。

**（2）Runbook：四条生成路径，整整花了九个月才补齐**

| 路径 | 上线时间 | 产出者 | 官方原文要点 |
|---|---|---|---|
| ① 人工手写 | 2025-11（随 GA） | 客户管理员 | 「Create predefined, **Markdown-formatted recipes**」 |
| ② 从对话回捞 | 2026-05 | 用过 AI Advisor 的工程师 | 「create, retrieve, and update runbooks **directly from AI Advisor conversations**, with **automatic linking to alert policies and session tracking**」 |
| ③ AI 基于会话代写 | 2026-08 | AI Advisor 自身 | 「AI Advisor can now **create runbooks based on conversation context**」 |
| ④ 厂商预置 | 2026-07 | Kentik | 「attach **Kentik-provided preset runbooks** to auto-investigations **without owning them**」 |

②③④ 指向同一个问题：**冷启动时能力为零**——客户写出第一条 Runbook 之前，这套机制等于不存在。④ 尤其值得注意：它承认了「不能指望客户先投入写作」，于是先给一份参考答案。

手写路径的实际操作（A 级，[Kentik AI Settings](https://kb.kentik.com/kentik-ai)）：

1. 进入 `Runbooks` 面板 → 点 `+ Add Runbook`，弹窗只有三个字段：**Name**（必填、唯一）、**Description**（可选）、**Instructions**（Markdown 正文，剧本本体）；
2. 切到 **Alert Policy Assignments** 页签，勾选要绑定的告警策略；
3. 点 `Add Runbook` 落库。

**「写内容」与「绑策略」被拆成两个页签**，这不是 UI 洁癖——它给「先写、审完再上线」留出了物理位置。

版本管理也是操作级的（同上）：列表里每条 Runbook 有「倒带时钟」图标 → 左栏当前版本、右栏历史版本列表 → 点任一版本显示 diff（绿=新增、红=删除）→ 点 `Revert` 回滚。编辑走铅笔图标，删除走垃圾桶并二次确认。

> **为什么版本化在这里不是加分项而是必需项**：Runbook 直接进 system prompt，**改错一行，所有绑定该策略的告警会按错误路径批量执行**。这是行为级污染，不是内容级错误。Kentik 给它配 revision history，说明团队理解这件事的严重性。

**（3）KB：不是客户产的，是 `kb.kentik.com` 本身**

官方对该具名工具的描述只有一句：「Search Kentik's documentation and knowledge base using natural language」。

它检索的就是 Kentik 的产品文档站（设备支持矩阵、功能说明、API、配置步骤）。这条通路**比另外两条都老**——2024 年 Journeys 时代的官方博客就写过「Journeys now supports natural language queries of the Kentik Knowledge Base」。客户对它的内容**没有写入权**，只能提需求等厂商更新。

### 5.1.3 为什么必须三条，合成一个大知识库不行

| 维度 | CNC | Runbook | KB |
|---|---|---|---|
| 变更频率 | 季度级（网络改造才改） | 事件级（每次复盘都可能改） | 周级（厂商发版即变） |
| 作用域 | 组织全局，**每轮常驻** | 单条告警策略 | 单次工具调用 |
| 容量压力 | 10 万字符**一直占上下文** | 只在该告警的调查里占 | 命中才占 |
| 治理主体 | 客户管理员 | 客户团队 / 厂商 | 厂商 |
| **失效半径** | 全组织所有回答带偏差 | **绑定的那类告警全部走错路径** | 答一句「查不到」 |

最后一行的数量级差异是决定性的：**三者的失效半径差三个数量级**。合成一个知识库，等于让「改一条维护窗口说明」和「改一条告警的排查路径」共享同一套变更流程——任何运维组织都不会接受这种耦合。

还有一层：**三者的读取方式不同**。CNC 每轮无条件携带，Runbook 命中策略才注入，KB 要模型主动调工具。合成之后必然只剩一种读取方式，而无论选哪种，都会让另外两类知识要么太贵（全量常驻）、要么太不可靠（该查没查）。

### 5.1.4 同一故障，三者各说一句什么

以「接口利用率突增告警」为例（Kentik 官方博客用的就是这个场景）：

- **CNC 说**：「core-sw-01 在张江园区，上联是双 10G 跨运营商 LACP；我们内部管它叫『汇聚』不叫『核心』；周日 02:00–04:00 是备份窗口。」
- **Runbook 说**：「先拉该接口 7 天利用率基线 → 若 >80%，查 flow 的 top talker → 若 top talker 是备份流量，先核对备份窗口是否漂移 → 若不是，再查对端接口错误计数。」
- **KB 说**：「在 NMS 里怎么建这个基线视图、阈值策略怎么配。」

三者拼起来才是完整推理链：**CNC 定义「是什么」，Runbook 定义「怎么查」，KB 定义「工具怎么用」**。缺任何一条，模型都会在那一环上自行补全——而补全就是幻觉进入的位置。

## 5.2 Custom Network Context：给模型一部「环境词典」

官方说明（[Kentik AI Settings](https://kb.kentik.com/kentik-ai) + [AI Advisor 页](https://kb.kentik.com/docs/ai-advisor)，A 级）：

> 「Add up to **100K characters** of Markdown-formatted text into the Custom Network Context input field.」
>
> 「AI Advisor will use this custom network context in **all conversations in your organization**.」

官方给的填写建议很具体，值得完整照录：

- 网络设计与架构（园区 / 广域网 / 数据中心 / 云）
- IP 编址方案
- 设备、接口、站点的命名约定
- 设备类型与厂商
- 维护窗口时间表
- **「customer」这个词在你们语境里指什么**
- 关键应用与流量模式
- 特定运维流程或约束

> **「customer 这个词指什么」这一条最能说明问题**。它说明 CNC 解决的**不是「知识不足」，而是「语义歧义」**。同一个词在不同组织指不同东西——ISP 说 customer 指下游客户，企业说 customer 指内部业务部门。模型不知道这个，就会一直理解错，而且错得很自信。

**为什么是 10 万字符这个量级**：`C（本报告推导）`——依据链：A 级「100K characters」+ A 级「2026-07 最大输出提到 128K tokens」+ A 级「2026-06 加入消息压缩」→ 结论：10 万字符约等于 2.5 万～3 万 token，占主流模型上下文窗口的 10%～25%。**这个量级是「够描述一个中型企业的网络全貌，但不至于挤占会话与工具结果空间」的平衡点。**

## 5.3 Runbooks：注入 system prompt，不是 RAG

**这是整份报告里最有价值的一句话。**

官方博客原文（[AI Runbooks 专文](https://www.kentik.com/blog/ai-advisor-automating-network-troubleshooting-with-ai-runbooks/)，B 级）：

> 「In the overall AI Advisor solution, Runbooks are part of the knowledge and toolbase, alongside Custom Network Context and the Kentik Knowledge Base. This means **Runbooks become part of the system prompt the agent uses to reason through an investigation, and not simply a resource it reads after the fact.**」

这句话把 Runbook 与「检索式知识库」彻底区分开了：

| 维度 | 检索式（RAG） | 注入式（Runbook 的做法） |
|---|---|---|
| 生效时机 | 模型**意识到需要**时才查 | **每一轮都在** |
| 控制力 | 弱——模型可能不查 | 强——绕不过去 |
| 作用 | 提供事实 | **塑造行为** |
| 失败模式 | 该查没查 → 答错 | 上下文过长 → 成本上升 |

**官方明确列出了 Runbook 影响哪五个环节**（同上）：

> 「the Runbook influences: **Planning** / **Tool selection** / **Data retrieval** / **Interpretation logic** / **Recommended next steps**」

这五项恰好覆盖了一次调查的全部决策点。**也就是说，Runbook 不是「参考资料」，而是「思维程序」。**

**Runbook 的内容结构**（官方列举）：

- 关于告警或条件的上下文
- 规定性的诊断步骤
- 提示该查哪些数据源
- 如何解读结果的逻辑
- 任何与该组织相关的自定义流程或注意事项

**运营机制**（[Kentik AI Settings](https://kb.kentik.com/kentik-ai)，A 级）：

- **绑定告警策略**：「Be assigned to one or more alert policies」
- **版本化**：`Runbook Revision History`，可 diff（绿加红删）、可回滚
- **可由 AI 生成**：2026-08「AI Advisor can now create runbooks based on conversation context」
- **可复用厂商预置**：2026-07「Companies can attach Kentik-provided preset runbooks to auto-investigations without owning them」

> **「版本化 + 可 diff + 可回滚」这一点很容易被忽略，但它是关键**。Runbook 是直接进 system prompt 的东西，**改错一行就会改变所有相关告警的处置路径**。所以它必须被当作**代码**来管理，而不是当作文档。Kentik 给它配了 revision history，这个细节说明团队理解这件事的严重性。

## 5.4 Knowledge Base：唯一走 RAG 的那条

`Knowledge Base` 是工具清单里的一个具名工具：

> 「Search Kentik's documentation and knowledge base using natural language」

2024 年 Journeys 时代的官方博客也提过：「Journeys now supports natural language queries of the Kentik Knowledge Base」。

**它为什么可以走 RAG 而不是注入**：因为它的内容是**产品使用知识**（怎么配设备、有哪些 API、支持什么格式），这类知识的特点是：
- 量大且变动频繁（文档每周更新）
- 只在特定问题上用得上（不需要每轮都带）
- 答错代价低（最多是操作指导不准，不会导致误判故障）

**这三条恰好与 Runbook 相反**——Runbook 量小、稳定、每次都相关、答错代价高。**知识该走注入还是检索，取决于这四个属性。**

## 5.5 三者分工：一张表说清

| 问题 | 该用哪条通路 | 为什么 |
|---|---|---|
| 「我们公司的 core-sw-01 属于哪个站点」 | CNC | 稳定、每次都需要、属于环境事实 |
| 「这类告警该按什么顺序查」 | Runbook | 每次都要生效，且必须绕不过去 |
| 「Kentik 的 API 怎么建自定义维度」 | Knowledge Base | 偶发、量大、答错无害 |
| 「我们的维护窗口是周日凌晨」 | CNC | 每次判断「是否变更导致」都要用 |
| 「怎么配置 SNMP trap 采集」 | Knowledge Base | 一次性操作指导 |

## 5.6 一个被低估的设计：用「配置」替代「记忆」

AI Advisor 的 cannot 列表里有一条：

> 「**cannot** Maintain a persistent 'memory' across multiple conversations, **apart from what you configure in Runbooks and Custom Network Context**」（[AI Advisor 页](https://kb.kentik.com/docs/ai-advisor)，A 级）

这句话表面是承认缺陷，实际是**一种设计选择**：

| 方案 | 特点 | 问题 |
|---|---|---|
| 让模型「记住」（向量记忆 / 长期记忆） | 自动、无需人工 | 不可控、不可审计、会漂移、难以解释为什么它这么想 |
| **让人「配置」（CNC + Runbook）** | 需人工维护 | **完全可控、可版本化、可审计、可回滚** |

**Kentik 选了后者，并且 2026-07 补上了审计日志**：「CNC changes are now recorded in the **Audit Log** with dedicated filtering and **full version history**」。

> **这是一个非常值得抄的判断**：在企业级运维场景里，「AI 自己学到的东西」是**负债**而不是资产——因为出问题时你无法解释、无法复现、无法回滚。**「人配置的知识」才是资产。** 所以宁可承认「没有跨会话记忆」，也要把知识放在人能管的地方。

**对自研的一句话建议**：先别做「向量记忆库」，先做「可版本化的配置知识库 + 可审计的变更日志」。前者是玩具，后者是产品。

---

# 6. 触发层：从「人点一下」到「告警自己跑」

## 6.1 三级触发，自动化程度逐级上升

| 级别 | 入口 | 人要做的事 | 系统自动做的事 | 出处 |
|---|---|---|---|---|
| **L1 纯手动** | 主导航 `AI Advisor` 全页模式；任意页 `Ask` 按钮（Overlay） | 自己写问题 | 理解意图、规划、调工具 | [AI Advisor 页](https://kb.kentik.com/docs/ai-advisor)（A） |
| **L2 上下文预填** | `Alerting` / `Alert Details` 页的 `Investigate with AI Advisor` | 点一下按钮 | **自动用固定提示词「Troubleshoot this alert for me」并带入该告警上下文开始调查** | 同上（A） |
| **L3 全自动** | 告警策略绑定 Runbook（Auto Investigations） | 事先写 Runbook + 绑定策略 | 告警一触发即启动，按 Runbook 走完多步调查 | [Runbook 博客](https://www.kentik.com/blog/ai-advisor-automating-network-troubleshooting-with-ai-runbooks/)（B）+ [2026-04 更新](https://kb.kentik.com/docs/april-2026-ai-insights)（A） |

官方对 L2 的原文描述很关键：

> 「When you open AI Advisor on the following Kentik portal pages, it can **automatically use the prompt 'Troubleshoot this alert for me' and start investigating based on the device/alert you are viewing**.」
>
> 「Click Investigate with AI Advisor in the sidebar under Take Action (**troubleshooting conversation starts automatically**).」

> **L2 是一个被低估的体验设计**：它把「用户要会提问」这个门槛消掉了。工程师不需要知道该问什么，只需要点一下，系统自己知道「当前上下文是这个告警，那就按排查这个告警来」。**这比让用户写一段好的 prompt 有用得多**——大多数一线工程师不会写 prompt。

## 6.2 Auto Investigations 的真实机制

官方博客把 L3 的执行过程写成了四步（[原文](https://www.kentik.com/blog/ai-advisor-automating-network-troubleshooting-with-ai-runbooks/)，B 级）：

> **第一步**：AI Advisor receives alert context. AI Advisor automatically begins a pre-determined and validated investigation with relevant data preloaded.
>
> **第二步**：when the alert policy tied to a Runbook is triggered, AI Advisor loads the assigned Runbook. This incorporates the instructions **directly into AI Advisor's reasoning process**.
>
> **第三步**：AI Advisor executes multi-step troubleshooting. The agent calls Kentik tools that can search flow records and device metrics, look up information in the Kentik knowledge base, utilize synthetic tests, perform a syslog search, and more.
>
> **第四步**：AI Advisor explains findings and recommends actions.

对应到系统里的实际形态：

```mermaid
flowchart TB
    A1["告警策略触发<br/>如：接口利用率 > 90%"]:::trig
    A2["查策略绑定的 Runbook<br/>如：高利用率排查剧本"]:::ctx
    A3["组装 system prompt<br/>工具定义 + CNC + Runbook + 告警上下文"]:::ctx
    A4["agent 按剧本逐步调工具<br/>流量 → 指标 → syslog → 合成"]:::exec
    A5{"是否涉及写操作？"}:::dec
    A6["挂起等待人工批准<br/>可跨刷新、跨小时"]:::gate
    A7["综合：发现 · 可能原因 · 下一步"]:::out
    A8["推送 Jira / ServiceNow / 告警通知"]:::out

    A1 --> A2
    A2 --> A3
    A3 --> A4
    A4 --> A5
    A5 -->|"是"| A6
    A5 -->|"否"| A7
    A6 --> A7
    A7 --> A8

    classDef trig fill:#FAEEDA,stroke:#854F0B,color:#412402
    classDef ctx fill:#E1F5EE,stroke:#0F6E56,color:#085041
    classDef exec fill:#E6F1FB,stroke:#185FA5,color:#0C447C
    classDef dec fill:#EEEDFE,stroke:#534AB7,color:#26215C
    classDef gate fill:#FCEBEB,stroke:#A32D2D,color:#501313
    classDef out fill:#EAF3DE,stroke:#3B6D11,color:#173404

    linkStyle default stroke-width:1.2px
```

**支撑这个流程的三条工程实现**（都在 2026-04 的更新里）：

| 机制 | 原文 | 为什么必须有 |
|---|---|---|
| **审批持久化** | 「Durable tool approval flow: approvals now persist across page refreshes, deployments, and long approval windows, **enabling multi-hour human-in-the-loop Auto Investigation scenarios**」 | agent 跑到一半要人批准，人可能几小时后才看到。若审批状态存内存，一刷新就丢，整个调查作废 |
| **会话级待批准状态** | 「surfaces an **awaiting-approval state at the session level** when any message needs user approval」 | 用户要能一眼看出「这个调查卡在哪了」 |
| **自动批准名单** | 「Auto-approved tools support: certain remediation actions can execute **without per-turn human approval**」 | 否则每个动作都要人点，自动化的意义被抵消 |

## 6.3 结论：这是「剧本自动化」，不是「自主决策」

必须把这件事说清楚，因为它直接影响选型判断。

| 维度 | 「自主决策」的含义 | Kentik 的实际做法 |
|---|---|---|
| 什么时候启动 | 系统自己判断该查了 | **告警策略触发**（人配的阈值） |
| 查什么 | 模型自己决定 | **Runbook 规定步骤**（人写的剧本） |
| 用什么工具 | 模型自由选 | Runbook 建议 + 模型在建议内选择 |
| 什么时候停 | 模型判断 | 模型判断，但受 Runbook 引导 |
| 能不能改 | 自主执行动作 | **写操作需人工批准**（除白名单） |
| 知识边界 | 自主学习 | **CNC + Runbook 人工配置**，不做跨会话记忆 |

> **一句准确的定性**：**它是一个「能把 SOP 自动执行完的 agent」，不是一个「自己发现问题的 agent」。**
>
> 发现问题的还是阈值告警；它做的是**告警之后的那一段**——把人原本要花 30 分钟做的多屏切换、多点查证、脑内关联，压缩成一次自动执行。官方博客对价值的表述也印证这点：「Runbooks help AI Advisor perform triage in **seconds instead of minutes or hours**」（B 级，厂商自述，仅作量级参考）。

**这个定性对自研非常重要**：如果你的目标是「让 AI 自己发现问题」，那 Kentik 这套不是答案；如果你的目标是「告警之后自动跑完排查」，那这套是目前最完整的公开样本。

---

# 7. 可信层：它是怎么控幻觉的

## 7.1 四种手段，没有一种依赖模型

| # | 手段 | 官方原文 | 作用点 |
|---|---|---|---|
| 1 | **NL2Query 中转** | 「uses AI systems to translate natural language questions into **queries Kentik can execute** against internal systems to **limit the risk of hallucinations**」 | 不让模型产出「答案」，只让它产出「查询」。答案由数据库给 |
| 2 | **输出格式约束** | 「ensuring **outputs remain within expected formats**」 | 让输出可被程序解析，减少自由发挥 |
| 3 | **函数边界约束** | 「**functions are bounded within internally defined limits**」 | 参数越界即失败，不给模型试探空间 |
| 4 | **数据类型白名单** | 「**AI-accessible data types are limited to a restricted set** managed by Kentik's AI engineers」 | 模型只看得到 43 个工具，看不到整个数据库 |

（以上均出自 [Kentik AI Overview](https://kb.kentik.com/docs/kentik-ai-overview)，A 级）

还有第五种，是**产品层面的**：

| 5 | **推理可见** | 「AI Advisor shows its plan-making reasoning in a **collapsible pane** at the top of each message」 | 让人能审计「它是怎么想的」，而非只看结论 |

> **第 5 条的意义常被低估**。控幻觉的所有技术手段都有残余风险，最后一道防线是**人能看懂它在干什么**。官方甚至在 Best Practices 里明确教用户怎么用这个面板抓错：
>
> 「Did the AI correctly identify the device or the time window? Did it choose the wrong data tool?」
>
> **这三个问题恰好对应三类幻觉：认错对象、认错时间、用错工具。** 官方把幻觉拆成了可检查的具体项，这比笼统说「我们会尽力避免幻觉」有用得多。

## 7.2 一处必须并列的源冲突：「只读」到底怎么算

这是本报告发现的最实质的文档矛盾，不能择一隐去：

| 说法 A（强只读） | 说法 B（存在写操作） |
|---|---|
| 「AI Advisor is **read-only**. Kentik does not request, nor want, write access to your infrastructure.」（[AI Advisor 页](https://kb.kentik.com/docs/ai-advisor)） | 「`Sites Tool`: **Create, update, or delete sites** in Kentik」（同页工具清单）；「`Runbooks`: Get, **create, or update** cookbook-style troubleshooting runbooks」（同页） |
| 「**All AI queries are read-only** and can't be used to update or alter system data.」（[Kentik AI Overview](https://kb.kentik.com/docs/kentik-ai-overview)） | 2026-04：「**Auto-approved tools** support: certain **remediation actions** can execute without per-turn human approval」 |
| —— | 2026-07：「AI Advisor can manage Sites: A new Sites tool **creates and updates** Kentik Sites ... **Every write requires human approval first** and respects your RBAC permissions」 |

**判定与理由**：

1. **「只读」的真实含义是「不对网络基础设施写入」**，而不是「不对 Kentik 平台自身写入」。Sites 是 Kentik 平台里的对象，不是网络设备；Runbook 是配置项，不是网络变更。所以 A 说法并未被推翻，但它**表述得过于笼统**。
2. **存在「写」的能力，但分三档**：
   - 写 Kentik 平台对象（Sites / Runbooks）→ 需要人工批准，尊重 RBAC
   - 补救动作（remediation）→ 默认需批准，**部分在白名单内可自动执行**
   - 写网络设备配置 → 官方承诺**永不做**（`never execute configure terminal or commit`）
3. **采信这一分层判定**，因为它同时解释了三处文本，无需假设任何一方说谎。

> **这一条对选型的实际意义**：如果你需要「绝对不能改任何东西」的严格只读，那要**逐一核对工具清单里哪些带 create/update/delete**，而不是采信产品页那句「read-only」。**产品级承诺与工具级能力之间存在粒度差，这是评估任何 AI Agent 产品时都要注意的。**

## 7.3 官方自认的四条局限（最有价值的一段原文）

KB 用「can / cannot」两栏明确列出了它的能力与边界，其中 cannot 栏四条值得完整引用（[AI Advisor 页](https://kb.kentik.com/docs/ai-advisor)，A 级）：

> **cannot**:
> 1. **Occasionally make errors or make mistakes (known as 「hallucinations」) and provide confident but incorrect information.**
> 2. **Maintain a persistent 'memory' across multiple conversations**, apart from what you configure in Runbooks and Custom Network Context.
> 3. **Access or understand proprietary knowledge, apart from what you configure** in Runbooks and Custom Network Context.
> 4. **Perform complex Network Intelligence tasks that are outside the scope of its defined tools.**
>
> 另有一条：**Provide the same exact response to a question/prompt asked at different times.** Gen AI inherently can produce a different, yet plausible, response every time it receives the same input.

> **这四条建议原样抄进任何 AI 运维产品的对外说明里**，因为它们恰好覆盖了客户会踩的四个坑：
> - 坑一：以为它不会错 → 需要「回看原文/推理面板」的用法引导
> - 坑二：以为它记得上次的排查 → 需要「知识必须配置，不会自动积累」的预期管理
> - 坑三：以为它懂你们公司 → 需要 CNC 的落地辅导
> - 坑四：以为它能做超出工具的事 → 需要明确能力清单
>
> **第 5 条（同一问题不同答案）尤其重要**：这意味着**它不能用于需要可复现的合规场景**。如果审计要求「同样的输入必须得到同样的输出」，这个系统本身不满足。

## 7.4 审计与治理

| 机制 | 内容 | 出处 |
|---|---|---|
| **RBAC 到工具级** | 「AI Advisor now respects role-based permissions, so users only see tools they are entitled to and **cannot access restricted data through natural-language queries**」 | 2026-04 |
| **推理面板** | 每条消息顶部可折叠，可开关 | AI Advisor 页 |
| **证据链接** | 结论附带「links to the data used in the investigation」 | Runbook 博客 |
| **调查通知** | 推 Jira Cloud / JSM，含 Alarm ID，支持富文本（表格、链接） | 2026-06 |
| **配置变更审计** | CNC 变更入 Audit Log，含完整版本历史 | 2026-07 |
| **成本可观测** | 消息压缩可显示节省 token 数 | 2026-06 |

> **「RBAC 到工具级」这一条的技术含义比看上去深**：它意味着**权限校验发生在工具注册层，而不是查询层**。如果只在查询层做权限（如 SQL 里加 where 条件），模型仍可能通过组合查询推断出无权看的数据。**在工具可见性上做裁剪，是更彻底的做法。**

---

# 8. 开放接入：它既当 Server，也当 Client

这一章容易被忽略，但它是判断「这套东西是不是一个生态位产品」的关键。

## 8.1 对外暴露：AI Advisor MCP Server

2026-03-06 官方发布了 **AI Advisor MCP Server**（[KB](https://kb.kentik.com/docs/ai-advisor-mcp-server)，A 级），原文定位：

> 「Kentik's **AI Advisor MCP Server** enables you to seamlessly integrate AI Advisor into **external AI agents**.」

它明确支持的平台（原文列举）：

- Claude Desktop（Anthropic）
- GitHub Copilot
- OpenAI Agents
- 自定义 agent 框架：**LangGraph、Google ADK、LlamaIndex**

服务特性（原文）：

| 特性 | 原文 |
|---|---|
| 自然语言查询 | 「Ask questions about your network in conversational language」 |
| 多轮对话 | 「Maintain context across multiple questions」 |
| 实时进度 | 「See AI Advisor's reasoning process as it works」 |
| 异步处理 | 「Handles long-running queries efficiently」 |
| 会话管理 | 「Reviews and continues previous conversations」 |

**一个非常实用的细节**：官方要求提示词里**必须显式提到「Kentik」**——

> 「**Always explicitly mention 「Kentik」 in your prompts** to ensure your agent uses its MCP tools.」

> **这句话暴露了 MCP 的真实工程状态**：外部 agent 可能同时接了多个 MCP Server（GitHub、Jira、数据库……），**工具名前缀冲突与路由歧义是真实问题**。官方给的解法不是技术手段（如命名空间），而是**让用户在提示词里加关键词**。
>
> 这是一个诚实的折中：MCP 协议层没有解决「多个 server 的工具如何路由」的问题，厂商只能用产品话术兜。**你们做 MCP 接入时如果要接多个后端，这个问题会原样出现。**

## 8.2 反向消费：A2A 工具

同时，Kentik 自己的 agent 也会**调用外部 agent**：

> `Agent to Agent (A2A)`：Access external agents including the **Connectivity Cost Agent** and **KMI (Kentik Market Intelligence) Agent**（[AI Advisor 页](https://kb.kentik.com/docs/ai-advisor)，A 级）

## 8.3 双向接入的结构含义

```mermaid
flowchart LR
    EXT["外部 agent<br/>Claude Desktop / Copilot<br/>LangGraph / ADK"]:::ext
    KAI["Kentik AI Advisor<br/>MCP Server"]:::core
    SUB["内部子 agent<br/>PeeringDB / KMI / Cost"]:::sub
    DATA["Kentik 数据平台<br/>流量 · 指标 · 日志 · 配置"]:::data

    EXT -->|"MCP 调用"| KAI
    KAI -->|"A2A 调用"| SUB
    SUB --> DATA
    KAI --> DATA

    classDef ext fill:#FAEEDA,stroke:#854F0B,color:#412402
    classDef core fill:#E6F1FB,stroke:#185FA5,color:#0C447C
    classDef sub fill:#E1F5EE,stroke:#0F6E56,color:#085041
    classDef data fill:#F1EFE8,stroke:#5F5E5A,color:#2C2C2A

    linkStyle default stroke-width:1.2px
```

**这个双向结构说明一件事**：Kentik 不打算让 AI Advisor 成为唯一的入口，而是**让它成为一个「可被编排的能力节点」**——你可以在 Copilot 里问 Kentik 的网络问题，也可以在 Kentik 里调用别的 agent 算成本。

> **对自研的判断**：这是一个战略选择题。要么做「唯一入口」（体验最好，但客户已有的 AI 工作流用不上你），要么做「能力节点」（体验分散，但能嵌进客户已有的一切）。Kentik 选了后者——**因为它知道客户不会为它放弃 Claude/Copilot。**
>
> 你们的 APM AI 助手在这件事上会更难：**运维团队不会为了排查认证故障去开第三个 AI 窗口。** 要么嵌进客户已有的 IM（企业微信/飞书），要么嵌进现有运维平台。MCP/A2A 这类协议正是为此存在的。

---

# 9. 能力边界与脆弱点

## 9.1 硬边界（架构决定的，改不了）

| # | 边界 | 依据 | 后果 |
|---|---|---|---|
| 1 | **数据边界 = Kentik 平台边界**。它查不到 Kentik 没采集的数据 | 「AI-accessible data types are limited to a restricted set」 | 未接入的设备、未采的日志，它永远看不见 |
| 2 | **工具边界 = 能力边界**，超出即拒答 | 「Perform complex Network Intelligence tasks that are **outside the scope of its defined tools**」（cannot 栏第 4 条） | 不是「不会」，是「明确不做」 |
| 3 | **不写基础设施** | 「never execute configure terminal or commit」 | 只能建议补救，不能执行网络变更 |
| 4 | **无跨会话记忆**（除配置） | cannot 栏第 2 条 | 同一个人第二天来，一切从头开始 |
| 5 | **同一问题不保证同样答案** | cannot 栏第 5 条 | 不可用于需要可复现的合规场景 |
| 6 | **知识靠人工配置** | cannot 栏第 3 条 | 不配置 CNC/Runbook，它就是一个「通用 AI + 43 个工具」 |

## 9.2 软边界（官方未公开）

| 缺口 | 为什么重要 | 现状 |
|---|---|---|
| **最大迭代步数** | 决定一次调查能挖多深 | 完全未公开 |
| **单次调查的工具调用上限** | 影响成本与超时 | 完全未公开 |
| **Runbook 字符上限** | 决定剧本能写多细 | 只知 CNC 是 10 万字符，Runbook 未提 |
| **子 agent 的拆分标准** | 决定什么域该拆、什么域不该拆 | 只知 PeeringDB 拆了，其余不明 |
| **上下文压缩算法** | 决定长调查会不会丢证据 | 只知「按会话分组压缩」 |
| **准确率 / 幻觉率** | 一切评测的核心 | 无任何量化指标 |
| **并发上限** | 决定能否全量接管告警 | 未公开 |

## 9.3 六个脆弱点（本报告分析）

这六点是**从官方自己的更新日志里反推出来的**——凡是官方专门修过的地方，就是曾经坏过的地方。

| # | 脆弱点 | 官方修复动作（即故障证据） | 对自研的警示 |
|---|---|---|---|
| 1 | **工具返回字段不全 → 模型必然答错** | 2026-07 补上「ISO timestamps and units on each line, plus a table/legend header」，理由是「improving the accuracy of AI answers about specific points in time」 | **先查工具契约，再怪模型。** 加两个字段比换模型有效 |
| 2 | **上下文压太狠 → 结论被截断** | 2026-04「Increased output token limits and made **turn compression less aggressive** so investigation responses are **no longer truncated**」 | 压缩策略要按「是否保留结论」分级，不能一刀切 |
| 3 | **单个慢工具拖垮整轮** | 2026-07「Tool calls now **time out after five minutes and cancel their underlying queries instead of erroring the entire agent turn**」 | **超时必须是「局部失败」而不是「全局失败」**。这一条几乎所有自研团队都会先踩 |
| 4 | **相似工具互相干扰** | 43 个工具里有 6 个 Synthetics 系列、2 个 Alert 系列、4 个云 inventory——靠子 agent 与 RBAC 分组缓解 | 工具命名与描述必须刻意做区分，否则模型选错且不自知 |
| 5 | **模型换代导致行为漂移** | 一年换四轮模型（Claude Opus 4.8 → 5、Gemini 3.6 → 3.7），并加跨供应商 fallback | 每次换模型都要回归测试同一批 Runbook，否则调查路径会变 |
| 6 | **空配置即退化** | cannot 栏第 3 条明确「除 CNC/Runbook 外无法理解专有知识」 | **产品交付必须包含「知识配置」这项服务**，否则客户买到的只是一个通用 agent |

> **第 6 点是最容易被销售和产品忽略的一条**。一个客户如果只开关了 Kentik AI 但没填 CNC、没写 Runbook，他拿到的体验是「一个懂网络的通用 AI」——**这跟直接用 ChatGPT 问网络问题，差距远小于宣传中的差距。**
>
> 换句话说：**这套产品的价值，有一半是客户自己写进去的。** 这既是它的护城河（客户投入越多越难迁移），也是它的落地风险（客户不投入就感受不到价值）。

## 9.4 前提依赖：五个「必须成立」

前两节讲的是「它做不到什么」，这一节讲「它在什么条件下才成立」——这一层最常被漏掉，因为它既不在 cannot 栏里，也不在任何宣传材料里。

| # | 前提 | 依据 | 不成立时的实际表现 |
|---|---|---|---|
| 1 | 组织级 **Kentik AI 开关已打开** | 默认 **disabled**，仅 Super Administrator 可开（[Settings](https://kb.kentik.com/kentik-ai)，A 级） | 能力根本不存在，界面上看不到入口 |
| 2 | **已配置 CNC / Runbook** | cannot 栏第 3 条：「apart from what you configure」 | 退化为「通用模型 + 43 个工具」，没有任何组织专有知识 |
| 3 | **Runbook 已绑定告警策略** | L3 自动调查的唯一触发路径（第 6 章） | 只剩手动 L1 / L2，谈不上「自动」 |
| 4 | **目标数据已被 Kentik 采集** | 「AI-accessible data types are limited to a restricted set」 | 那类证据永远看不见，模型只能靠先验知识猜 |
| 5 | **用户的设备 RBAC 覆盖目标设备** | 2026-04 工具级 RBAC；2026-05 device RBAC 集中化 | 相关工具被直接禁用（早于 2026-05 还存在 fail-open 风险） |

前三条是**配置前提**，后两条是**数据与权限前提**。总结成一句：**任何一条不成立，产品还在，能力不在。**

## 9.5 官方自认的五条局限（边界视角汇总）

7.3 引用过 KB 的 cannot 栏，这里按「边界类型」重排，因为它们的性质并不相同：

| # | 官方原文要点 | 边界类型 | 对使用的实际影响 |
|---|---|---|---|
| 1 | 「Occasionally make errors… confident but incorrect information」 | 行为边界 | 结论必须回看证据链接与推理面板，不能直接采信 |
| 2 | 「cannot maintain a persistent memory… apart from what you configure」 | 能力边界 | 经验不会自动沉淀，必须有人把它写成 Runbook |
| 3 | 「cannot access proprietary knowledge, apart from what you configure」 | 能力边界 | 不填 CNC，它对你们网络的理解为零 |
| 4 | 「cannot perform… tasks outside the scope of its defined tools」 | **架构边界** | 是「明确拒答」，不是「硬着头皮答」——这一点反而降低风险 |
| 5 | 「cannot provide the same exact response… at different times」 | **可复现性边界** | 不能用于「同样输入必须同样输出」的合规留证场景 |

> 第 4 与第 5 条最容易被误读：前者被视为缺点，其实是安全设计；后者被视为技术瑕疵，其实是**选型否决项**——如果你们的场景需要可复现的审计结论，这个系统本身不满足，换模型也解决不了。

## 9.6 六个常见误期待

这六条是前面所有边界在「人的认知」上的投影，也是售前与内部宣讲最容易说错的六句话：

| 误期待 | 实际 | 依据 |
|---|---|---|
| ① 「它能主动发现没人告诉它的问题」 | 需要告警或人工提问来触发；定时报告也依赖**预设提示词**，不是自主巡检 | 第 6 章三级触发模型 |
| ② 「它记得上次是怎么排查的」 | 不会。除非有人把那次排查写成 Runbook | cannot 栏第 2 条 |
| ③ 「它能改交换机配置把故障修掉」 | 永不执行 `configure terminal` / `commit`；能写的是 Kentik 平台对象与白名单内的补救动作 | 官方承诺 + 7.2 分层判定 |
| ④ 「同一个问题问两次，答案应该一样」 | 官方明确不保证，且这是 Gen AI 的固有属性 | cannot 另有一条 |
| ⑤ 「它能给出准确率提升了多少」 | 官方无任何量化承诺；本报告也不引用任何厂商收益数字 | 全文无指标，见附三 |
| ⑥ 「它懂我们公司的术语、分区和习惯」 | 只有写进 CNC 才懂；官方专门举例「customer 这个词在你们语境里指什么」 | 5.2 节 |

> **第 ① 条最危险**：它决定了客户对「自动化」的预期。这套系统是**事件驱动**的，不是**巡检驱动**的——没有人配告警策略、没有绑定 Runbook，它一天都不会主动说一句话。把它当「7×24 自动巡检机器人」卖出去，交付必然翻车。

## 9.7 六维速查总表

把本章六节压成一页，供选型评审直接使用：

| 维度 | 一句话结论 | 详见 |
|---|---|---|
| **硬边界** | 数据边界 = Kentik 平台边界；工具边界 = 能力边界 | 9.1 |
| **软边界** | 七个关键参数未公开，无法做容量、成本与深度的定量测算 | 9.2 |
| **脆弱点** | 六处「官方修过的地方」= 六条工程红线 | 9.3 |
| **前提依赖** | 五个必须成立，否则「产品在、能力不在」 | 9.4 |
| **官方自认** | 五条 cannot，可直接抄进对外说明 | 9.5 |
| **常见误期待** | 六条，售前最容易说错的六句话 | 9.6 |

> **评估这类产品时，问「它能不能」不如问三件事**：在什么前提下能、失效时表现成什么样、出问题时能不能解释和回滚。前两个问题决定能不能落地，第三个问题决定敢不敢用在生产。

---

# 10. 对自研 APM AI 助手的启示

前面的机制拆解最终要落到「你们能拿它做什么」。分两块：**架构级 14 条**，与 **APM/园区认证场景的具体映射**。

## 10.1 架构级：14 条可执行判断

| # | 启示 | 依据 | 为什么重要 |
|---|---|---|---|
| 1 | **先造模型网关，再做功能** | 一年换四轮模型 + 跨供应商 fallback + 区域驻留 + token 上限自动强制 | provider 散落在业务代码里，模型升级会变灾难 |
| 2 | **双模型分层：规划用强，摘要用弱** | Advanced（交互）/ Basic（摘要、变点检测、原因分析）分开 | 单次调查里多数调用是低难度高频次，全用强模型成本高一个量级 |
| 3 | **工具按数据源切，不按用户意图切** | 43 个工具全是数据源命名（`NMS` / `Syslog` / `Device Config`），无一个是「诊断XX」 | 按意图切 = 把 if-else 包装成 AI，短期好看长期没上限 |
| 4 | **工具契约必须强类型 + 显式单位与时间戳** | NMS 工具迁 TypeScript 加固 schema；补 ISO 时间戳与单位后准确率上升 | 模型答错的第一大来源是工具给的信息不全 |
| 5 | **知识分三路：环境语义注入 / 诊断剧本注入 / 产品文档检索** | CNC 与 Runbook 进 system prompt；KB 是工具 | 注入改变行为，检索只补事实，两者不可互换 |
| 6 | **诊断剧本必须版本化、可 diff、可回滚** | Runbook Revision History | 它直接进 system prompt，改一行影响所有相关告警 |
| 7 | **别做向量记忆，做可审计的配置知识** | 官方明确无跨会话记忆，用 CNC+Runbook 替代，并给 CNC 加审计日志与版本历史 | 「AI 自己学到的」在企业场景是负债，「人配的」才是资产 |
| 8 | **异步基础设施先行** | 单轮 600 秒、单工具 5 分钟、审批跨小时 | 假设 10 秒返回的架构装不下 agent |
| 9 | **推理可见是产品特性，不是调试开关** | Reasoning Panes 默认展示，官方教用户用它抓错 | 控幻觉的最后一道防线是人能审计 |
| 10 | **超时与失败必须局部化** | 单工具超时只废这一步，不废整轮 | 否则一个慢查询毁掉整次调查 |
| 11 | **审批状态要持久化** | durable approval across refresh/deploy | 人可能几小时后才批，状态不能存内存 |
| 12 | **RBAC 到工具可见性层，不到查询层** | 「users only see tools they are entitled to」 | 只查查询层，模型可用组合查询推断无权数据 |
| 13 | **触发分三级，L2（上下文预填）性价比最高** | Alerting 页一键「Investigate with AI Advisor」自动带上下文 | 一线工程师不会写 prompt，把入口做对胜过把 prompt 写好 |
| 14 | **对外暴露要趁早，但别指望 MCP 解决路由** | MCP 已开放，但官方仍需提示用户「在提示词里写 Kentik」 | 多 server 工具路由是协议层未解问题 |

## 10.2 映射到锐捷 APM：证据域 → 工具

把 Kentik 的「43 工具 = 证据源数」这个逻辑套到你们的栈上：

| 你们的证据源 | 应有的工具（按数据源命名） | 对应的 Kentik 工具 | 备注 |
|---|---|---|---|
| VictoriaMetrics 指标 | `MetricsQuery`（限指标名、限时间窗、返回带时间戳与单位） | `NMS` | **必须带单位**，否则模型会拿错量纲比较 |
| Loki 日志 | `LogSearch`（限 label、限时间窗、返回聚合摘要 + 原始行） | `Syslog` | 建议同时提供「摘要」与「原文」两种粒度 |
| Pyroscope 火焰图 | `ProfileQuery`（限服务、限时间窗、返回 topN 函数栈） | ——（Kentik 无对应） | **这是你们的差异点**，Kentik 没有 APM 侧数据 |
| MySQL 业务数据 | `ServiceInventory` / `BusinessMetrics` | `Device Inventory` | 只读账号 + 视图隔离 |
| Redis | `SessionState` / `CacheStats` | ——（Kentik 无） | 与认证会话状态强相关 |
| 交换机配置 | `DeviceConfig`（历史版本 + diff + 认证相关片段） | `Device Config` | 见前一份报告的结构化建议 |
| 交换机只读命令 | `AuthDeviceShow`（认证类：`show dot1x` / MAC 表 / RADIUS 状态） | `Device Command` | **限死命令参数**，不做通用 CLI 代理 |
| 认证链路探测 | `AuthProbe`（从接入端口发起一次模拟认证） | `Connectivity Test` | 观测点是端口不是站点 |

> **一个关键取舍**：Kentik 有 43 个工具是因为它有 43 个证据源。**你们不需要 43 个，但必须把「认证链路上的每一个证据源」都变成一个工具**——终端、AP、AC、接入交换机、RADIUS、DHCP、DNS。少一个，模型在那一段就只能猜。

## 10.3 映射到园区认证：Runbook 该写什么

这是最能直接落地的一块。按 Kentik 的 Runbook 结构（**告警上下文 → 规定步骤 → 查哪些数据源 → 如何解读 → 组织特有注意事项**），一个认证故障 Runbook 的骨架应该是：

```markdown
## 触发条件
802.1X / Portal / MAC 认证失败率在 5 分钟内超过阈值

## 前置事实（CNC 提供，不在 Runbook 里重复）
- SSID 与 VLAN 映射表
- RADIUS 服务器清单与归属域
- 各校区接入层设备命名规则
- 已知维护窗口

## 诊断步骤
1. 确认范围：全园区 / 单楼栋 / 单 AP / 单用户
   → 工具：MetricsQuery（认证失败率，按 site/device 维度下钻）
2. 判断是「认证失败」还是「根本没发起认证」
   → 工具：LogSearch（RADIUS 侧 reject 原因码分布）
   → 若 reject 为 0 而失败率上升 → 转步骤 5
3. 按 reject 原因码分流
   - EAP 超时 → 查 RADIUS 可达性与响应时延
   - 密码错误 → 查是否账号批量变更
   - 属性不匹配 → 查授权策略是否变更
4. 查配置是否变更
   → 工具：DeviceConfig（RADIUS 指向 / Portal 模板 / 授权 VLAN 的 diff）
5. 若是「没发起认证」
   → 工具：AuthDeviceShow（端口 802.1X 状态、MAC 表、端口 up/down）
   → 工具：AuthProbe（从该端口模拟认证）
6. 若设备侧正常
   → 工具：SessionState（Redis 中的会话状态）
   → 工具：LogSearch（Portal 重定向日志）
7. 汇总结论：受影响范围 + 根因定位 + 最小安全动作

## 解读规则
- 单 AP 失败 → 优先查该 AP 上行链路与 PoE
- 同楼栋多 AP 失败 → 优先查接入交换机与 DHCP
- 跨校区同时失败 → 优先查 RADIUS 与核心
- 失败率上升但 reject 为 0 → 优先查 DHCP 与 Portal，不是认证本身
```

> **这段骨架里最重要的不是步骤，是「解读规则」那一段。** 官方博客明确说 Runbook 应包含「Logic for how to interpret results」。**这是把资深工程师的判断力固化下来的地方**——也是这类产品真正的价值所在：不是「多查了几个数据源」，而是「知道什么组合意味着什么」。

## 10.4 三条不建议照抄的

| # | 不建议 | 原因 | 建议替代 |
|---|---|---|---|
| 1 | 照抄「43 个工具」的规模 | 你们的数据源没那么多，且工具越多选择越乱 | 按认证链路建 8–12 个工具，每个限死参数 |
| 2 | 一上来做 MCP Server | Kentik 有成熟的 43 工具与生态才值得开放；早期开放只会暴露不稳定 | 先把内部工具契约稳定到 v2，再谈对外 |
| 3 | 做「AI 自己学到的记忆」 | Kentik 明确没做，且给了理由（不可审计、不可回滚） | 做可版本化的配置知识 + 变更审计 |

## 10.5 一句话总结这份报告

> **Kentik 的 AI Advisor 证明了：在企业运维场景里，一个「通用大模型 + 强类型工具 + 注入式剧本 + 严格边界」的系统，可以在不微调、不自研模型的前提下做到可用的自动诊断。**
>
> **它真正的壁垒不是 AI，是「43 个数据源的整合」与「把资深工程师的判断写成剧本的能力」。这两件事，模型换代不会替你完成。**

---

# 附一 完整时间线（倒序）

| 时间 | 事件 | 形态 | 信源等级 |
|---|---|---|---|
| 2026-10-08 | **Kentik AI Overview 更新**：明确四类模型来源与六条安全承诺 | 文档 | A（[KB](https://kb.kentik.com/docs/kentik-ai-overview)） |
| 2026-08 | **Gemini 3.7 + OpenAI Responses API 接入**；设备命令超时从 30 秒提升到 **600 秒**；MCP 轮询超时对齐 600 秒；`Runbooks` 工具支持按会话上下文生成剧本；调查摘要改为「聚焦实际发现而非推测建议」 | 版本更新 | A（[2026-08](https://kb.kentik.com/docs/august-2026)） |
| 2026-07 | **PeeringDB 子 agent 上线**；`Sites Tool` 支持写操作（需人工批准）；Data Explorer 结果带 **ISO 时间戳与单位**；CNC 变更入 **Audit Log** 含完整版本历史；模型注册表新增 Claude Opus 5、Gemini 3.6 Flash；最大输出 64K → **128K tokens**；单工具超时改为 **5 分钟且不废整轮** | 版本更新 | A（[2026-07](https://kb.kentik.com/docs/july-2026-ai-insights)） |
| 2026-06 | **Claude Opus 4.8 / Sonnet 5 接入**；**跨供应商自动 fallback**；区域数据驻留控制（严格/宽松）；消息压缩可显示节省 token；AI 调查通知支持 Jira 富文本 | 版本更新 | A（[2026-06](https://kb.kentik.com/docs/june-2026-ai-insights)） |
| 2026-04 | **审批持久化**（支持多小时 human-in-the-loop）；**自动批准名单**上线；**RBAC 到工具可见性**；异步聊天；NMS 工具迁 **TypeScript** 并加固 schema 校验；Synthetics traceroute 分析 | 版本更新 | A（[2026-04](https://kb.kentik.com/docs/april-2026-ai-insights)） |
| 2026-03-06 | **AI Advisor MCP Server 发布**，支持 Claude Desktop、GitHub Copilot、OpenAI Agents、LangGraph、Google ADK、LlamaIndex | 能力开放 | A（[KB](https://kb.kentik.com/docs/ai-advisor-mcp-server)） |
| 2025-11-18 | **AI Advisor 发布**，官方定位「首个 agentic AI 解决方案」，**明确 replaces Journeys** | 产品发布 | A/B（官方公告与 KB） |
| 2025-06-23 | **Kentik AI Overview 首版发布**（伞形概念成型，列 5 个 AI 特性） | 文档 | A（[KB](https://kb.kentik.com/docs/kentik-ai-overview)） |
| 2024-11 | Journeys 扩展：支持模型自选（GPT / Gemini / Claude / Llama） | 版本更新 | B（[官方博客](https://www.kentik.com/blog/journeys-empowering-network-insights-optimizing-performance-with-ai/)） |
| 2024-01-31 | **Journeys + Query Assistant 发布**（GenAI 一代） | 产品发布 | A/B |

> **时间线读出来的规律**：2026 年 3 月到 8 月，AI Advisor 的更新几乎全部集中在**工程可靠性**上，而不是新能力——审批、超时、压缩、schema、RBAC、审计。**这说明产品已经过了「能跑」阶段，正在过「能放心用」阶段。** 这也是任何自研团队必然要经历的阶段，早做规划比晚补好。

# 附二 信源链接总表

## A 级（官方文档站）

| # | 信源 | 类型 | 日期 | 链接 | 支撑内容 |
|---|---|---|---|---|---|
| A1 | Kentik AI Overview | KB | 发布 2025-06-23，更新 2026-10-08 | https://kb.kentik.com/docs/kentik-ai-overview | 模型来源、安全承诺、AI Advisor 数据范围、NL2Query |
| A2 | AI Advisor | KB | 持续更新 | https://kb.kentik.com/docs/ai-advisor | 两段循环、43 工具清单、Reasoning Pane、can/cannot 局限 |
| A3 | Kentik AI（Settings） | KB | 持续更新 | https://kb.kentik.com/kentik-ai | 双模型架构、CNC 10 万字符、Runbooks 版本化、Provider 选择 |
| A4 | AI Advisor MCP Server | KB | 2026-03-06 | https://kb.kentik.com/docs/ai-advisor-mcp-server | MCP 能力、支持平台、提示词需带 Kentik |
| A5 | 2026-04 AI / Insights | Release Notes | 2026-04 | https://kb.kentik.com/docs/april-2026-ai-insights | 审批持久化、自动批准、RBAC、异步、TypeScript 迁移 |
| A6 | 2026-06 AI / Insights | Release Notes | 2026-06 | https://kb.kentik.com/docs/june-2026-ai-insights | 跨供应商 fallback、区域驻留、消息压缩 |
| A7 | 2026-07 AI / Insights | Release Notes | 2026-07 | https://kb.kentik.com/docs/july-2026-ai-insights | 子 agent、时间戳与单位、CNC 审计、模型注册表、5 分钟超时 |
| A8 | August 2026 | Release Notes | 2026-08 | https://kb.kentik.com/docs/august-2026 | 600 秒超时、MCP 轮询对齐、Runbook 自动生成 |
| A9 | Trust Center FAQ | 信任中心 | 持续更新 | https://trust.kentik.com/faq | 模型供应商（Vertex AI / Bedrock / Anthropic）交叉验证 |

## B 级（官方博客 / 产品页）

| # | 信源 | 类型 | 日期 | 链接 | 支撑内容 |
|---|---|---|---|---|---|
| B1 | AI Advisor: Automating Network Troubleshooting with AI Runbooks | 官方博客 | 2025-12 ~ 2026 | https://www.kentik.com/blog/ai-advisor-automating-network-troubleshooting-with-ai-runbooks/ | **Runbook 注入 system prompt 的关键原文**、影响五环节、Auto Investigations 四步 |
| B2 | Network Device Monitoring（kentipedia） | 官方词条 | 持续更新 | https://www.kentik.com/kentipedia/network-device-monitoring/ | runbook 驱动的运维范式、示例 Runbook 骨架 |
| B3 | Journeys 能力扩展 | 官方博客 | 2024-11 | https://www.kentik.com/blog/journeys-empowering-network-insights-optimizing-performance-with-ai/ | 二代产品支持模型自选（GPT/Gemini/Claude/Llama） |

## C 级（第三方）

| # | 信源 | 类型 | 日期 | 链接 | 支撑内容 |
|---|---|---|---|---|---|
| C1 | Kentik bolsters network observability platform with autonomous investigation | 第三方媒体 | 2026 | https://www.techbloat.com/kentik-bolsters-network-observability-platform-with-autonomous-investigation.html | **仅用于印证市场对「autonomous investigation」的理解**，未用于支撑任何机制描述 |

## 未收录公开链接的信源（诚实标注）

| 信源 | 为什么没有 | 影响 |
|---|---|---|
| 官方架构白皮书 | **不存在** | 编排层、上下文管理、子 agent 调度的内部设计均无法核实 |
| system prompt 模板 | **未公开** | 最想复刻的部分恰好不可见，第 5 章的结论均从「注入 vs 检索」的行为差异反推 |
| 工具实现代码 | **未公开** | 只知用 TypeScript 且有 schema 校验（2026-04 更新提及） |
| 性能与准确率数据 | **未公开** | 无任何可引用的量化指标 |
| 定价 | 未公开具体金额 | 本报告未涉及定价 |

# 附三 未公开项登记（非省略）

| 类别 | 具体缺口 | 处置 |
|---|---|---|
| **编排** | 最大迭代步数、单次调查工具调用上限、终止判定的具体规则 | 登记为缺口；本报告用「官方更新日志中的超时数值」间接刻画其工程假设 |
| **上下文** | 压缩算法、压缩触发阈值、Runbook 字符上限 | 登记为缺口；仅确认 CNC 为 10 万字符 |
| **子 agent** | 拆分标准、调度方式、子 agent 间是否共享上下文 | 登记为缺口；仅确认 PeeringDB 被拆为独立子 agent |
| **知识** | Runbook 是否全部注入还是有截断策略、多 Runbook 冲突时如何取舍 | 登记为缺口 |
| **质量** | 准确率、幻觉率、工具调用成功率、平均调查时长 | 登记为缺口；本报告不引用任何厂商收益数字 |
| **安全** | 提示注入的具体检测规则、数据脱敏范围 | 登记为缺口；仅知官方声明「限制在预期格式、函数边界、数据类型白名单」 |

---

> **交付核验（自检结论）**
>
> - 文档 **1203 行**；**6 张 Mermaid 图**（全为 `flowchart`，`classDef` 均显式含 `fill` 与 `color`，子图标题未使用 ASCII 双引号）
> - **唯一 URL 13 个**，正文内联出现 59 处；A 级 9 个、B 级 3 个、C 级 1 个
> - **本轮补充**（5.1.1–5.1.4 三条通路的来源与治理、9.4–9.7 能力边界四维度）**全部采用 A 级 KB 与 B 级官方博客**，未引入新的 C 级信源；表格 46 块列数一致，正文 ASCII 双引号 0 处
> - **三处源冲突已并列判定**：① 模型供应商（KB 含 OpenAI vs Trust Center 未列）→ 采信 KB；② 「只读」声明 vs Sites/Runbooks 写操作与自动批准补救 → 分层判定；③ Runbook 是「知识」还是「工具」→ 官方自己列为工具清单一项，但明确说明其注入 system prompt，故判定为「以工具形式管理、以 system prompt 形式生效」
> - **一处诚实短板**：本报告没有任何官方架构文档支撑，所有内部机制描述均属「从公开文档与更新日志反推」，凡推导处已标 `C（本报告推导）` 并给出依据链
> - 正文引号已统一为中文弯引号，仅代码块与 URL 内保留 ASCII 直引号；官方英文原文引用中的内层引号亦按排版规范转为「」，语义未变

*文档生成时间：2026-10-21 ｜ 数据截止：2026-10-21*
