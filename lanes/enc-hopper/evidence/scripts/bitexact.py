"""Lane hostphase bit-exactness harness: prove N sub-batches of a relation from ONE source tree with DETERMINISTIC
randomness (os.urandom replaced by a seeded SHAKE stream: the runner's interactive step-0 coins and the prover's ZK mask keys
come from it), write system.bin + sub_NN.{stmt,proof[,coins]} the way relchain.bench_vu_rel dumps them.  Run once per tree
(main 5a8a744 vs lane/hostphase) with the same arguments; the trees' files must be byte-identical.

usage: python bitexact.py --tree DIR --rel bf16-hopper [--zk] --mode interactive|fiat-shamir --vus 170 --subs 3 --seed 7 --out DIR [--impl device|legacy]
"""
import argparse
import hashlib
import json
import os
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument("--tree", required=True)
ap.add_argument("--rel", required=True)
ap.add_argument("--zk", action="store_true")
ap.add_argument("--mode", default="interactive")
ap.add_argument("--vus", type=int, default=170)
ap.add_argument("--subs", type=int, default=3)
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--out", required=True)
ap.add_argument("--impl", default=None)
ap.add_argument("--cache", default="/workspace/instances-cache")
ap.add_argument("--total", type=int, default=4096, help="instance set size (the cache is keyed by it)")
args = ap.parse_args()

# deterministic randomness for BOTH trees: every os.urandom(n) call is the next SHAKE-256 block of (seed, call index)
_calls = [0]
_seed = args.seed.to_bytes(8, "little")


def _urandom(n: int) -> bytes:
    _calls[0] += 1
    return hashlib.shake_256(b"hostphase-bitexact|" + _seed + _calls[0].to_bytes(8, "little")).digest(n)


os.urandom = _urandom

os.chdir(args.tree)
sys.path.insert(0, args.tree)
for sub in ("packages/verity/src", "backends/numerical/python"):
    sys.path.insert(0, os.path.join(args.tree, sub))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from backends.direct.ligero import protocol as protocol_mod  # noqa: E402
from backends.direct.ligero import witness as witness_mod  # noqa: E402
from backends.direct.ligero.relations import relation  # noqa: E402
from backends.direct.ligero.relchain import RelationChainRunner, instances  # noqa: E402
from backends.direct.ligero.serialize import _statement_of, proof_bytes, statement_bytes, system_bytes  # noqa: E402

if args.impl is not None:
    if not hasattr(witness_mod, "IMPL"):
        print(f"tree has no witness.IMPL (main); --impl {args.impl} ignored")
    else:
        witness_mod.IMPL = args.impl
print(f"tree={args.tree} impl={getattr(witness_mod, 'IMPL', 'n/a')} rel={args.rel} zk={args.zk} mode={args.mode} vus/sub={args.vus} subs={args.subs} seed={args.seed}")

rel = relation(args.rel)
per_proof = args.vus
n_proofs = args.subs            # the statements' n_proofs = the sub-batches presented (ligero-verify batch checks it)
R = RelationChainRunner(rel, "cuda", -128.0, 2, n_proofs=n_proofs, zk=args.zk, mode=args.mode)
data = instances(rel, args.total, procs=8, cache=args.cache)
lay = R.layout(per_proof)
l = lay.l
interactive = args.mode == protocol_mod.MODE_INTERACTIVE
os.makedirs(args.out, exist_ok=True)
sysb = system_bytes(R.sys)
open(os.path.join(args.out, "system.bin"), "wb").write(sysb)
files = {"system.bin": hashlib.sha256(sysb).hexdigest()}
timings = []
for si in range(args.subs):
    lo, hi = si * per_proof, min((si + 1) * per_proof, args.total)
    V = protocol_mod.Coins.sample() if interactive else None
    t0 = time.perf_counter()
    proof, pubs, lay_i = R.prove_vus(data[lo:hi], check=False, min_l=l, coins=V)
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
    print(f"  {stem}: {len(outs['%s.proof' % stem]) / 1e6:.2f} MB, prove {proof.timings['total']:.3f}s (+hints {proof.timings.get('hints_host', 0):.3f}s), urandom calls so far {_calls[0]}")
json.dump({"args": vars(args), "files": files, "timings": timings, "urandom_calls": _calls[0]},
          open(os.path.join(args.out, "digests.json"), "w"), indent=1)
print("wrote", args.out, len(files), "files")
