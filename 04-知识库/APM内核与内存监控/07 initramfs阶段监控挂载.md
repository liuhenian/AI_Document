可以。你的目标其实是：

1. **尽早加载 eBPF**
2. **在所有非内建 `.ko` 加载前，就挂上对 `__alloc_pages_nodemask` 的监控**
3. **把监控信息先保存在内存里**
4. 之后再由用户态慢慢读取/落盘

这个目标是**可实现的**，而且比“监控某个模块内部函数”更容易，因为  
`__alloc_pages_nodemask` 是**内核核心函数**，不是某个 `.ko` 里的符号。

---

# 1 先说关键结论

## 1.1 可以早于所有非内建 ko
只要你把 eBPF loader 放到：

- **initramfs `/init`**
- 或系统最早 `/init`

并且在任何：
- `insmod`
- `modprobe`
- `udev/mdev/hotplug`
- 其他自动模块加载机制

之前执行，就可以做到。

因为你监控的是 **内核核心函数 `__alloc_pages_nodemask`**，它从系统很早期开始就存在，不需要等模块加载。

---

## 1.2 监控数据保存到“内存”是 eBPF 的标准玩法
这正适合用 BPF map：

- **ringbuf**
- **perf event array**
- **hash map / LRU hash**
- **per-CPU array / per-CPU hash**

这些都在内核内存里。

如果你的要求是：

> 在系统很早期就开始记录，哪怕用户态还没完全起来

那么最合适的是：

- **先写入 BPF map / ring buffer**
- 等后面用户态 ready 后再读取

---

## 1.3 你不一定应该直接 hook `__alloc_pages_nodemask`
这是重点。

在不同内核版本里：

- `__alloc_pages_nodemask`
- `__alloc_pages`
- `alloc_pages*`
- `get_page_from_freelist`
- `rmqueue`
- `__alloc_pages_slowpath`

这些路径可能变化。

而且有些内核上：
- 符号不可见
- 被 inline
- 名字变化
- kprobe 黑名单限制
- BTF/fentry 不支持

所以你需要根据内核能力选附着方式。

---

# 2 最推荐的监控方式

按优先级说：

## 2.1 方案 A：kprobe `__alloc_pages_nodemask`
最通用。

优点：
- 老内核也可能可用
- 不依赖模块
- 对非内建 `.ko` 之前就能生效

缺点：
- 有些内核符号可能不可探测
- 性能一般
- 高频路径压力大

示意：
```c
SEC("kprobe/__alloc_pages_nodemask")
int BPF_KPROBE(trace_alloc_pages)
{
    ...
}
```

---

## 2.2 方案 B：fentry `__alloc_pages_nodemask`
如果内核支持 BTF + trampoline，这是更好的选择。

优点：
- 性能更好
- 附着更稳

缺点：
- 需要较新内核和 BTF
- 嵌入式设备经常不具备

---

## 2.3 方案 C：退而求其次，hook 更底层或相邻函数
如果 `__alloc_pages_nodemask` 不可挂，可以试：

- `__alloc_pages`
- `get_page_from_freelist`
- `__alloc_pages_slowpath`

但语义会不同。

---

# 3 数据怎么存到内存里

你说“将监控的信息保存到内存”，分两种需求：

---

## 3.1 需求 1：记录每次分配事件
适合：
- ring buffer
- perf buffer

结构示例：

```c
struct alloc_evt {
    __u64 ts;
    __u32 pid;
    __u32 tgid;
    __u64 order;
    __u64 gfp_flags;
    __u64 ip;
    char comm[16];
};
```

每次命中时写一条到 ringbuf。

### 3.1.1 优点
- 保留事件流
- 用户态后续可消费

### 3.1.2 缺点
- `__alloc_pages_nodemask` 是高频函数
- 系统一忙，ringbuf 很容易爆
- 太早期如果没人读，旧数据会被覆盖/丢失

所以如果你要“全量保存”，ringbuf 未必合适。

---

## 3.2 需求 2：聚合统计，长期放内存
更适合 map 聚合。

例如按：
- `pid/tgid`
- `comm`
- `caller ip`
- `gfp_flags`
- `order`

聚合计数：

```c
struct alloc_key {
    __u64 ip;
    __u32 tgid;
    __u32 order;
};

struct alloc_val {
    __u64 cnt;
    __u64 bytes;
    __u64 last_ts;
};
```

每次命中：
- `cnt++`
- `bytes += (1ULL << order) * PAGE_SIZE`

### 3.2.1 优点
- 内存稳定
- 不容易爆
- 适合早期长期记录

### 3.2.2 缺点
- 丢失单次事件细节
- 只能看统计

---

## 3.3 最佳实践：双通道
建议同时做：

### 3.3.1 通道 1：聚合 map
长期存活，保证不爆。

### 3.3.2 通道 2：小 ringbuf
只保留最近事件，用于调试。

这样：
- 系统启动初期先把总量信息保住
- 后续用户态起来后再读详细事件

---

# 4 你要监控什么字段

对 `__alloc_pages_nodemask`，通常关心：

- 时间戳 `bpf_ktime_get_ns()`
- 当前 pid/tgid
- comm
- order
- gfp_mask / gfp_flags
- NUMA 节点参数（如果有）
- 返回地址/调用点
- 是否是中断上下文（可选）
- CPU 号

如果你想知道“哪个 ko 导致了内存申请”，关键是**调用者地址**。

---

# 5 如何判断是不是来自非内建 ko

你说的是：
> 在所有非内建 ko 中，需要监控的信息保存到内存

这里要澄清一下：

你挂的是 `__alloc_pages_nodemask`，它会捕获**所有来源**的页分配，包括：

- 内核本体
- built-in 驱动
- 非内建 `.ko`
- 用户进程触发的内核分配路径

如果你只关心 **非内建 ko 发起的调用**，核心问题就变成：

> 如何识别这次调用的 caller 是否位于某个已加载模块地址范围内

---

## 5.1 方法：记录 caller IP，再由用户态判断是否属于模块地址区间
在 eBPF 中拿到 caller，比如：

- `PT_REGS_IP(ctx)` 不一定是 caller
- 通常需要取返回地址/栈
- 或者用 `bpf_get_stackid`
- 或 `bpf_get_stack`

然后用户态维护：
- `/proc/modules`
- kallsyms
- 模块地址范围

据此判断某个 IP 是否落在某个 `.ko` 地址区间。

### 5.1.1 这个方案最稳妥
因为在 BPF 程序里直接做复杂“模块归属判断”不方便。

---

# 6 推荐架构

---

## 6.1 阶段 1：最早启动
在 initramfs `/init`：

1. 挂载 `/proc`
2. 挂载 `/sys`
3. 挂载 `/sys/fs/bpf`
4. 运行 eBPF loader
5. attach 到 `__alloc_pages_nodemask`
6. pin map 到 bpffs
7. 继续 boot

---

## 6.2 阶段 2：eBPF 内核侧只做轻量记录
不要在这个高频函数里做太重的事情。

建议记录：

- ts
- cpu
- pid/tgid
- comm
- order
- gfp
- caller ip / stack id
- count / bytes

写入：
- 一个聚合 hash map
- 一个 ringbuf（可选）

---

## 6.3 阶段 3：后期用户态进程分析
等系统起来后：

1. 读取 map / ringbuf
2. 读取 `/proc/modules`
3. 获取模块地址范围
4. 将 caller IP 映射到：
   - 内核本体
   - 某个 `.ko`
5. 输出结果

---

# 7 一个更现实的注意事项：高频路径性能
`__alloc_pages_nodemask` 很热，不能无脑全量打点。

## 7.1 建议做限流/采样
比如：

### 7.1.1 方式 1：只统计，不上报每次事件
最推荐。

### 7.1.2 方式 2：按采样率记录详细事件
例如 1/1024：
```c
if ((bpf_get_prandom_u32() & 1023) != 0)
    return 0;
```

### 7.1.3 方式 3：只抓大页分配
例如：
```c
if (order < 2)
    return 0;
```

### 7.1.4 方式 4：只抓来自模块地址空间的调用
这个在 BPF 里直接做不太方便，通常后处理更好。

---

# 8 eBPF 程序大概长这样

下面是一个**思路级**简化示例，不保证直接编译，但结构是对的。

## 8.1 BPF 侧
```c
struct alloc_key {
    __u64 ip;
    __u32 tgid;
    __u32 order;
    __u32 pad;
};

struct alloc_val {
    __u64 cnt;
    __u64 pages;
    __u64 last_ts;
};

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 16384);
    __type(key, struct alloc_key);
    __type(value, struct alloc_val);
} alloc_stat SEC(".maps");

SEC("kprobe/__alloc_pages_nodemask")
int BPF_KPROBE(kp_alloc_pages, gfp_t gfp_mask, unsigned int order, int preferred_nid, nodemask_t *nodemask)
{
    struct alloc_key key = {};
    struct alloc_val *val, init = {};
    __u64 id = bpf_get_current_pid_tgid();

    key.tgid = id >> 32;
    key.order = order;
    key.ip = PT_REGS_IP(ctx);   // 实际上这里未必是你想要的 caller，可能要调整

    val = bpf_map_lookup_elem(&alloc_stat, &key);
    if (!val) {
        init.cnt = 1;
        init.pages = 1ULL << order;
        init.last_ts = bpf_ktime_get_ns();
        bpf_map_update_elem(&alloc_stat, &key, &init, BPF_ANY);
    } else {
        __sync_fetch_and_add(&val->cnt, 1);
        __sync_fetch_and_add(&val->pages, 1ULL << order);
        val->last_ts = bpf_ktime_get_ns();
    }

    return 0;
}
```

> 注意：`PT_REGS_IP(ctx)` 在 kprobe 入口拿到的是当前指令地址，不一定就是“谁调用了这个函数”。如果你要定位调用方，通常要采栈或返回地址。这个实现细节要按架构修正。

---

# 9 更推荐：记录 stack id
如果你真正要知道“是谁在分配页”，比单独取 IP 更好的方式是：

- 开 `BPF_MAP_TYPE_STACK_TRACE`
- 记录 `bpf_get_stackid()`

这样后面用户态能把栈还原出来，再去判断是否某一帧属于某个 `.ko`。

这比只取一个 IP 更准确。

---

# 10 早期启动的最小 `/init` 模板

```sh
#!/bin/sh
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mkdir -p /sys/fs/bpf
mount -t bpf bpf /sys/fs/bpf

echo "[early] load alloc monitor"
/sbin/alloc_ebpf_loader

# 然后再启动 hotplug/udev/modprobe 链
exec /sbin/init
```

如果你想绝对确保“早于所有非内建 ko”，那必须保证：
- 在执行 `/sbin/alloc_ebpf_loader` 之前
- 没有任何 `modprobe/insmod`
- hotplug 没有启动
- 没有自动 request_module 导致用户态模块装载

---

# 11 可能踩的坑

## 11.1 `__alloc_pages_nodemask` 符号名不一致
不同内核可能没有这个名字，或者不可探测。  
要先检查：

```sh
grep __alloc_pages_nodemask /proc/kallsyms
```

如果没有，再试：
```sh
grep __alloc_pages /proc/kallsyms
grep get_page_from_freelist /proc/kallsyms
```

---

## 11.2 kprobe 不一定允许
某些内核配置限制 kprobe/BPF。

检查：
- `CONFIG_KPROBE_EVENTS`
- `CONFIG_BPF`
- `CONFIG_BPF_SYSCALL`
- `CONFIG_FTRACE`
- `CONFIG_DEBUG_INFO_BTF`（若用 fentry）

---

## 11.3 太高频导致系统抖动
一定要先做“统计优先”，不要一上来对每次分配都 ringbuf 输出。

---

## 11.4 早期没有用户态消费者
所以你的设计必须依赖 **map 常驻内存**，不能只依赖实时消费。

---

# 12 最推荐的最终方案

我建议你这样做：

## 12.1 内核侧 eBPF
- attach：`kprobe`/`fentry` 到 `__alloc_pages_nodemask`
- map1：`HASH/LRU_HASH`，按 `stack_id + order + gfp` 聚合
- map2：`STACK_TRACE`
- 可选 map3：小 ringbuf 记录最近异常事件

## 12.2 启动侧
- 在 initramfs `/init` 最早执行 loader
- pin map 到 `/sys/fs/bpf/...`

## 12.3 用户态
- 启动后读取 map
- 结合 `/proc/modules` / `/proc/kallsyms`
- 把 stack/IP 归属到某个 `.ko`
- 输出哪些非内建模块在申请页、申请量多少

---

# 13 一句话总结

**监控 `__alloc_pages_nodemask` 并早于所有非内建 `.ko` 是可行的；正确做法是在 initramfs 最早加载 eBPF，把事件先写进 BPF map 的内存中，并记录 caller IP 或 stack id，之后再由用户态把这些分配归因到具体 `.ko` 模块。**

如果你愿意，我下一条可以直接给你其中一个：

1. **可编译的 libbpf eBPF 程序骨架**（hook `__alloc_pages_nodemask`，统计到 map）
2. **早期 `/init` 加载脚本模板**
3. **用户态解析 `/proc/modules` + BPF map，把分配归因到 ko 的示例代码**