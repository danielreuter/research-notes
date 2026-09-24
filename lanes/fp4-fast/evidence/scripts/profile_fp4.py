"""Per-phase prover timings of FP4ChainRunner at a given l (steady state: warm-up sub-batch, then median over the rest)."""
import argparse
import os
import statistics
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument("--tree", required=True)
ap.add_argument("--batch", type=int, default=16384)
ap.add_argument("--subs", type=int, default=4)
ap.add_argument("--zk", action="store_true")
ap.add_argument("--hints", default="device")
ap.add_argument("--n-proofs", type=int, default=None)
ap.add_argument("--sleep", type=float, default=0.0)
args = ap.parse_args()
os.chdir(args.tree)
sys.path.insert(0, args.tree)
for sub in ("packages/verity/src", "backends/numerical/python"):
    sys.path.insert(0, os.path.join(args.tree, sub))
import torch  # noqa: E402

from backends.direct.ligero.fp4.chain import STEPS, FP4ChainRunner, instances_fp4  # noqa: E402
from backends.direct.ligero.protocol import soundness  # noqa: E402

per = args.batch // STEPS
n_proofs = args.n_proofs or -(-4096 // per)
R = FP4ChainRunner("cuda", -128.0, 2, n_proofs=n_proofs, zk=args.zk, hints=args.hints)
data = instances_fp4(per * args.subs)
lay = R.layout(per)
cfg = R.cfg(lay.l)
print(f"l={cfg.l} n={cfg.n} t={cfg.t} D={cfg.D} n_proofs={n_proofs} per={per} zk={args.zk} hints={args.hints} m={R.sys.m}")
rows = []
for si in range(args.subs):
    lo = si * per
    torch.cuda.synchronize()
    if args.sleep: time.sleep(args.sleep)
    t0 = time.perf_counter()
    proof, pubs, lay_i = R.prove_vus(data[lo:lo + per], check=(si == 0), min_l=lay.l)
    torch.cuda.synchronize()
    wall = time.perf_counter() - t0
    tm = dict(proof.timings)
    tm["wall"] = wall
    rows.append(tm)
    print(f"  sub {si}: total={tm['total']*1e3:.1f}ms wall={wall*1e3:.1f}ms encode={tm.get('encode',0)*1e3:.1f} tests={tm.get('tests',0)*1e3:.1f} tests_w={tm.get('tests_w',0)*1e3:.1f} openings={tm.get('openings',0)*1e3:.1f} statement={tm.get('statement',0)*1e3:.1f} hints={tm.get('hints_host',0)*1e3:.1f}")
    if si == 0:
        ok, why = R.verify_vus(proof, pubs, lay_i)
        assert ok, why
        print("warm-up:", " ".join(f"{k}={v:.3f}" for k, v in sorted(tm.items()) if v > 0.0005))
keys = sorted({k for r in rows[1:] for k in r})
med = {k: statistics.median(r.get(k, 0.0) for r in rows[1:]) for k in keys}
print("steady (median of %d):" % (len(rows) - 1), " ".join(f"{k}={med[k]*1e3:.1f}ms" for k in keys if med[k] > 0.0002))
print(f"peak device {torch.cuda.max_memory_allocated()/1e9:.2f} GB; proof bytes ~{sum(len(x) for x in []) or 'n/a'}")
print(f"per-sub-batch total {med['total']*1e3:.1f} ms -> x{n_proofs} = {med['total']*n_proofs:.3f} s for 4096 VUs")
