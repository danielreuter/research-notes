"""arith: the ordered kernel sequence of one tests-graph replay in a prof.py trace (name, grid, block, duration).

    python seq.py TRACE.json.gz [KIND=tests] [INDEX=3]
"""
import gzip
import json
import sys
from collections import defaultdict

tr = json.load(gzip.open(sys.argv[1]))
kind = sys.argv[2] if len(sys.argv) > 2 else "tests"
idx = int(sys.argv[3]) if len(sys.argv) > 3 else 3
MARK = {"tests": "quad_", "commit": "witness_program", "hints": "hints_fused"}[kind]
groups = defaultdict(list)
for e in tr["traceEvents"]:
    if e.get("ph") == "X" and e.get("cat") in ("kernel", "gpu_memcpy", "gpu_memset"):
        groups[(e.get("args") or {}).get("correlation")].append(e)
sel = [ks for ks in groups.values() if any(MARK in k["name"] for k in ks)]
sel.sort(key=lambda ks: min(k["ts"] for k in ks))
ks = sorted(sel[idx], key=lambda k: k["ts"])
t0 = ks[0]["ts"]
tot = 0.0
for k in ks:
    a = k.get("args") or {}
    d = k.get("dur", 0.0)
    tot += d
    print(f"{k['ts'] - t0:8.1f} {d:7.1f}us grid={a.get('grid')} blk={a.get('block')} {k['name'][:110]}")
print(f"n={len(ks)} sum={tot:.1f}us span={ks[-1]['ts'] + ks[-1].get('dur', 0) - t0:.1f}us")
