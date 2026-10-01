#!/usr/bin/env python3
"""The `note` and `hardware` labels of one node-2 GPU point: python3 n2label.py RUNS_DIR RUN_ID -> {"note": .., "hardware": ..}.

Runs on node 1 beside the shipped run dirs (RUNS_DIR/<run id>/n2.json). A point's socket neighbours are the other node-2 jobs on
the prover range while it ran: the n2h jobs its record saw on 128-191 at its start and end, every shipped run whose interval
overlaps it, and any process outside n2h on the range. Proofs (08:02Z) counts node-2 points beside node 1's on overhead, from
the E4M3 K=2048 parity; an FP4 point is node-2-only once RUNS_DIR/../FP4_NODE2_ONLY exists (the MXF4 K=2048 parity check's mean
overhead off by more than 3%), its first line the reason. Stdlib only.
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


def labels(runs: Path, run: str) -> dict:
    d = json.loads((runs / run / "n2.json").read_text())
    g = d.get("gpu") or {}
    slot = d.get("slot") or {}
    m = re.search(r"\bDTYPE=(\w+)", d.get("cmd") or "")
    fp4 = bool(m) and m.group(1).lower() in ("nvf4", "mxf4")
    where = (f"node vy-nebius-2, prover slice {d['cpuset']} (NUMA {slot.get('numa')}) via vy-provers, "
             f"GPU {g.get('cuda_visible_devices')} (NUMA {g.get('numa')})")
    nb = neighbours(runs, d)
    socket = f"socket neighbours on {d.get('range') or '128-191'}: {'; '.join(nb) if nb else 'none'}"
    flag = runs.parent / "FP4_NODE2_ONLY"
    if fp4 and flag.exists():
        why = (flag.read_text().splitlines() or ["MXF4 parity off by more than 3%"])[0]
        head = f"node-2-only ({REF}): FP4 points compare with node-2 points only, {why}"
    else:
        head = (f"counts beside node 1's on overhead ({REF}; proofs 08:02Z: E4M3 K=2048 x3 against node 1, mean overhead -2.0%, "
                f"GPU-held -2.0%, verify/statement -4.3%)")
        if fp4:
            head += "; FP4: back to node-2-only if the MXF4 K=2048 parity check's mean overhead is off by more than 3%"
    note = f"{head}; {where}; {socket}; a gain under 20% is confirmed on its baseline's node"
    hardware = (f"vy-nebius-2: GPU {g.get('cuda_visible_devices')} {g.get('name') or ''} (NUMA {g.get('numa')}); "
                f"prover slice {d['cpuset']} of {d.get('range') or '128-191'} (NUMA {slot.get('numa')}) via vy-provers")
    return {"note": note, "hardware": hardware, "ref": REF, "fp4": fp4}


if __name__ == "__main__":
    print(json.dumps(labels(Path(sys.argv[1]), sys.argv[2])))
