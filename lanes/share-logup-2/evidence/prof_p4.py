"""share-logup-2: steady-state pipelined passes of one runner (no verifier, no bench scaffolding).

usage: prof_p4.py <auth: excluded|included-hash|included-hash-shared> [rel=fp8-ada] [depth=4] [passes=8] [warm=3]
prints per pass: wall, prove_many LAST_STATS (host busy / waited, per-stage main-thread ms), and the median wall.
"""
import statistics
import sys
import time

import torch

from backends.direct.ligero import pipeline
from backends.direct.ligero import protocol as protocol_mod
from backends.direct.ligero.relations import RELATIONS
from backends.direct.ligero.relchain import (HashedRelationRunner, RelationChainRunner, SharedHashedRunner, instances,
                                             instances_digest, tile_digest, tile_instances)

auth = sys.argv[1]
relname = sys.argv[2] if len(sys.argv) > 2 else "fp8-ada"
depth = int(sys.argv[3]) if len(sys.argv) > 3 else 4
passes = int(sys.argv[4]) if len(sys.argv) > 4 else 8
warm = int(sys.argv[5]) if len(sys.argv) > 5 else 3
rel = RELATIONS[relname]
batch, total = 16384, 4096
per = batch // rel.steps
n_proofs = -(-total // per)
cls = {"excluded": RelationChainRunner, "included-hash": HashedRelationRunner, "included-hash-shared": SharedHashedRunner}[auth]
R = cls(rel, "cuda", -128.0, 2, n_proofs=n_proofs, zk=False, mode=protocol_mod.MODE_INTERACTIVE)
print("compile", round(R.compile_seconds, 2), "rows", R.sys.m, flush=True)
tile = (64, 64) if auth == "included-hash-shared" else None
if tile:
    data, xr, wc = tile_instances(rel, *tile, cache="/workspace/instances-cache")
    dig = tile_digest(rel, *tile) if rel.frozen_tier else instances_digest(rel, total)
    R.commit_vus(data, manifest_sha256=dig, cache=f"/workspace/auth-cache-shared-{relname}", tile=tile, x_rows=xr, w_cols=wc)
else:
    data = instances(rel, total, cache="/workspace/instances-cache")
    if auth == "included-hash":
        R.commit_vus(data, manifest_sha256=instances_digest(rel, total), cache=f"/workspace/auth-cache-hash-{relname}")
subs = [(lo, min(lo + per, total)) for lo in range(0, total, per)]
l = R.layout(per).l
batches = [data[lo:hi] for lo, hi in subs]
ids = [range(lo, hi) for lo, hi in subs]
fac = lambda i: protocol_mod.Coins.sample()  # noqa: E731
walls = []
for p in range(warm + passes):
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    many, wall = R.prove_vus_many(batches, fac, depth=depth, min_l=l, vu_ids_list=ids)
    st = dict(pipeline.LAST_STATS)
    tag = "warm" if p < warm else "pass"
    if p >= warm:
        walls.append(wall)
    tm = many[1][1].timings
    meas = {k[9:]: round(v * 1e3, 1) for k, v in sorted(tm.items()) if k.startswith("measured_") and v > 5e-4}
    print(f"{tag} {p}: wall {wall:.4f} host_busy {st['host_busy']:.4f} waited {st['host_waited']:.4f} stage_ms {st['stage_busy_ms']}",
          flush=True)
    if p == warm + passes - 2 and len(sys.argv) > 6:
        protocol_mod.HOST_TRACE = True
    if p == warm + passes - 1:
        print("  sub 1 measured ms:", meas)
        if protocol_mod.HOST_TRACE:
            def host_sum(get):
                acc = {}
                for _, pf, _, _ in many:
                    for k, v in get(pf).items():
                        if k.startswith("host_"):
                            acc[k[5:]] = acc.get(k[5:], 0.0) + v
                return {k: round(v * 1e3, 1) for k, v in sorted(acc.items(), key=lambda kv: -kv[1])}
            if auth == "included-hash-shared":
                print("  G host ms (sum over subs):", host_sum(lambda pf: pf.g.timings))
                print("  H host ms (sum over subs):", host_sum(lambda pf: pf.h.timings))
            else:
                print("  host ms (sum over subs):", host_sum(lambda pf: pf.timings))
        if auth == "included-hash-shared":
            pf = many[1][1]
            print("  G ms:", {k: round(v * 1e3, 1) for k, v in sorted(pf.g.timings.items()) if v > 5e-4 and not k.startswith("measured")})
            print("  H ms:", {k: round(v * 1e3, 1) for k, v in sorted(pf.h.timings.items()) if v > 5e-4 and not k.startswith("measured")})
print(f"{auth} {relname} depth {depth}: median wall {statistics.median(walls):.4f} min {min(walls):.4f} over {len(walls)} passes")
