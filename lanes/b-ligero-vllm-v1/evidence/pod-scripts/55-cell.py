#!/usr/bin/env python3
"""b-ligero-vllm-v1: print the plateau point of a sweep dir and its cell measurements (usage: 55-cell.py SWEEP_DIR)."""
import json, sys
from pathlib import Path
sd = Path(sys.argv[1]); sw = json.loads((sd / "sweep.json").read_text())
p = [p for p in sw["points"] if p["point"] == sw["plateau_point"]][0]
d = json.loads((sd / p["dir"] / "result.json").read_text())
m = {x["name"]: x["value"] for x in d["measurements"]}
print("plateau", p["dir"], "sweep", sw.get("id"))
keys = ("e2e", "t.total", "commit", "overhead", "bytes", "round", "rtt", "verif", "split", "soundness", "mem.peak", "vu.", "coin",
        "comm", "live", "net", "transcript", "proof")
for k in sorted(m):
    if any(s in k for s in keys):
        print(k, m[k])
print("contended", (d.get("contention") or {}).get("contended"))
print("keys", sorted(k for k in d if k != "measurements"))
