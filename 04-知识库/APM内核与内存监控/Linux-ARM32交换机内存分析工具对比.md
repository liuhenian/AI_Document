# 1 Linux ARM32 交换机内存分析工具对比

更新时间：2026-08-05

## 1.1 需求定义

目标环境：

- Linux 平台。
- ARM32 交换机设备，运行环境通常受限：CPU 弱、内存小、Flash/磁盘空间有限，可能没有完整发行版包管理器。
- 目标对象是用户态进程的内存分析。
- 需要知道“哪个调用栈分配了多少内存”。
- 统计结果需要自动减去已经 `free` 的内存，也就是更关注当前仍存活的堆内存，而不是只看累计分配量。
- 需要调用栈信息。
- 需要内存地址信息。
- “内存相关的要完整”，即最好能覆盖 `malloc/free/calloc/realloc/new/delete/aligned_alloc/posix_memalign/mmap/munmap` 等常见路径，至少不能只看单一指标。

本文评分以“在 ARM32 交换机设备上真实落地排查用户态堆内存问题”为核心，而不是以 PC 服务器上的体验为核心。

评分口径：

- 10 分：高度满足需求，可在 ARM32 Linux 上较完整地得到存活内存、调用栈、地址、释放关系，且可落地。
- 7-9 分：满足核心需求，但某些字段、平台或部署成本有明显限制。
- 4-6 分：能解决一部分问题，但不完整，适合作为辅助工具。
- 1-3 分：与需求偏离较大，或在 ARM32 交换机上落地困难。

## 1.2 关键判断维度

### 1.2.1 是否能自动减去 free

这是本需求最核心的点。工具必须能把“分配事件”和“释放事件”配对，最终按当前仍未释放的 block 统计。

满足方式通常有三类：

- 拦截分配器：如 `LD_PRELOAD`、替换 malloc、链接 tcmalloc。
- 动态二进制插桩：如 Valgrind。
- libc 自带 trace：如 `mtrace`。

`perf` 这类采样工具默认不理解 malloc/free 配对，不适合作为主工具统计“当前活跃堆内存”。

### 1.2.2 是否有调用栈

调用栈质量取决于：

- 程序是否带符号：至少需要未 strip 的符号表，最好有 `-g`。
- ARM32 编译时是否保留 frame pointer：建议加 `-fno-omit-frame-pointer`。
- 是否有可靠 unwinder：例如 libunwind、glibc backtrace、Valgrind 自己的 unwind 机制。
- 优化等级：`-O2` 下内联、尾调用、省略帧指针会让栈不完整。

建议测试版本使用：

```bash
CFLAGS="-g -O1 -fno-omit-frame-pointer"
CXXFLAGS="-g -O1 -fno-omit-frame-pointer"
LDFLAGS="-rdynamic"
```

### 1.2.3 是否有地址信息

地址信息分两类：

- 分配 block 地址：例如 `malloc` 返回的指针地址。
- 调用栈地址：PC/IP 地址，可配合符号表离线解析。

很多工具默认 UI 更强调“调用栈聚合后的大小”，不一定把每个 block 的地址作为一等输出字段。你的需求明确要求地址，因此要特别看工具是否能保留或导出 allocation address。

### 1.2.4 ARM32 交换机落地难点

交换机设备上常见限制：

- libc 可能是 glibc、uClibc-ng 或 musl。部分工具强依赖 glibc。
- 文件系统可能只读或空间很小，trace 文件容易撑爆。
- 设备 CPU 慢，Valgrind 这类工具可能慢 10-100 倍。
- 目标程序可能长时间运行，完整 trace 会非常大。
- 目标程序可能多进程、多线程、daemon 化，工具需要支持 attach 或启动时注入。
- 目标程序可能静态链接，`LD_PRELOAD` 类工具失效。
- 符号表可能不在设备上，需要把 trace 拿回 PC 离线解析。
- 内核版本、perf_event、debugfs、ftrace、BPF 等功能可能被裁剪。

## 1.3 工具逐项分析

## 1.4 Bytehound

### 1.4.1 功能支持

Bytehound 是一个面向 Linux 用户态程序的 heap profiler，典型使用方式是通过 `LD_PRELOAD` 注入 malloc/free 拦截库，记录分配和释放事件，并通过本机或远端 UI/分析端查看结果。

对需求的满足情况：

- 当前存活堆内存：支持。它会跟踪 allocation/free，所以可以统计 still allocated 的内存。
- 按调用栈聚合：支持。它的主要价值就是把分配按 backtrace 聚合。
- 自动减去 free：支持。
- 内存地址：部分支持。底层必须知道 allocation pointer 才能和 free 配对，但常规分析界面更强调聚合统计，不一定适合直接列出所有 block 地址。若必须导出每个活跃 block 的地址，需要确认版本和导出格式，可能需要改源码或解析内部数据。
- C/C++ malloc/new：通常可覆盖动态链接场景下的 libc allocator API；对自定义 allocator、静态链接、直接 `mmap` 的覆盖需要验证。
- 多线程：支持思路上没问题，但高并发下开销和 trace 量要评估。

### 1.4.2 优点

- 对“哪个调用栈当前占用多少堆内存”非常贴近。
- 比 Valgrind 更轻，适合较长时间运行的程序。
- 输出更偏工程排查，适合看热点调用栈。
- 不需要重新编译目标程序，动态链接程序可用 `LD_PRELOAD` 注入。

### 1.4.3 缺点

- ARM32 交换机落地不确定性较高。Bytehound 生态主要面向常规 Linux 桌面/服务器，ARM32 需要交叉编译和实测。
- 依赖 Rust 工具链、目标 libc、unwind 能力和动态链接环境，部署成本偏高。
- 如果设备用 musl/uClibc、旧内核、裁剪 libc，兼容性需要验证。
- 如果目标程序静态链接，或 allocator 被程序内部替换，`LD_PRELOAD` 可能无效。
- 对“每个 block 的地址清单”不是最强项。

### 1.4.4 环境要求

运行侧通常需要：

- Linux 用户态。
- 目标进程动态链接，且允许 `LD_PRELOAD`。
- 目标架构需要能编译 Bytehound runtime，ARM32 需要交叉编译验证。
- 目标 libc 和动态加载器兼容。
- 足够的 RAM 和存储保存 trace。
- 如果要看符号化栈，目标程序最好带符号或保留单独 debug symbol。

构建侧通常需要：

- Rust/Cargo 工具链。
- ARM32 交叉编译工具链，例如 `arm-linux-gnueabihf-gcc` 或厂商 SDK。
- 与目标设备 libc ABI 匹配的 sysroot。

### 1.4.5 适用建议

如果你的交换机设备是 glibc、动态链接、空间尚可，并且你可以交叉编译 Rust 项目，Bytehound 很值得试。但它不是最稳妥的第一选择，建议先做最小 demo：一个 ARM32 设备上的 malloc/free 测试程序，确认调用栈、净值、符号和导出能力。

### 1.4.6 评分

7/10

核心能力贴近需求，但 ARM32 交换机落地风险和地址导出能力不确定，扣分。

## 1.5 Heaptrack

### 1.5.1 功能支持

Heaptrack 是 KDE 生态里的 heap memory profiler，常用方式是运行：

```bash
heaptrack ./your_program
```

它会拦截 heap allocation，记录调用栈，生成 `heaptrack.*.gz` 数据文件，再用 `heaptrack_gui` 或命令行工具分析。

对需求的满足情况：

- 当前存活堆内存：支持。能看 leaked、peak、temporary allocations 等，也能按调用栈统计分配量。
- 按调用栈聚合：支持，是它的核心能力。
- 自动减去 free：支持。它会记录 allocation/deallocation。
- 内存地址：部分支持。内部需要记录指针用于匹配释放，但常规报告主要是聚合统计，不是面向“列出每个活跃地址”的工具。
- malloc/new：支持常规 C/C++ heap API。
- mmap：覆盖程度取决于版本和拦截点，不能假定能完整覆盖所有匿名映射或自定义内存池。

### 1.5.2 优点

- 对 C/C++ heap 分析成熟，报告质量好。
- 比 Valgrind 快很多，更适合实际程序。
- 支持离线分析：设备上采集，PC 上打开结果。
- 命令行和 GUI 都可用，GUI 不一定要跑在交换机上。
- 对“哪个调用栈分配了多少，当前还剩多少”比较贴近。

### 1.5.3 缺点

- ARM32 设备上部署依赖偏重：libunwind、zlib、动态加载、符号解析相关库等。
- `heaptrack_gui` 不适合在交换机设备上跑，需要把结果拿到 PC。
- 交叉编译和依赖裁剪有一定成本。
- 对每个 block 的地址不是主要展示目标。
- 对静态链接程序、特殊 allocator、自定义内存池覆盖有限。

### 1.5.4 环境要求

运行侧通常需要：

- Linux。
- 目标程序动态链接，能被 heaptrack preload/interpose。
- ARM32 可执行的 heaptrack runtime。
- libunwind 或等价 unwind 支持。
- zlib，用于压缩 trace。
- 可写目录保存 `heaptrack.*.gz`。
- 程序和依赖库的符号文件最好可用。

分析侧建议：

- 在 x86 Linux PC 上安装完整 heaptrack 和 `heaptrack_gui`。
- 把设备上的 trace 文件和符号文件一起拷回 PC。
- 如果设备路径和 PC 路径不同，需要配置符号搜索路径。

### 1.5.5 适用建议

Heaptrack 是本需求下最值得优先验证的工具之一。建议把它作为“主力候选”，但先确认能否为你的 ARM32 SDK 成功编译 runtime，并确认采集文件大小是否能接受。

### 1.5.6 评分

8/10

调用栈、净存活内存和离线分析能力很好；地址明细和嵌入式依赖成本扣分。

## 1.6 gperftools / tcmalloc

### 1.6.1 功能支持

gperftools 提供 tcmalloc 和 heap profiler。它不是简单的外部观察工具，而是通过链接或预加载 tcmalloc 来替换 malloc 实现。典型方式：

```bash
LD_PRELOAD=/path/to/libtcmalloc.so HEAPPROFILE=/tmp/hprof ./your_program
```

或在程序链接时链接 tcmalloc。

对需求的满足情况：

- 当前存活堆内存：支持。heap profile 可以显示 in-use objects/bytes。
- 按调用栈聚合：支持，但质量依赖 unwinder/frame pointer。
- 自动减去 free：支持，因为 allocator 本身知道分配和释放。
- 内存地址：弱。gperftools heap profile 主要输出按调用栈聚合的对象数和字节数，不适合列出每个 block 地址。
- malloc/new：支持通过 tcmalloc 接管的分配。
- 自定义 allocator/mmap：不能完整覆盖。

### 1.6.2 优点

- 运行开销通常低于 Valgrind，适合嵌入式设备长期观察。
- 对“当前 in-use heap 按调用栈统计”很实用。
- 可以通过环境变量控制 dump，便于线上或准线上设备采集。
- 采集结果可离线用 `pprof` 分析。

### 1.6.3 缺点

- 会替换系统 malloc，可能改变程序内存行为。对交换机控制面进程要谨慎。
- 与目标 libc、线程库、动态链接器、已有 allocator 可能冲突。
- ARM32 上调用栈质量依赖 frame pointer 或 libunwind。
- 地址级信息不足。
- 如果程序静态链接或已经使用专用 allocator，接入成本较高。

### 1.6.4 环境要求

运行侧通常需要：

- ARM32 版本的 `libtcmalloc.so` 或静态链接 tcmalloc。
- 目标程序可动态预加载，或可重新链接。
- 可写目录保存 heap profile。
- 程序最好带 `-g` 和 `-fno-omit-frame-pointer`。
- 如果使用 libunwind，需要目标设备有对应库。

构建侧通常需要：

- gperftools 可针对目标 ARM32 libc 编译。
- 厂商 SDK/sysroot。
- 如果设备 libc 是 uClibc/musl，需要额外验证兼容性。

### 1.6.5 适用建议

如果你可以接受替换 malloc，gperftools 是交换机设备上很现实的方案，尤其适合“线上低开销看哪个调用栈占用最多”。但它不满足“需要完整地址信息”的要求，因此更适合作为主力统计工具加辅助手段，而不是唯一工具。

### 1.6.6 评分

7/10

净内存和调用栈能力强，嵌入式可行性比 Bytehound/Heaptrack 可能更好；但地址信息弱，且替换 allocator 有行为风险。

## 1.7 mtrace

### 1.7.1 功能支持

`mtrace` 是 glibc 提供的 malloc trace 机制。程序需要调用 `mtrace()`，并设置 `MALLOC_TRACE` 环境变量。它会记录 malloc/free 事件，之后用 `mtrace` 脚本分析。

典型方式：

```c
#include <mcheck.h>

int main(void) {
    mtrace();
    ...
}
```

```bash
MALLOC_TRACE=/tmp/mtrace.log ./your_program
mtrace ./your_program /tmp/mtrace.log
```

对需求的满足情况：

- 当前存活堆内存：支持有限。它可以通过 malloc/free 配对找出未释放内存。
- 按调用栈聚合：不支持。mtrace 主要记录调用点地址，不提供完整调用栈。
- 自动减去 free：支持。
- 内存地址：支持。trace 中会包含分配/释放地址。
- malloc/free：支持 glibc malloc 相关路径。
- new/delete：如果最终走 glibc malloc/free，可以间接覆盖；符号化和调用栈仍然弱。

### 1.7.2 优点

- 极轻量，部署简单。
- glibc 环境下无需复杂第三方库。
- 可以得到地址，适合确认某些 block 是否释放。
- 对 ARM32 没有额外架构门槛，只要目标是 glibc。

### 1.7.3 缺点

- 强依赖 glibc；musl/uClibc 环境通常不可用。
- 需要修改程序调用 `mtrace()`，或至少能控制初始化逻辑。
- 没有完整调用栈，只能看到分配点地址，复杂场景下定位能力不足。
- trace 文件可能很大。
- 不适合完整分析 C++、复杂多线程和自定义 allocator 场景。

### 1.7.4 环境要求

运行侧通常需要：

- glibc。
- 程序包含 `<mcheck.h>` 并调用 `mtrace()`。
- 设置 `MALLOC_TRACE` 到可写路径。
- 有足够空间保存文本 trace。

分析侧需要：

- `mtrace` 工具脚本。
- 目标程序符号文件。
- `addr2line` 或等价符号解析工具。

### 1.7.5 适用建议

mtrace 适合做低成本初筛或补充验证，特别是你明确需要 allocation address 时很有用。但它缺少完整调用栈，不满足你的核心需求，不建议作为主工具。

### 1.7.6 评分

5/10

地址和 free 配对不错，调用栈能力明显不足，且受 glibc 限制。

## 1.8 perf

### 1.8.1 功能支持

`perf` 是 Linux 内核性能分析工具。它可以采样 CPU、事件、tracepoint，也可以通过 uprobes 跟踪 `malloc/free`，或者结合 eBPF/perf script 做内存事件分析。

对需求的满足情况：

- 当前存活堆内存：默认不支持。需要自己把 malloc/free 事件配对，做用户态后处理。
- 按调用栈聚合：支持采样调用栈，但对 malloc/free 的完整精确统计不是默认能力。
- 自动减去 free：不支持，需要自研脚本。
- 内存地址：可以通过 uprobe 读取 malloc 返回值、free 参数，但配置复杂。
- malloc/new：需要分别挂 hook，C++ new/delete 可能要额外符号。
- mmap/munmap：可以通过 sys_enter/sys_exit tracepoint 或 uprobes 跟踪，但后处理复杂。

### 1.8.2 优点

- 系统级工具，很多 Linux 内核自带 perf_event 支持。
- 运行开销可控，适合采样和低频事件观察。
- 不需要替换 malloc。
- 可以分析 CPU、页错误、cache miss、调度等与内存相关的系统行为。

### 1.8.3 缺点

- 不是 heap profiler。不能开箱即用地回答“哪个调用栈当前还占用多少堆内存”。
- ARM32 上用户态调用栈采集质量依赖 frame pointer、内核配置和 perf 支持。
- uprobes/tracepoints 在嵌入式内核中可能被裁剪。
- 要完整跟踪 malloc 返回值和 free 参数，需要复杂脚本，且多线程、高频分配下事件量巨大。
- 对 stripped binary 和没有符号的库定位困难。

### 1.8.4 环境要求

运行侧可能需要：

- 内核启用 `CONFIG_PERF_EVENTS`。
- 如果用 uprobes，需要 `CONFIG_UPROBES`。
- 如果用 tracefs/debugfs，需要挂载 `/sys/kernel/tracing` 或 `/sys/kernel/debug/tracing`。
- 目标设备有 `perf` 用户态工具，且版本最好匹配内核。
- 允许访问 perf_event，`perf_event_paranoid` 不应限制过高。
- 栈回溯需要 frame pointer 或 DWARF unwind 支持。

### 1.8.5 适用建议

perf 不适合作为本需求的主工具。它适合辅助回答：

- 分配热点是否也消耗 CPU。
- 是否有大量 page fault。
- 是否有 mmap/brk 系统调用风暴。
- 内核态内存或 DMA 行为是否异常。

如果要用 perf 做精确 heap live set，需要自研 malloc/free 事件配对器，成本高且稳定性一般。

### 1.8.6 评分

4/10

系统观测能力强，但对用户态 heap live allocation 不是开箱即用。

## 1.9 dmabuffer_alloc_trace

### 1.9.1 功能支持

`dmabuffer_alloc_trace` 通常指围绕 Linux DMA-BUF 分配的 trace/debug 能力，可能来自 Android/vendor 内核、debugfs、tracefs 或厂商自定义补丁。它关注的是 DMA-BUF 对象，而不是普通进程 heap。

对需求的满足情况：

- 当前存活堆内存：不支持。它分析的是 DMA-BUF，不是 malloc heap。
- 按用户态调用栈聚合：通常不支持。最多有内核调用栈、进程名、pid、size、fd、inode 等信息，取决于内核实现。
- 自动减去 free：对 DMA-BUF 对象可能支持统计当前存在的 buffer。
- 内存地址：通常不会给普通用户态 heap 地址。DMA-BUF 可能有物理/IOVA/内核对象信息，但不是 malloc 指针。
- mmap/图形/驱动 buffer：可能有帮助。

### 1.9.2 优点

- 对 DMA-BUF 泄漏、驱动 buffer 泄漏、视频/图形/硬件加速内存问题有价值。
- 如果交换机芯片 SDK 使用 DMA-BUF 管理硬件 buffer，它可能非常关键。
- 运行开销一般较低，很多信息来自内核 debug/trace。

### 1.9.3 缺点

- 与普通用户态堆内存分析需求不匹配。
- 功能高度依赖内核版本和厂商补丁，不是标准统一工具。
- 用户态调用栈通常拿不到。
- 无法替代 heap profiler。

### 1.9.4 环境要求

运行侧可能需要：

- 内核启用 DMA-BUF。
- debugfs/tracefs 可用。
- 对应厂商内核提供 `dmabuffer_alloc_trace` 节点或 tracepoint。
- root 权限。
- 如果要看内核调用栈，需要 ftrace stacktrace 或相关配置。

### 1.9.5 适用建议

只有当你的“内存问题”涉及 DMA-BUF、驱动 buffer、硬件转发 buffer、视频/图形 buffer 或 ION/dma-heap 时，它才值得使用。对于普通进程 `malloc/free` 堆内存，它不是目标工具。

### 1.9.6 评分

2/10

对 DMA-BUF 专项有用，但基本不满足用户态 heap 调用栈和地址需求。

## 1.10 Valgrind

### 1.10.1 功能支持

Valgrind 是动态二进制插桩框架。与本需求相关的工具主要有：

- Memcheck：检测非法读写、未初始化值、泄漏、double free、use-after-free 等。
- Massif：heap profiler，分析堆内存峰值和调用栈。
- DHAT：分析 heap block 生命周期、使用情况和分配点。

对需求的满足情况：

- 当前存活堆内存：支持。Memcheck 泄漏检查、Massif snapshot、DHAT 都能从不同角度分析 live heap。
- 按调用栈聚合：支持。Valgrind 的调用栈通常比较可靠。
- 自动减去 free：支持。
- 内存地址：支持较好。Memcheck 报错和泄漏 block 会包含地址；DHAT/Massif更偏聚合和生命周期，地址明细取决于工具输出类型。
- malloc/free/new/delete：支持好。
- mmap/brk：Valgrind 能跟踪进程地址空间和堆行为，但不同工具关注点不同。
- 内存错误完整性：最强。非法访问、UAF、未初始化、重叠拷贝、泄漏分类等是其他工具难以替代的。

### 1.10.2 优点

- 对内存错误检查最完整。
- 不需要修改程序源码。
- 不需要替换 malloc。
- 调用栈质量通常好于很多轻量 profiler。
- 可以得到泄漏地址、分配栈、释放错误栈等详细信息。
- 对“内存相关完整性”最强。

### 1.10.3 缺点

- 运行开销极大，常见慢 10-100 倍，内存占用也会显著增加。
- ARM32 交换机设备上可能跑不动真实业务进程。
- 需要目标 CPU 指令集被 Valgrind 支持。ARM32 支持程度取决于具体架构、内核 ABI、浮点 ABI 和 Valgrind 版本。
- 对内核版本、syscall 支持有要求。交换机 SDK 上的私有 syscall/ioctl 可能遇到 Valgrind 不支持。
- 多进程、daemon、看门狗、实时性要求高的进程不适合直接跑。
- 静态链接、特殊 libc、特殊线程库可能有兼容性问题。

### 1.10.4 环境要求

运行侧通常需要：

- Valgrind 已移植到目标 ARM32 Linux。
- 目标 rootfs 有足够空间放 Valgrind 可执行文件、工具库和 suppression 文件。
- 目标设备有足够 RAM。
- 目标程序可以在 Valgrind 下慢速运行，最好是可控复现场景。
- 程序带 debug symbol，或至少可离线符号化。
- 对缺失 syscall/ioctl 可能要补 Valgrind wrapper 或加 suppression/绕过。

构建侧通常需要：

- ARM32 交叉编译工具链。
- 与设备 ABI 匹配：软浮点/硬浮点、EABI、glibc/uClibc/musl。
- Valgrind 对目标架构和 libc 的支持验证。

### 1.10.5 适用建议

Valgrind 是“最完整”的内存正确性工具，但不是最适合长期跑在交换机上的 profiler。建议作为实验室复现工具使用：

- 小流量、小用例、短时间运行。
- 用 Memcheck 查内存错误和泄漏。
- 用 Massif/DHAT 看堆增长路径。
- 如果目标业务无法在设备上承受 Valgrind 开销，考虑在同 ABI 的开发板或仿真环境复现。

### 1.10.6 评分

8/10

功能完整度最高，地址和调用栈能力强；但 ARM32 交换机上的性能和 syscall/ABI 兼容性风险很大。

## 1.11 总体对比表

| 工具 | 当前存活堆内存统计 | 自动减去 free | 调用栈 | 分配地址 | 覆盖完整性 | ARM32 交换机落地难度 | 运行开销 | 主要优点 | 主要缺点 | 推荐角色 | 评分 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|
| Bytehound | 强 | 是 | 强 | 中 | 中-强 | 高 | 中 | 贴近 live heap + stack 需求，体验好 | ARM32/嵌入式兼容性需实测，地址导出不一定直接 | 候选主工具 | 7 |
| Heaptrack | 强 | 是 | 强 | 中 | 中-强 | 中-高 | 中 | 成熟 heap profiler，离线分析好 | 依赖较多，地址明细不是重点 | 优先候选主工具 | 8 |
| gperftools/tcmalloc | 强 | 是 | 中-强 | 弱 | 中 | 中 | 低-中 | 低开销，适合长期观察 in-use heap | 替换 malloc，地址信息弱 | 线上/准线上统计工具 | 7 |
| mtrace | 中 | 是 | 弱 | 强 | 中-弱 | 低-中 | 低 | 简单轻量，有地址 | 无完整调用栈，强依赖 glibc | 辅助验证工具 | 5 |
| perf | 弱 | 否，需自研 | 中 | 中，需脚本 | 弱-中 | 中-高 | 低-中 | 系统级观测能力强 | 不是 heap profiler，不能直接统计 live heap | 辅助系统分析 | 4 |
| dmabuffer_alloc_trace | 不适用 | 仅 DMA-BUF | 弱 | 弱 | 仅 DMA-BUF | 中 | 低 | DMA-BUF/驱动 buffer 专项有效 | 不分析普通 malloc heap | DMA-BUF 专项工具 | 2 |
| Valgrind | 强 | 是 | 强 | 强 | 强 | 高 | 极高 | 内存错误检查最完整，地址和栈详细 | 很慢，嵌入式设备可能跑不动 | 实验室深度诊断工具 | 8 |

## 1.12 推荐组合

### 1.12.1 首选组合

建议组合：

1. Heaptrack：主力看“哪个调用栈当前占用多少 heap”。
2. Valgrind Memcheck/DHAT/Massif：实验室复现时做完整内存正确性分析。
3. gperftools/tcmalloc：如果 Heaptrack 难以部署，或需要更低开销长期观察，作为替代主力。
4. mtrace：需要分配地址、低成本验证 glibc malloc 泄漏时作为补充。
5. perf：辅助看 page fault、mmap/brk 频率、CPU 热点，不作为 heap live set 主工具。
6. dmabuffer_alloc_trace：只在怀疑 DMA-BUF/驱动 buffer 泄漏时启用。

### 1.12.2 如果设备极度受限

如果交换机上不能跑 Valgrind/Heaptrack/Bytehound，建议按以下顺序降级：

1. 先尝试 gperftools/tcmalloc heap profiler，因为开销相对可控。
2. 如果是 glibc 且允许改代码，使用 mtrace 获取地址级分配/释放日志。
3. 自研轻量 malloc wrapper：`LD_PRELOAD` 拦截 malloc/free，记录 pointer、size、caller return address 或 backtrace。
4. 用 perf/ftrace 观察 mmap/brk/page fault 作为系统级辅助。

### 1.12.3 如果“地址信息”是硬要求

严格要求每个未释放 block 都有地址、大小、分配调用栈时，最稳妥的路线不是直接选现成 GUI profiler，而是：

1. Valgrind Memcheck：用于短用例，直接给泄漏 block 地址和分配栈。
2. 自研或二次开发 malloc wrapper：用于设备长时间运行，记录 live map。
3. mtrace：glibc 环境下低成本得到地址，但调用栈不足。

Heaptrack、Bytehound、gperftools 更适合聚合视角，不一定满足“列出每个活跃地址”的硬要求。

## 1.13 推荐落地方案

### 1.13.1 第一阶段：确认环境

在交换机设备上确认：

```bash
uname -a
cat /proc/cpuinfo
ldd --version 2>&1 | head
getconf GNU_LIBC_VERSION 2>/dev/null
cat /proc/self/maps | head
mount | grep -E 'debugfs|tracefs'
cat /proc/sys/kernel/perf_event_paranoid 2>/dev/null
```

确认目标进程：

```bash
file ./your_program
readelf -h ./your_program
readelf -d ./your_program | grep NEEDED
readelf -s ./your_program | grep -E 'malloc|free|operator new|operator delete'
```

重点判断：

- 是否 ARM32 hard-float。
- libc 是 glibc、uClibc 还是 musl。
- 是否动态链接。
- 是否 strip。
- 是否允许 `LD_PRELOAD`。
- 是否有可写大目录，例如 `/tmp`、`/var/log`、外接存储。

### 1.13.2 第二阶段：优先验证 Heaptrack

如果能交叉编译 Heaptrack runtime：

```bash
HEAPTRACK_OUTPUT=/tmp/heaptrack.out heaptrack ./your_program
```

采集后把结果拷回 PC：

```bash
heaptrack --analyze heaptrack.your_program.*.gz
heaptrack_gui heaptrack.your_program.*.gz
```

验证点：

- 是否能启动。
- 是否能看到调用栈。
- 是否能看到 peak 和 leaked/in-use 信息。
- trace 文件增长速度是否可接受。

### 1.13.3 第三阶段：Valgrind 短用例深查

Memcheck：

```bash
valgrind \
  --tool=memcheck \
  --leak-check=full \
  --show-leak-kinds=all \
  --track-origins=yes \
  --num-callers=30 \
  --log-file=/tmp/vg.%p.log \
  ./your_program
```

Massif：

```bash
valgrind \
  --tool=massif \
  --stacks=yes \
  --massif-out-file=/tmp/massif.%p.out \
  ./your_program
```

DHAT：

```bash
valgrind \
  --tool=dhat \
  --num-callers=30 \
  --log-file=/tmp/dhat.%p.log \
  ./your_program
```

注意：Valgrind 不适合直接跑完整交换机业务长流程，建议构造最小复现场景。

### 1.13.4 第四阶段：低开销长期观察

如果 Heaptrack/Valgrind 都太重，可尝试 gperftools：

```bash
export LD_PRELOAD=/lib/libtcmalloc.so
export HEAPPROFILE=/tmp/hprof
export HEAP_PROFILE_ALLOCATION_INTERVAL=10485760
./your_program
```

必要时通过信号触发 dump，或在代码里调用 heap profiler API。

### 1.13.5 第五阶段：地址级硬需求

如果最终必须要完整输出：

- live block address
- size
- allocation stack
- free stack 或释放状态
- 按 stack 聚合的当前 size

建议实现一个轻量 ARM32 malloc wrapper。核心字段：

```text
ptr, size, timestamp, tid, allocation_backtrace[]
```

`free(ptr)` 时从 live map 删除。周期性输出：

```text
stack_hash, live_bytes, live_count
ptr, size, stack_hash
```

这比强行让 Heaptrack/gperftools 导出地址更可控，也更适合交换机环境裁剪。

## 1.14 最终结论

按你的需求“Linux ARM32 交换机、进程堆内存、按调用栈统计当前未释放内存、需要地址、内存相关尽量完整”，推荐排序如下：

| 排名 | 工具 | 结论 |
|---:|---|---|
| 1 | Heaptrack | 最适合作为主力 heap profiler，但要验证 ARM32 依赖和 trace 大小 |
| 2 | Valgrind | 功能最完整，适合短用例深查，不适合长时间真实业务 |
| 3 | gperftools/tcmalloc | 低开销实用方案，但地址信息弱且会替换 malloc |
| 4 | Bytehound | 能力贴近需求，但 ARM32 交换机落地风险较高 |
| 5 | mtrace | 简单、有地址，但没有完整调用栈 |
| 6 | perf | 很好的辅助工具，但不是 heap profiler |
| 7 | dmabuffer_alloc_trace | 只适合 DMA-BUF/驱动 buffer，不适合普通 heap |

如果只能选一个优先验证：选 Heaptrack。

如果必须要“地址 + 调用栈 + live block 完整清单”：短用例用 Valgrind，长期运行建议做轻量 malloc wrapper。

## 1.15 参考链接

- Bytehound: https://github.com/koute/bytehound
- Heaptrack: https://github.com/KDE/heaptrack
- gperftools: https://github.com/gperftools/gperftools
- gperftools heap profiler 文档: https://gperftools.github.io/gperftools/heapprofile.html
- glibc mtrace manual: https://www.gnu.org/software/libc/manual/html_node/Tracing-malloc.html
- Linux man-pages mtrace: https://man7.org/linux/man-pages/man3/mtrace.3.html
- perf wiki: https://perf.wiki.kernel.org/
- Linux DMA-BUF documentation: https://docs.kernel.org/driver-api/dma-buf.html
- Valgrind manual: https://valgrind.org/docs/manual/manual.html
- Valgrind Memcheck manual: https://valgrind.org/docs/manual/mc-manual.html
- Valgrind Massif manual: https://valgrind.org/docs/manual/ms-manual.html
- Valgrind DHAT manual: https://valgrind.org/docs/manual/dh-manual.html
