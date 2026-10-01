#!/usr/bin/env python3
"""The `note` and `hardware` labels of one node-2 GPU point: python3 n2label.py RUNS_DIR RUN_ID -> {"note": .., "hardware": ..}.

Runs on node 1 beside the shipped run dirs (RUNS_DIR/<run id>/n2.json). A point's socket neighbours are the other node-2 jobs on
the prover range while it ran: the n2h jobs its record saw on 128-191 at its start and end, every shipped run whose interval
overlaps it, and any process outside n2h on the range. Node-2 points go on the overhead curve labelled by node, and proofs'
offset rule (08:30Z) divides a node-2 overhead by 0.95 before any comparison with a node-1 number; an FP4 point is node-2-only
once RUNS_DIR/../FP4_NODE2_ONLY exists (proofs 08:02Z: the MXF4 K=2048 parity check's mean overhead off by more than 3%), its
first line the reason. Stdlib only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REF = "note:proofs-n2-hill/20261001T0755Z-finding-node2-parity"


def neighbours(runs: Path, d: dict) -> list[str]:
    seen: dict[str, str] = {}
    a = d.get("affinity_check") or {}
    for k in ("before_range", "after_range"):
        for x in (a.get(k) or {}).get("n2h_other_slots") or []:
            if x.get("n2h_item"):
                seen.setdefault(x["n2h_item"], x.get("cpus_allowed") or "?")
    for p in runs.glob("n2h-*/n2.json"):
        try:
            o = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        if o.get("run_id") == d["run_id"] or not (o.get("t_start") and o.get("t_end")):
            continue
        if not (o["t_start"] < d["t_end"] and d["t_start"] < o["t_end"]):
            continue
        seen.setdefault(o.get("item_id") or o["run_id"], o.get("cpuset") or "?")
    out = [f"{item.replace('__', ' ', 1)} on {cpus}" for item, cpus in sorted(seen.items(), key=lambda kv: kv[1])]
    others = max((a.get(k) or {}).get("others_n") or 0 for k in ("before_range", "after_range"))
    if others:
        out.append(f"{others} processes outside n2h")
    return out


def slice_numa(cpuset: str) -> str:
    """Node 2's NUMA node 0 is CPUs 0-95 and node 1 is 96-191, so 92-107 straddles them."""
    lo, hi = (int(x) for x in cpuset.split("-"))
    if hi <= 95 or lo >= 96:
        return str(0 if hi <= 95 else 1)
    return f"0+1: {lo}-95 on 0, 96-{hi} on 1"


def labels(runs: Path, run: str) -> dict:
    d = json.loads((runs / run / "n2.json").read_text())
    g = d.get("gpu") or {}
    m = re.search(r"\bDTYPE=(\w+)", d.get("cmd") or "")
    fp4 = bool(m) and m.group(1).lower() in ("nvf4", "mxf4")
    where = (f"node vy-nebius-2, prover slice {d['cpuset']} (NUMA {slice_numa(d['cpuset'])}) via vy-provers, "
             f"GPU {g.get('cuda_visible_devices')} (NUMA {g.get('numa')})")
    nb = neighbours(runs, d)
    socket = f"socket neighbours on {d.get('range') or '128-191'}: {'; '.join(nb) if nb else 'none'}"
    flag = runs.parent / "FP4_NODE2_ONLY"
    if fp4 and flag.exists():
        why = (flag.read_text().splitlines() or ["MXF4 parity off by more than 3%"])[0]
        head = (f"node-2-only ({REF}): FP4 points compare with node-2 points only, {why}; "
                f"a gain under 20% is confirmed on node 2")
    else:
        head = (f"on the overhead curve as a node-2 point ({REF}; proofs' offset rule, 08:30Z): divide this overhead by 0.95 "
                f"before comparing it with any node-1 number (E4M3 K=2048 x3 against node 1: -5.4%, +0.5%, -1.1%, mean -2.0%), "
                f"and report the raw value with its node beside the corrected one; same-node pairs need no correction; "
                f"the 20% rule applies to the corrected gain, and a gain under 20% is confirmed on its baseline's node")
    note = f"{head}; {where}; {socket}"
    hardware = (f"vy-nebius-2: GPU {g.get('cuda_visible_devices')} {g.get('name') or ''} (NUMA {g.get('numa')}); "
                f"prover slice {d['cpuset']} of {d.get('range') or '128-191'} (NUMA {slice_numa(d['cpuset'])}) via vy-provers")
    return {"note": note, "hardware": hardware, "ref": REF, "fp4": fp4}


if __name__ == "__main__":
    print(json.dumps(labels(Path(sys.argv[1]), sys.argv[2])))
