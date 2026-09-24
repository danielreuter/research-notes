#!/usr/bin/env python3
"""table.py RESULTS_DIR... : one markdown row per (relation, l, pipeline) cell, aggregated over the rounds (result files
TAG, TAGr2, TAGr3, ...). Each round's t.total is already the median of its 3 reps; the row gives the median / min / max
over rounds, the per-phase medians, peak device memory, proof bytes and the Rust verdicts of every round's rep-1 dump."""
import glob
import json
import os
import re
import statistics
import sys
from collections import defaultdict

cells = defaultdict(list)
for R in sys.argv[1:]:
    for f in sorted(glob.glob(os.path.join(R, "*.json"))):
        if f.endswith("_rust.json"):
            continue
        tag = os.path.basename(f)[:-5]
        d = json.load(open(f))
        wf = d["workload_fingerprint"]
        m = {x["name"]: x["value"] for x in d["measurements"]}
        name = wf["software"]["backend"]["name"]
        rel = name.split(",")[1].split()[0] if "," in name else "bf16 (vu.py)"
        p = wf["software"]["backend"].get("pipeline") or 1
        rv = None
        rf = f[:-5] + "_rust.json"
        if os.path.exists(rf):
            r = json.load(open(rf))
            rv = r["batch_accepted"] and r["system_pinned"] and r["accepted"] == r["n"], r["n"]
        gpu = wf["hardware"]["gpu"]["name"]
        cells[(gpu, rel, wf["security"]["rs_l"], p)].append(dict(
            tag=tag, tt=m["t.total"], hints=m.get("split.hints_seconds", float("nan")), wit=m["t.witness"],
            enc=m["t.encoding_commitment"], ar=m["t.arithmetic"], peak=m["mem.peak_device_bytes"] / 2**30,
            mb=m["transcript.bytes"] / 1e6, N=wf["N_subbatches"], rv=rv, man=wf["instances"]["manifest_sha256"][:8]))

med = statistics.median
print("| GPU | relation | l | depth | sub-batches | rounds | t.total median (min–max) s | hints | enc+commit | arithmetic | "
      "peak GiB | proof MB | Rust (rep-1 dump, every round) | instances | tags |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for (gpu, rel, l, p), rs in sorted(cells.items(), key=lambda kv: (kv[0][0], kv[0][1].replace("-v3", "~"), kv[0][2], kv[0][3])):
    tts = [r["tt"] for r in rs]
    ok = all(r["rv"] and r["rv"][0] for r in rs)
    rust = f"{len(rs)}/{len(rs)} batch ACCEPT, pinned, {rs[0]['rv'][1]}/{rs[0]['rv'][1]}" if ok else "NOT ALL ACCEPT"
    short = "H100" if "H100" in gpu else "A100" if "A100" in gpu else gpu
    print(f"| {short} | {rel} | {l} | {p} | {rs[0]['N']} | {len(rs)} | **{med(tts):.4f}** ({min(tts):.4f}–{max(tts):.4f}) | "
          f"{med(r['hints'] for r in rs):.4f} | {med(r['enc'] for r in rs):.4f} | {med(r['ar'] for r in rs):.4f} | "
          f"{rs[0]['peak']:.2f} | {rs[0]['mb']:.1f} | {rust} | {rs[0]['man']} | {' '.join(r['tag'] for r in rs)} |")
