"""wave-a100-2: per candidate, every cell's t.total (= median of its reps) across rounds, and the pooled reps.
   python3 pool.py [PREFIX...]    (default: bare- live- shared64)  -> one line per (prefix, candidate)"""
import glob, json, os, re, statistics as st, sys

pre = sys.argv[1:] or ["bare-", "live-", "shared64"]
rows = {}
for d in sorted(glob.glob("/workspace/wave-a100/runs/*/result.json")):
    tag = d.split("/")[-2]
    if not any(tag.startswith(p) for p in pre):
        continue
    cand, rnd = re.match(r"(.*)-r(\d+)$", tag).groups()
    r = json.load(open(d))
    m = {x["name"]: x["value"] for x in r["measurements"]}
    reps = [x["prover_total"] for x in r["validation"]["evidence"]["reps"]]
    rows.setdefault(cand, []).append((int(rnd), m["t.total"], m.get("t.total_live"), reps, m.get("proof_bytes")))
for cand, xs in sorted(rows.items()):
    xs.sort()
    cells = [x[1] for x in xs]
    pooled = [y for x in xs for y in x[3]]
    live = [x[2] for x in xs if x[2] is not None]
    s = (f"{cand:22s} rounds={len(xs)} cell t.total " + " ".join(f"r{x[0]}:{x[1]:.4f}" for x in xs)
         + f" | median-of-cells {st.median(cells):.4f} pooled-median {st.median(pooled):.4f} min {min(pooled):.4f}")
    if live:
        s += " | t.total_live " + " ".join(f"{v:.4f}" for v in live) + f" median {st.median(live):.4f}"
    print(s + f" | proof_bytes {xs[0][4]}")
