我先查看澄清节点与意图解析节点的完整逻辑，确保状态推演准确。



Read , lines 1 to 140

让我查看意图解析节点与澄清节点的其余逻辑，以准确推演状态流转。



Searched for regex `def intent_resolution_node|dialogue_phase\s*=|next_stage\s*=` (`**/apm_ai_canvas/nodes/*.py`), 12 results

Read , lines 140 to 260

让我读取意图解析节点与澄清节点剩余逻辑，确保状态推演准确。



Read , lines 260 to 460

Read , lines 150 to 320

我需要确认流程结束节点的状态设置，以保证状态机推演准确。



Read , lines 300 to 300

Read 

我需要确认澄清节点生成追问后的 `dialogue_phase` 设置，以准确推演状态。读取 `clarify_intent_node` 剩余部分。



Read , lines 460 to 547

让我确认意图解析节点对不支持操作分支的 `dialogue_phase` 设置，确保状态推演准确。



Read , lines 318 to 420

我已充分梳理了整个多轮对话状态机（会话控制 → 意图解析 → 参数解析 → 澄清 → 测试结束，以及 5 轮触发的对话压缩）。以下是一份完整的多轮对话测试设计文档。

---

# 1 多轮对话意图状态机测试设计

## 1.1 一、状态机总览

### 1.1.1 节点流转（每轮用户输入）
```
会话控制(session_controller) → 意图解析(intent_resolution) → 参数解析(parameter_extraction) → 澄清(clarify_intent) / 测试结束(test_end)
```

### 1.1.2 关键状态字段
| 字段 | 取值/含义 |
|---|---|
| `dialogue_phase` | `idle` / `processing` / `paused`(等待澄清回复) / `slot_filling`(澄清回复处理中) / `new_intent`(澄清中打断) / `unsupported_operation` |
| `next_stage` | `session_controller` / `intent_resolution` / `parameter_extraction` / `clarify_intent` / `diagnosis_planning` / `end` |
| `parsed_intents[].stage` | `parameter_extraction` / `waiting_clarification` / `suspended` / `ready_for_planning` / `completed` / `failed` |
| `active_intent_id` | 当前焦点意图（本轮新解析意图 + 澄清恢复意图） |
| `pending_clarifications` | `{intent_id: [缺失项...]}`，一次只澄清一个意图 |
| `extraction_targets` | 本轮待参数提取的 intent_id 列表 |

### 1.1.3 压缩逻辑（`_compact_history`）
- 触发条件：对话**轮数 > 5**（用户消息轮次计数）
- 动作：仅保留最近 **3** 轮，清理对应轮次产生的意图
- 保护规则：**父意图保护**（被保留意图引用为父意图的意图不删）+ **executing 保护**
- 重编号：清理后按 `intent_1..N` 重新编号，同步 `active_intent_id`/`last_completed_intent_id`/`extraction_targets`/`pending_*`/`parent_intent_id`

### 1.1.4 测试用设备池（全部 device_id=1, slot_id=30，以 IP 区分）
```
10.110.186.140 / 10.110.187.41 / 10.96.4.206 / 10.96.4.248 / 10.96.4.249 / 10.96.5.4
```

---

## 1.2 二、测试场景与意图状态（分场景独立会话）

### 1.2.1 场景 A：单意图完整流程（无澄清）

**A1**：`10.110.186.140 的CPU使用率`

| 节点 | 动作 | 状态变化 |
|---|---|---|
| 意图解析 | `simple_metric_query`，metrics=`process_cpu_usage`，parent=null | 生成 `intent_1`(stage=parameter_extraction)，`intent_counter=1` |
| 参数解析 | 提取实体 ip，设备验证通过，无缺失 | `intent_1` → `ready_for_planning` |
| 测试结束 | 标记完成 | `intent_1` → `completed` |

**完成后状态机信息：**
```json
{
  "dialogue_phase": "idle",
  "next_stage": "end",
  "intent_counter": 1,
  "active_intent_id": [],
  "extraction_targets": [],
  "last_completed_intent_id": ["intent_1"],
  "parsed_intents": [
    {"id": "intent_1", "stage": "completed", "parent_intent_id": null,
     "intent_type": "simple_metric_query", "metrics": ["process_cpu_usage"]}
  ],
  "pending_clarifications": {}
}
```
✅ **断言**：无缺失 → 一次直达 completed；active/extraction 清空。

---

### 1.2.2 场景 B：追问（同实体换指标，继承父意图实体）

**B1**：`10.110.186.140 的CPU使用率`（同 A1 → `intent_1` completed）

**B2**：`它的内存呢？`

| 节点 | 动作 | 状态变化 |
|---|---|---|
| 意图解析 | 结合历史识别为追问 → 新意图 parent=`intent_1`，metrics=`process_mem_usage` | 生成 `intent_2`，`intent_counter=2` |
| 参数解析 | 追问模式，继承父实体 ip=10.110.186.140，无缺失 | `intent_2` → `ready_for_planning` |
| 测试结束 | 标记完成 | `intent_2` → `completed` |

**完成后状态机信息：**
```json
{
  "dialogue_phase": "idle",
  "next_stage": "end",
  "intent_counter": 2,
  "active_intent_id": [],
  "last_completed_intent_id": ["intent_1", "intent_2"],
  "parsed_intents": [
    {"id": "intent_1", "stage": "completed", "parent_intent_id": null,
     "metrics": ["process_cpu_usage"]},
    {"id": "intent_2", "stage": "completed", "parent_intent_id": "intent_1",
     "metrics": ["process_mem_usage"], "target_entities": [{"type":"ip","name":"10.110.186.140"}]}
  ]
}
```
✅ **断言**：B2 继承 B1 实体且不带入 parent 的额外信息；`parent_intent_id=intent_1` 正确关联。

---

### 1.2.3 场景 C：澄清流程（参数缺失 → 追问 → 补充回复）

**C1**：`10.110.186.140 的端口丢包情况`（缺端口名）

| 节点 | 动作 | 状态变化 |
|---|---|---|
| 意图解析 | `simple_metric_query`，metrics=`intf_bw_drop` | 生成 `intent_1` |
| 参数解析 | 有 ip，但缺端口 `label` | `intent_1` → `waiting_clarification`；`pending_clarifications={"intent_1":[...]}` |
| 澄清节点 | 生成追问 | `dialogue_phase=paused`，`next_stage=end`，`final_response=追问` |

**完成后状态机信息：**
```json
{
  "dialogue_phase": "paused",
  "next_stage": "end",
  "intent_counter": 1,
  "active_intent_id": ["intent_1"],
  "pending_clarifications": {"intent_1": ["缺端口名..."]},
  "parsed_intents": [
    {"id": "intent_1", "stage": "waiting_clarification", "parent_intent_id": null,
     "target_entities": [{"type":"ip","name":"10.110.186.140"}]}
  ]
}
```

**C2**：`端口名是 HundredGigabitEthernet_1/3/17`

| 节点 | 动作 | 状态变化 |
|---|---|---|
| 会话控制 | `paused` → `slot_filling` | `next_stage=clarify_intent` |
| 澄清节点 | 判断为澄清回复（非新意图） | 恢复 `intent_1` 入 active，清空 pending，`dialogue_phase=processing` |
| 参数解析 | 澄清回复模式，继承 ip + 补全 label | `intent_1` → `ready_for_planning` |
| 测试结束 | 标记完成 | `intent_1` → `completed` |

**完成后状态机信息：**
```json
{
  "dialogue_phase": "idle",
  "next_stage": "end",
  "pending_clarifications": {},
  "active_intent_id": [],
  "parsed_intents": [
    {"id": "intent_1", "stage": "completed",
     "target_entities": [
       {"type":"ip","name":"10.110.186.140"},
       {"type":"label","name":"HundredGigabitEthernet_1/3/17"}],
     "metrics": ["intf_bw_drop"]}
  ]
}
```
✅ **断言**：C1 进入 paused + pending 记录；C2 走澄清回复路径复用原意图，不生成新意图，最终 completed。

---

### 1.2.4 场景 D：澄清期间提出新意图（打断旧澄清）

**D1**：`10.110.186.140 的端口丢包情况`（同 C1 → 进入澄清 `paused`，`intent_1` waiting_clarification）

**D2**：`10.96.4.206 的健康度怎么样`（不回答澄清，提出全新问题）

| 节点 | 动作 | 状态变化 |
|---|---|---|
| 会话控制 | `paused` → `slot_filling` | `next_stage=clarify_intent` |
| 澄清节点 | `_is_new_intent=true` → 全部未完成意图挂起，清空 pending | `intent_1` → `suspended`；`dialogue_phase=new_intent`，`next_stage=session_controller` |
| 会话控制 | `new_intent` → 转意图解析 | `dialogue_phase=processing` |
| 意图解析 | 全新 healthy 查询，parent=null | 生成 `intent_2`，`intent_counter=2` |
| 参数解析 | healthy 场景 ip-only 校验通过，无缺失 | `intent_2` → `ready_for_planning` |
| 测试结束 | 标记完成 | `intent_2` → `completed`；`intent_1` 保持 `suspended` |

**完成后状态机信息：**
```json
{
  "dialogue_phase": "idle",
  "next_stage": "end",
  "intent_counter": 2,
  "pending_clarifications": {},
  "active_intent_id": [],
  "last_completed_intent_id": ["intent_2"],
  "parsed_intents": [
    {"id": "intent_1", "stage": "suspended", "parent_intent_id": null, "metrics": ["intf_bw_drop"]},
    {"id": "intent_2", "stage": "completed", "parent_intent_id": null,
     "metrics": ["healthy"], "target_entities": [{"type":"ip","name":"10.96.4.206"}]}
  ]
}
```
✅ **断言**：新意图打断旧澄清；旧意图被 `suspended` 而非删除；`dialogue_phase` 经 `new_intent → processing` 正确流转。

---

### 1.2.5 场景 E：多意图复合（单句拆多个）

**E1**：`10.110.186.140 的CPU怎么样，10.96.4.248 的丢包率高吗？`

| 节点 | 动作 | 状态变化 |
|---|---|---|
| 意图解析 | `multi_intent` → 拆 2 个 | 生成 `intent_1`(cpu)、`intent_2`(丢包率)，`intent_counter=2`，均入 `active` + `extraction_targets` |
| 参数解析 | 两个意图均完整 | 均 → `ready_for_planning` |
| 测试结束 | 标记完成 | 均 → `completed` |

**完成后状态机信息：**
```json
{
  "dialogue_phase": "idle",
  "next_stage": "end",
  "intent_counter": 2,
  "active_intent_id": [],
  "extraction_targets": [],
  "last_completed_intent_id": ["intent_1", "intent_2"],
  "parsed_intents": [
    {"id": "intent_1", "stage": "completed", "parent_intent_id": null, "metrics": ["process_cpu_usage"], "target_entities": [{"type":"ip","name":"10.110.186.140"}]},
    {"id": "intent_2", "stage": "completed", "parent_intent_id": null, "metrics": ["intf_bw_usage"], "target_entities": [{"type":"ip","name":"10.96.4.248"}]}
  ]
}
```
✅ **断言**：单句多意图正确拆分、各自实体不串；两个意图独立 completed。

---

### 1.2.6 场景 F：不支持操作

**F1**：`重启 10.110.186.140`

| 节点 | 动作 | 状态变化 |
|---|---|---|
| 意图解析 | `general_chat` + errors=`["不支持的操作：重启设备..."]` | 生成 `intent_1`(stage=`failed`)，`dialogue_phase=unsupported_operation`，`next_stage=session_controller` |
| 会话控制 | 提取 errors 提示用户 | `final_response="当前不支持该操作：重启设备..."`，`dialogue_phase=idle`，`next_stage=end` |

**完成后状态机信息：**
```json
{
  "dialogue_phase": "idle",
  "next_stage": "end",
  "final_response": "当前不支持该操作：重启设备，仅支持指标/日志/告警/实体设备的查询",
  "parsed_intents": [
    {"id": "intent_1", "stage": "failed", "parent_intent_id": null,
     "intent_type": "general_chat", "errors": ["不支持的操作：重启设备，仅支持指标/日志/告警/实体设备的查询"]}
  ]
}
```
✅ **断言**：变更操作标记 `failed`，经 `unsupported_operation` 回到会话控制提示后恢复 idle。

---

## 1.3 三、对话压缩专项测试（>5 轮触发）

### 1.3.1 场景 G：连续多轮 + 父意图保护

**G1**：`10.110.186.140 的CPU使用率` → `intent_1` completed
**G2**：`它的内存呢？` → `intent_2`(parent=`intent_1`) completed
**G3**：`10.96.4.206 的CPU使用率` → `intent_3` completed
**G4**：`10.96.4.248 的磁盘使用率` → `intent_4` completed
**G5**：`10.96.4.249 的CPU使用率` → `intent_5` completed

此时 `rounds=5`（未超阈值），`intent_counter=5`。

**G6**：`10.96.5.4 的内存使用率` —— **触发压缩**（rounds=6 > 5）

| 步骤 | 动作 | 结果 |
|---|---|---|
| `_compact_history` | 保留最近 3 轮（G4,G5,G6），清理 G1~G3 | `removed_count=3` |
| 父意图保护 | `intent_2.parent=intent_1` → **`intent_1` 被保护，不能删** | 实际删除 `intent_2,intent_3,intent_4`（3 个） |
| 重编号 | 剩余 `intent_1, intent_5` 重新编号 | `intent_1→intent_1`、`intent_5→intent_2`，`intent_counter=2` |
| 意图解析 | 新查询 | 生成 `intent_3`(10.96.5.4 内存) |
| 参数解析+结束 | 无缺失 | `intent_3` → completed |

**G6 完成后状态机信息：**
```json
{
  "dialogue_phase": "idle",
  "next_stage": "end",
  "intent_counter": 3,
  "last_completed_intent_id": ["intent_3"],
  "parsed_intents": [
    {"id": "intent_1", "stage": "completed", "parent_intent_id": null,
     "metrics": ["process_cpu_usage"], "note": "父意图保护，未被压缩清除"},
    {"id": "intent_2", "stage": "completed", "parent_intent_id": null,
     "metrics": ["process_cpu_usage"], "note": "原 intent_5（G5）"},
    {"id": "intent_3", "stage": "completed", "parent_intent_id": null,
     "metrics": ["process_mem_usage"], "target_entities": [{"type":"ip","name":"10.96.5.4"}]}
  ]
}
```

**G7**（压缩后回归验证）：`10.110.186.140 的CPU使用率`
- 预期：正常识别为新意图 `intent_4`，compaction 未再次触发（rounds 已降到 3+1=4），流程正常 completed。
- ✅ **断言**：
  1. 压缩保留最近 3 轮，意图从 5 → 2；
  2. **父意图 `intent_1` 被保护保留**（即使是最老意图）；
  3. 重编号后 `parent_intent_id`、`active_*`、`pending_*` 引用字段同步更新；
  4. 压缩后对话仍能正常继续（G7 回归）。

---

## 1.4 四、测试断言要点汇总

| 编号 | 场景 | 核心断言 |
|---|---|---|
| A | 单意图完整 | 无缺失直达 `completed`；active/extraction 清空 |
| B | 追问 | 新意图 `parent_intent_id` 关联正确；实体从父意图继承 |
| C | 澄清 | `paused`+`pending_clarifications`；澄清回复复用原意图，不生成新意图 |
| D | 澄清打断 | 旧意图 `suspended`；`new_intent→processing` 流转；新意图独立处理 |
| E | 多意图 | 单句拆多意图、实体不串、各自 completed |
