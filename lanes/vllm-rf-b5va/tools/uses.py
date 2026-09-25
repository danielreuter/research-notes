"""List every use of `verity_vllm.engine.vllm_adapter` names across the tree (stdlib only; no verity_vllm import).

    uvx --python 3.12 python uses.py WORKTREE

For each Python file under integrations/, packages/ and tools/: the aliases bound to the module (`import ... as X`,
`from verity_vllm.engine import vllm_adapter as X`), every `X.name` attribute read, every `from ...vllm_adapter import
name`, and every string that names `verity_vllm.engine.vllm_adapter.<name>` (monkeypatch / mock targets).
"""
import ast
import re
import sys
from collections import defaultdict
from pathlib import Path

MOD = "verity_vllm.engine.vllm_adapter"
root = Path(sys.argv[1])
per_file: dict[str, set[str]] = defaultdict(set)
aliases_of: dict[str, set[str]] = defaultdict(set)
for top in ("integrations", "packages", "tools"):
    for p in sorted((root / top).rglob("*.py")):
        rel = str(p.relative_to(root))
        if rel.endswith("engine/vllm_adapter.py"):
            continue
        try:
            text = p.read_text()
            tree = ast.parse(text)
        except (SyntaxError, UnicodeDecodeError):
            continue
        aliases: set[str] = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    if a.name == MOD:
                        aliases.add(a.asname or a.name)
            elif isinstance(n, ast.ImportFrom):
                if n.module == "verity_vllm.engine":
                    for a in n.names:
                        if a.name == "vllm_adapter":
                            aliases.add(a.asname or a.name)
                elif n.module == MOD:
                    for a in n.names:
                        per_file[rel].add(f"from-import:{a.name}")
        for n in ast.walk(tree):
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in aliases:
                per_file[rel].add(n.attr)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("getattr", "setattr", "hasattr") \
                    and n.args and isinstance(n.args[0], ast.Name) and n.args[0].id in aliases:
                per_file[rel].add(f"{n.func.id}:{ast.unparse(n.args[1]) if len(n.args) > 1 else '?'}")
            elif isinstance(n, ast.Name) and n.id in aliases and not isinstance(getattr(n, "ctx", None), ast.Store):
                pass
        for m in re.finditer(re.escape(MOD) + r"\.(\w+)", text):
            per_file[rel].add(f"string:{m.group(1)}")
        if aliases:
            aliases_of[rel] = aliases
        # bare alias passed around (e.g. monkeypatch.setattr(va, "x", ...) or a function receiving the module)
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                for a in n.args:
                    if isinstance(a, ast.Name) and a.id in aliases:
                        per_file[rel].add(f"module-passed-to:{ast.unparse(n.func)}")
allnames: dict[str, set[str]] = defaultdict(set)
for f, names in sorted(per_file.items()):
    print(f"{f}  aliases={sorted(aliases_of.get(f, []))}")
    print("   ", ", ".join(sorted(names)))
    for nm in names:
        allnames[nm].add(f)
print("\n== by name ==")
for nm, fs in sorted(allnames.items()):
    print(f"{nm:40s} {len(fs)}  {', '.join(sorted(Path(x).name for x in fs))}")
