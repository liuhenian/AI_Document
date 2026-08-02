要把 eBPF 监控探针放到比所有“非内建内核模块”更早的位置，核心思路是：**将 eBPF 加载器（loader）打包进 initramfs，并在 initramfs 的 `/init` 极早阶段运行，随后再让系统继续正常启动**。这样就能保证在任何外部 `.ko` 被 udev/modprobe 拉起来之前，你的监控程序已经附着到 `bpf()` 系统调用上了。

下面给出从编写监控程序、静态编译、到集成进 initramfs 的完整操作步骤。

---

## 0.4 集成到 initramfs（以 dracut 为例）

在 dracut 中，模块加载发生在 udev 触发之后，而 **`pre-trigger`** 钩子在 udev 启动之前运行，符合“早于所有非内建 ko”的要求。

### 0.4.1 创建自定义 dracut 模块

```bash
mkdir -p /usr/lib/dracut/modules.d/99ebpf-monitor
```

**`/usr/lib/dracut/modules.d/99ebpf-monitor/module-setup.sh`**：
```bash
#!/bin/bash

check() {
    # 如果 monitor 二进制不存在，跳过该模块
    [ -x /usr/local/bin/monitor ] || return 1
    return 0
}

depends() {
    echo ""
}

install() {
    # 安装静态编译的监控程序
    inst /usr/local/bin/monitor /usr/bin/monitor

    # 安装钩子脚本到 pre-trigger 阶段
    inst_hook pre-trigger 01 "$moddir/start-monitor.sh"
}
```

**`/usr/lib/dracut/modules.d/99ebpf-monitor/start-monitor.sh`**：
```bash
#!/bin/sh

# 此时 /proc 和 /sys 已经挂载，但 /dev/kmsg 可能还不可用？
# dracut 在 pre-trigger 前已经挂载了 devtmpfs，所以 /dev 可用。
# 保险起见，也可以手动挂载
mount -t devtmpfs devtmpfs /dev 2>/dev/null

# 启动监控程序（后台运行，脱离当前 shell）
/usr/bin/monitor &
disown
```

### 0.4.2 安装并重建 initramfs

```bash
cp monitor /usr/local/bin/monitor           # 放到系统目录
chmod +x /usr/local/bin/monitor

# 重新生成 initramfs（不同发行版命令略有差异）
dracut --force --add 99ebpf-monitor /boot/initramfs-$(uname -r).img
```

重启后，只要执行 `dmesg | grep ebpf-monitor` 就能看到任何后续 eBPF 程序的加载记录。

---

## 0.5 手动构建 initramfs 的方法（备选）

如果想完全自己控制 initramfs，可以用 busybox 构建最小镜像。

**目录结构**：
```
custom_initramfs/
├── init
├── bin/
│   ├── busybox
│   └── monitor
└── ...
```

**`init`** 脚本：
```sh
#!/bin/busybox sh

# 挂载基本文件系统
busybox mount -t proc proc /proc
busybox mount -t sysfs sys /sys
busybox mount -t devtmpfs dev /dev

# 启动 eBPF 监控
/bin/monitor &

# 切换到真正的 init
exec /sbin/init
```

打包：
```bash
find . | cpio -H newc -o | gzip > /boot/custom-initramfs.img
```

然后修改 bootloader 使用该 initramfs。

---

## 0.6 验证与注意事项

1. **内核配置**：确保 `CONFIG_DEBUG_INFO_BTF=y`（CO-RE 需要）以及 `CONFIG_BPF_SYSCALL=y`、`CONFIG_BPF_EVENTS=y` 等。
2. **时机确认**：`pre-trigger` 在 systemd-udevd 启动之前运行，此时尚未处理任何 uevent，不会触发外部 `.ko` 的自动加载；而内建模块早已在内核里，所以监控点足够早。
3. **日志持久化**：`/dev/kmsg` 的内容就是 `dmesg` 的输入源，在 pivot root 之前写入的信息都会保留在内核环形缓冲区中，切换根文件系统后依然能通过 `dmesg` 看到。如果希望存成文件，可以在 initramfs 的 `cleanup` 钩子里把日志复制到 `/sysroot/var/log/`。
4. **性能与安全**：生产环境中要注意 perf buffer 的丢事件处理，可通过增大缓冲区来缓解。

这样一套流程下来，你就能在系统最早阶段（甚至先于大部分内核模块加载）用 eBPF 捕获所有后续 eBPF 程序的加载行为，真正做到“用 eBPF 监控 eBPF”。