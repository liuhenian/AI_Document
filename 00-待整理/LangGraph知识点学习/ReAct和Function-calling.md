好的，我们来深入拆解 **ReAct / Function-calling** 这一现代 Agent 的核心范式，并重点说明它如何**天然地解决了意图识别问题**，以及如何在 LangGraph 中落地。

---

## 0.1 一、ReAct 是什么

**ReAct = Reasoning + Acting**，是一种让 LLM 交替进行“思考（推理）”和“行动（调用工具）”的提示与执行模式。它让模型在解决问题时，不仅生成最终答案，还会：

1. 输出一段**推理文字**（Thought），分析当前状态、决定下一步做什么。
2. 输出一个**行动指令**（Action），指定要调用的工具及其参数。
3. 系统执行该行动，把**观察结果**（Observation）追加回对话上下文。
4. 模型根据观察继续推理，直到认为可以给出最终答案。

经典 ReAct 提示词模板如下：

```
You have access to the following tools:
search: Search the web for information.
calculator: Perform math calculations.

Use the format:
Thought: <your reasoning>
Action: <tool name>
Action Input: <tool input>
Observation: <result from tool>
... (repeat as needed)
Final Answer: <response to user>
```

通过这个循环，模型能自主决定何时调用工具、调用哪个工具、如何利用工具结果完成用户目标。

---

## 0.2 二、Function-calling（函数调用）是 ReAct 的“结构化进化”

Function-calling 是目前主流 LLM（GPT-4、Claude、Gemini、通义千问等）原生支持的能力。它本质上是 **ReAct 模式的标准化实现**：

- 不再需要手动解析“Action: xxx”这种文本，而是由模型直接输出一个结构化的 **tool_call 字段**（JSON），包含工具名和参数。
- 平台/框架（如 LangChain、LangGraph）负责**自动执行**对应函数，并把结果封装成 **tool 消息**返回给模型。
- 整个循环由模型自身决定何时停止调用工具并生成给用户的自然语言回复。

**一次完整的 Function-calling 交互过程**：

1. 用户输入 `"帮我查一下北京今天的天气，并告诉我适合穿什么"`
2. 模型思考后返回一个 AI 消息，**不包含文本内容**，只包含一个 `tool_calls` 数组：
   ```json
   [
     {
       "id": "call_1",
       "name": "get_weather",
       "arguments": {"city": "北京", "date": "today"}
     }
   ]
   ```
3. 系统执行 `get_weather`，得到结果 `{"weather": "晴，25°C"}`，将其包装为 `Tool` 消息放入上下文。
4. 模型收到工具结果后，可能直接生成最终回答：`“北京今天晴，25°C，建议穿轻薄长袖或T恤。”` 也可能决定再次调用工具（比如再查穿衣指数）。

这个流程正是 **ReAct 循环**，只是思考（Thought）被隐含在模型内部，行动（Action）和观察（Observation）通过结构化的 `tool_calls` 和 `Tool` 消息完成。

---

## 0.3 三、为什么说它天然解决了意图识别

在传统多轮对话系统中，“意图识别”是一个独立的 NLU 模块，需要预先定义意图、收集语料、训练模型，然后路由到不同的处理逻辑。

**而在 ReAct/Function-calling Agent 中，意图识别被“工具选择”所取代：**

- 你不再需要显式地问“用户想干什么（订单查询？售后？推荐？）”，而是提供一组工具函数，每个工具对应一种**可执行的能力**。
- 模型在看到用户输入后，会自主决定**调用哪个工具**来完成用户目标。
- 工具的 `name` 和 `description` 就是“意图”的语义载体。模型通过自然语言理解将它们与用户意图匹配。

**举个例子**：你定义了三个工具：

```python
def query_order(order_id: str): "查询订单状态，需要提供订单号"
def create_refund(order_id: str, reason: str): "发起退款或售后，需要订单号和原因"
def recommend_products(preference: str): "根据用户偏好推荐商品"
```

当用户说 `“我的订单12345到哪了？”`，模型会自动选择 `query_order(order_id="12345")`。  
当用户说 `“刚买的衣服不喜欢，想退掉”`，模型可能先调 `query_order` 获取最近订单，再调 `create_refund`。

**没有显式的意图分类器，但意图已经被精准执行。**  
这就是“工具调用式意图识别”的本质：**意图 = 被调用的工具**。

---

## 0.4 四、在 LangGraph 中如何实现这种 Agent

LangGraph 对 Function-calling 有一等公民支持，核心是通过 **ToolNode** 和**条件边**来实现推理-行动循环。

### 0.4.1 基础结构：`ToolNode` + 条件路由

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

# 定义工具
tools = [query_order, create_refund, recommend_products]
tool_node = ToolNode(tools)

# 定义状态
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 定义调用模型的节点（绑定工具）
def call_model(state: State):
    # 绑定工具，让模型知道可以调用哪些函数
    response = llm.bind_tools(tools).invoke(state["messages"])
    return {"messages": [response]}

# 条件路由函数：判断模型是否想调用工具
def should_continue(state: State):
    last_message = state["messages"][-1]
    # 如果有 tool_calls，则进入 ToolNode 执行
    if last_message.tool_calls:
        return "tools"
    # 否则结束
    return END

# 构建图
builder = StateGraph(State)
builder.add_node("agent", call_model)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue, {
    "tools": "tools",
    END: END
})
builder.add_edge("tools", "agent")  # 工具结果返回 agent 继续思考
```

**执行流程可视化**：
```
START → agent (模型决策) → 有工具调用? 
                                ├─ 是 → tools (执行) → agent (再次推理)
                                └─ 否 → END (输出最终回答)
```

这个循环会一直运行，直到模型不再产生 `tool_calls`，输出给用户的最终自然语言消息。

### 0.4.2 这样设计带来的好处

- **无感扩展**：新增功能只需增加一个工具函数，模型自动学会何时调用它，无需修改路由逻辑。
- **多步推理**：用户复杂请求（“帮我查订单并判断是否该退款”）会被自动拆解为多次工具调用。
- **动态纠错**：工具返回错误时（如订单号不存在），模型会读取错误信息并尝试修正参数后重新调用。
- **意图边界模糊问题消失**：不再纠结一个对话到底是“查询+售后”还是“查询+推荐”，模型可以按需混合调用不同工具。

---

## 0.5 五、更高级的实践：结合少量意图显式路由

虽然 Function-calling 可以覆盖大多数场景，但在**性能敏感或需要精确控制流程**时，你仍然可以将其与显式意图路由结合。例如：

1. 先用一个极快的规则/小模型提取**明确的高频意图**（如“订单查询”），直接走优化路径（跳过 LLM 推理）。
2. 剩下的请求交给 Function-calling Agent，让模型自主处理。

在 LangGraph 中，这可以通过一个**前置路由节点**实现，该节点返回“快速意图”或“交给 Agent”，然后由条件边分流。

```python
def pre_route(state):
    if re.search(r"订单.*查询|物流", state["messages"][-1].content):
        return "fast_order_handler"
    return "agent"   # 进入 Function-calling 循环
```

---

## 0.6 六、总结

- **ReAct** 是一种让 LLM 通过“思考-行动-观察”循环解决复杂任务的模式。
- **Function-calling** 是它的工程化落地，结构化的工具调用让 Agent 可靠、可扩展。
- 在这种模式下，**意图识别不再是一个独立的分类任务，而是模型根据工具描述自主决策的过程**——意图变成了工具选择。
- LangGraph 通过 `ToolNode` + 条件边，能非常简洁地实现这个循环，并且可以轻松嵌入任何自定义逻辑。

这种设计是现代 Agent 系统的主流方案，也是我建议你在意图识别设计上优先考虑的路径。如果你有特定领域/工具集，我可以帮你设计具体的工具描述和图结构。