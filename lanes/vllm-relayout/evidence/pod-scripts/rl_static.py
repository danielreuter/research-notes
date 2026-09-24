"""rl_static.py MOVED_INTEGRATION_DIR [BASE_INTEGRATION_DIR] -- static checks of a relayout-applied tree (light; laptop-safe):
  1. every file the README '## Layout' section names under a subpackage exists;
  2. `verity_vllm/...` paths (plain, regex-escaped) that do not exist, split out into the ones whose base-tree line pointed at an
     existing file (real breakage) and ghosts (already dangling in the base tree).
"""
import glob
import os
import re
import subprocess
import sys

MOVED = os.path.abspath(sys.argv[1])
BASE = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else None
os.chdir(MOVED)

s = open("README.md").read()
i = s.index("## Layout")
j = s.find("\n## ", i + 5)
sec = s[i: j if j > 0 else None]
blk = sec.split("~~~text\n", 1)[1].split("~~~", 1)[0]
missing = []
for line in blk.splitlines():
    m = re.match(r"\s{2}(\w+)/\s+\S.*?\s{2,}(.*)$", line)
    if not m:
        continue
    sub = m.group(1)
    for tok in m.group(2).split():
        tok = tok.rstrip(",")
        if not re.search(r"[./]", tok) or tok == "...":
            continue
        pats = []
        if "{" in tok:
            a, rest = tok.split("{", 1)
            opts, b = rest.split("}", 1)
            pats += [a + o + b for o in opts.split(",")]
        else:
            pats.append(tok)
        for p in pats:
            path = os.path.join("verity_vllm", sub, p)
            if not glob.glob(path) and not glob.glob(path.rstrip("/")):
                missing.append(f"tree {sub}/: {p}")
for sub, text in re.findall(r"\*\*`(\w+)/`\*\*(.*?)(?=\n\n\*\*`|\Z)", sec, re.S):
    for f in re.findall(r"`([\w]+\.(?:py|sh|json|cu|cpp))`", text):
        if not glob.glob(os.path.join("verity_vllm", sub, "**", f), recursive=True):
            missing.append(f"prose {sub}/: {f}")
print("README layout names missing:", len(missing))
for m in missing:
    print("  ", m)

old_of = {}
for l in open("tools/move_map.txt"):
    p = l.split()
    if len(p) >= 3 and p[1] == "->" and not l.startswith("REWRITE"):
        old_of[p[2]] = p[0]
REC = ("tests/regression/expected/", "manifests/", "data/", "fixtures/", "workloads/", "docs/", "tests/program/data/", "tools/")
tok = re.compile(r"(?<![\w./-])(verity_vllm(?:/[\w.*-]+|\\\.)+)")
old_tok = re.compile(r"(?<![\w./-])((?:verity_capture|verity_vllm_numerics|verity_vllm_adapter|verity_vllm)(?:/[\w.*-]+|\\\.)+)")
real, ghost = [], []
for f in subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split():
    if f.startswith(REC) or "/fixtures/" in f:
        continue
    try:
        lines = open(f).read().splitlines()
    except Exception:
        continue
    base_lines = None
    for n, line in enumerate(lines, 1):
        for m in tok.finditer(line):
            p = m.group(1).replace("\\.", ".").rstrip(".,:;)")
            if any(c in p for c in "*{<") or os.path.exists(p) or os.path.exists(p + ".py"):
                continue
            was_live = False
            if BASE:
                if base_lines is None:
                    try:
                        base_lines = open(os.path.join(BASE, old_of.get(f, f))).read().splitlines()
                    except Exception:
                        base_lines = []
                if n <= len(base_lines):
                    for t in old_tok.findall(base_lines[n - 1].replace("\\.", ".")):
                        t = t.rstrip(".,:;)")
                        if os.path.exists(os.path.join(BASE, t)) or os.path.exists(os.path.join(BASE, t + ".py")):
                            was_live = True
            (real if was_live else ghost).append(f"{f}:{n}: {p}")
print("dangling paths whose base line resolved:", len(real))
for r in real:
    print("  ", r)
print("dangling paths already dangling in base (ghosts):", len(ghost))
