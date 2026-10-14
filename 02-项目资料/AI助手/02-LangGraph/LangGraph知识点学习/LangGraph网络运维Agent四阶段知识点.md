# 1 LangGraph 网络运维 Agent 四阶段知识点

> 场景目标：用 LangGraph 构建面向网络运维的 Agent，从单实体查询逐步演进到跨实体关联、复杂聚合、开放式诊断与安全操作。
>
> 参考：LangGraph 官方文档中，`StateGraph` 是围绕共享状态组织节点和边的核心图 API；节点读取当前状态并返回部分状态更新，边决定下一步执行；持久化能力通过 checkpointer 保存线程级状态，通过 store 保存跨线程长期记忆；人在回路依赖持久化能力暂停并恢复执行。
>
> 官方资料：
> - [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api)
> - [StateGraph Reference](https://reference.langchain.com/python/langgraph/graph/state/StateGraph)
> - [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
> - [Human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)

## 1.1 总体阶段划分

| 阶段  | 能力目标           | 典型问题                              | 主要 LangGraph 能力                              |
| --- | -------------- | --------------------------------- | -------------------------------------------- |
| 阶段一 | 单实体、单维度查询      | “核心交换机 CoreSW-01 的 CPU 利用率是多少？”   | StateGraph、节点、条件边、工具定义、function calling、基础状态 |
| 阶段二 | 跨实体、上下文关联      | “刚才查了 CoreSW-01，那它的 Gi1/0/1 端口呢？” | 状态持久化、多步工具编排、消息裁剪、结构化输出                      |
| 阶段三 | 时间、空间、复合条件聚合查询 | “对比 CoreSW-01 今天和昨天的 CPU 峰值”      | 高级工具设计、复杂条件解析、后处理、可视化接口、错误降级                 |
| 阶段四 | 开放式诊断、规划、操作意图  | “研发中心网络很卡，帮我分析原因”                 | 多 Agent、子图、RAG、人在回路、可观测性                     |

---

# 2 第一阶段：单实体/单维度查询

## 2.1 LangGraph 基础

### 2.1.1 StateGraph

**知识点说明**

`StateGraph` 是 LangGraph 的核心建模方式。可以把它理解为“以状态为中心的工作流图”：

- `State`：一次对话或一次任务执行期间共享的数据结构。
- `Node`：读取 `State`，执行一段逻辑，然后返回对 `State` 的局部更新。
- `Edge`：决定节点之间的执行顺序。
- `Conditional Edge`：根据当前状态动态选择下一步节点。

在网络运维查询中，`State` 通常保存这些信息：

- 用户原始问题。
- 识别出的意图，例如 `device_metric_query`、`port_stat_query`、`log_query`。
- 抽取出的参数，例如设备名、端口名、时间范围。
- 工具调用结果。
- 最终回答。

**适用阶段**

阶段一的核心是把自然语言问题转换成“可执行查询”。`StateGraph` 负责把“意图识别 -> 参数抽取 -> 工具选择 -> 查询执行 -> 答案生成”串起来。

**例子**

用户问：

> 核心交换机 CoreSW-01 的 CPU 利用率是多少？

对应的状态可以设计为：

```python
from typing import Literal, TypedDict

class NocQueryState(TypedDict, total=False):
    user_id: str
    question: str
    intent: Literal["device_metric_query", "port_stat_query", "log_query", "unknown"]
    device_name: str
    port_name: str
    time_range: str
    query_language: Literal["promql", "logql", "sql"]
    query_text: str
    tool_result: dict
    answer: str
```

一次执行后，状态可能变成：

```json
{
  "user_id": "u-1001",
  "question": "核心交换机 CoreSW-01 的 CPU 利用率是多少？",
  "intent": "device_metric_query",
  "device_name": "CoreSW-01",
  "time_range": "now",
  "query_language": "promql",
  "query_text": "avg(device_cpu_usage_percent{device='CoreSW-01'})",
  "tool_result": {"value": 42.7, "unit": "%"},
  "answer": "CoreSW-01 当前 CPU 利用率为 42.7%。"
}
```

---

### 2.1.2 不同用户和 State 的关系

**知识点说明**

在 LangGraph 中，`State` 表示一次图运行过程中的共享上下文。不同用户不应该共享同一个运行上下文，否则会出现数据串扰，例如：

- A 用户刚查了 `CoreSW-01`。
- B 用户追问“它的 Gi1/0/1 呢？”
- 如果状态没有用户隔离，B 用户的“它”可能错误指向 A 用户查过的设备。

因此需要区分三个层次：

| 层次 | 作用 | 例子 |
| --- | --- | --- |
| `user_id` | 标识真实用户 | `alice`, `ops_zhangsan` |
| `thread_id` | 标识一条对话线程 | `alice-session-20260630-001` |
| `State` | 当前线程的任务上下文 | 最近查询设备、端口、工具结果 |

**设计原则**

- 同一个用户可以有多个 `thread_id`，例如多个浏览器标签页或多个工单。
- 上下文追问依赖 `thread_id`，不是只依赖 `user_id`。
- 长期偏好或用户权限可以放在跨线程 store 中。
- 当前对话的短期记忆放在 checkpointer 管理的线程状态中。

**例子**

A 用户线程：

```json
{
  "user_id": "alice",
  "thread_id": "thread-alice-001",
  "last_device": "CoreSW-01"
}
```

B 用户线程：

```json
{
  "user_id": "bob",
  "thread_id": "thread-bob-001",
  "last_device": "FW-Edge-01"
}
```

当 Bob 问：

> 它的 Gi1/0/1 端口呢？

系统应该从 `thread-bob-001` 中解析“它”是 `FW-Edge-01`，而不是 Alice 的 `CoreSW-01`。

---

### 2.1.3 如何在代码中实现用户隔离

**知识点说明**

用户隔离一般通过 `configurable.thread_id` 实现。调用图时，每个用户会话传入不同的 `thread_id`。如果需要长期记忆，再把 `user_id` 作为 store 的命名空间或 key 的一部分。

**核心做法**

1. 前端或网关生成稳定的 `thread_id`。
2. 每次调用 graph 时带上 `thread_id`。
3. State 中显式保存 `user_id`、`tenant_id`、`permissions`。
4. 工具执行前校验用户权限和租户边界。

**例子**

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

checkpointer = InMemorySaver()

builder = StateGraph(NocQueryState)

def parse_question(state: NocQueryState) -> dict:
    # 实际项目中这里通常调用 LLM 做意图识别和参数抽取
    return {
        "intent": "device_metric_query",
        "device_name": "CoreSW-01",
        "time_range": "now",
    }

def run_metric_query(state: NocQueryState) -> dict:
    device = state["device_name"]
    return {
        "query_language": "promql",
        "query_text": f"avg(device_cpu_usage_percent{{device='{device}'}})",
        "tool_result": {"value": 42.7, "unit": "%"},
    }

def render_answer(state: NocQueryState) -> dict:
    value = state["tool_result"]["value"]
    return {"answer": f"{state['device_name']} 当前 CPU 利用率为 {value}%."}

builder.add_node("parse_question", parse_question)
builder.add_node("run_metric_query", run_metric_query)
builder.add_node("render_answer", render_answer)

builder.add_edge(START, "parse_question")
builder.add_edge("parse_question", "run_metric_query")
builder.add_edge("run_metric_query", "render_answer")
builder.add_edge("render_answer", END)

graph = builder.compile(checkpointer=checkpointer)

result = graph.invoke(
    {
        "user_id": "alice",
        "question": "核心交换机 CoreSW-01 的 CPU 利用率是多少？",
    },
    config={"configurable": {"thread_id": "alice-noc-session-001"}},
)
```

这个例子中，`thread_id` 决定了当前会话的状态隔离边界。

---

### 2.1.4 节点

**知识点说明**

节点是 LangGraph 中真正执行工作的单元。一个节点可以是：

- 普通 Python 函数。
- 调用 LLM 的函数。
- 调用外部工具的函数。
- 调用数据库、指标平台、日志平台的函数。
- 一个完整 Agent 的封装。

阶段一建议把节点设计得小而清晰：

| 节点 | 职责 |
| --- | --- |
| `intent_classifier` | 判断用户要查设备状态、端口统计、日志还是资产信息 |
| `parameter_extractor` | 抽取设备名、端口名、时间范围 |
| `query_builder` | 生成 PromQL、LogQL 或 SQL |
| `tool_executor` | 调用 VictoriaMetrics、Loki、MySQL |
| `answer_renderer` | 把结果转成自然语言回答 |

**例子**

用户问：

> 端口 Gi1/0/23 最近 1 小时有丢包吗？

可以拆成以下节点：

```python
def classify_intent(state: NocQueryState) -> dict:
    return {"intent": "port_stat_query"}

def extract_params(state: NocQueryState) -> dict:
    return {
        "device_name": "CoreSW-01",
        "port_name": "Gi1/0/23",
        "time_range": "last_1h",
    }

def build_port_loss_promql(state: NocQueryState) -> dict:
    return {
        "query_language": "promql",
        "query_text": (
            "increase(if_out_discards_total"
            "{device='CoreSW-01', interface='Gi1/0/23'}[1h])"
        ),
    }
```

节点越清晰，后续排错和扩展越容易。例如要支持“查接口错误包”，只需要扩展 `query_builder` 或新增一个查询节点。

---

### 2.1.5 agent 和节点之间的关系

**知识点说明**

Agent 和节点不是同一层概念：

- 节点是 LangGraph 的执行单元。
- Agent 是一个具备推理、工具选择、行动能力的逻辑角色。
- 一个 Agent 可以被封装成一个节点。
- 一个节点也可以只是普通函数，不一定是 Agent。
- 一个图中可以有多个 Agent 节点，也可以完全没有 Agent 节点。

在阶段一，推荐先使用“确定性节点 + 少量 LLM 节点”的方式，而不是把所有事情都交给一个大 Agent。

**例子**

以下两种设计都可以：

方案 A：普通节点风格。

```text
parse_question -> build_query -> run_tool -> answer
```

方案 B：把工具选择能力封装成 Agent 节点。

```text
parse_question -> metric_agent_node -> answer
```

`metric_agent_node` 内部可能会判断：

- CPU 利用率：调用 `query_victoriametrics`。
- 端口丢包：调用 `query_victoriametrics`。
- 端口日志：调用 `query_loki`。

示例代码：

```python
def metric_agent_node(state: NocQueryState) -> dict:
    question = state["question"]

    if "CPU" in question or "cpu" in question:
        return {
            "intent": "device_metric_query",
            "query_language": "promql",
            "query_text": "avg(device_cpu_usage_percent{device='CoreSW-01'})",
        }

    if "丢包" in question:
        return {
            "intent": "port_stat_query",
            "query_language": "promql",
            "query_text": (
                "increase(if_out_discards_total"
                "{device='CoreSW-01', interface='Gi1/0/23'}[1h])"
            ),
        }

    return {"intent": "unknown"}
```

==阶段一的建议是：先让 Agent 负责“理解和选择”，让确定性节点负责“查询和校验”。==

---

### 2.1.6 条件边

**知识点说明**

条件边用于根据当前状态选择下一步节点。它非常适合阶段一的意图分流：

- 查设备指标 -> VictoriaMetrics 查询节点。
- 查日志 -> Loki 查询节点。
- 查资产或拓扑 -> MySQL 查询节点。
- 参数缺失 -> 追问节点。
- 意图不明 -> 澄清节点。

**例子**

```python
def route_by_intent(state: NocQueryState) -> str:
    if state.get("intent") == "device_metric_query":
        return "metric_query"
    if state.get("intent") == "port_stat_query":
        return "metric_query"
    if state.get("intent") == "log_query":
        return "log_query"
    if state.get("intent") == "asset_query":
        return "sql_query"
    return "clarify"

builder.add_conditional_edges(
    "parameter_extractor",
    route_by_intent,
    {
        "metric_query": "query_victoriametrics",
        "log_query": "query_loki",
        "sql_query": "query_mysql",
        "clarify": "ask_clarification",
    },
)
```

当用户问“CoreSW-01 最近有没有 OSPF flap 日志？”时，状态中的 `intent` 会变成 `log_query`，条件边会路由到 `query_loki`。

---

## 2.2 工具定义

**知识点说明**

工具是 Agent 与外部系统交互的边界。网络运维 Agent 常见工具包括：

| 工具 | 数据源 | 用途 |
| --- | --- | --- |
| `query_metrics` | VictoriaMetrics | 查 CPU、内存、端口流量、丢包、错误包 |
| `query_logs` | Loki | 查设备日志、认证日志、无线漫游日志 |
| `query_inventory` | MySQL | 查设备、端口、终端、拓扑、位置 |
| `normalize_interface` | 本地函数 | 统一端口命名，例如 `G1/0/1` -> `Gi1/0/1` |
| `resolve_time_range` | 本地函数 | 把“最近 1 小时”“今天”解析成时间戳 |

工具定义的关键是参数要明确、返回值要结构化、错误要可处理。

**例子**

```python
from typing import Literal
from pydantic import BaseModel, Field

class MetricsQueryInput(BaseModel):
    query: str = Field(description="PromQL 查询语句")
    start: int | None = Field(default=None, description="开始时间 Unix 时间戳")
    end: int | None = Field(default=None, description="结束时间 Unix 时间戳")
    step: str | None = Field(default=None, description="查询步长，例如 1m")

class MetricsQueryResult(BaseModel):
    source: Literal["victoriametrics"]
    query: str
    series: list[dict]
    is_partial: bool = False

def query_metrics(args: MetricsQueryInput) -> MetricsQueryResult:
    # 实际项目中这里调用 VictoriaMetrics HTTP API
    return MetricsQueryResult(
        source="victoriametrics",
        query=args.query,
        series=[{"metric": {"device": "CoreSW-01"}, "value": [1719715200, "42.7"]}],
    )
```

对于问题“核心交换机 CoreSW-01 的 CPU 利用率是多少？”，Agent 最终调用：

```json
{
  "query": "avg(device_cpu_usage_percent{device='CoreSW-01'})"
}
```

---

## 2.3 function calling

**知识点说明**

function calling 是让模型以结构化方式选择工具并提供参数的机制。它解决阶段一的三个关键问题：

- 意图识别：模型判断该用哪个工具。
- 参数提取：模型输出设备名、端口名、时间范围。
- 查询翻译：模型把自然语言翻译成 PromQL、LogQL 或 SQL。

注意：function calling 不等于直接信任模型生成的查询。生产环境中应该增加：

- 参数白名单。
- SQL 只读限制。
- PromQL 模板化。
- 设备名和端口名规范化。
- 权限校验。

**例子**

用户问：

> 端口 Gi1/0/23 最近 1 小时有丢包吗？

模型不应该只输出自然语言，而应输出类似工具调用：

```json
{
  "tool_name": "query_metrics",
  "arguments": {
    "query": "increase(if_out_discards_total{device='CoreSW-01', interface='Gi1/0/23'}[1h])"
  }
}
```

更稳妥的方式是让模型只抽取结构化意图，不直接写完整 PromQL：

```json
{
  "intent": "port_packet_loss_query",
  "device_name": "CoreSW-01",
  "port_name": "Gi1/0/23",
  "time_range": "last_1h",
  "metric": "out_discards"
}
```

然后由代码模板生成 PromQL：

```python
def build_packet_loss_query(device: str, port: str, window: str) -> str:
    return (
        "increase(if_out_discards_total"
        f"{{device='{device}', interface='{port}'}}[{window}])"
    )
```

这种方式可控性更强。

---

## 2.4 基础 Prompt 工程

**知识点说明**

阶段一的 Prompt 重点不是让模型“自由分析”，而是让模型稳定完成三个动作：

1. 识别意图。
2. 抽取参数。
3. 输出结构化结果。

基础 Prompt 应该明确：

- 当前 Agent 的角色。
- 可用工具和适用场景。
- 支持的数据源。
- 输出 JSON schema。
- 参数缺失时必须澄清，不能编造。
- 设备名、端口名、时间范围必须原样保留或规范化后输出。

**例子**

```text
你是网络运维查询 Agent。
你的任务是把用户问题解析为结构化查询意图。

只允许输出 JSON，不要输出解释文字。

可选 intent：
- device_metric_query：查询设备级指标，例如 CPU、内存、在线状态
- port_stat_query：查询端口统计，例如流量、丢包、错误包
- log_query：查询日志
- inventory_query：查询资产、端口、终端、拓扑
- unknown：无法判断

如果缺少必要参数，missing_fields 中列出缺失字段。

输出格式：
{
  "intent": "...",
  "device_name": "...",
  "port_name": "...",
  "time_range": "...",
  "missing_fields": []
}
```

输入：

```text
端口 Gi1/0/23 最近 1 小时有丢包吗？
```

输出：

```json
{
  "intent": "port_stat_query",
  "device_name": null,
  "port_name": "Gi1/0/23",
  "time_range": "last_1h",
  "missing_fields": ["device_name"]
}
```

此时图应该路由到澄清节点，询问用户端口属于哪台设备，或者尝试从上下文补全设备。

---

## 2.5 简单的状态管理

**知识点说明**

阶段一的状态管理不需要复杂记忆，重点是让一次查询的关键中间结果可追踪：

- 原始问题。
- 解析出的意图。
- 参数。
- 查询语句。
- 工具结果。
- 最终答案。
- 错误信息。

建议把状态设计成“可审计”的，而不是只保存消息列表。这样后续可以做日志追踪、失败重试、工具结果复用。

**例子**

一次查询的完整状态流转：

```json
{
  "question": "CoreSW-01 的 CPU 利用率是多少？",
  "intent": "device_metric_query",
  "device_name": "CoreSW-01",
  "time_range": "now",
  "query_language": "promql",
  "query_text": "avg(device_cpu_usage_percent{device='CoreSW-01'})",
  "tool_result": {"value": 42.7, "unit": "%"},
  "answer": "CoreSW-01 当前 CPU 利用率为 42.7%。",
  "error": null
}
```

如果查询失败，状态可以变成：

```json
{
  "question": "CoreSW-01 的 CPU 利用率是多少？",
  "intent": "device_metric_query",
  "device_name": "CoreSW-01",
  "query_language": "promql",
  "query_text": "avg(device_cpu_usage_percent{device='CoreSW-01'})",
  "tool_result": null,
  "error": {
    "code": "METRICS_TIMEOUT",
    "message": "VictoriaMetrics 查询超时"
  }
}
```

然后由条件边路由到降级回答节点，例如返回“指标平台暂时超时，建议稍后重试或查看近 5 分钟缓存值”。

---

# 3 第二阶段：跨实体/上下文关联

## 3.1 状态持久化

**知识点说明**

阶段二开始出现追问和上下文引用，例如“它”“刚才那个设备”“这个端口”。这要求 Agent 能记住上一轮结果。

LangGraph 的持久化可以分为两类：

| 类型 | 作用 | 网络运维例子 |
| --- | --- | --- |
| Checkpointer | 保存某个 `thread_id` 的图状态 | 当前对话最近查过的设备、端口、时间范围 |
| Store | 保存跨线程长期数据 | 用户偏好、默认园区、常用设备组、权限范围 |

**例子**

第一轮：

> 查 CoreSW-01 的 CPU。

状态保存：

```json
{
  "last_device": "CoreSW-01",
  "last_intent": "device_metric_query",
  "last_time_range": "now"
}
```

第二轮：

> 那它的 Gi1/0/1 端口呢？

解析时从持久化状态补全：

```json
{
  "device_name": "CoreSW-01",
  "port_name": "Gi1/0/1",
  "intent": "port_stat_query"
}
```

调用图时保持同一个 `thread_id`：

```python
config = {"configurable": {"thread_id": "ops-user-001-ticket-8848"}}

graph.invoke(
    {"question": "查 CoreSW-01 的 CPU。", "user_id": "ops-user-001"},
    config=config,
)

graph.invoke(
    {"question": "那它的 Gi1/0/1 端口呢？", "user_id": "ops-user-001"},
    config=config,
)
```

---

## 3.2 多步工具编排

**知识点说明**

跨实体查询通常不是一次工具调用能完成的。Agent 需要根据中间结果继续调用下一个工具。

典型链路：

```text
设备名 -> 设备 ID -> 端口列表 -> MAC 表 -> 终端信息 -> 回答
```

LangGraph 适合把每一步建成节点，并在状态中携带中间结果。

**例子**

用户问：

> 查一下连接在 SW-Access-F2-Finance 上的所有终端。

执行步骤：

1. 查询设备表，得到 `device_id`。
2. 查询端口表，得到该交换机所有接入口。
3. 查询 MAC 地址表，得到端口上的 MAC。
4. 查询终端表，得到 IP、主机名、用户、厂商。
5. 汇总输出。

状态示例：

```json
{
  "device_name": "SW-Access-F2-Finance",
  "device_id": 2031,
  "ports": ["Gi1/0/1", "Gi1/0/2", "Gi1/0/3"],
  "mac_entries": [
    {"port": "Gi1/0/1", "mac": "00:11:22:33:44:55"},
    {"port": "Gi1/0/2", "mac": "66:77:88:99:AA:BB"}
  ],
  "endpoints": [
    {"ip": "10.20.8.101", "hostname": "FIN-PC-101", "port": "Gi1/0/1"},
    {"ip": "10.20.8.102", "hostname": "FIN-PC-102", "port": "Gi1/0/2"}
  ]
}
```

图结构：

```text
parse_question
  -> resolve_device
  -> list_access_ports
  -> query_mac_table
  -> query_endpoint_inventory
  -> render_endpoint_table
```

---

## 3.3 条件边

**知识点说明**

阶段二的条件边不只用于意图分流，还用于根据中间结果决定下一步：

- 设备不存在 -> 返回未找到。
- 设备存在但无端口 -> 返回空结果。
- 查到 MAC 但终端库缺失 -> 部分结果输出。
- 多台设备同名 -> 追问用户选择。
- 权限不足 -> 路由到拒绝回答。

**例子**

```python
def route_after_resolve_device(state: NocQueryState) -> str:
    if state.get("error", {}).get("code") == "PERMISSION_DENIED":
        return "deny"
    if not state.get("device_id"):
        return "device_not_found"
    if state.get("ambiguous_devices"):
        return "ask_device_choice"
    return "list_ports"
```

用户问：

> 查一下连接在 SW-Access-F2-Finance 上的所有终端。

如果 MySQL 中查到两台同名历史设备：

```json
{
  "ambiguous_devices": [
    {"device_id": 2031, "name": "SW-Access-F2-Finance", "status": "active"},
    {"device_id": 981, "name": "SW-Access-F2-Finance", "status": "retired"}
  ]
}
```

条件边应该路由到 `ask_device_choice`，而不是随便选一台。

---

## 3.4 消息裁剪策略

**知识点说明**

阶段二有了上下文后，消息会越来越长。如果把所有历史消息都塞给模型，会带来成本、延迟和干扰。

消息裁剪的目标：

- 保留当前任务必需上下文。
- 删除无关对话。
- 保留结构化摘要，而不是保留所有原文。
- 保留最近一次实体引用，例如 `last_device`、`last_port`。

建议维护两类上下文：

| 上下文 | 保存方式 | 作用 |
| --- | --- | --- |
| 原始消息窗口 | 最近 N 轮消息 | 保留自然语言表达 |
| 结构化工作记忆 | State 字段 | 支持追问、实体补全、工具复用 |

**例子**

完整历史可能是：

```text
用户：查 CoreSW-01 的 CPU
助手：当前 CPU 为 42.7%
用户：再看下内存
助手：当前内存为 61%
用户：那它的 Gi1/0/1 呢？
```

裁剪后给模型的上下文可以是：

```json
{
  "recent_messages": [
    {"role": "user", "content": "那它的 Gi1/0/1 呢？"}
  ],
  "working_memory": {
    "last_device": "CoreSW-01",
    "last_metric": "memory_usage",
    "last_time_range": "now"
  }
}
```

这样模型仍然能解析“它”是 `CoreSW-01`。

---

## 3.5 结构化输出

**知识点说明**

阶段二的结果通常是表格、列表、关系链，而不是一句话。结构化输出可以同时服务：

- 前端渲染。
- 后续追问。
- 告警或工单系统引用。
- 可审计日志。

建议让回答节点输出两层内容：

1. `answer_text`：给人的自然语言。
2. `answer_data`：给系统消费的结构化数据。

**例子**

用户问：

> 查一下连接在 SW-Access-F2-Finance 上的所有终端。

输出：

```json
{
  "answer_text": "SW-Access-F2-Finance 当前查询到 2 台在线终端。",
  "answer_data": {
    "type": "endpoint_table",
    "device": "SW-Access-F2-Finance",
    "rows": [
      {
        "port": "Gi1/0/1",
        "mac": "00:11:22:33:44:55",
        "ip": "10.20.8.101",
        "hostname": "FIN-PC-101",
        "user": "finance_zhang"
      },
      {
        "port": "Gi1/0/2",
        "mac": "66:77:88:99:AA:BB",
        "ip": "10.20.8.102",
        "hostname": "FIN-PC-102",
        "user": "finance_li"
      }
    ]
  },
  "follow_up_context": {
    "last_device": "SW-Access-F2-Finance",
    "last_entity_type": "switch",
    "last_result_type": "endpoint_table"
  }
}
```

如果用户追问“第一个终端最近有没有异常？”，Agent 可以根据 `answer_data.rows[0]` 找到对应 MAC/IP。

---

# 4 第三阶段：带时间/空间/复合条件的聚合查询

## 4.1 高级工具设计

**知识点说明**

阶段三的问题经常包含聚合、比较、过滤、空间条件和多数据源关联。单一“执行查询”工具会变得过于宽泛，建议设计更高阶的领域工具。

工具可以按“业务语义”封装，而不是只暴露底层数据库：

| 高级工具 | 内部可能调用 | 用途 |
| --- | --- | --- |
| `compare_metric_peak` | VictoriaMetrics | 对比今天和昨天 CPU 峰值 |
| `get_wireless_heatmap` | MySQL + 指标库 | 生成楼层无线信号热图数据 |
| `find_poor_experience_roamers` | 日志 + 指标 + 终端表 | 找出高频漫游且体验差的用户 |
| `resolve_location_scope` | MySQL | 把“研发中心三楼”解析为空间范围 |

**例子**

用户问：

> 对比 CoreSW-01 今天和昨天的 CPU 峰值。

高级工具输入：

```json
{
  "device_name": "CoreSW-01",
  "metric": "cpu_usage_percent",
  "aggregation": "max",
  "ranges": [
    {"label": "today", "start": 1782748800, "end": 1782835199},
    {"label": "yesterday", "start": 1782662400, "end": 1782748799}
  ]
}
```

高级工具输出：

```json
{
  "device_name": "CoreSW-01",
  "metric": "cpu_usage_percent",
  "comparison": [
    {"label": "today", "peak": 81.2, "peak_at": "2026-06-30T10:42:00+08:00"},
    {"label": "yesterday", "peak": 67.5, "peak_at": "2026-06-29T15:18:00+08:00"}
  ],
  "delta": 13.7,
  "unit": "%"
}
```

这样上层 Agent 不需要关心 PromQL 的具体拼接细节。

---

## 4.2 思维链提示

**知识点说明**

在生产系统中，不建议要求模型输出完整隐藏推理过程。更合适的做法是让模型输出“可审计计划”或“任务分解”，例如：

- 需要查询哪些数据。
- 每一步使用什么工具。
- 每一步产物是什么。
- 最终如何合并。

这类提示可以提升复杂问题的稳定性，同时避免把内部推理暴露给用户。

**例子**

用户问：

> 过去 1 小时，漫游 > 5 次且体验差的用户。

推荐让模型输出任务计划：

```json
{
  "task_type": "compound_filter_query",
  "plan": [
    {
      "step": "resolve_time_range",
      "input": "过去1小时",
      "output": "start_ts,end_ts"
    },
    {
      "step": "query_roaming_events",
      "filter": "roam_count > 5",
      "output": "candidate_users"
    },
    {
      "step": "query_experience_score",
      "filter": "experience_score < 60",
      "output": "poor_experience_users"
    },
    {
      "step": "join_and_rank",
      "join_key": "user_id",
      "output": "ranked_users"
    }
  ]
}
```

图根据这个计划执行工具，而最终用户看到的是结论：

```text
过去 1 小时共有 3 名用户满足“漫游超过 5 次且体验差”的条件，其中 user_013 漫游 9 次，体验分 42，主要集中在研发中心三楼东侧 AP 切换。
```

---

## 4.3 结构化输出

**知识点说明**

阶段三的结构化输出需要能承载聚合结果、比较结果、图表数据和后续 drill-down。

建议结构：

```json
{
  "summary": "...",
  "result_type": "comparison|heatmap|ranked_table|timeseries",
  "data": {},
  "insights": [],
  "next_actions": []
}
```

**例子**

用户问：

> 对比 CoreSW-01 今天和昨天的 CPU 峰值。

输出：

```json
{
  "summary": "CoreSW-01 今天 CPU 峰值为 81.2%，比昨天高 13.7 个百分点。",
  "result_type": "comparison",
  "data": {
    "x_axis": ["昨天", "今天"],
    "series": [
      {"name": "CPU峰值", "values": [67.5, 81.2], "unit": "%"}
    ]
  },
  "insights": [
    "今天峰值出现在 10:42。",
    "峰值已超过 80%，建议继续观察是否存在持续高负载。"
  ],
  "next_actions": [
    {"label": "查看峰值时段接口流量", "intent": "drill_down_interface_traffic"},
    {"label": "查看同时段日志", "intent": "drill_down_logs"}
  ]
}
```

这种输出既能给人读，也能给前端画图。

---

## 4.4 数据可视化接口准备

**知识点说明**

阶段三开始出现热图、趋势图、拓扑图、排名表。Agent 不应该只返回自然语言，而应该返回前端可直接渲染的数据结构。

常见可视化类型：

| 类型 | 场景 | 数据结构重点 |
| --- | --- | --- |
| `timeseries` | CPU、流量、丢包趋势 | 时间戳、数值、单位 |
| `comparison_bar` | 今天 vs 昨天峰值 | 分类、指标值 |
| `heatmap` | 无线信号热图 | x/y 坐标、强度值、楼层底图 ID |
| `topology_path` | 到服务器路径及延迟 | 节点、边、延迟、丢包 |
| `ranked_table` | 体验差用户排行 | 排名、指标、关联位置 |

**例子**

用户问：

> 研发中心三楼的无线信号热图。

输出：

```json
{
  "summary": "研发中心三楼无线信号整体正常，东南角存在弱覆盖区域。",
  "result_type": "heatmap",
  "data": {
    "floor_id": "rd-center-f3",
    "floor_name": "研发中心三楼",
    "metric": "rssi",
    "unit": "dBm",
    "points": [
      {"x": 12.5, "y": 8.1, "value": -48},
      {"x": 15.2, "y": 8.4, "value": -53},
      {"x": 31.8, "y": 19.6, "value": -76}
    ],
    "thresholds": {
      "good": -60,
      "warning": -70,
      "bad": -75
    }
  },
  "insights": [
    "东南角 RSSI 最低约 -76 dBm。",
    "建议检查 AP-RD-F3-08 的发射功率和安装位置。"
  ]
}
```

前端拿到 `result_type = heatmap` 后即可选择热图组件渲染。

---

## 4.5 错误处理与降级

**知识点说明**

复杂查询更容易失败，原因包括：

- 指标库超时。
- 日志库不可用。
- MySQL 查不到映射关系。
- 空间位置无法解析。
- 部分数据源延迟。
- 时间范围过大导致查询成本过高。

错误处理要区分：

| 错误类型 | 处理方式 |
| --- | --- |
| 参数缺失 | 追问用户 |
| 权限不足 | 拒绝并说明范围 |
| 查询超时 | 缩小时间范围或返回缓存 |
| 部分数据缺失 | 返回部分结果并标注缺失 |
| 数据源不可用 | 降级到其他数据源或建议重试 |

**例子**

用户问：

> 过去 1 小时，漫游 > 5 次且体验差的用户。

执行中日志库可用，但体验分指标库超时。降级输出：

```json
{
  "summary": "已查到过去 1 小时漫游超过 5 次的用户，但体验分数据源查询超时，无法确认体验差条件。",
  "result_type": "partial_ranked_table",
  "data": {
    "rows": [
      {"user": "user_013", "roam_count": 9, "experience_score": null},
      {"user": "user_028", "roam_count": 7, "experience_score": null}
    ]
  },
  "is_partial": true,
  "missing_sources": ["experience_metrics"],
  "next_actions": [
    {"label": "仅查看高频漫游用户", "intent": "show_roaming_only"},
    {"label": "重试体验分查询", "intent": "retry_experience_score"}
  ]
}
```

这样用户知道结果不是完整结论，不会误判。

---

# 5 阶段四：开放式诊断/规划/操作意图

## 5.1 多 agent 架构

**知识点说明**

阶段四的问题通常是开放式的，例如“网络很卡，帮我分析原因”。这类任务不是单一查询，而是一组并行或串行诊断任务。

可以设计多个专业 Agent：

| Agent | 职责 |
| --- | --- |
| `planner_agent` | 分解诊断任务，确定执行顺序 |
| `wireless_agent` | 分析 AP 负载、信号强度、漫游、干扰 |
| `switch_agent` | 分析交换机端口丢包、错误包、带宽利用率 |
| `endpoint_agent` | 分析终端体验、认证、IP、DNS |
| `topology_agent` | 分析链路路径、拓扑依赖、上下游设备 |
| `synthesis_agent` | 汇总证据，输出根因和建议 |
| `safety_agent` | 判断是否涉及变更操作，触发确认 |

**例子**

用户问：

> 研发中心网络很卡，帮我分析原因。

任务分解：

```json
{
  "diagnosis_goal": "研发中心网络卡顿根因分析",
  "subtasks": [
    {"agent": "wireless_agent", "task": "检查研发中心 AP 负载、信号、漫游"},
    {"agent": "switch_agent", "task": "检查研发中心接入交换机端口丢包和错误包"},
    {"agent": "endpoint_agent", "task": "检查投诉用户终端体验指标"},
    {"agent": "topology_agent", "task": "检查研发中心到核心网络路径延迟"}
  ]
}
```

汇总结论：

```text
初步判断研发中心三楼卡顿主要与无线侧有关。证据包括：AP-RD-F3-08 接入用户数达到 63，平均 RSSI 为 -74 dBm，过去 1 小时高频漫游用户 18 人；同时接入交换机上联口未发现明显丢包，核心到出口链路延迟正常。
```

---

## 5.2 子图

**知识点说明**

子图是把一组稳定流程封装成可复用模块。阶段四中，不同诊断领域可以各自成为子图：

- 无线诊断子图。
- 交换机诊断子图。
- 终端诊断子图。
- 拓扑路径诊断子图。
- 安全确认子图。

子图的好处：

- 复杂系统分层。
- 每个子图可以独立测试。
- 子图可以被多个上层工作流复用。
- 不同团队可以维护不同子图。

**例子**

无线诊断子图：

```text
resolve_location
  -> list_aps
  -> query_ap_load
  -> query_client_rssi
  -> query_roaming_events
  -> detect_wireless_anomalies
  -> summarize_wireless_findings
```

上层诊断图：

```text
planner
  -> wireless_diagnosis_subgraph
  -> switch_diagnosis_subgraph
  -> topology_diagnosis_subgraph
  -> synthesis
```

当用户问“研发中心网络很卡”时，上层图调用无线诊断子图；当用户问“研发中心三楼无线信号热图”时，也可以复用其中的 `resolve_location` 和 `list_aps` 逻辑。

---

## 5.3 RAG/知识库

**知识点说明**

RAG 用于让 Agent 查询企业内部知识，而不是只依赖模型常识。网络运维中常见知识库包括：

- 网络拓扑说明。
- 设备命名规范。
- 故障处理手册。
- 厂商配置手册。
- 变更记录。
- 工单历史。
- 已知问题库。
- SLA 和告警阈值规范。

RAG 在阶段四尤其重要，因为开放式诊断需要结合“本企业网络怎么设计”的上下文。

**例子**

用户问：

> 画出到官网服务器的路径及延迟。

RAG 检索可能返回：

```json
{
  "documents": [
    {
      "title": "官网服务器网络接入说明",
      "content": "官网服务器 www-prod-01 位于 DMZ 区，业务 VIP 为 203.0.113.10，上联防火墙 FW-DMZ-01。"
    },
    {
      "title": "核心网络拓扑规范",
      "content": "研发中心到 DMZ 的路径通常为 Access -> Dist -> Core -> FW-DMZ -> Server。"
    }
  ]
}
```

随后 Agent 结合 MySQL 拓扑表和实时探测结果输出：

```json
{
  "result_type": "topology_path",
  "data": {
    "nodes": [
      {"id": "client", "label": "研发中心用户"},
      {"id": "SW-RD-F3", "label": "接入交换机"},
      {"id": "CoreSW-01", "label": "核心交换机"},
      {"id": "FW-DMZ-01", "label": "DMZ防火墙"},
      {"id": "www-prod-01", "label": "官网服务器"}
    ],
    "edges": [
      {"from": "client", "to": "SW-RD-F3", "latency_ms": 1.2},
      {"from": "SW-RD-F3", "to": "CoreSW-01", "latency_ms": 2.8},
      {"from": "CoreSW-01", "to": "FW-DMZ-01", "latency_ms": 4.5},
      {"from": "FW-DMZ-01", "to": "www-prod-01", "latency_ms": 3.1}
    ]
  }
}
```

---

## 5.4 人在回路

**知识点说明**

人在回路用于高风险操作、权限边界、诊断不确定性确认。阶段四中尤其重要，因为用户可能从“查询”进入“操作”：

- 找出未使用端口。
- 关闭未使用端口。
- 调整 AP 功率。
- 清理 MAC 表。
- 重启端口。
- 下发 ACL。

原则：

- 只读查询可以自动执行。
- 变更操作必须展示影响范围和回滚方式。
- 需要用户确认后才能执行。
- 用户可以批准、修改、拒绝或补充信息。

**例子**

用户问：

> 找出 SW-F3-Market 上所有未使用端口。

这是只读查询，可以直接执行：

```json
{
  "device": "SW-F3-Market",
  "unused_ports": [
    {"port": "Gi1/0/17", "last_seen": "2026-05-12T09:20:00+08:00"},
    {"port": "Gi1/0/18", "last_seen": "2026-04-28T14:10:00+08:00"}
  ]
}
```

如果用户继续说：

> 把这些端口都 shutdown。

这就是变更操作，必须进入人在回路：

```json
{
  "requires_approval": true,
  "action": "shutdown_ports",
  "device": "SW-F3-Market",
  "ports": ["Gi1/0/17", "Gi1/0/18"],
  "risk": "可能影响临时接入设备或未登记终端",
  "rollback": "no shutdown Gi1/0/17, Gi1/0/18"
}
```

用户确认后，图才继续执行配置变更节点。

---

## 5.5 可观测性与调试

**知识点说明**

LangGraph Agent 一旦进入多节点、多工具、多 Agent 阶段，就必须具备可观测性。否则出现错误时很难判断是：

- 意图识别错。
- 参数抽取错。
- 工具选择错。
- 查询语句错。
- 数据源超时。
- 后处理逻辑错。
- 多 Agent 汇总时误判。

建议记录：

| 观测对象 | 内容 |
| --- | --- |
| State 快照 | 每个关键节点前后的状态变化 |
| 工具调用 | 工具名、参数、耗时、返回大小、错误码 |
| 路由决策 | 条件边选择了哪个分支，以及原因 |
| LLM 输出 | 结构化输出、解析失败原因 |
| 子图结果 | 每个子诊断的证据、置信度 |
| 用户确认 | 谁在什么时候批准了什么操作 |

**例子**

一次“研发中心网络很卡”的诊断 trace：

```json
{
  "trace_id": "diag-20260630-0001",
  "thread_id": "ops-user-001-ticket-8848",
  "nodes": [
    {
      "node": "planner",
      "duration_ms": 820,
      "output": {
        "subtasks": ["wireless", "switch", "topology", "endpoint"]
      }
    },
    {
      "node": "wireless_diagnosis_subgraph",
      "duration_ms": 4130,
      "output": {
        "finding": "AP-RD-F3-08 高负载且弱信号用户集中",
        "confidence": 0.82
      }
    },
    {
      "node": "switch_diagnosis_subgraph",
      "duration_ms": 2760,
      "output": {
        "finding": "核心和接入链路未见明显丢包",
        "confidence": 0.76
      }
    },
    {
      "node": "synthesis",
      "duration_ms": 970,
      "output": {
        "root_cause": "无线侧容量和覆盖问题可能性最高",
        "confidence": 0.79
      }
    }
  ]
}
```

当用户质疑“为什么判断是无线问题？”时，系统可以返回证据链，而不是只给结论。

---

# 6 推荐学习顺序

1. 先掌握 `StateGraph`、State、节点、边、条件边。
2. 再实现阶段一的单实体查询闭环。
3. 引入 checkpointer，支持阶段二的追问和上下文。
4. 设计结构化输出，为表格、图表、拓扑做好接口。
5. 把复杂查询封装成高级工具，不要让模型直接拼接所有查询。
6. 把诊断能力拆成子图和多 Agent。
7. 最后补齐人在回路、权限、安全确认、可观测性。

# 7 最小可行架构建议

```text
入口 API
  -> LangGraph 主图
      -> parse_intent_node
      -> parameter_extraction_node
      -> context_resolution_node
      -> conditional_router
          -> metric_query_subgraph
          -> log_query_subgraph
          -> inventory_query_subgraph
          -> diagnosis_subgraph
          -> operation_approval_subgraph
      -> answer_render_node
  -> 前端渲染
```

阶段一可以先只实现：

```text
parse_intent -> build_query -> run_tool -> render_answer
```

阶段二再增加：

```text
context_resolution -> multi_step_tool_chain -> structured_output
```

阶段三再增加：

```text
time_range_resolver -> aggregation_tools -> post_processor -> visualization_output
```

阶段四再增加：

```text
planner -> multiple_specialist_agents -> evidence_synthesis -> human_approval
```

# 8 实践注意事项

- 不要让 LLM 直接执行任意 SQL，应该使用只读账号、白名单表、参数化查询或模板查询。
- PromQL 和 LogQL 建议用模板生成，LLM 只负责抽取结构化参数。
- 所有工具返回都要带 `source`、`query`、`duration_ms`、`is_partial`、`error`。
- 所有回答都应保留结构化数据，方便追问和前端渲染。
- 涉及配置变更、重启、shutdown、ACL、路由调整时必须进入人在回路。
- 对开放式诊断，要输出证据链和置信度，避免只给结论。
- 对多数据源结果，要明确时间范围和数据新鲜度。

