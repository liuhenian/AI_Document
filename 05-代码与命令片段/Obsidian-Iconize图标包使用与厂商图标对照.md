---
title: Obsidian Iconize 图标包使用与厂商图标对照
created: 2026-10-16
tags:
  - Obsidian
  - 工具配置
  - Iconize
---

# Obsidian Iconize 图标包使用与厂商图标对照

> 结论速查：图标包已装好，**看不到是因为图标选择器是搜索框**；但 **Simple Icons 只覆盖你 19 个厂商中的 4 个**。

---

## 一、当前状态（2026-10-16 实测）

图标包目录：`.obsidian/icons/`

| 文件 | 大小 | 状态 |
|---|---|---|
| `simple-icons.zip` | 3.0 MB | ✅ 已下载，含 3093 个图标 |
| `font-awesome-brands.zip` | 6.2 MB | ✅ 已下载 |
| `font-awesome-regular.zip` | 6.2 MB | ✅ 已下载 |

**关键认知：Iconize 不解压图标包。** 它在内存里直接读 zip（源码里是 `readZipFile(arrayBuffer)` → JSZip）。所以目录里只有 zip、没有文件夹，**这是正常的**。

---

## 二、为什么"添加图标时看不到"

图标选择器（`Change icon` 弹出的窗口）是一个 **FuzzySuggestModal 搜索框**，一次只展示 **150 条**结果。而你的库里现在有 **1 万多个图标**：

- Lucide（内置）
- Emoji（约 3600 条，每个 emoji 收录两次：短名 + 字符本身）
- Simple Icons 3093 条
- Font Awesome 2040 条 × 2

**所以：必须输入英文关键字，纯靠滚动永远翻不到。**

显示格式是 `名称 (前缀)`，前缀由包名自动生成：

| 图标包 | 前缀 | 选择器里长这样 |
|---|---|---|
| Simple Icons | `Si` | `Splunk (Si)` |
| Font Awesome Brands | `Fab` | `Cisco (Fab)` |
| Lucide | `Li` | `ArrowDown (Li)` |
| Emoji | `Emoji` | `fire (Emoji)` |

### 可直接搜的关键字

```
splunk      elastic     cisco       pagerduty
datadog     grafana     prometheus  juniper
vmware      nginx       redis       mysql
python      docker      github      kubernetes
cloudflare  netdata     dynatrace   newrelic
victoriametrics
```

---

## 三、⚠️ 厂商覆盖实测：19 个里只有 4 个

从已下载的 `simple-icons.zip`（3093 个）与 `font-awesome-brands.zip`（484 个品牌）逐个匹配 `00-待整理/业界分析/` 下的厂商目录：

### Simple Icons 命中

| 厂商目录 | 可搜关键字 |
|---|---|
| Splunk | `splunk` |
| Elastic | `elastic`（另有 `elasticsearch`、`elasticcloud`、`elasticstack`） |
| Catalyst（Cisco） | `cisco` |
| PageDuty | `pagerduty` |

### 未命中（17 个）

Arista · Auvik · BigPanda · Catchpoint · Conformiq · Forward · Kentik · ManageEngine · Metoro · Middleware · NetBox · NetScout · Obkio · Selector · SolarWinds · Synopsys · Traversal

> **Font Awesome Brands 一个都没命中。**

**原因**：Simple Icons 因商标合规政策持续下架中小厂商 logo，目前基本只剩大厂。

---

## 四、推荐方案：通用图标 + 颜色区分

既然"每家配自己的 logo"走不通，改用**图标表达类别、颜色表达厂商**：

| 厂商类型 | 建议图标（Tabler / Lucide） | 建设颜色 |
|---|---|---|
| 网络设备监控（Arista、Auvik、NetScout、NetBox、SolarWinds） | `network` / `router` / `server` | 蓝色系 |
| 流量与路径分析（Kentik、Catchpoint、Obkio、Traversal） | `chart-line` / `route` | 绿色系 |
| AI / 事件聚合（BigPanda、Metoro、Middleware） | `activity` / `brain` | 紫色系 |
| APM / 应用可观测（Splunk、Elastic、Datadog、ManageEngine） | `pulse` / `gauge` | 橙/红系 |
| 测试与合规（Conformiq、Synopsys） | `flask` / `shield-check` | 灰/青色系 |
| 数字孪生（Forward、Selector） | `git-branch` / `layers` | 青绿色系 |

**操作顺序**：右键文件夹 → `Change icon` → 输关键字选图标 → 再右键 → `Change color of icon` → 选色。

---

## 五、自己加厂商 logo（可选，一劳永逸）

从各厂商官网或品牌资料页下载 SVG，放进：

```
.obsidian/icons/vendor-logos/
```

**重启 Obsidian 即生效**，会作为一个自定义图标包出现，前缀是 `Vl`。

> 这条路径官方文档没写（文档只讲"设置里 Add icon pack + 手动打 zip"），是从源码确认的：Iconize 会扫描图标包目录下的**文件夹**，把每个文件夹当成一个自定义图标包。所以**不需要打 zip**。

### 注意事项

- **只支持 `.svg`**，不接受 PNG / JPG
- **文件名必须以英文字母或数字开头**（源码里 `validIconName = /^[(A-Z)|(0-9)]/`，且会先转首字母大写）。**中文文件名会被静默跳过**
- 文件名就是搜索结果里显示的名字，建议直接用品名，如 `auvik.svg`、`kentik.svg`
- 文件夹名用英文（`vendor-logos`），它的首字母组合决定前缀

---

## 六、两个容易踩的坑

### 1. emoji 图标永远不能上色

`Change color of icon` 只在**同时满足**两个条件时出现：

1. 该项**已单独设过图标**（用自定义规则批量套的图标不算）
2. **图标不是 emoji**（源码 `if (!emoji.isEmoji(icon))`）

emoji 判断依据是图标字符串本身，**与 Emoji Style 是 native 还是 twemoji 无关**。而且颜色实现是 CSS `color` 作用于内联 SVG，Twemoji 产出的是 `<img>`，同样吃不到颜色。

→ **想上色，只能用 Lucide 或图标包里的 SVG 图标。**

### 2. 移动文件会让图标失效

Iconize 以 **vault 相对路径**为 key 记录图标。文件一改名或移动，图标就**静默失效**（不报错，只是不再显示）。

`data.json` 里现存一条 `"00-待整理/APM AI助手技术选型与演进方案.md": "🔥"`，该文件已在 2026-10-14 归位时移到 `02-项目资料/AI助手/01-技术选型/ai初步分析/`，所以这条配置已失效，需重设。

> 若开启了 `iconInFrontmatterEnabled`，文件的图标会写进笔记 YAML 的 `icon` 字段，跟随文件走；**但文件夹没有 frontmatter，仍存在插件数据里，搬目录时照样会丢。**

---

## 附：相关设置项

| 设置 | 当前值 | 说明 |
|---|---|---|
| `iconPacksPath` | `.obsidian/icons` | 图标包目录（默认值，便于同步） |
| `emojiStyle` | `twemoji` | emoji 渲染方式 |
| `iconColor` | `null` | 全局默认图标色 |
| `iconInTabsEnabled` | `false` | 标签页显示图标（未开） |
| `iconInTitleEnabled` | `false` | 标题显示图标（未开） |
| `iconInFrontmatterEnabled` | `false` | 图标写入 frontmatter（未开） |
| `iconsInLinksEnabled` | `true` | 链接处显示图标 |
| `rules` | `[]` | 自定义规则（空，未配） |

---

## 七、想用中文搜图标？三条路

### 结论：现成的中文图标包没有

Iconize 内置的 10 个包（Font Awesome / Remix / Icon Brew / Simple Icons / Lucide / Tabler / BoxIcons / RPG Awesome / coolicons / Feather）**全部是英文命名**，社区也没有中文图标包。原因在机制上：

**Iconize 的搜索文本就是图标文件名。** 源码里：

```js
// 1. 文件名 → 显示名：按 空格/连字符/下划线 切分，每段首字母大写后拼接
const getNormalizedName = (s) =>
    s.split(/[ -]|[ _]/g)
     .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
     .join('');

// 2. 显示名 → 校验：首字符（大写化后）必须是 A-Z 或 0-9，否则整个图标被丢弃
const validIconName = /^[(A-Z)|(0-9)]/;
if (!validIconName.exec(normalizedName)) {
    logger.info(`Skipping icon with invalid name: ${iconName}`);
    return null;
}
```

→ **中文开头的文件名会被静默跳过**（`重点.svg` 直接消失）。**但中文字符本身不会被清除**，只要首字符是拉丁字母或数字即可。

### 路一（推荐）：英文名 + 中文名双命名

文件名写成 `<英文><中文>.svg`，例如：

```
Star重点.svg        Flag待关注.svg      Pin常用.svg
Check已完成.svg     Archive归档.svg     Book资料.svg
```

放进 `.obsidian/icons/cn-markers/`（文件夹名会成为图标包名），**重启 Obsidian 即生效**。因为：

- 首字符 `S` 是拉丁字母 → 通过校验，不会被跳过
- 显示名变成 `Star重点` → **搜 `star` 和搜 `重点` 都能命中**

**中英双语都能搜，这是最实用的做法。**

### 路二：纯拼音命名

`zhongdian.svg`、`yiwancheng.svg`。能过校验，但打拼音不如打字快，不推荐。

### 路三：干脆用 emoji

emoji 在 Iconize 选择器里也能搜（搜索文本是英文短名，如 `fire`、`star`、`pushpin`），且图形本身即语义，不用记名字。**但代价是 emoji 不能上色**（见第六节）。

---

## 八、中文意图 → 英文关键字 速查表

> 输**前 3–5 个字母**即可，不用输全（fuzzy 搜索）。带括号的是别名可能要试的写法。

| 中文意图 | 英文关键字 |
|---|---|
| 重点 / 重要 | `star` `flame` `zap` `target` |
| 待关注 / 标记 | `flag` `bookmark` `pin` |
| 进行中 | `loader` `play` `timer` `hourglass` |
| 待办 | `list-todo` `clipboard-list` `circle-dashed` |
| 已完成 | `check` `circle-check`（旧名 `check-circle`）`badge-check` |
| 草稿 / 待整理 | `pencil` `notebook-pen` `file-pen` |
| 归档 / 封存 | `archive` `box` `package` |
| 资料 / 参考 | `book` `book-open` `library` `scroll` |
| 灵感 / 想法 | `lightbulb` `sparkles` |
| 警告 / 注意 | `alert`（`triangle-alert`／旧名 `alert-triangle`） |
| 网络 | `network` `router` `server` `wifi` `cable` |
| 数据 | `database` `bar-chart` `line-chart` `activity` |
| 监控 / 告警 | `gauge` `radar` `bell` `eye` `siren` |
| AI / 智能 | `brain` `bot` `cpu` `sparkles` |
| 文档 | `file-text` `files` `file` |
| 会议 / 日程 | `calendar` `video` `users` |
| 客户 / 组织 | `building` `user` `users` |
| 代码 / 命令 | `code` `terminal` `braces` |
| 生活 | `home` `heart` `gamepad` `shopping-cart` |
| 财务 | `wallet` `coins` `banknote` `receipt` |
| 学习 | `graduation-cap` `book-marked` |
| 计划 | `calendar-check` `list-checks` `target` |
| 复盘 / 回顾 | `history` `rotate-ccw` `search` |
| 项目 / 看板 | `kanban` `layout-grid` `folder-kanban` |
| 废弃 / 停用 | `trash` `ban` `circle-x`（旧名 `x-circle`） |
| 时间 | `clock` `calendar-days` `history` |
| 位置 / 地图 | `map` `map-pin` |
| 安全 / 权限 | `shield` `lock` `key` |
| 邮件 | `mail` `send` |
| 链接 | `link` `external-link` |
| 图片 / 媒体 | `image` `film` `video` |

> Lucide 在版本迭代中改过一批名字（`alert-triangle` → `triangle-alert`、`x-circle` → `circle-x`）。Obsidian 内置的 Lucide 版本可能滞后，**搜不到就试括号里的旧名**，或者只输前缀（如 `alert`、`circle`）看完整列表。
