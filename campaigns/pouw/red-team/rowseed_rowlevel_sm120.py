"""P2 (`tt-out/pearl-c-sm120-rowseed`): how often does one fresh row carry a joint skip set shared by its fragment's 8 columns?

Per-row seeds let a prover grind A's rows one at a time, but an `mma.sync m16n8k32` fragment also spans 8 rows of B, whose
noise is one per-job draw from root_B that per-row A seeds don't re-roll. A fragment-wide set needs, first, one row whose
8 words share a joint set. This draws N fresh candidate rows of a family (independent background, fresh s5 noise) against
one fixed block of 8 B rows and reports, per row:
  - word 0's joint set (the census's per-word greedy: pairs neither atom of which skips alone, then singles);
  - the row-level set: the part of word 0's units that stays jointly skippable on all 8 words (greedy over the units).
The distribution over N rows is what a per-row prover grinding N variants per row could reach for its first row.
"""
import argparse
import importlib.util
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

TREE = Path(os.environ.get("CENSUS_TREE") or f"/workspace/research/src/{os.environ.get('RESEARCH_SOURCE_SHA', '')}")
_spec = importlib.util.spec_from_file_location("pearlc_census", TREE / "benchmarks/pouw/pearlc_census.py")
C = importlib.util.module_from_spec(_spec)
sys.modules["pearlc_census"] = C
_spec.loader.exec_module(C)
C.set_atom(os.environ.get("CENSUS_ATOM", "sm120-e4m3-k32"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rowseed_grind_sm120 import atoms, pack, pair_units  # noqa: E402


def job(args):
    fam, k, G, n, chunk = args
    XA, XB, _, _ = C.family_rows(fam, k, 1.0, n, 8, 1)
    FcA, FcB = C.s5_lines(k, 1, 16.0)
    a, _, _, fa, la = C.form_s5(XA, FcA, 1.0, 16.0, C._rng(1, fam, k, n, "rowlevel-A"))
    b, _, _, fb, lb = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, fam, k, n, "rowlevel-B"))
    out = []
    for r in range(chunk[0], chunk[1]):
        units = pair_units(a[r:r + 1], b[:1], G)
        row = pack(np.repeat(a[r:r + 1], 8, 0), b, G, units)
        out.append((len(atoms(units)), len(atoms(row))))
    return {"family": fam, "k": k, "layout": "pure" if G == 0 else f"G{G}", "rows": out,
            "in_domain": bool(np.all(fa) and np.all(la) and np.all(fb) and np.all(lb))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--families", default="aligned-spikes-r64,aligned-spikes-pm1-r64,aligned-spikes-r56")
    ap.add_argument("--layouts", default="0,4")
    ap.add_argument("--procs", type=int, default=48)
    args = ap.parse_args()
    step = 16
    jobs = [(f, args.k, int(G), args.n, (lo, lo + step)) for f in args.families.split(",") for G in args.layouts.split(",")
            for lo in range(0, args.n, step)]
    agg = {}
    with Pool(args.procs) as pool:
        for r in pool.imap_unordered(job, jobs):
            key = (r["family"], r["layout"])
            a = agg.setdefault(key, {"rows": [], "in_domain": True})
            a["rows"] += r["rows"]
            a["in_domain"] &= r["in_domain"]
    for (fam, lay), a in sorted(agg.items()):
        w = np.array([x[0] for x in a["rows"]])
        rl = np.array([x[1] for x in a["rows"]])
        print(json.dumps({"family": fam, "k": args.k, "layout": lay, "rows": len(rl), "in_domain": a["in_domain"],
                          "word0_set_mean": float(w.mean()), "word0_set_max": int(w.max()),
                          "row_level_set_max": int(rl.max()), "rows_with_row_level_set": int((rl > 0).sum()),
                          "row_level_hist": {int(v): int((rl == v).sum()) for v in np.unique(rl)}}), flush=True)


if __name__ == "__main__":
    main()
