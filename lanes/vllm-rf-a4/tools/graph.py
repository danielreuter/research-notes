"""Import graph of integrations/vllm/verity_vllm (pure ast; imports nothing from the package).

Mirrors tests/lint/_imports.py edge semantics so a move map can be checked before files move.
usage: python graph.py REPO [who MODULE | deps MODULE | layers]
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

SKIP_DIRS = {"__pycache__", "tests"}


def library_files(pkg: Path) -> list[Path]:
    out = []
    for p in sorted(pkg.rglob("*.py")):
        parts = p.relative_to(pkg).parts
        if any(d in SKIP_DIRS for d in parts[:-1]) or parts[-1].startswith("test_") or parts[-1].startswith("._"):
            continue
        out.append(p)
    return out


def module_name(p: Path, pkg: Path) -> str:
    parts = list(p.relative_to(pkg.parent).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def dynamic_module(node):
    if isinstance(node, ast.Call):
        f = node.func
        fn = ast.unparse(f) if isinstance(f, (ast.Name, ast.Attribute)) else ""
        if fn in ("importlib.import_module", "import_module", "__import__", "sys.modules.get") and node.args \
                and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            return node.args[0].value
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) and ast.unparse(node.value) == "sys.modules" \
            and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
        return node.slice.value
    return None


def resolve(target: str, known) -> str | None:
    parts = target.split(".")
    for i in range(len(parts), 0, -1):
        c = ".".join(parts[:i])
        if c in known:
            return c
    return None


def edges(pkg: Path):
    files = library_files(pkg)
    known = {module_name(p, pkg): p for p in files}
    out = []
    for p in files:
        mod = module_name(p, pkg)
        is_pkg = p.name == "__init__.py"
        pk = mod if is_pkg else mod.rpartition(".")[0]
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Import):
                targets = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:
                    anchor = pk.split(".")[: len(pk.split(".")) - node.level + 1]
                    base = ".".join([*anchor, *([base] if base else [])])
                targets = [f"{base}.{a.name}" if f"{base}.{a.name}" in known else base for a in node.names]
            else:
                lit = dynamic_module(node)
                if lit:
                    targets = [lit]
            for t in targets:
                if not (t == "verity_vllm" or t.startswith("verity_vllm.")):
                    continue
                d = resolve(t, known)
                if d and d != mod:
                    out.append((mod, d, str(p.relative_to(pkg.parent.parent)) if False else str(p), getattr(node, "lineno", 0)))
    return known, out


def sccs(nodes, adj):
    index, low, on, stack, out = {}, {}, set(), [], []
    counter = 0
    for root in sorted(nodes):
        if root in index:
            continue
        work = [(root, iter(sorted(adj.get(root, ()))))]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on.add(root)
        while work:
            v, it = work[-1]
            adv = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    on.add(w)
                    work.append((w, iter(sorted(adj.get(w, ())))))
                    adv = True
                    break
                if w in on:
                    low[v] = min(low[v], index[w])
            if adv:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1:
                    out.append(sorted(comp))
    return sorted(out)


def package_of(m: str) -> str:
    parts = m.split(".")
    return parts[1] if len(parts) > 1 else parts[0]


def package_cycles(es):
    pairs = set()
    for a, b, *_ in es:
        pa, pb = package_of(a), package_of(b)
        if pa != pb and "verity_vllm" not in (pa, pb):
            pairs.add((pa, pb))
    return sorted(f"{a} <-> {b}" for a, b in pairs if a < b and (b, a) in pairs)


def main():
    repo = Path(sys.argv[1])
    pkg = repo / "integrations/vllm/verity_vllm"
    known, es = edges(pkg)
    cmd = sys.argv[2] if len(sys.argv) > 2 else "summary"
    if cmd == "who":
        m = sys.argv[3]
        for a, b, f, ln in sorted(set(es)):
            if b == m or b.startswith(m + "."):
                print(f"{a} -> {b}  ({Path(f).name}:{ln})")
    elif cmd == "deps":
        m = sys.argv[3]
        for a, b, f, ln in sorted(set(es)):
            if a == m or a.startswith(m + "."):
                print(f"{a} -> {b}  ({Path(f).name}:{ln})")
    else:
        print(len(known), "modules", len({(a, b) for a, b, *_ in es}), "edges")
        for c in package_cycles(es):
            print("pkg-cycle", c)
        adj = {}
        for a, b, *_ in es:
            adj.setdefault(a, set()).add(b)
        for c in sccs(set(known), adj):
            print("scc", " <-> ".join(x.removeprefix("verity_vllm.") for x in c))


if __name__ == "__main__":
    main()
