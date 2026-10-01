#!/usr/bin/env python3
"""Compare a node-2 point with its node-1 reference (run on node 1): python3 parity.py N2_RUN_DIR N1_RUN_DIR [TOL]

Prints, as JSON, overhead, verify s per statement and GPU-held s per VU of both, their relative differences, and whether every
one is within TOL (default 0.03).
"""
import json
import sys
from pathlib import Path

KEYS = ("overhead", "verify_s_per_statement", "gpu_held_s_per_vu")
MORE = ("overhead_prove_only", "throughput_vu_per_s", "gpu_util", "t_session_s_per_vu", "t_prove_only_s_per_vu", "setup_s", "cpu_slice_others",
        "byte_identical", "flags", "commit", "vus")


def main() -> int:
    n2, n1 = Path(sys.argv[1]), Path(sys.argv[2])
    tol = float(sys.argv[3]) if len(sys.argv) > 3 else 0.03
    a, b = json.loads((n2 / "hillclimb.json").read_text()), json.loads((n1 / "hillclimb.json").read_text())
    rel = {k: (a[k] - b[k]) / b[k] for k in KEYS}
    out = {"node2": {"run": a.get("run_id") or n2.name, **{k: a.get(k) for k in KEYS + MORE}},
           "node1": {"run": b.get("run_id") or n1.name, **{k: b.get(k) for k in KEYS + MORE}},
           "relative_difference": {k: round(v, 4) for k, v in rel.items()}, "tolerance": tol,
           "within": all(abs(v) <= tol for v in rel.values())}
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
