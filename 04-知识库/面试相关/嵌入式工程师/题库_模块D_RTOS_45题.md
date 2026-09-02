# 题库 · 模块 D：RTOS（共 45 题）

> **本模块知识点导图**
> - RTOS 基础：RTOS 与裸机对比、实时性指标（确定性/抖动）、常见 RTOS 家族
> - 任务管理：任务状态机、任务创建与栈分配、栈溢出检测（高水位）、任务删除的坑
> - 调度器：抢占式优先级调度、时间片轮转、空闲任务、tick 与 vTaskDelay/vTaskDelayUntil、上下文切换原理（PendSV/SysTick）
> - 同步与通信：二值/计数信号量、互斥锁（优先级继承）、递归互斥锁、队列、事件组、任务通知、流缓冲区
> - 经典问题：优先级反转与继承（火星探路者案例）、优先级反转 vs 死锁、优先级丢弃
> - 中断与 RTOS：FromISR API、xHigherPriorityTaskWoken、portYIELD_FROM_ISR、ISR 中禁止调用的 API
> - 其他：软件定时器与守护任务、heap_1~heap_5、临界区实现（关中断 vs 挂起调度器）、tickless 低功耗、RT-Thread 基础、看门狗喂狗设计

---

## 一、单项选择题（18 题）

### D-001 ★
以下关于 RTOS 与裸机系统的对比，说法正确的是：
A. RTOS 的中断响应延迟一定比裸机小
B. RTOS 的本质价值在于提供"确定性的响应时间上界"，而非绝对速度
C. 裸机系统无法实现多任务并发
D. RTOS 中所有任务共享同一个栈空间

**答案：B**
**解析**：
- A 错：裸机中断延迟仅取决于指令流，往往更小；RTOS 若临界区关中断时间过长，中断延迟反而增大；
- B 对：RTOS 核心价值是可预测性——高优先级任务能在确定的时间上界内被调度；
- C 错：裸机用前后台 + 状态机同样能"并发"，只是响应时间上界难以保证；
- D 错：RTOS 每个任务拥有独立栈。
**知识点**：RTOS-基本概念

### D-002 ★
FreeRTOS 中，任务从"就绪（Ready）"转为"运行（Running）"的唯一条件是：
A. 任务调用了 vTaskDelay(0)
B. 调度器选中它为当前最高优先级就绪任务
C. 任务获得了信号量
D. 任务调用了 taskYIELD()

**答案：B**
**解析**：任务被调度运行的唯一途径是被调度器选中。A/D 只是触发一次调度请求，不保证切换；C 是任务从阻塞转为就绪的条件之一。
**知识点**：RTOS-任务状态机

### D-003 ★★
`vTaskDelay(100)` 与 `vTaskDelayUntil(&last, 100)` 的核心区别是：
A. 前者以毫秒为单位，后者以 tick 为单位
B. 前者是相对延时（从调用时刻起算），后者是绝对周期（从上次唤醒时刻起算）
C. 前者会阻塞，后者不会阻塞
D. 两者完全等价

**答案：B**
**解析**：
- 两者参数都是 tick 数，A 错；
- B 对：vTaskDelay 是"从现在起睡 100 tick"，任务实际执行时间会累积到周期上；vTaskDelayUntil 是"睡到上次唤醒 + 100 tick"，周期精确，**所有周期性控制任务必须用 DelayUntil**；
- C 错：两者都阻塞。
**知识点**：RTOS-延时函数

### D-004 ★★
FreeRTOS 的互斥锁（Mutex）相比二值信号量（Binary Semaphore）的关键差异是：
A. Mutex 不支持在 ISR 中使用，Binary Semaphore 支持
B. Mutex 带优先级继承机制，可缓解优先级反转；Binary Semaphore 没有
C. Mutex 只能被创建它的任务获取
D. Mutex 计数最大值为 1，Binary Semaphore 可以为任意值

**答案：B**
**解析**：
- A 表述本身正确（Mutex 确实不能 FromISR），但它不是"关键差异"的完整描述，且属于从属特征；B 才是设计目的层面的本质差异——Mutex 明确用于资源保护，故带优先级继承；
- C 错：Mutex 可被任何任务获取（非递归 Mutex 被其他任务持有时报错，但不是"只有创建者"）；
- D 错：两者最大值都是 1，计数信号量才是任意值。
**知识点**：RTOS-互斥锁与信号量

### D-005 ★
在 FreeRTOS 中断服务程序里调用 `xQueueSend()`，正确的做法是：
A. 直接调用，无需任何修改
B. 调用 `xQueueSendFromISR()`，并正确处理 `pxHigherPriorityTaskWoken` 参数
C. 先关中断再调用 `xQueueSend()`
D. 在 ISR 中创建一个临时任务去调用 `xQueueSend()`

**答案：B**
**解析**：
- A 错：非 FromISR 版本内部可能阻塞、会访问调度器数据结构，在 ISR 中调用直接触发 configASSERT 或未定义行为；
- B 对：ISR 专用 API 不阻塞，且通过 `xHigherPriorityTaskWoken` + `portYIELD_FROM_ISR()` 把"是否需要切换上下文"延迟到 ISR 退出时一次性处理，这是 FreeRTOS 中断设计的精髓；
- C 错：ISR 本身就在中断上下文，关中断无意义且不能解决 API 合法性问题；
- D 错：ISR 中禁止调用会阻塞/创建任务的 API（xTaskCreate 不可在 ISR 调用）。
**知识点**：RTOS-中断与FromISR API

### D-006 ★★
经典优先级反转问题（火星探路者故障）中，最终导致系统复位的原因是：
A. 低优先级任务持有互斥锁长期不释放，高优先级任务被饿死，看门狗超时
B. 高优先级任务死锁
C. 中断丢失
D. 栈溢出

**答案：A**
**解析**：事件链：高优先级任务（总线管理）等待低优先级任务（气象任务）持有的互斥量；期间中优先级任务（通信任务）抢占低优先级任务执行 → 高优先级任务实际被"中"优先级任务间接阻塞（这就是"反转"：优先级最低的间接决定了最高的何时运行）→ 高优先级任务看门狗喂狗失败 → 复位。解决方案是把该互斥量改为优先级继承模式（VxWorks 中打开 priority inheritance flag）。
**知识点**：RTOS-优先级反转

### D-007 ★★
`taskENTER_CRITICAL()` 与 `vTaskSuspendAll()` 的区别是：
A. 功能完全相同，只是名字不同
B. 前者通过关中断实现（保护代码不被中断打断，包括 ISR）；后者仅挂起调度器（任务不会被切换，但中断仍然可以响应）
C. 前者保护时间可以很长，后者必须很短
D. 后者比前者更安全

**答案：B**
**解析**：
- taskENTER_CRITICAL()：关中断（或提升 BASEPRI），临界区内**中断与调度都不会发生**，必须极短；
- vTaskSuspendAll()：只禁止任务切换，中断照常执行。若临界区内调用的函数会访问中断也在访问的数据，则挂起调度器不够安全；
- 典型选择：保护的是"只被任务访问"的数据 → SuspendAll（允许中断，降低中断延迟）；数据会被 ISR 访问 → 关中断。
**知识点**：RTOS-临界区

### D-008 ★★
FreeRTOS 中查看任务栈历史最小剩余量的 API 是：
A. uxTaskGetStackHighWaterMark()
B. uxTaskStackSize()
C. xTaskGetFreeStack()
D. vTaskStackCheck()

**答案：A**
**解析**：栈高水位（High Water Mark）= 任务运行以来栈空闲历史最小值（单位通常是字/word）。FreeRTOS 创建任务时会用 `tskSTACK_FILL_BYTE`（0xA5）填充栈，通过扫描未被覆盖的填充区计算剩余量。工程实践：量产前跑完所有极端分支，HWM 应保留 ≥ 25%~30% 余量。
**知识点**：RTOS-栈管理

### D-009 ★
FreeRTOS 默认调度策略中，同优先级任务之间采用：
A. 先来先服务，永不切换
B. 时间片轮转（每个 tick 轮换一次）
C. 随机调度
D. 抢占式，后创建的任务优先运行

**答案：B**
**解析**：FreeRTOS 在抢占式调度（configUSE_TIME_SLICING = 1）下，同优先级就绪任务在每个 tick 中断时轮转。注意：时间片单位是 1 个 tick，任务也可主动 taskYIELD() 让出。
**知识点**：RTOS-调度策略

### D-010 ★★
关于 FreeRTOS 任务通知（Task Notification），以下说法错误的是：
A. 任务通知比队列、信号量更轻量，无需创建内核对象
B. 任务通知只能一对一，不能广播给多个任务
C. 任务通知可以完全替代互斥锁用于所有场景
D. 发送通知的一方可以等待对方接收完成（模仿"握手"）

**答案：C**
**解析**：
- A 对：直接写入 TCB 内的通知值，无独立对象，速度快约 45%（官方数据）；
- B 对：一对一直达，这是它的限制；
- C 错：任务通知没有优先级继承，用它替代 Mutex 保护共享资源会重新引入优先级反转；它适合"事件通知"而非"资源保护"；
- D 对：eSetValueWithOverwrite/eIncrement 等模式 + ulTaskNotifyTake 可实现多种同步语义。
**知识点**：RTOS-任务通知

### D-011 ★★
FreeRTOS 软件定时器回调函数运行的上下文是：
A. 定时器创建时所在的任务
B. 定时器服务任务（Timer Daemon / 守护任务）
C. 中断上下文
D. 单独创建的定时器线程

**答案：B**
**解析**：所有软件定时器回调都在同一个守护任务（prvTimerTask）中顺序执行。推论（高频考点）：**回调里绝不能阻塞**（vTaskDelay、死等信号量），否则会拖延所有其他定时器回调；回调里 FromISR API 也不能用（不是 ISR）。若回调工作量大，正确做法是回调里只发通知/入队，由工作任务处理。
**知识点**：RTOS-软件定时器

### D-012 ★★★
Cortex-M 上 FreeRTOS 上下文切换使用 PendSV 异常且优先级配置为最低，原因是：
A. PendSV 硬件上就是最低优先级，无法修改
B. 保证上下文切换发生在所有其他中断处理完成之后，避免在中断嵌套过程中切换上下文
C. 节省 CPU 周期
D. 为了兼容 M0 内核

**答案：B**
**解析**：
- A 错：PendSV 优先级可配置，只是规范要求设为最低；
- B 对：若在 NVIC 嵌套中断中途切换上下文，被切换走的上下文可能持有尚未完成的中断状态，导致栈混乱。PendSV 设为最低 + PENDSVSET 挂起标志，意味着"等所有中断处理完、退出嵌套后才执行切换"——一次触发只切换一次，天然合并多次切换请求；
- SysTick 负责 tick 计数与时间片；SVC 用于启动第一个任务（M0 用 SVC 0 也可启动）。
**知识点**：RTOS-上下文切换原理

### D-013 ★★
FreeRTOS 中 `xSemaphoreTake(mutex, portMAX_DELAY)` 在互斥锁被低优先级任务持有时，当前高优先级任务的阻塞行为是：
A. 完全阻塞，低优先级任务做什么都无关
B. 低优先级任务被临时提升到与高优先级任务相同的优先级运行（优先级继承），以尽快释放锁
C. 低优先级任务立刻释放锁
D. 系统死锁

**答案：B**
**解析**：这就是优先级继承（Priority Inheritance）：高优先级任务 H 在 Mutex 上阻塞时，持有者 L 的优先级被临时提升至 H 的水平，防止中优先级任务 M 抢占 L 拖长阻塞（火星探路者问题）。L 释放锁后恢复原优先级。注意继承的局限：不能解决死锁；传递链上的"链式继承"部分实现不完整（FreeRTOS 只做单级继承）。
**知识点**：RTOS-优先级继承

### D-014 ★
FreeRTOS 的空闲任务（Idle Task）不能被删除或阻塞的原因是：
A. 空闲任务是最高优先级
B. 低功耗 tickless 模式与任务内存回收（删除任务后的 TCB/栈释放）依赖空闲任务运行
C. 空闲任务持有系统互斥锁
D. 删除空闲任务 API 不存在但技术上可行且无影响

**答案：B**
**解析**：
- 空闲任务优先级为 0（最低），A 错；
- B 对：vTaskDelete() 删除任务时若非"自杀"则直接释放内存；若是任务删除自己，内存释放被推迟到空闲任务（prvCheckTasksWaitingTermination）；tickless idle 也在空闲任务中进入；
- 若用 vTaskSuspendAll() 挂起空闲任务且删除了大量"自杀"任务，会内存泄漏。
**知识点**：RTOS-空闲任务

### D-015 ★★
关于 FreeRTOS 的内存分配方案，`heap_4.c` 的特点是：
A. 不支持内存释放
B. 支持释放，且相邻空闲块自动合并（coalescence），使用 first-fit 算法
C. 支持释放但碎片永不合并
D. 使用外部堆（malloc/free 包装）

**答案：B**
**解析**：
- heap_1：只分配不释放，确定性最好；
- heap_2：支持释放，不合并相邻块，反复分配/释放不同大小会产生碎片；
- heap_3：线程安全包装标准 malloc/free；
- heap_4：在 heap_2 基础上增加相邻空闲块合并，first-fit，**最常用默认选择**；
- heap_5：heap_4 + 支持不连续内存区域（多块 RAM 合并）。
**知识点**：RTOS-内存管理

### D-016 ★★
某任务使用 `xQueueReceive(queue, &buf, 100)`，队列当前为空。100 tick 后队列仍为空，函数返回值是：
A. pdTRUE
B. pdFALSE
C. pdPASS
D. errQUEUE_EMPTY

**答案：B**
**解析**：成功收到数据返回 pdTRUE；超时未收到返回 pdFALSE。pdPASS 用于发送/创建类 API 的成功返回。顺带记忆：ISR 版 `xQueueReceiveFromISR` 无阻塞参数，通过返回 pdTRUE/pdFALSE 表示是否取到。
**知识点**：RTOS-队列API

### D-017 ★★★
下列哪种情况**不会**触发 FreeRTOS 的栈溢出检测（configCHECK_FOR_STACK_OVERFLOW = 2 模式）？
A. 任务栈被写穿越过栈底边界超过若干字节（破坏了填充模式）
B. 任务栈溢出但恰好只破坏了紧邻栈底边界处的填充字节
C. 栈指针本身越过边界但溢出方向未触及填充区（如向高地址溢出越过栈顶）
D. A 和 B 和 C 都会被检测到

**答案：C**
**解析**：
- 模式 1：仅检查栈指针是否越界（context switch 时），只在切换瞬间检查，溢出发生在两次切换之间且已弹回则漏检；
- 模式 2：模式 1 + 检查栈尾填充模式字节是否被破坏，可捕获"指针已弹回但数据已写穿"的情况；
- 但两者都只监控栈**末端（低地址）**。若栈向高地址溢出（越过栈顶、进入相邻内存），检测机制不覆盖——B 会被模式 2 捕获（填充字节被破坏即触发），C 不会被捕获。
- 工程结论：溢出检测是概率性兜底，**静态栈预算 + HWM 监控**才是主防线。
**知识点**：RTOS-栈溢出检测

### D-018 ★★
RT-Thread 中，线程调度器的调度依据与线程状态管理，与 FreeRTOS 最主要的设计差异是：
A. RT-Thread 只有协作式调度
B. RT-Thread 线程有时间片参数且支持 256 级优先级，同优先级线程按剩余时间片轮转，时间片耗尽自动排到同级队尾
C. RT-Thread 不支持中断
D. RT-Thread 不支持信号量

**答案：B**
**解析**：
- A 错：RT-Thread 默认为抢占式优先级调度；
- B 对：RT-Thread 优先级 0~255（0 最高），创建线程时 `rt_thread_create(..., priority, timeslice)` 显式指定时间片；同优先级线程按时间片轮转，时间片单位是调度器 tick。FreeRTOS 同优先级固定 1 tick 时间片；
- C/D 错：RT-Thread 有完整中断管理（rt_interrupt_enter/leave）和 IPC 组件（信号量/互斥锁/事件/邮箱/消息队列）。
**知识点**：RTOS-RT-Thread

## 二、多项选择题（5 题）

### D-019 ★★
以下哪些 API **禁止**在中断服务程序中调用（假设 FreeRTOS 正确配置了 configASSERT）？
A. xQueueSend()
B. xSemaphoreTakeFromISR()
C. vTaskDelay()
D. xTaskCreate()
E. xSemaphoreGiveFromISR()

**答案：A、C、D**
**解析**：
- A 错用：需换成 xQueueSendFromISR()，原版可能阻塞；
- C：ISR 中无法阻塞，vTaskDelay 在 ISR 中触发断言/未定义行为；
- D：xTaskCreate 使用堆且访问调度器就绪链表，不允许在 ISR 中调用（xTaskCreateFromISR 新版本存在但限制极多，常规语境判定禁止）；
- B、E 是正确的 ISR 专用 API。
**知识点**：RTOS-ISR安全API

### D-020 ★★
使用互斥锁保护共享资源时，正确的做法包括：
A. 临界区尽量短，只包含真正访问共享资源的代码
B. 临界区内不调用任何可能阻塞的 API（如队列等待、长延时）
C. 多把锁按全局统一的顺序加锁/解锁
D. 为降低开销，在 ISR 中直接 Take/Give 互斥锁
E. 高优先级任务用 portMAX_DELAY 无限期等待锁

**答案：A、B、C、E**
**解析**：
- A/B：缩短临界区 + 禁止嵌套阻塞，是防死锁与抖动的第一原则；
- C：锁排序（lock ordering）是避免死锁的标准手段；
- D 错：互斥锁带优先级继承、依赖任务上下文，**ISR 中绝对禁止**使用 xSemaphoreTake(Mutex)——优先级继承在 ISR 中无意义且实现非法，ISR 需要同步时用 FromISR 信号量；
- E：portMAX_DELAY 等锁本身合法（配合优先级继承可防饿死），关键在于临界区内容受控。
**知识点**：RTOS-互斥锁使用规范

### D-021 ★★
关于死锁，以下说法正确的有：
A. 死锁四个必要条件：互斥、持有并等待、不可剥夺、循环等待
B. 打破"循环等待"（统一加锁顺序）是最常用的工程预防手段
C. 优先级继承可以完全防止死锁发生
D. 超时等待（带 timeout 的 Take）可以把死锁退化为可恢复的超时错误
E. 死锁只能靠人工复位恢复

**答案：A、B、D**
**解析**：
- A、B 对：Coffman 四条件 + 打破循环等待是教科书答案，也是工程唯一可靠手段；
- C 错：优先级继承解决"优先级反转"，与死锁是两类问题，继承对死锁无预防作用；
- D 对：所有锁操作带有限超时并处理超时分支，能把死锁降级为可检测可恢复的故障（配合释放已持有锁回滚）；
- E 错：超时 + 回滚、看门狗复位、锁序审计都是恢复/预防途径。
**知识点**：RTOS-死锁

### D-022 ★★
FreeRTOS 中，configTICK_RATE_HZ 配置为 1000 与配置为 100 的对比，正确的有：
A. tick 越密，时间片轮转切换越频繁，调度开销越大
B. vTaskDelay(1) 的实际最小睡眠时间在两种配置下都是"最多 1 个 tick 周期 + 调度误差"
C. tick 频率越高，时间分辨率越高，但系统平均功耗通常上升
D. vTaskDelayUntil 的周期精度与 tick 频率无关
E. 低功耗产品应尽量选择低 tick 频率并配合 tickless 模式

**答案：A、C、E**
**解析**：
- A 对：1000Hz 时同优先级任务每 1ms 轮转一次，切换与 tick 中断开销显著上升；
- B 对：vTaskDelay(n) 至少睡 n 个 tick，但最长可能 n+1 个 tick（调用时刻位于 tick 周期内的相位决定），与频率无关的规律相同；
- C 对：tick 中断本身阻止 CPU 深睡，高频 tick 直接推高功耗；
- D 错：DelayUntil 的周期精度受 tick 周期量化限制，1000Hz 精度 1ms，100Hz 精度 10ms；
- E 对：tickless idle 在空闲时停掉 tick、用低功耗定时器补偿，唤醒后补 tick 数。
**知识点**：RTOS-tick与调度开销

### D-023 ★★★
多任务系统中设计"看门狗喂狗"机制，正确的做法有：
A. 所有任务各自直接抢着喂硬件看门狗，喂得越勤越好
B. 由一个监控任务统一喂狗，其他任务定期向监控任务"报到"（存活标记/心跳）
C. 各任务报到设有超时，任何任务"失联"则监控任务停止喂狗，触发复位
D. 关键阻塞调用都设置有限超时，避免任务卡死在 portMAX_DELAY 中无法检测
E. 把喂狗放在高优先级任务的死循环里，其他任务卡死也不影响

**答案：B、C、D**
**解析**：
- A 错：某任务卡死、另一任务仍高频喂狗 → 看门狗失效。喂狗≠系统健康；
- B/C 对：中心化心跳监测是标准设计——监控任务检查所有关键任务的 last_seen 时间戳，全部正常才喂狗；任何任务失联即"主动断粮"复位；
- D 对：无限期阻塞使卡死不可检测，重要等待必须有限超时 + 重试/上报；
- E 错：这正是"喂狗任务饿死其他任务还保持假健康"的反模式。
**知识点**：RTOS-看门狗设计

## 三、填空题（4 题）

### D-024 ★
FreeRTOS 任务四种基本状态：运行、就绪、阻塞、______。

**答案**：挂起（Suspended）
**解析**：vTaskSuspend() 进入挂起态，唯一退出方式是 vTaskResume()，挂起态不参与调度、不计超时。
**知识点**：RTOS-任务状态

### D-025 ★★
FreeRTOS 中用 `xSemaphoreCreateMutex()` 创建的互斥锁，初始状态为______（可用/不可用）。

**答案**：可用（即创建即处于"已释放"状态，任务可立即 Take 成功）
**解析**：Mutex 创建即可用；对比 `xSemaphoreCreateBinary()` 创建后为空（不可用），典型用法是 ISR Give、任务 Take，正好匹配"等事件"语义。
**知识点**：RTOS-信号量初始化

### D-026 ★★
Cortex-M 上 FreeRTOS 的三个关键系统异常：SysTick 用于______，SVC 用于______，PendSV 用于______。

**答案**：提供系统 tick（时基与时间片）；启动调度器/第一个任务（以及部分 API 系统服务）；执行上下文（任务）切换
**解析**：SysTick 周期中断驱动 vTaskIncrementTick；SVC 在 vTaskStartScheduler 时触发一次切入首个任务；PendSV 优先级最低，承载实际的上下文切换。M0 没有 BASEPRI，临界区直接关 PRIMASK。
**知识点**：RTOS-内核端口

### D-027 ★★
RT-Thread 中，调度器依据线程的______字段决定就绪顺序，该字段取值范围 0~255，数值越______优先级越高。

**答案**：priority（线程优先级）；小
**解析**：RT-Thread 的 rt_thread 结构体含 `rt_uint8_t priority` 与 `rt_uint8_t remaining_tick`（同优先级时间片轮转）。0 为最高优先级，空闲线程为 255（RT_THREAD_PRIORITY_MAX-1）。
**知识点**：RTOS-RT-Thread

## 四、判断题（5 题）

### D-028 ★
FreeRTOS 中，创建任务时传入的栈大小参数单位是字节。（ ）

**答案：错**
**解析**：单位是**字（word）**，即 `usStackDepth × 4` 字节（32 位平台）。这是新手最常踩的坑之一：想要 512 字节栈，应传 128。经验法则：局部大数组、printf（半主机模式可吃掉 >1KB）都会瞬间推高需求。
**知识点**：RTOS-任务创建

### D-029 ★★
在中断服务函数中调用 `portYIELD_FROM_ISR(xHigherPriorityTaskWoken)`，若参数为 pdFALSE，则不会触发上下文切换。（ ）

**答案：对**
**解析**：该宏检查参数，为 pdTRUE 时挂起 PendSV，ISR 退出后完成切换；pdFALSE 时什么都不做。这使 ISR 统一"先记账、退出时一次结算"，避免中断嵌套中切换。有的端口写成 `portEND_SWITCHING_ISR()`，两者等价。
**知识点**：RTOS-中断退出切换

### D-030 ★★
优先级继承能彻底解决优先级反转的所有问题，包括链式反转和死锁。（ ）

**答案：错**
**解析**：
- 单级继承解决基本反转；但"链式反转"（L 持锁、M 持另一锁、H 需要两把锁）中继承传递不完整时仍会出问题；
- 继承还可能引入"优先级继承自身导致的死锁"（继承不传递经典问题）与"继承期间被提升任务的临界区长度不可控"；
- 工程上：继承是缓解手段，锁排序 + 短临界区才是根治手段。
**知识点**：RTOS-优先级继承局限

### D-031 ★
计数信号量的计数值等于"当前可用资源数量"，Take 使计数减一，Give 使计数加一。（ ）

**答案：对**
**解析**：计数信号量经典用途：资源池管理（N 个缓冲区）、事件计数（中断发生次数累积，防止事件丢失——事件来不及处理时计数不清零，处理循环会把积压全部取走）。
**知识点**：RTOS-计数信号量

### D-032 ★★
在 FreeRTOS 中，如果调用 `vTaskDelete(NULL)` 删除任务自身，任务的栈和 TCB 内存会立即在调用点被释放。（ ）

**答案：错**
**解析**：删除自身时，任务不能释放"自己正站在上面"的栈，因此内存释放被推迟到空闲任务（Idle Task）中执行。推论：频繁自杀的任务若调度器挂起或空闲任务饿死，会持续占用内存（隐性泄漏）；调试期建议保留 configASSERT 与内存统计（vPortGetHeapStats）。
**知识点**：RTOS-任务删除

## 五、简答题（6 题）

### D-033 ★★
简述"优先级反转"的发生过程、危害与三种解决途径。

**参考答案**：
1. **发生过程**：高优先级任务 H 因等待低优先级任务 L 持有的共享资源而阻塞；此时中优先级任务 M（不需要该资源）抢占 L 执行，导致 H 被 M 间接阻塞——H 的实际优先级"反转"为低于 M。
2. **危害**：高优先级任务响应时间上界失控，实时性被破坏；严重时喂狗超时导致系统复位（火星探路者实例）。
3. **解决途径**：
   - **优先级继承（Priority Inheritance）**：H 阻塞时临时提升 L 至 H 的优先级，让 L 尽快执行并释放资源。用 Mutex（而非二值信号量）即可获得该机制；
   - **优先级天花板（Priority Ceiling）**：为每个锁预设天花板优先级，任务获得锁即提升到天花板，可同时防死锁（开销大，工业 RTOS 如 VxWorks/RTEMS 常用）；
   - **架构规避**：缩短临界区、高优先级任务不直接抢共享资源（改用消息队列通信）、锁排序。
**知识点**：RTOS-优先级反转

### D-034 ★★
简述 FreeRTOS 的二值信号量、互斥锁、任务通知三者的适用场景与选择原则。

**参考答案**：
- **二值信号量**：**任务↔中断同步**首选（ISR 中 Give、任务中 Take）；也用于任务间事件通知。无优先级继承，**不能**用于保护共享资源。
- **互斥锁（Mutex）**：**保护任务间共享资源**专用。带优先级继承 + 可递归（Recursive Mutex 版本） + 持有者概念。禁止在 ISR 中使用。
- **任务通知（Task Notification）**：最轻量（直接写 TCB），一对一事件通知，支持 32 位通知值（可当"轻量邮箱"）。速度最快、RAM 占用最少，但只能点对点、无优先级继承、无广播。
- **选择原则口诀**：中断通知任务用二值信号量或任务通知；任务抢资源用 Mutex；任务间简单事件用任务通知；需要缓冲/解耦/多对多用队列。
**知识点**：RTOS-同步机制选型

### D-035 ★★★
描述一次完整的"UART 接收中断 → 数据入队 → 处理任务唤醒"的 FreeRTOS 数据流，说明每步使用的 API 与上下文。

**参考答案**：
1. **中断上下文（UART ISR）**：收到数据/IDLE 事件 → 读取硬件 FIFO → 调用 `xQueueSendFromISR(rxQueue, &frame, &xHigherPriorityTaskWoken)`（初始化 `BaseType_t xHigherPriorityTaskWoken = pdFALSE;`）；
2. 若本次发送唤醒了比当前被打断任务更高优先级的任务，xHigherPriorityTaskWoken 被置 pdTRUE；
3. ISR 末尾调用 `portYIELD_FROM_ISR(xHigherPriorityTaskWoken)`，中断退出时一次性完成上下文切换；
4. **任务上下文（解析任务）**：`xQueueReceive(rxQueue, &frame, portMAX_DELAY)` 阻塞等待，被唤醒后拿到完整帧，进行 CRC 校验、解析、分发；
5. **设计要点**：ISR 内只做搬运不做解析（中断延迟可控）；队列深度按"处理任务最坏被阻塞时间 × 最大帧速率"计算；若速率高、帧大，用"环形缓冲区 + 空闲中断 + 任务通知"组合比队列更省 RAM（队列每条消息有指针拷贝/边界开销）。
**知识点**：RTOS-中断数据流设计

### D-036 ★★
简述 FreeRTOS 栈溢出检测两种模式（configCHECK_FOR_STACK_OVERFLOW = 1 / 2）的原理与局限，并给出工程上的三层防线。

**参考答案**：
- **模式 1（栈指针检查）**：每次上下文切换时检查当前任务栈指针是否越过栈边界。局限：只在切换瞬间检查，若任务在运行中深潜后弹回（溢出发生在两次切换之间），漏检。
- **模式 2（填充模式检查））**：创建任务时栈按 0xA5 填充，每次切换扫描栈尾若干字节是否仍为 0xA5，可捕获"指针已弹回但写穿了栈底"的情况。局限：① 检测有滞后（要等下次切换）；② 只覆盖栈底方向；③ 极浅的写穿（未触及检查区）仍漏检。
- **工程三层防线**：
  1. **静态预算**：编码规范约束（禁止大局部数组，改 static/堆），Code Review + 静态分析（如栈深度分析工具）；
  2. **动态监控**：量产前压力测试中周期读取 `uxTaskGetStackHighWaterMark()`，要求所有任务余量 ≥ 30%；
  3. **兜底检测**：开模式 2 + 栈溢出钩子（vApplicationStackOverflowHook）里保存现场/记录日志，便于量产定位。
**知识点**：RTOS-栈溢出防护

### D-037 ★★
解释 FreeRTOS 中"优先级"数值与实际优先级高低的关系，以及使用 `configMAX_PRIORITIES` 时需要注意什么。

**参考答案**：
- FreeRTOS 中**数值越大优先级越高**（与 RT-Thread、VxWorks 相反，跨平台开发时极易搞混）；0 是最低，空闲任务固定为 0；
- configMAX_PRIORITIES 设定可用优先级数（0 ~ MAX-1）。注意：
  1. 每增加优先级，内核就绪链表数组增加一项，RAM 开销轻微上升（每级一个 ListHead），M0 小 RAM 平台常压缩到 5~8 级；
  2. 若启用优化（configUSE_PORT_OPTIMISED_TASK_SELECTION，Cortex-M 用 CLZ 指令），优先级数通常限制为 32；
  3. 规划原则：相邻关键任务间隔留空级（如 3 和 5），后期插队救急；定时/通信/业务/日志由高到低分层，别全挤两三个优先级里互相抢。
**知识点**：RTOS-优先级规划

### D-038 ★★★
为什么说"把耗时的计算放在高优先级任务里做"和"在中断里做协议解析"都是典型反模式？正确的分层结构是什么？

**参考答案**：
- **高优先级 ≠ 适合跑长任务**：优先级表达的是"响应紧急程度"，不是"业务重要性"。长计算霸占 CPU 会压制所有低优先级任务（喂狗任务被饿死 → 复位；低优先级日志/通信任务饿死 → 数据丢失）。
- **中断里解析协议**：拉长中断关闭时间（若解析中又关中断），系统性抬高中断延迟，其他实时事件丢失；且 ISR 中不可用阻塞 API，解析逻辑被迫写成状态机泥球，难维护。
- **正确分层（ISR–快任务–慢任务）**：
  - **ISR 层**：只搬运（FIFO→RAM/环形缓冲）+ 发通知，执行时间 µs 级；
  - **高优先级实时任务**：短小确定的工作（组帧、硬件时序控制），用 vTaskDelayUntil 保持周期；
  - **中优先级业务任务**：协议解析、状态机、业务逻辑；
  - **低优先级任务**：日志、统计、显示；
  - 层间用队列/通知衔接，天然的背压（队列满 = 上游过载信号）。
**知识点**：RTOS-任务分层设计

## 六、编程题（4 题）

### D-039 ★★（代码找错）
以下代码试图用互斥锁保护共享计数器并周期打印，存在多处错误。请找出并改正：

```c
void sensor_task(void *pv)
{
    for (;;) {
        read_sensor();                 // 读硬件,约 2ms
        xSemaphoreTake(xMutex, portMAX_DELAY);
        g_count += 10;
        vTaskDelay(pdMS_TO_TICKS(50)); // 故意延时?
        xSemaphoreGive(xMutex);
    }
}

void logger_task(void *pv)
{
    for (;;) {
        xSemaphoreTake(xMutex, portMAX_DELAY);
        printf("count=%d\n", g_count);
        xSemaphoreGive(xMutex);
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
```

**答案**：
错误 1：**临界区内调用 vTaskDelay()** —— 持锁睡眠 50ms，其他等锁任务全部被拖慢 50ms，这是"锁内阻塞"的教科书级错误。改法：`g_count += 10; xSemaphoreGive(xMutex);` 后再延时；
错误 2：**临界区过大** —— read_sensor()（2ms 硬件 IO）不需要锁保护，应移出临界区，锁内只保留 `g_count += 10` 一行；
错误 3（隐患）：logger_task 打印期间长时间持锁，printf 本身可能阻塞（串口慢），应改为"锁内拷贝、锁外打印"：

```c
void sensor_task(void *pv)
{
    for (;;) {
        read_sensor();                                  // 锁外做耗时IO
        xSemaphoreTake(xMutex, portMAX_DELAY);
        g_count += 10;                                  // 临界区:仅一行
        xSemaphoreGive(xMutex);
        vTaskDelay(pdMS_TO_TICKS(50));                  // 锁外延时
    }
}

void logger_task(void *pv)
{
    int snap;
    for (;;) {
        xSemaphoreTake(xMutex, portMAX_DELAY);
        snap = g_count;                                 // 快照
        xSemaphoreGive(xMutex);
        printf("count=%d\n", snap);                     // 锁外打印
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
```
**知识点**：RTOS-临界区最小化

### D-040 ★★（写代码）
实现一个"按键去抖 + 事件发布"任务：按键 ISR（已实现，触发时 Give 信号量 `xBtnSem`）每按一次触发一次，要求过滤 30ms 内的重复触发，并把有效按键以参数 `event_code` 发送到队列 `xEventQueue`（深度 10）。写出任务函数。

**参考答案**：

```c
extern SemaphoreHandle_t xBtnSem;   // ISR 中 xSemaphoreGiveFromISR 给出
extern QueueHandle_t    xEventQueue;

#define DEBOUNCE_MS   30

void button_task(void *pv)
{
    TickType_t last = 0;
    Event_t ev;

    for (;;) {
        /* 阻塞等待按键中断信号 */
        if (xSemaphoreTake(xBtnSem, portMAX_DELAY) == pdTRUE) {
            TickType_t now = xTaskGetTickCount();
            /* 30ms 内的触发视为抖动/重复,丢弃 */
            if ((now - last) >= pdMS_TO_TICKS(DEBOUNCE_MS)) {
                last = now;
                ev.code = EV_BUTTON;
                ev.timestamp = now;
                /* 队列满则丢弃并计数,绝不阻塞 */
                if (xQueueSend(xEventQueue, &ev, 0) != pdPASS) {
                    g_event_drop_cnt++;
                }
            }
        }
    }
}
```
**逐行讲解**：
- `(now - last) >= DEBOUNCE`：tick 是无符号整数，回绕时减法结果在模 2³² 意义下依然正确，无需特殊处理——这是 tick 计算的标准技巧；
- 首次进入时 last=0，若系统刚启动 30ms 内来第一次按键会被误滤，可在初始化时把 last 设为负偏置，属可接受边界（也可显式用 static bool first 标记）；
- 发送超时给 0：按键事件不能因队列满而阻塞实时任务，满即丢弃 + 计数上报。
**知识点**：RTOS-信号量+时间过滤

### D-041 ★★★（写代码 + 分析）
实现一个支持"超时升级"的资源访问模式：任务先尝试 `xSemaphoreTake(xMutex, 100)`，失败后不要死等，而是记录告警、继续自旋重试（最多 3 次），最终失败返回错误码。写出函数骨架并说明这样设计的价值。

**参考答案**：

```c
typedef enum { RES_OK = 0, RES_TIMEOUT } res_ret_t;

res_ret_t resource_access_with_retry(void)
{
    const int MAX_RETRY = 3;
    for (int i = 0; i < MAX_RETRY; i++) {
        if (xSemaphoreTake(xMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            /* ---- 临界区:短小确定 ---- */
            do_shared_work();
            /* ------------------------ */
            xSemaphoreGive(xMutex);
            return RES_OK;
        }
        log_warning("mutex timeout, retry %d/%d", i + 1, MAX_RETRY);
    }
    log_error("mutex acquisition failed, give up");
    return RES_TIMEOUT;
}
```
**设计价值**：
1. **死锁退化为超时**：无限期 portMAX_DELAY 等锁，一旦死锁任务永久冻结且无从发现；有限超时 + 重试上限把故障变成"可观测、可上报、可降级"的错误；
2. **超时即诊断信号**：Mutex 正常持有时间应远小于 100ms，反复超时说明临界区失控或低优先级持有者被抢占，告警日志直接指向病灶；
3. **重试上限防止雪崩**：失败到上限后返回错误由上层决定降级（用缓存数据、复位子系统），而不是无限占用 CPU 重试。
**知识点**：RTOS-超时与重试设计

### D-042 ★★★（读代码答结果）
以下代码在 FreeRTOS（抢占式调度、32 位 tick、configUSE_16_BIT_TICKS = 0）下运行，任务 A 优先级 2，任务 B 优先级 1，串口打印瞬时完成。写出输出序列并解释。

```c
void task_a(void *pv)   /* 优先级2,先创建 */
{
    printf("A1\n");
    vTaskDelay(pdMS_TO_TICKS(100));
    printf("A2\n");
}

void task_b(void *pv)   /* 优先级1 */
{
    printf("B1\n");
    vTaskDelay(pdMS_TO_TICKS(50));
    printf("B2\n");
}
```

**答案**：输出序列为 `A1 → B1 → B2 → A2`。
**解析**：
1. 调度器启动，A（优先级高）先运行，打印 A1；
2. A 调用 vTaskDelay(100) 主动阻塞 → 调度器切到 B，打印 B1；
3. B 阻塞 50ms。t=50ms 时 B 唤醒（此时 A 还在睡），打印 B2；
4. t=100ms 时 A 唤醒，打印 A2。
**考察点**：优先级抢占 + 阻塞让出 CPU 的时间线推演。变体：若把 vTaskDelay 去掉且 A 是死循环，B 将永远得不到运行（饿死）——优先级反转之外的"纯饿死"场景。
**知识点**：RTOS-调度时间线

## 七、设计题（3 题）

### D-043 ★★（模块设计）
设计一个"任务健康监控 + 智能喂狗"模块：系统含 4 个周期任务（采集 10ms、控制 5ms、通信 100ms、日志 500ms）和 1 个空闲任务，硬件看门狗超时 4s。给出模块结构、数据结构与伪代码。

**参考设计**：
**结构**：中心监控任务（优先级高于所有被监控任务）+ 每任务心跳表 + 硬件 WDG。

```c
#define N_MON 4
typedef struct {
    const char   *name;
    TickType_t    period;      /* 期望周期 */
    TickType_t    last_seen;   /* 最后报到时刻 */
    bool          enabled;
} mon_item_t;

static mon_item_t s_mon[N_MON] = {
    {"acq",  pdMS_TO_TICKS(10),  0, true},
    {"ctrl", pdMS_TO_TICKS(5),   0, true},
    {"comm", pdMS_TO_TICKS(100), 0, true},
    {"log",  pdMS_TO_TICKS(500), 0, true},
};

/* 各任务在主循环中调用 */
void mon_kick(int id)
{
    taskENTER_CRITICAL();
    s_mon[id].last_seen = xTaskGetTickCount();
    taskEXIT_CRITICAL();
}

/* 监控任务:周期 500ms 巡检 */
void mon_task(void *pv)
{
    for (;;) {
        TickType_t now = xTaskGetTickCount();
        bool all_alive = true;
        for (int i = 0; i < N_MON; i++) {
            if (!s_mon[i].enabled) continue;
            /* 判据:超过 3 个周期未报到视为失联 */
            if ((now - s_mon[i].last_seen) > 3 * s_mon[i].period) {
                log_fault("task %s stuck, dt=%u", s_mon[i].name,
                          (unsigned)(now - s_mon[i].last_seen));
                all_alive = false;      /* 断粮:不再喂狗 */
            }
        }
        if (all_alive) wdg_refresh();   /* IWDG 喂狗 */
        vTaskDelayUntil(&xLast, pdMS_TO_TICKS(500));
    }
}
```
**关键设计点**：
1. **判据用周期倍数**（3×）而非统一超时——10ms 任务卡 500ms 就是灾难，而日志任务 500ms 周期本身就不该按 10ms 判；
2. **断粮而非复位调用**：监控任务只决定"喂/不喂"，由硬件 WDG 完成复位，路径最短最可靠；
3. **失联时先记日志再等复位**：nofail 存储区留下诊断现场，复位后可回溯；
4. **监控任务自身由谁监控？**——它不喂狗时 WDG 会超时，即"监控任务卡死 → 系统复位"，自闭环；
5. 无符号 tick 差值回绕安全。
**知识点**：RTOS-健康监控设计

### D-044 ★★★（系统设计）
设计一个多传感器数据采集系统的 RTOS 任务架构：3 路 UART 传感器（不同速率，50~200Hz）+ 1 路 I2C 传感器 + 1 路网络上报（TCP），要求任一路故障不影响其他通路，且内存占用可控。给出任务划分、优先级、通信拓扑与故障处理。

**参考设计**：

**任务划分与优先级**（高→低）：

| 优先级 | 任务 | 职责 | 栈预算 |
|-----|------|-----|------|
| 5 | uart1/2/3_rx（或单串口任务） | 从环形缓冲取原始帧，校验、解包为标准样本结构 | 512B×3 |
| 4 | i2c_task | 按各传感器 ODR 轮询读取（vTaskDelayUntil） | 384B |
| 3 | aggr_task | 多路样本合并、时间戳对齐、滑动滤波、打包 | 1KB |
| 2 | net_task | TCP 连接管理（状态机：断线退避重连）、发送、ACK 跟踪 | 1KB |
| 1 | mon_task | 健康监控 + 喂狗（上题方案） | 384B |
| 0 | idle | tickless + 回收 | 最小 |

**通信拓扑**：
```
UART ISR →(DMA+IDLE→环形缓冲+任务通知)→ uart_rx_task →(样本队列)→ aggr_task
I2C task（DelayUntil 轮询）────────────────────────→(样本队列)→ aggr_task
aggr_task →(数据包队列,深度=突发容忍)→ net_task →(socket)
```

**故障隔离设计**：
1. **通路独立**：每路 UART 独立环形缓冲 + 独立任务（或同任务独立状态机），单路 CRC 连续错误 → 该路标记 offline、进入慢速探测（1Hz 重试），不影响其他路；
2. **队列即背压**：net_task 断线时数据包队列渐满 → aggr_task 检测队列高水位，切换"丢弃低价值样本 + 保留告警"策略，环形结构内存占用恒定；
3. **超时永不为 MAX**：所有阻塞（队列、锁、socket）均有限超时 + 重试计数，配合 mon_task 心跳可检测任何任务卡死；
4. **TCP 重连退避**：1s→2s→4s→…→60s 封顶，指数退避防止设备端与服务器端风暴；
5. **内存预算制**：每任务栈写进设计文档，量产前 HWM 审查 ≥30% 余量；总 RAM 占用 = Σ栈 + Σ队列 + 环形缓冲，全部静态可算。

**加分论述点**：为什么单"大任务 + 超级循环"不行——任何一路阻塞（如 socket 同步等待）会冻结所有采集，违背故障隔离原则；任务化的本质是把"故障域"按硬件通路切开。
**知识点**：RTOS-任务架构设计

### D-045 ★★★（排查设计）
现场现象：产品运行数小时后"假死"——串口无日志输出、网络断开，但 3s 后看门狗复位、重启后一切正常。日志显示复位前最后一个事件是"通信任务进入重连"。请给出系统化的排查方案（至少 4 个方向，每个方向给出具体手段）。

**参考排查方案**：
1. **优先级/饿死假设**：通信任务重连逻辑若为高优先级 + 忙等死循环（while(!connected) { try_connect(); } 无延时），会饿死低优先级日志/喂狗任务 → 假死 + WDG 复位。手段：① 复现时接 J-ThreadRTT/Segger SystemView 或 Tracealyzer 看任务 CPU 占用时间线；② 检查重连代码是否含 vTaskDelay（指数退避）；③ 复现后不复位，暂停内核用调试器读各任务状态（uxTaskGetSystemState 导出所有任务 state/优先级/HWM）。
2. **中断风暴假设**：重连期间网络芯片中断异常（如 INT 脚被噪声反复触发），ISR 打满 CPU，任务层完全得不到执行。手段：在中断入口递增计数器（noinit 段保存），复位后读计数器判断风暴；逻辑分析仪抓 INT 引脚。
3. **死锁/循环等待假设**：重连路径拿了网络 Mutex，日志任务打印也碰网络资源 → 循环等待，恰好喂狗任务也间接等日志锁 → 整体冻结。手段：① 静态审查重连路径与日志路径的加锁顺序；② 复现时调试器暂停，查看所有 Mutex 的持有者（FreeRTOS+Tracealyzer 的死锁视图）；③ 把所有 Take 改成有限超时试运行，若日志出现"mutex timeout"即实锤。
4. **栈溢出假设**：重连分支调用深（TLS 握手栈消耗大），通信任务栈溢出破坏相邻 TCB → 链表损坏 → 系统冻结，溢出钩子没来得及跑。手段：开 CHECK_FOR_STACK_OVERFLOW=2 + 溢出钩子写 noinit 日志；审查通信任务栈预算（TLS/AT 指令解析常需 2~4KB）。
5. **内存耗尽假设**：重连循环中反复创建 socket/任务而未释放（heap 泄漏），heap 耗尽后 xQueueSend/xTaskCreate 失败，系统逻辑瘫痪。手段：每分钟 vPortGetHeapStats 记录 xAvailableHeapSize 曲线，看复位前是否单调下降到 0。
**方法论收束**：所有假设都强调"可观测性先行"——noinit 存活日志、任务状态快照、资源统计曲线三大件是量产固件排查假死的标准配置。
**知识点**：RTOS-系统假死排查

---

**本批共 45 题（D-001 ~ D-045），累计已完成 240 / 600 题。**
题型分布：单选 18 / 多选 5 / 填空 4 / 判断 5 / 简答 6 / 编程 4 / 设计 3。
回复「继续」获取下一批【模块 E：Linux 系统原理（40 题）】。
