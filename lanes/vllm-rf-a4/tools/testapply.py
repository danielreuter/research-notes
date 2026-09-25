"""Apply testmap.txt: git mv each test file / fixture dir, then rewrite its dotted and path references across the repo.

usage: testapply.py REPO [--dry]      writes /tmp/a4-testmap.json (old -> new test paths, for the jdiff id map)
"""
import json, re, subprocess, sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
dry = "--dry" in sys.argv
T = repo / "integrations/vllm/tests"
here = Path(__file__).parent
NEW_DIRS = {"pipeline", "engine", "properties"}
GONE = ("harness", "input_provenance", "tp")

moves = []
for line in (here / "testmap.txt").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    src, dst = line.split()
    name = src.rsplit("/", 1)[1]
    moves.append((src, name if dst == "." else f"{dst}/{name}"))


def git(*a):
    if dry:
        print("git", *a); return
    subprocess.run(["git", "-C", str(repo), *a], check=True)


for d in sorted(NEW_DIRS):
    init = T / d / "__init__.py"
    if not init.exists() and not dry:
        init.parent.mkdir(parents=True, exist_ok=True)
        init.write_text(f'"""tests.{d}: tests mirror the package"""\n')
        git("add", str(init))
for src, dst in moves:
    (T / dst).parent.mkdir(parents=True, exist_ok=True)
    git("mv", str(T / src), str(T / dst))
for d in GONE:
    init = T / d / "__init__.py"
    if init.exists():
        git("rm", "-q", str(init))

path_map, dot_map = {}, {}
for src, dst in moves:
    path_map[f"tests/{src}"] = f"tests/{dst}"
    if src.endswith(".py"):
        dot_map["tests." + src[:-3].replace("/", ".")] = "tests." + dst[:-3].replace("/", ".")
json.dump({"paths": path_map, "dotted": dot_map}, open("/tmp/a4-testmap.json", "w"), indent=1)

files = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"], capture_output=True, text=True, check=True).stdout.split("\0")
TEXT = {".py", ".sh", ".md", ".txt", ".json", ".toml", ".cfg", ".ini", ".yaml", ".yml", ""}
p_keys = sorted(path_map, key=len, reverse=True)
d_keys = sorted(dot_map, key=len, reverse=True)
p_re = re.compile(r"(?<![\w.])(" + "|".join(re.escape(k) for k in p_keys) + r")(?![\w])")
d_re = re.compile(r"(?<![\w.])(" + "|".join(re.escape(k) for k in d_keys) + r")(?![\w])")
from_re = re.compile(r"^(\s*from\s+)(tests\.(?:" + "|".join(GONE + ("acquire", "check", "observe", "program", "query", "correspondence")) +
                     r"))(\s+import\s+)([\w, ()]+)$", re.M)
changed = []
for f in files:
    if not f or Path(f).suffix not in TEXT:
        continue
    p = repo / f
    if not p.is_file():
        continue
    try:
        s = p.read_text()
    except UnicodeDecodeError:
        continue
    t = p_re.sub(lambda m: path_map[m.group(1)], s)
    t = d_re.sub(lambda m: dot_map[m.group(1)], t)

    def fix_from(m):
        pkg, names = m.group(2), [n.strip() for n in m.group(4).strip("() ").split(",") if n.strip()]
        news = {dot_map.get(f"{pkg}.{n.split(' as ')[0]}", "").rsplit(".", 1)[0] for n in names}
        if news == {""}:
            return m.group(0)
        if len(news) != 1 or "" in news:
            print(f"SPLIT {f}: {m.group(0).strip()}"); return m.group(0)
        return m.group(1) + news.pop() + m.group(3) + m.group(4)
    t = from_re.sub(fix_from, t)
    if t != s:
        changed.append(f)
        if not dry:
            p.write_text(t)
print(f"{len(moves)} moves, {len(changed)} files rewritten")
for f in changed:
    print("  ", f)
