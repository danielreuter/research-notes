"""Static check: every verity_vllm import (and dotted verity_vllm.* string) in tracked Python resolves to a module in the tree.

usage: python resolve.py REPO
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

DOTTED = re.compile(r"(?<![\w.])(?:integrations\.vllm\.)?(verity_vllm(?:\.\w+)+)")


def main():
    repo = Path(sys.argv[1]).resolve()
    integ = repo / "integrations/vllm"
    files = subprocess.run(["git", "-C", str(repo), "ls-files", "-co", "--exclude-standard", "integrations/vllm", "tools/research",
                            "packages/verity/src"], capture_output=True, text=True, check=True).stdout.split()
    mods = set()
    for f in files:
        if f.startswith("integrations/vllm/verity_vllm/") and f.endswith(".py") and (repo / f).exists():
            parts = Path(f).relative_to("integrations/vllm").with_suffix("").parts
            parts = list(parts[:-1]) if parts[-1] == "__init__" else list(parts)
            mods.add(".".join(parts))
            for i in range(1, len(parts)):
                mods.add(".".join(parts[:i]))   # namespace dirs count as importable
    tests = set()
    for f in files:
        if f.startswith("integrations/vllm/tests/") and f.endswith(".py") and (repo / f).exists():
            parts = list(Path(f).relative_to("integrations/vllm").with_suffix("").parts)
            if parts[-1] == "__init__":
                parts.pop()
            tests.add(".".join(parts))
    defs: dict[str, set[str]] = {}

    def names_in(mod):
        if mod in defs:
            return defs[mod]
        p = integ / (mod.replace(".", "/") + ".py")
        if not p.exists():
            p = integ / mod.replace(".", "/") / "__init__.py"
        out = set()
        if p.exists():
            t = ast.parse(p.read_text())
            for n in ast.walk(t):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    out.add(n.name)
                elif isinstance(n, ast.Assign):
                    for tg in n.targets:
                        for x in ast.walk(tg):
                            if isinstance(x, ast.Name):
                                out.add(x.id)
                elif isinstance(n, (ast.AnnAssign, ast.AugAssign)) and isinstance(n.target, ast.Name):
                    out.add(n.target.id)
                elif isinstance(n, (ast.Import, ast.ImportFrom)):
                    for a in n.names:
                        out.add((a.asname or a.name).split(".")[0])
        defs[mod] = out
        return out

    bad = 0
    for f in files:
        if not f.endswith(".py") or not (repo / f).exists():
            continue
        src = (repo / f).read_text(encoding="utf-8", errors="replace")
        if "verity_vllm" not in src and "from tests" not in src and "import tests" not in src:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            print(f"SYNTAX {f}: {e}")
            bad += 1
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                m = n.module.removeprefix("integrations.vllm.")
                if m.split(".")[0] == "verity_vllm":
                    if m not in mods:
                        print(f"MISSING {f}:{n.lineno} from {m}")
                        bad += 1
                        continue
                    for a in n.names:
                        if a.name != "*" and f"{m}.{a.name}" not in mods and a.name not in names_in(m):
                            print(f"NONAME {f}:{n.lineno} from {m} import {a.name}")
                            bad += 1
                elif m.split(".")[0] == "tests":
                    if m not in tests and m != "tests":
                        print(f"MISSING-TEST {f}:{n.lineno} from {m}")
                        bad += 1
                        continue
                    for a in n.names:
                        if f"{m}.{a.name}" not in tests and a.name not in names_in(m):
                            print(f"NONAME-TEST {f}:{n.lineno} from {m} import {a.name}")
                            bad += 1
            elif isinstance(n, ast.Import):
                for a in n.names:
                    m = a.name.removeprefix("integrations.vllm.")
                    if m.split(".")[0] == "verity_vllm" and m not in mods:
                        print(f"MISSING {f}:{n.lineno} import {m}")
                        bad += 1
                    if m.split(".")[0] == "tests" and m not in tests and m != "tests":
                        print(f"MISSING-TEST {f}:{n.lineno} import {m}")
                        bad += 1
            elif isinstance(n, ast.Constant) and isinstance(n.value, str) and "verity_vllm." in n.value:
                for mm in DOTTED.finditer(n.value):
                    name = mm.group(1)
                    parts = name.split(".")
                    if len(parts) > 1 and parts[1] in ("harness", "tp", "input_provenance", "build_paths"):
                        print(f"STALE-STR {f}:{n.lineno} {name}")
                        bad += 1
                    elif parts[1] not in {x.split(".")[1] for x in mods if "." in x}:
                        print(f"UNKNOWN-STR {f}:{n.lineno} {name}")
    print("problems:", bad)


if __name__ == "__main__":
    main()
