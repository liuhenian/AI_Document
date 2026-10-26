---
title: Smart Connections 模型加载失败（Failed to fetch）排查与修复
category: Obsidian / 插件排障
plugin: smart-connections 4.7.2
created: 2026-10-23
tags: [obsidian, smart-connections, embedding, 排障, 国内网络]
---

# Smart Connections 模型加载失败：Failed to fetch

## 一、症状

启动时报错：

```
ERROR  Failed to load embedding model TaylorAI/bge-micro-v2.
       Failed to fetch
```

界面上的「关联」「查找」全部不可用，索引停在 0。

## 二、根因：模型权重从 huggingface.co 下载，国内直连不通

这个插件本身**不内置模型**，首次使用时才去下载。链路有三段，任何一段断都会报错：

| 环节 | 地址 | 本机实测 |
|---|---|---|
| ① 运行时 JS（transformers.js 4.2.0） | `cdn.jsdelivr.net/npm/@huggingface/transformers@4.2.0` | **通**（HTTP 200） |
| ② 模型权重（config / tokenizer / onnx） | `huggingface.co/TaylorAI/bge-micro-v2/resolve/main/…` | **不通**（连接被重置） |
| ③ hf-mirror 国内镜像 | `hf-mirror.com/TaylorAI/bge-micro-v2/resolve/main/…` | **通**（HTTP 200，文件齐全） |

所以 `Failed to fetch` 的准确含义是：**第 ② 段网络失败**，不是插件损坏，也不是模型不存在。

### 模型要下哪些文件、多大

| 文件 | 大小 | 何时用到 |
|---|---|---|
| `config.json` | 745 B | 必有 |
| `tokenizer.json` / `tokenizer_config.json` | 711 KB / 1.6 KB | 必有 |
| `onnx/model_quantized.onnx` | **约 17 MB** | CPU（WASM）路径 |
| `onnx/model.onnx` | **约 66 MB** | GPU（WebGPU）路径 |

`dtype: "auto"` 会按设备自动选：WASM → `q8`（用的是 `_quantized` 这一份）；WebGPU → `fp32`。

## 三、插件的实现细节（决定了怎么修）

模型加载跑在一个 **Web Worker** 里，源码是**以字符串形式内嵌在 `main.js`** 中的（变量名 `transformers_v4_worker_default`，运行时转成 Blob 再 `new Worker`）。关键几行：

```js
this.transformers_module = await import('https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.2.0');
const { env } = this.transformers_module;
env.allowLocalModels = false;      // 不用本地目录
env.useBrowserCache = true;        // 下载后缓存在 Electron 的 Cache Storage
// → 之后每次请求都拼成  remoteHost + '{model}/resolve/{revision}/' + 文件名
this.pipeline = await pipeline('feature-extraction', this.model_key, { device, dtype });
```

- 下载地址 = `env.remoteHost` + `env.remotePathTemplate` + 文件名，默认 `remoteHost = 'https://huggingface.co/'`
- **插件设置里没有「自定义下载源」这种选项**，唯一的嵌入适配器只有 `transformers`（本地）和 `ollama` 两个
- 模型下载成功后进 Chromium 缓存，**之后可离线**；清 Obsidian 缓存会重新下载

结论：要改源，只能改 `env.remoteHost`，也就是要动内嵌的那个 worker 字符串。

## 四、已实施的修复（两处补丁，改 `main.js`）

补丁位置：`.obsidian/plugins/smart-connections/main.js`

### 补丁 1：把下载源指向国内镜像

在 `env.allowLocalModels = false;` 之后插入一行：

```js
env.remoteHost = 'https://hf-mirror.com/';
```

镜像的路径结构与官方完全一致（`{model}/resolve/{revision}/{file}`），所以只改 host 就够，`remotePathTemplate` 不用动。

### 补丁 2：镜像失败时自动回退官方源

原代码是单次调用，失败即抛错。改为：

```js
try {
  this.pipeline = await pipeline('feature-extraction', this.model_key, pipeline_options);
} catch (load_error) {
  const tf_env = this.transformers_module && this.transformers_module.env;
  const cur_host = String((tf_env && tf_env.remoteHost) || '');
  const alt_host = cur_host.indexOf('hf-mirror') !== -1
    ? 'https://huggingface.co/'
    : 'https://hf-mirror.com/';
  console.warn('[Transformers worker] model load failed via ' + cur_host + ', retry via ' + alt_host, load_error);
  if (tf_env) tf_env.remoteHost = alt_host;
  this.pipeline = await pipeline('feature-extraction', this.model_key, pipeline_options);
}
```

这样镜像挂了会自动试官方源，反之亦然。

### 校验

```bash
node --check .obsidian/plugins/smart-connections/main.js   # 无输出 = 语法通过
```

原始文件已备份在 `.git/_sc-main.js.orig-4.7.2`（不随仓库同步、Obsidian 也看不到）。

## 五、生效步骤

1. `Ctrl+P` → **重新加载应用**（Reload app without saving）
   - ⚠️ 别用正常退出再打开：插件列表与配置在内存里有一份副本，正常退出会写回磁盘覆盖手工改动
2. 首次会下载模型：CPU 路径约 17 MB，GPU 路径约 66 MB，看网速几十秒到几分钟
3. 索引 295 篇笔记，按这个规模是很小的量级

如果下载卡住或再次报错，**在插件设置里把模型的 GPU 开关关掉**（`use_gpu: false`），强制走 WASM + 17 MB 的量化模型，成功率更高、速度也够用。

## 六、插件升级后补丁会被覆盖，怎么重打

`main.js` 是插件的构建产物，升级会整文件替换。重打脚本（Python，幂等，已打过会跳过）：

```python
import os, shutil, sys

MAIN = r"D:/WORKSPACE/Obsidian-Workspace/.obsidian/plugins/smart-connections/main.js"
s = open(MAIN, encoding="utf-8", newline="").read()
if "hf-mirror" in s:
    print("已打过补丁"); sys.exit(0)

old1 = r"env.allowLocalModels = false;\n      if (typeof env.useBrowserCache !== 'undefined') {"
new1 = (r"env.allowLocalModels = false;\n"
        r"      // [patch] use CN mirror\n"
        r"      env.remoteHost = 'https://hf-mirror.com/';\n"
        r"      if (typeof env.useBrowserCache !== 'undefined') {")
assert s.count(old1) == 1, "补丁1 锚点未命中，插件结构可能已变，需人工核对"
s = s.replace(old1, new1, 1)

old2 = (r"this.pipeline = await pipeline(\n"
        r"      'feature-extraction',\n"
        r"      this.model_key,\n"
        r"      pipeline_options,\n"
        r"    );")
new2 = (r"try {\n"
        r"      this.pipeline = await pipeline('feature-extraction', this.model_key, pipeline_options);\n"
        r"    } catch (load_error) {\n"
        r"      const tf_env = this.transformers_module && this.transformers_module.env;\n"
        r"      const cur_host = String((tf_env && tf_env.remoteHost) || '');\n"
        r"      const alt_host = cur_host.indexOf('hf-mirror') !== -1\n"
        r"        ? 'https://huggingface.co/'\n"
        r"        : 'https://hf-mirror.com/';\n"
        r"      if (tf_env) tf_env.remoteHost = alt_host;\n"
        r"      this.pipeline = await pipeline('feature-extraction', this.model_key, pipeline_options);\n"
        r"    }")
assert s.count(old2) == 1, "补丁2 锚点未命中，插件结构可能已变，需人工核对"
s = s.replace(old2, new2, 1)

shutil.copy2(MAIN, MAIN + ".bak")
open(MAIN, "w", encoding="utf-8", newline="").write(s)
print("补丁完成")
```

> ⚠️ 注意 `open()` 必须带 `newline=""`：这个文件是纯 LF 换行，用默认模式读写会整体改写行尾，产生 1.5 MB 的伪变更。

## 七、备选方案（补丁失效时）

| 方案 | 代价 | 适用 |
|---|---|---|
| **换更小的模型** `TaylorAI/bge-micro-v2` | 中文弱，但下载 17 MB、推理最快 | 只要能跑起来、不挑中文质量 |
| **换模型** `Xenova/multilingual-e5-small` | 量化版 113 MB，需重建全部向量 | 中文语义质量要求高 |
| **全局代理** | 让 Electron 走系统代理即可直连官方源 | 本机已有稳定代理 |

> ⚠️ **更正一个常见误解：Smart Connections 4.7.2 的嵌入模型只能走 `transformers`（本地 ONNX），不支持 Ollama，也没有远程 embedding API。**
> `main.js` 里 `adapter: "ollama"` 只出现在 `smart_chat_threads.chat_model` —— 那是**聊天**模型，不是嵌入模型。嵌入适配器只有 `TransformersWorkerEmbeddingModelAdapter` 一个。所以「装了 Ollama 就能加速建索引」这条路在本版本不成立。

## 八、实际更换：bge-micro-v2 → multilingual-e5-small（2026-10-23）

### 为什么换

`bge-micro-v2` 是**纯英文**训练的 384 维小模型，中文能力弱。库里是几千字技术长文、术语密度高，它给出的多是「大致相关」。`Xenova/multilingual-e5-small` 同为 384 维，但多语言（含中文）训练，是插件内置模型列表里**中文性价比最高**的一个。

### 体积对比（镜像实测）

| 文件 | bge-micro-v2 | multilingual-e5-small |
|---|---|---|
| `onnx/model_quantized.onnx`（`q8`，WASM 用） | 17.4 MB | **112.8 MB** |
| `onnx/model.onnx`（`fp32`，WebGPU 用） | 69 MB | **448.5 MB** |
| `onnx/model_fp16.onnx` | 无 | 224.4 MB |
| `tokenizer.json` | 711 KB | 16.3 MB |

### 关键：改模型要改**两个地方**

这一步踩过坑：只改设置文件不生效。

| 位置 | 内容 | 作用 |
|---|---|---|
| `.smart-env/smart_env.json` → `smart_sources.embed_model.transformers.model_key` | 设置层 | 插件设置界面的值 |
| `.smart-env/embedding_models/embedding_models.ajson` | **实际生效的模型条目** | `env.embedding_models.default` 读的就是它，它的 `data.model_key` 优先级更高 |

`embed_model_key` 的取值逻辑是 `embed_model_data.model_key || embed_model_item.model_key` —— **ajson 里的 `data` 优先**，所以只改 `smart_env.json` 会被旧条目盖住。

ajson 是 append-only 的，改法：

```json
"embedding_models:transformers#<原时间戳>": {"provider_key":"transformers","model_key":"Xenova/multilingual-e5-small","dims":384,"max_tokens":512,"class_name":"EmbeddingModel","created_at":<原值>,"key":"transformers#<原值>","use_gpu":false},
```

**保留原 key 与时间戳**，只改 `model_key`，再加 `use_gpu:false`。

### 关键：强制走 WASM，否则会下 448 MB

`dtype: "auto"` 是按设备解析的：`DEFAULT_DEVICE_DTYPE_MAPPING[wasm] = q8`，webgpu 则是 fp32。也就是说 **WebGPU 可用时会去下 448 MB 的 fp32**，从镜像拉这么重的文件失败概率不低。

所以额外打一处补丁（worker 内）：

```js
this.use_gpu = params.use_gpu !== false;
// [patch] force WASM(q8) backend: avoids the 448MB fp32 download on the WebGPU path
this.use_gpu = false;
```

⚠️ 注意 `use_gpu` 不能只靠配置：适配器里写的是 `use_gpu: this.use_gpu !== false`，而 getter 在拿不到布尔值时返回 `undefined`，`undefined !== false` 恒为 `true` —— 所以「配置里不写」并不会关掉 GPU，必须显式 `false` 或改代码。

代价：不用 GPU 加速。295 篇笔记的量级，WASM 跑 384 维小模型完全够（首次索引约 1–2 分钟），换来的是下载量 448 MB → 129 MB。

### 回滚到 bge-micro-v2

1. `embedding_models.ajson`：`model_key` 改回 `TaylorAI/bge-micro-v2`，删掉 `"use_gpu":false`
2. `smart_env.json`：`model_key` 同样改回，删掉 `"use_gpu": false`
3. `main.js`：删掉 `this.use_gpu = false;` 这一行（保留 `params.use_gpu !== false` 原逻辑）
4. 删掉 `.smart-env/smart_sources/smart_sources.ajson` 里已生成的向量（或直接删除整个 `.smart-env/` 让插件重建）

> 换模型 = 换向量空间，旧向量必须作废。本次更换前库里 **0 条向量**（原模型从未加载成功），所以没有损失，也无需重建。

## 九、换完之后：怎么判断索引在跑还是在卡

### 先看模型有没有下载完

模型不走 vault 目录，而是进 Chromium 的 **Cache API**，位置：

```
C:\Users\admin\AppData\Roaming\obsidian\Service Worker\CacheStorage
```

里面按大小就能认出来（文件名是哈希，看不出模型名）：

| 大小 | 对应文件 |
|---|---|
| **112.83 MB** | `onnx/model_quantized.onnx`（e5 量化版） |
| **16.29 MB** | `tokenizer.json` |
| 0.7 KB | `config.json` |

> 注意：不要看 `%APPDATA%\obsidian\Cache\Cache_Data`，那是普通 HTTP 缓存，大模型不进那儿（那里最大只有 16 MB）。

### 再看索引在不在跑

四个独立信号，任一在动就说明没死：

| 信号 | 怎么看 | 正常表现 |
|---|---|---|
| 进程 CPU | 任务管理器里 Obsidian 渲染进程 | **稳定占满一个核**（≈10s/10s），说明在推理 |
| 事件日志 | `.smart-env/event_logs/event_logs.ajson` | `embedding:progress` 的 `ct` 持续增加 |
| 内存 | 渲染进程工作集 | 建块阶段爬到 1.4 GB 左右后**回落/稳定** |
| 报错 | 事件日志里的 `embed_model:load_failed` / `embedding:error` | **时间戳不再更新** |

### 一个必须知道的坑：中途没有断点

**嵌入结果先全部存在内存里，跑完才落盘。** 判断依据：

- `.smart-env/smart_sources/smart_sources.ajson` 长时间不变（15 MB，停在改模型之前）
- `.smart-env/smart_blocks/` 目录**直到最后才创建**
- 事件里只有 `embedding:started` 和 `embedding:progress`，没有 `embedding:completed`

所以**索引过程中别重启 Obsidian**，重启等于全部重来。

### 为什么这么慢

三件事叠在一起：

1. **单线程**：ONNX Runtime Web 的多线程要 SharedArrayBuffer，Obsidian 没给 COOP/COEP 响应头 → 只能用 1 个核。
2. **逐条推理**：`batch_size: 1`（模型档案里写死的），每块单独一次前向。
3. **工作量**：286 篇笔记切成 **32,372 个块**，其中 6,873 块需要嵌入，合计 **612 万字符**（≈ 350 万 token）。

量级换算：单线程 WASM 大约 100–300 token/s → **几小时**；若开 WebGPU(fp32) 可到数千 token/s → **十几到几十分钟**，代价是多下 448 MB。

### 三种取舍

| 方案 | 改动 | 首次耗时 | 质量 |
|---|---|---|---|
| 等它跑完 | 不动 | 数小时 | 块级，最细 |
| **关块级嵌入**（`embed_blocks: false`） | `.smart-env/smart_env.json` 里 `smart_blocks.embed_blocks` 设 false | 十分钟级 | 整篇粒度，长报告定位变粗 |
| **开 GPU** | 删掉 `this.use_gpu = false;` 这一行，重下 448 MB fp32 | 十几到几十分钟 | 块级，最细 |

## 十、Lookup 已从主插件拆出去（2026-10-23 实测）

### 症状

装好 4.7.2 之后，命令面板搜不到 Lookup，也没有 Lookup 视图，只剩一个 Connections。

### 根因

不是没启用，是**代码里已经没有 Lookup 了**。`main.js` 里 `smart-lookup` 这个 view_type 的完整注册代码不存在，只有一段迁移提示：

```js
// connections_settings_lookup_callout 组件
// "Lookup is moving to a dedicated plugin. Please install to continue using
//  lookup features and access lookup settings."
// 按钮 "Install" → install_smart_lookup(plugin)
```

而 `install_smart_lookup()` 走的是 `api.github.com` 拿 release，再从 `github.com/.../releases/download/...` 下三件套。**在国内网络这一步很容易失败**，失败了只有一个 `plugin:install_failed` 事件，UI 上就是按钮点了没反应。

### 正确做法：手动装 `smart-lookup`

仓库 `brianpetro/smart-lookup-obsidian`，本次装的是 **0.3.4**（2026-08-06 发布）。

需要下三个文件到 `.obsidian/plugins/smart-lookup/`：

| 文件 | 大小 |
|---|---|
| `main.js` | 1,340,932 B |
| `manifest.json` | 410 B |
| `styles.css` | 101,493 B |

再把它加进 `.obsidian/community-plugins.json`，**重启 Obsidian**才生效。

### 装完必须再打两个补丁

`smart-lookup` 的 worker 是**独立的一份**（`transformers_v4_worker_default`），不共享 `smart-connections` 里那份补丁。实测它全文 **0 处** `huggingface.co`、**0 处** `remoteHost` —— 也就是说它用的是 transformers.js 的默认源，在国内必失败。

和第四节同样的两处，只是锚点略有不同（同样是 **字符串形式的 worker 源码**，`\n` 是转义的）：

```js
// 补丁 1：锚点 env.allowLocalModels = false;\n 之后插入
env.remoteHost = 'https://hf-mirror.com/';\n

// 补丁 2：锚点 this.use_gpu = params.use_gpu !== false;\n 之后插入
this.use_gpu = false;\n
```

打完后校验：**只多 77 个字符**，LF 数不变（34,674），无 CRLF；把两处插入删掉后 SHA256 与原文件完全一致（`1cabdeb0…`）。原始备份在 `.git/_sl-main.js.orig-0.3.4`。

### 为什么不用重新下模型

模型文件存在 Chromium 的 `Service Worker/CacheStorage` 里，**按 URL 作键**。`smart-lookup` 打了同样的 hf-mirror 补丁后请求的 URL 与 `smart-connections` 完全一致（`Xenova/multilingual-e5-small` + `model_quantized.onnx`），直接命中缓存，**不会再下 112 MB**。

同时它读的是**同一个** `.smart-env/`（`env_data_dir` 找根目录下的 `smart_env.json`），所以现有 **6,755 条向量立即可用**，不需要重建索引。

### 升级会覆盖补丁

`main.js` 被覆盖后，两处补丁同时丢失，表现回到 `Failed to fetch`。重打方法同上；升级前先看一眼 `manifest.json` 里 `version` 有没有变。


