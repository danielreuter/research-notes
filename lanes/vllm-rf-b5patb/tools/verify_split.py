"""Check that a split moved every top-level statement verbatim.

    uvx --python 3.12 python verify_split.py ORIGINAL.py NEW_1.py NEW_2.py ...

For each top-level statement of ORIGINAL other than the docstring and imports: it occurs in exactly one NEW file, with the
same source lines (decorators included) and the same AST.  No NEW file has a top-level statement ORIGINAL lacks (other than
its docstring and imports).  Prints one line per NEW file.
"""
import ast
import sys
from pathlib import Path


def statements(path: Path) -> dict[str, tuple[str, str]]:
    text = path.read_text()
    lines = text.splitlines(keepends=True)
    out = {}
    for s in ast.parse(text).body:
        if isinstance(s, (ast.Import, ast.ImportFrom)) or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)):
            continue
        if isinstance(s, (ast.FunctionDef, ast.ClassDef)):
            name = s.name
        else:
            t = s.targets[0]
            name = ",".join(e.id for e in t.elts) if isinstance(t, ast.Tuple) else t.id
        start = min([s.lineno] + [d.lineno for d in getattr(s, "decorator_list", [])]) - 1
        assert name not in out, f"{path}: {name} defined twice"
        out[name] = ("".join(lines[start:s.end_lineno]), ast.dump(s, include_attributes=False))
    return out


orig = statements(Path(sys.argv[1]))
seen: dict[str, str] = {}
bad = []
for p in map(Path, sys.argv[2:]):
    new = statements(p)
    for name, (src, dump) in new.items():
        if name not in orig:
            bad.append(f"{p.name}: {name} is not in the original")
            continue
        if name in seen:
            bad.append(f"{name} in both {seen[name]} and {p.name}")
        seen[name] = p.name
        if src != orig[name][0]:
            bad.append(f"{p.name}: {name} source differs")
        if dump != orig[name][1]:
            bad.append(f"{p.name}: {name} AST differs")
    print(f"{p.name:16s} {len(new):3d} statements")
missing = sorted(set(orig) - set(seen))
if missing:
    bad.append(f"not moved: {missing}")
print(f"original: {len(orig)} statements; moved: {len(seen)}")
if bad:
    print("\n".join(bad))
    sys.exit(1)
print("OK: every statement moved once, source and AST identical")
