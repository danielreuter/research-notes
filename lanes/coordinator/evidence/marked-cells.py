"""Print the "Marked cells" block for the scoreboard: every Table 2 footnote whose artifact's LATEST `finding` label starts with
"UNDER RE-VERIFICATION" (a cleared or pulled cell gets a later finding label: "CLEARED ..." / "PULLED ..."), from the rendered
tables markdown on argv[1]. Prints nothing when no cell is marked."""
import json, re, sys
from pathlib import Path

LABELS = Path.home() / ".research/store/labels"
md = Path(sys.argv[1]).read_text()
t2 = md.split("## Table 3")[0]
rows = {}
for line in t2.splitlines():
    if line.startswith("| NVIDIA"):
        cells = [c.strip() for c in line.strip("|").split("|")]
        for i, c in enumerate(cells):
            for n in re.findall(r"\[(\d+)\]", c):
                rows[n] = f"{cells[0]} {cells[1].split(' ')[0]}"
foot = dict(re.findall(r"^\[(\d+)\] art:([0-9a-f]{64})", md, re.M))
out = []
for n, art in sorted(foot.items(), key=lambda kv: int(kv[0])):
    d = LABELS / f"art_{art}"
    if not d.is_dir():
        continue
    findings = []
    for f in d.glob("*.json"):
        try:
            j = json.loads(f.read_text())
        except ValueError:
            continue
        if j.get("key") == "finding":
            findings.append((j.get("ts") or "", str(j.get("value") or "")))
    if findings:
        ts, v = max(findings)
        if v.startswith("UNDER RE-VERIFICATION"):
            out.append(f"- **[{n}] {rows.get(n, '')} (art:{art[:8]}): {v.split(':', 1)[0]}.** {v.split(':', 1)[1].strip()}")
if out:
    print("## Marked cells (read before the tables)\n")
    print("These published cells stay in the tables below but are **under re-verification**; each is pulled with its reason if the")
    print("strengthened check fails, and its mark is removed when it passes.\n")
    print("\n".join(out))
    print()
