# 04 - Leader AI 独立事实基线（评审抽检用，第三方交叉核验记录）

- 用途：Leader 在最终评审时用于抽检数据AI-A/B 是否**编造链接或错标日期**的独立参照。
- 来源要求：仅记录**官方域名**（vendor.com / 官方 IR / 官方 newsroom / 官方 GitHub）且已被独立检索命中的条目。
- 状态：持续追加中（本文件不作为报告内容，仅作为评审工具）。

## 交换机/网络侧锚点

| 技术/事件 | 厂商 | 官方锚点 URL | 日期/事实 | 核验状态 |
|---|---|---|---|---|
| Silicon One 可编程交换芯片架构发布 | Cisco | [Cisco Unveils Plan for Building Internet for the Next Decade](https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2019/m12/cisco-unveils-plan-for-building-internet-for-the-next-decade-of-digital-innovation.html) | 2019-12-11 发布 | ✅ 已核验 |
| Silicon One 发展史（含 G200/800G、NVIDIA 合作） | Cisco | [The story of Silicon One](https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2025/m12/the-story-of-silicon-one.html) | 2019 首次发布；2025 回顾（G200 800G、NVIDIA 合作） | ✅ 已核验 |
| Spectrum-X 加速以太网平台（生成式AI） | NVIDIA | [NVIDIA Launches Accelerated Ethernet Platform for Hyperscale Generative AI](https://nvidianews.nvidia.com/news/nvidia-launches-accelerated-ethernet-platform-for-hyperscale-generative-ai) | 单交换机 256×200Gb/s、两层 16,000 端口 | ✅ 已核验 |
| Spectrum-X 客户落地（Meta、Oracle） | NVIDIA | [NVIDIA Spectrum-X Ethernet Switches Speed Up Networks for Meta and Oracle](https://investor.nvidia.com/news/press-release-details/2025/NVIDIA-Spectrum-X-Ethernet-Switches-Speed-Up-Networks-for-Meta-and-Oracle/default.aspx) | 2025 官方新闻稿（含客户名） | ✅ 已核验 |
| Marvis AI Assistant（对话式网络运维） | Juniper | [Marvis AI Assistant Datasheet](https://www.juniper.net/us/en/products/cloud-services/marvis-ai-assistant-datasheet.html) | 官方 datasheet；扩展至 Routing/WAN | ✅ 已核验 |
| Mist AI-Driven Enterprise 演进（首次 AI 驱动网络约 5 年前） | Juniper/Mist | [AI-Driven Enterprise 4.0](https://www.mist.com/ai-driven-enterprise-4-0-unparalleled-user-experiences-from-client-to-cloud/) | 官方博客，回顾 AI 驱动网络起源 | ✅ 已核验 |
| AVA (Autonomous Virtual Assist) 与 agentic AI 扩展 | Arista | [Arista Networks Introduces AI-Driven Network Identity](https://www.arista.com/en/company/news/press-release/17244-pr-20230424) / [Press Releases](https://www.arista.com/en/company/news/press-release/pr-2025) | 2023-04-24 官方新闻稿；2025 扩展 agentic AI | ✅ 已核验 |
| iMaster NCE 自治网络管理控制系统 | 华为 | [iMaster Autonomous Network Management and Control System](https://carrier.huawei.com/en/products/fixed-network/imaster-nce-fbb) | 官方产品页：业界首个融合管理/控制/分析/… | ✅ 已核验 |
| iMaster NCE 自动驾驶网络说明 | 华为 | [iMaster NCE Enables Autonomous Driving Network](https://www.youtube.com/watch?v=c3BJ1NtvDcg) | 官方视频（A 级） | ✅ 已核验 |

## APM/可观测侧锚点

| 技术/事件 | 厂商 | 官方锚点 URL | 日期/事实 | 核验状态 |
|---|---|---|---|---|
| Davis 超模态 AI（预测+因果+生成式 AI 融合） | Dynatrace | [Dynatrace Expanding Davis to Deliver ... Hypermodal AI (IR)](https://ir.dynatrace.com/news-events/press-releases/detail/302/dynatrace-expanding-davis-to-deliver-the-observability-and-security-industrys-first-hypermodal-artificial-intelligence-converging-predictive-causal-and-generative-ai) | Davis 预测/因果 AI 已可用；Davis CoPilot 2023 年内推出；基于 Grail 数据湖仓 | ✅ 已核验 |
| Davis 超模态 AI 新闻稿（公司站） | Dynatrace | [Dynatrace expanding Davis to deliver first hypermodal AI](https://www.dynatrace.com/news/press-release/dynatrace-expanding-davis-hypermodal-ai/) | 同上 | ✅ 已核验 |
| Continuous Profiler（低开销 7×24 代码剖析） | Datadog | [Datadog Releases Continuous Profiler for Low-Overhead ...](https://www.datadoghq.com/about/latest-news/press-releases/continuous-profiler/) | **⚠️ 精确日期：2020-08-11**（页面正文 "August 11, 2020"，Business Wire 发布）。"GA of Continuous Profiler, low-overhead 24x7"，定价 $12/host/月；官方引用客户 **Cvent**（Ian Schell, Site Reliability Architect）。**若数据稿写 2021 或写"2021 年推出"即为 P1 时间错误** | ✅ 已逐字读取核验 |
| Continuous Profiler 产品页 | Datadog | [Continuous Profiler](https://www.datadoghq.com/product/code-profiling/) | 官方产品页 | ✅ 已核验 |
| Arista AVA (Autonomous Virtual Assist) 与 Network Identity | Arista | [Arista Networks Introduces AI-Driven Network Identity](https://www.arista.com/en/company/news/press-release/17244-pr-20230424) | **⚠️ 精确日期：2023-04-24**（页面正文 "April 24, 2023"）。AVA 描述为"codifies real-world network and security operations expertise and leverages **supervised and unsupervised ML models** into an 'Ask AVA' service, a chat-like interface"；CV AGNI 当时为 trials、**Q2 2023 GA**。官方引用客户：**Baptist Healthcare CIO Aaron Miri**。**若把 AVA 首次发布写成 2023-04-24 需注明是"AVA for Network Identity"；AVA 更早的发布需另找官方证据** | ✅ 已逐字读取核验 |
| Watchdog（内置智能分析层） | Datadog | [Watchdog](https://www.datadoghq.com/product/platform/watchdog/) / [docs](https://docs.datadoghq.com/watchdog/) | 持续分析数十亿数据点，面向检测与排障 | ✅ 已核验 |

## 使用方式（写给评审AI）

1. 对数据稿中**每一条 S/A 级链接**，抽检 ≥10 条：确认 (a) 链接可访问、(b) 页面标题与引用描述一致、(c) 页面内确实出现所引用的日期与事实。
2. 若发现链接 404、域名非官方（如 content farm / 二手转载站充当官方）、标题与内容不符 → 记为 **P0 来源造假/失真**，必须修改。
3. 若发现日期与官方页面不符 → 记为 **P1 时间错误**，必须修正并给出官方页面内日期证据。
4. 抽检结论必须写入评审报告，格式：`条目编号 | 链接 | 抽检结果（通过/失败：原因）`。
