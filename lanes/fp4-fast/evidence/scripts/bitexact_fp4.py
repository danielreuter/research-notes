"""Lane fp4-fast bit-exactness harness (hostphase's bitexact.py for the fp4-nvf4 runner): prove N sub-batches of fp4-nvf4 from
ONE source tree with DETERMINISTIC randomness (os.urandom replaced by a seeded SHAKE stream: the runner's interactive step-0
coins and the prover's ZK mask keys come from it), write system.bin + sub_NN.{stmt,proof[,coins]} the way
fp4.chain.bench_vu_fp4 dumps them.  Run once per tree (main 6babe27 vs lane/fp4-fast) with the same arguments at the same
operating point (--batch); the trees' files must be byte-identical.

usage: python bitexact_fp4.py --tree DIR [--zk] --mode interactive|fiat-shamir --batch 4096 --subs 3 --seed 7 --out DIR [--hints device|numpy]
"""
import argparse
import hashlib
import json
import os
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument("--tree", required=True)
ap.add_argument("--zk", action="store_true")
ap.add_argument("--mode", default="interactive")
ap.add_argument("--batch", type=int, default=4096)
ap.add_argument("--subs", type=int, default=3)
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--out", required=True)
ap.add_argument("--hints", default=None)
ap.add_argument("--total", type=int, default=4096)
ap.add_argument("--pipeline", type=int, default=0, help="prove_vus_many depth (trees with the staged protocol); 0 = sequential prove_vus")
args = ap.parse_args()

_calls = [0]
_seed = args.seed.to_bytes(8, "little")


def _urandom(n: int) -> bytes:
    _calls[0] += 1
    return hashlib.shake_256(b"fp4-fast-bitexact|" + _seed + _calls[0].to_bytes(8, "little")).digest(n)


os.urandom = _urandom

# torch.compile (dynamo's output_graph.compile_and_call_fx_graph -> unique_id -> uuid.uuid4 -> os.urandom(16)) draws a uuid per
# compiled graph, and how many graphs compile depends on the inductor cache state (first run vs warm cache), so a seeded
# os.urandom alone is NOT replayable across runs -- the ZK mask key (protocol._sample_masks) would land at a different
# stream position.  uuid4 gets its own deterministic counter stream; the protocol's draws stay on the seeded one.
import uuid  # noqa: E402

_uuid_calls = [0]


def _uuid4():
    _uuid_calls[0] += 1
    return uuid.UUID(bytes=hashlib.sha256(b"fp4-fast-uuid|" + _uuid_calls[0].to_bytes(8, "little")).digest()[:16], version=4)


uuid.uuid4 = _uuid4

os.chdir(args.tree)
sys.path.insert(0, args.tree)
for sub in ("packages/verity/src", "backends/numerical/python"):
    sys.path.insert(0, os.path.join(args.tree, sub))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from backends.direct.ligero import protocol as protocol_mod  # noqa: E402
from backends.direct.ligero.fp4.chain import STEPS, FP4ChainRunner, instances_fp4  # noqa: E402
from backends.direct.ligero.serialize import _statement_of, proof_bytes, statement_bytes, system_bytes  # noqa: E402

per_proof = args.batch // STEPS
n_proofs = args.subs
kw = {}
if args.hints is not None:
    import inspect
    if "hints" in inspect.signature(FP4ChainRunner.__init__).parameters:
        kw["hints"] = args.hints
    else:
        print(f"tree has no FP4ChainRunner(hints=...) (main); --hints {args.hints} ignored")
R = FP4ChainRunner("cuda", -128.0, 2, n_proofs=n_proofs, zk=args.zk, mode=args.mode, **kw)
print(f"tree={args.tree} hints={getattr(R, 'hints_mode', 'numpy (main)')} zk={args.zk} mode={args.mode} batch={args.batch} per_proof={per_proof} subs={args.subs} seed={args.seed}")
t0 = time.perf_counter()
data = instances_fp4(min(args.total, per_proof * args.subs))
print(f"{len(data)} instances in {time.perf_counter() - t0:.1f}s")
lay = R.layout(per_proof)
l = lay.l
interactive = args.mode == protocol_mod.MODE_INTERACTIVE
os.makedirs(args.out, exist_ok=True)
sysb = system_bytes(R.sys)
open(os.path.join(args.out, "system.bin"), "wb").write(sysb)
files = {"system.bin": hashlib.sha256(sysb).hexdigest()}
timings = []
bounds = [(si * per_proof, min((si + 1) * per_proof, len(data))) for si in range(args.subs)]
many = None
if args.pipeline > 1:
    if not hasattr(R, "prove_vus_many"):
        sys.exit("tree has no FP4ChainRunner.prove_vus_many")
    # the same draws in the same order as the sequential loop: coins_factory as each sub-batch starts, then its mask keys
    pre = _calls[0]                                              # the draws before the first coins (runner / instances) stay
    R.prove_vus_many([data[lo:hi] for lo, hi in bounds[:1]], lambda: protocol_mod.Coins.sample() if interactive else None, depth=1, min_l=l)
    _calls[0] = pre                                              # the warm-up's draws do not count: resume the seeded stream
    many, wall = R.prove_vus_many([data[lo:hi] for lo, hi in bounds], lambda: protocol_mod.Coins.sample() if interactive else None,
                                  depth=args.pipeline, min_l=l)
    print(f"pipeline depth {args.pipeline}: {len(many)} sub-batches in {wall:.3f}s wall")
for si in range(args.subs):
    lo, hi = bounds[si]
    if many is not None:
        V, proof, pubs, lay_i = many[si]
    else:
        V = protocol_mod.Coins.sample() if interactive else None
        proof, pubs, lay_i = R.prove_vus(data[lo:hi], check=(si == 0), min_l=l, coins=V)
    ok, why = R.verify_vus(proof, pubs, lay_i, coins=V)
    assert ok, why
    st = _statement_of(R, pubs, lay_i, R.cfg(lay_i.l), n_proofs)
    stem = f"sub_{si:02d}"
    outs = {f"{stem}.stmt": statement_bytes(st), f"{stem}.proof": proof_bytes(proof)}
    if V is not None:
        outs[f"{stem}.coins"] = V.r1 + V.s1 + V.r2 + V.s2
    for name, blob in outs.items():
        open(os.path.join(args.out, name), "wb").write(blob)
        files[name] = hashlib.sha256(blob).hexdigest()
    timings.append({k: round(v, 4) for k, v in proof.timings.items()})
    print(f"  {stem}: l={lay_i.l} {len(outs['%s.proof' % stem]) / 1e6:.2f} MB, prove {proof.timings['total']:.3f}s (+hints {proof.timings.get('hints_host', 0):.3f}s), urandom calls so far {_calls[0]}")
json.dump({"args": vars(args), "files": files, "timings": timings, "urandom_calls": _calls[0]},
          open(os.path.join(args.out, "digests.json"), "w"), indent=1)
print("wrote", args.out, len(files), "files")
