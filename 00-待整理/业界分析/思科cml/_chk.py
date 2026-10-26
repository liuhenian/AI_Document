import re, io, collections
p = r"D:\WORKSPACE\Obsidian-Workspace\00-待整理\业界分析\思科cml\思科CML-2020-2026-功能体系与能力边界.md"
txt = io.open(p, encoding="utf-8").read()
lines = txt.split("\n")
n = len(lines) - (1 if lines and lines[-1] == "" else 0)
print("lines:", n)
fence = sum(1 for l in lines if l.strip().startswith("```"))
print("fences:", fence, "paired:", fence % 2 == 0)
tables = 0
bad = []
for i in range(len(lines) - 1):
    a, b = lines[i].strip(), lines[i + 1].strip()
    if a.startswith("|") and re.match(r"^\|[\s\-:|]+\|$", b):
        tables += 1
        cols = a.strip("|").count("|") + 1
        j = i + 2
        while j < len(lines) and lines[j].strip().startswith("|"):
            row = lines[j].strip()
            if not re.match(r"^\|[\s\-:|]+\|$", row) and row.strip("|").count("|") + 1 != cols:
                bad.append((j + 1, cols, row.strip("|").count("|") + 1))
            j += 1
print("tables:", tables, "bad rows:", len(bad), bad[:5])
urls = re.findall(r"https?://[^\s\)\|，。；、<>\"]+", txt)
print("url occurrences:", len(urls), "unique:", len(set(urls)))
in_code = False
q = 0
ql = []
for i, l in enumerate(lines):
    if l.strip().startswith("```"):
        in_code = not in_code
        continue
    if in_code:
        continue
    if '"' in l:
        q += l.count('"'); ql.append(i + 1)
print("ascii quotes body:", q, ql[:5])
src = re.findall(r"^\| ([ABC])(\d+) \|", txt, re.M)
print("src:", dict(collections.Counter(x[0] for x in src)))
print("dup ids:", [k for k, v in collections.Counter([x[0] + x[1] for x in src]).items() if v > 1])
print("mermaid:", txt.count("```mermaid"))
print("h3/h4 headings:", len(re.findall(r"^#{2,4} ", txt, re.M)))
