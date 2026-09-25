"""Check that the engine/vllm_adapter.py split moved every top-level statement verbatim.

usage: verify_split.py <original vllm_adapter.py> <engine dir>

1. Every non-import top-level statement of the original (with its attached leading comments) appears exactly once in the new
   modules, with identical source lines and an identical AST.
2. The new modules contain no other top-level statement (only docstrings, imports and the moved statements).
3. Every global name each new module reads is bound at its top level or is a builtin (symtable, all scopes).
4. Every name the original module bound at top level that is not bound in the new vllm_adapter is listed (the facade's gaps).
"""
import ast
import builtins
import symtable
import sys
from pathlib import Path

MODULES = ("vllm_adapter", "build", "code_identity", "run_facts", "pinned", "capture")


def stmt_names(n):
    if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
        return [n.name]
    if isinstance(n, ast.Assign):
        return [t.id for t in n.targets]
    if isinstance(n, ast.AnnAssign):
        return [n.target.id]
    return None


def bound(tree):
    out = set()
    for n in tree.body:
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            out |= {(a.asname or a.name).split(".")[0] for a in n.names}
        elif stmt_names(n):
            out |= set(stmt_names(n))
    return out


def segments(src):
    lines = src.splitlines()
    tree = ast.parse(src)
    out, prev_end = {}, 0
    for n in tree.body:
        names = stmt_names(n)
        start = min([n.lineno] + [d.lineno for d in getattr(n, "decorator_list", [])])
        if names is None:
            if not (isinstance(n, (ast.Import, ast.ImportFrom)) or (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))):
                raise SystemExit(f"unexpected top-level statement at line {n.lineno}: {ast.dump(n)[:120]}")
            prev_end = n.end_lineno
            continue
        s = start
        while s - 2 >= 0 and lines[s - 2].startswith("#") and s - 1 > prev_end:
            s -= 1
        out[tuple(names)] = ("\n".join(lines[s - 1:n.end_lineno]), ast.dump(n, include_attributes=False))
        prev_end = n.end_lineno
    return out, tree


def global_reads(src, name):
    reads = set()
    def walk(t):
        for s in t.get_symbols():
            if (s.is_global() or (t.get_type() == "module" and s.is_referenced())) and s.is_referenced():
                reads.add(s.get_name())
        for c in t.get_children():
            walk(c)
    walk(symtable.symtable(src, name, "exec"))
    return reads


def main():
    orig_src = Path(sys.argv[1]).read_text()
    eng = Path(sys.argv[2])
    orig, orig_tree = segments(orig_src)
    new = {}
    bad = 0
    for m in MODULES:
        src = (eng / f"{m}.py").read_text()
        segs, tree = segments(src)
        for k, v in segs.items():
            if k in new:
                print(f"DUPLICATE {k} in {m} and {new[k][0]}"); bad += 1
            new[k] = (m, v)
        missing = sorted(global_reads(src, m) - bound(tree) - set(dir(builtins)) - {"__file__", "__name__"})
        if missing:
            print(f"UNBOUND in {m}: {missing}"); bad += 1
        print(f"{m}: {len(src.splitlines())} lines, {len(segs)} moved statements")
    for k, (text, dump) in orig.items():
        if k not in new:
            print(f"MISSING {k}"); bad += 1
            continue
        m, (t2, d2) = new[k]
        if t2 != text:
            print(f"SOURCE DIFFERS {k} in {m}"); bad += 1
        if d2 != dump:
            print(f"AST DIFFERS {k} in {m}"); bad += 1
    for k in new:
        if k not in orig:
            print(f"EXTRA {k} in {new[k][0]}"); bad += 1
    facade = bound(ast.parse((eng / "vllm_adapter.py").read_text()))
    gaps = sorted(bound(orig_tree) - facade)
    print(f"{len(orig)} statements checked; {bad} problem(s)")
    print(f"original top-level names not bound in the new vllm_adapter ({len(gaps)}): {' '.join(gaps)}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
