"""Ratchet-lint report for a worktree without pytest: new violations and stale entries per allowlist.

    uvx --python 3.12 python relint.py WORKTREE [--fix-stale]

Imports only tests/lint (pure ast + regex; nothing under verity_vllm is imported).  --fix-stale deletes stale entries
and lowers counts (P10: lowers caps to the current size); new violations are only reported.
"""
from __future__ import annotations

import importlib
import json
import sys
from collections import Counter
from pathlib import Path

wt = Path(sys.argv[1]).resolve()
fix = "--fix-stale" in sys.argv
root = wt / "integrations" / "vllm"
sys.path.insert(0, str(root))
R = importlib.import_module("tests.lint._ratchet")
mods = sorted(p.stem for p in (root / "tests" / "lint").glob("test_p*.py"))


def rewrite(name: str, keep: dict) -> None:
    path = R.ALLOWLISTS / f"{name}.json"
    data = json.loads(path.read_text())
    lines = []
    for e in data["entries"]:
        k = (e["file"], e["kind"], e["symbol"], e["detail"])
        if k in keep and keep[k] > 0:
            lines.append("    " + R.entry_line(k, keep[k]))
    head = {k: v for k, v in data.items() if k != "entries"}
    out = "{\n" + "".join(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},\n" for k, v in head.items())
    out += '  "entries": [\n' + ",\n".join(lines) + ("\n" if lines else "") + "  ]\n}\n"
    path.write_text(out)


for m in mods:
    mod = importlib.import_module(f"tests.lint.{m}")
    name = mod.NAME
    viol = list(mod.scan())
    allowed = R.load_allowlist(name)
    if name == "p10_size":
        have = {v.key: v.line for v in viol}
        new = [f"  {k} {n} (cap {allowed.get(k)})" for k, n in sorted(have.items()) if k not in allowed or n > allowed[k]]
        stale = {k: have.get(k, 0) for k, n in allowed.items() if have.get(k, 0) < n}
    else:
        found = Counter(v.key for v in viol)
        lines = {}
        for v in viol:
            lines.setdefault(v.key, []).append(v.line)
        new = [f"  {k} x{n} (allowed {allowed.get(k, 0)}) lines {sorted(lines[k])}" for k, n in sorted(found.items())
               if n > allowed.get(k, 0)]
        stale = {k: found.get(k, 0) for k, n in allowed.items() if found.get(k, 0) < n}
    print(f"== {name}: {len(new)} new, {len(stale)} stale")
    for ln in new:
        print("NEW", ln)
    for k, have in sorted(stale.items()):
        print("STALE", k, allowed[k], "->", have)
    if fix and stale:
        keep = dict(allowed)
        keep.update(stale)
        rewrite(name, keep)
