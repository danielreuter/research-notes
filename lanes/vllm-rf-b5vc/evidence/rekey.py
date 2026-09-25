"""Re-key the lint allowlists after the vllm_bindings split, and report per-rule counts (no pytest; the lints are stdlib).

python3 rekey.py [--write]   (from integrations/vllm)

For each rule: the entries keyed to the old file are dropped and the violations the scan finds in the package are added
at their counts.  Prints the old and new totals per (rule, kind), then every rule's new/stale check over the whole tree.
"""
import importlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, ".")
OLD = "verity_vllm/program/frontend/rules/vllm_bindings.py"
NEW = "verity_vllm/program/frontend/rules/vllm_bindings/"
R = importlib.import_module("tests.lint._ratchet")
RULES = sorted(p.stem for p in Path("tests/lint").glob("test_p*.py"))
write = "--write" in sys.argv
bad = False
for rule in RULES:
    m = importlib.import_module(f"tests.lint.{rule}")
    name = m.NAME
    path = R.ALLOWLISTS / f"{name}.json"
    data = json.loads(path.read_text())
    entries = data["entries"]
    old = [e for e in entries if e["file"] == OLD]
    found = Counter(v.key for v in m.scan() if v.file.startswith(NEW))
    if name == "p10_size":
        found = Counter({v.key: v.line for v in m.scan() if v.file.startswith(NEW)})
    old_kinds = Counter()
    for e in old:
        old_kinds[e["kind"]] += e.get("count", 1)
    new_kinds = Counter()
    for k, n in found.items():
        new_kinds[k[1]] += n
    if old or found:
        print(f"{name}: old {dict(old_kinds)}  new {dict(new_kinds)}")
        for k, n in sorted(found.items()):
            print("   +", R.entry_line(k, n))
    if write and (old or found):
        lines = path.read_text().splitlines(keepends=True)
        idx = [i for i, ln in enumerate(lines) if f'"file": "{OLD}"' in ln]
        add = ["    " + R.entry_line(k, n) + ",\n" for k, n in sorted(found.items())]
        if idx:
            at = idx[0]
            lines = [ln for i, ln in enumerate(lines) if i not in idx]
        else:
            at = next(i for i, ln in enumerate(lines) if ln.strip().startswith('{"file"') and ln > add[0])
        lines[at:at] = add
        # the last entry has no trailing comma
        ents = [i for i, ln in enumerate(lines) if ln.strip().startswith('{"file"')]
        for i in ents[:-1]:
            if not lines[i].rstrip().endswith(","):
                lines[i] = lines[i].rstrip() + ",\n"
        lines[ents[-1]] = lines[ents[-1]].rstrip().rstrip(",") + "\n"
        path.write_text("".join(lines))
        json.loads(path.read_text())
for rule in RULES:
    m = importlib.import_module(f"tests.lint.{rule}")
    for mod in [m]:
        for fn in ("scan",):
            getattr(mod, fn).cache_clear() if hasattr(getattr(mod, fn), "cache_clear") else None
    R.load_allowlist.cache_clear() if hasattr(R.load_allowlist, "cache_clear") else None
    new = R.new_violations(m.NAME, m.scan())
    stale = R.stale_entries(m.NAME, m.scan())
    if m.NAME == "p10_size":
        caps = R.load_allowlist(m.NAME)
        sizes = m.sizes()
        new = [k for k, n in sizes.items() if k not in caps or n > caps[k]]
        stale = [k for k, n in caps.items() if sizes.get(k) != n]
    print(f"{m.NAME}: new {len(new)} stale {len(stale)}")
    for x in list(new)[:10] + list(stale)[:10]:
        print("    ", x)
    bad |= bool(new or stale)
print("LINTS-OK" if not bad else "LINTS-FAIL")
