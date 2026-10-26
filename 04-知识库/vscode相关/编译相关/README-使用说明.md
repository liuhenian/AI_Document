# 1 clangd 一键配置器使用说明

## 1.1 一句话

在目标机器上执行（**在容器内执行，不是本地 Windows**）：

```bash
python3 clangd_setup.py \
    --src-dir <你日常编辑的源码目录> \
    --build-cmd "<编译命令>"
```

本工程的现成命令：

```bash
python3 /root/clangd-tools/clangd_setup.py \
    --src-dir /code/ctc_master_s/prj_rgos/tmp/rootfs-build/ce_apm_sw-0 \
    --build-cmd "make ce_apm_sw"
```

或者用兼容入口（参数已固化，等价）：

```bash
bash /root/clangd-tools/refresh.sh
```

---

## 1.2 两个必填参数到底填什么

| 参数 | 含义 | 怎么判断 |
|---|---|---|
| `--src-dir` | **你打开 VSCode 编辑的那个目录**（git 仓库目录） | 你的光标实际所在位置，不是编译产物目录 |
| `--build-cmd` | 你平时手敲的那条编译命令 | 不含 `bear`，脚本自己会包 |

如果两者不同目录（本项目就是：编译在 `ce_apm_sw/`，编辑在 `ce_apm_sw-0/`），
脚本会自动推断映射关系，不需要你告诉它。

---

## 1.3 脚本自动做的事

你不必预先 `make defconfig`，也不必预先跑编译。

| 阶段 | 动作 |
|---|---|
| 0 探测 | OS / 包管理器 / clangd / bear / locale / 权限 / 磁盘 |
| 1 安装 | 缺 clangd 或 bear 才装；**装前做影响模拟**，会升级或删除系统包时停下来问 |
| 2 规划 | 向上查找 `env-setup` 定位编译目录；识别 buildroot stamp 并规划强制重编 |
| 3 拦截 | 用 bear 包住编译命令，真实跑一次，抓全部编译参数 |
| 4 后处理 | 推断路径映射 / 绝对化 / 同文件去重 / 剔除 gcc 专有参数 |
| 5 配置 | 生成 `.vscode/settings.json`（合并已有）；写 git 本地忽略 |
| 6 自检 | 起 clangd 真解析，**0 诊断才算成功**；发现未知参数自动剔除重试 |

---

## 1.4 什么时候需要重跑

| 情况 | 需要重跑？ |
|---|---|
| 只改 `.c` / `.h` 里的代码内容 | **不需要**（clangd 自己重新解析） |
| 自己跑 `make` 验证编译 | **不需要** |
| 新增 / 删除 `.c` 文件 | **需要** |
| 改 Makefile / `-I` / CFLAGS | **需要** |
| 切分支、别人更新了平台仓库 | 建议重跑 |

`compile_commands.json` 记录的是「**怎么编译**」，不是「编译了什么内容」。
改代码不动编译参数，就不用重新生成。

---

## 1.5 常用选项

```bash
# 只体检，不改任何东西
--dry-run

# 工具已装好，跳过安装检查
--skip-install

# 前置步骤不是 env-setup（换个工程时用）
--pre-cmd "source ./setup.sh" --pre-cmd "cmake ."

# 前置步骤根本不需要
--no-pre-cmd

# 编译显示 "nothing to be done"，脚本没识别出清理方式
--clean-cmd "make clean"

# 仍报 unknown argument
--remove-flag "-f某选项"

# 交叉工具链头文件解析不全
--query-driver "/path/to/toolchain/bin/*"

# 全部确认自动通过（无人值守）
--yes
```

---

## 1.6 跑完之后在 VSCode 里做三件事

1. 扩展面板搜 **clangd**（LLVM 出品），安装时选 **Install in SSH: \<远程主机\>**
   —— 必须装远端，装本地无效
2. 工作区打开 `--src-dir` 指向的目录（不是父目录）
3. 命令面板 `F1` → **clangd: Restart language server**
   首次后台建索引 1–3 分钟

---

## 1.7 为什么必须这么绕

三个坑，缺一个跳转就不准：

**1. 编译目录 ≠ 编辑目录**
buildroot 把 `ce_apm_sw-0` 整个 `cp -rf` 到 `ce_apm_sw` 再编译。
bear 抓到的是副本路径。若直接喂给 clangd，跳转会落到副本上——
而副本每次编译都被覆盖，看到的是旧内容。所以必须把路径重写回去。

**2. 编译参数经过多层包装**
`make` → buildroot → `gcc-wapper` → 真实交叉编译器。
cpptools 没有编译数据库，只能靠猜 `-I` 和宏，必然猜不全。
这是之前 cpptools 跳转效果差的根因。

**3. gcc 与 clang 参数不交集**
`-flive-patching=inline-only-static` 这类参数 clang 完全不认识，
留着会让 clangd 报 `Unknown argument` 红色错误，掩盖真实问题。

---

## 1.8 已知边界

- **clangd 版本受限于内网源**（本项目为 10.0.0）。
  基础跳转 / 补全 / 诊断完整，但没有 inlay hints 等 12+ 特性。
  以后拿到离线新版包，改 `--clangd-path` 即可，其余不用动。
- **按 host 架构解析**：`-mabi=lp64 -mcpu=cortex-a53` 的目标语义被忽略。
  对语法级跳转无影响（实测 0 诊断）；若某段代码只在 `__aarch64__` 下编译，可能灰显。
- **`refresh.sh` 会重置平台仓库**：其内部 `source env-setup` 会把
  rgos-platform 恢复到指定 commit。跑之前确认工作区干净。

---

## 1.9 排查问题

出问题时日志都在 `~/.clangd-setup/`：

| 文件 | 内容 |
|---|---|
| `build.log` | 完整编译输出 |
| `capture.sh` | 实际执行的拦截脚本，可手工改完重跑 |
| `compile_commands.raw.json` | bear 原始输出（未后处理） |

编译失败时脚本会中止且**不覆盖旧的 `compile_commands.json`**，
clangd 继续用旧库工作，不会因此瘫痪。

![[附件资料/clangd_setup.py]]