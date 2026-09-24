"""sp1-table (pod): per-proof timeline of an SP1 GPU prover log (RUST_LOG=debug), grouped by proof_id.
For each proof: seconds from its first log line to the first ProveShard task start, to the first / last ProveShard success,
and to its last line; the ProveShard count, and the median gap between successive ProveShard successes.
    timeline.py prover.log
"""

import re
import statistics
import sys
from datetime import datetime

ANSI = re.compile(r"\x1b\[[0-9;]*m")
LINE = re.compile(r"^(\S+Z) +\w+ (.*)$")
PID = re.compile(r"proof_id=(proof_\w+)")
TASK = re.compile(r"ProveShard\{proof_id=proof_\w+ task_id=(\w+)\}")

proofs = {}
for raw in open(sys.argv[1], errors="replace"):
    m = LINE.match(ANSI.sub("", raw.rstrip("\n")))
    if not m:
        continue
    t = datetime.fromisoformat(m.group(1).replace("Z", "+00:00")).timestamp()
    rest = m.group(2)
    p = PID.search(rest)
    if not p:
        continue
    d = proofs.setdefault(p.group(1), {"first": t, "last": t, "start": {}, "done": {}, "kinds": {}})
    d["last"] = t
    k = TASK.search(rest)
    if k:
        d["start"].setdefault(k.group(1), t)
        if "task succeeded" in rest:
            d["done"][k.group(1)] = t
    for kind in re.findall(r"submitting task of kind (\w+)", rest):
        d["kinds"][kind] = d["kinds"].get(kind, 0) + 1

print(f"{'proof':34s} {'first_shard_start':>17s} {'first_done':>10s} {'last_done':>9s} {'end':>6s} {'shards':>6s} {'gap_med':>7s}  kinds")
for pid, d in proofs.items():
    t0 = d["first"]
    starts = sorted(d["start"].values())
    dones = sorted(d["done"].values())
    gaps = [b - a for a, b in zip(dones, dones[1:])]
    med = statistics.median(gaps) if gaps else float("nan")
    print(f"{pid:34s} {(starts[0] - t0) if starts else float('nan'):17.2f} {(dones[0] - t0) if dones else float('nan'):10.2f} "
          f"{(dones[-1] - t0) if dones else float('nan'):9.2f} {d['last'] - t0:6.2f} {len(dones):6d} {med:7.3f}  {d['kinds']}")
