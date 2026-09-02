# 题库 · 模块 F：Linux 应用与驱动开发（共 55 题）

> **本模块知识点导图**
> - 内核模块：module_init/exit、insmod/rmmod/modprobe、模块参数、EXPORT_SYMBOL、GPL 许可与符号导出
> - 字符设备驱动：cdev 三件套、主/次设备号、file_operations、miscdevice、udev/devtmpfs 自动创建节点、open/release/read/write/ioctl/poll/mmap 驱动侧实现
> - 用户态与内核态交互：copy_to/from_user、access_ok、ioctl 命令编码（_IO/_IOR/_IOW）
> - 设备树（Device Tree）：DTS 结构、compatible 匹配、of_ API（of_iomap/of_get_resource/of_property_read）、pinctrl 与 overlay
> - 总线-设备-驱动模型：bus/device/driver 三角关系、probe/remove 时机、match 规则、platform 框架（resource/platform_data）、-EPROBE_DEFER 延迟探测
> - 内核并发与同步：spinlock vs mutex（能否睡眠）、原子操作、信号量、completion、中断共享与中断上下文禁忌
> - 中断处理：request_irq/threaded IRQ、上半部下半部、tasklet vs workqueue
> - 内核内存：kmalloc/vmalloc/ioremap、GFP 标志、DMA 基础（一致性 vs 流式映射）
> - 调试手段：printk 等级与 dev_ 系列日志、dmesg、/proc、/sys、devmem、ftrace、oops 解码（addr2line/objdump）、WARN_ON/BUG_ON、dynamic debug

---

## 一、单项选择题（22 题）

### F-001 ★
内核模块源码中 `MODULE_LICENSE("GPL")` 的作用是：
A. 仅是版权声明，对功能无影响
B. 声明模块许可证；只有 GPL 兼容许可的模块才能使用内核导出的 GPL 符号（EXPORT_SYMBOL_GPL），非 GPL 模块加载时会污染内核（tainted）且无法链接这些符号
C. 决定模块能否被卸载
D. 决定模块编译为 .ko 还是内建

**答案：B**
**解析**：
- 缺失或不兼容声明时，模块无法使用 EXPORT_SYMBOL_GPL 导出的符号（链接报 "Unknown symbol"），且内核被标记 tainted（dmesg 出现 "module: loading out-of-tree module taints kernel"），社区不给 tainted 内核报 bug 的支持；
- C 错：可否卸载取决于模块引用计数（lsmod 的 Used by）；
- D 错：内建/模块由 Kconfig 的 y/m 决定。
**知识点**：驱动-模块许可

### F-002 ★★
`insmod` 与 `modprobe` 的区别是：
A. 两者完全等价
B. modprobe 会自动解析并加载依赖模块（依据 modules.dep），insmod 只加载指定文件、不处理依赖
C. insmod 会自动处理依赖
D. modprobe 只能加载内建模块

**答案：B**
**解析**：insmod 直接把 .ko 塞进内核，缺依赖符号即报错；modprobe 按 /lib/modules/$(uname -r)/modules.dep 递归先装依赖，并支持按模块名（而非路径）与 /etc/modprobe.d 配置（别名、黑名单 blacklist、安装参数）。开发调试常用 insmod 看直接报错；产品环境用 modprobe。
**知识点**：驱动-模块加载工具

### F-003 ★★
字符设备驱动注册的核心三件套（新内核）是：
A. register_chrdev_region / cdev_init / cdev_add
B. kmalloc / copy_to_user / ioremap
C. platform_driver_register / of_match_table / module_init
D. request_irq / enable_irq / free_irq

**答案：A**
**解析**：
- register_chrdev_region（或 alloc_chrdev_region 动态分配）：拿到 dev_t（主+次设备号）；
- cdev_init(&my_cdev, &my_fops)：绑定操作表；cdev_add：注册进内核，此后内核能分派 open/read 到该设备；
- 最后一步是 udev/devtmpfs 自动创建 /dev 节点（旧内核手动 class_create + device_create）；
- misc 驱动（misc_register）把上述全部封装，适合"只有一个次设备号"的小驱动。
**知识点**：驱动-字符设备注册

### F-004 ★★
用户空间程序调用 `write(fd, buf, n)` 到达字符设备驱动后，驱动中负责搬运数据到内核的是：
A. memcpy(buf, kbuf, n)
B. copy_from_user(kbuf, buf, n)
C. strncpy(kbuf, buf, n)
D. 直接 return n

**答案：B**
**解析**：
- 用户指针不能在内核直接解引用：用户地址可能无效（缺页/恶意），且内核直接访问用户页会在缺页时死锁；
- copy_from_user/copy_to_user 做合法性校验 + 容错拷贝（失败返回未拷贝字节数，不 oops）；
- C 的 strncpy 遇到用户无效指针直接内核崩溃；
- 返回值约定：write 应返回成功拷贝的字节数，或 -EFAULT（copy_from_user 失败时未清零的返回值转换而来）。
**知识点**：驱动-用户内核数据拷贝

### F-005 ★★
关于设备树（Device Tree），正确的说法是：
A. 设备树是给 CPU 描述软件算法的
B. 设备树是描述硬件拓扑（外设、地址、中断、时钟、引脚配置）的数据结构（DTS 编译为 DTB），内核启动时解析它来创建平台设备，取代了旧的板级代码
C. 设备树就是文件系统树
D. 修改设备树必须重新编译内核

**答案：B**
**解析**：
- D（设备节点）+ 驱动通过 `compatible` 字符串匹配 —— "硬件描述"与"驱动逻辑"解耦，一份内核镜像通过不同 DTB 适配不同板子；
- D 错：只重新编译 dtc 生成 DTB，U-Boot 传新 DTB 即可，内核镜像不动——这正是设备树的核心价值；
- 常用属性：reg（地址+长度）、interrupts、clocks、pinctrl-0、status（"okay"/"disabled"）。
**知识点**：驱动-设备树概念

### F-006 ★★
platform 总线上设备与驱动匹配成功后，内核接下来执行的是：
A. 驱动的 probe 函数
B. 驱动的 remove 函数
C. open 函数
D. module_exit

**答案：A**
**解析**：match（按 compatible 或 name/id_table）成功 → 调 driver.probe(pdev)；匹配失败/设备移除/驱动卸载 → remove。probe 里完成：解析资源（of_iomap/platform_get_resource）、映射寄存器、request_irq、申请设备号、创建 /dev 节点。**"probe 没被调用"是最高频驱动初学问题**，排查顺序：① compatible 是否与驱动 of_match_table 完全一致（含大小写）；② status 是否 disabled；③ 内核 config 是否开启对应驱动（make menuconfig/模块是否加载）；④ 设备是否真的在 DTB 里（/proc/device-tree 下检查）。
**知识点**：驱动-platform框架

### F-007 ★★
中断处理函数（硬中断上半部）中**禁止**执行的操作是：
A. 读自己映射的寄存器
B. 睡眠（如调用可能阻塞的 kmalloc(GFP_KERNEL)、mutex_lock、msleep）
C. 给自旋锁加锁后立即解锁
D. 递增一个原子计数

**答案：B**
**解析**：
- 硬中断上下文不可睡眠：调度器无法切走中断上下文（没有独立 task 上下文），睡眠 = 内核 BUG/oops；
- kmalloc(GFP_KERNEL) 可能睡眠，必须用 GFP_ATOMIC；mutex 可能阻塞，必须 spinlock（且临界区极短）；
- A/C/D 合法且常见（自旋锁 + 原子计数 + 寄存器访问是上半部标准操作）。
**知识点**：驱动-中断上下文禁忌

### F-008 ★★
`spin_lock` 与 `mutex` 的选择原则是：
A. 优先 spinlock，性能总比 mutex 好
B. 进程上下文且临界区可能较长（或需要睡眠）用 mutex；中断上下文或临界区极短（几十条指令）用 spinlock
C. 两者可任意互换
D. mutex 可用于中断处理函数

**答案：B**
**解析**：
- spinlock：忙等（单核上实为关抢占），绝不睡眠——适用中断上下文与极短临界区；
- mutex：拿不到就睡眠让出 CPU——适用进程上下文、临界区长、可能睡眠（如持有锁期间调 copy_to_user）；
- A 错：长临界区用 spinlock 会白烧 CPU；D 错：中断中 mutex 睡眠 = BUG；
- 组合考点：中断与进程共享数据 → 进程侧用 spin_lock_irqsave（关本地中断防本 CPU 中断重入死锁），不能只 spin_lock。
**知识点**：驱动-锁选型

### F-009 ★★
驱动中 `kmalloc` 与 `vmalloc` 的区别，正确的说法是：
A. 两者都返回物理连续内存
B. kmalloc 返回物理连续内存（适合 DMA、小分配）；vmalloc 返回虚拟连续但物理可离散的内存（适合大缓冲，不能直接用于 DMA）
C. vmalloc 更快
D. kmalloc 分配大小无上限

**答案：B**
**解析**：
- kmalloc：物理连续、快、上限一般为 4MB（KMALLOC_MAX_SIZE）；DMA 需要物理连续（除 scatter-gather）；
- vmalloc：页表映射拼出连续虚拟地址，有 TLB 开销，DMA 不能直接用其返回地址；
- ioremap：与 vmalloc 类似的映射机制，专用于映射设备寄存器（MMIO）——三者经常一起考。
**知识点**：驱动-内核内存分配

### F-010 ★★
printk 的日志等级中，默认控制台输出阈值（console_loglevel）之下、数值上表示"最高严重级"的是：
A. KERN_INFO（6）
B. KERN_DEBUG（7）
C. KERN_EMERG（0）
D. KERN_WARNING（4）

**答案：C**
**解析**：
- 等级数值越小越紧急（0 EMERG ~ 7 DEBUG）；只有"消息等级数值 < console_loglevel"的消息才会打印到控制台；
- 临时调阈值：`echo 8 > /proc/sys/kernel/printk`（4 个数中第 2 个是 console_loglevel）；
- dmesg 永远能看全部日志（环形缓冲区 devkmsg）；`pr_err/pr_info/pr_debug` 是推荐写法；dev_dbg 需开 dynamic debug（CONFIG_DYNAMIC_DEBUG + /sys/kernel/debug/dynamic_debug/control）才输出。
**知识点**：驱动-printk日志

### F-011 ★★
`/dev/mem` 与 `devmem` 工具的典型用途是：
A. 格式化内存
B. 在用户空间直接读写物理地址（寄存器），用于无驱动时验证硬件寄存器（配合数据手册）
C. 释放内存
D. 加载内核模块

**答案：B**
**解析**：
- `busybox devmem 0x50002000`（读）、`devmem 0x50002000 32 0x1`（写）：生产调试阶段快速验证"这个寄存器写下去硬件有没有反应"，把问题切成"硬件/寄存器问题"还是"驱动逻辑问题"的第一刀；
- 前提：内核未开 CONFIG_STRICT_DEVMEM（嵌入式一般可用）；
- 关联：无驱动点亮一段裸寄存器也常用 mmap /dev/mem 后直接访问。
**知识点**：驱动-devmem硬件验证

### F-012 ★★★
驱动 probe 返回 `-EPROBE_DEFER` 的含义是：
A. 驱动代码写错了
B. 依赖的资源（时钟、regulator、GPIO、另一个设备）尚未就绪，内核稍后会自动重新尝试 probe
C. 设备树写错了
D. 内核内存不足

**答案：B**
**解析**：
- 典型场景：网卡驱动的 PHY 设备、时钟/电源在 probe 时还没 ready；返回 -EPROBE_DEFER 告诉内核"我不是失败，是还没轮到我"；
- 内核把它放回 deferred 链表，后续新设备注册时重试；用户可通过 `/sys/kernel/debug/devices_deferred` 查看积压——若某设备**永远**卡在这里，说明它的依赖链条上有人真正 probe 失败了；
- 初学误区：以为返回 DEFER 就是驱动有 bug，其实它是驱动模型设计的优雅降级。
**知识点**：驱动-延迟探测

### F-013 ★★
`request_threaded_irq()` 相比传统 `request_irq()` 的优势是：
A. 中断响应更快
B. 把中断处理拆成"轻量上半部（应答硬件）+ 内核线程下半部（可睡眠）"，线程化的下半部可以进行耗时处理、甚至持有 mutex、分配 GFP_KERNEL 内存
C. 不需要中断号
D. 只能用于 GPIO 中断

**答案：B**
**解析**：
- handler 返回 IRQ_WAKE_THREAD 时内核唤醒 irq 线程执行 thread_fn；线程上下文可睡眠，替代了手写 tasklet/workqueue 的样板代码；
- 对实时性友好的副作用：中断线程有调度优先级（默认 50），可以被高优先级实时任务抢占——系统实时性反而提升；
- A 错：多一次唤醒开销，裸延迟略增，换来的是整体实时性。
**知识点**：驱动-线程化中断

### F-014 ★★
用户程序对设备 fd 调用 `poll()`，驱动侧对应的 file_operations 成员是：
A. read
B. poll（驱动在 poll 回调里调用 `poll_wait()` 挂等待队列 + 返回当前就绪掩码）
C. select
D. ioctl

**答案：B**
**解析**：
- 驱动 poll 模板：①`poll_wait(file, &my_waitqueue, wait);` 注册等待队列（不阻塞，仅登记）；②返回掩码 `POLLIN | POLLRDNORM`（可读）或 `POLLOUT`（可写）或 0（未就绪）；
- 数据到达时（如中断里）`wake_up_interruptible(&my_waitqueue)` 唤醒阻塞在 poll/read 上的进程；
- 阻塞 read 的标准配套：无数据时 `wait_event_interruptible()` + 条件变量，被信号打断返回 -ERESTARTSYS。
**知识点**：驱动-poll支持

### F-015 ★★
`ioctl` 命令码的规范编码宏（`_IO/_IOR/_IOW/_IOWR`）的作用是：
A. 只是好看，可随便定义命令号
B. 把"方向（读/写）、类型（幻数）、命令序号、参数大小"编码进一个 32 位命令字，防止不同驱动命令冲突并让内核校验用户缓冲大小
C. 自动拷贝用户数据
D. 加密命令

**答案：B**
**解析**：
- 例：`#define MYIOC_RESET _IO('M', 0)`、`#define MYIOC_SET_FREQ _IOW('M', 1, uint32_t)`；
- 内核侧 `if (_IOC_DIR(cmd) == _IOC_WRITE) copy_from_user(...)`，用 _IOC_SIZE 自动获取长度；
- B 不规范的下场：命令号冲突 + 用户传错缓冲区尺寸直接踩内存——字符设备驱动的经典安全漏洞。
**知识点**：驱动-ioct命令编码

### F-016 ★★
设备树节点 `status = "disabled"` 的效果是：
A. 该节点及其子节点不会被内核创建为平台设备，对应驱动不会 probe
B. 驱动照常 probe，只是日志提示
C. 设备被禁用但中断仍使能
D. 仅影响 U-Boot

**答案：A**
**解析**：板级裁剪手段——同一份 SoC 级 DTSI，板级 DTS 中把用不到的外设 overlay 成 disabled，即可裁掉设备与驱动。反过来说，**"设备树里节点存在但 status 是 disabled"是 probe 不执行的常见原因之一**（与 F-006 的排查清单呼应）。
**知识点**：驱动-设备树status

### F-017 ★★
关于 `EXPORT_SYMBOL()` 与 `EXPORT_SYMBOL_GPL()`，正确的说法是：
A. 两者无区别
B. 都把内核符号（函数/变量）导出供其他模块使用；_GPL 版只允许 GPL 兼容许可的模块引用
C. 用于导出符号到用户空间
D. 用于卸载模块

**答案：B**
**解析**：模块间依赖（如公共库模块被多个驱动引用）必须 EXPORT_SYMBOL，否则加载报 "Unknown symbol in module"（用 `nm -D` 或 modinfo 查依赖）。_GPL 版配合 MODULE_LICENSE("GPL") 使用，闭源模块引用会被拒绝。
**知识点**：驱动-符号导出

### F-018 ★★★
内核 oops 信息中 `PC is at mydrv_read+0x38/0xc0`，`LR is at ...`，要定位到具体源码行，正确做法是：
A. 无法定位
B. 用带调试信息的 vmlinux（非压缩镜像）执行 `addr2line -e vmlinux -f -C <PC地址>`（或 `gdb vmlinux` 后 list *PC），偏移 +0x38 对应反汇编定位具体行；并可用 objdump -d 反汇编该函数
C. 查看 /etc/passwd
D. 重新格式化磁盘

**答案：B**
**解析**：
- 定位链：oops 的 PC 值（或函数名+偏移）→ `arm-none-linux-gnueabihf-objdump -d vmlinux | less` 找函数，按 +0x38 偏移找到出错指令 → addr2line 出文件:行号；
- 注意用**编译该内核的同一份 vmlinux**（含 debug info，CONFIG_DEBUG_INFO=y）；
- 配套信息：R0-R3 通常是出错参数、调用栈 Call trace 逐层回溯、`BUG: unable to handle kernel NULL pointer dereference` 直接说明错误类型；
- CONFIG_DEBUG_INFO_REDUCED 或裁剪过 debug info 会让 addr2line 失效——编译时保留调试信息是可调试性投资。
**知识点**：驱动-oops解码

### F-019 ★★
`/sys` 文件系统（sysfs）中，导出驱动/设备属性给用户空间的常规方式是：
A. 直接写 /dev
B. 定义 attribute（DEVICE_ATTR）并通过 sysfs_create_group 创建，用户空间用 cat/echo 读写
C. 修改内核源码重新编译
D. 使用 printk

**答案：B**
**解析**：
- 例：`static DEVICE_ATTR(threshold, 0644, threshold_show, threshold_store);` → `/sys/class/mydev/mydev/threshold` 可 cat 读、echo 写；
- 语义约定：**一个文件一个值、文本格式**——这是 sysfs 的铁律，方便 shell 脚本运维（不用写 C 程序）；
- 产品里"参数在线调整 + 状态查看"的标准做法就是 sysfs 属性 + udev 规则，而非发明私有 ioctl。
**知识点**：驱动-sysfs属性

### F-020 ★★
DMA"一致性映射（coherent/dma_alloc_coherent）"与"流式映射（dma_map_single）"的区别是：
A. 没有区别
B. 一致性映射的内存对 CPU 与设备都无需手动 cache 维护（硬件保证或非缓存）；流式映射需要 map/unmap 时做 cache 刷新/失效，适合一次性的传输缓冲
C. 流式映射不需要处理 cache
D. 一致性映射不能用于 DMA

**答案：B**
**解析**：
- dma_alloc_coherent：申请即映射，无需每次同步（通常是非 cache 区或硬件一致性），适合高频小包（描述符环）；
- dma_map_single：普通 kmalloc 内存，传输前 map（刷 cache）、传输完成 unmap（失效 cache）或 dma_sync_single_for_cpu；适合大块偶发传输；
- 嵌入式强相关：无 IOMMU/无硬件一致性的平台上忘记流式同步 = **数据偶发错乱**（cache 里是旧值），极难排查——F-037 排查题会展开。
**知识点**：驱动-DMA映射

### F-021 ★★
`ioremap()` 的返回值正确的用法是：
A. 当作普通内存指针直接 memcpy 大量数据
B. 作为 MMIO 寄存器虚拟地址，用 readl/writel（或 ioread32/iowrite32）访问；少量数据可用 memcpy_fromio/toio
C. free 后继续使用
D. 直接 free 掉

**答案：B**
**解析**：
- 寄存器区映射后是（可能）强序非缓存设备内存，编译器重排与 CPU 乱序都会出问题；readl/writel 自带内存屏障语义保证访问顺序与到达硬件；
- C 是典型的 use-after-free；释放用 iounmap（配 request_mem_region/iounmap+release_mem_region 成对）；
- 与 mmap 实现联动：驱动 mmap 里用 io_remap_pfn_range 把寄存器页暴露给用户空间（用户态直接操作寄存器的正规途径）。
**知识点**：驱动-MMIO访问

### F-022 ★★★
ftrace 相比 printk 调试驱动的主要优势是：
A. 不需要内核配置
B. 无需改代码插入打印，动态跟踪函数调用（function tracer）、事件、调用栈与延迟（irqsoff/preemptoff），开销可动态开关，且带时间戳可分析时序
C. 输出更漂亮
D. 只能用于用户态程序

**答案：B**
**解析**：
- 经典用法：`echo function > /sys/kernel/debug/tracing/current_tracer` + `echo mydrv_probe > set_ftrace_filter` → cat trace 只看该函数的调用流；
- `echo 1 > events/irq/enable` 开事件；irqsoff tracer 找"关中断最久"的凶手（实时性问题定位神器）；
- A 错：需 CONFIG_FTRACE/CONFIG_FUNCTION_TRACER（多数发行版默认开）；
- 与 printk 的关系：printk 看"点"，ftrace 看"线"（时序/调用路径）；产品级时序问题（偶发卡顿）几乎必须 ftrace。
**知识点**：驱动-ftrace动态跟踪

## 二、多项选择题（6 题）

### F-023 ★★
以下哪些操作属于"驱动 probe 函数"的典型职责？
A. 从设备树/platform 资源获取寄存器地址并 ioremap
B. request_irq 注册中断（或 gpiod_to_irq）
C. 分配并注册字符设备/misc 设备，创建 /dev 节点
D. 初始化硬件寄存器、复位外设
E. 执行长时间 msleep 等待硬件稳定（数秒级）

**答案：A、B、C、D**
**解析**：
- A~D 是标准 probe 流程四件套；
- E 错：probe 在内核启动/模块加载路径上执行（且持有设备锁），秒级睡眠会显著拖慢启动甚至触发超时；需要慢初始化应放到工作队列/独立 kthread 或 request_threaded_irq 的下半部。
**知识点**：驱动-probe职责

### F-024 ★★
关于设备树节点与驱动匹配，下列说法正确的有：
A. 驱动 of_match_table 中的 compatible 字符串必须与 DTS 节点的 compatible 属性（列表中任一）完全一致才匹配
B. 一个节点可以有多个 compatible 字符串（从特殊到通用排列），驱动可匹配其中任一个
C. compatible 通常采用 "厂商,器件名" 的命名约定（如 "fsl,imx6-uart"）
D. 匹配成功后驱动可通过 platform_get_resource 获取 DTS 中的 reg/interrupts 资源
E. 设备树中两个节点可以用完全相同的 compatible 且无需其他区分手段

**答案：A、B、C、D**
**解析**：
- A/B/C/D 均正确；B 是兼容设计惯例：`compatible = "vendor,new-chip", "vendor,old-chip"`——新芯片先试专属驱动，退回通用驱动；
- E 不严谨：两个相同 compatible 的节点（如同型双 UART）匹配同一驱动，靠**不同的 reg 地址/别名/节点路径**区分实例（probe 被调用两次，各自资源不同）。若完全无区分信息则设计有误。
**知识点**：驱动-compatible匹配

### F-025 ★★
中断上下文（硬中断）中允许执行的操作包括：
A. spin_lock/spin_unlock（短临界区）
B. 原子操作 atomic_inc
C. wake_up_interruptible 唤醒等待队列
D. kmalloc(GFP_ATOMIC)
E. msleep(1)

**答案：A、B、C、D**
**解析**：
- A/B：中断上下文标准操作；C：唤醒进程是中断的常见收尾（配 poll_wait，见 F-014）；D：GFP_ATOMIC 从紧急池分配不睡眠（失败返回 NULL，驱动要判空）；
- E 错：任何形式的睡眠（msleep/mutex/可能阻塞的 kmalloc(GFP_KERNEL)/copy_to_user 缺页）在中断上下文都是 BUG。
**知识点**：驱动-中断上下文许可操作

### F-026 ★★
排查"驱动 probe 未执行"问题，正确的检查步骤包括：
A. 确认驱动已编译进内核或 .ko 已 insmod（lsmod / 内核日志）
B. 检查 /proc/device-tree 下该节点的 compatible 与 status
C. 对比驱动 of_match_table 与 DTS compatible 是否逐字符一致
D. 查 dmesg 中是否有 -EPROBE_DEFER 或依赖设备失败的信息
E. 直接重装操作系统

**答案：A、B、C、D**
**解析**：四步即标准排查树（配置→设备树→匹配→依赖）。补充工具：`ls /sys/bus/platform/devices/` 看设备是否注册；`cat /sys/bus/platform/drivers/<drv>/` 看绑定状态；绑定了的设备会出现在驱动目录下（软链接）。E 显然是玩笑级干扰项。
**知识点**：驱动-probe排查

### F-027 ★★
关于 workqueue 与 tasklet 的对比，正确的有：
A. workqueue 运行在内核线程上下文，允许睡眠；tasklet 运行在软中断上下文，不允许睡眠
B. tasklet 执行时机更接近中断（延迟小），workqueue 因调度延迟略大
C. 延后工作中需要 kmalloc(GFP_KERNEL)、mutex、大量计算时，应选 workqueue
D. 新内核推荐 INIT_WORK + schedule_work 的接口，几乎不再手写 tasklet
E. 两者都运行在中断处理函数的调用栈上

**答案：A、B、C、D**
**解析**：
- A/B/C 是选型三要素；D 是趋势：tasklet 逐步被线程化 IRQ 与 workqueue 取代（内核文档已标记 tasklet 为"过渡 API"）；
- E 错：两者都不在中断栈上——tasklet 由 ksoftirqd 或中断返回路径触发，workqueue 由 kworker 线程执行。
**知识点**：驱动-下半部机制

### F-028 ★★★
以下属于"降低中断负载"的工程手段的有：
A. 中断 + DMA：硬件批量搬运数据，CPU 只在整块完成时被中断一次
B. NAPI（网络子系统的轮询/中断混合模式）：高流量时关中断改轮询，低流量恢复中断
C. 合并中断/中断聚合（interrupt coalescence）：网卡等硬件攒一批事件再触发一次中断
D. 上半部把工作全部做完，不用下半部
E. 多队列/亲和性：把不同硬件队列中断绑到不同 CPU 核处理

**答案：A、B、C、E**
**解析**：
- A/C/E 是"减少中断次数与分散中断处理"的硬件+系统手段；B 是 Linux 网络栈的经典设计（在极高包率下中断风暴比丢包更致命，所以切换到轮询）；
- D 错：方向反了——上半部越长中断延迟越大，必须"上半部最小化 + 下半部延后"。
**知识点**：驱动-中断负载优化

## 三、填空题（5 题）

### F-029 ★
内核模块加载/卸载函数的注册宏分别是 module_init() 与______。

**答案**：module_exit()
**解析**：module_exit 注册的函数在 rmmod 时调用，负责释放 probe 期间申请的所有资源（设备号、irq、ioremap、类/设备节点）。**内建（=y）驱动的 exit 函数不会执行**（内核不卸载）。资源不释放 = 卸载后再加载必然失败/泄漏。
**知识点**：驱动-模块生命周期

### F-030 ★★
设备号 dev_t 由主设备号（major，标识驱动）和______（标识具体设备实例）组成。

**答案**：次设备号（minor）
**解析**：`MAJOR(dev_t)`/`MINOR(dev_t)` 提取；alloc_chrdev_region 动态分配主号（配合 udev 是主流），register_chrdev_region 静态指定。同一次号组由同一驱动 fops 服务，驱动内用 MINOR(inode->i_rdev) 区分实例。
**知识点**：驱动-设备号

### F-031 ★★
用户态阻塞读设备时，驱动 read 回调中无数据可读的标准做法是调用宏 `______(wq, condition)`，它睡眠直至条件为真或被信号打断。

**答案**：wait_event_interruptible
**解析**：`wait_event_interruptible(my_wq, data_ready)`：条件假则睡眠（可被信号打断，返回 -ERESTARTSYS，read 应回传它让系统自动重启调用）；数据到达路径（中断/写端）执行 `wake_up_interruptible(&my_wq)`。不可中断版本 wait_event 只用于"睡多久都必须等"的场景。
**知识点**：驱动-阻塞读实现

### F-032 ★★
将物理寄存器地址映射为内核虚拟地址的函数是 ioremap()，其逆操作是______()。

**答案**：iounmap
**解析**：规范配对：`request_mem_region(start, len, name)` → `ioremap` → 使用 → `iounmap` → `release_mem_region`。region 申请把地址"圈地"进 /proc/iomem，防止两个驱动映射同一寄存器段（映射冲突在启动日志中可见）。
**知识点**：驱动-IO映射

### F-033 ★★
设备树源文件 .dts 通过编译器______编译为 .dtb，由 U-Boot 加载并传递给内核。

**答案**：dtc（Device Tree Compiler）
**解析**：`dtc -I dts -O dtb -o board.dtb board.dts`；反编译核查用 `dtc -I dtb -O dts`。内核源码树 make dtbs 会编译所有启用板卡的 DTB。运行期核查设备树：`ls /proc/device-tree/`（软链接到当前 DTB）。
**知识点**：驱动-设备树编译

## 四、判断题（5 题）

### F-034 ★
驱动模块的 .ko 文件与内核版本必须严格匹配（vermagic），跨版本直接 insmod 会失败。（ ）

**答案：对**
**解析**：模块带 vermagic（内核版本+SMP/preempt 等指纹），不匹配报 "version magic mismatch"。解决：为目标内核源码树重新编译模块（make -C /lib/modules/$(uname -r)/build M=$PWD modules）。嵌入式的"内核与驱动分开交付"场景必须用同一套源码与配置编译。
**知识点**：驱动-模块版本匹配

### F-035 ★★
`copy_to_user()` 的返回值是成功拷贝的字节数。（ ）

**答案：错**
**解析**：返回值是**未能拷贝的字节数**（0 表示全部成功），失败时应返回 -EFAULT 给用户。与 read/write 的"返回成功字节数"习惯正好相反，是笔试高频陷阱。可用 `ret = copy_to_user(...); if (ret) return -EFAULT;` 的惯用法。
**知识点**：驱动-copy语义

### F-036 ★★
在中断处理函数中可以调用 `spin_lock()`；在进程上下文中与中断共享的数据也只需用 `spin_lock()`。（ ）

**答案：错（前半句对，后半句错）**
**解析**：
- 中断里 spin_lock 合法；
- 但**进程上下文**保护"中断也会访问"的数据时，若只 spin_lock：进程持锁瞬间被同核中断打断，中断里再 spin_lock 同一把锁 → 死锁（中断无法被持锁进程唤醒，单核直接自旋到底）；
- 正解：进程侧 `spin_lock_irqsave(&lock, flags)`（保存并关本地中断），中断侧可继续 spin_lock（中断本来就不可被本核中断打断）。
**知识点**：驱动-自旋锁与中断

### F-037 ★★
`platform_get_resource(pdev, IORESOURCE_MEM, 0)` 获取的是设备树节点 reg 属性描述的寄存器区域。（ ）

**答案：对**
**解析**：DTS 的 reg → 内核自动转成 platform 设备的 IORESOURCE_MEM 资源；interrupts → IORESOURCE_IRQ（platform_get_irq / platform_get_resource(pdev, IORESOURCE_IRQ, n)）；时钟、pinctrl 通过各自的 API（devm_clk_get/devm_gpiod_get）按名字引用。resource 索引 n 对应 reg/中断列表的第 n 项。
**知识点**：驱动-资源获取

### F-038 ★★★
`devm_kmalloc()` 分配的内存在驱动 remove 或 probe 失败时会被内核自动释放，无需手动 kfree。（ ）

**答案：对**
**解析**：devm（device-managed）系列：devm_kmalloc/devm_ioremap/devm_request_irq/devm_gpiod_get… 全部挂到设备生命周期，remove/失败路径自动逆序释放——**消灭了"probe 失败 6 个 goto 出口漏释放其中一个资源"这类经典 bug**。代价：生命周期绑死设备，模块自己管理复用内存时不适用。新驱动应默认用 devm 系列。
**知识点**：驱动-devm资源管理

## 五、简答题（7 题）

### F-039 ★★
简述 Linux 设备驱动模型中 bus、device、driver 三者的关系与 probe 触发流程。

**参考答案**：
- **关系**：bus 是匹配场所（platform/i2c/spi/usb/pci 总线各自实现 match 回调）；device 描述"硬件存在"（来自设备树或代码注册），driver 描述"怎么操作某类硬件"；
- **匹配**：设备或驱动任一注册到总线时，总线调用 match——platform 按 compatible（of_match_table）/name/id_table 匹配，i2c/spi 按 address+name；
- **probe**：match 成功 → 内核调 driver->probe(dev)，驱动完成资源获取与硬件初始化；probe 返回 0 建立绑定（/sys/bus/platform/drivers/xxx/ 下出现设备软链接）；
- **remove**：设备注销/驱动卸载/probe 失败时调用，释放资源；
- **价值**：一套驱动代码 + 数据描述（DTB）适配任意多板卡；电源管理（runtime PM）、热插拔都挂在该模型上。
**知识点**：驱动-总线设备驱动模型

### F-040 ★★
字符设备驱动中 open/read/write 的完整调用链（从用户程序到驱动）是怎样的？

**参考答案**：
1. 用户 `open("/dev/mydev", O_RDWR)` → glibc → 系统调用 sys_open；
2. VFS 依路径找 inode（设备节点由 devtmpfs/udev 创建，inode 内含 dev_t）；
3. VFS 按 major 在 cdev_map 中找到注册的 cdev（含 fops），把 file->f_op 指向驱动的 file_operations，调用驱动 `.open`（如做独占判断、上电）；
4. `read(fd, buf, n)` → sys_read → VFS 调 f_op->read（新驱动实现 `.read_iter` 也可）→ 驱动里：检查数据可用性 → `copy_to_user(buf, kbuf, n)` → 返回字节数（0 表示 EOF，负值为 errno）；
5. `write` 同理，`copy_from_user` 进内核后通常还要校验（长度、格式）；
6. close 调 `.release`（注意：**release 在最后一个 fd 关闭时才调用**，与 open 一一对应的语义要区分 dup/fork 造成的引用计数）。
**知识点**：驱动-VFS调用链

### F-041 ★★
简述设备树中一个典型 SPI/I2C 外设节点的结构，并说明驱动如何取用其中信息。

**参考答案**（以 SPI 传感器为例）：

```dts
&spi1 {
    status = "okay";
    spidev0: sensor@0 {
        compatible = "acme,tph080";
        reg = <0>;                    /* 片选 CS0 */
        spi-max-frequency = <10000000>;
        interrupt-parent = <&gpio1>;
        interrupts = <5 2>;           /* GPIO1_5, 下降沿 */
        vdd-supply = <&reg_3v3>;
    };
};
```
驱动侧取用：
- `of_match_table` 中 `compatible` 匹配节点；
- `spi->irq`（SPI 核心已解析）或 `of_irq_get` 取中断号；
- `devm_gpiod_get(dev, "reset", GPIOD_OUT_LOW)` 按名字取 GPIO（对应 reset-gpios 属性）；
- `devm_regulator_get(dev, "vdd")` 取电源 regulator；
- 自定义属性用 `of_property_read_u32(np, "acme,sample-rate", &rate)` 读取；
- 好处：换板只改 DTS，驱动零改动。
**知识点**：驱动-设备树节点解析

### F-042 ★★
驱动中实现用户空间 mmap（把设备寄存器或 DMA 缓冲映射给用户）的要点是什么？

**参考答案**：
- 实现 `.mmap` 回调：`vm->vm_pgoff` 是用户要求的物理页偏移；
- 寄存器区：`io_remap_pfn_range(vm, vaddr, (phys >> PAGE_SHIFT), size, pgprot_noncached(vm->vm_page_prot))`——**必须非缓存属性**，否则用户读写被 cache 吞掉/延迟；
- DMA 缓冲：dma_mmap_coherent(dev, vm, cpu_addr, dma_handle, size)——一致性映射内存直接映射（它本就非 cache 或硬件一致）；
- 通用防护：校验 size/offset 合法性、`vm->vm_flags |= VM_DONTEXPAND | VM_DONTDUMP`（禁止扩容与进 core dump，防信息泄漏/越界）；
- 使用场景：用户态直接操作寄存器（低延迟控制）、零拷贝共享数据帧、UI frame buffer。
**知识点**：驱动-mmap实现

### F-043 ★★★
简述 kmalloc/vmalloc/ioremap 三者用途区别，并说明各自适合/禁止的场合。

**参考答案**：
| 函数 | 物理连续 | 用途 | 适合/禁止 |
|------|---------|------|----------|
| kmalloc | 是 | 内核通用小对象（<4MB） | 适合 DMA 缓冲、描述符；GFP_KERNEL 可睡（仅进程上下文），GFP_ATOMIC 中断可用 |
| vmalloc | 否（仅虚拟连续） | 大缓冲（MB 级查表、大数组） | 适合大而不做 DMA 的内存；禁止直接给 DMA 用地址、有 TLB 开销 |
| ioremap | 映射 MMIO | 设备寄存器窗口 | 适合 readl/writel 访问；禁止当普通内存 memset/大量 memcpy、禁止解引用做运算 |
- 共同纪律：谁申请谁释放，配对释放（kmalloc/kfree、vmalloc/vfree、ioremap/iounmap），devm 系列可自动管理；
- 高频陷阱：把 ioremap 返回值当普通指针 `*p = x`（在无 device memory 抽象的平台上行为不可预期，必须 writel）。
**知识点**：驱动-内存三件套

### F-044 ★★
简述 dynamic debug（动态调试）机制与使用方法。

**参考答案**：
- 编译时内核开 CONFIG_DYNAMIC_DEBUG，代码中用 `pr_debug()/dev_dbg()`（默认不输出）；
- 运行期通过 `/sys/kernel/debug/dynamic_debug/control` 精确开关：`echo 'file mydrv.c line 120 +p' > control`（文件+行）、`echo 'func mydrv_probe +p' > control`（函数）、`echo 'module mydrv +p' > control`（整个模块）；
- 关闭：把 +p 换成 -p；`+p` 还可叠加格式控制（+t 加时间戳等）；
- 价值：**量产镜像保留全部调试点但零开销关闭**，现场问题开启指定行调试无需重新编译——嵌入式产品的调试基建标配。对比：printk 分级只能按等级粗粒度开关。
**知识点**：驱动-动态调试

### F-045 ★★★
简述如何系统化排查"驱动加载成功但读取数据偶发错误（约万分之一概率）"这类概率性问题。

**参考答案**：
1. **缩小范围——硬件还是软件**：用 devmem 直接读寄存器（F-011）做基准对比；硬件侧用示波器/逻辑分析仪抓信号质量（干扰、边沿、时序余量）；
2. **怀疑并发竞态**：审查数据路径的中断与进程共享是否用对锁（spin_lock_irqsave 而非 spin_lock，见 F-036）、标志是否漏 volatile/屏障、等待队列唤醒时序；
3. **怀疑 cache/DMA 一致性**（无硬件一致平台高发）：检查流式 DMA 是否漏 dma_sync_single_for_cpu/for_device（F-020）——症状恰是"偶发旧数据"；
4. **怀疑边界条件**：缓冲长度溢出、off-by-one、读快于写时半包；用 KASAN（内核地址消毒器，CONFIG_KASAN）抓越界/释放后使用；
5. **概率放大复现**：提高中断频率/并发度/温度应力，让问题从 1/万 到 1/百，才能验证修复；
6. **留证据手段**：错误现场把相关寄存器、环形缓冲快照记到 nofail 日志区；kprobe/eprobe 挂探针不改代码。
**方法论**：概率问题 = 竞态/时序/cache 类，几乎从不是"逻辑写错"——先找物理层与内存序，再审代码。
**知识点**：驱动-概率故障排查

## 六、编程题（6 题）

### F-046 ★★（找错）
以下字符设备驱动 read 实现有哪些错误？

```c
static ssize_t my_read(struct file *f, char __user *ubuf, size_t n, loff_t *off)
{
    char kbuf[16] = "hello driver";
    memcpy(ubuf, kbuf, n);            /* 拷给用户 */
    return n;
}
```

**答案**：
错误 1：**直接 memcpy 到用户指针**——用户指针不能直接解引用（见 F-004），必须 `copy_to_user(ubuf, kbuf, n)`；
错误 2：**未校验 n 与源缓冲大小**——n 可能大于 16（用户传 count=4096），memcpy 读越界；应 `size_t len = min(n, sizeof(kbuf));`；
错误 3：**未处理 copy_to_user 返回值**——失败返回非 0，应 `return -EFAULT`；
修正版：

```c
static ssize_t my_read(struct file *f, char __user *ubuf, size_t n, loff_t *off)
{
    char kbuf[16] = "hello driver";
    size_t len = min(n, sizeof(kbuf));
    if (copy_to_user(ubuf, kbuf, len))
        return -EFAULT;
    return len;
}
```
**知识点**：驱动-read实现规范

### F-047 ★★★（写代码）
写一个完整的最小字符设备驱动骨架（misc 设备），支持 open/release/read，并说明每个部分作用。

**参考答案**：

```c
#include <linux/module.h>
#include <linux/miscdevice.h>
#include <linux/fs.h>
#include <linux/uaccess.h>

static char msg[] = "hello misc\n";
static int opened;                       /* 演示独占访问计数 */

static int my_open(struct inode *inode, struct file *file)
{
    if (opened++)                        /* 简易独占:第二个打开者拒绝 */
        { opened--; return -EBUSY; }
    return 0;
}

static int my_release(struct inode *inode, struct file *file)
{
    opened--;
    return 0;
}

static ssize_t my_read(struct file *file, char __user *buf,
                       size_t count, loff_t *ppos)
{
    size_t len = min(count, sizeof(msg) - 1 - (size_t)*ppos);
    if (len == 0) return 0;              /* EOF */
    if (copy_to_user(buf, msg + *ppos, len))
        return -EFAULT;
    *ppos += len;                        /* 维持偏移,重复 read 不重复给数据 */
    return len;
}

static const struct file_operations my_fops = {
    .owner   = THIS_MODULE,              /* 防止 fops 还在被用时模块被卸载 */
    .open    = my_open,
    .release = my_release,
    .read    = my_read,
};

static struct miscdevice my_misc = {
    .minor = MISC_DYNAMIC_MINOR,         /* 自动分配次设备号 */
    .name  = "mydev0",                   /* /dev/mydev0 */
    .fops  = &my_fops,
    .mode  = 0666,                       /* 节点权限,免手 chmod */
};

static int __init my_init(void)
{
    int ret = misc_register(&my_misc);   /* 一步搞定设备号+cdev+节点 */
    pr_info("mydev registered %s\n", ret ? "FAIL" : "OK");
    return ret;
}
static void __exit my_exit(void)
{
    misc_deregister(&my_misc);
}

module_init(my_init);
module_exit(my_exit);
MODULE_LICENSE("GPL");
```
**逐段讲解**：
- misc_register 一行完成 F-003 三件套 + /dev 节点——小驱动首选；
- `.owner = THIS_MODULE`：用户进程还开着 fd 时禁止 rmmod（否则释放后调用 fops = oops）；
- *ppos 维护：cat 这类工具会反复 read 直到 EOF，不推进偏移会死循环输出。
**知识点**：驱动-misc驱动骨架

### F-048 ★★★（写代码）
为字符设备实现 poll 支持：设备有数据时 poll 返回可读，无数据时阻塞；数据由（模拟的）中断路径 wake_up。

**参考答案**：

```c
#include <linux/poll.h>
#include <linux/wait.h>

static DECLARE_WAIT_QUEUE_HEAD(rx_wq);
static bool data_ready;                  /* 有数据标志,实际驱动由中断置位 */

/* --- 数据到达路径(真实驱动在硬中断或下半部中) --- */
static void rx_isr(void)
{
    data_ready = true;
    wake_up_interruptible(&rx_wq);       /* 唤醒阻塞在 poll/read 的进程 */
}

static unsigned int my_poll(struct file *file, poll_table *wait)
{
    unsigned int mask = 0;
    poll_wait(file, &rx_wq, wait);       /* 1.登记等待队列(不阻塞) */
    if (data_ready)
        mask |= POLLIN | POLLRDNORM;     /* 2.报告当前就绪状态 */
    return mask;
}

static ssize_t my_read(struct file *file, char __user *buf,
                       size_t count, loff_t *ppos)
{
    ssize_t ret = wait_event_interruptible(rx_wq, data_ready);
    if (ret)          return ret;        /* -ERESTARTSYS:被信号打断 */
    /* ...取数据 copy_to_user... */
    data_ready = false;                  /* 数据被消费 */
    return ret ? ret : count;
}
```
**逐行讲解**：
- poll_wait 不会睡眠，只是把 wq 挂进 poll 表；真正阻塞发生在 poll 系统调用层（多 fd 统一等）；
- 返回 mask 的即时快照语义：调用时刻没数据就返回 0（未就绪），醒来后 VFS 重查各驱动的 poll；
- read 用同一个 wq —— poll 与阻塞 read 共享等待队列是标准设计；
- data_ready 实际工程应为含锁保护的队列非空判断，此处以 bool 示意机制。
**知识点**：驱动-poll实现

### F-049 ★★★（写代码）
写一个 platform 驱动的 probe/remove 骨架：从设备树取寄存器与中断，devm 方式申请资源，threaded IRQ 处理中断。

**参考答案**：

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/mod_devicetable.h>
#include <linux/interrupt.h>
#include <linux/io.h>

struct my_dev {
    void __iomem *base;
    int irq;
};

static irqreturn_t my_hard_isr(int irq, void *devid)
{
    struct my_dev *m = devid;
    u32 st = readl(m->base + REG_STATUS);
    if (!(st & ST_MASK))
        return IRQ_NONE;                 /* 不是我的中断(共享中断必须判) */
    writel(st & ST_MASK, m->base + REG_CLR);  /* 清中断标志:必须在上半部 */
    return IRQ_WAKE_THREAD;              /* 唤醒线程下半部 */
}

static irqreturn_t my_thread_fn(int irq, void *devid)
{
    struct my_dev *m = devid;
    /* 可睡眠:取数据、kmalloc(GFP_KERNEL)、上报、唤醒用户等待队列 */
    process_event(m);
    return IRQ_HANDLED;
}

static int my_probe(struct platform_device *pdev)
{
    struct my_dev *m;
    int ret;

    m = devm_kzalloc(&pdev->dev, sizeof(*m), GFP_KERNEL);
    if (!m) return -ENOMEM;
    platform_set_drvdata(pdev, m);

    m->base = devm_platform_ioremap_resource(pdev, 0);  /* region+ioremap 一步 */
    if (IS_ERR(m->base)) return PTR_ERR(m->base);

    m->irq = platform_get_irq(pdev, 0);
    if (m->irq < 0) return m->irq;

    ret = devm_request_threaded_irq(&pdev->dev, m->irq, my_hard_isr,
                                    my_thread_fn,
                                    IRQF_TRIGGER_FALLING | IRQF_ONESHOT,
                                    "mydev", m);
    if (ret) return dev_err_probe(&pdev->dev, ret, "irq request failed\n");

    dev_info(&pdev->dev, "probed, irq=%d\n", m->irq);
    return 0;
}

static const struct of_device_id my_of_match[] = {
    { .compatible = "acme,mydev-v1" },
    { /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, my_of_match);

static struct platform_driver my_driver = {
    .probe  = my_probe,
    .remove_new = NULL,                  /* 全 devm 资源,可无 remove */
    .driver = { .name = "mydev", .of_match_table = my_of_match },
};
module_platform_driver(my_driver);       /* 一行替代 init/exit+注册 */
MODULE_LICENSE("GPL");
```
**逐段讲解**：
- devm 全家桶（kzalloc/ioremap/request_threaded_irq）：probe 失败任意一行 return，已申请资源自动释放——**没有 goto 清理链**（F-038）；
- IRQF_ONESHOT：线程执行期间中断保持屏蔽，防止同一事件上半部重复触发；
- IRQ_NONE 告知"非本设备中断"——共享中断不判断会引发 spurious disable；
- dev_err_probe 统一处理 -EPROBE_DEFER 打印（DEFER 不该当 error 打日志吓人）；
- module_platform_driver 宏把模块样板压到一行。
**知识点**：驱动-platform骨架

### F-050 ★★★（读代码答结果）
以下驱动代码在 64 位系统上被用户程序 `ioctl(fd, MYIOC_GET, &val)` 调用，val 是 `uint32_t`。命令定义 `#define MYIOC_GET _IOR('M', 1, uint64_t)`。会发生什么？

```c
static long my_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
{
    uint64_t tmp;
    switch (cmd) {
    case MYIOC_GET:
        tmp = get_value();
        if (copy_to_user((void __user *)arg, &tmp, _IOC_SIZE(cmd)))
            return -EFAULT;
        break;
    }
    return 0;
}
```

**答案**：内核会向用户只传了 `sizeof(uint32_t)=4` 字节的缓冲里拷 `sizeof(uint64_t)=8` 字节——**写越界 4 字节，踩坏用户栈/相邻变量**（本例恰好 copy_to_user 越界不报错，若目标页尾则 EFAULT）。
**解析**：
- 病根：用户侧命令宏与内核侧不一致（一侧 uint32_t 一侧 uint64_t），或用户复用了旧头文件；
- copy_to_user 的 size 来自 _IOC_SIZE(cmd)，cmd 是用户传入的——**命令字本身不可信**；健壮做法：内核 switch 用自己定义的常量匹配（本例已这样做，能拦下 cmd 不匹配），并校验 `_IOC_SIZE(cmd) == sizeof(期望类型)`；
- 教训：ioctl 命令定义必须唯一头文件源（内核与用户态共用同一 header），且升级命令结构体尺寸时必须改命令号（用 _IOR 重新编码，新旧命令并存）。
**知识点**：驱动-ioct越界

### F-051 ★★★（写代码 + 分析）
实现一个 sysfs 属性 `threshold`（可读写 uint32），写入时校验范围 1~1000，非法值返回错误。

**参考答案**：

```c
static u32 threshold = 100;

static ssize_t threshold_show(struct device *dev,
                              struct device_attribute *attr, char *buf)
{
    return scnprintf(buf, PAGE_SIZE, "%u\n", threshold); /* 一个文件一个值+换行 */
}

static ssize_t threshold_store(struct device *dev,
                               struct device_attribute *attr,
                               const char *buf, size_t count)
{
    u32 val;
    int ret = kstrtou32(buf, 0, &val);   /* 内核标准解析:自动处理进制/越界 */
    if (ret)
        return ret;                      /* 输入不是数字 */
    if (val < 1 || val > 1000)
        return -EINVAL;                  /* 业务校验 */
    threshold = val;
    return count;                        /* 成功必须返回 count! */
}

static DEVICE_ATTR_RW(threshold);        /* 生成 dev_attr_threshold */

/* probe 中: */
ret = device_create_file(&pdev->dev, &dev_attr_threshold);
/* remove 中: */
device_remove_file(&pdev->dev, &dev_attr_threshold);
```
**逐行讲解**：
- store 返回 count 表示"消费了全部输入"，否则 echo 报写错误；
- kstrtou32 替代手工 sscanf/atoi——内核已弃用 sscanf 于 sysfs 场景（安全+严格）；
- `echo 50 > /sys/.../threshold` 即热更新参数，`cat` 即查看——运维零成本；
- 多属性用 attribute_groups 一次性创建更整洁；
- 并发注意：threshold 若被中断/多进程同时读写，需 READ_ONCE/WRITE_ONCE 或锁（本例单 32 位读写在多数架构天然原子）。
**知识点**：驱动-sysfs实现

## 七、设计题（4 题）

### F-052 ★★（模块设计）
设计一个 GPIO 按键驱动的中断处理链（含消抖）：要求中断触发后 20ms 消抖，稳定后上报按键事件给用户空间。给出机制选型与代码骨架。

**参考设计**：
**机制选型**：硬中断（应答+启动定时器）→ 内核定时器 20ms 后确认电平 → workqueue/直接上报。用 `mod_timer` 而非中断里 msleep（中断不能睡）。

```c
static struct timer_list debounce_timer;
static int gpio;

static irqreturn_t key_isr(int irq, void *devid)
{
    /* 上半部:立刻防抖——20ms 内再触发由 timer 重新计时 */
    mod_timer(&debounce_timer, jiffies + msecs_to_jiffies(20));
    return IRQ_HANDLED;
}

static void debounce_fn(struct timer_list *t)
{
    int level = gpiod_get_value(gpiod);   /* 定时器上下文(软中断类,不可睡) */
    if (level == PRESSED_LEVEL) {
        pressed_time = jiffies;
        input_report_key(input_dev, KEY_1, 1);  /* input 子系统上报 */
        input_sync(input_dev);
    }
}
```
**要点**：
- mod_timer 每次抖动都把确认时刻后推 20ms——抖动期自动"续命"，无需计数；
- 定时器回调仍在软中断类上下文（不可睡），重活交给 input 子系统或 schedule_work；
- **更优的现代方案**：gpiolib 自带消抖（设备树 `debounce-interval`）或内核自带 keys GPIO 驱动（gpio-keys）——设计题加分点：先复用子系统，不重复造轮子；
- 用户空间经 /dev/input/eventX 标准接口读取，evtest 调试。
**知识点**：驱动-按键消抖设计

### F-053 ★★★（系统设计）
设计一个高速 ADC 采集驱动的数据通路：采样率 1MSPS、每样本 2 字节、需要把数据连续送给用户态处理程序。要求：CPU 占用低、不丢样本、用户态零拷贝。

**参考设计**：
**通路**：ADC 硬件 → DMA 环形缓冲（内核一致性内存）→ 中断（半满/满）→ 驱动把"整页数据就绪"通知用户态 → mmap 共享 → 用户态处理。

1. **DMA 环形缓冲**：dma_alloc_coherent 分配 N 块（如 4 块 × 64KB）一致性内存组成环（非 cache，无需流式同步）；DMA 循环搬运；
2. **中断设计**：每块搬运完成产生一次中断（DMA 半满/块满中断），上半部仅记录块索引并 wake_up/发 eventfd 级通知（1MB/s÷64KB ≈ 每 64ms 一次中断，负载可忽略）；
3. **用户态零拷贝**：驱动 mmap 用 dma_mmap_coherent 把环形缓冲映射到用户进程；用户态读到块索引（ioctl/sysfs 或 read 4 字节索引）后直接处理对应块；
4. **背压与丢帧策略**：用户态处理落后超过一圈时旧数据被 DMA 覆盖——驱动维护序号，用户态检测跳变即知道"丢了 k 块"，可上报统计而非静默使用脏数据；
5. **可选增强**：userfaultfd/DMABUF 交接、或直接用 UIO/VFIO 框架把设备交给用户态驱动（采集逻辑简单且要求极致时序时，UIO 让寄存器+中断都到用户态，内核侧几乎零代码）。
**设计要点提炼**：高吞吐三件套 = DMA 环 + 低频中断 + mmap 零拷贝；可靠性 = 序号检测丢帧，绝不假装没丢。
**知识点**：驱动-高速数据通路

### F-054 ★★★（系统设计）
为一个 SPI 传感器（带数据就绪中断）设计完整驱动分层：寄存器访问层、轮询/中断模式、缓冲、对用户暴露的接口（字符设备）。说明各层职责与关键代码路径。

**参考设计**：
**分层**：
1. **总线传输层**：封装 `spi_write/spi_read` 成 `reg_read/reg_write`（传感器多为"首字节寄存器地址 + 数据"协议）；高频访问可用 regmap-spi 框架（缓存寄存器、统一调试接口 `/sys/kernel/debug/regmap`）；
2. **数据采集层**：
   - 轮询模式：定时读（kernel timer/periodic work），适合无中断引脚的低成本设计；
   - 中断模式：data-ready IRQ（threaded IRQ，见 F-049）里读样本（SPI 事务可睡眠，正合线程下半部），写入 kfifo；
3. **缓冲层**：`kfifo`（内核无锁 SPSC 环形缓冲，sizeof 对齐_pow2）保存样本；溢出策略：覆盖旧样本 + 溢出计数（采集类设备通常"新数据更重要"）；
4. **用户接口层**：字符设备 read（阻塞/非阻塞 + poll，见 F-048）按样本结构体整数倍出队；sysfs 暴露 odr/量程配置（F-051）；ioctl 仅做不易文本化的操作（校准触发）；
5. **电源管理**：runtime PM（dev_pm_ops）在无消费者时令传感器待机。
**关键路径**：DRDY 中断 → thread_fn 读 SPI → kfifo_in → wake_up；用户 read → kfifo_out（空则 wait_event）。整套结构即 industrialio（IIO）子系统的骨架——加分答案：直接指出"产品优先用 IIO 框架 + iio_dma_buffer，上述分层 IIO 已标准化"。
**知识点**：驱动-传感器驱动分层

### F-055 ★★★（排查设计）
产品日志出现如下 oops。给出完整分析流程与结论方向。

```
Unable to handle kernel NULL pointer dereference at virtual address 00000010
pgd = c0004000, [00000010] *pgd=00000000
PC is at mydev_ioctl+0x44/0xd0
LR is at mydev_ioctl+0x30/0xd0
Call trace:
[<c0123f4c>] mydev_ioctl+0x44/0xd0 from [<c01a8b20>] do_vfs_ioctl+0x78/0x5a4
...
```

**参考分析流程**：
1. **读症状**：NULL 指针解引用于地址 0x10——典型"结构体指针为 NULL，访问其偏移 0x10 的成员"（ptr->member，ptr=NULL，member 偏移 16 字节）；
2. **定位代码**：`mydev_ioctl+0x44` → 同版本 vmlinux 用 objdump -d 反汇编 mydev_ioctl，找 +0x44 处指令（形如 `ldr r3, [rX, #0x10]`）；addr2line 得到源码行；确认哪个指针为 NULL；
3. **推断成因**（ioctl 常见 NULL 源）：①私有数据未赋值——probe 里忘了 `platform_set_drvdata`/`file->private_data`，或 open 时没做 `filp->private_data = ...`；②设备未 probe 成功但节点存在（defer 后用户已打开）；③用户 ioctl 传的结构里指针字段为 NULL，驱动未校验直接解引用；
4. **修复方向**：所有来自外部的指针（private_data、ioctl 参数内嵌指针）先判空；open 时校验设备就绪状态；probe 失败确保不暴露 /dev 节点；
5. **防复发**：开 CONFIG_DEBUG_INFO、oops 后 panic_on_oops=1（产品策略）+ kdump 保留 vmcore；code review 规则"任何 `->` 前的指针若来源不确定必须判空"。
**结论示范**：0x10 = NULL + 偏移，本例应最终定位到 `mydev_ioctl` 里解引用了未初始化的 private_data（比如 open 里漏了赋值，或模块重新加载后旧 fd 仍持有旧 fops）。
**知识点**：驱动-oops分析实战

---

**本批共 55 题（F-001 ~ F-055），累计已完成 335 / 600 题。**
题型分布：单选 22 / 多选 6 / 填空 5 / 判断 5 / 简答 7 / 编程 6 / 设计 4。
回复「继续」获取下一批【模块 G：通信协议（55 题）】——UART/SPI/I2C/CAN/USB 原理与时序、TCP/IP 协议栈、自定义协议设计（帧格式、CRC、粘包、重传）。
