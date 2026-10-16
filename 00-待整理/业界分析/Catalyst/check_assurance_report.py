# -*- coding: utf-8 -*-
"""交付前自检（章节感知版，v2）——针对《Catalyst-Center-Assurance端到端体验可观测-2023-2026》
覆盖用户要求的 9 条自检 + 信源条数核对。仅本地静态解析，不写文件。
"""
import re, sys
from pathlib import Path

P = Path(sys.argv[1] if len(sys.argv) > 1 else "Catalyst-Center-Assurance端到端体验可观测-2023-2026-功能体系与痛点解法.md")
text = P.read_text(encoding="utf-8")
lines = text.split("\n")
problems = []

# ---------- 围栏掩码 ----------
fence = [i for i, l in enumerate(lines) if l.strip().startswith("```")]
if len(fence) % 2:
    problems.append(f"[围栏] 代码围栏数为奇数({len(fence)})")
in_code = [False] * len(lines)
t = False
for i, l in enumerate(lines):
    if l.strip().startswith("```"):
        in_code[i] = True; t = not t; continue
    in_code[i] = t

# ---------- 章节切分 ----------
chap_re = re.compile(r"^# (\d+) 大功能点 (\d+)：(.+?) —— (.+)$")
ch = []
for i, l in enumerate(lines):
    m = chap_re.match(l)
    if m:
        ch.append(dict(h1=int(m.group(1)), cn=int(m.group(2)),
                       title=m.group(3).strip(), kh=m.group(4).strip(), start=i))
appx = next((i for i, l in enumerate(lines) if l.startswith("# 9 附一")), len(lines))
for j, c in enumerate(ch):
    c["end"] = ch[j + 1]["start"] if j + 1 < len(ch) else appx

print(f"== 章节数：{len(ch)}（预期 7）")
if len(ch) != 7:
    problems.append(f"[结构] 章数={len(ch)}，预期 7")

EXP_SMALL = {1: 18, 2: 18, 3: 16, 4: 16, 5: 16, 6: 18, 7: 14}
EXP_PS = {1: 6, 2: 6, 3: 5, 4: 5, 5: 6, 6: 7, 7: 5}
small_total = ps_total = 0
stats = {}
for c in ch:
    seg = lines[c["start"]:c["end"]]
    hn, cn = c["h1"], c["cn"]
    sec = {int(m.group(1)): m.group(2) for m in
           (re.match(r"^## %d\.(\d) (.+)$" % hn, l) for l in seg) if m}
    if sorted(sec) != [1, 2, 3, 4, 5]:
        problems.append(f"[五节] 第{cn}章 小节={sorted(sec)}，预期[1..5]")
    sub4 = sorted({int(m.group(1)) for m in
                   (re.match(r"^### %d\.4\.(\d) " % hn, l) for l in seg) if m})
    if not {1, 2, 3}.issubset(set(sub4)):
        problems.append(f"[K.4] 第{cn}章 三级小节={sub4}，缺 4.1/4.2/4.3")
    small = [l for l in seg if re.match(r"^\| %d\.\d+ \|" % cn, l)]
    # 章内小功能点编号须连续 1..n 且前缀=大功能点号
    snums = sorted(int(re.match(r"^\| %d\.(\d+) \|" % cn, l).group(1)) for l in small)
    if snums != list(range(1, len(snums) + 1)):
        problems.append(f"[编号] 第{cn}章 小功能点序号不连续：{snums}")
    small_total += len(small)
    p_defs = sorted({int(m.group(1)) for l in seg for m in [re.match(r"- \*\*P(\d+)（", l)] if m})
    s_refs = {}
    for l in seg:
        ms = re.match(r"^\| \*\*S(\d+)｜", l)
        if ms:
            s_refs[int(ms.group(1))] = {int(x) for x in re.findall(r"解\s*P(\d+)", l)}
    ps_total += len(p_defs)
    s_nums = sorted(s_refs)
    if p_defs != list(range(1, len(p_defs) + 1)):
        problems.append(f"[P] 第{cn}章 P 编号不连续：{p_defs}")
    if s_nums != list(range(1, len(s_nums) + 1)):
        problems.append(f"[S] 第{cn}章 S 编号不连续：{s_nums}")
    if len(p_defs) != len(s_nums):
        problems.append(f"[闭环] 第{cn}章 P数={len(p_defs)}≠S数={len(s_nums)}")
    dang = [p for p in p_defs if not any(p in r for r in s_refs.values())]
    if dang:
        problems.append(f"[闭环] 第{cn}章 悬空痛点 {['P%d'%x for x in dang]}")
    noS = [s for s, r in s_refs.items() if not r]
    if noS:
        problems.append(f"[闭环] 第{cn}章 悬空解法 {['S%d'%x for x in noS]}")
    bad = {s: sorted(r - set(p_defs)) for s, r in s_refs.items() if r - set(p_defs)}
    if bad:
        problems.append(f"[闭环] 第{cn}章 引用不存在痛点 {bad}")
    if len(small) != EXP_SMALL[cn]:
        problems.append(f"[计数] 第{cn}章 小功能点={len(small)}，1.4 声明={EXP_SMALL[cn]}")
    if len(p_defs) != EXP_PS[cn]:
        problems.append(f"[计数] 第{cn}章 P={len(p_defs)}，声明={EXP_PS[cn]}")
    stats[cn] = (len(small), len(p_defs), len(s_nums))
    print(f"  第{cn}章 {c['title']} / {c['kh']}：小功能点 {len(small)}，P {len(p_defs)}，S {len(s_nums)}，K.4子节 {sub4}")

print(f"== 小功能点总计 {small_total}（预期116）; P 总计 {ps_total}（预期40）")
if small_total != 116: problems.append(f"[计数] 小功能点合计={small_total}≠116")
if ps_total != 40: problems.append(f"[计数] P 合计={ps_total}≠40")

# 1.4 全景表核对
for l in lines:
    m = re.match(r"^\| (\d) \| (.+?) \| (.+?) \| (\d+) \|", l)
    if m and 1 <= int(m.group(1)) <= 7:
        cn = int(m.group(1)); n = int(m.group(4))
        if cn in stats and n != stats[cn][0]:
            problems.append(f"[同步] 1.4 表第{cn}行 声明 {n} ≠ 实际 {stats[cn][0]}")

# ---------- 链接 ----------
urls = re.findall(r"https?://[^\s\)\]]+", text)
tagged = re.findall(r"\[(?:A|B|C)\]\(https?://", text)
print(f"== 链接处数 {len(urls)}（去重 {len(set(urls))}）；带等级标注 {len(tagged)}")

# ---------- C 级标注 ----------
print(f"== 「C（本报告推导）」标注 {len(re.findall(chr(67)+'（本报告推导）', text))} 处")

# ---------- 表格列数 ----------
bad = []; i = 0; tn = 0
while i < len(lines):
    if lines[i].lstrip().startswith("|") and not in_code[i]:
        blk = []
        while i < len(lines) and lines[i].lstrip().startswith("|"):
            blk.append(lines[i]); i += 1
        tn += 1
        if len(blk) >= 2:
            nc = lambda s: len(s.strip().strip("|").split("|"))
            hc = nc(blk[0])
            for r in blk[2:]:
                if nc(r) != hc:
                    bad.append((tn, hc, nc(r), r[:50]))
    else:
        i += 1
print(f"== 表格块数 {tn}；列数不一致 {len(bad)}")
for b in bad[:15]: problems.append(f"[表格] 第{b[0]}块 {b[1]}列 vs {b[2]}列: {b[3]}")

# ---------- Mermaid ----------
mm = re.findall(r"```mermaid\n(.*?)```", text, re.S)
print(f"== Mermaid 图数 {len(mm)}")
for k, g in enumerate(mm, 1):
    f = g.strip().split("\n")[0].strip()
    if not f.startswith("flowchart"):
        problems.append(f"[Mermaid] 第{k}图 首行={f}")
    for cd in re.findall(r"classDef\s+\w+\s+([^\n]+)", g):
        if "fill" not in cd or "color" not in cd:
            problems.append(f"[Mermaid] 第{k}图 classDef 缺 fill/color: {cd.strip()}")
    for s in [l for l in g.split("\n") if l.strip().startswith("subgraph")]:
        # 子图标题由 ["…"] 包裹，标题内部不得再含 ASCII 双引号
        m = re.search(r'\["(.*)"\]\s*$', s.strip())
        if not m:
            problems.append(f"[Mermaid] 第{k}图 subgraph 语法异常: {s.strip()}")
        elif '"' in m.group(1):
            problems.append(f"[Mermaid] 第{k}图 subgraph 标题内嵌 ASCII 双引号: {s.strip()}")
    if re.search(r"^\s*(mindmap|timeline)\b", g, re.M):
        problems.append(f"[Mermaid] 第{k}图 使用了 mindmap/timeline")

# ---------- 引号 ----------
si = lambda s: re.sub(r"`[^`]*`", "", s)
rq = [i+1 for i, l in enumerate(lines) if not in_code[i] and ('"' in si(l) or "'" in si(l))]
print(f"== 代码块外 ASCII 直引号行数 {len(rq)}")
for n in rq[:20]: problems.append(f"[引号] 第{n}行: {lines[n-1][:60]}")

# ---------- 未公开项 / 信源条数 ----------
print(f"== 13.4 节存在 {'## 13.4 未收录公开链接的信源' in text}")
for lvl, hd in (("A", "13.1"), ("B", "13.2"), ("C", "13.3")):
    n = len(re.findall(r"^\| %s\d+ \|" % lvl, text, re.M))
    print(f"   {lvl} 级信源条数 {n}")
print(f"== 附五总计行 {'总计 37 条信源' in text}")

print("\n" + "=" * 62)
if problems:
    print(f"[FAIL] {len(problems)} 处待修正：")
    for p in problems: print("  -", p)
else:
    print("[OK] 全部检查项通过。")
print("=" * 62)
