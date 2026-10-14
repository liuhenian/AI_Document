在 `initramfs` 阶段启动 eBPF，其“模块依赖”情况比较特殊。**核心答案是：eBPF 基础设施本身通常被编译进内核核心，不依赖外部内核模块（`.ko`文件），但你的**具体 eBPF 程序**可能会依赖内核的特定功能（`kconfig` 选项）和用户态工具（`bpftool`、`libbpf` 等）。

### 0.1.1 eBPF 依赖的是内核特性，而非内核模块

首先要明确一个关键区别：eBPF 并非像普通驱动那样作为一个独立的内核模块（`.ko`）存在。它是内核核心的一部分，其基础功能（如解释器、JIT编译器、验证器）通常通过以下内核配置选项（`kconfig`）静态编译进内核镜像（`vmlinuz`）：

*   `CONFIG_BPF`：eBPF 的总开关。
*   `CONFIG_BPF_JIT`：启用 JIT（即时编译），将 eBPF 字节码转为本地机器码以提升性能。
*   `CONFIG_BPF_SYSCALL`：启用 `bpf()` 系统调用，这是用户空间程序加载 eBPF 程序的入口。

因此，在 `initramfs` 阶段，只要你的内核在编译时包含了这些选项，**eBPF 的基础运行环境就已经就绪，不需要加载任何额外的内核模块**。

### 0.1.2 可能涉及的“模块”式依赖

虽然 eBPF 核心不依赖模块，但在特定场景下，你可能会遇到与“模块”相关的依赖：

1.  **BPF 类型的 BTF (BPF Type Format) 信息**：为了支持 `CO-RE` (Compile Once - Run Everywhere)，eBPF 程序需要内核的 BTF 信息。对于内核本身，BTF 信息位于 `/sys/kernel/btf/vmlinux`。对于**内核模块**中定义的函数或数据类型，其 BTF 信息位于 `/sys/kernel/btf/<模块名>`。
    *   **潜在问题**：如果你的 eBPF 程序需要 `kprobe` 或 `tracepoint` 到某个**内核模块**（而非核心内核）内部的函数，那么该模块必须被加载，并且其 BTF 信息必须可用。这依赖于内核配置 `CONFIG_DEBUG_INFO_BTF_MODULES`。
    *   **解决方案**：确保目标内核模块在 eBPF 程序加载前已被加载。

2.  **`bpfilter` 框架**：这是一个实验性的、基于 eBPF 的包过滤框架，用于替代 `iptables` 的部分功能。`bpfilter` 本身可能被编译为一个独立的内核模块（`bpfilter.ko`），其编译依赖于 `BPF` 和 `INET` 等选项。
    *   **注意**：这并非通用 eBPF 程序开发的依赖，仅在需要使用该特定框架时才会涉及。

### 0.1.3 在 initramfs 中的真正挑战：用户态工具与库

在 `initramfs` 阶段运行 eBPF 程序，最大的挑战通常不是内核模块，而是**用户态空间**的依赖。你需要将以下内容打包进 `initramfs`：

*   **eBPF 程序字节码**：你编译好的 `.o` 文件。
*   **加载器**：用于将 eBPF 程序加载到内核的程序，例如：
    *   `bpftool` 工具。
    *   你自己编写的、使用 `libbpf` 库的 C 程序。
    *   使用 `cilium/ebpf` 等 Go 库编译的加载器。
*   **依赖库**：上述加载器所依赖的动态链接库，如 `libbpf.so`、`libelf.so` 等。
*   **加载脚本**：在 `initramfs` 的 `init` 脚本中，在合适的时机（如 `pre-mount` 阶段）调用你的加载器。

### 0.1.4 操作建议

1.  **确保内核配置**：检查你的内核是否启用了必要的 `CONFIG_BPF_*` 选项。如果使用 `CO-RE`，还需确保 `CONFIG_DEBUG_INFO_BTF=y`。
2.  **识别程序依赖**：明确你的 eBPF 程序 attach 到了哪个 Hook 点（如 `kprobe`、`tracepoint`）。如果目标在内核模块中，需确保该模块在 `initramfs` 阶段被提前加载。
3.  **构建自定义 initramfs**：使用 `dracut`、`initramfs-tools` 或 `mkinitcpio` 等工具，将你的 eBPF 程序、加载器及其所有依赖库一同打包进 `initramfs`。
4.  **调试与验证**：如果遇到加载失败，首先检查 `dmesg` 输出，这通常能提供最直接的错误原因，例如是 BTF 缺失、权限不足（`CAP_BPF`）还是库文件找不到。

总而言之，在 `initramfs` 中启用 eBPF，你通常不需要操心内核模块的依赖，但需要仔细准备用户态的工具链和库文件。