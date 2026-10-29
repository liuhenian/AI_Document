# Nautobot Golden Config：功能清单与运行原理详解

> 对象：Nautobot Golden Config（`nautobot-app-golden-config`）v3.0.8 系列，2026-09-25 发布
> 归属：Network to Code（NTC，美国网络自动化公司）主导的开源 App，Apache-2.0
> 前置依赖：Nautobot ≥ 3.1.0、`nautobot-plugin-nornir`、数据库 PostgreSQL / MySQL
> 资料口径：官方文档（docs.nautobot.com/projects/golden-config）+ 仓库源码（models.py / jobs.py / nornir_plays/*.py / utilities/helper.py）+ 其依赖库 netutils、hier_config
> 整理时间：2026-10-27

## 0.0 体例说明

- 英文术语首次出现一律写作 `中文（English）`；专有名词、产品名保留原名并括注中文释义。
- 命令、代码、路径、字段名、版本号不翻译。
- 批量术语用表格并列，不塞进长段落。

| 英文 | 中文 | 一句话释义 |
|---|---|---|
| Golden Config | 金标准配置 | 行业行话，指"设备应当长什么样"的基线；本处也是产品名 |
| Source of Truth (SSoT) | 单一数据源 | 网络设备、接口、IP、机柜等元数据的权威登记簿 |
| Intended Configuration | 意图配置 | 由数据 + 模板生成出来的"应该有"的配置 |
| Actual / Backup Configuration | 实际配置／备份配置 | 从设备上抓回来的"现在是什么" |
| Configuration Compliance | 配置合规 | 两者逐特性比对，判定是否一致 |
| Configuration Drift | 配置漂移 | 实际配置偏离基线的现象 |
| Remediation | 修复 | 生成把设备拉回基线的增量命令 |
| Config Plan | 配置计划 | 可审批、可追溯的一次变更命令集 |
| Compliance Feature | 合规特性 | 用户自定义的配置关注点（如 NTP、SNMP、BGP） |
| Dynamic Group | 动态分组 | Nautobot 原生的设备集合，用过滤器动态求值 |

---

## 一、它是什么，不是什么

**是**：Nautobot 平台上的一个官方 App（应用/插件），做"配置保障"（configuration assurance）——备份、生成意图配置、比对合规、生成修复命令、按审批下发。

**不是**：
- 不是独立的配置管理平台，必须有 Nautobot 做主数据底座；
- 不是网络性能/流量监控产品；
- 不是形式化验证工具（不回答"这条命令改了会不会断网"，只回答"和基线差在哪"）；
- 不是配置数据库（备份落在 Git + Nautobot 数据库，没有独立后端）。

**能力边界一句话**：它把"配置治理"拆成一条可执行的流水线——**基线有出处（数据+模板）→ 现状有快照（备份）→ 差异有结构（特性级）→ 修复有方案（命令）→ 下发有闸门（审批）**。

---

## 二、功能清单

### 2.1 六大核心用例（官方定义）

| # | 用例 | 输入 | 输出 | 关键落点 |
|---|---|---|---|---|
| 1 | 配置备份（Configuration Backups） | 设备、平台驱动、仓库路径模板 | Git 里的配置文件 + 数据库 `backup_config` | Nornir 拉取 → 正则清洗 → 落盘 |
| 2 | 意图配置（Intended Configuration） | GraphQL 数据 + Jinja2 模板 | Git 里的 `.intended_cfg` + `intended_config` | 单入口模板渲染 |
| 3 | 数据源聚合（Source of Truth Aggregation） | 每设备一条 GraphQL 保存查询 | 一份结构化 JSON 数据 | 供模板渲染使用 |
| 4 | 配置合规（Configuration Compliance） | 备份 + 意图配置 + 合规规则 | `ConfigCompliance` 记录（缺/多/是否有序） | 三种比对引擎 |
| 5 | 配置修复（Configuration Remediation） | 实际/意图配置差异 | 增量修复命令（逐特性） | HierConfig 或自定义函数 |
| 6 | 配置下发（Configuration Deployment） | 配置计划（Config Plan） | 推到设备的变更 + 执行结果 | 合并 → 后处理 → merge_config |

另有一个 **Beta** 功能：**配置后处理（Configuration Post-processing）**——把意图配置渲染成"可直接推送"的成品（补密钥、补隐含配置），当前只渲染、不下发。

### 2.2 交付形态与运营面

| 功能面 | 说明 |
|---|---|
| 九类 Job（作业） | 见 2.3；全部通过 Nautobot Jobs 框架注册、可 API 触发 |
| 合规总览报表（Overview Report） | 设备级、特性总数、逐特性三个维度的合规率；设备要"所有特性都合规"才算合规设备 |
| 合规明细报表（Detail Report） | 可按设备属性筛选、自定义列、批量删除 |
| 设备页内联卡片（Template Content） | 在 Nautobot 设备详情页直接显示该设备/该站点的合规状态 |
| 合规详情页 | 实际 vs 意图并排差异、是否有序、修复命令字段 |
| 配置计划页 | 计划的生成、编辑（仅状态/变更单/标签）、审批、部署 |
| 单设备即时渲染 | Web UI `/plugins/golden-config/generate-intended-config/` 与 REST API，绕开 Job 直接看渲染结果 |
| 配置后处理 API | `/api/plugins/golden-config/config-postprocessing/{device_id}` |
| Git 仓库管理 | 复用 Nautobot `GitRepository`，通过 `Provides` 区分 backup / intended / jinja templates |
| 范围控制 | 通过 `Dynamic Group` 定义"哪些设备归这套设置管" |
| 多套设置 | 一个 App 实例可配多套 `GoldenConfigSetting`，按权重（weight）择优匹配 |

### 2.3 九个 Job

| Job 类 | 显示名 | 作用 |
|---|---|---|
| `BackupJob` | Backup Configurations | 备份实际配置 |
| `IntendedJob` | Generate Intended Configurations | 生成意图配置 |
| `ComplianceJob` | Perform Configuration Compliance | 执行合规比对 |
| `AllGoldenConfig` | Execute All Golden Configuration Jobs - Single Device | 单设备依次跑 意图→备份→合规 |
| `AllDevicesGoldenConfig` | Execute All Golden Configuration Jobs - Multiple Device | 多设备同上 |
| `GenerateConfigPlans` | Generate Config Plans | 由特性/手工命令批量生成配置计划 |
| `DeployConfigPlans` | Deploy Config Plans | 部署选定计划 |
| `DeployConfigPlanJobButtonReceiver` | Deploy Config Plan (Job Button Receiver) | 页面按钮触发单计划部署 |
| `SyncGoldenConfigWithDynamicGroups` | Sync GoldenConfig Table | 按动态分组成员增删 `GoldenConfig` 行 |

### 2.4 可配置的开关

`nautobot_config.py` 的 `PLUGINS_CONFIG["nautobot_golden_config"]` 控制整个组件是否启用：

| 键 | 默认 | 说明 |
|---|---|---|
| `enable_backup` / `enable_compliance` / `enable_intended` / `enable_sotagg` | True | 四大组件总开关 |
| `enable_plan` / `enable_deploy` | True | 计划与下发开关 |
| `enable_postprocessing` | False | 后处理开关（会引入密钥渲染，默认关） |
| `default_deploy_status` | `"Not Approved"` | 新建计划的初始状态；**必须先在 Nautobot 里自建同名 Status** |
| `jinja_env` | `StrictUndefined` + `trim_blocks=True` | Jinja2 沙箱环境变量 |
| `sot_agg_transposer` | None | 对 GraphQL 数据做整形的函数路径 |
| `postprocessing_callables` / `postprocessing_subscribed` | `[]` | 后处理可用函数表与执行顺序 |
| `get_custom_compliance` / `get_custom_remediation` | 无 | 自定义合规/修复函数（点号路径动态导入） |
| `custom_dispatcher` | 无 | 按平台指定自有 Nornir dispatcher |

---

## 三、机制总览：一条五段式流水线

```
                    ┌──────────────── Nautobot 数据库（SSoT）────────────────┐
                    │ Device / Platform / Location / Role / config_context  │
                    │ DynamicGroup → GoldenConfigSetting（weight 择优）      │
                    └───────────────┬──────────────────────────────────────┘
                                    │ GraphQL 保存查询（每设备一条）
                                    ▼
   Jinja2 模板仓库 ──────────► ② 意图配置（intended）───► Git: intended_repo
                                    │                      （+ DB.intended_config）
                                    │
   设备 ◄── Nornir ──► ① 备份（backup）────────────────► Git: backup_repo
                                    │                      （+ DB.backup_config）
                                    ▼
                            ③ 合规（compliance）
                     按特性切段 → 逐特性比对 → ConfigCompliance
                                    │
                                    ▼
                            ④ 修复（remediation）→ 增量命令
                                    │
                                    ▼
                     ⑤ 配置计划（Config Plan）→ 审批 → 下发（deploy）
```

**四条关键设计约束**（理解机制的前提）：

1. **一切都由 Job 驱动，非实时**。数据变了不会自动重算；包含关系变了也不会自动补记录（要跑一次任意 Job）。
2. **配置有两个副本**：Git 仓库（给人看、给审计、给版本回溯）和数据库字段（给合规引擎读）。合规比对读的是**数据库副本**，不是 Git 文件。
3. **原样纯文本，不做语义归一**。`int g0/0` 与 `interface GigabitEthernet0/0` 在它眼里就是不同。这是刻意的：厂商语法归一化的维护成本不可控。
4. **特性（feature）是比对的最小单位**，不是整份配置。全文 diff 只作为辅助视图存在，不参与合规率计算。

---

## 四、逐环节原理

### 4.1 范围解析：设备如何被纳入、如何绑定设置

三件事按顺序发生：

**第一件，算设备集合（`get_job_filter`）**

1. 把 Job 表单里的过滤条件（平台、位置、机柜、角色、租户、标签、状态……）转成 `DeviceFilterSet` 的查询参数；主键类字段取 pk 列表，名称类字段（tags/status）取名称列表。
2. 取所有 `GoldenConfigSetting` 的 `DynamicGroup.generate_query()`，用 OR 串起来作为**基础范围**。
   - 特例：若存在某套设置的过滤条件是空字典 `{}`（即"全部设备"），则跳过 OR 拼接，基础范围直接是全表。
3. `Device.objects.filter(基础范围)` → 再用表单条件过滤。
4. 三道护栏：
   - 基础范围为空 → `E3015`
   - 表单条件与基础范围无交集 → `E3016`
   - 命中设备缺 `platform` → `E3017`（平台是必填，因为要拿 `network_driver`）

**第二件，设备绑定设置（`get_device_to_settings_map`）**

- 先 `update_dynamic_groups_cache()`：把每套设置对应动态分组的成员缓存刷新一遍（除非配置了 `_manual_dynamic_group_mgmt`）。
- 然后用一条 SQL 子查询完成绑定：对每台设备，在 `GoldenConfigSetting` 中找"其动态分组包含该设备"的记录，按 `-weight` 排序取第一条（`[:1]` 是数据库 LIMIT，不是 Python 切片）。
- 结果：`{device_id: GoldenConfigSetting}`。**一台设备最多命中一套设置**；权重相同按名称次序。

**第三件，仓库就绪（`get_refreshed_repos` / `ensure_git_repository`）**

- 按 Job 类型决定要拉哪些仓库：备份 Job 拉 backup；意图 Job 拉 jinja + intended；合规 Job 拉 intended + backup；All 系列拉三类。
- 只拉"本次范围真的有设备命中"的那几套设置的仓库，避免无谓同步。
- `ensure_git_repository` 执行 git fetch/pull 到 `filesystem_path`（本地工作副本）。

> 这一步的工程含义：**范围、设置、仓库三者是解耦的**。同一实例可以做到"数据中心 A 用模板仓 A、分支试跑，数据中心 B 用模板仓 B"，只要给两套设置、两个权重。

### 4.2 备份：从设备到 Git 与数据库

`config_backup()` → Nornir 并发 fan-out → 每设备 `run_backup()`：

```
1. 取该设备的设置，取/建 GoldenConfig 行
2. 记 backup_last_attempt_date = now（先记"试过"，再干活）
3. 渲染 backup_path_template（Jinja，上下文只有 {"obj": device}）
   例：{{obj.location.name|slugify}}/{{obj.name}}.cfg
4. 可选：dispatcher(check_connectivity) 先探连通性（backup_test_connectivity，默认 True）
5. dispatcher(get_config)：
     - 连设备、拉 running-config
     - 传入 remove_lines / substitute_lines（来自 ConfigRemove / ConfigReplace，按 network_driver 分组）
     - 配置写入 backup_file
6. 记 backup_last_success_date = now，把配置文本写进 GoldenConfig.backup_config
```

**清洗机制（`ConfigRemove` / `ConfigReplace`）**

- 两者都是"平台 + 正则"的规则表，按 `platform.network_driver` 分组后在 Job 开始前汇编成两个字典：`{driver: [{regex}]}`、`{driver: [{regex, replace}]}`。
- 语义：删除匹配行 / 把匹配行替换成固定文本（如 `<redacted_config>`）。
- **官方明确立场**：不预置任何规则，因为"哪些算敏感"因组织而异；因此这是"尽力而为"的脱敏，靠用户把正则写全。Git 历史不可撤回——提交过的就是留过的。

**Git 提交机制（`gc_repos` 装饰器）**

- 三个 Job（备份/意图/合规）都套了同一个装饰器，形成事务外壳：
  - **前置**：`gc_repo_prep` → 算范围、绑设置、拉仓库
  - **执行**：真正的 Nornir play
  - **后置（finally）**：`gc_repo_push` → 对需要提交的仓库执行 `commit_with_added` + `push`；无变更则跳过（2026-06 修过一次"空提交"问题）
- commit message 未指定时默认 `"{JOB NAME} JOB {时间}"`。
- 结果：**一次 Job = 一次原子提交**，天然对应一条变更记录。

### 4.3 数据源聚合：为什么必须走 GraphQL

- 每套设置挂一条 Nautobot 保存查询（`GraphQLQuery`），**必须以 `query ($device_id: ID!)` 开头**——因为执行时只传一个变量 `device_id`。
- 执行入口 `graph_ql_query(request, obj, query)`，返回 `(status, data)`；非 200 直接 `E3012` 中断。
- 取回的数据会 `task.host.data.update(device_data)`，让它进入 Nornir 主机的数据上下文。
- 核心字段是 `config_context`：一个**厂商中立、JSON 结构化**的配置值集合（NTP 服务器列表、AAA、Syslog、VRF、SNMP 等）。设备上的 CLI 千差万别，但"我有哪几台 NTP"是同一件事——**把差异收敛到数据层，模板层才可能复用**。
- 可选 `sot_agg_transposer`：给一个函数路径，对 GraphQL 返回做整形（例如把扁平列表转成字典、补默认值）。

### 4.4 意图配置：单入口模板 + 沙箱渲染

`config_intended()` → 每设备 `run_template()`：

```
1. 渲染 intended_path_template → 输出文件位置
2. 渲染 jinja_path_template → 选定该设备用哪个模板
   例：{{obj.platform.network_driver}}/{{obj.role.name}}/main.j2
3. 执行 GraphQL，拿到 device_data
4. dispatcher(generate_config)：
     jinja_template        = 上一步的模板路径
     jinja_root_path       = jinja 仓库本地路径（include 的相对根）
     output_file_location  = 输出文件
     jinja_filters/env     = 来自 django_jinja 的过滤器 + 沙箱环境
     → 渲染结果写文件，并返回 config
5. 记 intended_last_success_date、写 GoldenConfig.intended_config
```

三个值得注意的实现细节：

- **一设备一模板**。也只能一个入口，官方明确建议用 `{% include %}` 拆成特性片段（`services.j2` / `ntp.j2` / `hostname.j2`），主模板只做编排。否则单文件 Jinja 会迅速腐化。
- **渲染环境是 `SandboxedEnvironment`**，过滤器从 Django 的 `jinja` 引擎搬过来。所以你在 `nautobot_config.py` 里用 `@django_jinja.library.filter` 注册的自定义过滤器（如 `get_netmask`），在意图配置里可直接用。
- **`undefined` 默认 `StrictUndefined`**：模板引用了不存在的数据会直接报错而不是渲染成空——这是刻意的，避免"静默生成半份配置"。错误码 `E3019`（未定义变量）/`E3020`（语法错）/`E3021`（其他模板错）。
- 另有"单设备即时渲染"通道（UI + REST），会先拉模板仓库最新 commit 再渲染，**但不做后处理**——用于调模板，不用于生产产物。

### 4.5 合规：本产品技术含量最高的一段

合规分两个阶段，**切段在 Nornir play 里做，比对在模型保存时做**。这个拆分很关键：前者需要设备上下文（平台驱动、解析器），后者只依赖数据。

#### 阶段一：按特性切段（`config_compliance.py`）

```
get_rules()  →  {network_driver: [ {ordered, section, obj} ]}
                section = rule.match_config.splitlines()   # 行首前缀列表
对每台设备：
  读 backup 文件、读 intended 文件（缺文件 → E3005/E3006）
  该平台没有规则 → E3007
  对每条规则：
      _actual   = get_config_element(rule, backup_cfg, ...)
      _intended = get_config_element(rule, intended_cfg, ...)
      ConfigCompliance.objects.update_or_create(device, rule,
          defaults={actual, intended, missing:"", extra:""})
```

`get_config_element` 按 `rule.config_type` 分三条路：

| 类型 | 切段方式 | 边界条件 |
|---|---|---|
| CLI | `netutils.config.compliance.section_config()`，用该平台的 `netutils_parser` 解析 | 解析器不存在 → `E3003` 预失败 |
| JSON | `json.loads` 后按 `match_config` 的行取**顶层键**子集 | 无法解析 → `E3002`；match 为空则整份比对 |
| XML | `lxml` 解析 → XPath 取节点 → `get_xml_subtree_with_full_path` 重建根路径 | XPath 非法 → `E3031`；match 为空则整份序列化 |

**CLI 切段的算法（这是"能理解父子关系"的真正来源）**

1. 用平台解析器把整份配置解析成**行对象序列**，每行带两个属性：`config_line`（本行文本）、`parents`（祖先行列表）。
2. 逐行扫描：
   - 若当前行 `parents` 为空（顶层行）且以某个 section 前缀开头 → 收下，置 `match=True`；
   - 若 `match=True` 且该行有 `parents`（是子行）→ 一并收下；
   - 一旦遇到新的顶层行 → 视为父块结束，`match=False`，停止收集。
3. 因此 `router bgp 65250` 与它下面所有缩进行被视为**一个整体**，而不是散落的文本行。
4. 特例：HP Comware 属于 `NON_STRIP_NETWORK_OS`，不做首尾空白裁剪，因为它的层级语义依赖空白。

**匹配是"行首前缀 + 贪婪"**：`match_config` 写 `service`，则 `service`、`service timestamps`、`no service password-recovery` 全部进入该特性。这是能力也是坑——前缀写得太宽会把无关配置吞进来，造成"假不合规"。

#### 阶段二：比对（`models.py`，`ConfigCompliance.save()` 里触发）

```
save()
 ├─ compliance_on_save()
 │    custom_compliance ? FUNC_MAPPER["custom"](self) : FUNC_MAPPER[config_type](self)
 │    → 写 compliance / compliance_int / ordered / missing / extra
 ├─ remediation_on_save()      # 依赖上一步的 compliance 结果
 ├─ full_clean()
 └─ super().save()
```

`FUNC_MAPPER` 是一张分派表：`cli → _get_cli_compliance`、`json → _get_json_compliance`、`xml → _get_xml_compliance`、`hierconfig → _get_hierconfig_remediation`；配置里提供了 `get_custom_compliance` / `get_custom_remediation` 时，用 `import_string` 动态导入并注册为 `"custom"`。

**（1）CLI 比对：`netutils.config.compliance.feature_compliance`**

```python
feature = {
    "ordered": rule.config_ordered,
    "name": rule,                                  # Platform - Feature
    "section": rule.match_config.splitlines(),
}
value = feature_compliance(feature, actual, intended, netutils_parser)
```

内部三步：

- **有序判定**：`ordered_compliant` = 实际段与意图段**字符串完全相等**（都空也算通过）。
- **算差异**（仅在不等时才做）：
  - `missing = diff_network_config(intended, actual)`——意图有、实际没有的行；输出时**先父行后子行**，所以给出来的片段是自带上下文的可读命令块。
  - `extra = diff_network_config(actual, intended)`——实际有、意图没有的行。
- **无序判定**（仅在 missing 与 extra 都为空时）：`find_unordered_cfg_lines` 比对行集合——行数相同且集合差集为空，即"内容一样、只是顺序不同"，置 `unordered_compliant=True`。

最终结论由规则的 `config_ordered` 决定：

| `config_ordered` | 通过条件 | 典型适用 |
|---|---|---|
| True | `ordered_compliant`（顺序也必须一致） | ACL、路由策略等顺序敏感的配置 |
| False | `unordered_compliant`（内容一致即可，允许乱序） | SNMP community、日志服务器列表等 |

产出五个字段：`compliance`（布尔）、`compliance_int`（0/1，给 django-pivot 画图）、`ordered`（是否顺序合规）、`missing`、`extra`。另外整机层面还会存一份 `compliance_config`：备份文件与意图文件的 **unified diff 全文**（`difflib.unified_diff`），只用于详情页展示，**不参与合规率**。

**（2）JSON 比对：DeepDiff**

```python
diff = DeepDiff(actual, intended, ignore_order=obj.ordered,
                report_repetition=True, threshold_to_diff_deeper=0)
# 有差异时
missing = _normalize_diff(diff, "added")     # 意图有、实际无 → 该补
extra   = _normalize_diff(diff, "removed")   # 实际有、意图无 → 该删
```

- `_normalize_diff` 把四类差异（`dictionary_item_added/removed`、`iterable_item_added/removed`、`values_changed`、`type_changes`）的路径键拉平成字符串列表。
- 与 CLI 不同，JSON 只有"合规/不合规"两态，不区分"仅顺序不同"这个中间态。
- 适用场景：设备原生返回结构化数据（YANG/NETCONF、或厂商 JSON 接口），此时文本 diff 无意义。

**（3）XML 比对：xmldiff**

- `diff_texts(actual, intended)` 与 `diff_texts(intended, actual)` 双向比对，`fast_match=True`、相似度阈值 `F=0.1`（偏好"文本修改"而非"节点增删"，避免整块误判为删除+新增）。
- 只保留 `actions.UpdateTextIn` 操作，格式化为 `"XPath 路径, 期望值"` 的文本。
- 合规条件：**两个方向都没有差异**。`ordered` 直接沿用对象上已有值，不重算。
- 适用场景：以 XML 为原生配置格式的设备（如部分 Nokia、Juniper 配置树导出）。

**（4）自定义比对**

- 规则勾选 `custom_compliance` 后，调用配置里的 `get_custom_compliance` 函数，返回同构的五个字段。
- 返回值会被严格校验：五个键必须齐全；`compliance`/`ordered` 必须是布尔；`compliance_int` 必须是 0/1；`missing`/`extra` 必须是字符串或可 JSON 序列化对象。
- 用途：JSON/XML 也不适用的场景（如二进制、私有二进制格式、或需要跨系统交叉验证的合规判定）。

#### 阶段三：呈现

- **总览报表**：三个维度——设备（10 个特性里有 1 个不合规，整机判不合规）、特性总数、逐特性合规/不合规计数。
- **明细报表**：设备 × 特性的二维表，可筛选、可配列、可批量删除。
- **详情页**：实际/意图并排；若完全一致则合并成单格；若"内容一致但顺序不同"则两栏都显示且带有序性图标。
- **删除重跑**：数据被"坏规则"污染时，官方建议直接删设备记录再跑——计算是幂等的 `update_or_create`，但结果不会自我修正。

### 4.6 修复：从"差在哪"到"改什么"

`remediation_on_save()` 有**明确的短路顺序**（这点常被忽略）：

```
已合规            → remediation = ""   （不需要修）
未开 config_remediation → ""           （特性级开关）
该平台无 RemediationSetting → ""        （平台级开关）
否则按 remediation_type 调 FUNC_MAPPER
```

**HierConfig 路径（`hierconfig`）**

```
1. 取 platform.network_driver_mappings["hier_config"]（如 ios / nxos），无则报"平台不支持"
2. 取 RemediationSetting.objects.get(platform=...)（JSON 选项字段 remediation_options）
3. hconfig_v2_os_v3_platform_mapper() 做版本兼容映射
4. load_hconfig_v2_options(options, os) 加载自定义选项
5. get_hconfig(os, actual) / get_hconfig(os, intended)
6. WorkflowRemediation(running, intended)
7. remediation_config_filtered_text(include_tags={}, exclude_tags={})
```

- `hier_config` 是"分层配置修复"库：把两份配置建成树（父/子节点），求差后产出**有序**的修复命令序列。顺序在这里是硬需求——先建 VRF 再绑接口，顺序错了设备直接拒绝。
- `remediation_options` 本质是 hier_config 的 `options.json` 透传：定义哪些命令是父级、哪些可否定、哪些是幂等的等等。**这是多厂商适配的真正的开关**。
- 已验证的 OS 覆盖：Cisco IOS / IOS-XR / NX-OS、Arista EOS、Ruckus FastIron；"CLI 语法近似 IOS 的都能基本开箱可用"。
- 产出是**逐特性的增量补丁**，不是全量配置。这决定了它天然适合做"最小变更"。

**自定义路径（`custom_remediation`）**

- 配置里给 `get_custom_remediation` 函数路径，输入一个 `ConfigCompliance` 对象，返回命令文本。
- 每次合规 Job 都会重算。
- 适用：非 CLI 层次结构（JSON/XML 配置），或需要借助 Nautobot 外部数据生成修复方案的场景。

### 4.7 配置计划与下发：把"自动化"关进流程里

**计划（`ConfigPlan`）是什么**：一台设备 + 一组命令 + 一个来源 + 一个状态 + 可选的变更单号/链接。命令集**生成后不可编辑**（要改就删了重生成，逼你回到源头改）——可改的只有状态、变更单号、URL、备注、标签。

四种来源（`plan_type`）：

| 类型 | 来源 | 语义 |
|---|---|---|
| `intended` | 该特性的意图配置 | 用整段覆盖 |
| `missing` | 该特性的 missing | 只补缺的 |
| `remediation` | 该特性的 remediation | 用修复引擎算出来的最小补丁 |
| `manual` | 人工输入 | 混合场景、临时操作 |

**生成**：`GenerateConfigPlans` Job（页面点 Add → Generate 触发；API 不能直接 POST 建计划，要跑这个 Job）。按设备过滤条件批量生成，每设备每特性一条。

**审批闸门**（`config_deployment()` 的前置校验，写得很直白）：

```
有计划状态 == default_deploy_status（默认 "Not Approved"） → E3025：不能部署，未审批
有计划状态 == "Completed"                                → E3026：不能部署，已执行过
```

也就是说：**审批 = 把状态从 `Not Approved` 改成别的值**。再叠加 Nautobot 原生的 Job 审批流（Approval Dashboard），就形成"人审 → 自动排队执行"的两级控制。

**下发（`run_deployment()`）**：

```
1. 取该设备的所有待部署计划，回填 deploy_result（本次 JobResult）
2. 多计划的 config_set 用 "\n" 拼成一份（同一设备合并成一次连接）
3. 若开启后处理 → get_config_postprocessing(plans, request) 生成可推送产物
4. 全部计划状态 → In Progress
5. dispatcher(merge_config) 推配置（默认 netmiko 框架，可按平台/方法四级回退选框架）
6. 结果三态回写：
     changed=False, failed=False → Completed（无实质变更）
     changed=True,  failed=False → Completed（成功）
     changed=True,  failed=True  → Failed（意味着 napalm_configure 已自动回滚）E3023
     NornirSubTaskError          → Failed  E3024
```

**框架选择逻辑（`dispatch_params`）**值得单独说：按 `方法 × 驱动 → 方法 × all → default × 驱动 → default × all` 四级回退，都找不到就 `E3022` 预失败。这条机制让"新增一个厂商"不必改 App 代码，只需在 `nornir-nautobot` 里补一个 dispatcher。

### 4.8 配置后处理：为什么需要"第二次渲染"

**问题的本质**：意图配置同时存进数据库和 Git，所以**绝不能含明文密钥**；但推送出去的那份**必须含密钥**。同时运行配置的形态 ≠ 可推送的形态：

- SNMPv3 的某些配置不出现在 running-config；
- VTP 配置完全不在 running-config 里；
- 隐含配置（接口的 `no shutdown`）不会显示；
- 顺序要求不同（先删后建的顺序可能引发中断）。

**解法**：两阶段渲染。

```
阶段一（意图配置 Job）
  模板里写： {% raw %}ppp pap sent-username {{ secrets_group["name"] | get_secret_by_secret_group_name("username") }}{% endraw %}
  产物（入库、入 Git）：ppp pap sent-username {{ secrets_group["name"] | get_secret_by_secret_group_name("username") }}
                        ↑ 用 raw 包住，保证这一阶段不提前渲染

阶段二（后处理 / 下发前）
  render_secrets 再渲染一次 → ppp pap sent-username my_username
```

- 后处理函数表：`postprocessing_callables`（可扩展的点号路径），执行顺序由 `postprocessing_subscribed` 定义。
- 默认处理器 `render_secrets` 提供 `get_secret_by_secret_group_name`，以及 `encrypt_<vendor>_type5` / `encrypt_<vendor>_type7`（设备侧密码加密）。
- 第二阶段的 Jinja 环境**不提供** Django/netutils 那批常规过滤器——只给密钥相关过滤器，避免在"产物渲染"阶段引入不可控逻辑。
- 权限：请求者必须有 Secret Group、Golden Config、目标 Device 的读权限，否则拿不到明文。

### 4.9 数据模型：十张表撑起整条链路

| 模型 | 关键字段 | 作用 |
|---|---|---|
| `GoldenConfig` | device（1:1）、backup_config、intended_config、compliance_config、三组 last_attempt/success 时间 | 每设备的配置与时间戳总账；**时间戳是首页状态灯的来源** |
| `GoldenConfigSetting` | weight、backup/intended/jinja 三个仓库 + 三个路径模板、sot_agg_query、dynamic_group（1:1） | 一套策略；按权重择优绑定设备 |
| `ComplianceFeature` | name、slug | 特性字典（如 NTP、SNMP） |
| `ComplianceRule` | feature × platform（唯一）、config_type、match_config、config_ordered、config_remediation、custom_compliance | 特性在某平台"怎么比、用不用修" |
| `ConfigCompliance` | device × rule（唯一）、compliance、compliance_int、ordered、actual、intended、missing、extra、remediation | 一次比对的完整结果；保存时自动计算 |
| `ConfigRemove` | platform、regex | 备份清洗：删行 |
| `ConfigReplace` | platform、regex、replace | 备份清洗：替换 |
| `RemediationSetting` | platform（1:1）、remediation_type、remediation_options | 平台级修复引擎与选项 |
| `ConfigPlan` | plan_type、device、config_set、feature（M2M）、plan_result、deploy_result、change_control_id/url、status | 一次待执行的变更 |

两个安全细节：`GoldenConfig` 与 `ConfigCompliance` 的 `to_objectchange()` 都会剔除配置正文字段，避免明文配置写进变更日志（changelog）。

---

## 五、能力边界：能做到什么程度

功能清单回答"有什么"，能力边界回答"到哪为止"。下面按**能承诺 / 有条件 / 做不到**三档切分，并给出证据与前提。

### 5.1 五级能力台阶（判断它在演进路线的哪一格）

| 级别 | 能力 | 判定标准 | 本产品 |
|---|---|---|---|
| L1 | 可观测 | 能看到"设备当前配置是什么、上次成功是什么时候" | ✅ 完整（备份 + 三组 attempt/success 时间戳 + 首页状态灯） |
| L2 | 可判定 | 能对"是否偏离基线"给出布尔结论与结构化差异 | ✅ 完整（特性级 + missing/extra + 有序性） |
| L3 | 可修复 | 能给出"改什么"的增量命令，且顺序安全 | ✅ 基本完整（HierConfig，覆盖主流 CLI 平台） |
| L4 | 可执行 | 能把修复关进审批流程并下发、回写结果 | ✅ 可用（缺变更预演与自动回滚编排） |
| L5 | 可解释 | 能回答"为什么漂移、影响谁、改了会怎样" | ❌ 完全没有 |

**结论**：它把 L1–L4 做成了工程可用，L5 是空白。这个空白不是实现缺陷，而是**架构定位**——它只比较两份文本，手里没有变更事件、拓扑因果、运行状态。

### 5.2 明确能做到（可直接写进方案承诺）

| 能力 | 做到什么程度 | 依据 |
|---|---|---|
| 配置快照与版本回溯 | 每次备份 = 一次 Git 提交；可回溯任意历史版本、按设备/路径检索 | `gc_repos` 装饰器 + `commit_with_added` |
| 漂移检测 | 精确到"特性 × 设备"二元组，输出缺什么、多什么 | `ConfigCompliance` 唯一约束 `(device, rule)` |
| 差异可读、可直接当命令 | missing 片段**先父行后子行**输出，自带上下文，不用人工补 `router bgp` 包头 | `diff_network_config` 借助 `line.parents` |
| 顺序敏感性区分 | 能区分"内容对但顺序错"与"内容就错"两种不合规 | `ordered_compliant` / `unordered_compliant` 双判据 |
| 多厂商 CLI 覆盖 | 官方 FAQ 列出约 17 个 `network_driver` 可直接做 CLI 合规 | 依赖 netutils `parser_map` |
| 非 CLI 形态适配 | JSON 走 DeepDiff、XML 走 xmldiff，都能做特性级判定 | `FUNC_MAPPER` 三引擎 |
| 增量修复 | 逐特性生成最小补丁，不是全量覆盖 | `WorkflowRemediation` 输出 |
| 变更治理 | 计划不可篡改 + 状态机 + 变更单号/URL + 审批闸门 + 结果回写 | `ConfigPlan` 模型与部署前置校验 |
| 密钥不入库 | 意图配置可只含占位表达式，下发前二次渲染注入明文 | `{% raw %}` + `render_secrets` |
| 多域隔离 | 多套设置 + 动态分组 + 权重，可让不同站点用不同模板与仓库 | `GoldenConfigSetting.weight` |
| 部分能力可单独启用 | 只用备份、不用合规；或用 RANCID/Oxidized 产出的仓库做合规 | 官方明确"四组件非硬绑定" |

**一句话**：**"设备配置有没有偏离基线、偏离在哪几行、怎么改回去、改的动作有没有留痕"——这四问它能闭环回答。**

### 5.3 有条件做到（前提不成立就退化成幻觉）

这一档最危险，因为它看起来"有结果"，但结果的可信度取决于前提。

| 能力 | 成立前提 | 前提不成立时 |
|---|---|---|
| 合规率数字可信 | ① 特性映射（feature map）定义正确；② 解析器覆盖该平台语法；③ 模板与数据正确；④ 清洗规则不误删非敏感行 | 出现**假阳性**：报不合规但实际合理。官方自列五类成因——设备真缺、设备真多、**数据错**、**模板错**、**解析器错**（后三类是工具侧引入的） |
| 修复命令可直接下发 | 平台在 `hier_config` 支持列表内，且 `remediation_options`（父级/否定/幂等规则）调过 | 顺序错、父级缺失，下发即中断或产生歧义配置 |
| 平台覆盖 | 平台 `network_driver` 在 nornir-nautobot / netutils 支持内（备份/意图约 10 个 driver） | 需自建 dispatcher（`custom_dispatcher`）+ 解析器；**锐捷不在默认列表**——语法近 IOS 时可用 IOS 解析器近似，但 `parents` 层级与 ordered 判定必须逐特性验证后才行 |
| 规模化 | 分批跑 + worker 扩容 + 仓库 IO 跟得上；单次 Job 建议控制在数百台量级（工程经验值，官方无硬指标） | 单 Job 时间线性拉长，Git 单次提交过大，失败重跑代价高 |
| 密钥安全 | 正则清洗**写全** + 仓库自建（内网 Git）+ 扫描/push protection | 漏一条规则，密钥就永久留在 Git 历史里（不可撤回） |
| 结构化合规（JSON/XML） | 设备真能吐结构化配置（NETCONF/YANG 或厂商 JSON/XML 接口） | 传统盒式交换机多数只能给 CLI 文本，这条路走不通 |

### 5.4 明确做不到（硬边界，别指望）

| 做不到 | 原因 | 该由谁做 |
|---|---|---|
| 语义等价判等 | `int g0/0` 与 `interface GigabitEthernet0/0` 视为不同；多余空格也算差异 | 官方明确放弃（厂商语法归一维护成本不可控）；需上层做归一或换模型驱动方案（NSO/YANG） |
| 识别隐含/默认配置 | running-config 里根本没有 `no shutdown`、VTP 某些项、SNMPv3 部分项 | 后处理阶段手工补（这是 Beta 功能存在的原因） |
| 看运行状态 | 路由表、MAC/ARP 表、CPU、光衰、会话数——**完全不在视野内** | 监控/采集系统（这恰好是 APM 类产品的领地） |
| 回答"为什么漂移" | 无变更事件源、无工单关联、无操作者归因 | 变更管理系统 + 日志审计 + 上层关联分析 |
| 变更预演（改了会怎样） | 不做可达性/环路/ACL 影响推演 | Batfish 类形式化工具 |
| 跨域关联（配置↔性能/认证失败） | 数据模型只有配置，没有性能与业务指标 | 需要自建关联层 |
| 实时性 | 一切通过 Job 触发；数据变了、分组变了都不自动重算 | 架构刻意非实时（怕"猜用户意图"） |
| 配置之外的合规 | 密码强度策略在 AAA 服务器上、账号权限在域控里 | IAM / 认证系统 |
| 交互式/多段确认变更 | 走 `merge_config` 一次性推送，无法处理需要人机交互的命令流 | 专用编排工具或人工 |
| 跨设备事务与自动回滚编排 | 回滚只到"单设备单次下发失败时由 napalm 自动 revert" | NSO 类事务化引擎 |

### 5.5 量化边界（能对外说的数）

| 维度 | 量级 | 说明 |
|---|---|---|
| CLI 合规支持平台 | 约 17 个 `network_driver` | 以官方 FAQ 列表为准；扩展需 netutils 解析器 |
| 备份/意图配置支持平台 | 约 10 个 `network_driver` | 可用 `custom_dispatcher` 扩展 |
| 合规判定粒度 | 设备 × 特性，一特性一条记录 | 特性数量由用户定义，无上限约束 |
| 判定精度 | 布尔判定本身确定；**可信度取决于规则质量** | 假阳性五源中三类由数据/模板/解析器引起 |
| 时效粒度 | 一轮 Job 的周期 | 无增量、无事件驱动、无秒级能力 |
| 规模上限 | 无硬编码上限，受 Nornir 并发 + worker + 仓库 IO 约束 | 官方建议分批；单次数百台为稳妥区间（工程经验） |

### 5.6 成熟度评级（主观判断，供选型参考）

| 能力 | 生产可用度 | 判断依据 |
|---|---|---|
| 备份 + 历史回溯 | **A（可直接上生产）** | 逻辑简单、幂等、失败影响可控 |
| 意图配置生成 | **A–**（前提是 `config_context` 数据模型已建好） | 数据模型是真正的门槛，不是代码 |
| 特性级合规 | **A–**（前提是 feature map 打磨过） | 引擎成熟；规则质量决定一切 |
| 修复生成 | **B（有条件可用）** | 平台/options 适配成本高，需逐特性验证 |
| 计划化下发 | **B（有条件可用）** | 缺变更预演，需外部补偿（人工评审 / Batfish 预检） |
| 配置后处理 | **C（Beta，勿独立承载生产）** | 官方明确只渲染不下发，且引入密钥路径 |
| 根因/影响面分析 | **D（不存在）** | 不在产品范围内，任何宣传都不应暗示 |

### 5.7 边界的一句话总结

> **它把"配置状态"做到了工程可用，把"配置原因"完全留空。**
>
> 具体说：**能答"是不是基线、差在哪、怎么改、改了有没有留痕"；不能答"为什么变成这样、会影响到谁、现在网络为什么不正常"。** 前半段是它的全部价值，后半段是任何把它当"根因分析工具"宣传的方案都会踩空的地方。

---

## 六、设计取舍与已知局限

这一节比功能列表更有价值——它标出了这套机制的能力天花板（与第五章互补：第五章讲**对外能承诺什么**，本章讲**内部为什么只能到这个程度**）。

| # | 局限 | 具体表现 | 根因 |
|---|---|---|---|
| 1 | 严格字符串比较，无语义归一 | `int g0/0` ≠ `interface GigabitEthernet0/0`；多余空格也算不合规 | 厂商语法归一化的维护成本不可控，官方明确不做 |
| 2 | 非实时 | 数据变了、分组变了都不会自动重算；要跑 Job | 刻意避免"猜用户意图"，生成与合规都是显式动作 |
| 3 | 备份只有 Git + DB 双写 | 无对象存储、无数据库旁路后端 | 架构定型，官方称不在范围 |
| 4 | 一设备一模板（单入口） | 逻辑全塞主模板会迅速腐化 | 靠 `{% include %}` 分层缓解，不提供多模板组合 |
| 5 | 特性映射（feature map）必须自维护 | 不预置"BGP 包含哪些配置" | "什么算一个特性"永远达不成共识 |
| 6 | 前缀匹配贪婪 | `service` 会吞掉 `no service ...` 等所有同前缀行 | CLI 切段按行首前缀，非语法树精确定位 |
| 7 | 规模化靠横向扩 | 全量重跑、Nornir 线性 fan-out、无增量 diff 计算 | Job 模型；大网需分批 + 加 worker |
| 8 | 只报差异，不查原因 | 输出"缺什么/多什么"，不解释"为什么漂移" | 它只比较两份文本，没有变更上下文与拓扑因果 |
| 9 | 敏感信息脱敏"尽力而为" | 正则漏一条，密钥就进 Git 历史 | 清洗规则由用户维护 |
| 10 | `name` 键冲突 | GraphQL 数据用 `**data` 解包，撞 Nornir 的 host `name` | 需用别名 `hostname: name` 规避 |

**最值得记住的一条**：它解决的是**"配置与基线是否一致"**，不是**"网络为什么不正常"**。这两件事之间隔着一整层因果推理——配置漂移只是可疑原因之一，还可能是硬件、链路、上游路由、认证服务器。这也是这类工具天然的分析断点。

---

## 七、与相邻方案的机制差异（用于定位，不用于评优劣）

| 方案 | 比对方式 | 修复/下发 | 数据底座 | 特点 |
|---|---|---|---|---|
| Golden Config | 特性级段落比对（文本/JSON/XML 三引擎） | HierConfig 增量补丁 + 计划审批 | Nautobot SSoT + Git | 开源，闭环最完整，强依赖主数据质量 |
| Ansible + Git 自建 | 全文 diff 或自定义脚本 | Playbook 推送 | 无强制底座 | 灵活但资产全靠自建，无统一报表 |
| SolarWinds NCM / ManageEngine NCM | 基线/策略式合规（预置 PCI/SOX 等模板） | 配置模板回滚 | 自有设备库 | 开箱即用，偏"配置备份 + 合规巡检" |
| Cisco NSO | 模型驱动（YANG）事务化比对 | 事务化下发，失败自动回滚 | NSO CDB | 语义最强，闭源重、强绑定 Cisco 生态 |
| Batfish | 解析为形式化模型做静态分析 | 不负责下发 | 快照 | 能回答"改了会怎样"（可达性/环路/ACL 影响），不回答"现在是不是基线" |

组合使用的现实形态：**NSO/Batfish 管"变更前推演"，Golden Config 管"变更后守夜"**。

---

## 八、对自研场景的三点可复用结论

（面向"配置类问题如何自动化分析"的设计参考，非产品评价）

1. **"标准态"必须由数据 + 模板生成，不能人工写死。** 人工维护的基线必然腐化；只有从权威数据渲染出来的意图配置，才能随拓扑自动变化。这是整条链路成立的前提，也是最贵的一步（要先把 `config_context` 这类厂商中立数据模型建起来）。

2. **比对粒度决定可用性。** 全文 diff 的噪声让人放弃；切到"特性级"（几十条规则）后，输出才变成可执行工单。**切段的边界定义（match_config）是这套系统真正的知识资产**，比代码值钱。

3. **"发现问题"与"执行变更"必须在架构上分离。** 用配置计划（命令集不可改 + 状态机 + 变更单号 + 审批闸门）承载动作，是让人敢开自动化的关键。反过来说，如果一段自动化"发现即执行"，它在生产网里永远只能停在演示阶段。
