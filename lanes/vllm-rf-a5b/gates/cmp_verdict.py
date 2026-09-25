"""Compare two row dirs' verdict.json: the fields of record, then every check's outcome, then what else differs.
   usage: python3 cmp_verdict.py BASE_ROW_DIR HEAD_ROW_DIR"""
import json
import sys
from pathlib import Path

RECORD = ("outcome", "program_digest", "manifest_digest", "run_roots", "query_id", "correspondence_digest", "correspondence_digests")


def checks(v):
    c = v.get("checks")
    if isinstance(c, dict):
        return {k: (x.get("outcome") if isinstance(x, dict) else x) for k, x in c.items()}
    if isinstance(c, list):
        return {x.get("id") or x.get("name"): x.get("outcome") for x in c if isinstance(x, dict)}
    return {}


def walk(p, u, v, out):
    if isinstance(u, dict) and isinstance(v, dict):
        for k in sorted(set(u) | set(v)):
            walk(f"{p}.{k}", u.get(k), v.get(k), out)
    elif u != v:
        out.append((p, str(u)[:120], str(v)[:120]))


a, b = (json.loads((Path(d) / "verdict.json").read_text()) for d in sys.argv[1:3])
bad = 0
for k in RECORD:
    same = a.get(k) == b.get(k)
    bad += not same
    print(f"{k}: {'EQUAL' if same else 'DIFFERENT'} {str(a.get(k))[:100]}" + ("" if same else f" -> {str(b.get(k))[:100]}"))
ca, cb = checks(a), checks(b)
diff = {k: (ca.get(k), cb.get(k)) for k in sorted(set(ca) | set(cb), key=str) if ca.get(k) != cb.get(k)}
bad += bool(diff)
print(f"checks: {len(ca)} base, {len(cb)} head, outcome differs on {len(diff)}", diff or "")
out = []
for k in sorted(set(a) | set(b)):
    if k not in RECORD and k != "checks":
        walk(k, a.get(k), b.get(k), out)
print(f"other differing leaves: {len(out)}")
for o in out[:40]:
    print("  ", *o, sep="\n     ")
print("RESULT", "SAME-OF-RECORD" if not bad else "DIFFERENT")
sys.exit(1 if bad else 0)
