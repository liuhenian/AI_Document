---
title: Smart Connections 中文对照与汉化方案
created: 2026-10-23
tags: [obsidian, plugin, 汉化, smart-connections]
---

# Smart Connections 4.7.2 中文对照与汉化方案

> 结论先行：**这个插件没有做国际化**（源码里 `i18n`、`zh-cn` 各出现 0 次，`main.js` 1.53MB 全英文硬编码）。
> 但它的**真正需要看懂的功能设置只有 11 项**，其余是账号与 Pro 推销文案。所以「对照表」的性价比远高于「改代码汉化」。

---

## 一、源码事实（可复现）

在 `.obsidian/plugins/smart-connections/main.js` 中检索：

| 标记 | 出现次数 | 含义 |
|---|---|---|
| `i18n` | 0 | 没有任何国际化框架 |
| `zh-cn` / `zh_cn` | 0 | 没有中文语言包 |
| `setName(` | 12 | 设置项标题（命令式） |
| `setDesc(` | 13 | 设置项说明 |
| `setButtonText(` | 13 | 按钮文案 |
| `settings_config` 声明式条目 | 11 | 核心功能设置 |

设置项是用**声明式配置对象**（`{ name, type, description }`）定义的，不是散落在 JSX 里 —— 这也是为什么它们能被完整提取出来翻译。

---

## 二、核心设置项（11 项，你真正会看的）

| 英文原文 | 中文 | 说明 |
|---|---|---|
| Minimum length | 最小长度 | 参与向量化的片段最小字符数。太短的片段不建向量，避免噪声 |
| Model Platform | 模型平台 | Smart Model 使用的服务商 |
| Embedding model platform | 嵌入模型平台 | 默认 `transformers` = 用内置本地模型（推荐） |
| Embedding model | 嵌入模型 | 选具体模型，默认 `bge-micro-v2`（384 维） |
| Lookup retrieval strategy | 检索策略 | Lookup 的检索与排序方式，默认 Cosine Similarity（余弦相似度） |
| Lookup results type | Lookup 结果类型 | 返回整篇笔记（source）还是段落块（block） |
| Embed blocks | 生成块级向量 | 块 = 笔记里的小节/片段。开启后结果更细，但索引量变大 |
| Connection results type | 关联结果类型 | 同上，source 或 block |
| Results limit | 结果数量上限 | Connections 视图显示几条，**默认 20** |
| Show full path | 显示完整路径 | 结果里带上文件夹路径 |
| Render markdown | 渲染 Markdown | 关掉则结果以纯文本显示 |

---

## 三、账号与 Pro 区（了解即可，不用细读）

| 英文 | 中文 |
|---|---|
| Checking session... | 正在校验会话… |
| Session needs refresh | 会话需要刷新 |
| Connect account | 连接账号 |
| All-access subscription expired | 全权限订阅已过期 |
| Give $30 off Pro. Get 30 days of Pro | 邀请好友可省 $30，自己得 30 天 Pro |
| Referral link | 邀请链接 |
| Include embedding vectors | 导出时包含嵌入向量（会让导出文件大很多） |
| Browse Smart Plugins | 浏览 Smart 插件 |

**按钮**：Refresh 刷新 / Login 登录 / Logout 退出登录 / Get Pro 升级 Pro / Update subscription 更新订阅 / Start free trial 开始免费试用 / Copy link 复制链接 / Open referrals 打开邀请页 / Export 导出 / Export again 再次导出 / Retry export 重试导出 / Exporting... 正在导出…

**四个 Smart 插件条目**：

| 英文 | 中文 | 作用 |
|---|---|---|
| Smart Connections | 智能关联 | 看与你当前所写内容相关的笔记 |
| Smart Context | 智能上下文 | 用选择器/链接/模板把笔记组装成 AI 可用上下文 |
| Smart Chat | 智能对话 | 在 Obsidian 里跑对话工作流（需单独装） |
| Smart Lookup | 智能查找 | 把语义搜索做成独立视图 |

---

## 四、三条汉化路线

| 路线 | 效果 | 风险 | 维护成本 |
|---|---|---|---|
| **A. 只看对照表** | 界面仍是英文，但你看得懂 | **无** | 零 |
| **B. obsidian-i18n 插件** | 界面真的变中文，且通用于所有插件 | 第三方插件、未上官方商店；运行时注入/改写其它插件代码，出错需手动还原 | 低（插件升级后需重新映射） |
| **C. 直接改 main.js 字符串** | 界面真的变中文 | 插件一更新就被覆盖；改坏要重装；每次升级重做 | 高 |

### 路线 B 具体步骤

仓库：`https://github.com/eondrcode/obsidian-i18n`（旧地址 `0011000000110010/obsidian-i18n`、`zenozero-dev/obsidian-i18n` 会 301 到它）

1. 装 **BRAT**（社区商店有）→ `Ctrl+P` → `BRAT: Plugins: Add a beta plugin for testing` → 粘贴上面的仓库地址
2. 启用 `Obsidian i18n`
3. 设置里把**目标语言**填 `zh-cn`
4. 侧栏点 i18n 图标 → 找到 `smart-connections`
5. **云端词典模式**：点「下载」→ 再点「翻译」（最省心，但社区词典未必收录了这个插件）
6. **本地提取模式**：点「提取」→ 用内置编辑器逐条填译文 → 点「翻译」
7. 出问题：点 **还原（Restore）** 即可回滚

⚠️ **动手前先备份 `.obsidian/plugins/smart-connections/` 整个目录**（或者直接 `git` 提交一次，出问题 `git checkout` 就回来了）。

### 路线 C 为什么不推荐

插件 2026-08 才发布 4.7.2，更新节奏不慢；每次升级都会覆盖 `main.js`，你改的中文全部丢失，而且没有版本对照，下一次要重新找一遍字符串。

---

## 五、建议

1. **现在**：用本文第二节那张表（11 项），五分钟就够。你要用的功能其实只有「结果数量上限」「检索策略」「生成块级向量」这三个。
2. **如果你还想汉化别的英文插件**（QuickAdd、Dataview、Tasks 也都是英文），那路线 B 值得一次性投入 —— 它是一次性解决全局问题的工具，不是专为 Smart Connections 做的。
3. **不建议**为这一个插件去改源码。

---

## 附：Obsidian 本体语言 ≠ 插件语言

`设置 → 关于 → 语言`（Settings → About → Language）**只影响 Obsidian 核心界面**，对所有社区插件的文案无效。这是官方设计的边界，不是设置没生效。
