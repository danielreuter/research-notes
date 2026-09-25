"""Propose a home (tests/<top package>/) for each test file from the verity_vllm modules it imports.

usage: testhome.py REPO            prints: CUR  PROPOSED  reason
A file whose name is test_<module>.py follows <module>'s package; otherwise the package most imported (by module count).
"""
import ast, collections, sys
from pathlib import Path

repo = Path(sys.argv[1])
vroot = repo / "integrations/vllm"
pkg = vroot / "verity_vllm"
tests = vroot / "tests"
SKIP = {"lint", "regression", "ops", "correspondence"}

mod_pkg = {}
for p in pkg.rglob("*.py"):
    rel = p.relative_to(vroot).with_suffix("")
    parts = rel.parts
    if len(parts) < 2:
        continue
    top = parts[1] if len(parts) > 2 else parts[1].removesuffix("")
    name = parts[-1]
    if name == "__init__":
        continue
    mod_pkg.setdefault(name, set()).add(parts[1] if len(parts) > 2 else parts[1])


def top_of(dotted):
    parts = dotted.split(".")
    if parts[0] != "verity_vllm" or len(parts) < 2:
        return None
    p = pkg / parts[1]
    return parts[1] if p.is_dir() else parts[1].removesuffix(".py")


for f in sorted(tests.rglob("*.py")):
    rel = f.relative_to(tests)
    if len(rel.parts) < 2 or rel.parts[0] in SKIP or f.name == "__init__.py":
        continue
    cur = rel.parts[0]
    try:
        tree = ast.parse(f.read_text())
    except SyntaxError:
        print(f"{rel}\t?\tsyntax"); continue
    counts = collections.Counter()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            t = top_of(n.module)
            if t:
                if n.module.count(".") == 0:
                    for a in n.names:
                        counts[a.name] += 1
                else:
                    counts[t] += 1
        elif isinstance(n, ast.Import):
            for a in n.names:
                t = top_of(a.name)
                if t:
                    counts[t] += 1
    stem = f.stem.removeprefix("test_")
    by_name = None
    for k in range(len(stem), 0, -1):
        cand = stem[:k]
        if cand in mod_pkg and len(mod_pkg[cand]) == 1:
            by_name = next(iter(mod_pkg[cand])); break
    prop = by_name or (counts.most_common(1)[0][0] if counts else cur)
    prop = prop.removesuffix(".py")
    mark = "" if prop == cur else "MOVE"
    print(f"{mark}\t{rel}\t{prop}\tname={by_name} imports={dict(counts.most_common(4))}")
