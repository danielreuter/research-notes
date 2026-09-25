"""Report `"verity_vllm" / "a" / "b" ...` literal chains (pathlib or os.path.join) that name no existing path.

usage: python segcheck.py REPO
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


def chain(node: ast.AST) -> list[str] | None:
    """Flatten a / b / c of string constants (leading non-constant allowed); None when a later part is not a constant."""
    parts: list[str] = []
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        if not (isinstance(node.right, ast.Constant) and isinstance(node.right.value, str)):
            return None
        parts.append(node.right.value)
        node = node.left
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        parts.append(node.value)
    return list(reversed(parts))


def main() -> None:
    repo = Path(sys.argv[1]).resolve()
    root = repo / "integrations/vllm"
    files = subprocess.run(["git", "-C", str(repo), "ls-files", "integrations/vllm", "tools/research"], check=True,
                           capture_output=True, text=True).stdout.splitlines()
    for f in files:
        if not f.endswith(".py"):
            continue
        try:
            tree = ast.parse((repo / f).read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            segs = None
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                segs = chain(node)
            elif isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "join":
                segs = [a.value for a in node.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
                if len(segs) != len(node.args) - 1 and len(segs) != len(node.args):
                    segs = None
            if not segs or "verity_vllm" not in segs:
                continue
            tail = segs[segs.index("verity_vllm"):]
            if len(tail) < 2:
                continue
            rel = "/".join(tail)
            if not (root / rel).exists():
                print(f"{f}:{node.lineno}: {rel}")


if __name__ == "__main__":
    main()
