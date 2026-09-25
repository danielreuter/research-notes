"""List every Definition registered with a literal name/version in the integration and in core (AST only; imports nothing).

usage: python defs_inventory.py TREE > inventory.tsv
"""
import ast
import sys
from pathlib import Path

CALLS = {"primitive", "composite", "PrimitiveDefinition", "CompositeDefinition"}


def scan(root: Path, base: Path):
    for p in sorted(root.rglob("*.py")):
        if any(part in {"tests", "__pycache__"} for part in p.relative_to(base).parts):
            continue
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            fn = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else ""
            if fn not in CALLS or len(node.args) < 2:
                continue
            a0, a1 = node.args[0], node.args[1]
            if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                name = a0.value
            elif isinstance(a0, ast.JoinedStr):
                name = "f:" + ast.unparse(a0)
            else:
                name = "?:" + ast.unparse(a0)
            ver = a1.value if isinstance(a1, ast.Constant) else "?:" + ast.unparse(a1)
            reg = not any(k.arg == "register" and isinstance(k.value, ast.Constant) and k.value.value is False
                          for k in node.keywords)
            kind = "prim" if fn in ("primitive", "PrimitiveDefinition") else "comp"
            yield p.relative_to(base).as_posix(), node.lineno, kind, name, ver, reg


def main():
    tree = Path(sys.argv[1])
    roots = [(tree / "integrations/vllm/verity_vllm", tree / "integrations/vllm"),
             (tree / "packages/verity/src/verity", tree / "packages/verity/src")]
    for root, base in roots:
        for rel, line, kind, name, ver, reg in scan(root, base):
            print(f"{rel}\t{line}\t{kind}\t{name}\t{ver}\t{'reg' if reg else 'noreg'}")


main()
