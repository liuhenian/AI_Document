# AI 助手的 Skill 体系与自定义数据源接入指南

> **文档说明**：本文档分两部分解答——第一部分系统讲解 AI 助手中 Skill 的概念、架构与使用方法；第二部分详细说明如何将自定义数据源接入多 Agent 系统。  
> **日期**：2026-06-27

---

## 目录

### 第一部分：Skill 是什么？如何使用？
1. [Skill 的定义与本质](#一skill-的定义与本质)
2. [Skill 的三层架构模型](#二skill-的三层架构模型)
3. [Skill vs Tool：关键区别](#三skill-vs-tool关键区别)
4. [Skill 的四大类型](#四skill-的四大类型)
5. [Skill 的生命周期：创建 → 使用 → 进化](#五skill-的生命周期创建--使用--进化)
6. [各框架中 Skill 的具体实现](#六各框架中-skill-的具体实现)
7. [Skill 使用实战示例](#七skill-使用实战示例)

### 第二部分：自定义数据源如何接入？
8. [自定义数据源接入的三层架构](#八自定义数据源接入的三层架构)
9. [第一层：数据连接器（Connector）](#九第一层数据连接器connector)
10. [第二层：MCP 协议封装](#十第二层mcp-协议封装)
11. [第三层：RAG 检索融合](#十一第三层rag-检索融合)
12. [完整接入示例：从自定义 API 到 Agent 可用](#十二完整接入示例从自定义-api-到-agent-可用)
13. [各框架的数据源接入方式对比](#十三各框架的数据源接入方式对比)
14. [接入决策建议](#十四接入决策建议)

---

# 第一部分：Skill 是什么？如何使用？

## 一、Skill 的定义与本质

### 1.1 一句话定义

> **Skill（技能）是 AI 助手中一种模块化、可复用的能力封装单元——它不只包含执行逻辑，还携带语义描述、触发条件和输出规范，让 Agent 像调用"专家"一样使用它。**

### 1.2 为什么需要 Skill

传统 AI 助手的工具调用存在三个痛点：

| 痛点 | 说明 | Skill 如何解决 |
|------|------|---------------|
| **能力不可复用** | 每次任务都要重新写调用逻辑 | Skill 封装为独立单元，即插即用 |
| **语义不透明** | LLM 不知道何时该用什么工具 | Skill 携带语义描述，LLM 自主判断激活 |
| **维护散乱** | 工具逻辑分散在各业务代码中 | Skill 集中管理，版本可控 |

### 1.3 核心类比

```
传统 Tool Call  ≈  给 Agent 一把锤子（单一函数）
Agent Skill     ≈  给 Agent 一个"木工专家"（完整能力包）
                   ├── 知道什么时候该出手（语义层）
                   ├── 知道怎么干活（执行层）
                   └── 知道干完怎么汇报（感知层）
```

---

## 二、Skill 的三层架构模型

一个设计良好的 Skill 由三层构成：

```
┌─────────────────────────────────────────────────┐
│              Skill 三层架构                       │
│                                                  │
│  ┌───────────────────────────────────┐          │
│  │  语义层（Semantic Layer）          │          │
│  │  "大脑"——告诉 LLM 这是什么能力    │          │
│  │                                   │          │
│  │  • 技能名称与描述（SKILL.md）      │          │
│  │  • 适用场景定义                    │          │
│  │  • 触发条件                        │          │
│  │  • 参数规范                        │          │
│  └──────────────┬────────────────────┘          │
│                 │                                │
│  ┌──────────────▼────────────────────┐          │
│  │  执行层（Execution Layer）         │          │
│  │  "手脚"——实际干活的部分            │          │
│  │                                   │          │
│  │  • 工具调用序列                    │          │
│  │  • 代码 / 脚本                     │          │
│  │  • API 调用                        │          │
│  │  • 沙箱隔离与权限控制              │          │
│  └──────────────┬────────────────────┘          │
│                 │                                │
│  ┌──────────────▼────────────────────┐          │
│  │  感知层（Perception Layer）        │          │
│  │  "眼睛"——理解执行结果              │          │
│  │                                   │          │
│  │  • 结果解析与状态更新              │          │
│  │  • 上下文反馈                      │          │
│  │  • 下一步行动建议                  │          │
│  └───────────────────────────────────┘          │
└─────────────────────────────────────────────────┘
```

### 各层职责详解

| 层级 | 职责 | 关键产出 |
|------|------|---------|
| **语义层** | 让 LLM 理解"这个 Skill 是干什么的、什么时候用" | SKILL.md 描述文件 |
| **执行层** | 将 LLM 的概率性输出转化为系统可接受的确定性行为 | 工具调用 + 结果 |
| **感知层** | 解析结果、更新 Agent 状态、为下一步提供信息 | 上下文更新 |

---

## 三、Skill vs Tool：关键区别

这是理解 Skill 最重要的一张表：

| 对比维度 | 传统 Tool Call | Agent Skill |
|----------|---------------|-------------|
| **能力封装粒度** | 单一函数 / API | 完整语义能力单元 |
| **上下文感知** | 不具备，依赖外部传参 | 内置上下文匹配与语义理解 |
| **跨任务复用** | 困难，需手动适配 | 即插即用，模块化复用 |
| **安全边界** | 依赖调用方控制 | 内置沙箱隔离与权限约束 |
| **组合编排** | 线性调用，扩展性差 | 支持多技能动态组合与并行 |
| **维护成本** | 高（分散在业务代码中） | 低（集中管理，版本可控） |
| **典型形态** | `def search(query): ...` | SKILL.md + scripts/ + references/ |

**举个具体例子**：

```
Tool Call 方式：
  用户："帮我查一下这个月的销售数据"
  → Agent 调用 search_database(query="本月销售")
  → 返回原始数据
  → Agent 再调用 format_report(data)
  → Agent 再调用 send_email(...)
  （每一步都要 Agent 自己决定，容易出错）

Skill 方式：
  用户："帮我查一下这个月的销售数据"
  → Agent 匹配到 "monthly-sales-report" 技能
  → 技能自动执行完整流程：查询 → 分析 → 格式化 → 发送
  → 一步到位，流程已验证过
```

---

## 四、Skill 的四大类型

| 类型 | 说明 | 典型示例 |
|------|------|---------|
| **文档处理类** | 处理 PPT/Excel/Word/PDF 等文档 | 生成季度汇报 PPT、解析 Excel 数据 |
| **数据分析与搜索类** | 实时搜索、数据库查询、多源聚合 | 网络搜索、SQL 查询、数据聚合分析 |
| **流程自动化类** | 触发和协调其他系统/Agent | 审批流程、跨系统数据同步 |
| **行业定制类** | 针对特定业务场景定制 | 零售导购、金融风控、医疗问诊 |

---

## 五、Skill 的生命周期：创建 → 使用 → 进化

### 5.1 完整生命周期

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  创建   │ ──→ │  注册   │ ──→ │  使用   │ ──→ │  进化   │
│ Create  │     │ Register│     │  Use    │     │ Evolve  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     ↑                                               │
     └───────────────────────────────────────────────┘
                      循环改进
```

### 5.2 阶段一：创建 Skill

#### Skill 文件结构（agentskills.io 开放标准）

```
my-skill/
├── SKILL.md          # 语义层：技能描述文件（必须）
├── scripts/          # 执行层：脚本文件
│   ├── main.py
│   └── utils.py
└── references/       # 感知层：参考文档
    └── api-spec.md
```

#### SKILL.md 模板

```yaml
---
name: monthly-sales-report          # 技能名称（唯一标识）
description: |                       # 一句话描述（LLM 据此判断是否激活）
  从数据库查询月度销售数据，生成趋势分析图表，
  并发送到指定飞书群
version: 1.0.0                       # 版本号
platforms: [linux, macos]           # 支持平台
metadata:
  category: data-analysis            # 分类
  tags: [sales, report, chart]       # 标签
  requires_toolsets: [terminal, web] # 依赖的工具集
  fallback_for_toolsets: []          # 降级触发条件
---

# 月度销售报告技能

## 触发条件
- 用户要求查询销售数据
- 用户要求生成销售报告
- 定时任务触发（每月1号）

## 执行步骤
1. 连接数据库，查询本月销售数据
2. 使用 pandas 按产品线分组统计
3. 使用 matplotlib 生成趋势图
4. 调用飞书 API 发送图表到指定群

## 输入参数
- month: 查询月份（可选，默认当月）
- product_line: 产品线（可选，默认全部）
- chat_id: 飞书群 ID

## 输出格式
JSON：{"status": "success", "chart_path": "...", "sent": true}

## 已知限制
- 数据库连接超时时间为 30 秒
- 图表分辨率固定为 1920x1080
```

### 5.3 阶段二：注册与发现

```
Skill 注册流程

  SKILL.md 文件
       │
       ▼
  框架扫描技能目录（~/.skills/ 或项目 .skills/）
       │
       ▼
  解析 SKILL.md frontmatter
       │
       ▼
  注册到技能索引（只加载 name + description）
       │
       ▼
  Agent 运行时按需加载完整内容（渐进式披露）
```

**渐进式披露（Progressive Disclosure）** 是关键设计：

```
200 个技能注册
    │
    ├── 启动时：只加载名称 + 简介（< 200 Tokens 总量）
    │           ↑ 不随技能数量线性增长
    │
    └── 运行时：Agent 判断需要某个技能时，才加载完整内容
                ↑ 按需加载，控制上下文消耗
```

### 5.4 阶段三：使用 Skill

Agent 在运行时使用 Skill 的流程：

```
用户输入："帮我查一下本月销售数据"
       │
       ▼
Agent 读取技能索引（200个技能的名称+简介）
       │
       ▼
LLM 推理：匹配到 "monthly-sales-report" 技能
       │
       ▼
加载该技能的完整 SKILL.md 内容
       │
       ▼
LLM 按技能描述的步骤执行：
  ├── 调用 query_database 工具
  ├── 调用 execute_code 工具（pandas + matplotlib）
  └── 调用 send_feishu_message 工具
       │
       ▼
感知层：解析结果，更新状态，返回用户
```

### 5.5 阶段四：进化 Skill

Skill 不是一次创建就固定不变的，它应该持续进化：

| 进化方式 | 说明 | 触发时机 |
|----------|------|---------|
| **Patch（补丁）** | 只修改部分内容，保留已验证的部分 | 发现小错误或优化点 |
| **Edit（编辑）** | 修改较大范围的内容 | 流程有中等变化 |
| **Recreate（重建）** | 完全重写 | 流程发生根本变化 |
| **Delete（删除）** | 移除不再需要的技能 | 技能废弃 |

**最佳实践：优先使用 Patch 而非全量重写**，原因：
1. 保证正确性（全量重写可能把好用的部分改崩）
2. 省 Token
3. 执行更轻量

---

## 六、各框架中 Skill 的具体实现

| 框架 | Skill 实现方式 | 文件标准 | 自动进化 |
|------|--------------|---------|---------|
| **Hermes Agent** | `~/.hermes/skills/` 目录，SKILL.md 格式 | agentskills.io | ✅ 自动从实战生成 |
| **Claude（Anthropic）** | Agent Skills 框架，SKILL.md 规范 | agentskills.io | ❌ 手动创建 |
| **LangGraph** | 无原生 Skill 概念，用 Subgraph + Tool 组合 | 自定义 | ❌ |
| **CrewAI** | 无原生 Skill 概念，用 Agent + Task 组合 | 自定义 | ❌ |
| **Dify** | 通过 Workflow 模板 + 工具集实现类似功能 | 平台内 | ❌ |

**关键结论**：Skill 概念在 Hermes Agent 和 Claude 中是原生支持的，在 LangGraph / CrewAI 中需要自行实现类似机制。

---

## 七、Skill 使用实战示例

### 场景：为 AI 助手创建"客户工单处理"技能

#### 步骤 1：创建技能文件

```
~/.skills/handle-customer-ticket/
├── SKILL.md
├── scripts/
│   └── classify_ticket.py
└── references/
    └── ticket-categories.md
```

#### 步骤 2：编写 SKILL.md

```yaml
---
name: handle-customer-ticket
description: |
  接收客户工单，自动分类、查询历史、生成回复建议。
  适用于客服场景的工单处理全流程。
version: 1.0.0
metadata:
  category: customer-service
  tags: [ticket, support, classification]
  requires_toolsets: [terminal, web]
---

# 客户工单处理技能

## 执行步骤
1. 读取工单内容，使用 LLM 分类（退款/咨询/投诉/技术问题）
2. 查询该客户的历史工单（调用 CRM API）
3. 查询知识库中相关的解决方案（RAG 检索）
4. 生成回复建议，标记优先级
5. 如果优先级为"高"，自动升级到人工处理

## 输入
- ticket_id: 工单 ID
- ticket_content: 工单内容

## 输出
{
  "category": "退款",
  "priority": "high",
  "suggested_reply": "...",
  "history_tickets": [...],
  "escalated": true
}
```

#### 步骤 3：Agent 自动使用

```
用户："帮我处理工单 #T20260627001"
       │
       ▼
Agent 扫描技能索引 → 匹配 "handle-customer-ticket"
       │
       ▼
加载完整技能 → 按步骤执行
       │
       ├── 调用 LLM 分类 → "退款"
       ├── 调用 CRM API → 查到 3 条历史工单
       ├── 调用 RAG 检索 → 找到 2 条相关解决方案
       ├── 生成回复建议
       └── 优先级"高" → 标记升级人工
       │
       ▼
返回结果给用户
```

#### 步骤 4：技能进化

使用 5 次后，Agent 发现常见模式，自动 Patch 技能：

```diff
+ ## 优化规则
+ - 退款类工单如果金额 < 100 元，可直接自动退款，无需升级
+ - 技术问题类工单优先匹配知识库解决方案
```

---

# 第二部分：自定义数据源如何接入？

## 八、自定义数据源接入的三层架构

将自定义数据源接入多 Agent 系统，需要构建三层架构：

```
┌─────────────────────────────────────────────────────────┐
│                    Agent 层                              │
│  （LangGraph / CrewAI / Dify / Hermes 等）               │
│                                                          │
│  通过两种方式使用数据：                                   │
│  ① 作为 Tool——Agent 主动查询数据源                       │
│  ② 作为 RAG 知识——数据预先索引，Agent 检索使用           │
└────────────┬──────────────────────────┬─────────────────┘
             │                          │
             ▼                          ▼
┌────────────────────────┐  ┌─────────────────────────────┐
│  方式一：MCP 工具层     │  │  方式二：RAG 检索层          │
│  （实时查询）           │  │  （预索引检索）              │
│                        │  │                             │
│  数据源 → MCP Server   │  │  数据源 → 摄取管道           │
│  → Agent 直接调用      │  │  → 向量化 → 向量库           │
│                        │  │  → RAG 检索 → Agent 使用     │
└────────────┬───────────┘  └─────────────┬───────────────┘
             │                            │
             ▼                            ▼
┌─────────────────────────────────────────────────────────┐
│              第一层：数据连接器（Connector）               │
│                                                          │
│  统一抽象：BaseDataConnector                             │
│  具体实现：你的自定义数据源 Connector                     │
│  （API / 数据库 / 文件系统 / S3 / ...）                  │
└─────────────────────────────────────────────────────────┘
```

### 两种接入方式的选择

| 维度 | 方式一：MCP 工具层（实时查询） | 方式二：RAG 检索层（预索引） |
|------|---------------------------|------------------------|
| **数据时效性** | 实时，每次查询最新数据 | 有延迟，依赖同步频率 |
| **查询方式** | 结构化查询（SQL/API） | 语义检索（向量相似度） |
| **适合数据** | 交易数据、实时库存、用户状态 | 文档、知识库、历史记录 |
| **Agent 负担** | 较重（需构造查询参数） | 较轻（自然语言检索） |
| **实施复杂度** | 中（封装 API 为工具） | 高（需建索引管道） |

**实际项目中，两种方式通常组合使用。**

---

## 九、第一层：数据连接器（Connector）

### 9.1 统一抽象基类

无论你的数据源是什么类型，都应该实现统一的连接器接口：

```python
from abc import ABC, abstractmethod
from typing import List, Dict, AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class SyncMode(Enum):
    FULL = "full"           # 全量同步
    INCREMENTAL = "incremental"  # 增量同步

@dataclass
class DataSourceConfig:
    """统一数据源配置"""
    source_id: str          # 数据源唯一标识
    source_type: str        # 类型：api / database / file / s3 ...
    connection_params: Dict # 连接参数
    sync_mode: SyncMode     # 同步模式
    sync_schedule: str      # 同步计划（cron 表达式）
    filters: Dict           # 过滤条件

@dataclass
class Document:
    """统一文档对象——所有数据源的数据都转为这个格式"""
    doc_id: str             # 文档唯一 ID
    content: str            # 文本内容
    metadata: Dict          # 元数据（来源、时间、类型等）
    source_type: str        # 来源类型
    checksum: str           # 校验和（用于增量同步去重）

class BaseDataConnector(ABC):
    """数据连接器基类——所有自定义数据源都要继承此类"""

    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.last_sync_time: datetime = None

    @abstractmethod
    async def connect(self) -> bool:
        """建立连接"""
        pass

    @abstractmethod
    async def list_documents(self, since: datetime = None) -> List[Dict]:
        """列出文档（支持增量：只列出 since 之后变更的）"""
        pass

    @abstractmethod
    async def fetch_document(self, doc_id: str) -> Document:
        """获取单个文档的完整内容"""
        pass

    @abstractmethod
    async def stream_documents(self, batch_size: int = 100) -> AsyncIterator[List[Document]]:
        """流式批量获取文档（控制内存）"""
        pass

    @abstractmethod
    async def query(self, params: Dict) -> List[Dict]:
        """实时查询（供 MCP 工具层使用）"""
        pass
```

### 9.2 实现自定义数据源连接器

假设你的数据源是一个内部 REST API：

```python
import httpx
from datetime import datetime

class CustomAPIDataConnector(BaseDataConnector):
    """自定义 REST API 数据源连接器"""

    async def connect(self) -> bool:
        """测试 API 连通性"""
        base_url = self.config.connection_params["base_url"]
        api_key = self.config.connection_params["api_key"]
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{base_url}/health",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            return resp.status_code == 200

    async def list_documents(self, since: datetime = None) -> List[Dict]:
        """列出 API 中的数据项"""
        base_url = self.config.connection_params["base_url"]
        api_key = self.config.connection_params["api_key"]
        endpoint = self.config.connection_params.get("list_endpoint", "/items")

        params = {}
        if since and self.config.sync_mode == SyncMode.INCREMENTAL:
            params["updated_after"] = since.isoformat()

        # 应用过滤条件
        params.update(self.config.filters)

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{base_url}{endpoint}",
                headers={"Authorization": f"Bearer {api_key}"},
                params=params
            )
            resp.raise_for_status()
            return resp.json()["data"]

    async def fetch_document(self, doc_id: str) -> Document:
        """获取单条数据详情"""
        base_url = self.config.connection_params["base_url"]
        api_key = self.config.connection_params["api_key"]

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{base_url}/items/{doc_id}",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            resp.raise_for_status()
            data = resp.json()

            return Document(
                doc_id=str(data["id"]),
                content=data.get("content", ""),
                metadata={
                    "title": data.get("title"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "category": data.get("category"),
                },
                source_type="custom_api",
                checksum=str(hash(data.get("content", "")))
            )

    async def stream_documents(self, batch_size: int = 100) -> AsyncIterator[List[Document]]:
        """分批流式获取文档"""
        docs_meta = await self.list_documents(since=self.last_sync_time)
        batch = []
        for meta in docs_meta:
            doc = await self.fetch_document(meta["id"])
            batch.append(doc)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    async def query(self, params: Dict) -> List[Dict]:
        """实时查询接口——供 MCP 工具层调用"""
        base_url = self.config.connection_params["base_url"]
        api_key = self.config.connection_params["api_key"]
        query_endpoint = self.config.connection_params.get("query_endpoint", "/query")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}{query_endpoint}",
                headers={"Authorization": f"Bearer {api_key}"},
                json=params
            )
            resp.raise_for_status()
            return resp.json()["data"]
```

### 9.3 配置与使用

```python
# 配置你的自定义数据源
config = DataSourceConfig(
    source_id="internal-crm-api",
    source_type="api",
    connection_params={
        "base_url": "https://internal.company.com/api/v1",
        "api_key": "your-api-key-here",
        "list_endpoint": "/customers",
        "query_endpoint": "/customers/search"
    },
    sync_mode=SyncMode.INCREMENTAL,
    sync_schedule="0 */6 * * *",  # 每6小时同步一次
    filters={
        "status": "active",
        "type": "enterprise"
    }
)

# 创建连接器
connector = CustomAPIDataConnector(config)
await connector.connect()
```

---

## 十、第二层：MCP 协议封装

### 10.1 为什么用 MCP 封装

MCP（Model Context Protocol）是 Anthropic 发布的标准化协议，将你的数据源封装为 MCP Server 后：

- 任何支持 MCP 的 Agent 框架都能直接使用你的数据源
- 工具描述、参数校验、权限控制都标准化
- 一次封装，到处复用

### 10.2 将自定义数据源封装为 MCP Server

```python
from mcp import Server, Tool, TextContent
import json

class CustomDataMCPServer:
    """将自定义数据源封装为 MCP Server"""

    def __init__(self, connector: BaseDataConnector):
        self.connector = connector
        self.server = Server("custom-datasource")
        self._setup_handlers()

    def _setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="data_search",
                    description="搜索自定义数据源中的数据。支持按关键词、分类、时间范围查询。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "keyword": {
                                "type": "string",
                                "description": "搜索关键词"
                            },
                            "category": {
                                "type": "string",
                                "description": "数据分类（可选）"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回结果数量上限",
                                "default": 10
                            }
                        },
                        "required": ["keyword"]
                    }
                ),
                Tool(
                    name="data_get_detail",
                    description="根据 ID 获取单条数据的详细信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "doc_id": {
                                "type": "string",
                                "description": "数据项 ID"
                            }
                        },
                        "required": ["doc_id"]
                    }
                ),
                Tool(
                    name="data_list_recent",
                    description="列出最近更新的数据项",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "hours": {
                                "type": "integer",
                                "description": "查询最近多少小时内的数据",
                                "default": 24
                            }
                        }
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            if name == "data_search":
                result = await self.connector.query({
                    "keyword": arguments["keyword"],
                    "category": arguments.get("category"),
                    "limit": arguments.get("limit", 10)
                })
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

            elif name == "data_get_detail":
                doc = await self.connector.fetch_document(arguments["doc_id"])
                return [TextContent(type="text", text=json.dumps({
                    "id": doc.doc_id,
                    "content": doc.content,
                    "metadata": doc.metadata
                }, ensure_ascii=False))]

            elif name == "data_list_recent":
                from datetime import datetime, timedelta
                since = datetime.now() - timedelta(hours=arguments.get("hours", 24))
                docs = await self.connector.list_documents(since=since)
                return [TextContent(type="text", text=json.dumps(docs, ensure_ascii=False))]

    async def run(self):
        """启动 MCP Server"""
        async with self.server.run_stdio() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)
```

### 10.3 MCP 服务注册中心

多个数据源可以统一注册管理：

```python
class MCPRegistry:
    """MCP 服务注册中心——统一管理多个数据源"""

    def __init__(self):
        self.servers = {}
        self.tools_cache = {}

    def register_server(self, name: str, server):
        self.servers[name] = server

    async def discover_tools(self) -> Dict[str, list]:
        """发现所有已注册数据源的工具"""
        all_tools = {}
        for name, server in self.servers.items():
            tools = await server.server.list_tools()
            all_tools[name] = tools
            self.tools_cache[name] = tools
        return all_tools

    async def execute_tool(self, server_name, tool_name, arguments):
        """执行指定数据源的工具"""
        server = self.servers[server_name]
        return await server.execute_tool(tool_name, arguments)

# 使用示例
registry = MCPRegistry()

# 注册自定义 API 数据源
api_connector = CustomAPIDataConnector(api_config)
api_server = CustomDataMCPServer(api_connector)
registry.register_server("custom-api", api_server)

# 注册数据库数据源
# db_connector = DatabaseConnector(db_config)
# db_server = DatabaseMCPServer(db_connector)
# registry.register_server("internal-db", db_server)

# 发现所有工具
tools = await registry.discover_tools()
```

---

## 十一、第三层：RAG 检索融合

### 11.1 数据摄取管道

将自定义数据源的数据预处理为向量索引：

```python
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding

class DataIngestionPipeline:
    """数据摄取管道：数据源 → 分块 → 向量化 → 存储"""

    def __init__(self, vector_store, embed_model=None):
        self.vector_store = vector_store
        self.text_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=200)
        self.embed_model = embed_model or OpenAIEmbedding(model="text-embedding-3-large")

    async def ingest_from_source(self, connector: BaseDataConnector):
        """从数据源摄取数据到向量库"""
        total_processed = 0

        async for batch in connector.stream_documents(batch_size=50):
            for doc in batch:
                # 1. 文本分块
                chunks = self.text_splitter.split_text(doc.content)

                # 2. 生成 Embedding
                embeddings = []
                for chunk in chunks:
                    embedding = self.embed_model.get_text_embedding(chunk)
                    embeddings.append({
                        "id": f"{doc.doc_id}_{len(embeddings)}",
                        "content": chunk,
                        "embedding": embedding,
                        "metadata": {
                            **doc.metadata,
                            "doc_id": doc.doc_id,
                            "source_type": doc.source_type,
                            "chunk_index": len(embeddings)
                        }
                    })

                # 3. 写入向量库
                self.vector_store.upsert(embeddings)
                total_processed += 1

            print(f"已处理 {total_processed} 篇文档")

        return {"total_processed": total_processed}
```

### 11.2 混合 RAG 检索器

```python
class HybridRAGRetriever:
    """混合检索：向量检索 + 关键词检索 + 重排序"""

    def __init__(self, vector_store, keyword_index=None, reranker=None):
        self.vector_store = vector_store
        self.keyword_index = keyword_index  # BM25 索引（可选）
        self.reranker = reranker            # Cross-Encoder 重排序器（可选）

    async def retrieve(self, query: str, top_k: int = 5, filters: Dict = None):
        results = []

        # 1. 向量检索
        query_embedding = self.embed_model.get_text_embedding(query)
        vector_results = self.vector_store.search(
            query_embedding, top_k=top_k * 3, filters=filters
        )
        results.extend(vector_results)

        # 2. 关键词检索（可选）
        if self.keyword_index:
            keyword_results = self.keyword_index.search(query, top_k=top_k * 2)
            results.extend(keyword_results)

        # 3. 去重合并
        seen_ids = set()
        unique_results = []
        for r in results:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                unique_results.append(r)

        # 4. 重排序（可选）
        if self.reranker:
            unique_results = self.reranker.rerank(query, unique_results, top_k=top_k)
        else:
            unique_results = unique_results[:top_k]

        return unique_results
```

### 11.3 自适应 RAG（根据查询复杂度选择策略）

```python
class AdaptiveRAG:
    """自适应 RAG：根据查询复杂度动态选择检索策略"""

    def __init__(self, retriever: HybridRAGRetriever, llm):
        self.retriever = retriever
        self.llm = llm

    async def query(self, question: str, user_context: Dict = None):
        # 1. 分析查询复杂度
        complexity = await self._analyze_complexity(question)

        if complexity == "simple":
            # 简单查询：直接检索 Top 3
            results = await self.retriever.retrieve(question, top_k=3)
            return await self._generate_answer(question, results)

        elif complexity == "medium":
            # 中等查询：多跳检索
            sub_queries = await self._decompose_query(question)
            all_results = []
            for sq in sub_queries:
                results = await self.retriever.retrieve(sq, top_k=3)
                all_results.extend(results)
            return await self._generate_answer(question, all_results)

        else:
            # 复杂查询：Agent 式迭代检索
            return await self._agent_based_retrieve(question)

    async def _analyze_complexity(self, query: str) -> str:
        """使用 LLM 判断查询复杂度"""
        prompt = f"判断以下查询的复杂度（simple/medium/complex）：\n{query}"
        response = await self.llm.complete(prompt)
        return response.text.strip().lower()
```

---

## 十二、完整接入示例：从自定义 API 到 Agent 可用

### 完整流程图

```
你的自定义数据源（REST API）
       │
       ▼
┌──────────────────────────────────┐
│  第1步：实现 Connector            │
│  CustomAPIDataConnector          │
│  （连接、列表、获取、查询）        │
└──────────────┬───────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐  ┌──────────────────┐
│  第2步A：     │  │  第2步B：         │
│  MCP 封装     │  │  RAG 摄取管道     │
│  （实时查询） │  │  （预索引检索）   │
│              │  │                  │
│  暴露3个工具：│  │  分块→向量化     │
│  data_search │  │  →写入向量库      │
│  data_get    │  │                  │
│  data_list   │  │                  │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       ▼                   ▼
┌──────────────────────────────────┐
│  第3步：接入 Agent 框架           │
│                                  │
│  方式A：在 LangGraph 中注册为 Tool│
│  方式B：在 Dify 中配置为知识库    │
│  方式C：在 Hermes 中通过 MCP 加载 │
└──────────────────────────────────┘
```

### 在不同框架中的接入代码

#### 方式 A：LangGraph 中接入

```python
from langgraph.graph import StateGraph, END

# 1. 创建 Connector
connector = CustomAPIDataConnector(config)
await connector.connect()

# 2. 定义 Agent 可调用的工具函数
async def search_custom_data(keyword: str, category: str = None, limit: int = 10):
    """搜索自定义数据源"""
    results = await connector.query({
        "keyword": keyword,
        "category": category,
        "limit": limit
    })
    return results

# 3. 将工具绑定到 Agent
tools = [search_custom_data]
agent = create_react_agent(llm, tools)

# 4. 在 Graph 中使用
graph = StateGraph(AgentState)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
graph.add_edge("tools", "agent")
app = graph.compile()
```

#### 方式 B：Dify 中接入

```
Dify 接入步骤（无代码）：
1. 进入 Dify → 知识库 → 添加数据源
2. 选择"外部 API"类型
3. 填写：
   - API 地址：https://internal.company.com/api/v1/items
   - 认证方式：Bearer Token
   - 请求参数映射
4. 配置同步频率
5. Dify 自动完成：分块 → 向量化 → 索引
6. 在 Workflow 中添加"知识库检索"节点即可使用
```

#### 方式 C：通过 MCP 接入（框架无关）

```python
# 1. 启动 MCP Server
connector = CustomAPIDataConnector(config)
mcp_server = CustomDataMCPServer(connector)

# 2. 在 MCP 配置文件中注册
# ~/.workbuddy/mcp.json 或 框架的 MCP 配置
{
    "mcpServers": {
        "custom-datasource": {
            "command": "python",
            "args": ["path/to/mcp_server.py"],
            "env": {
                "API_BASE_URL": "https://internal.company.com/api/v1",
                "API_KEY": "your-key"
            }
        }
    }
}

# 3. 任何支持 MCP 的框架都能自动发现和使用这些工具
```

---

## 十三、各框架的数据源接入方式对比

| 框架 | 接入方式 | 代码量 | 灵活性 | 适合数据源类型 |
|------|---------|--------|--------|-------------|
| **LangGraph** | 自定义 Tool 函数 | 中 | ⭐⭐⭐⭐⭐ | 任何（API/DB/文件） |
| **Dify** | 知识库配置 + 外部工具 | 极低 | ⭐⭐⭐ | API/文件/数据库 |
| **CrewAI** | BaseTool 子类 | 低 | ⭐⭐⭐⭐ | API/DB/文件 |
| **Hermes** | MCP Server 或 插件 | 中 | ⭐⭐⭐⭐⭐ | 任何 |
| **通用 MCP** | MCP Server 封装 | 中 | ⭐⭐⭐⭐⭐ | 任何（一次封装到处用） |

---

## 十四、接入决策建议

### 14.1 决策树

```
你的自定义数据源是什么类型？
│
├── 结构化数据（数据库/API），需要实时查询？
│   └── 用 MCP 工具层方式（方式A）
│       └── 将数据源封装为 MCP Server → Agent 直接调用
│
├── 非结构化文档（PDF/Word/网页），需要语义检索？
│   └── 用 RAG 检索层方式（方式B）
│       └── 数据摄取 → 向量化 → RAG 检索
│
└── 两者都有？
    └── 组合使用：MCP 工具层 + RAG 检索层
        └── 结构化查询走 MCP，语义检索走 RAG
```

### 14.2 实施建议

| 阶段 | 建议动作 | 预计时间 |
|------|---------|---------|
| **第1周** | 实现 Connector 基类 + 你的自定义 Connector | 2-3 天 |
| **第1-2周** | 选择接入方式（MCP 或 RAG），实现封装 | 3-5 天 |
| **第2-3周** | 接入 Agent 框架，测试端到端流程 | 3-5 天 |
| **第3-4周** | 增量同步、性能优化、监控告警 | 3-5 天 |

### 14.3 安全注意事项

| 安全项 | 建议 |
|--------|------|
| **API 密钥管理** | 使用环境变量或密钥管理服务，不要硬编码 |
| **权限最小化** | 数据源 Connector 只授予必要的读权限 |
| **沙箱隔离** | 代码执行类操作在 Docker 沙箱中运行 |
| **审计日志** | 记录每次数据查询的来源、参数、结果 |
| **数据脱敏** | 敏感字段在进入 LLM 上下文前脱敏 |
| **速率限制** | 对数据源 API 设置调用频率上限 |

---

## 附录：Skill 与数据源接入的关系

```
Skill（技能）和 数据源接入 的关系：

  数据源接入 = 让 Agent "能访问"你的数据
  Skill（技能）= 让 Agent "知道怎么用"这些数据

  完整链路：
  自定义数据源 → Connector → MCP/RAG 封装 → Agent 可用
                                                  ↓
                                          被封装进 Skill
                                          （Skill 定义了
                                           "何时用、怎么用、
                                            用完怎么处理"）
                                                  ↓
                                          用户一句话触发
                                          → Skill 自动执行
                                          → 调用数据源
                                          → 返回结果
```

---

*文档版本：v1.0 | 整理日期：2026-06-27*
