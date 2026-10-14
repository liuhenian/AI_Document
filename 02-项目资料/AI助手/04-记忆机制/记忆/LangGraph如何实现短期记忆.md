下面我按 **概念 → 原理 → 组件 → 实现方式 → 代码示例 → 常见坑 → 最佳实践** 来详细讲 **LangGraph 的短期记忆**。

---

# 1 什么是 LangGraph 的“短期记忆”

在 LangGraph 里，**短期记忆（short-term memory）** 指的是：

> 在当前会话 / 当前线程 / 当前任务执行期间，系统为了保持上下文连续性而保存的状态信息。

它通常包括：

- 最近几轮对话消息
- 当前任务的中间推理结果
- 工具调用结果
- 当前计划、下一步动作
- 当前会话内需要保留的用户信息
- 中断后恢复执行所需的上下文

你可以把它理解成：

- **人类工作记忆**：眼下正在处理的事
- 而不是长期存档的人生档案

---

# 2 LangGraph 里短期记忆的本质

LangGraph 本质是一个 **状态驱动的图执行框架**。  
所以短期记忆的核心不是“memory 类”本身，而是：

> **State + Checkpoint + Thread**

也就是说，LangGraph 的短期记忆主要由这三层构成：

---

## 2.1 State：记忆内容
State 是图执行过程中传递的数据结构。

比如：

- `messages`
- `tool_result`
- `current_plan`
- `final_answer`
- `next_step`

这些字段本身就是“短期记忆内容”。

---

## 2.2 Thread：记忆归属
Thread 是一次会话 / 一条执行链的标识。

最常见是：
```python
config={"configurable": {"thread_id": "user_001"}}
```

这表示：

- 同一个 `thread_id` 的执行，共享同一份会话上下文
- 下一次调用时，LangGraph 可以从这个线程中继续读取上次状态

---

## 2.3 Checkpoint：记忆存储
Checkpoint 负责把 state 保存下来，并能在下次恢复。

没有 checkpointer 时：
- State 只在当前 `invoke()` 里有效
- 一旦程序结束，这些状态就没了

有 checkpointer 时：
- 同一 thread 的 state 可以被恢复
- 支持多轮对话
- 支持中断恢复
- 支持会话级上下文连续

---

# 3 短期记忆到底存什么？

短期记忆不只是聊天记录。

在 LangGraph 里，它可以存这几类信息：

---

## 3.1 对话消息 messages
最常见。

例如：
- HumanMessage
- AIMessage
- ToolMessage

这些消息通常构成了当前会话上下文。

---

## 3.2 中间变量
例如：
- 意图识别结果 `intent`
- 当前步骤 `step`
- 当前计划 `plan`
- 工具输入输出 `tool_input`, `tool_result`
- 检索结果 `retrieved_docs`

这些都属于 agent 在当前任务中临时需要记住的内容。

---

## 3.3 控制信息
例如：
- `next_step`
- `iteration_count`
- `is_done`
- `error`

这些是图流转时必须保留的执行控制数据。

---

## 3.4 中断恢复所需信息
如果你用了：
- interrupt
- human-in-the-loop
- 多步任务恢复

那么短期记忆还要保存：
- 当前停在哪个节点
- 已执行到哪一步
- 上下文是什么

---

# 4 LangGraph 是怎么实现短期记忆的？

LangGraph 的短期记忆不是一个独立“黑盒记忆系统”，而是依赖以下机制共同完成：

---

## 4.1 通过 State 在节点间传递
每个节点：

- 读取当前 state
- 生成新的 state 更新
- 下一个节点继续读取

所以记忆首先体现在 **状态的延续性** 上。

例如：

```python
def tool_node(state):
    result = "订单已发货"
    return {"tool_result": result}
```

这个 `tool_result` 会进入后续节点可见的 state。  
这就是短期记忆的最小形式。

---

## 4.2 通过 reducer 管理字段合并
有些字段是覆盖式更新，有些字段要追加。

特别是 `messages`，通常不是每次覆盖，而是**追加**。

LangGraph 常用 reducer 机制来处理这种“记忆累积”。

典型场景：
- 旧消息 + 新消息 = 新的 messages
- 而不是直接替换成最新消息

---

## 4.3 通过 Checkpointer 持久化线程状态
这一步是“真正会话级短期记忆”的关键。

编译图时加上：

```python
graph = builder.compile(checkpointer=checkpointer)
```

然后每次调用用同一个 thread_id：

```python
graph.invoke(
    {"messages": [HumanMessage(content="你好")]},
    config={"configurable": {"thread_id": "thread-1"}}
)
```

LangGraph 会把该线程的状态保存起来。  
下一次再用 `thread-1` 调用时，它能恢复到之前的状态基础上继续执行。

---

# 5 短期记忆的两种层次

可以把 LangGraph 的短期记忆理解成两层：

---

## 5.1 运行期短期记忆
只在本次 `invoke()` 有效。

特点：
- 不依赖 checkpointer
- state 在本次图执行内可传递
- 执行结束后通常不保留

适合：
- 单次任务流
- 一次性问答
- 工具链式调用

---

## 5.2 会话级短期记忆
跨多次 `invoke()` 保留。

特点：
- 依赖 checkpointer
- 依赖 thread_id
- 可做多轮对话
- 可做中断恢复

适合：
- 聊天机器人
- 多轮任务助理
- 人工审批流程
- 会话中持续追踪用户任务

---

# 6 一个最小短期记忆示例

下面我给你一个 **最小可理解示例**。

---

## 6.1 目标
做一个简单聊天图：

- 用户发消息
- 模型回复
- 对话历史保存在短期记忆里
- 同一 thread 下多次调用，可以记住之前说过的话

---

## 6.2 代码示例

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# 1) 定义 State
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]

# 2) 初始化模型
llm = ChatOpenAI(
    model="your-open-source-model",
    base_url="http://your-api/v1",
    api_key="xxx"
)

# 3) 定义节点
def chatbot_node(state: ChatState):
    response = llm.invoke(state["messages"])
    return {
        "messages": [response]
    }

# 4) 构建图
builder = StateGraph(ChatState)
builder.add_node("chatbot", chatbot_node)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# 5) 添加 checkpointer
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# 6) 第一次调用
result1 = graph.invoke(
    {"messages": [HumanMessage(content="我叫张三")]},
    config={"configurable": {"thread_id": "user-1"}}
)

print("第一次回复：")
for msg in result1["messages"]:
    print(type(msg).__name__, msg.content)

# 7) 第二次调用：同一个 thread_id
result2 = graph.invoke(
    {"messages": [HumanMessage(content="你还记得我叫什么吗？")]},
    config={"configurable": {"thread_id": "user-1"}}
)

print("\n第二次回复：")
for msg in result2["messages"]:
    print(type(msg).__name__, msg.content)
```

---

# 7 这个例子里短期记忆是怎么工作的？

我们拆开看。

---

## 7.1 `messages` 是短期记忆内容
```python
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
```

这里说明：

- state 中有个 `messages`
- 它不是普通字段
- 它使用 `add_messages` reducer

意思是：
> 每次节点返回的新消息，会追加到已有消息列表中，而不是直接覆盖。

---

## 7.2 `MemorySaver` 是短期记忆存储器
```python
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
```

这表示图执行后的状态会被保存到内存中。

注意：
- 这是开发测试用
- 程序重启后就丢失
- 但在同一进程内足够展示短期记忆效果

---

## 7.3 `thread_id` 决定记忆归属
```python
config={"configurable": {"thread_id": "user-1"}}
```

这个非常关键。

含义是：
- 第一次调用把用户 `user-1` 的消息和响应存起来
- 第二次调用如果还是 `user-1`，就会接着之前的状态继续

如果你换成：
```python
thread_id = "user-2"
```
那就会像新会话一样，没有之前记忆。

---

## 7.4 为什么第二次能记住“张三”
第一次调用后，state 大致是：

```python
messages = [
    HumanMessage("我叫张三"),
    AIMessage("好的，我记住了，你叫张三。")
]
```

第二次调用时，新的输入：
```python
HumanMessage("你还记得我叫什么吗？")
```

由于 `add_messages` 会追加，所以实际发给模型的消息可能变成：

```python
[
    HumanMessage("我叫张三"),
    AIMessage("好的，我记住了，你叫张三。"),
    HumanMessage("你还记得我叫什么吗？")
]
```

因此模型能根据上下文回答。

这就是 LangGraph 短期记忆最核心的机制。

---

# 8 再看一个更像 Agent 的示例

短期记忆不止记 messages。  
下面给你一个“工具调用型”思路示例。

---

## 8.1 目标
做一个简单订单助手：

- 用户先说订单号
- 后面只说“帮我查一下状态”
- agent 能记住刚才提到的订单号

---

## 8.2 State 设计

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class OrderState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    order_id: str
    tool_result: str
    final_answer: str
```

这里：
- `messages`：聊天上下文短期记忆
- `order_id`：从当前会话中提取出的临时业务记忆
- `tool_result`：工具返回结果
- `final_answer`：最终回答

---

## 8.3 节点示例

### 8.3.1 提取订单号节点
```python
import re
from langchain_core.messages import HumanMessage

def extract_order_node(state: OrderState):
    last_msg = state["messages"][-1].content
    match = re.search(r"A\d+", last_msg)
    if match:
        return {"order_id": match.group()}
    return {}
```

### 8.3.2 工具节点
```python
def query_order_tool(order_id: str):
    return f"订单 {order_id} 当前状态：已发货"
```

```python
def tool_node(state: OrderState):
    if not state.get("order_id"):
        return {"final_answer": "请先提供订单号。"}
    result = query_order_tool(state["order_id"])
    return {"tool_result": result}
```

### 8.3.3 回答节点
```python
def answer_node(state: OrderState):
    if state.get("tool_result"):
        return {"final_answer": state["tool_result"]}
    return {"final_answer": "暂时没有查到结果。"}
```

---

## 8.4 图流程
```text
用户输入
  ↓
extract_order_node
  ↓
tool_node
  ↓
answer_node
  ↓
END
```

---

## 8.5 短期记忆效果
第一次用户说：
> 我的订单号是 A10086

state 里会被记住：
```python
order_id = "A10086"
```

第二次同一 thread 用户说：
> 帮我查一下状态

即使这次没再提订单号，由于同一个 thread 的 checkpoint 中已经保存了 `order_id`，工具节点依然可以查。

这说明：
> LangGraph 的短期记忆不只是“聊天历史”，也可以是结构化业务状态。

---

# 9 短期记忆为什么比“只传历史消息”更强？

因为它不仅能存自然语言，还能存结构化状态。

传统聊天记忆常常只是：
- 把前几轮对话拼到 prompt 里

而 LangGraph 的短期记忆可以额外保留：
- 当前订单号
- 当前计划
- 已完成的步骤
- 已调用的工具结果
- 当前审批状态
- 当前工作流位置

所以它更适合 agent / workflow 场景。

---

# 10 短期记忆的关键组件详解

---

## 10.1 `messages`
最常用字段。  
表示会话消息序列。

常与：
```python
Annotated[list, add_messages]
```
一起使用。

作用：
- 自动追加消息
- 保留上下文连续性

---

## 10.2 `add_messages`
这是一个 reducer，用于合并消息列表。

没有它的话，你返回：
```python
{"messages": [response]}
```
可能会把旧消息覆盖掉。

有了它：
- 新消息会追加到旧消息之后

所以对聊天短期记忆非常关键。

---

## 10.3 `checkpointer`
负责保存和恢复 state。

常见开发时先用：
```python
from langgraph.checkpoint.memory import MemorySaver
```

生产通常会换成持久化后端。

---

## 10.4 `thread_id`
短期记忆的会话键。

你必须显式传入：

```python
config={"configurable": {"thread_id": "abc"}}
```

否则：
- 每次都可能是独立执行
- 无法形成会话级短期记忆

---

# 11 短期记忆与中断恢复

LangGraph 的短期记忆一个很强的点是：  
它不仅支持“记住聊天”，还支持“记住执行现场”。

比如：

- 图执行到审批节点暂停
- 人工过几分钟/几小时后再恢复
- 系统还能知道之前执行到哪里、已有哪部分状态

这是因为短期记忆保存的是整个 state + graph execution context，而不是单纯聊天文本。

这也是 LangGraph 区别于普通聊天框架的重要地方。

---

# 12 常见问题与坑

---

## 12.1 忘记传 `thread_id`
如果你没传：
```python
config={"configurable": {"thread_id": "..."}}
```

那通常每次都是新上下文。  
表现为：
- “为什么记不住上一轮？”

---

## 12.2 没有配置 checkpointer
如果不加：
```python
builder.compile(checkpointer=memory)
```

那 state 只在一次执行内存在。  
跨多次调用无法保留。

---

## 12.3 `messages` 被覆盖而不是追加
如果 `messages` 没配置：
```python
Annotated[list, add_messages]
```

你每次返回的新消息可能把旧的全覆盖。  
表现为：
- “看起来没有历史消息”
- “模型像失忆了一样”

---

## 12.4 消息越来越长
短期记忆不是越多越好。

如果每轮都无限追加 messages，会带来：
- token 成本上涨
- 推理变慢
- 噪音变多
- 模型更容易跑偏

所以短期记忆通常需要管理。

---

# 13 短期记忆的管理策略

---

## 13.1 保留最近 N 轮
例如只保留最近 10 轮消息。

适合：
- 普通聊天助手
- 上下文依赖不长

---

## 13.2 做会话摘要
把旧消息压缩为 summary，再保留最近几轮原文。

例如：
- `conversation_summary`
- `recent_messages`

这样比全量 messages 更稳。

---

## 13.3 结构化提取
不要完全依赖自然语言历史。  
把关键短期状态提取出来：

- 当前订单号
- 当前任务编号
- 当前主题
- 当前目标

这样就算消息裁剪了，关键上下文还在。

---

# 14 生产级建议

如果你在正式项目里做短期记忆，我建议：

---

## 14.1 短期记忆至少分两层
- `messages`：保留最近对话
- `structured_state`：保留关键结构化字段

例如：
```python
class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    current_order_id: str
    current_plan: str
    tool_result: str
    final_answer: str
```

---

## 14.2 用 thread_id 做用户会话隔离
例如：
- `tenant_id:user_id:session_id`

这样更安全，也方便多租户。

---

## 14.3 不要把短期记忆当长期记忆
短期记忆适合：
- 当前会话
- 当前任务
- 当前线程

不适合：
- 永久用户画像
- 跨月知识积累
- 跨系统共享用户事实

那些应该放长期记忆系统里。

---

## 14.4 给 messages 做裁剪或摘要
尤其是开源模型上下文不稳定时，更要控制长度。

---

# 15 一个更完整的短期记忆示例模板

下面给你一个更接近实战的模板。

```python
from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    user_name: Optional[str]
    final_answer: Optional[str]

llm = ChatOpenAI(
    model="your-model",
    base_url="http://your-api/v1",
    api_key="xxx"
)

def extract_profile_node(state: AgentState):
    last_user_msg = state["messages"][-1].content
    if "我叫" in last_user_msg:
        name = last_user_msg.split("我叫")[-1].strip()
        return {"user_name": name}
    return {}

def chat_node(state: AgentState):
    system_prefix = ""
    if state.get("user_name"):
        system_prefix = f"用户名字是{state['user_name']}。请在合适时利用这个信息。\n"

    response = llm.invoke([
        HumanMessage(content=system_prefix + "\n".join([m.content for m in state["messages"]]))
    ])
    return {"messages": [response]}

builder = StateGraph(AgentState)
builder.add_node("extract_profile", extract_profile_node)
builder.add_node("chat", chat_node)

builder.add_edge(START, "extract_profile")
builder.add_edge("extract_profile", "chat")
builder.add_edge("chat", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# 第一次
graph.invoke(
    {"messages": [HumanMessage(content="你好，我叫李雷")]},
    config={"configurable": {"thread_id": "session-001"}}
)

# 第二次
result = graph.invoke(
    {"messages": [HumanMessage(content="你知道我叫什么吗？")]},
    config={"configurable": {"thread_id": "session-001"}}
)

for msg in result["messages"]:
    print(type(msg).__name__, msg.content)
```

这个例子里：

- `messages` 保存对话上下文
- `user_name` 保存结构化短期记忆
- `MemorySaver + thread_id` 保证跨调用可恢复

这是非常典型的 LangGraph 短期记忆模式。

---

# 16 总结

LangGraph 的短期记忆，本质上是：

> **把当前会话/线程中需要持续保留的信息放进 state，并借助 checkpointer 按 thread 保存与恢复。**

它的核心组成是：

- **State**：记忆内容
- **messages / 结构化字段**：记忆形式
- **reducer**：记忆合并方式
- **checkpointer**：记忆保存机制
- **thread_id**：记忆归属标识

它比传统聊天历史记忆更强，因为它不仅能记住“说过什么”，还能记住：

- 当前任务状态
- 中间结果
- 工具输出
- 结构化业务变量
- 中断恢复现场

---

如果你愿意，我下一步可以继续给你两种更实用的内容：

1. **画一个 LangGraph 短期记忆的执行流程图**
2. **给你一个“开源模型 API + LangGraph + 短期记忆”的可运行完整 demo**

如果你想继续，直接回复：

**“给我短期记忆完整 demo”**  
或者  
**“给我画短期记忆流程图”**