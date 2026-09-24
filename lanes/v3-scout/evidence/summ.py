#!/usr/bin/env python3
"""summ.py RESULTS_DIR [--md]: one line per result json (t.total median + phases, peak memory, proof MB, Rust verdict)."""
import glob
import json
import os
import sys

R = sys.argv[1]
md = "--md" in sys.argv
for f in sorted(glob.glob(os.path.join(R, "*.json"))):
    if f.endswith("_rust.json"):
        continue
    tag = os.path.basename(f)[:-5]
    d = json.load(open(f))
    m = {x["name"]: x["value"] for x in d["measurements"]}
    wf = d["workload_fingerprint"]
    rust = os.path.join(R, tag + "_rust.json")
    rv = "-"
    if os.path.exists(rust):
        r = json.load(open(rust))
        rv = (f"{r['accepted']}/{r['n']} {'ACCEPT' if r['batch_accepted'] else 'REJECT'} "
              f"{'pinned' if r['system_pinned'] else 'UNPINNED'} py={r['python_agree']}/{r['n']}")
    rel = wf["software"]["backend"]["name"].split(",")[1].strip().split()[0] if "," in wf["software"]["backend"]["name"] else "?"
    vals = dict(tag=tag, rel=rel, p=wf["software"]["backend"].get("pipeline"), l=wf["security"]["rs_l"], N=wf["N_subbatches"],
                tt=m["t.total"], hints=m.get("split.hints_seconds", float("nan")), enc=m["t.encoding_commitment"],
                ar=m["t.arithmetic"], ser=m["t.serialization"], peak=m["mem.peak_device_bytes"] / 2**30,
                mb=m["transcript.bytes"] / 1e6, val=d["validation"], man=wf["instances"]["manifest_sha256"][:8],
                rid=d.get("run_id"), rv=rv)
    if md:
        print("| {tag} | {rel} | {l} | {p} | {N} | **{tt:.4f}** | {hints:.4f} | {enc:.4f} | {ar:.4f} | {peak:.2f} | {mb:.1f} | {val} | {rv} | {man} | {rid} |".format(**vals))
    else:
        print("{tag:7s} {rel:15s} l={l:5d} p={p} N={N:3d} t.total={tt:.4f} hints={hints:.4f} enc={enc:.4f} arith={ar:.4f} "
              "ser={ser:.4f} peak={peak:.2f}GiB proof={mb:.1f}MB val={val} man={man} rust={rv}".format(**vals))
