"""ab.py DIR REL [REL...]: task 1 A/B table from bench_<rel>_<base|lane>_r<N>.json (--zk rounds only: r3 is the no-ZK round).
Per tree: the per-run t.total / t.encoding_commitment / t.arithmetic medians, their median over the rounds, and the paired
lane - base difference per round (same round = adjacent runs)."""
import glob
import json
import re
import statistics as st
import sys

d = sys.argv[1]
for rel in sys.argv[2:]:
    runs: dict = {}
    for f in glob.glob(f"{d}/bench_{rel}_*_r*.json"):
        m = re.search(rf"bench_{re.escape(rel)}_(base|lane)_r(\d+)\.json$", f)
        if not m:
            continue
        j = json.load(open(f))
        meas = {x["name"]: x["value"] for x in j["measurements"]}
        zk = j["validation"]["evidence"]["soundness"]["zk"]
        runs[(m.group(1), int(m.group(2)))] = (zk, meas, j["validation"]["status"], j.get("run_id"))
    for zk_want in (True, False):
        rounds = sorted({r for (t, r), v in runs.items() if v[0] == zk_want and (("base", r) in runs and ("lane", r) in runs)})
        if not rounds:
            continue
        print(f"{rel} zk={zk_want} rounds={rounds}")
        for key in ("t.total", "t.encoding_commitment", "t.arithmetic", "t.witness"):
            b = [runs[("base", r)][1][key] for r in rounds]
            l = [runs[("lane", r)][1][key] for r in rounds]
            diff = [y - x for x, y in zip(b, l)]
            mb, ml = st.median(b), st.median(l)
            print(f"  {key:22s} base {' '.join(f'{x:.4f}' for x in b)} | median {mb:.4f}   lane {' '.join(f'{x:.4f}' for x in l)} | "
                  f"median {ml:.4f}   lane-base median {st.median(diff):+.4f} ({(ml / mb - 1) * 100:+.1f} %), lane faster in "
                  f"{sum(x < 0 for x in diff)}/{len(diff)} rounds")
        bad = [(t, r) for (t, r), v in runs.items() if v[2] != "passed"]
        print(f"  validation: {'all passed' if not bad else 'NOT passed: ' + str(bad)}")
