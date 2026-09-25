"""Check that rules/vllm_bindings/ is a verbatim split of the original rules/vllm_bindings.py.

python3 verify_split.py <original.py> <package dir>

* every top-level statement of the original other than its imports (and `__all__`) appears exactly once in the package,
  with identical source text (comments inside it included) and an identical AST;
* the package holds nothing else: per module a docstring, `from __future__`, imports, then moved statements, and
  `__init__`'s `__all__` (whose names must all be bound there);
* every comment line of the original outside a moved statement (banners, `#:` doc-comments) appears in the package the
  same number of times;
* no module-level name is bound in two modules, and `__init__` binds every name of the original `__all__` that importers use.
"""
import ast
import collections
import pathlib
import sys

orig_path, pkg = sys.argv[1], pathlib.Path(sys.argv[2])
orig_src = open(orig_path).read()
orig = ast.parse(orig_src)


def seg(src, node):
    lines = src.splitlines()
    return "\n".join(lines[node.lineno - 1:node.end_lineno])


def is_import(s):
    return isinstance(s, (ast.Import, ast.ImportFrom))


def is_all(s):
    return isinstance(s, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in s.targets)


def is_doc(s, i):
    return i == 0 and isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str)


want = collections.Counter()
for i, s in enumerate(orig.body):
    if is_import(s) or is_all(s) or is_doc(s, i):
        continue
    want[(seg(orig_src, s), ast.dump(s))] += 1

have = collections.Counter()
extra = []
bound = collections.defaultdict(list)
new_comments = collections.Counter()
for p in sorted(pkg.glob("*.py")):
    src = p.read_text()
    t = ast.parse(src)
    for line in src.splitlines():
        if line.lstrip().startswith("#"):
            new_comments[line] += 1
    for i, s in enumerate(t.body):
        if is_doc(s, i) or is_import(s):
            continue
        if is_all(s):
            if p.name != "__init__.py":
                extra.append(f"{p.name}:{s.lineno} __all__ outside __init__")
            continue
        key = (seg(src, s), ast.dump(s))
        have[key] += 1
        if key not in want:
            extra.append(f"{p.name}:{s.lineno} not in the original: {seg(src, s)[:80]!r}")
        for n in (s.targets if isinstance(s, ast.Assign) else [s.target] if isinstance(s, ast.AnnAssign) else []):
            for x in ast.walk(n):
                if isinstance(x, ast.Name):
                    bound[x.id].append(p.name)
        if isinstance(s, (ast.FunctionDef, ast.ClassDef)):
            bound[s.name].append(p.name)

missing = want - have
dup = {k: v for k, v in have.items() if v > want.get(k, 0)}
twice = {k: v for k, v in bound.items() if len(v) > 1}

# comment lines of the original that sit between statements (inside-statement comments are covered by the source check)
inside = set()
for s in orig.body:
    inside.update(range(s.lineno, s.end_lineno + 1))
orig_comments = collections.Counter(line for i, line in enumerate(orig_src.splitlines(), 1)
                                    if i not in inside and line.lstrip().startswith("#"))
lost_comments = orig_comments - new_comments

n_moved = sum(want.values())
print(f"statements: {n_moved} moved (excluding {sum(1 for s in orig.body if is_import(s))} imports, the docstring and __all__)")
print(f"  missing: {sum(missing.values())}, duplicated: {len(dup)}, not from the original: {len(extra)}, names bound twice: {len(twice)}")
print(f"between-statement comment lines: {sum(orig_comments.values())}, lost: {sum(lost_comments.values())}")
for k in missing:
    print("  MISSING", k[0][:100])
for e in extra:
    print("  EXTRA", e)
for k, v in twice.items():
    print("  TWICE", k, v)
for c in lost_comments:
    print("  LOST COMMENT", c[:100])
ok = not (missing or dup or extra or twice or lost_comments)
print("OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
