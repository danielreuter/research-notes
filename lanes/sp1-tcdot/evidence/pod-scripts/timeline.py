"""Per-shard timeline of one sp1-gpu-server debug log (the host's stdout): python3 timeline.py events.jsonl [proof_id]"""
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

ANSI = re.compile(r"\x1b\[[0-9;]*m")
TS = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+)Z\s+\w+\s+(.*)$")


def ts(s):
    return datetime.strptime(s[:26], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc).timestamp()


tasks = defaultdict(lambda: {"start": None, "end": None, "chips": {}, "cells": None, "proof": None})
proofs = defaultdict(lambda: {"first": None, "last": None, "exec": None})
for raw in open(sys.argv[1], errors="replace"):
    line = ANSI.sub("", raw).rstrip()
    m = TS.match(line)
    if not m:
        continue
    t, msg = ts(m.group(1)), m.group(2)
    pid = re.search(r"proof_id=(proof_[a-z0-9]+)", msg)
    if not pid:
        continue
    pid = pid.group(1)
    p = proofs[pid]
    p["first"] = t if p["first"] is None else p["first"]
    p["last"] = t
    if "minimal Executor finished" in msg:
        e = re.search(r"elapsed: ([0-9.]+)s", msg)
        p["exec"] = float(e.group(1)) if e else None
    tid = re.search(r"ProveShard\{proof_id=\S+ task_id=(\S+?)\}", msg)
    if not tid:
        continue
    d = tasks[tid.group(1)]
    d["proof"] = pid
    if "Proving shard" in msg and d["start"] is None:
        d["start"] = t
    if "task succeeded" in msg:
        d["end"] = t
    c = re.search(r"sp1_gpu_jagged_tracegen: (\w+)\s+\| Prep Cols = ([\d_]+)\s+\| Main Cols = ([\d_]+)\s+\| Rows = ([\d_]+)", msg)
    if c:
        d["chips"][c.group(1)] = (int(c.group(3).replace("_", "")), int(c.group(4).replace("_", "")))
    c = re.search(r"Total number of cells: ([\d_]+)", msg)
    if c:
        d["cells"] = int(c.group(1).replace("_", ""))

want = sys.argv[2] if len(sys.argv) > 2 else None
for pid, p in proofs.items():
    if want and pid != want:
        continue
    ts_ = sorted((d for d in tasks.values() if d["proof"] == pid and d["start"]), key=lambda d: d["start"])
    if not ts_:
        continue
    t0 = p["first"]
    print(f"{pid}: span {p['last'] - t0:.2f}s executor {p['exec']}s shards {len(ts_)}")
    for d in ts_:
        tc = d["chips"].get("TcDotBf16", (0, 0))
        top = sorted(d["chips"].items(), key=lambda kv: -kv[1][0] * kv[1][1])[:3]
        dur = (d["end"] - d["start"]) if d["end"] else float("nan")
        print(f"  +{d['start'] - t0:6.2f}s .. +{(d['end'] or float('nan')) - t0:6.2f}s ({dur:5.2f}s) cells {d['cells']} "
              f"TcDotBf16 rows {tc[1]} | " + ", ".join(f"{k} {c}x{r}" for k, (c, r) in top))
