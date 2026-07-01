
# 1 agent 自身通常包含什么

一个完整 agent 一般包含这几类东西：

## 1.1 角色/目标
它是谁，负责什么。

比如：
- 客服 agent
- 检索 agent
- SQL 查询 agent
- 代码 agent
- 审核 agent
- supervisor agent

这部分决定它的行为边界。

---

## 1.2 输入上下文
agent 能看到什么信息。

常见包括：
- 用户问题
- 历史对话
- 系统提示词
- 上游 agent 的输出
- 工具调用结果
- 检索结果
- 当前任务目标
- 当前状态字段

没有上下文，agent 就没法决策。

---

## 1.3 状态 State
这是 LangGraph 里最关键的部分。

状态是 agent 工作时依赖和更新的数据，比如：
- `messages`
- `user_input`
- `plan`
- `intent`
- `tool_name`
- `tool_input`
- `tool_result`
- `final_answer`
- `next_step`
- `status`
- `error`

agent 的本质就是：
> 读取 state → 做判断/执行 → 返回 state 更新

---

## 1.4 大模型能力
agent 通常会用 LLM 做这些事：
- 理解用户意图
- 决定下一步
- 生成结构化输出
- 选择工具
- 总结工具结果
- 生成最终答案

也就是说，LLM 是 agent 的“大脑”，但不是 agent 的全部。

---

## 1.5 工具 Tools
如果 agent 要做事，就需要工具。

例如：
- 查数据库
- 查订单
- 搜索知识库
- 发请求到内部 API
- 执行 Python
- 调用搜索引擎
- 写文件 / 读文件

工具是 agent 的“手”。

---

## 1.6 决策逻辑
agent 要知道下一步做什么。

比如：
- 直接回答
- 调工具
- 继续追问用户
- 转交给别的 agent
- 结束
- 重试

这部分在 LangGraph 里通常体现为：
- 节点里的判断
- 条件边
- 路由函数
- 结构化输出中的 `next_step`

---

## 1.7 输出结果
agent 工作后要产出什么。

比如：
- 最终答案
- 工具调用请求
- 路由决策
- 审核结果
- 计划
- 任务执行状态

---

## 1.8 约束与边界
agent 不应该无限制发挥。

要定义：
- 什么时候结束
- 最大循环次数
- 不能调用哪些工具
- 缺少信息时必须先追问
- 输出必须是什么格式
- 出错时怎么办

这部分很重要，否则 agent 很容易失控。

---

# 2 二、用一句话总结 agent 的构成

一个 agent 本质上是：

> **角色 + 上下文 + 状态 + LLM + 工具 + 决策逻辑 + 输出约束**

---

# 3 如果你要自己写一个 agent，需要做什么？

如果你要自己从 0 写一个 LangGraph agent，通常要做下面这些工作。

---

## 3.1 第一步：明确 agent 的职责
先不要写代码，先写一句话：

> 这个 agent 到底负责什么？

例如：
- 根据用户问题决定是否查订单
- 读取知识库并回答问题
- 根据任务生成执行计划
- 负责代码生成
- 负责审核另一个 agent 的结果

### 3.1.1 很重要
一个 agent 最好职责单一。
不要一开始写成：
- 既负责规划
- 又负责执行
- 又负责审核
- 又负责调度

这样会很乱。

---

## 3.2 第二步：定义输入和输出
你要先想清楚：

### 3.2.1 输入是什么？
- 用户消息？
- 上游节点结果？
- 检索文档？
- 当前任务目标？

### 3.2.2 输出是什么？
- 一段回答？
- 一个工具调用请求？
- 一个路由决策？
- 一个 plan？
- 一个审核结果？

### 3.2.3 例子
比如“订单查询 agent”：

输入：
- 用户问题
- 历史消息

输出：
- next_step
- tool_name
- tool_input
- final_answer

---

## 3.3 第三步：设计 State
这是最重要的一步。

你要定义 agent 在运行中需要保存哪些字段。

比如：

```python
from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict, total=False):
    messages: List[BaseMessage]
    user_input: str
    intent: str
    next_step: str
    tool_name: str
    tool_input: dict
    tool_result: str
    final_answer: str
    error: str
```

### 3.3.1 设计 state 的原则
- 只放真正需要流转的数据
- 字段命名清晰
- 尽量结构化
- 区分“原始输入”和“处理结果”
- 提前考虑异常字段

---

## 3.4 第四步：定义 agent 的行为步骤
你要把 agent 的动作拆开。

### 3.4.1 比如一个简单 agent 的步骤可能是：
1. 理解用户问题
2. 判断是否需要工具
3. 生成工具参数
4. 调用工具
5. 根据工具结果生成最终答案
6. 结束

这些步骤在 LangGraph 里通常就是节点。

---

## 3.5 第五步：写 prompt / 决策规则
如果 agent 需要 LLM 判断下一步，那你就要写 prompt。

比如：
- 识别用户意图
- 判断该不该查订单
- 输出结构化 JSON
- 从多个工具中选一个

### 3.5.1 推荐做法
不要让模型自由说太多，最好让它输出固定结构：

```json
{
  "intent": "query_order",
  "next_step": "call_tool",
  "tool_name": "get_order_info",
  "tool_input": {
    "order_id": "A12345"
  }
}
```

这样后续节点更稳定。

---

## 3.6 第六步：实现工具
如果 agent 需要操作外部系统，就要自己实现工具。

例如：

```python
def get_order_info(order_id: str) -> str:
    return f"订单 {order_id} 状态：已发货"
```

或者更复杂一些：
- 调数据库
- 调 HTTP API
- 查向量库
- 调内部服务

### 3.6.1 你要考虑
- 输入参数校验
- 返回值格式
- 异常处理
- 超时
- 权限

---

## 3.7 第七步：写节点函数
在 LangGraph 中，agent 的步骤一般都写成节点函数。

例如：

```python
def decide_node(state: AgentState):
    # 调 LLM 做决策
    return {
        "next_step": "call_tool",
        "tool_name": "get_order_info",
        "tool_input": {"order_id": "A12345"}
    }
```

```python
def tool_node(state: AgentState):
    result = get_order_info(state["tool_input"]["order_id"])
    return {"tool_result": result}
```

```python
def answer_node(state: AgentState):
    return {"final_answer": f"查询结果：{state['tool_result']}"}
```

---

## 3.8 第八步：定义路由逻辑
agent 不是只有节点，还要定义：
> 当前状态下下一步去哪

例如：

```python
def route_after_decide(state: AgentState):
    return state["next_step"]
```

然后映射：
- `call_tool` → 工具节点
- `respond` → 回答节点
- `end` → 结束

---

## 3.9 第九步：定义终止条件
你必须决定 agent 什么时候停。

常见方式：
- `final_answer` 已生成
- `next_step == "end"`
- 工具执行完成且无需继续
- 超过最大轮数
- 出现错误

==如果没有结束条件，agent 容易循环。==

---

## 3.10 第十步：处理错误和异常
自己写 agent 时，别只考虑“正常路径”。

你还要考虑：
- 模型输出非法 JSON
- 模型没返回 `next_step`
- 工具参数缺失
- 工具调用失败
- API 超时
- 用户输入不完整

### 3.10.1 建议 state 里带上
```python
error: str
retry_count: int
```

并设计：
- 重试节点
- fallback 节点
- 错误结束节点

---

# 4 四、如果从工程角度看，自己写一个 agent 的最小清单是什么？

最小需要这几项：

## 4.1 必须有
1. **State**
2. **LLM**
3. **Prompt**
4. **节点函数**
5. **路由逻辑**
6. **结束条件**

## 4.2 常见还需要
7. **工具**
8. **结构化输出解析**
9. **异常处理**
10. **日志**
11. **记忆/持久化**

---

# 5 五、一个 agent 的最小结构长什么样

你可以把它理解成这个公式：

> **Agent = 决策器 + 执行器 + 状态容器 + 路由器**

拆开看：

- **决策器**：LLM / 规则，决定下一步
- **执行器**：工具、检索、API 调用
- **状态容器**：保存 messages / tool_result / next_step 等
- **路由器**：决定图流转到哪个节点

---

# 6 最小可落地示例思路

假设你要自己写一个“订单查询 agent”，你要做的是：

## 6.1 定义 state
```python
class AgentState(TypedDict, total=False):
    user_input: str
    next_step: str
    tool_input: dict
    tool_result: str
    final_answer: str
```

## 6.2 定义 agent 决策节点
- 如果用户提到“订单状态”
- 就设置 `next_step = "tool"`

## 6.3 定义工具节点
- 调用 `get_order_info`

## 6.4 定义回答节点
- 把工具结果转成自然语言

## 6.5 定义路由
- `decide -> tool -> answer -> END`

这就是一个完整 agent 了。

---

# 7 很多人理解错的一点

很多人以为“写 agent”就是：
- 写一个 system prompt
- 接一个模型
- 让它自己决定一切

但在 LangGraph 里，更推荐你这样理解：

> 写 agent = 设计状态机 + 给状态机接入 LLM 能力

所以重点不是 prompt 本身，而是：
- 状态怎么设计
- 节点怎么拆
- 工具怎么接
- 路由怎么控
- 异常怎么处理

---

# 8 如果你是初学者，我建议你按这个顺序写 agent

## 8.1 第一版
只做：
- 一个决策节点
- 一个工具节点
- 一个回答节点

## 8.2 第二版
再加：
- 结构化输出
- 工具参数提取
- 错误处理

## 8.3 第三版
再加：
- memory
- checkpoint
- interrupt
- human approval

## 8.4 第四版
最后再考虑：
- 多 agent
- supervisor
- 并行分支
- 审核机制

---

# 9 结论

如果你问：
> agent 自身包含什么？
答案是：
> **目标、上下文、状态、模型、工具、决策逻辑、输出和约束。**
如果你问：
> 我要自己写一个 agent，需要做什么？
答案是：
> **先定义职责，再设计 state，然后拆节点、接模型、接工具、写路由、定结束条件、补异常处理。**
---

如果你愿意，我下一步可以直接给你这 3 种内容之一：

1. **一个 LangGraph 自定义 agent 的最小代码模板**
2. **一个“开源模型 API + LangGraph” 的完整 demo**
3. **根据你的业务场景，帮你设计一个 agent 的 State / Node / Tool / Route**

如果你想要最实用的，我建议你下一句直接说：

**“给我一个自己写 LangGraph agent 的最小模板”**

我可以直接把代码骨架给你。