"""Decide which test files follow their subject module into a new package (test file moves only).

usage: testmoves.py REPO BASE     prints: SRC  DST  reason
A test moves when its directory is no longer a package (harness, input_provenance, tp), or when its subject moved out of
the package its directory names. Subject: the moved module whose old stem the file name starts with; otherwise, the
verity_vllm modules it imports, when more of them moved out (all to one package) than stayed.
"""
import ast, collections, subprocess, sys
from pathlib import Path

repo, base = Path(sys.argv[1]), sys.argv[2]
V = "integrations/vllm/"
tests = repo / V / "tests"
GONE = {"harness", "input_provenance", "tp"}
SKIP = {"lint", "regression", "ops"}

out = subprocess.run(["git", "-C", str(repo), "diff", "-M", "--name-status", base, "HEAD", "--", V + "verity_vllm"],
                     capture_output=True, text=True, check=True).stdout
new2old, oldstem = {}, {}


def dotted(path):
    p = path.removeprefix(V).removesuffix(".py")
    p = p.removesuffix("/__init__")
    return p.replace("/", ".")


def top(mod):
    parts = mod.split(".")
    return "(top)" if len(parts) == 2 else parts[1]


for line in out.splitlines():
    f = line.split("\t")
    if f[0].startswith("R") and f[1].endswith(".py"):
        o, n = dotted(f[1]), dotted(f[2])
        new2old[n] = o
        if top(o) != top(n):
            oldstem.setdefault(o.rsplit(".", 1)[1], set()).add((top(o), top(n)))


def imports(tree):
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and n.level == 0 and n.module.startswith("verity_vllm"):
            base = repo / V / n.module.replace(".", "/")
            subs = [a.name for a in n.names if (base / f"{a.name}.py").is_file() or (base / a.name).is_dir()]
            if subs:
                yield from (f"{n.module}.{s}" for s in subs)
            else:
                yield n.module
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name.startswith("verity_vllm."):
                    yield a.name


for f in sorted(tests.rglob("*.py")):
    rel = f.relative_to(tests)
    if len(rel.parts) < 2 or rel.parts[0] in SKIP or f.name == "__init__.py":
        continue
    d = rel.parts[0]
    mods = set(imports(ast.parse(f.read_text())))
    stayed, moved = 0, collections.Counter()
    for m in mods:
        o = new2old.get(m, m)
        if top(o) == d and top(m) != d:
            moved[top(m)] += 1
        elif top(m) == d:
            stayed += 1
    stem = f.stem.removeprefix("test_")
    hit = None
    for k in range(len(stem), 2, -1):
        c = {t for (s, t) in oldstem.get(stem[:k], ()) if s == d}
        if len(c) == 1 and (k == len(stem) or stem[k] == "_"):
            hit = (next(iter(c)), f"name:{stem[:k]}"); break
    if hit is None and len(moved) == 1 and sum(moved.values()) > stayed:
        hit = (next(iter(moved)), f"imports moved={dict(moved)} stayed={stayed}")
    if hit is None and d in GONE:
        hit = ("?", f"gone dir; imports={sorted(mods)}")
    if hit:
        print(f"{rel}\t{hit[0]}\t{hit[1]}")
