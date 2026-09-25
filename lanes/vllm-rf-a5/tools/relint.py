"""Ratchet-lint report for a worktree without pytest: new violations and stale entries per allowlist.

    uvx --python 3.12 python relint.py WORKTREE [--fix-stale] [--move]

Imports only tests/lint (pure ast + regex; nothing under verity_vllm is imported).  --fix-stale deletes stale entries
and lowers counts (P10: lowers caps to the current size).  --move pairs each new violation with a stale entry of the same
(kind, detail) in the same file (or a renamed file, RENAMES) and moves the entry; the moves are printed.  Anything else
new is only reported.
"""
from __future__ import annotations

import importlib
import json
import sys
from collections import Counter
from pathlib import Path

wt = Path(sys.argv[1]).resolve()
fix = "--fix-stale" in sys.argv
move = "--move" in sys.argv
root = wt / "integrations" / "vllm"
sys.path.insert(0, str(root))
R = importlib.import_module("tests.lint._ratchet")
mods = sorted(p.stem for p in (root / "tests" / "lint").glob("test_p*.py"))
RENAMES = {"verity_vllm/pipeline/cli.py": {"verity_vllm/pipeline/manifest.py"},
           "verity_vllm/target_family.py": {"verity_vllm/config.py"},
           "verity_vllm/check/verdict.py": {"verity_vllm/pipeline/verdict_record.py"},
           "verity_vllm/pipeline/telemetry/admission.py": {"verity_vllm/pipeline/telemetry/admission_commands.py"}}


def rewrite(name: str, keep: dict) -> None:
    path = R.ALLOWLISTS / f"{name}.json"
    data = json.loads(path.read_text())
    order = [(e["file"], e["kind"], e["symbol"], e["detail"]) for e in data["entries"]]
    for k in sorted(set(keep) - set(order)):
        i = next((j for j, o in enumerate(order) if o > k), len(order))
        order.insert(i, k)
    lines = [(k, keep[k]) for k in order if keep.get(k, 0) > 0]
    head = {k: v for k, v in data.items() if k != "entries"}
    out = "{\n" + "".join(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},\n" for k, v in head.items())
    out += '  "entries": [\n' + ",\n".join("    " + R.entry_line(k, n) for k, n in lines) + ("\n" if lines else "") + "  ]\n}\n"
    path.write_text(out)


for m in mods:
    mod = importlib.import_module(f"tests.lint.{m}")
    name = mod.NAME
    viol = list(mod.scan())
    allowed = R.load_allowlist(name)
    if name == "p10_size":
        have = {v.key: v.line for v in viol}
        new = {k: n for k, n in have.items() if k not in allowed or n > allowed[k]}
        stale = {k: have.get(k, 0) for k, n in allowed.items() if have.get(k, 0) < n}
        found = have
    else:
        found = Counter(v.key for v in viol)
        new = {k: n - allowed.get(k, 0) for k, n in found.items() if n > allowed.get(k, 0)}
        stale = {k: found.get(k, 0) for k, n in allowed.items() if found.get(k, 0) < n}
    keep = dict(allowed)
    moved = []
    if move and name != "p10_size":
        for k, extra in sorted(new.items()):
            files = {k[0]} | {src for src, dsts in RENAMES.items() if k[0] in dsts}
            for s in sorted(stale):
                if extra <= 0:
                    break
                if s[0] in files and s[1] == k[1] and s[3] == k[3] and keep[s] > stale[s]:
                    n = min(extra, keep[s] - stale[s])
                    keep[s] -= n
                    keep[k] = keep.get(k, 0) + n
                    extra -= n
                    moved.append((s, k, n))
            new[k] = extra
        new = {k: n for k, n in new.items() if n > 0}
        stale = {k: found.get(k, 0) for k, n in keep.items() if found.get(k, 0) < n}
    print(f"== {name}: {len(new)} new, {len(stale)} stale, {len(moved)} moved")
    for s, k, n in moved:
        print("MOVE", s, "->", k[0], k[2], f"x{n}")
    for k, n in sorted(new.items()):
        print("NEW", k, n, "(allowed", allowed.get(k, 0), ")")
    for k, have in sorted(stale.items()):
        print("STALE", k, keep[k], "->", have)
    if fix:
        keep.update(stale)
    if (fix and stale) or moved:
        rewrite(name, keep)
