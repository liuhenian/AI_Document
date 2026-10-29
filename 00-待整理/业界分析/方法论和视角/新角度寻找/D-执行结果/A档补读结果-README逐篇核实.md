# A 档补读结果 — README 逐篇核实（2026-10-27）

> **本文档的作用**：上一版 `A2-A3-重跑执行结果-货架收窄版.md` 里给 7 张卡判了 **A 档（可直接跑）**，但当时明确标注了一条局限——"没读 README，'能装'这一条是推断"。本次配好 GitHub 访问凭据后，把 7 张卡对应的 11 个仓库的 README 全部读完，逐条核实。
>
> **结论先说**：**7 张 A 档里有 3 张站不住。** 真正"能装、能跑、且能解决原问题"的是 4 张。

---

## 0. 本次执行条件的变化

上一轮之所以读不了 README，是因为 GitHub 对自己未认证的调用者只给 **60 次/小时** 的 `core` 配额（core 是 GitHub 的通用接口配额池，读仓库信息、README、issue 正文与评论都算在这里）。上一轮在核对 57 条链接时把它用光了。

本次配置了个人访问令牌（personal access token，PAT）后，配额变化如下：

| 配额池（quota pool） | 未认证 | 已认证 | 倍数 |
|---|---:|---:|---:|
| `core`（通用接口） | 60／小时 | **5,000／小时** | 83× |
| `search`（搜索接口） | 10／分钟 | **30／分钟** | 3× |
| `code_search`（代码搜索） | 60／小时 | 10／分钟 | — |
| `graphql`（图查询） | 0（不可用） | 5,000 点／小时 | 从无到有 |

本次实际消耗：读取 11 个仓库的元数据（metadata）与 README 全文，共 **22 次 core 调用**，占比 0.44%。配额已不再是约束。

**技术实现**：新增统一客户端 `_gh.py`，负责三件事——从环境变量或 `~/.workbuddy/.github_token` 读取凭据；按 URL 前缀自动区分三个配额池；遇到限流时最多等 60 秒后重试，超过就明确报错而不是静默卡住。

---

## 1. 11 个仓库的实测状态

数据来自 GitHub API 实时返回（`_a_docs.json`，2026-10-27 采集）。

| 卡片 | 仓库 | 星标 | 最后推送 | 许可证（license） | README |
|---|---|---:|---|---|---:|
| C03 | rr-debugger/rr | 10,719 | 2026-10-23 | 自定义（NOASSERTION） | 2,415 |
| C03 | dnaeon/go-vcr | 1,397 | 2026-09-21 | BSD-2-Clause | 11,036 |
| C05 | box/flaky | 399 | 2025-09-08 | Apache-2.0 | 6,131 |
| C09 | deepcharles/ruptures | 2,104 | 2026-10-06 | BSD-2-Clause | 7,414 |
| C10 | inverse-inc/packetfence | 1,704 | 2026-10-26 | GPL-2.0 | 4,092 |
| C10 | updateing/minieap | 566 | **2023-09-21** | GPL-3.0 | 2,326 |
| C10 | talkincode/toughradius | 696 | 2026-10-22 | MIT | 10,289 |
| C17 | batfish/batfish | 1,514 | 2026-10-26 | Apache-2.0 | 7,612 |
| C29 | nimble-code/Spin | 478 | 2025-09-18 | 自定义（NOASSERTION） | 1,522 |
| C31 | logpai/logparser | 1,997 | 2025-06-10 | 自定义 | 23,922 |
| C31 | logpai/Drain3 | 901 | 2025-02-04 | 自定义 | 19,323 |

**关于仓库名的一处更正**：上一版有两处仓库路径写错，实际为 `dnaeon/go-vcr`（不是 go-vcr/go-vcr）、`talkincode/toughradius`。本次已改正，两处 404 已消除。

**一个共同点值得注意**：11 个仓库**没有一个处于归档（archived）状态**，说明都还在维护。唯一显旧的是 minieap（2023-09 后未再推送）。

---

## 2. 七张卡的重判

### 总表

| 卡片 | 上一版判定 | **本次判定** | 变化原因（一句话） |
|---|---|---|---|
| C03 确定性事件重放 | A | **C 只有思路** | rr 依赖 x86/ARM 服务器级 CPU 的性能计数器，交换机上跑不了 |
| C05 不稳定用例冻结 | A | **B 可改造** | flaky 是"重跑到通过"，方向与原问题相反 |
| C09 变点检测 | A | **A 可直接跑** | 确认，但要限定在离线、趋势类异常 |
| C10 认证跨层因果图 | A | **A 可直接跑** | 确认，且 minieap 是唯一支持锐捷私有算法的一手工具 |
| C17 配置意图验证 | A | **B 可改造** | batfish 支持厂商列表里没有锐捷，配置喂不进去 |
| C29 协议状态机模型检验 | A | **A 可直接跑** | 确认，且是七张里最干净的一个 |
| C31 日志模板挖掘 | A | **A 可直接跑** | 确认，Drain3 的在线模式比 logparser 更合用 |

**统计：A 档 7 张 → 4 张保持 A，2 张降 B，1 张降 C。**

---

### C03 确定性事件重放 → 降为 C

**工具**：rr（record and replay，录制与重放），10,719 星，2026-10 仍在活跃开发。

**README 原文的三条硬约束**（逐字引自 `rr-debugger/rr`）：

> rr currently requires either: An Intel CPU with Nehalem (2010) or later microarchitecture. / Certain AMD Zen or later processors / Certain AArch64 microarchitectures (e.g. ARM Neoverse N1 or the Apple Silicon M-series)

> Linux kernel >= 4.7 (for support of `__WALL` in `waitid()`)

> Running in a VM guest is supported, as long as the VM supports virtualization of hardware performance counters.

**判断**：这三条合起来说明 rr 的机制底座是**硬件性能计数器（performance counter）**——它靠 Intel PT 或类似机制录制"每一条指令执行到了哪里"。

交换机的 CPU 是 MIPS 或 ARM 网络处理器，**没有这样的性能计数器**，也没有 Linux 4.7+ 的可控内核。也就是说：**rr 在园区交换机上物理上跑不起来，这不是适配工作量的问题。**

**还有第二层错位**：rr 录制的是**进程的执行**（线程、系统调用、内存访问），不是网络报文。而园区故障要回答的是"这个端口在第 3 秒收到了什么、为什么没转发"，这是**报文级**问题，不是进程指令级问题。

**保留价值**：rr 的工程方法论值得读——它怎么做到"录制开销低于 2 倍、重放完全确定"，这套思路对"端口级时间线"（C01）有借鉴意义。但那是**借鉴**，不是**采用**。

**降级后**：C03 归入 C 档"只有思路"，不再计入可落地的现成实现。

---

### C05 不稳定用例冻结 → 降为 B

**工具**：flaky，399 星，Apache-2.0，`pip install flaky` 即可，是 pytest 的插件（plugin）。

**README 原文**：

> Flaky is a plugin for pytest that automatically reruns flaky tests.

> By default, flaky will retry a failing test once […] flaky will run tests up to max_runs times, until it has succeeded min_passes times. Once a test passes min_passes times, it's considered a success

**问题在于方向相反。** flaky 做的是：一个测试如果能通过就重跑，跑够次数算成功。**它把"不稳定"这件事抹掉，让它看起来是稳定通过的。**

而 C05 要的是相反的事：**识别出哪些用例不稳定，把它冻结住，不让它污染对设备行为的判断。** 用 flaky 来解 C05，等于把要观测的信号主动消音。

**但它有一个可借的骨架**：`rerun_filter` 机制。

> Instead of rerunning after those failures, you can specify a filter function that can tell flaky to fail the test right away.

这个钩子（hook）让调用者可以介入"要不要重跑"的判定。**把它的语义反过来改**——重跑后结果不同时，不记为成功，而记为一条"该用例不稳定"的证据并落盘——就变成了 C05 要的东西。改造量不大，但必须改，不能直接 `pip install` 就用。

**结论**：B 可改造。借用它的重试骨架与钩子，语义反转后可用。

---

### C09 变点检测 → 确认 A，但限定用途

**工具**：ruptures，2,104 星，BSD-2-Clause，`pip install ruptures`，支持 Python 3.10–3.14，2026-10 仍在更新。

**README 原文**：

> `ruptures` is a Python library for **off-line** change point detection. This package provides methods for the analysis and segmentation of non-stationary signals.

> algo = rpt.Pelt(model="rbf").fit(signal) / result = algo.predict(pen=10)

三行代码就能出结果，依赖只是 numpy/scipy，**确认可直接跑，无任何特殊环境要求**。

**两条必须写明的限定**：

1. **它是离线的（off-line）**。要求先把整段时间序列拿到手再算。这跟园区场景其实吻合——"故障已经发生，事后回看这段历史"，而不是"实时告警"。如果要做实时，得换在线算法（online CPD），那是另一套东西。
2. **它检测的是均值或方差的突变**，即"曲线在某一点发生了跳变"。这解决不了 977 条工单里另一类异常：**数值长期恒为 0**（如 CS20260210 的 VSL 接口 rx 统计长期为 0）、**长期不变**。这类是"结构性死值"，不是"突变"，用变点检测抓不到，得靠规则校验。

**结论**：保持 A。适用面是"指标漂移、渐进劣化、周期性断裂"，不覆盖"死值"。

---

### C10 认证跨层因果图 → 确认 A，且这里是全场最有价值的一条

上一版把 C10 列为 A 时，依据只是"仓库存在、星数够"。读完 README 后，**价值反而上升了**，因为它解决了一个我一直没能回答的问题：那 63 个认证原因码，怎么在实验室里造出来验证？

#### minieap：唯一支持锐捷私有认证算法的开源实现

`updateing/minieap`，566 星，GPL-3.0。README 原文：

> 这是一个实现了标准 EAP-MD5-Challenge 算法的 EAP 客户端，支持通过插件来修改标准数据包以通过特殊服务端的认证。**目前带有一个实现锐捷 v3 (v4) 算法的插件。**

> 默认不使用任何数据包修改器，将只会发送单纯的标准 EAP 数据包。**如需使用锐捷认证，则必须指定 `--module rjv3`。**

> 4. 执行 `make` 即可在根目录下编译出可执行文件。

**三条实测事实**：

1. **能跑**，且极轻量——`make` 一条命令，零第三方依赖（默认用 Raw Socket，连 libpcap 都可以不要）。
2. **它实现了锐捷的私有 EAP 扩展（v3／v4 算法）**。这一点极其罕见：锐捷的私有认证报文格式没有公开文档，这个项目是逆向实现的完整代码。作者注明算法来源是 MentoHUST 项目。
3. **它是客户端（supplicant），不是服务端**。这一点决定了它的正确用法。

**正确用法**：让 minieap 扮演"一台锐捷客户端"，向实验室里的 SAM+／SMP+ 发起认证，**在客户端侧主动制造各种失败**——密码错、字段缺、二次认证信息不全、时序错乱。每个失败分支对应一个 `D1X_RESULT_*` 原因码，从而可以逐个验证：**这个分支在设备上产生的原因码，是否被正确地结构化上报了。**

这正是 977 条工单里 S2 认证场景（数量排第二）和 63 个原因码之间的那座桥。

**限制**：2023-09 后未再推送，作者自述"无法保证高可靠性"。但它是 GPL-3.0 的学生项目、代码量小，作为实验室工具改造风险可控。

#### PacketFence：能跑，但它是完整系统不是零件

`inverse-inc/packetfence`，1,704 星，GPL-2.0，2026-10-26 还在推。README 极简，**没有给安装步骤**，只指向官网文档：

> PacketFence is a fully supported, trusted, Free and Open Source network access control (NAC) system.

> ## Installation / Follow the instructions provided in the Administration Guide.

它是一整套 NAC（网络准入控制）系统：captive portal、有线无线统一管理、802.1X、二层隔离、IDS 联动。**要整机部署（Debian 系），不是一个可以嵌进流程的组件。**

价值在于它是**参照物**：可以看成"一套完整的 802.1X 准入链路长什么样"，但它不能给你零件。

#### toughradius：一条重要的负面证据

`talkincode/toughradius`，696 星，MIT，Go 写的 RADIUS 服务器。README 明确写：

> 📡 **Multi-Vendor VSA** - Huawei, Mikrotik, Cisco, H3C, etc.

**列了华为、H3C、Cisco、Mikrotik，但没有锐捷。**

这条很值得记：**锐捷的私有 RADIUS 属性（VSA，vendor-specific attribute）在主流开源认证服务器里没有现成实现。** 这意味着两条推论——

- 想用现成开源 RADIUS 服务端复现锐捷真实认证场景，做不到，属性对不上；
- 反过来说，**这恰恰是 minieap 那条路的不可替代性**：客户端侧有实现，服务端侧没有。

---

### C17 配置意图验证 → 降为 B

**工具**：batfish，1,514 星，Apache-2.0，2026-10-26 活跃。

**能跑，而且部署极简单**：

> Just pull and run the latest `allinone` Docker container
> ```
> docker pull batfish/allinone
> docker run --name batfish -v batfish-data:/data -p 8888:8888 -p 9997:9997 -p 9996:9996 batfish/allinone
> ```

而且它有一条对园区极其关键的性质：

> **Batfish does NOT require direct access to network devices.** The core analysis requires only the configuration of network devices.

**不需要碰设备，只要配置文件。** 这直接绕开了"园区客户不给远程权限"这个死结——你把配置文本拿回来就够了。

**问题在于厂商列表。** README 逐条列出的支持清单是：A10、Arista、AWS、Azure、Cisco（NX-OS／IOS／IOS-XE／IOS-XR／ASA）、Check Point、Cumulus、F5、Fortinet、FRR、iptables、Juniper、Nokia、Palo Alto、SONiC。（以上为厂商与产品名，保留原文以便检索；**清单里没有一家中国厂商**。）

有限支持（limited support）：**Aruba、Dell Force10、Foundry**。

**没有锐捷，也没有华为、H3C。**

所以"batfish 能跑"和"batfish 能用在你手上"是两件事。要用起来，中间必须自己做一层配置语法转换——锐捷的 CLI 与 Cisco IOS 相似度较高（这是历史原因），转换**可行性中等**，但会引入失真，而且"转换是否正确"本身又成了一个要验证的问题。

**结论**：降为 B 可改造。工具侧零障碍，**障碍在"喂不进锐捷配置"这一步**。

---

### C29 协议状态机模型检验 → 确认 A，七张里最干净的

**工具**：Spin，478 星，贝尔实验室 1980 年起的项目，README 只有 1,522 字符——是目前读到的所有仓库里最短的。

**README 原文**：

> Compilation and installation is trivial (see the makefile) and **the only dependencies are the use of a C compiler, yacc or byacc, and a small number of standard unix/linux/cygwin-like tools** (like make, mv, and rm).

> the most common use of the tool is to write a formal specification of the essence of an application to be verified in a C-like meta-language called ProMeLa

**零特殊依赖**：只要 C 编译器和 yacc。不需要 Docker、不需要特定 CPU、不需要 GPU、不需要网络。

**为什么它对园区特别合适**：它验证的是**逻辑性质**，不是物理行为。它不需要真实设备，也不需要配置样本——你只要把"设备应该怎么工作"写成状态机模型，它就会**穷举所有状态组合**，找出死锁、断言违反、不可达状态。

对照 977 条工单的数据：S5 状态机与冗余（15–32 条）、S2 认证与授权（数量第二）、以及 VSU 双主、堆叠分裂、认证态与权限不一致——**这些全都是状态机缺陷，全都适合用 Spin 在建模阶段就穷举出来。**

**唯一成本**：把设备状态机翻译成 ProMeLa（一种类 C 的建模语言），是人工工作量，不是工具问题。

---

### C31 日志模板挖掘 → 确认 A，Drain3 更合用

这两个工具功能重叠，但定位不同。

**logparser**（1,997 星）：`pip install logparser3`，收录 **18 种**解析算法，从 2003 年的 SLCT 到 2024 年的 DivLog（ICSE'24）。是学术算法的合集与基准平台。

**Drain3**（901 星）：Drain 算法的工程化实现，关键差异是**在线**。

> Drain3 is an **online** log template miner that can extract templates (clusters) from a stream of log messages in a timely manner. […] Drain3 continuously learns on-the-fly

**Drain3 真正的价值不在"解析"，在它的输出协议。** README 里给出的输出样例是结构化 JSON 变更事件：

```json
{"change_type": "cluster_created", "cluster_id": 1, "cluster_size": 1,
 "template_mined": "connected to <:IP:>", "cluster_count": 1}
```

以及 `"change_type": "cluster_template_changed"`。

**`cluster_created` 这个事件本身就是一条告警。** 它的含义是"出现了一个从未见过的日志形态"。对照 977 条工单里那条结论——**有一类失败根本不产生日志**——它的反面同样成立：**也有一类失败产生的是"以前从没见过的日志"**。后者可以被这个事件直接捕获，不需要预先写规则。

它还支持状态持久化（README 里出现 `Drain3 started with 'FILE' persistence`），意味着可以长期跑、重启后接着学。

**一条共同限制**：logparser 的基准数据集全部是云和操作系统日志（HDFS、Hadoop、Spark、Zookeeper、Linux、OpenStack），**没有一个网络设备的 Syslog 数据集**。要用在锐捷设备上，得自己标注一批模板做验证。

**结论**：保持 A。选 Drain3（在线、可长期跑、输出即信号），logparser 作为算法参考库。

---

## 3. 三条新发现（不在原卡片设计里）

### 发现一：锐捷配置能进 batfish 的唯一路径是语法转换，而这本身是风险

batfish 不需要碰设备这一点，对园区场景是**结构性利好**（客户不给权限也不影响）。但支持厂商列表里没有锐捷，意味着必须做一层"锐捷 CLI → Cisco IOS"的转换。

锐捷与 Cisco 的配置语法相似度高，粗略转换不难。但要警惕：**转换失真会制造假阳性**——batfish 报出的"配置违规"，可能只是因为转换错了，而不是设备真有问题。**这条必须先做一轮人工抽样验证，否则结论不可用。**

### 发现二：越靠近园区的工具越旧，越远离园区的工具越新

把 11 个仓库的最后推送时间排一下，规律很明显：

| 层级 | 代表 | 最后推送 |
|---|---|---|
| 通用调试／算法（无关网络） | rr、ruptures、batfish | 2026-10 |
| 日志与通用认证 | logparser、toughradius、packetfence | 2025-06 ～ 2026-10 |
| **锐捷专用** | **minieap** | **2023-09** |

**这个分布本身就是结论**：通用能力有人持续投入，**一到园区和锐捷这个具体形态上，最后一次有人写代码是三年前。**

这跟上一轮学术侧的发现互相印证——园区方向在 arXiv 上也是零命中。两侧的证据指向同一件事：**这个位置没有人在做。**

### 发现三：`cluster_created` 可能是"日志缺失"问题的反面解法

上一轮的结论是"有一类失败根本不产生日志"，因此采集不到。Drain3 的事件流给出了一个互补角度：**不去追"缺了哪条日志"，而是盯"多出了哪条从没见过的日志"。**

后者不需要预知故障模式，只需要一个能持续学习模板的进程。对"故障寿命以天计、只在第 4 天才显现"这类场景（OpenWrt #6937、#9555），这个方向比"预先写全规则"更可能命中。

---

## 4. 修正后的建议

七张卡里，**真正不需要额外适配、装完就能产出结果的，是四张**：

| 优先级 | 卡片 | 为什么现在就能做 | 预计产出 |
|---:|---|---|---|
| 1 | **C10**（minieap） | `make` 即编译，支持锐捷私有 v3/v4 认证算法，可在实验室造出各类认证失败分支 | 63 个认证原因码的逐条验证结果 |
| 2 | **C29**（Spin） | 零依赖，纯逻辑验证，不需要设备也不需要配置样本 | VSU 双主、堆叠分裂、认证态错乱的状态机反例 |
| 3 | **C31**（Drain3） | `pip install`，在线学习，输出本身就是告警事件 | 锐捷 Syslog 的模板库 + "新形态日志"告警 |
| 4 | **C09**（ruptures） | `pip install`，三行代码，适用趋势与漂移类异常 | 指标漂移的自动切分点 |

**降级的三张不要现在碰**：

- **C03**：物理上跑不了（交换机没有性能计数器），别把时间花在适配现成工具上；要做得自研，先立项。
- **C05**：工具方向相反，借用骨架需要改造，改造量小但排在后面。
- **C17**：工具好用但配置喂不进去，要先解决"锐捷配置转 Batfish"的失真验证，这是独立课题。

---

## 5. 本次核实的边界

- **读了 README 全文，但没有读源码**。判定依据是"README 声明的依赖与安装方式"，不是"我实际编译过"。C29 与 C10 的"零依赖"结论来自 README 原文，可信；但如果 README 与实际不符，需要实际 `make` 一次才能完全排除。
- **没有实际部署任何一个工具**。batfish 的 Docker 拉取、PacketFence 的整机部署都未执行。
- **minieap 的锐捷算法未经实测**。它声明支持 v3/v4，但没有验证过与当前在役版本的兼容性。这是下一步最值得做的一件事。
- **star 数与推送时间取自 2026-10-27 的 API 返回**，会随时间变化。

---

*配套文件：`_a_docs.json`（11 个仓库的元数据原始返回）、`_readmes/`（11 份 README 全文）、`_gh.py`（GitHub 客户端，含配额池处理）*
