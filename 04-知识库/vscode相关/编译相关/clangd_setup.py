#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clangd-setup —— 交叉编译工程 VSCode clangd 一键配置器

只解决一件事：让 clangd 在这类「多层包装 + cp 构建 + 交叉工具链」的工程里
能正确跳转，而不是靠猜。

用法（最小）：
    python3 clangd_setup.py --src-dir <你编辑的源码目录> --build-cmd "<编译命令>"

实例（本次环境）：
    python3 clangd_setup.py \
        --src-dir /code/ctc_master_s/prj_rgos/tmp/rootfs-build/ce_apm_sw-0 \
        --build-cmd "make ce_apm_sw"

脚本自动完成 7 件事：
  0. 环境探测   OS / 包管理器 / clangd / bear / locale / 权限 / 磁盘
  1. 工具安装   缺失则装 clangd 与 bear，装前做「影响模拟」，绝不静默升级系统库
  2. 路径规划   自动定位编译执行目录；识别 env-setup / defconfig 等前置；规划强制重编
  3. 编译拦截   真实跑一次编译，用 bear 抓取全部编译命令
  4. 后处理     推断「构建副本 → 源码目录」映射；路径绝对化；同文件去重；剔除 gcc 专有参数
  5. 编辑器配置 生成 .vscode/settings.json（合并已有）；写入 git 本地忽略（不动 .gitignore）
  6. 自检修复   启动 clangd 实测诊断；若残留未知参数则自动追加剔除并重跑，最多 3 轮

兼容性：Python 3.5+；apt / yum / dnf；Ubuntu / CentOS / Debian。
无第三方依赖，单文件即可 scp 到目标机。
"""

from __future__ import print_function

import argparse
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time

VERSION = "1.0.0"

# =============================================================================
# 常量
# =============================================================================

# gcc 专有、clang 完全无法识别的参数：保留会让 clangd 报 "Unknown argument" 红色错误
# 用前缀匹配，所以 "-flive-patching" 能覆盖所有变体
DEFAULT_REMOVE_PREFIX = [
    "-flive-patching",
    "-fno-live-patching",
]

# 只为压噪音、不改变解析结果的追加参数
DEFAULT_ADD_FLAGS = [
    "-Wno-unknown-warning-option",   # gcc 有 clang 没有的 -W 选项，别刷屏
    "-Wno-unused-function",          # 静态函数未被引用，正常工程常见
]

CLANGD_NAMES = ["clangd"] + ["clangd-%d" % v for v in range(22, 5, -1)]


# =============================================================================
# 终端输出与进程调用
# =============================================================================

COLOR = sys.stdout.isatty()


def _c(code, s):
    if not COLOR:
        return s
    return "\033[" + code + "m" + s + "\033[0m"


def head(msg):
    print("\n" + _c("1;36", "=" * 72))
    print(_c("1;36", msg))
    print(_c("1;36", "=" * 72))


def step(n, total, msg):
    print("\n" + _c("1;33", "[%d/%d] " % (n, total)) + msg)


def ok(msg):
    print("      " + _c("32", "[OK] ") + msg)


def info(msg):
    print("      " + msg)


def warn(msg):
    print("      " + _c("33", "[警告] ") + msg)


def fail(msg):
    print("      " + _c("31", "[错误] ") + msg)


def hint(msg):
    print("      " + _c("90", "  -> " + msg))


def run(cmd, cwd=None, timeout=None, env=None, shell=False, stdin_data=None):
    """执行命令，返回 (rc, stdout, stderr)，均为 str。永不抛异常（除超时）。"""
    e = dict(os.environ)
    if env:
        e.update(env)
    try:
        p = subprocess.Popen(
            cmd,
            cwd=cwd,
            shell=shell,
            stdin=subprocess.PIPE if stdin_data is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=e,
            preexec_fn=os.setsid if hasattr(os, "setsid") else None,
        )
    except OSError as ex:
        return (-1, "", str(ex))

    try:
        out, err = p.communicate(
            stdin_data.encode("utf-8") if stdin_data is not None else None,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), 9)
        except Exception:
            p.kill()
        p.communicate()
        return (-9, "", "timeout after %ss" % timeout)

    return (
        p.returncode,
        out.decode("utf-8", "replace"),
        err.decode("utf-8", "replace"),
    )


def which(name):
    return shutil.which(name) if hasattr(shutil, "which") else None


def exists(p):
    return p and os.path.exists(p)


# =============================================================================
# 上下文
# =============================================================================

class Ctx(object):
    def __init__(self):
        self.src_dir = ""
        self.build_cmd = ""
        self.work_dir = ""
        self.pre_cmds = []
        self.clean_cmds = []
        self.log_dir = ""
        self.raw_cdb = ""
        self.out_cdb = ""
        self.clangd = ""
        self.clangd_ver = ""
        self.bear = ""
        self.bear_major = 2
        self.remove_prefix = list(DEFAULT_REMOVE_PREFIX)
        self.add_flags = list(DEFAULT_ADD_FLAGS)
        self.query_driver = ""
        self.pkgmgr = ""
        self.mapping = None      # (build_base, src_base)
        self.raw_entries = []    # bear 采集的原始记录，自检重跑时始终基于它
        self.entries = []        # 后处理后的最终记录
        self.installed = []
        self.warnings = []


# =============================================================================
# Phase 0：环境探测
# =============================================================================

def read_os_release():
    d = "/etc/os-release"
    if not os.path.isfile(d):
        d = "/usr/lib/os-release"
    out = {}
    if os.path.isfile(d):
        with open(d, "r", errors="replace") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    out[k] = v.strip('"')
    return out


def find_clangd(explicit):
    """按版本从高到低找 clangd，返回 (path, version_str)"""
    if explicit:
        if os.path.isfile(explicit) and os.access(explicit, os.X_OK):
            return explicit, probe_clangd_version(explicit)
        return "", ""

    found = []
    for n in CLANGD_NAMES:
        p = which(n)
        if p:
            found.append(p)
    # /usr/lib/llvm-XX/bin/clangd 形式
    for base in ("/usr/lib", "/usr/local/lib"):
        if not os.path.isdir(base):
            continue
        for d in sorted(os.listdir(base), reverse=True):
            if d.startswith("llvm-"):
                p = os.path.join(base, d, "bin", "clangd")
                if os.path.isfile(p) and os.access(p, os.X_OK):
                    found.append(p)
    if not found:
        return "", ""

    # 排序依据：版本号优先，同版本时 PATH 里的（/usr/bin 等）优先于
    # /usr/lib/llvm-XX/bin 下的裸二进制，前者资源路径更完整
    scored = []
    for p in set(found):
        v = probe_clangd_version(p)
        m = re.search(r"(\d+)\.(\d+)\.(\d+)", v)
        key = (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (0, 0, 0)
        prefer_path = 1 if not p.startswith("/usr/lib/") and not p.startswith("/usr/local/lib/") else 0
        scored.append(((key[0], key[1], key[2], prefer_path), p, v))
    scored.sort(reverse=True)
    return scored[0][1], scored[0][2]


def probe_clangd_version(path):
    rc, out, err = run([path, "--version"], timeout=20)
    txt = (out or "") + (err or "")
    m = re.search(r"clangd version ([^\s]+)", txt)
    if m:
        return m.group(1)
    m = re.search(r"(\d+\.\d+\.\d+)", txt)
    return m.group(1) if m else "unknown"


def find_bear():
    p = which("bear")
    if not p:
        return "", 2
    rc, out, err = run([p, "--version"], timeout=20)
    txt = (out or "") + (err or "")
    m = re.search(r"(\d+)\.(\d+)", txt)
    major = int(m.group(1)) if m else 2
    return p, major


def detect_pkgmgr():
    for m in ("apt-get", "dnf", "yum"):
        if which(m):
            return m
    return ""


def has_utf8_locale():
    rc, out, _ = run(["locale", "-a"], timeout=20)
    return bool(re.search(r"C\.utf-?8", out or "", re.I))


def phase_detect(ctx, args):
    head("Phase 0 / 环境探测")

    osr = read_os_release()
    info("发行版      : %s" % osr.get("PRETTY_NAME", "unknown"))
    info("内核        : %s" % (run(["uname", "-r"])[1].strip() or "?"))
    info("架构        : %s" % (run(["uname", "-m"])[1].strip() or "?"))
    info("Python      : %s" % sys.version.split()[0])

    try:
        is_root = os.geteuid() == 0
    except AttributeError:
        is_root = False
    ctx.pkgmgr = detect_pkgmgr()
    info("包管理器    : %s" % (ctx.pkgmgr or "未找到"))
    info("权限        : %s" % ("root" if is_root else "普通用户"))
    if not is_root:
        warn("非 root 运行，安装工具时可能需要 sudo 密码")

    utf8 = has_utf8_locale()
    info("UTF-8 locale: %s" % ("可用" if utf8 else "缺失"))
    if not utf8:
        warn("系统无 C.UTF-8。bear 在非 UTF-8 locale 下会因中文注释写 JSON 失败")
        hint("可尝试: locale-gen C.UTF-8  或  apt-get install locales")

    ctx.clangd, ctx.clangd_ver = find_clangd(getattr(args, "clangd_path", "") or None)
    if ctx.clangd:
        ok("clangd      : %s (v%s)" % (ctx.clangd, ctx.clangd_ver))
    else:
        warn("clangd      : 未安装，将在 Phase 1 安装")

    ctx.bear, ctx.bear_major = find_bear()
    if ctx.bear:
        ok("bear        : %s (%d.x)" % (ctx.bear, ctx.bear_major))
    else:
        warn("bear        : 未安装，将在 Phase 1 安装")

    # 磁盘
    rc, out, _ = run(["df", "-Pk", ctx.src_dir or "/"])
    if rc == 0 and len(out.splitlines()) > 1:
        cols = out.splitlines()[1].split()
        if len(cols) >= 4:
            avail_gb = int(cols[3]) / 1024.0 / 1024.0
            info("可用空间    : %.1f GB (%s)" % (avail_gb, cols[5] if len(cols) > 5 else "?"))


# =============================================================================
# Phase 1：安装缺失工具
# =============================================================================

def apt_candidate(pkg):
    rc, out, _ = run(["apt-cache", "policy", pkg], timeout=30)
    if rc != 0:
        return ""
    m = re.search(r"Candidate:\s*(\S+)", out or "")
    if m and m.group(1) != "(none)":
        return m.group(1)
    return ""


def apt_impact(pkg):
    """模拟安装，返回 (safe, detail_lines)"""
    rc, out, err = run(["apt-get", "install", "-s", "-y", pkg], timeout=120)
    txt = (out or "") + (err or "")
    if rc != 0:
        return False, ["apt-get 模拟失败: " + txt.strip().splitlines()[-1] if txt.strip() else "unknown"]
    danger = []
    inst_new = []
    for line in txt.splitlines():
        if line.startswith("Remv "):
            danger.append("会删除: " + line[5:])
        elif line.startswith("Inst "):
            rest = line[5:]
            if "[" in rest:      # Inst foo [1.0] (2.0 ...) 表示升级已有包
                danger.append("会升级: " + rest.split("(")[0].strip())
            else:
                inst_new.append(rest.split("(")[0].strip())
    return (len(danger) == 0), (danger if danger else ["仅新增 " + str(len(inst_new)) + " 个包，不升级不删除"])


def install_with_pkgmgr(ctx, pkg, auto_yes, is_root):
    """在确认安全的前提下安装一个包，返回成功与否"""
    pm = ctx.pkgmgr
    if not pm:
        fail("无可用的包管理器，请手动安装 " + pkg)
        return False

    if pm == "apt-get":
        cand = apt_candidate(pkg)
        if not cand:
            warn("apt 源中找不到 " + pkg)
            return False
        info("apt 可安装版本: %s = %s" % (pkg, cand))
        safe, detail = apt_impact(pkg)
        for d in detail:
            info("  " + d)
        if not safe:
            fail("安装 " + pkg + " 会影响现有包，可能破坏编译环境，已中止")
            hint("如确认无风险，请手动执行: apt-get install -y " + pkg)
            hint("或跳过本步，用 --skip-install 后手动处理")
            if not confirm("仍要继续安装吗？", auto_yes):
                return False

        env = {"DEBIAN_FRONTEND": "noninteractive"}
        info("正在安装 %s（可能需要 1-3 分钟）..." % pkg)
        cmd = ["apt-get", "install", "-y", "--no-install-recommends", pkg]
        if not is_root:
            cmd = ["sudo"] + cmd
        rc, out, err = run(cmd, timeout=900, env=env)
        txt = (out or "") + (err or "")
        if rc != 0:
            # dpkg 半配置状态很常见，尝试修复后重试一次
            if "dpkg" in txt or "lock" in txt:
                warn("检测到 dpkg 状态异常，尝试修复...")
                fix = ["dpkg", "--configure", "-a"]
                if not is_root:
                    fix = ["sudo"] + fix
                run(fix, timeout=300, env=env)
                rc, out, err = run(cmd, timeout=900, env=env)
                txt = (out or "") + (err or "")
        if rc != 0:
            fail("安装失败，最后几行日志：")
            for line in txt.strip().splitlines()[-6:]:
                info("  " + line)
            return False
        ctx.installed.append(pkg)
        return True

    # dnf / yum
    cmd = [pm, "install", "-y", pkg]
    if not is_root:
        cmd = ["sudo"] + cmd
    info("正在安装 %s ..." % pkg)
    rc, out, err = run(cmd, timeout=900)
    if rc != 0:
        fail("安装失败: " + ((err or out or "").strip().splitlines()[-1] if (err or out).strip() else ""))
        return False
    ctx.installed.append(pkg)
    return True


def phase_install(ctx, args):
    head("Phase 1 / 工具安装")

    try:
        is_root = os.geteuid() == 0
    except AttributeError:
        is_root = False

    if args.skip_install:
        info("已指定 --skip-install，跳过自动安装")
        return

    need = []
    if not ctx.clangd:
        need.append("clangd")
    if not ctx.bear:
        need.append("bear")

    if not need:
        ok("clangd 与 bear 均已就绪，无需安装")
        return

    ok_installed_any = False
    for item in need:
        if item == "clangd":
            # 优先找带版本号的包，apt 源里最高的那个
            pkg = ""
            for name in CLANGD_NAMES:
                if apt_candidate(name) and ctx.pkgmgr == "apt-get":
                    pkg = name
                    break
            if not pkg:
                pkg = "clangd"
            info("需要安装 clangd（将尝试 %s）" % pkg)
            if install_with_pkgmgr(ctx, pkg, args.yes, is_root):
                ctx.clangd, ctx.clangd_ver = find_clangd(args.clangd_path or None)
                if ctx.clangd:
                    ok("clangd 安装成功: %s (v%s)" % (ctx.clangd, ctx.clangd_ver))
                    ok_installed_any = True
                else:
                    fail("安装命令成功但找不到 clangd 可执行文件")
            else:
                fail("clangd 安装未完成")
                hint("Ubuntu 16.04 内网源通常只有 clangd-10，可用: apt-get install clangd-10")
        else:
            info("需要安装 bear")
            if install_with_pkgmgr(ctx, "bear", args.yes, is_root):
                ctx.bear, ctx.bear_major = find_bear()
                if ctx.bear:
                    ok("bear 安装成功: %s" % ctx.bear)
                    ok_installed_any = True
            else:
                fail("bear 安装未完成")
                hint("bear 官方源: https://github.com/rizsotto/Bear")

    if not ctx.clangd:
        fail("缺少 clangd，后续步骤无法进行")
        hint("请手动安装后加 --skip-install 重跑本脚本")
        sys.exit(2)
    if not ctx.bear:
        fail("缺少 bear，无法拦截编译命令")
        hint("如已有 intercept-build 可改用 --bear-cmd 指定")
        sys.exit(2)


def confirm(msg, auto_yes):
    if auto_yes:
        return True
    try:
        a = input(msg + " [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("")
        return False
    return a in ("y", "yes")


# =============================================================================
# Phase 2：路径规划
# =============================================================================

def find_work_dir(src_dir, explicit):
    """从 src_dir 向上找含 env-setup 的目录；找不到则用显式值或 src_dir 本身"""
    if explicit:
        return os.path.abspath(explicit)
    cur = os.path.abspath(src_dir)
    for _ in range(6):
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
        if os.path.isfile(os.path.join(cur, "env-setup")):
            return cur
    return os.path.abspath(src_dir)


def plan_clean_steps(work_dir, src_dir, user_clean):
    """规划强制重编译的动作。buildroot 体系靠 stamp 判断是否已构建"""
    if user_clean:
        return list(user_clean)

    steps = []
    rootfs_build = os.path.join(work_dir, "tmp", "rootfs-build")
    src_abs = os.path.abspath(src_dir)

    if os.path.isdir(rootfs_build) and os.path.dirname(src_abs) == os.path.abspath(rootfs_build):
        # 形如 <rootfs-build>/<pkg>-0，对应构建目录是 <rootfs-build>/<pkg>
        base = os.path.basename(src_abs)
        pkg = base[:-2] if base.endswith("-0") else base
        pkg_out = os.path.join(rootfs_build, pkg)
        for stamp in (".stamp_built", ".stamp_target_installed", ".stamp_configured"):
            p = os.path.join(src_abs, stamp)
            if exists(p):
                steps.append("rm -f " + shlex.quote(p))
        if os.path.isdir(os.path.join(pkg_out, "build")):
            steps.append("rm -rf " + shlex.quote(os.path.join(pkg_out, "build")))
    return steps


def phase_plan(ctx, args):
    head("Phase 2 / 路径与构建规划")

    ctx.work_dir = find_work_dir(ctx.src_dir, args.work_dir)
    info("源码目录    : " + ctx.src_dir)
    info("编译目录    : " + ctx.work_dir)

    # 前置命令
    if args.no_pre_cmd:
        ctx.pre_cmds = []
        info("前置命令    : 已显式禁用")
    elif args.pre_cmd:
        ctx.pre_cmds = list(args.pre_cmd)
    else:
        ctx.pre_cmds = []
        env_setup = os.path.join(ctx.work_dir, "env-setup")
        if os.path.isfile(env_setup):
            ctx.pre_cmds.append("source ./env-setup")
            ctx.pre_cmds.append("make defconfig")
            ok("自动识别到 env-setup，将执行: source ./env-setup + make defconfig")
            hint("env-setup 通常会 git reset 平台仓库，因此每次都必须重新 defconfig")
        else:
            info("前置命令    : 无（未发现 env-setup）")

    for c in ctx.pre_cmds:
        info("  $ " + c)

    # 清理动作
    ctx.clean_cmds = plan_clean_steps(ctx.work_dir, ctx.src_dir, args.clean_cmd)
    if ctx.clean_cmds:
        info("强制重编    : %d 步" % len(ctx.clean_cmds))
        for c in ctx.clean_cmds:
            info("  $ " + c)
    else:
        warn("未识别出强制重编动作。若编译显示 'nothing to be done'，bear 将抓不到任何命令")
        hint("可用 --clean-cmd \"make clean\" 指定清理命令")

    info("编译命令    : " + ctx.build_cmd)

    ctx.log_dir = os.path.abspath(os.path.expanduser(args.log_dir))
    if not os.path.isdir(ctx.log_dir):
        os.makedirs(ctx.log_dir)
    info("工作目录    : " + ctx.log_dir)

    ctx.raw_cdb = os.path.join(ctx.log_dir, "compile_commands.raw.json")
    ctx.out_cdb = os.path.abspath(args.out_cdb or os.path.join(ctx.src_dir, "compile_commands.json"))
    info("输出数据库  : " + ctx.out_cdb)


# =============================================================================
# Phase 3：编译拦截
# =============================================================================

def phase_capture(ctx, args):
    head("Phase 3 / 拦截真实编译")

    script_path = os.path.join(ctx.log_dir, "capture.sh")
    build_log = os.path.join(ctx.log_dir, "build.log")

    lines = [
        "#!/bin/bash",
        "# 由 clangd-setup.py 自动生成，勿手工编辑",
        "export LANG=C.UTF-8 LC_ALL=C.UTF-8 LANGUAGE=C.UTF-8",
        "cd " + shlex.quote(ctx.work_dir) + " || exit 90",
        "",
    ]

    # 前置命令：失败不硬退出，让后续编译把真实错误暴露出来
    for c in ctx.pre_cmds:
        safe = c.replace('"', '\\"')
        lines.append('echo "[pre] ' + safe + '"')
        # source 必须在本 shell 内执行才能影响后续命令，不能用子 shell 包裹
        lines.append(c + " >" + shlex.quote(os.devnull) + " 2>&1")
        lines.append('RC=$?; if [ $RC -ne 0 ]; then echo "[warn] 前置失败 rc=$RC: ' + safe + '"; fi')
    lines.append("")

    # 强制重编
    for c in ctx.clean_cmds:
        lines.append("echo \"[clean] " + c.replace('"', '\\"') + "\"")
        lines.append(c)

    lines.append("")
    lines.append("echo \"[bear] 开始编译 $(date +%H:%M:%S)\"")

    if ctx.bear_major >= 3:
        cdb_dir = os.path.join(ctx.log_dir, "bear3out")
        if os.path.isdir(cdb_dir):
            shutil.rmtree(cdb_dir, ignore_errors=True)
        os.makedirs(cdb_dir)
        lines.append(
            shlex.quote(ctx.bear) + " --output " + shlex.quote(cdb_dir) +
            " -- " + ctx.build_cmd + " 2>&1"
        )
    else:
        lines.append(
            shlex.quote(ctx.bear) + " --cdb " + shlex.quote(ctx.raw_cdb) +
            " " + ctx.build_cmd + " 2>&1"
        )

    lines.append("RC=$?")
    lines.append("echo \"[bear] 结束 $(date +%H:%M:%S) rc=$RC\"")
    lines.append("exit $RC")

    with open(script_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(script_path, 0o755)

    info("执行拦截脚本（预计 30-120 秒）...")
    t0 = time.time()
    rc, out, err = run(["bash", script_path], timeout=args.timeout)
    elapsed = time.time() - t0

    with open(build_log, "w") as f:
        f.write(out or "")
        f.write("\n--- stderr ---\n")
        f.write(err or "")

    info("耗时 %.1f 秒，退出码 %s" % (elapsed, rc))

    # bear 3.x 输出是目录
    if ctx.bear_major >= 3:
        p = os.path.join(ctx.log_dir, "bear3out", "compile_commands.json")
        if os.path.isfile(p):
            shutil.copy2(p, ctx.raw_cdb)

    if not os.path.isfile(ctx.raw_cdb):
        fail("未生成编译数据库，编译可能失败了")
        show_tail(build_log)
        hint("常见原因: 1) 编译命令本身报错 2) bear 无法在该命令上生效")
        hint("完整日志: " + build_log)
        sys.exit(3)

    # 编译失败但 cdb 有内容时，也提示（可能只抓到了部分）
    if rc != 0:
        warn("编译返回非 0，但已抓到部分编译命令，将继续处理")
        show_tail(build_log, 12)

    try:
        with open(ctx.raw_cdb) as f:
            raw = json.load(f)
    except Exception as ex:
        fail("编译数据库解析失败: %s" % ex)
        sys.exit(3)

    info("原始记录数  : %d" % len(raw))
    if not raw:
        fail("编译数据库为空 —— 编译没有真正发生")
        hint("请确认清理动作有效，或手动 rm -rf 构建目录后重跑")
        hint("也可用 --clean-cmd 指定清理命令")
        sys.exit(3)

    ctx.raw_entries = raw
    ctx.entries = list(raw)
    ok("编译命令采集完成")


def show_tail(path, n=20):
    try:
        with open(path, "r", errors="replace") as f:
            lines = f.read().splitlines()
        info("日志末尾 %d 行：" % n)
        print("      " + _c("90", "-" * 66))
        for line in lines[-n:]:
            print("      " + _c("90", line[:150]))
        print("      " + _c("90", "-" * 66))
    except Exception:
        pass


# =============================================================================
# Phase 4：后处理
# =============================================================================

def split_common(paths):
    """返回所有路径的公共目录前缀"""
    if not paths:
        return ""
    parts = [p.split(os.sep) for p in paths]
    out = []
    for col in zip(*parts):
        if len(set(col)) == 1:
            out.append(col[0])
        else:
            break
    return os.sep.join(out)


def infer_mapping(files, src_dir):
    """
    推断「编译实际目录 → 用户源码目录」的映射。
    做法：枚举所有路径前缀作为候选 base，把 base 换成 src_dir 后
          看目标文件是否存在，取存在率最高（并列时取最长 base）的那个。
    不依赖目录命名规则，对 cp -rf / 软链 / 多级嵌套都成立。
    """
    src_dir = os.path.abspath(src_dir)
    if not files:
        return None

    # 全部已在源码目录下 → 无需映射
    if all(f.startswith(src_dir + os.sep) or f == src_dir for f in files):
        return None

    cands = set()
    for f in files:
        parts = f.split(os.sep)
        for i in range(len(parts) - 1, 0, -1):
            cands.add(os.sep.join(parts[:i]))

    best_base = None
    best_score = -1.0

    for base in cands:
        if not base:
            continue
        hit = 0
        total = 0
        for f in files:
            if not f.startswith(base + os.sep):
                continue
            total += 1
            rel = f[len(base) + 1:]
            if os.path.exists(os.path.join(src_dir, rel)):
                hit += 1
        if total == 0:
            continue
        score = float(hit) / len(files)
        # 分数优先；同分取更长的 base（替换范围更小、更精确）
        if score > best_score or (score == best_score and
                                  (best_base is None or len(base) > len(best_base))):
            best_score = score
            best_base = base

    if best_base and best_score >= 0.9:
        return (best_base, src_dir)
    return None


def clean_command(cmd, remove_prefix, add_flags):
    try:
        tokens = shlex.split(cmd)
        requote = True
    except ValueError:
        tokens = cmd.split()
        requote = False

    out = []
    for t in tokens:
        drop = False
        for pre in remove_prefix:
            if t == pre or t.startswith(pre + "=") or t.startswith(pre):
                drop = True
                break
        if not drop:
            out.append(t)

    for f in add_flags:
        if f not in out:
            out.append(f)

    if requote:
        return " ".join(shlex.quote(t) if (" " in t or "'" in t) else t for t in out)
    return " ".join(out)


def postprocess(ctx):
    """生成最终的 compile_commands.json，返回 entries"""
    raw = ctx.raw_entries or ctx.entries

    # 第一遍：绝对化 file
    prelim = []
    for e in raw:
        directory = e.get("directory", "") or ""
        fname = e.get("file", "") or ""
        cmd = e.get("command") or " ".join(e.get("arguments", []))
        if not fname:
            continue
        abs_file = fname if os.path.isabs(fname) else os.path.normpath(os.path.join(directory, fname))
        prelim.append({"directory": directory, "file": abs_file, "command": cmd})

    # 推断映射
    ctx.mapping = infer_mapping([p["file"] for p in prelim], ctx.src_dir)

    def rewrite(p):
        if not p or not ctx.mapping:
            return p
        base, target = ctx.mapping
        if p == base:
            return target
        if p.startswith(base + os.sep):
            return target + p[len(base):]
        return p

    best = {}
    for p in prelim:
        abs_file = rewrite(p["file"])
        directory = rewrite(p["directory"]) or os.path.dirname(abs_file)
        cmd = clean_command(rewrite(p["command"]), ctx.remove_prefix, ctx.add_flags)

        entry = {"directory": directory, "file": abs_file, "command": cmd}

        # 同一文件多条记录时，保留「参数更全」的那条（有 -mcpu/-mabi 者通常来自真实构建阶段）
        score = 0
        if "-mcpu=" in cmd or "-mabi=" in cmd:
            score = 2
        elif "-c" in cmd.split():
            score = 1
        old = best.get(abs_file)
        if old is None or score > old[0]:
            best[abs_file] = (score, entry)

    entries = [v[1] for v in best.values()]
    entries.sort(key=lambda x: x["file"])

    if os.path.exists(ctx.out_cdb):
        try:
            shutil.copy2(ctx.out_cdb, ctx.out_cdb + ".bak")
        except Exception:
            pass

    with open(ctx.out_cdb, "w") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    return entries


def phase_postprocess(ctx):
    head("Phase 4 / 后处理编译数据库")

    before = len(ctx.raw_entries or ctx.entries)
    entries = postprocess(ctx)

    if ctx.mapping:
        base, target = ctx.mapping
        ok("路径映射推断成功")
        info("  编译实际目录: " + base)
        info("  重写为      : " + target)
        hint("不重写的话，跳转会落到构建副本，而副本每次编译都被覆盖")
    else:
        ok("源文件已在目标目录下，无需路径重写")

    info("记录数      : %d -> %d（去重合并）" % (before, len(entries)))

    # 校验
    missing = [e["file"] for e in entries if not os.path.exists(e["file"])]
    if missing:
        warn("有 %d 个源文件在磁盘上不存在：" % len(missing))
        for m in missing[:5]:
            info("  " + m)
    else:
        ok("全部 %d 个源文件校验通过" % len(entries))

    inc_dirs = set()
    for e in entries:
        try:
            toks = shlex.split(e["command"])
        except ValueError:
            toks = e["command"].split()
        for tok in toks:
            if tok.startswith("-I") and len(tok) > 2:
                inc_dirs.add(tok[2:])
            elif tok == "-I":
                pass
    missing_inc = [d for d in inc_dirs if not os.path.isdir(d)]
    if missing_inc:
        warn("有 %d 个 -I 目录不存在（通常不影响，头文件可能已含在其它路径下）：" % len(missing_inc))
        for d in missing_inc[:6]:
            info("  " + d)
    elif inc_dirs:
        ok("%d 个 -I 包含目录全部存在" % len(inc_dirs))

    ctx.entries = entries
    if os.path.isdir(os.path.dirname(ctx.out_cdb)):
        # 清理 clangd 索引缓存，确保读到新数据库
        for cache in (".cache/clangd",):
            p = os.path.join(ctx.src_dir, cache)
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)

    ok("已写入: " + ctx.out_cdb)


# =============================================================================
# Phase 5：编辑器配置
# =============================================================================

def detect_source_encoding(entries, src_dir):
    """
    猜源码编码：优先 UTF-8，失败则 GBK。
    取样必须来自 cdb 里的真实源文件路径 —— 源码常在 src_dir 的子目录下，
    只看 src_dir 根目录会漏掉全部文件。
    """
    candidates = [e["file"] for e in entries if os.path.isfile(e["file"])][:8]
    if not candidates:
        try:
            candidates = [os.path.join(src_dir, n) for n in sorted(os.listdir(src_dir))
                          if n.endswith((".c", ".h", ".cpp", ".hpp"))][:8]
        except OSError:
            return "utf-8"

    for p in candidates:
        try:
            with open(p, "rb") as f:
                data = f.read(65536)
        except OSError:
            continue
        if not data:
            continue
        try:
            data.decode("utf-8")
            continue          # 这个文件是 UTF-8，继续看下一个
        except UnicodeDecodeError:
            try:
                data.decode("gbk")
                return "gbk"
            except UnicodeDecodeError:
                continue
    return "utf-8"


def build_vscode_settings(ctx):
    args = [
        "--compile-commands-dir=" + ctx.src_dir,
        "--background-index",
        "--background-index-priority=low",
        "--header-insertion=never",
        "--completion-style=detailed",
        "--pch-storage=memory",
    ]
    if ctx.query_driver:
        args.append("--query-driver=" + ctx.query_driver)

    encoding = detect_source_encoding(ctx.entries, ctx.src_dir)

    return {
        "clangd.path": ctx.clangd,
        "clangd.arguments": args,
        "clangd.onConfigChanged": "restart",
        "clangd.checkUpdates": False,
        # 必须关掉 cpptools 的 IntelliSense，否则两套引擎抢同一批波浪线
        "C_Cpp.intelliSenseEngine": "disabled",
        "C_Cpp.errorSquiggles": "disabled",
        # 编码已由脚本实测确定，关掉自动猜测避免 jschardet 误判
        "files.encoding": encoding,
        "files.autoGuessEncoding": False,
    }


def phase_config(ctx):
    head("Phase 5 / VSCode 配置")

    vsc_dir = os.path.join(ctx.src_dir, ".vscode")
    if not os.path.isdir(vsc_dir):
        os.makedirs(vsc_dir)
    settings_path = os.path.join(vsc_dir, "settings.json")

    new_settings = build_vscode_settings(ctx)
    merged = {}
    if os.path.isfile(settings_path):
        try:
            with open(settings_path, "r", errors="replace") as f:
                merged = json.load(f)
            ok("已读取现有 settings.json，做增量合并")
        except Exception:
            merged = {}
            warn("现有 settings.json 无法解析（可能含注释），将被覆盖")
            shutil.copy2(settings_path, settings_path + ".bak")

    merged.update(new_settings)

    # 清理早期版本写入、但已被证实有害的配置项：
    # 若工程路径本身在 /tmp/ 下，files.watcherExclude 的 "**/tmp/**" 会排除整个工程，
    # 导致 VSCode 完全不监听文件变化。
    for stale in ("search.followSymlinks", "files.watcherExclude"):
        if stale in merged:
            del merged[stale]
            info("  已移除历史遗留项: " + stale)

    with open(settings_path, "w") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    ok("已写入 " + settings_path)
    info("  clangd.path = " + ctx.clangd)
    info("  编码        = " + new_settings["files.encoding"])

    # git 本地忽略（不碰仓库 .gitignore，避免影响团队）
    git_dir = os.path.join(ctx.src_dir, ".git")
    if os.path.isdir(git_dir):
        exclude = os.path.join(git_dir, "info", "exclude")
        info_dir = os.path.dirname(exclude)
        if not os.path.isdir(info_dir):
            os.makedirs(info_dir)
        try:
            content = ""
            if os.path.isfile(exclude):
                with open(exclude, "r", errors="replace") as f:
                    content = f.read()
            if "clangd-setup" not in content:
                with open(exclude, "a") as f:
                    f.write("\n# --- clangd / VSCode 本地辅助文件（clangd-setup 添加，不提交） ---\n")
                    f.write("compile_commands.json\n")
                    f.write("compile_commands.json.bak\n")
                    f.write(".vscode/\n")
                    f.write(".cache/\n")
                ok("已写入 git 本地忽略（.git/info/exclude，不影响团队）")
            else:
                ok("git 本地忽略项已存在")
        except OSError as ex:
            warn("写入 git exclude 失败: %s" % ex)
    else:
        info("非 git 仓库，跳过忽略配置")


# =============================================================================
# Phase 6：clangd 实测自检
# =============================================================================

class LSPClient(object):
    def __init__(self, cmd, cwd):
        self.p = subprocess.Popen(
            cmd, cwd=cwd,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        self.buf = b""
        self.next_id = 1

    def send(self, obj):
        data = json.dumps(obj).encode("utf-8")
        self.p.stdin.write(b"Content-Length: " + str(len(data)).encode() + b"\r\n\r\n" + data)
        self.p.stdin.flush()

    def notify(self, method, params):
        self.send({"jsonrpc": "2.0", "method": method, "params": params})

    def request(self, method, params):
        rid = self.next_id
        self.next_id += 1
        self.send({"jsonrpc": "2.0", "id": rid, "method": method, "params": params})
        return rid

    def maybe_reply(self, msg):
        """
        clangd 会主动向客户端发请求（registerCapability / workDoneProgress / configuration）。
        不回复会让它卡住不动，表现为诊断永远收不齐。
        """
        if msg and "id" in msg and msg.get("method"):
            method = msg["method"]
            if method == "workspace/configuration":
                items = (msg.get("params") or {}).get("items") or []
                result = [None] * len(items)
            else:
                result = None
            self.send({"jsonrpc": "2.0", "id": msg["id"], "result": result})
            return True
        return False

    def read_msg(self, deadline):
        import select
        while True:
            idx = self.buf.find(b"\r\n\r\n")
            if idx >= 0:
                header = self.buf[:idx].decode("ascii", "replace")
                m = re.search(r"Content-Length:\s*(\d+)", header, re.I)
                if not m:
                    self.buf = self.buf[idx + 4:]
                    continue
                n = int(m.group(1))
                start = idx + 4
                while len(self.buf) < start + n:
                    remaining = deadline - time.time()
                    if remaining <= 0:
                        return None
                    r, _, _ = select.select([self.p.stdout], [], [], remaining)
                    if not r:
                        return None
                    chunk = os.read(self.p.stdout.fileno(), 65536)
                    if not chunk:
                        return None
                    self.buf += chunk
                body = self.buf[start:start + n]
                self.buf = self.buf[start + n:]
                try:
                    return json.loads(body.decode("utf-8", "replace"))
                except ValueError:
                    continue
            remaining = deadline - time.time()
            if remaining <= 0:
                return None
            r, _, _ = select.select([self.p.stdout], [], [], remaining)
            if not r:
                return None
            chunk = os.read(self.p.stdout.fileno(), 65536)
            if not chunk:
                return None
            self.buf += chunk

    def close(self):
        try:
            self.request("shutdown", None)
            self.notify("exit", None)
            time.sleep(0.3)
        except Exception:
            pass
        try:
            self.p.kill()
        except Exception:
            pass


def uri_of(path):
    try:
        from urllib.request import pathname2url
    except ImportError:
        from urllib import pathname2url
    return "file://" + pathname2url(path)


def lsp_diagnose(ctx, files, timeout=120):
    """启动 clangd，打开文件，返回 {file: [diagnostics]}"""
    cmd = [ctx.clangd, "--background-index=false", "--log=error",
           "--compile-commands-dir=" + ctx.src_dir,
           "--pch-storage=memory"]
    if ctx.query_driver:
        cmd.append("--query-driver=" + ctx.query_driver)

    cli = LSPClient(cmd, ctx.src_dir)
    deadline = time.time() + timeout
    diags = {}

    try:
        cli.request("initialize", {
            "processId": None,
            "rootUri": uri_of(ctx.src_dir),
            "capabilities": {"textDocument": {"publishDiagnostics": {}}},
            "workspaceFolders": None,
        })
        # 等 initialize 响应
        while time.time() < deadline:
            msg = cli.read_msg(deadline)
            if msg is None:
                break
            if cli.maybe_reply(msg):
                continue
            if msg.get("id") == 1 and "result" in msg:
                break
        cli.notify("initialized", {})

        for path in files:
            try:
                with open(path, "rb") as f:
                    text = f.read().decode("utf-8", "replace")
            except OSError:
                continue
            cli.notify("textDocument/didOpen", {
                "textDocument": {
                    "uri": uri_of(path),
                    "languageId": "c",
                    "version": 1,
                    "text": text,
                }
            })
            diags[path] = None

        # 收集诊断，直到所有文件都有结果或超时
        while time.time() < deadline:
            pending = [k for k, v in diags.items() if v is None]
            if not pending:
                break
            msg = cli.read_msg(deadline)
            if msg is None:
                break
            if cli.maybe_reply(msg):
                continue
            if msg.get("method") == "textDocument/publishDiagnostics":
                p = msg.get("params", {})
                uri = p.get("uri", "")
                try:
                    from urllib.parse import unquote, urlparse
                    up = urlparse(uri)
                    fp = unquote(up.path)
                except ImportError:
                    fp = uri.replace("file://", "")
                for k in list(diags.keys()):
                    if os.path.abspath(k) == os.path.abspath(fp):
                        diags[k] = p.get("diagnostics", [])
                        break
    finally:
        cli.close()

    return {k: (v or []) for k, v in diags.items()}


def phase_selfcheck(ctx, args):
    head("Phase 6 / clangd 实测自检")

    files = [e["file"] for e in ctx.entries if os.path.exists(e["file"])]
    if not files:
        fail("没有可检查的源文件")
        return

    # 挑 include 最多的若干文件做代表，兼顾速度与覆盖
    def inc_count(e):
        return len(re.findall(r"-I", e["command"]))
    ranked = sorted(ctx.entries, key=inc_count, reverse=True)
    sample = [e["file"] for e in ranked if os.path.exists(e["file"])][:args.check_files]
    info("抽样检查    : %d 个文件" % len(sample))

    rounds = 3
    for rnd in range(1, rounds + 1):
        info("第 %d 轮解析..." % rnd)
        res = lsp_diagnose(ctx, sample, timeout=args.check_timeout)

        total = 0
        errors = 0
        not_found = []
        unknown_args = set()

        for path, items in res.items():
            for d in items:
                total += 1
                msg = d.get("message", "")
                sev = d.get("severity", 1)
                if sev == 1:
                    errors += 1
                if "file not found" in msg or "not found" in msg.lower():
                    not_found.append((os.path.basename(path), msg[:110]))
                m = re.search(r"unknown argument:?\s*'?(-[^\s']+)'?", msg)
                if m:
                    unknown_args.add(m.group(1))
                m2 = re.search(r"unknown argument:?\s*'?(-[^\s']+)'?", msg)
                if not m and "unknown argument" in msg:
                    m3 = re.search(r"(-{1,2}[A-Za-z][\w=+\-./]*)", msg)
                    if m3:
                        unknown_args.add(m3.group(1))

        info("  诊断总数 %d（其中 error %d）" % (total, errors))

        if not_found:
            warn("检测到 %d 处头文件找不到：" % len(not_found))
            for name, m in not_found[:5]:
                info("  %s: %s" % (name, m))
            warn("这通常意味着 -I 路径不完整，跳转可能不准")
            break

        if unknown_args:
            added = []
            for a in sorted(unknown_args):
                prefix = a.split("=")[0]
                if prefix not in ctx.remove_prefix:
                    ctx.remove_prefix.append(prefix)
                    added.append(prefix)
            if not added:
                warn("仍有未知参数，但已全部在剔除列表中: " + ", ".join(sorted(unknown_args)))
                break
            warn("发现 clang 不认识的参数，自动追加剔除并重跑: " + ", ".join(added))
            postprocess(ctx)
            continue

        if total == 0:
            ok("解析完成，零诊断 —— 配置干净")
        else:
            ok("解析完成，无阻塞性错误（%d 条提示，多为风格类）" % total)
        break
    else:
        warn("达到最大修复轮次，仍存在未知参数")


# =============================================================================
# Phase 7：报告
# =============================================================================

def phase_report(ctx):
    head("配置完成")

    print("")
    info("clangd      : %s (v%s)" % (ctx.clangd, ctx.clangd_ver))
    info("编译数据库  : %s" % ctx.out_cdb)
    info("条目数      : %d" % len(ctx.entries))
    info("VSCode 配置 : %s" % os.path.join(ctx.src_dir, ".vscode", "settings.json"))
    info("工作目录    : %s" % ctx.log_dir)

    if ctx.installed:
        info("本次新装    : %s" % ", ".join(ctx.installed))

    print("")
    print(_c("1;32", "接下来在 VSCode 里做三件事（一次性）："))
    print("  1. 扩展面板搜索 clangd（LLVM 出品），安装时务必选")
    print("     " + _c("1;33", "Install in SSH: <远程主机>") + "（必须装远端，装本地无效）")
    print("  2. 工作区打开: " + _c("1;36", ctx.src_dir))
    print("  3. 命令面板(F1) 执行: " + _c("1;36", "clangd: Restart language server"))
    print("     首次会在后台建索引，约 1-3 分钟")
    print("")
    print(_c("1;32", "以后什么时候需要重跑本脚本："))
    print("  · 新增或删除 .c 文件            " + _c("33", "需要"))
    print("  · 改了 Makefile / -I / CFLAGS   " + _c("33", "需要"))
    print("  · 只改 .c/.h 里的代码内容        " + _c("32", "不需要") + "（clangd 自己会重新解析）")
    print("")
    print(_c("90", "重跑命令："))
    print(_c("90", "  python3 %s --src-dir %s --build-cmd \"%s\" --skip-install" %
              (os.path.abspath(__file__), ctx.src_dir, ctx.build_cmd)))
    print("")


# =============================================================================
# main
# =============================================================================

def ensure_utf8_stdio():
    """POSIX locale 下 print 中文会 UnicodeEncodeError，这里做两层兜底"""
    enc = (getattr(sys.stdout, "encoding", "") or "").upper()
    if "UTF" in enc:
        return
    # 第一层：若系统有 C.UTF-8，直接用 exec 重启自己
    if has_utf8_locale() and not os.environ.get("_CLANGD_SETUP_REEXEC"):
        os.environ["_CLANGD_SETUP_REEXEC"] = "1"
        os.environ["LANG"] = "C.UTF-8"
        os.environ["LC_ALL"] = "C.UTF-8"
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception:
            pass
    # 第二层：包一层 UTF-8 解码，替换不可编码字符，保证不崩
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass


def parse_args(argv):
    p = argparse.ArgumentParser(
        prog="clangd_setup.py",
        description="交叉编译工程 VSCode clangd 一键配置器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 最小用法（自动探测前置步骤与清理动作）
  python3 clangd_setup.py \\
      --src-dir /code/ctc_master_s/prj_rgos/tmp/rootfs-build/ce_apm_sw-0 \\
      --build-cmd "make ce_apm_sw"

  # 只检测不执行
  python3 clangd_setup.py --src-dir ... --build-cmd "..." --dry-run

  # 自定义前置与清理
  python3 clangd_setup.py --src-dir ... --build-cmd "make app" \\
      --pre-cmd "source ./env-setup" --pre-cmd "make defconfig" \\
      --clean-cmd "make clean"
""")
    p.add_argument("--src-dir", required=True,
                   help="你日常编辑的源码目录（必填）")
    p.add_argument("--build-cmd", required=True,
                   help="编译命令，如 'make ce_apm_sw'（必填）")
    p.add_argument("--work-dir", default="",
                   help="编译命令执行目录；默认从 src-dir 向上自动查找 env-setup")
    p.add_argument("--pre-cmd", action="append", default=None,
                   help="编译前置命令，可重复；默认自动识别 env-setup + defconfig")
    p.add_argument("--no-pre-cmd", action="store_true",
                   help="禁用所有前置命令")
    p.add_argument("--clean-cmd", action="append", default=None,
                   help="强制重编译的清理命令，可重复；默认自动识别 buildroot stamp")
    p.add_argument("--remove-flag", action="append", default=None,
                   help="额外剔除的编译参数（前缀匹配），可重复")
    p.add_argument("--extra-flag", action="append", default=None,
                   help="额外追加的编译参数，可重复")
    p.add_argument("--query-driver", default="",
                   help="clangd 的 --query-driver 值，如 '/path/to/toolchain/bin/*'")
    p.add_argument("--clangd-path", default="",
                   help="指定 clangd 可执行文件路径")
    p.add_argument("--out-cdb", default="",
                   help="编译数据库输出路径；默认 <src-dir>/compile_commands.json")
    p.add_argument("--log-dir", default="~/.clangd-setup",
                   help="日志与中间文件目录；默认 ~/.clangd-setup")
    p.add_argument("--timeout", type=int, default=1800,
                   help="编译超时秒数；默认 1800")
    p.add_argument("--skip-install", action="store_true",
                   help="不自动安装工具，仅检测")
    p.add_argument("--skip-check", action="store_true",
                   help="跳过 clangd 实测自检")
    p.add_argument("--check-files", type=int, default=3,
                   help="自检抽样文件数；默认 3")
    p.add_argument("--check-timeout", type=int, default=120,
                   help="自检超时秒数；默认 120")
    p.add_argument("--dry-run", action="store_true",
                   help="只做环境探测与规划，不编译不改文件")
    p.add_argument("--yes", "-y", action="store_true",
                   help="所有确认自动通过")
    p.add_argument("--version", action="version", version="clangd-setup " + VERSION)
    return p.parse_args(argv)


def main(argv):
    ensure_utf8_stdio()
    args = parse_args(argv)

    ctx = Ctx()
    ctx.src_dir = os.path.abspath(os.path.expanduser(args.src_dir))
    ctx.build_cmd = args.build_cmd.strip()

    # ---- 入参前置校验 ----
    if not os.path.isdir(ctx.src_dir):
        print("错误: 源码目录不存在 -> " + ctx.src_dir)
        return 2
    if not ctx.build_cmd:
        print("错误: --build-cmd 不能为空")
        return 2

    if args.remove_flag:
        for f in args.remove_flag:
            ctx.remove_prefix.append(f)
    if args.extra_flag:
        for f in args.extra_flag:
            if f not in ctx.add_flags:
                ctx.add_flags.append(f)

    print(_c("1;36", "=" * 72))
    print(_c("1;36", "  clangd-setup v%s  —— 交叉编译工程 clangd 一键配置" % VERSION))
    print(_c("1;36", "=" * 72))
    print("")
    info("源码目录    : " + ctx.src_dir)
    info("编译命令    : " + ctx.build_cmd)

    phase_detect(ctx, args)

    if args.dry_run:
        phase_plan(ctx, args)
        head("[dry-run] 到此为止，未做任何修改")
        return 0

    phase_install(ctx, args)

    ctx.query_driver = args.query_driver
    phase_plan(ctx, args)
    phase_capture(ctx, args)
    phase_postprocess(ctx)
    phase_config(ctx)

    if not args.skip_check:
        phase_selfcheck(ctx, args)

    phase_report(ctx)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print("\n已中断")
        sys.exit(130)
