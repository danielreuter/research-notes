"""sp1-table (pod): per-VU opcode deltas between two exec_cmp outputs.  opdiff.py A.json B.json [VUS]"""

import json
import sys

vus = int(sys.argv[3]) if len(sys.argv) > 3 else 4096
a, b = (json.load(open(p)) for p in sys.argv[1:3])
a, b = ((d.get("execute") or d) for d in (a, b))
oa, ob = a.get("opcodes", {}), b.get("opcodes", {})
print(f"cycles/VU {a['total_cycles'] / vus:,.0f} -> {b['total_cycles'] / vus:,.0f}   gas {a['gas']:,} -> {b['gas']:,}")
for k in sorted(set(oa) | set(ob), key=lambda k: -(oa.get(k, 0))):
    x, y = oa.get(k, 0) / vus, ob.get(k, 0) / vus
    if abs(x - y) >= 1:
        print(f"  {k:6s} {x:8,.0f} -> {y:8,.0f}  ({y - x:+,.0f})")
