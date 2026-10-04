"""Red-team for `tt-out/pearl-c-sm120-unpromoted-chaincap1000`: which full 64 x 64 tiles of a family pass the chain cap?

The chain cap admits a tile when its replayed debit is at most rho times its chain's credited work, i.e. (lone-skip
flags on the unpromoted chain) a flagged share of atom-words <= rho = 1/1,000 (`chainCap_flagged_le`, restatements §5).
Per independent 64 x 64 tile (the protocol's tile, 4,096 words; census seeds `run` = 1 .. N), on the census's s5 forming and
the bit-exact sm_120 atom: the flagged share, and whether the tile is admitted.
"""
import argparse, importlib.util, json, os, sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

TREE = Path(os.environ.get("CENSUS_TREE") or f"/workspace/research/src/{os.environ.get('RESEARCH_SOURCE_SHA', '')}")
_spec = importlib.util.spec_from_file_location("pearlc_census", TREE / "benchmarks/pouw/pearlc_census.py")
C = importlib.util.module_from_spec(_spec)
sys.modules["pearlc_census"] = C
_spec.loader.exec_module(C)
C.set_atom("sm120-e4m3-k32")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rt_result  # noqa: E402

RHO = 1 / 1000


def tile(job):
    fam, k, run = job
    XA, XB, _, _ = C.family_rows(fam, k, 1.0, 64, 64, run)
    FcA, FcB = C.s5_lines(k, run, 16.0)
    a, _, _, fa, la = C.form_s5(XA, FcA, 1.0, 16.0, C._rng(run, fam, k, 1.0, "unit-A"))
    b, _, _, fb, lb = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(run, fam, k, 1.0, "unit-B"))
    A, B = np.repeat(a, 64, 0), np.tile(b, (64, 1))
    share = float(C.debit_pure(A, B).mean())
    return {"family": fam, "k": k, "run": run, "in_domain": bool(fa and la and fb and lb), "flagged_share": share,
            "admitted": bool(share <= RHO)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default="aligned-spikes-r64,aligned-spikes-pm1-r64,aligned-spikes-r56")
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--tiles", type=int, default=16)
    ap.add_argument("--procs", type=int, default=48)
    args = ap.parse_args()
    jobs = [(f, args.k, r) for f in args.families.split(",") for r in range(1, args.tiles + 1)]
    with Pool(min(args.procs, len(jobs))) as pool:
        cells = pool.map(tile, jobs)
    summary = {}
    for f in args.families.split(","):
        s = np.array([c["flagged_share"] for c in cells if c["family"] == f])
        summary[f] = {"tiles": int(s.size), "mean": float(s.mean()), "sd": float(s.std(ddof=1)) if s.size > 1 else 0.0,
                      "sem": float(s.std(ddof=1) / np.sqrt(s.size)) if s.size > 1 else 0.0,
                      "min": float(s.min()), "max": float(s.max()), "admitted_tiles": int((s <= RHO).sum())}
        print(json.dumps({"family": f, **summary[f]}), flush=True)
    meas = []
    for f, v in summary.items():
        meas += [(f"{f}.flagged_share_mean", round(v["mean"], 7), "fraction"),
                 (f"{f}.admitted_tiles", v["admitted_tiles"], "tiles")]
    rt_result.write("chaincap-tiles-sm120", meas, {"k": args.k, "rho": RHO, "summary": summary, "tiles": cells},
                    detail="lone-skip flagged share per independent 64x64 tile against the chain cap 1/1000")


if __name__ == "__main__":
    main()
