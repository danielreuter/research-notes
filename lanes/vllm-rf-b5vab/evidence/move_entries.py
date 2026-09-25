"""Move allowlist entries of engine/vllm_adapter.py to the module their code moved to (lintdiff output as input): the entry's
own line with only its "file" value changed, re-placed in sorted (file, kind, symbol, detail) order; the P10 module entry is deleted."""
import json
import re
import sys
from pathlib import Path

ALLOW = Path("tests/lint/allowlists")
OLD = "verity_vllm/engine/vllm_adapter.py"
diff = Path(sys.argv[1]).read_text().splitlines()
rule = None
adds, dels = {}, {}
for ln in diff:
    m = re.match(r"^(p\d\d_\w+): entries", ln)
    if m:
        rule = m.group(1)
        continue
    m = re.match(r"^\s+(ADD/RAISE|DEL/LOWER) (\{.*\})\s+\((allowed|found) \d+\)$", ln)
    if m:
        (adds if m.group(1) == "ADD/RAISE" else dels).setdefault(rule, []).append(json.loads(m.group(2)))


def rest(e):
    det = re.sub(r"^engine\.\w+ -> ", "", e["detail"]) if e["kind"] == "layer" else e["detail"]
    return (e["kind"], e["symbol"], det, e.get("count", 1))


for rule in sorted(set(adds) | set(dels)):
    a, d = adds.get(rule, []), dels.get(rule, [])
    assert all(e["file"] == OLD for e in d)
    target = {rest(e): e["file"] for e in a}
    if rule == "p10_size":
        assert not a and len(d) == 1
    else:
        assert sorted(map(rest, a)) == sorted(map(rest, d)) and len(target) == len(a), rule
    p = ALLOW / f"{rule}.json"
    lines = p.read_text().splitlines()
    idx = [i for i, l in enumerate(lines) if l.strip().startswith('{"file"')]
    assert idx == list(range(idx[0], idx[-1] + 1)), rule
    raw = [lines[i].rstrip().rstrip(",") for i in idx]
    ents = [json.loads(r) for r in raw]
    key = lambda e: (e["file"], e["kind"], e["symbol"], e["detail"])  # noqa: E731
    was_sorted = ents == sorted(ents, key=key)
    out = []
    for r, e in zip(raw, ents):
        if e["file"] == OLD and rest(e) in {rest(x) for x in d}:
            if rule == "p10_size":
                continue
            new_file = target[rest(e)]
            r = r.replace(f'"file": "{OLD}"', f'"file": "{new_file}"', 1)
            if e["kind"] == "layer":
                r = r.replace('"detail": "engine.vllm_adapter -> ', '"detail": "engine.' + Path(new_file).stem + ' -> ', 1)
            e = json.loads(r)
        out.append((e, r))
    if was_sorted:
        out.sort(key=lambda t: key(t[0]))
    body = [r + ("," if i < len(out) - 1 else "") for i, (_, r) in enumerate(out)]
    p.write_text("\n".join(lines[:idx[0]] + body + lines[idx[-1] + 1:]) + "\n")
    print(rule, "sorted" if was_sorted else "UNSORTED", len(ents), "->", len(out))
