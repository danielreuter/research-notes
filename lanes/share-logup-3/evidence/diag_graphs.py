"""share-logup-3: why is bf16 +shared host-bound at l = 16384?  Counts CUDA graph captures and tests static-set rebuilds per
pipelined pass of SharedHashedRunner (the bench's shape: 4096 VUs, batch 16384, 64x64 tile, depth 4, local coins).

usage: diag_graphs.py <rel> <interleave 0|1> [passes=3] [warm=2]
"""
import collections
import statistics
import sys
import time

import torch

from backends.direct.ligero import pipeline, relchain
from backends.direct.ligero import protocol as protocol_mod
from backends.direct.ligero.relations import RELATIONS
from backends.direct.ligero.relchain import SharedHashedRunner, instances_digest, tile_digest, tile_instances

relname, inter = sys.argv[1], bool(int(sys.argv[2]))
passes = int(sys.argv[3]) if len(sys.argv) > 3 else 3
warm = int(sys.argv[4]) if len(sys.argv) > 4 else 2
relchain.INTERLEAVE_PAIR = inter
caps, rebuilds = collections.Counter(), collections.Counter()
_cb = torch.cuda.CUDAGraph.capture_begin


def capture_begin(self, *a, **k):
    import traceback
    fr = [f for f in traceback.extract_stack(limit=8) if "ligero" in f.filename]
    caps[f"{fr[-1].name}:{fr[-1].lineno}" if fr else "?"] += 1
    return _cb(self, *a, **k)


torch.cuda.CUDAGraph.capture_begin = capture_begin
_ts = protocol_mod._TestsStatic.__init__


def ts_init(self, key, *a, **k):
    rebuilds[key[:2] + key[-4:]] += 1
    return _ts(self, key, *a, **k)


protocol_mod._TestsStatic.__init__ = ts_init
rel = RELATIONS[relname]
batch, total = 16384, 4096
per = batch // rel.steps
n_proofs = -(-total // per)
R = SharedHashedRunner(rel, "cuda", -128.0, 2, n_proofs=n_proofs, zk=False, mode=protocol_mod.MODE_INTERACTIVE)
data, xr, wc = tile_instances(rel, 64, 64, cache="/workspace/instances-cache")
dig = tile_digest(rel, 64, 64) if rel.frozen_tier else instances_digest(rel, total)
R.commit_vus(data, manifest_sha256=dig, cache=f"/workspace/auth-cache-shared-{relname}", tile=(64, 64), x_rows=xr, w_cols=wc)
subs = [(lo, min(lo + per, total)) for lo in range(0, total, per)]
l = R.layout(per).l
batches = [data[lo:hi] for lo, hi in subs]
ids = [range(lo, hi) for lo, hi in subs]
lay_h = collections.Counter()
for b, i in zip(batches, ids):
    bd = R.marshal_shared(b, i, l)
    lay_h[(bd["lay"].l, bd["lay_h"].l, bd["lay_h"].n_vus)] += 1
print(relname, "interleave", inter, "sub-batches", len(subs), "(l_G, l_H, n_units):", dict(lay_h), flush=True)
fac = lambda i: protocol_mod.Coins.sample()  # noqa: E731
walls = []
for p in range(warm + passes):
    caps.clear()
    rebuilds.clear()
    torch.cuda.synchronize()
    many, wall = R.prove_vus_many(batches, fac, depth=4, min_l=l, vu_ids_list=ids)
    st = dict(pipeline.LAST_STATS)
    if p >= warm:
        walls.append(wall)
    print(f"{'warm' if p < warm else 'pass'} {p}: wall {wall:.4f} host_busy {st['host_busy']:.4f} captures {sum(caps.values())} "
          f"{dict(caps)} static rebuilds {sum(rebuilds.values())} {dict(rebuilds)}", flush=True)
print(f"{relname} interleave {inter}: median wall {statistics.median(walls):.4f}")
