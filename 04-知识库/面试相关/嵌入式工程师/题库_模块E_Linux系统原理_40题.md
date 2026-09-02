# 题库 · 模块 E：Linux 系统原理（共 40 题）

> **本模块知识点导图**
> - 进程管理：进程与线程、fork/vfork/exec、进程状态（R/S/D/Z/T）、僵尸/孤儿进程、wait/waitpid、进程组与会话、守护进程
> - 进程间通信（IPC）：匿名管道、命名管道（FIFO）、信号（signal）、System V 消息队列/信号量/共享内存、socket
> - 信号机制：常用信号语义、SIGKILL vs SIGTERM、信号处理函数的可重入安全、信号屏蔽
> - 文件 IO：open/read/write、文件描述符、文件偏移量、stdio 缓冲 vs 内核缓冲、dup/dup2、O_APPEND 原子性、inode 与软硬链接
> - 内存管理：虚拟内存与分页、进程内存布局、写时复制（COW）、mmap、malloc 底层（brk/mmap）
> - I/O 模型：阻塞/非阻塞、五种 I/O 模型、select/poll/epoll（水平/边缘触发）
> - 系统启动流程：BootROM → Bootloader（U-Boot）→ 内核 → init/systemd；嵌入式 Linux 启动链

---

## 一、单项选择题（16 题）

### E-001 ★
关于进程与线程，正确的说法是：
A. 线程是"轻量级进程"，与同进程其他线程共享地址空间、文件描述符表，但拥有独立的栈和寄存器上下文
B. 线程拥有独立的虚拟地址空间
C. 创建线程的开销一定比创建进程大
D. 同进程线程间通信必须使用管道

**答案：A**
**解析**：
- B 错：进程才有独立地址空间，线程共享；
- C 错：线程创建不需复制页表/fd 表（即使 COW 也有开销），更轻量；
- D 错：同进程线程共享全局变量即可通信，反而需要注意加锁。
**知识点**：Linux-进程与线程

### E-002 ★★
`fork()` 的返回值语义正确的是：
A. 子进程返回 0，父进程返回子进程 PID，失败返回 -1
B. 父进程返回 0，子进程返回父进程 PID
C. 父子进程都返回子进程 PID
D. 成功时父子进程返回值相同

**答案：A**
**解析**：一次调用两次返回——这是理解 fork 的钥匙。标准写法：

```c
pid_t pid = fork();
if (pid < 0)      { /* 失败 */ }
else if (pid == 0){ /* 子进程分支 */ }
else              { /* 父进程分支, pid 为子进程 PID */ }
```
子进程可通过 `getppid()` 获得父进程 PID（若父进程已退出则变为 1 或 systemd）。
**知识点**：Linux-fork

### E-003 ★★
僵尸进程（zombie）产生的原因是：
A. 子进程调用了 exit() 但父进程尚未调用 wait()/waitpid() 回收其退出状态
B. 父进程先于子进程退出
C. 子进程被 SIGKILL 杀死
D. 子进程发生段错误

**答案：A**
**解析**：
- 子进程退出后，内核保留其进程表项（PID、退出状态）供父进程查询；父进程不 wait，这个"已死但没销户"的条目就是僵尸。僵尸本身不占内存资源，但占用 PID；
- B 描述的是孤儿进程（由 init/systemd 收养并自动回收，不产生僵尸）；
- C/D 是子进程退出的方式，只要父进程 wait 了都不会成僵尸；
- 工程对策：① 父进程 waitpid(-1, NULL, WNOHANG) 轮询；② 注册 SIGCHLD 处理函数内 waitpid 循环；③ 两次 fork 让孙进程被 init 收养；④ signal(SIGCHLD, SIG_IGN) 显式忽略（内核自动回收，Linux 特性）。
**知识点**：Linux-僵尸进程

### E-004 ★★
进程状态 D（Uninterruptible Sleep）的含义与典型场景是：
A. 可中断睡眠，等待信号即可唤醒
B. 不可中断睡眠，通常等待磁盘 IO 或 NFS 完成，此时连 SIGKILL 都无法立即生效
C. 进程已被暂停（收到 SIGSTOP）
D. 僵尸状态

**答案：B**
**解析**：
- S（可中断睡眠）：等待事件/信号，可被信号唤醒；
- D（不可中断睡眠）：内核态关键路径（如磁盘/NFS IO、驱动等待），不接受信号处理——避免 IO 半途而废；长时间 D 状态通常指向**存储/驱动层故障**（top 里常见 D 状态堆积 = IO hang）；
- T：暂停（SIGSTOP/SIGTSTP）；Z：僵尸。
**知识点**：Linux-进程状态

### E-005 ★
关于匿名管道（pipe），正确的说法是：
A. 匿名管道可用于任意两个无亲缘关系的进程间通信
B. 匿名管道是半双工的，一端读一端写，只用于有亲缘关系（父子/兄弟）进程间通信
C. 管道内数据按随机顺序读取
D. 管道容量无限

**答案：B**
**解析**：
- A 错：匿名管道无名字、靠继承 fd 存在，无法被无关进程打开（跨任意进程需 FIFO 或 socket）；
- B 对：半双工 + 继承性两个特征同时考到；
- C 错：管道是 FIFO 字节流；
- D 错：默认容量 64KB（`fcntl(F_SETPIPE_SZ)` 可调，/proc/sys/fs/pipe-max-size）。管道写满后 write 阻塞，读端全部关闭后 write 触发 SIGPIPE（经典崩溃点：网络程序必须忽略或处理 SIGPIPE）。
**知识点**：Linux-管道

### E-006 ★★
`ls -l` 显示某文件权限为 `lrwxrwxrwx`，开头的 `l` 表示：
A. 普通文件
B. 目录
C. 符号链接（软链接）
D. 块设备

**答案：C**
**解析**：
- 软链接（`ln -s`）：独立 inode，存的是目标路径字符串，可跨文件系统、可指向目录，删源后变"悬空链接"；
- 硬链接（`ln`）：与源文件同一 inode（链接计数+1），不可跨文件系统、不可指向目录，删源文件仍可访问（直到链接数为 0）。
**知识点**：Linux-软硬链接

### E-007 ★★
stdio 库（printf/fwrite）与系统调用（write）的缓冲关系，正确的说法是：
A. printf 直接写入硬件，无任何缓冲
B. printf 经过用户态缓冲（行缓冲/全缓冲），flush 时才调用 write 进入内核页缓存，内核再有磁盘缓冲
C. write 系统调用保证数据立即落盘
D. 两级缓冲指的是用户态缓冲和 CPU 缓存

**答案：B**
**解析**：
- 完整链路：`printf → stdio 用户态缓冲 → write() → 内核 page cache → fsync() → 磁盘`；
- 终端设备为**行缓冲**（遇 \n 刷新），重定向到文件/管道变为**全缓冲**（4KB~8KB 才刷）——这就是"fork 前 printf 内容重复输出"问题的根源；
- C 错：write 只到 page cache，落盘需 fsync/fdatasync；
- D 错：三级缓冲是 stdio 缓冲 + 内核 page cache + 磁盘/驱动缓存。
**知识点**：Linux-IO缓冲链

### E-008 ★★
多个进程以 `O_APPEND` 标志打开同一文件并发写入，正确的说法是：
A. 仍可能互相覆盖，O_APPEND 没有作用
B. 每次写操作将偏移量原子地移到文件末尾再写入，保证并发追加不互相覆盖
C. O_APPEND 只对读操作有意义
D. 只有文件系统加锁后才安全

**答案：B**
**解析**："移动偏移量 + 写入"被内核合并为一次原子操作。若不用 O_APPEND，先 lseek 再 write 是两步，多进程间会发生"都 seek 到同一位置再各自写"的覆盖。多进程日志追加的标准姿势就是 `open(..., O_WRONLY | O_APPEND | O_CREAT, 0644)`。注意：O_APPEND 原子性针对"偏移+写"，单条 write 大于 PIPE_BUF/相关限制时仍可能交错（文件写入通常仍保持 write 级原子性，但严谨场景需记录级加锁）。
**知识点**：Linux-O_APPEND原子性

### E-009 ★★
写时复制（Copy-On-Write）在 fork 中的作用是：
A. fork 时立即完整复制父进程物理内存
B. fork 后父子进程共享物理页并标记只读，任一方写入时触发缺页异常，内核才真正复制该页
C. 让子进程只读不能写
D. 复制文件系统缓存

**答案：B**
**解析**：
- fork 后子进程复制的是页表（虚拟→物理映射），物理页共享且标记 RO；父子任一写 → page fault → 内核分配新页复制内容 → 写进程映射新页。多数页面从未被写（典型"读多写少"的 fork+exec 场景），COW 让 fork 代价从"复制 GB 级内存"降为"复制页表"；
- 关联考点：pthread 线程的栈同样在写共享变量时才产生页复制错误吗？不——线程间本来就共享可写页，COW 只发生在 fork 语义下。
**知识点**：Linux-写时复制

### E-010 ★★
glibc 的 malloc 分配大块内存（如 >128KB）时通常采用的手段是：
A. 始终使用 brk() 扩展堆
B. 使用 mmap() 直接映射匿名内存（释放时归还系统）
C. 使用 fork() 
D. 直接调用 write()

**答案：B**
**解析**：
- 小块（<128KB，M_MMAP_THRESHOLD 默认值）：brk() 在堆顶伸缩，配合 ptmalloc 的 bins 复用——快，但 free 后内存留在进程池，**top of heap 不缩**则 RSS 不降（这是"free 了 top 也不降"的经典面试题）；
- 大块：mmap 匿名映射，free 时 munmap 立刻归还内核，RSS 立降——无碎片问题但每次 mmap 有缺页开销；
- 嵌入式关联：内存紧张设备上要意识到大量小块 free 后 RSS 不下降（内存池/碎片问题），必要时 mallopt 调阈值或直接用 mmap。
**知识点**：Linux-malloc原理

### E-011 ★★
下列信号中，进程**不能**捕获、阻塞或忽略的是：
A. SIGTERM
B. SIGKILL 和 SIGSTOP
C. SIGINT
D. SIGSEGV

**答案：B**
**解析**：
- SIGKILL（9）/SIGSTOP（19）由内核直接处理，留给系统最后控制权；
- SIGTERM（15）可捕获，是"礼貌终止"——进程可做清理后退出；`kill -9` 是"立即枪毙"——资源清理代码（刷缓冲、删临时文件、释放锁）不会执行，生产系统应先 SIGTERM、宽限后 SIGKILL；
- SIGSEGV 可注册 handler（如打印 backtrace），但 handler 内再触发 SIGSEGV 则死循环。
**知识点**：Linux-信号语义

### E-012 ★★
关于在信号处理函数中调用函数，安全的做法是：
A. 随便调用，与普通函数无区别
B. 只能调用可重入（async-signal-safe）函数，如 write()；printf/malloc/free 等不可重入函数有风险
C. 只能调用 static 函数
D. 不能调用任何函数

**答案：B**
**解析**：
- 场景：主程序正在 malloc（持有堆锁）时信号到来，handler 里再 malloc → 死锁/堆损坏。`man 7 signal-safety` 列出安全白名单（write/read/_exit 等）；
- 标准模式：handler 里只置 `volatile sig_atomic_t` 标志（或 write 一个字节到 self-pipe/eventfd），主循环检查标志后做复杂处理；
- volatile 保证不被优化缓存，sig_atomic_t 保证读写原子。
**知识点**：Linux-信号安全

### E-013 ★★
`mmap()` 文件映射后修改内存，正确的说法是：
A. 修改立刻直接写入磁盘
B. 修改作用于内核 page cache，由内核按策略（或 msync）刷盘，省去 read/write 的用户态↔内核态拷贝
C. mmap 的内存不占用进程地址空间
D. mmap 只能映射可执行文件

**答案：B**
**解析**：
- mmap 共享映射（MAP_SHARED）：CPU 直接读写 page cache（缺页时按需从磁盘调入），无 read/write 的两次拷贝；落盘依赖内核回写或显式 msync；
- MAP_PRIVATE：写时复制到私有页，不影响原文件；
- C 错：映射区占地址空间（文件大→VMA 多，32 位嵌入式设备注意地址空间耗尽）；
- 典型嵌入式用途：大配置文件/字库访问、进程间共享内存（匿名 MAP_SHARED|MAP_ANONYMOUS）、寄存器映射（配合 /dev/mem）。
**知识点**：Linux-mmap

### E-014 ★★
select 相比 epoll 的本质劣势是：
A. select 不能监听网络 socket
B. select 每次调用都需在用户态与内核态之间来回拷贝整个 fd 集合，且返回后需遍历所有 fd 找就绪者；epoll 在内核维护红黑树+就绪链表，只需拷贝就绪列表
C. select 只能用于读事件
D. select 没有超时机制

**答案：B**
**解析**：
- select：FD_SETSIZE 上限 1024（可改但麻烦）、O(n) 拷贝 + O(n) 遍历，fd 越多越慢；
- poll：无 1024 限制但仍 O(n)；
- epoll：epoll_ctl 增删改一次性注册（红黑树），事件就绪回调挂入就绪链表，epoll_wait 只返回就绪 fd，O(1) 拷贝级开销——C10K 问题的正解；
- 关联：epoll LT（水平触发，不读会反复通知）vs ET（边缘触发，只通知一次，必须一次性读到 EAGAIN，且配非阻塞 fd）。
**知识点**：Linux-IO多路复用

### E-015 ★★
嵌入式 Linux 系统启动的正确顺序是：
A. 内核 → Bootloader → init 进程 → 应用
B. BootROM → Bootloader（如 U-Boot）→ 内核（含挂载根文件系统）→ init/systemd（PID 1）→ 应用程序
C. init → 内核 → Bootloader
D. Bootloader → init → 内核

**答案：B**
**解析**：完整链条：SoC 上电 → BootROM（片内固化代码，从 eMMC/SD/NAND/UART/XIP 加载一级代码）→ SPL/BL2 → U-Boot（初始化 DDR、加载内核+设备树到内存、bootargs、bootz）→ 内核解压启动（head.S → start_kernel → 挂载 rootfs）→ 执行第一个用户态进程 init/systemd（PID 1）→ 按 runlevel/服务拉起应用。嵌入式产品常用 BusyBox init（/etc/inittab）或 systemd；init 死亡 = 内核 panic，PID 1 不可被杀死（即使 SIGKILL）。
**知识点**：Linux-启动流程

### E-016 ★★★
某守护进程文件描述符泄漏（每分钟泄漏 3 个 fd），系统最终的表现与原因最可能是：
A. 进程内存耗尽崩溃
B. fd 编号持续增长，触及进程 RLIMIT_NOFILE 上限后 open/socket 返回 EMFILE，业务新连接/文件操作全部失败；系统级则可能耗尽 file table
C. 磁盘写满
D. CPU 占用 100%

**答案：B**
**解析**：
- fd 是有限资源：每进程默认软限制常为 1024（`ulimit -n`，可用 setrlimit/系统配置调高），系统级总量受 `fs.file-max` 与内存限制；
- 泄漏初期无感，达到上限后所有 open()/socket()/accept() 返回 -1 且 errno=EMFILE——"运行几天后无法建立新连接"的经典病因；
- 定位手段：`ls /proc/<pid>/fd | wc -l` 监控 fd 数曲线；`lsof -p <pid>` 看泄漏 fd 的类型（socket 还是文件）；
- 嵌入式注意：RAM 小 → fs.file-max 天然小，泄漏爆发更早。
**知识点**：Linux-文件描述符与资源限制

## 二、多项选择题（5 题）

### E-017 ★★
进程退出时（正常 return 或 exit()），内核/运行库自动完成的清理包括：
A. 刷新并关闭 stdio 缓冲流（exit 会；_exit 不会）
B. 执行 atexit() 注册的函数（exit 会；_exit 不会）
C. 关闭所有打开的文件描述符
D. 释放进程地址空间、销毁页表
E. 解除持有的 flock 文件锁与 System V 信号量（避免死锁其他进程）

**答案：A、B、C、D、E**
**解析**：
- exit()（库函数）：调 atexit 处理器 + 刷 stdio → 再进 _exit()；_exit()（系统调用）：直接进内核；
- 内核侧：关全部 fd（自动解锁 flock）、回收地址空间与页表、向父进程发 SIGCHLD、保留退出状态成僵尸待 wait；
- E 是高级考点：进程死亡时 flock 与 POSIX 信号量自动释放，但 **System V 信号量不会自动释放**（semctl SEM_UNDO 可解）——持有者崩溃后其他等待进程可能永远阻塞。
**知识点**：Linux-进程退出语义

### E-018 ★★
下列哪些属于 Linux 进程间通信（IPC）方式？
A. 匿名管道与命名管道（FIFO）
B. Unix 域套接字（Unix Domain Socket）
C. 信号（signal）
D. 共享内存（shm/mmap MAP_SHARED）
E. 临时文件 + 轮询

**答案：A、B、C、D、E**
**解析**：
- A~D 是标准 IPC；E（文件 + 轮询/inotify）在工程中真实可用（配置热加载、简单数据交换），但效率最低、无原子性保证，属于"能用不推荐"；
- 全家福速记：**pipe、FIFO、signal、msgqueue、sem、shm、socket、eventfd**；
- 性能排序（同机大数据量）：共享内存 > Unix 域套接字 ≈ 管道 > 消息队列 > 信号/临时文件。
**知识点**：Linux-IPC分类

### E-019 ★★
关于共享内存（System V shm 或 mmap MAP_SHARED）IPC，正确的说法有：
A. 它是最快的 IPC 方方式，因为数据零拷贝、不经过内核转发
B. 共享内存自身不带同步机制，必须配合信号量/互斥锁/原子操作
C. 进程崩溃后共享内存（System V，已 shmat 过）可能残留，需 ipcrm 清理或用 IPC_RMID 标记
D. 两进程映射同一文件到 MAP_SHARED 也能达到共享内存效果
E. 多进程互斥可以用 pthread_mutex 初始化为 PTHREAD_PROCESS_SHARED 并放共享内存中

**答案：A、B、C、D、E**
**解析**：
- A：其他 IPC 都有"内核中转拷贝"，共享内存直接读写同一物理页；
- B：内核不会替你同步——并发写没有保护就是数据竞争，这是共享内存的头号陷阱；
- C：System V 对象生命周期随内核而非进程，`ipcs -m` 可见残留（nattch=0）；
- D：文件映射共享是更现代的等价做法（可持久化）；
- E：**进程间互斥锁**——放在共享内存的 pthread mutex，attr 设 PTHREAD_PROCESS_SHARED，多进程可直接互斥；还可加 PTHREAD_MUTEX_ROBUST 使持有者死亡时锁可恢复（防止持锁进程崩溃导致永久死锁）。
**知识点**：Linux-共享内存

### E-020 ★★
`ps` 中 STAT 列的可能取值与含义，下列对应正确的有：
A. R — 正在运行或就绪
B. S — 可中断睡眠（等待事件/信号）
C. D — 不可中断睡眠（通常 IO）
D. T — 已停止（暂停）
E. Z — 僵尸（已退出未被回收）

**答案：A、B、C、D、E**
**解析**：全部正确。附加记法：STAT 还可带后缀——`+`（前台进程组）、`s`（会话首进程）、`l`（多线程）、`<`（高优先级）、`N`（低优先级），如 `Ss+`、`Rl+`。排查思路：CPU 高找 R 堆积；IO 卡找 D 堆积；PID 不释放找 Z 堆积。
**知识点**：Linux-进程状态

### E-021 ★★★
进程地址空间从低到高的典型布局（32 位 Linux），下列说法正确的有：
A. .text（代码段）在最下方，只读
B. .data（已初始化全局/静态）与 .bss（未初始化全局/静态）相邻，.bss 不占文件体积
C. 堆（heap）从低向高增长（brk 方向），与 .bss 相邻
D. mmap 区（共享库、匿名映射）位于堆与栈之间，向下/向上增长依平台而异
E. 栈（stack）在最高地址附近，向下增长，受 RLIMIT_STACK 保护

**答案：A、B、C、D、E**
**解析**：
- 全对。经典布局：`.text → .rodata → .data → .bss → [heap ↑] → …mmap 区… → [stack ↓] → 内核空间`；
- B 的"bss 不占文件体积"是高频考点：未初始化变量只在 ELF 头记录大小，加载时内核清零映射（Anonymous zero-fill）；
- `size a.out` 可查看 text/data/bss 三段体积；栈默认限制常为 8MB（ulimit -s），线程栈由 pthread_attr_setstacksize 指定；
- 与嵌入式关联：MCU 上 .data 从 Flash 拷到 RAM、.bss 清零是启动代码干的同一件事，概念完全对应。
**知识点**：Linux-内存布局

## 三、填空题（4 题）

### E-022 ★
`kill -9` 发送的信号名是______，它不能被捕获或忽略。

**答案**：SIGKILL
**解析**：编号 9。对应 `kill -15`（SIGTERM，礼貌终止可捕获）。`kill -l` 查看全部信号。
**知识点**：Linux-信号

### E-023 ★★
子进程退出后，父进程通过系统调用______（或其变体 waitpid）获取子进程退出状态并回收僵尸。

**答案**：wait
**解析**：waitpid(-1, &status, 0) 阻塞等任意子进程；WNOHANG 非阻塞轮询；WEXITSTATUS(status) 取退出码（需先用 WIFEXITED 判断）。
**知识点**：Linux-进程回收

### E-024 ★★
`open()` 返回的整数称为______，它是进程级 fd 表的下标，0、1、2 默认对应标准输入、标准输出、标准错误。

**答案**：文件描述符（file descriptor）
**解析**：fd 是"进程 fd 表 → 系统级打开文件表（含当前偏移量）→ inode"三级结构的第一级。dup 复制的是 fd 表项（共享同一偏移量）；父子进程 fork 后共享同一打开文件表项——这也是管道跨进程的基础。
**知识点**：Linux-文件描述符

### E-025 ★★
两次调用 `write(fd, buf, 1)` 向管道写入 2 字节后，另一个进程一次 `read(fd, rbuf, 100)` 最多能读到的是______字节（管道读操作一次性取走当前可用数据）。

**答案**：2（所有已写入且未被读走的数据）
**解析**：管道/流式 socket 的 read 是"取当前可用，最多 count 字节"，没有消息边界——这就是**粘包**问题的内核根源；要恢复消息边界必须应用层定界（长度前缀/分隔符）。对比：消息队列与数据报（UDP/socket SEQPACKET）天然保边界。
**知识点**：Linux-流式读取与粘包

## 四、判断题（5 题）

### E-026 ★
vfork() 保证子进程先运行，且子进程必须立即调用 exec() 或 _exit()，不许写任何变量（写结果是未定义）。（ ）

**答案：对**
**解析**：vfork 不复制页表，子进程直接借用父进程地址空间运行，写变量等于改父进程内存。现代 Linux 上 fork 已有 COW，vfork 的性能收益仅在 exec 立即发生的场景，且逐渐被 posix_spawn 取代，但语义本身如题所述。
**知识点**：Linux-vfork

### E-027 ★★
`fork()` 之后，父进程里 stdio 缓冲区中尚未刷新的内容会被复制到子进程，导致重定向到文件时输出重复。（ ）

**答案：对**
**解析**：stdio 缓冲区在用户态内存中，fork 时被完整复制。终端下行缓冲（遇 \n 刷）无感；**重定向到文件变全缓冲**，父进程未刷的缓冲被父子各刷一次 → 内容重复两次。修复：fork 前 fflush(stdout) 或 setvbuf 无缓冲。这是 APUE 的经典实验，嵌入式日志模块（fork 守护进程）必须处理。
**知识点**：Linux-fork与stdio缓冲

### E-028 ★★
两个进程分别以 `open()` 打开同一文件（各自 open，非 fork 继承），它们共享同一个文件偏移量。（ ）

**答案：错**
**解析**：文件偏移量存于"系统级打开文件表项"中。fork/dup 共享表项 → 共享偏移；各自独立 open → 各有独立表项 → 各有独立偏移，互相 seek 不影响（并发写在中间区域会互相覆盖，O_APPEND 才保证追加原子性）。
**知识点**：Linux-文件偏移量

### E-029 ★★
`read()` 返回值小于请求字节数（但大于 0）表示出错。（ ）

**答案：错**
**解析**：read 返回 >0 的任意值都合法（信号打断后已读部分、终端行输入、管道当前只有这么多数据、到达 EOF 前的短读）；返回 0 表示 EOF；返回 -1 且 errno==EINTR 表示被信号打断应重试，其他 errno 才是错误。**循环读满**是文件 IO 的标准写法：

```c
ssize_t readn(int fd, void *buf, size_t n) {
    size_t left = n; char *p = buf;
    while (left > 0) {
        ssize_t r = read(fd, p, left);
        if (r < 0) { if (errno == EINTR) continue; return -1; }
        if (r == 0) break;          /* EOF */
        left -= r; p += r;
    }
    return n - left;
}
```
**知识点**：Linux-短读处理

### E-030 ★★
一个进程可以修改自己的 /proc/<pid>/maps 所描述的映射权限。（ ）

**答案：错（作为判断题：该说法不成立）**
**解析**：/proc/<pid>/maps 是**只读**的内核视角映射信息，用于排查地址空间布局（哪个 so 映射在哪、栈/堆范围、权限）。修改映射要用 mprotect/mmap 本身；排查内存踩踏时 maps 的价值在于：把崩溃地址对照 maps 找出"落在哪个区间"——so 基址 + 偏移即可定位是哪个库哪一段。
**知识点**：Linux-/proc与内存排查

## 五、简答题（5 题）

### E-031 ★★
对比五种 IPC 方式（管道、消息队列、共享内存、信号、Unix 域套接字）的适用场景。

**参考答案**：
| 方式 | 特点 | 适用 |
|------|------|------|
| 匿名管道 | 半双工字节流、亲缘进程、简单 | 父子进程命令流（shell 管道） |
| 消息队列 | 有消息边界、带类型可优先收取 | 小消息、多生产者（System V/POSIX） |
| 共享内存 | 零拷贝最快、需自配同步 | 大数据量高频交换（视频帧、遥测流） |
| 信号 | 异步事件通知、传递信息极少 | 事件触发（SIGCHLD/SIGUSR1 热重载） |
| Unix 域套接字 | 全双工、有 SOCK_STREAM/SEQPACKET、可传 fd | 本地服务化进程（守护进程与 CLI 通信、传 fd 是杀手锏） |
**选型原则**：量小用消息/管道；量大用共享内存+信号量；跨网络必须 socket；本地服务化首选 Unix 域套接字。
**知识点**：Linux-IPC选型

### E-032 ★★
简述孤儿进程与僵尸进程的区别，以及各自的系统级处理机制。

**参考答案**：
- **孤儿**：父进程先退出，子进程还在运行。机制：子进程被 init/systemd（PID 1）收养；孤儿退出时由收养者 wait 自动回收 → 无害；
- **僵尸**：子进程先退出，父进程活着但不 wait。机制：子进程保留 PID+退出状态（其余资源已释放），父进程不 wait 则僵尸永存 → 占 PID 资源，大量僵尸可耗尽 PID；
- **僵尸的四种消除法**：① 父进程 waitpid；② 父进程 signal(SIGCHLD, SIG_IGN)（Linux 内核自动回收）；③ SIGCHLD handler 中循环 `while (waitpid(-1, NULL, WNOHANG) > 0);`；④ 父进程自身退出，僵尸被 init 收养回收。
- **PID 1 特殊性**：init 的子进程即使退出也不会成僵尸？不——init 会立即 wait，等效于方案②的实现。
**知识点**：Linux-孤儿与僵尸

### E-033 ★★★
解释"五种 I/O 模型"（阻塞、非阻塞、多路复用、信号驱动、异步），并说明 epoll 属于哪一种、ET/LT 的区别。

**参考答案**：
1. **阻塞 I/O**：read 无数据则进程睡眠等数据+拷贝全程；
2. **非阻塞 I/O**：无数据立即返回 EAGAIN，需轮询（忙等浪费 CPU）；
3. **I/O 多路复用**：select/poll/epoll 一个线程同时守多个 fd，就绪才去 read（read 本身仍可能短阻塞在拷贝）；**epoll 属于此类**；
4. **信号驱动**：内核数据就绪发 SIGIO，进程在 handler 中读（少用）；
5. **异步 I/O（AIO/io_uring）**：内核完成"等待+拷贝"全程再通知，连拷贝阶段都不占进程；
- **LT 水平触发**：缓冲区还有数据就一直通知，天然防丢、编程简单（没读完下次还提醒）；
- **ET 边缘触发**：状态变化只通知一次，必须循环读到返回 EAGAIN，且 fd 必须非阻塞，否则最后一次 read 永远阻塞。ET 减少 epoll_wait 唤醒次数，高性能服务器（nginx）标配，但编程易错。
**知识点**：Linux-IO模型

### E-034 ★★
简述 Linux 中断处理的"上半部/下半部"思想，以及 softirq/tasklet/workqueue 三种下半部机制的区别。

**参考答案**：
- **思想**：上半部（硬中断）关中断、抢时间，只做"应答硬件 + 标记数据到达"；耗时工作推迟到下半部（开中断环境）执行，保证中断延迟可控；
- **softirq**：静态定义（网络/块设备核心路径），可多 CPU 并发同类型执行，性能最高；
- **tasklet**：动态注册、基于 softirq 实现，同一 tasklet 不会在多核同时执行（同类型串行），驱动常用；
- **workqueue**：推到**内核线程**（kworker）执行，**允许睡眠**——需要睡眠/大量内存分配的延后工作用它；
- **选型口诀**：不能睡眠 → tasklet；要睡眠 → workqueue；极致吞吐的子系统级 → softirq。对应 RTOS 语境：ISR 里只发信号量、任务里干活的分层思想完全一致。
**知识点**：Linux-中断上下半部

### E-035 ★★
简述嵌入式 Linux 从上电到应用程序运行的完整启动流程（以 U-Boot 为例），并说明每步传递的关键信息。

**参考答案**：
1. **BootROM**（片内固化）：初始化极小环境，按启动引脚从 eMMC/NAND/SD/UART/USB 加载二级镜像（SPL）；
2. **SPL/BL2**：初始化 DDR，加载 U-Boot 主体到 RAM；
3. **U-Boot**：初始化外设（网口/Flash/串口）、加载**内核镜像 + 设备树（DTB）**到内存、设置 **bootargs**（root= 挂载哪个设备、console=ttyS0 串口、init= 第一个用户进程、mem= 等），`bootz`/`bootm` 跳转内核；
4. **内核**：解压自举 → 架构初始化 → 解析设备树注册平台设备 → 挂载根文件系统（rootfs，常见 SquashFS 只读 + OverlayFS 可写层）→ 启动 PID 1；
5. **init/systemd**：BusyBox init 读 /etc/inittab（嵌入式）或 systemd 按 target 启服务，最终拉起应用程序（后台守护进程 + 看门狗）。
- **关键传递**：bootargs 是 U-Boot→内核的唯一参数通道；设备树是内核感知硬件的描述（取代板级 file）；根文件系统提供用户态世界。
**知识点**：Linux-嵌入式启动链

## 六、编程题（4 题）

### E-036 ★★（找错）
以下代码意图：父进程通过管道向子进程发一条消息。找出所有错误：

```c
int fd[2];
pipe(fd);
pid_t pid = fork();
if (pid == 0) {                       /* 子进程 */
    char buf[64];
    read(fd[1], buf, sizeof(buf));    /* 想收消息 */
    printf("child got: %s\n", buf);
    exit(0);
} else {                              /* 父进程 */
    write(fd[0], "hello", 6);         /* 想发消息 */
    wait(NULL);
}
```

**答案**：
错误 1：**读写了反向的 fd**——`fd[0]` 是读端、`fd[1]` 是写端。子进程应 `read(fd[0], …)`，父进程应 `write(fd[1], …)`；
错误 2：**未关闭不用的端口**——正确姿势是子进程 close(fd[1])、父进程 close(fd[0])。不关写端会导致子进程 read 永远无法感知 EOF（父进程退出后仍有子进程自己持有的写端）；不关读端则父进程写满管道后若子进程死掉，write 收不到 SIGPIPE 判断依据混乱；
错误 3：**read 未处理返回值**——应检查返回的字节数、处理 EINTR，且 buf 末尾补 '\0' 再 printf（write 只发了 6 字节含 '\0' 尚可，但规范上应显式处理）；
修正版：

```c
int fd[2];
pipe(fd);
pid_t pid = fork();
if (pid == 0) {
    close(fd[1]);                          /* 子进程只读 */
    char buf[64];
    ssize_t n;
    while ((n = read(fd[0], buf, sizeof(buf) - 1)) > 0) {
        buf[n] = '\0';
        printf("child got: %s\n", buf);
    }
    close(fd[0]);
    exit(0);
} else {
    close(fd[0]);                          /* 父进程只写 */
    write(fd[1], "hello", 6);
    close(fd[1]);                          /* 关写端 → 子进程 read 返回 0 退出 */
    wait(NULL);
}
```
**知识点**：Linux-管道编程

### E-037 ★★★（读代码答结果）
以下程序（重定向到文件运行：`./a.out > out.txt`）的输出是什么？为什么？

```c
#include <stdio.h>
#include <unistd.h>

int main(void)
{
    printf("A");               /* 无换行 */
    pid_t pid = fork();
    if (pid == 0) {
        printf("B");
        _exit(0);
    } else {
        wait(NULL);
        printf("C\n");
    }
    return 0;
}
```

**答案**：out.txt 内容为 `AABC\n`（A 出现两次）。
**解析**：
1. 重定向到文件 → stdout 全缓冲（4KB），`printf("A")` 只写入缓冲区未刷新；
2. fork 复制了含"A"的用户态缓冲区 → 父子各有一份；
3. 子进程 `printf("B")` 后 `_exit(0)`——**_exit 不刷新 stdio 缓冲**，"B"丢失！（若换成 exit(0) 则子进程刷出 "AB"，总输出 "ABAC"）；
4. 父进程打印 "C\n"，遇换行……注意全缓冲模式下 \n 不一定触发刷新，但 return main → exit() → 刷缓冲，输出 "A" + "C\n"；
5. 合计：父进程刷出 "A"+"C\n"，子进程若用 exit 则另有 "AB"。本例 `_exit` 版本 = `A A C`，即 "A"重复一次、"B"丢失——**一题同时考了 fork 缓冲复制与 _exit 不刷缓冲两个点**。
**知识点**：Linux-fork缓冲复制+_exit

### E-038 ★★★（写代码）
实现一个健壮的守护进程化函数 `daemonize()`：脱离终端、成为会话首进程、重定向标准流、防止重复运行（单实例锁）。

**参考答案**：

```c
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>

#define PID_LOCK_FILE "/var/run/myapp.pid"

int daemonize(void)
{
    /* 1.单实例锁:O_CREAT|O_EXCL 独占创建,防止双开 */
    int lockfd = open(PID_LOCK_FILE, O_RDWR | O_CREAT | O_EXCL, 0644);
    if (lockfd < 0) {
        fprintf(stderr, "another instance running?\n");
        return -1;
    }
    char pid[16];
    snprintf(pid, sizeof(pid), "%d\n", getpid());
    write(lockfd, pid, strlen(pid));          /* 记录 PID 便于运维 kill */

    /* 2.fork 并让父进程退出,子进程脱离原会话 */
    pid_t pid2 = fork();
    if (pid2 < 0)  return -1;
    if (pid2 > 0)  _exit(0);                  /* 父进程退出(不用 exit 防重复刷缓冲) */

    /* 3.创建新会话:setsid 使进程成为新会话首+组长,脱离控制终端 */
    if (setsid() < 0) return -1;

    /* 4.再次 fork(可选但推荐):确保进程永不重新获得控制终端 */
    pid_t pid3 = fork();
    if (pid3 < 0)  return -1;
    if (pid3 > 0)  _exit(0);

    /* 5.重置文件创建掩码,避免继承的 umask 影响日志权限 */
    umask(0);

    /* 6.切换工作目录到 /,防止占用可卸载文件系统 */
    chdir("/");

    /* 7.关闭/重定向 0,1,2 到 /dev/null:
       防止误用 stdio 写到已关闭 fd,以及误读终端 */
    int devnull = open("/dev/null", O_RDWR);
    if (devnull >= 0) {
        dup2(devnull, STDIN_FILENO);
        dup2(devnull, STDOUT_FILENO);
        dup2(devnull, STDERR_FILENO);
        if (devnull > STDERR_FILENO) close(devnull);
    }

    /* 8.忽略终端相关信号(SIGHUP 由会话首进程语义决定) */
    signal(SIGHUP, SIG_IGN);
    return 0;
}
```
**逐段讲解**：
- 单实例锁放在最前，双开时第二个进程立刻退出且不产生半初始化副作用；崩溃后残留 PID 文件需启动时检测 PID 是否存活（kill(pid,0) 探测）后清理；
- setsid 前必须先 fork：进程组长调用 setsid 会失败；
- 第二次 fork 防"将来误开终端设备重新成为控制进程"（经典双 fork 守护进程范式）；
- 重定向 stdio 而非只 close：fd 0/1/2 留空时后续 open 会复用这些编号，第三方库往 stderr 打日志会写坏业务文件——**这是嵌入式产品经典事故**；
- 现代简化：直接 `daemon(0, 0)` 或 systemd 前台运行（推荐，让 systemd 管生命周期与自动重启），但面试要求手写时按上例。
**知识点**：Linux-守护进程

### E-039 ★★★（写代码）
实现带信号安全的周期任务框架：主循环每 1 秒执行一次 `do_job()`，收到 SIGTERM/SIGINT 时优雅退出（完成当次循环、打印退出日志）；收到 SIGUSR1 时置位"立即重载配置"标志。

**参考答案**：

```c
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <time.h>

static volatile sig_atomic_t g_exit   = 0;   /* 退出请求 */
static volatile sig_atomic_t g_reload = 0;   /* 重载请求 */

static void sig_handler(int signo)
{
    /* handler 内只置原子标志——async-signal-safe */
    if (signo == SIGTERM || signo == SIGINT) g_exit = 1;
    else if (signo == SIGUSR1)               g_reload = 1;
}

int main(void)
{
    struct sigaction sa;
    sa.sa_handler = sig_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;                    /* 不用 SA_RESTART,让慢调用被打断 */
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT,  &sa, NULL);
    sigaction(SIGUSR1, &sa, NULL);

    struct timespec ts = {1, 0};        /* 1s 周期 */
    while (!g_exit) {
        do_job();
        if (g_reload) {                 /* 主循环统一处理重载 */
            reload_config();
            g_reload = 0;
        }
        /* nanosleep 被信号打断时继续睡完剩余时间 */
        while (nanosleep(&ts, &ts) < 0 && errno == EINTR) {
            if (g_exit) break;          /* 退出信号则不再补睡 */
        }
    }
    printf("graceful exit\n");
    return 0;
}
```
**逐行讲解**：
- `volatile sig_atomic_t`：volatile 防优化缓存，sig_atomic_t 保证单步读写原子——信号标志的唯二正确类型组合；
- handler 内只置标志，printf/malloc 等全部放主循环——E-012 原则的落地；
- nanosleep 剩余时间参数（第二个 &ts）+ EINTR 循环：信号打断睡眠后**继续睡剩余部分**，周期不漂移；被退出信号打断则立即跳出（响应性与周期性的平衡）；
- sa_flags 不设 SA_RESTART：让阻塞的系统调用被信号打断返回（否则 sleep 打断后自动重启，退出响应变慢）。若业务需要自动重启其他调用，可单独对无关信号设 SA_RESTART。
**知识点**：Linux-信号处理框架

## 七、设计题（1 题）

### E-040 ★★★（系统设计）
为一个嵌入式 Linux 产品（如智能网关）设计"主控 + 看门狗进程"双进程架构：主控进程 crash 后 3 秒内自动重启（保留故障现场）、看门狗进程自身被杀也有兜底、系统级资源泄漏可观测。给出进程拓扑、通信与保活设计。

**参考设计**：

**进程拓扑**：
```
systemd (PID 1, Restart=always 兜底)
 ├─ watchdogd.service   (看门狗守护进程, Restart=always)
 │    └─ 喂硬件看门狗 /dev/watchdog
 └─ mainapp.service     (业务主进程, Restart=on-failure, RestartSec=3)
      └─ 崩溃时 core dump 落盘 (ulimit -c unlimited + core_pattern)
```

**通信与保活设计**：
1. **主进程→watchdogd 心跳**：Unix 域套接字 `/var/run/wd.sock`，主进程每 1s 发送心跳帧（含自身状态摘要：fd 数、RSS、任务健康位）；watchdogd 连续 5 次未收到 → 先 `kill(SIGTERM)` 优雅杀（让主进程刷日志/释放资源），3s 后仍存活则 SIGKILL，由 systemd 拉起新实例；
2. **watchdogd→硬件 WDG**：心跳链全绿才 ioctl 喂狗（WDI_KEEPALIVE）；任一被监控对象失联即停止喂狗 → 硬件复位（应对整个用户态瘫痪、内核 hang 等最深层故障）；
3. **watchdogd 自身保活**：systemd `Restart=always`——watchdogd 被杀后 systemd 秒级拉起；拉起后先校验各被监控进程状态再恢复喂狗，避免空窗误复位（硬件 WDG 超时设 > 2×恢复时间）；
4. **故障现场保留**：core_pattern 指向 /var/crash（单独分区，限总量防写满）；每次崩溃同时 dump `/proc/<pid>/maps`、`/proc/<pid>/fd` 计数、最近 syslog 到现场目录；连续崩溃 3 次/5 分钟 → watchdogd 判定"反复崩溃"，通知云端并进入安全模式（只保留通信上报）；
5. **资源可观测**：心跳帧内嵌 fd 数与 RSS，watchdogd 记录趋势曲线到日志——fd 单调涨（泄漏，见 E-016）、RSS 单调涨（内存泄漏/碎片）在造成事故前即可告警；
6. **升级场景**：OTA 前主进程主动向 watchdogd 发"维护模式"指令，暂停心跳判活，避免升级重启被误判为故障。

**设计要点提炼**：三层保活（systemd 软件层、watchdogd 进程层、硬件 WDG 兜底层）各管一层故障域；优雅退出优先（SIGTERM→SIGKILL 两段式）；复位永远保留取证现场。
**知识点**：Linux-进程保活与故障恢复架构

---

**本批共 40 题（E-001 ~ E-040），累计已完成 280 / 600 题。**
题型分布：单选 16 / 多选 5 / 填空 4 / 判断 5 / 简答 5 / 编程 4 / 设计 1。
回复「继续」获取下一批【模块 F：Linux 应用与驱动开发（55 题）】——设备驱动模型、字符设备驱动、设备树、内核模块、platform 框架、中断处理、printk/devmem/ftrace 调试。
