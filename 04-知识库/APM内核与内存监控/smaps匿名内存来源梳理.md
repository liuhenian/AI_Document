在 Linux 下，通过 `/proc/<pid>/smaps` 看到的 **Anonymous** 内存区域，是指那些**没有对应磁盘文件后备**、由内核动态分配物理页、内容初始为全零的内存。下面的表格总结了所有能在用户态产生这类匿名内存的分配方式。

| 分配方式 | 对应系统调用 / 接口 | 是否在 `smaps` 中显示为匿名 | 说明 |
|----------|-------------------|---------------------------|------|
| **私有匿名映射** | `mmap(NULL, size, PROT_READ\|PROT_WRITE, MAP_PRIVATE\|MAP_ANONYMOUS, -1, 0)` | ✔ 是 | 最标准的匿名内存分配方式，用于临时缓冲区、私有数据结构等。 |
| **共享匿名映射** | `mmap(NULL, size, PROT_READ\|PROT_WRITE, MAP_SHARED\|MAP_ANONYMOUS, -1, 0)` | ✔ 是 | 创建匿名共享内存，主要用于父子进程之间共享内存（fork 后继承）。 |
| **`brk` / `sbrk` 扩展数据段** | `brk()` / `sbrk()` | ✔ 是 | 调整进程的堆顶（program break）。C 库的 `malloc` 在分配小内存（通常 <128KB）时使用这个系统调用，所有的堆内存都是匿名页。 |
| **`malloc` 触发的大块 `mmap`** | `malloc` / `new` 内部调用 `mmap(MAP_ANONYMOUS)` | ✔ 是 | 当分配大小超过 `MMAP_THRESHOLD`（默认 128KB）时，`malloc` 会直接用 `mmap` 创建独立的匿名映射来服务请求。这些映射在 `smaps` 中表现为独立的匿名区域。 |
| **线程栈** | `pthread_create` 内部调用 `mmap(MAP_ANONYMOUS\|MAP_STACK\|MAP_GROWSDOWN ...)` | ✔ 是 | 线程库（NPTL）为每个线程分配栈空间，通常是 8MB 的匿名映射，还包含一个 guard page（不可访问）。 |
| **主线程栈** | 内核在 `execve` 时创建 | ✔ 是 | 进程初始栈由内核建立，映射为匿名，大小由 ELF 文件中的 `PT_GNU_STACK` 程序头或 `RLIMIT_STACK` 决定。 |
| **`mremap` 扩展匿名映射** | `mremap(old_addr, old_size, new_size, MREMAP_MAYMOVE)` | ✔ 是（新增部分） | 如果原始区域是匿名映射，`mremap` 扩展出的新空间也是匿名内存。 |
| **大页匿名映射** | `mmap(..., MAP_HUGETLB\|MAP_ANONYMOUS, ...)` | ✔ 是 | 使用大页（2MB / 1GB）分配的匿名内存，对物理页面的管理方式不同，但仍属于匿名页。 |
| **映射 `/dev/zero`（已过时）** | `open("/dev/zero")` + `mmap(..., fd, 0)` | ✔ 是 | 等效于 `MAP_ANONYMOUS`，现在极少使用。产生的 VMA 在 `/proc/pid/maps` 中可能显示文件路径 `/dev/zero`，但页本身是匿名页。 |
| **`mmap` 文件 + `MAP_PRIVATE` 写时拷贝** | `mmap(file, ..., MAP_PRIVATE)` 后发生写操作 | **部分匿名** | 当程序修改私有文件映射的页时，内核会复制原页并变为匿名页（写时拷贝）。在 `smaps` 中该 VMA 的 `Anonymous` 计数会增加。 |
| **`userfaultfd` 按需填充** | `userfaultfd` + `mmap(MAP_ANONYMOUS)` 等 | ✔ 是 | 注册 userfaultfd 处理的未映射区域，内核仍视其为匿名内存，但物理页的填充可由用户态控制。 |
| **`memfd_create` / `shm_open` /  SystemV 共享内存** | `memfd_create` + `mmap` 等 | ✘ 不是（通常显示为文件映射） | 这些方式创建的是**匿名 inode**（驻留在 tmpfs 中），尽管没有磁盘文件，但 VMA 关联了一个文件描述符，在 `/proc/pid/maps` 和 `smaps` 中会被记为文件映射（`/memfd:...` 或 `/dev/shm/...`），`Anonymous` 计数为 0。它们不会贡献到匿名内存的统计。 |
| **栈上的 `alloca`** | `alloca(size)` | ✘ 不产生新映射 | 只在当前栈帧上移动栈指针，不会创建新的 VMA，因此不会在 `smaps` 中产生新的匿名区域。 |

### 0.1.1 总结
在 `smaps` 中看到的大量匿名内存，最有可能来源于以下几类操作：
1. 直接调用 `mmap(MAP_ANONYMOUS)` 的大块分配（自定义内存管理、大缓冲区）。
2. `malloc` 分配超过阈值的大块内存（内部转调 `mmap`）。
3. 大量线程带来的线程栈（线程数 × 8MB）。
4. 私有文件映射因写操作而产生的匿名页（写时拷贝）。

使用 `cat /proc/<pid>/maps` 可以查看各个区域的路径名：若路径名为空或显示 `[heap]`、`[stack]`、`[anon]` 等，即为典型匿名映射；若看到实际文件路径，则是文件映射。通过 `grep -E "\\[heap\\]|\\[stack\\]|^[0-9a-f]+-[0-9a-f]+ ....... [0-9a-f]+ 00:00 0" /proc/<pid>/maps` 可快速筛选出匿名区域。


你观察到 `--pages-as-heap=yes` 下 Massif 报告的内存值远大于 `/proc/<pid>/smaps` 中的匿名内存量，这是**完全符合预期**的，但两者的“差距”需要先确认你对比的具体是哪个指标。  
通常情况下，这个差距来自于：**Massif 统计的是虚拟内存分配总量（包括从未访问过的部分），而 `smaps` 中常见的“匿名内存”指的是物理常驻的匿名页（Anonymous RSS）**。

下面用表格详细列出造成巨大差距的所有原因，并给出验证方法。

---

## 0.2 对比基准说明
- **Massif `total(B)`**：程序通过 `brk` / `mmap` 动态申请的**虚拟内存大小总和**（包含未实际使用的部分）。
- **`smaps` 中常被关注的“匿名内存”**：通常是汇总所有 VMA 的 `Anonymous` 字段，这是**已分配物理页的匿名内存量（匿名 RSS）**，属于物理内存占用的子集。
- 如果你对比的是 `smaps` 的 `Size`（虚拟大小）而非 `Anonymous`，则差距会小很多，但仍会因文件映射等因素而不完全一致。

---

## 0.3 导致 Massif 数据与 smaps 匿名内存差距巨大的原因

| 原因分类                               | 详细说明                                                                                                                                                                                                       | 导致差距方向                      | 如何验证                                                                                        |                                  |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------- | -------------------------------- |
| **1. 虚拟内存 vs 物理内存**                | Massif 记录的是 `mmap(length)` 请求的虚拟地址空间，即使程序从未访问过这块内存，Massif 也全额计入。而 `smaps` 的 `Anonymous` 字段只统计**已分配物理帧并常驻的匿名页**（RSS 的匿名部分）。<br>例：`mmap` 1GB 匿名空间，但只写入 10MB，Massif 显示 1GB，`smaps` 匿名页只有 10MB。                | Massif 远大于 smaps            | `grep Anonymous /proc/<pid>/smaps \| awk '{s+=$2}END{print s}'` 看物理匿名总量；`grep -E "^[0-9a-f] | ^Size:" /proc/<pid>/smaps` 看虚拟总和 |
| **2. 大量未使用的线程栈**                   | 每个线程栈由 `pthread_create` 通过 `mmap(MAP_ANONYMOUS\|MAP_STACK)` 分配，默认虚拟大小 8MB（可配置）。Massif 会把所有线程栈的虚拟空间全部计入。但通常每个线程只用到栈顶的几十 KB，`smaps` 中的匿名物理页极少。                                                               | Massif 远大于 smaps            | 检查线程数：`ls /proc/<pid>/task \| wc -l`；查看 `[stack]` 区域的 `Size` 和 `Anonymous`                  |                                  |
| **3. 文件映射被错误计入 Massif**            | `--pages-as-heap=yes` 会捕获**所有** `mmap` 调用，包括加载共享库、映射数据文件、字体、资源等。这些映射在 `/proc/<pid>/maps` 中有明确的文件路径，不属于匿名内存。而 `smaps` 的 `Anonymous` 字段为 0（除非发生写时拷贝）。Massif 将它们与匿名映射混在一起，造成总量虚增。                             | Massif 远大于 smaps            | `grep -v "00:00 0" /proc/<pid>/maps` 查看文件映射；`strace -e mmap` 看映射时是否指定了 fd                   |                                  |
| **4. 共享内存（匿名 inode）映射**            | `memfd_create`、`shm_open`、`shmget` 等创建的共享内存，在 `maps` 中显示为文件路径（如 `/memfd:xxx`、`/dev/shm/xxx`），其 VMA 属于文件映射。即便这些文件只在内存中，**`smaps` 的 `Anonymous` 字段仍为 0**，不计入匿名内存。但 Massif 会把整个映射计入 `total`。                  | Massif 远大于 smaps            | 检查 `maps` 中是否出现 `/memfd:` 或 `/dev/shm/` 路径；用 `pmap -X` 查看                                   |                                  |
| **5. Massif 记录的是“分配事件”而非当前使用量**    | 若程序频繁 `mmap` 后 `munmap`，Massif 的峰值快照可能远大于程序稳定时的虚拟内存占用。而你查看 `smaps` 时，这些区域可能早已释放。`smaps` 显示的是瞬时状态。                                                                                                          | Massif 峰值 >> smaps 当前值      | 对比 Massif 报告的时间点与 `smaps` 快照是否在同一时刻；用 `ms_print` 查看时间线                                      |                                  |
| **6. 写时复制 (Copy-on-Write) 产生的匿名页** | 对 `MAP_PRIVATE` 的文件映射进行写入后，内核会复制原页并变成匿名页，**增加 `smaps` 中的 `Anonymous` 计数**。但 Massif 只记录原始的 `mmap` 调用，不会为这些新增的匿名页额外增加总量。这种情形下，`smaps` 的匿名物理内存**可能大于** Massif 中对应文件映射的贡献（但通常不会改变整体趋势，因为文件映射占大头时 Massif 仍然偏大）。 | smaps 匿名可能 > Massif 中该映射的贡献 | 查看某个文件映射 VMA 的 `Anonymous` 是否大于 0；`pmap -X <pid>`                                           |                                  |
| **7. `brk` 收缩后内存未归还**              | 当 `malloc` 通过 `brk` 释放内存并调用 `brk` 降低 program break 时，Massif 会减少 `total`。但若 glibc 没有立即收缩（如内存碎片化），`smaps` 中的 `[heap]` 虚拟大小可能大于 Massif 记录的当前值。                                                                | smaps 可能大于 Massif           | 观察 `[heap]` 的 `Size` 与 Massif 报告中 `brk` 的当前值                                                |                                  |
| **8. 内核直接分配的匿名页**                  | 某些匿名页可能并非通过用户态 `mmap` 产生，例如 `process_vm_writev`、`userfaultfd` 的某些模式、或内核为 vDSO、vvar 等映射的匿名页。Massif 完全看不到这些，而它们会出现在 `smaps` 中（尽管通常量很小）。                                                                      | smaps 略大                    | 一般可忽略，量级很小                                                                                  |                                  |

---

## 0.4 如何才能正确比较 Massif 与 smaps？

你需要**对齐比较的维度**：  
- 若想验证 Massif 是否遗漏了分配，应对比 **Massif `total(B)` 与 `/proc/<pid>/maps` 中所有匿名映射（路径为空或 `[heap]`、`[stack]`、`[anon]`）的虚拟大小总和**，而不是 `smaps` 的 `Anonymous` 字段。  
- 若想分析物理内存压力，则**完全不应该用 Massif 的数据**，而应只看 `smaps` 的 `Pss` 或 `Anonymous`，并配合 `perf` 缺页堆栈定位热点。

**快速对比虚拟匿名内存的方法**：
```bash
# 1. 获取当前进程所有匿名映射的虚拟大小总和
awk '/^[0-9a-f]/ && $0 !~ /\// {split($1,a,"-"); sum+=strtonum("0x"a[2])-strtonum("0x"a[1])} END{print sum " bytes"}' /proc/<pid>/maps

# 2. 将结果与 Massif 峰值时刻的总量进行对比（应基本一致，差异来自内核态直接分配的少量匿名区域）。
```

---

## 0.5 结论
你看到的巨大差距，最主要的前三位通常是：  
1. **虚拟 vs 物理**（Massif 计虚拟，smaps 计物理）  
2. **文件映射混入 Massif**（Massif 包含了非匿名映射）  
3. **线程栈虚拟空间全额计入**

理解这些差异后，你就能正确使用 Massif 定位匿名内存的**分配来源**，而把物理占用的分析交给 `smaps` 和 `perf` 缺页采样。