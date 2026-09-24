"""share-logup-2: device occupancy of one steady-state pipelined pass (torch.profiler / CUPTI).

usage: prof_dev.py <auth> [rel=fp8-ada] [depth=4] [warm=3]
prints: pass wall, union of device activity intervals (busy), the sum of kernel time, the top kernels.
"""
import sys
import time

import torch
from torch.profiler import ProfilerActivity, profile

from backends.direct.ligero import protocol as protocol_mod
from backends.direct.ligero.relations import RELATIONS
from backends.direct.ligero.relchain import (HashedRelationRunner, RelationChainRunner, SharedHashedRunner, instances,
                                             instances_digest, tile_digest, tile_instances)

auth = sys.argv[1]
relname = sys.argv[2] if len(sys.argv) > 2 else "fp8-ada"
depth = int(sys.argv[3]) if len(sys.argv) > 3 else 4
warm = int(sys.argv[4]) if len(sys.argv) > 4 else 3
rel = RELATIONS[relname]
batch, total = 16384, 4096
per = batch // rel.steps
n_proofs = -(-total // per)
cls = {"excluded": RelationChainRunner, "included-hash": HashedRelationRunner, "included-hash-shared": SharedHashedRunner}[auth]
R = cls(rel, "cuda", -128.0, 2, n_proofs=n_proofs, zk=False, mode=protocol_mod.MODE_INTERACTIVE)
if auth == "included-hash-shared":
    data, xr, wc = tile_instances(rel, 64, 64, cache="/workspace/instances-cache")
    dig = tile_digest(rel, 64, 64) if rel.frozen_tier else instances_digest(rel, total)
    R.commit_vus(data, manifest_sha256=dig, cache=f"/workspace/auth-cache-shared-{relname}", tile=(64, 64), x_rows=xr, w_cols=wc)
else:
    data = instances(rel, total, cache="/workspace/instances-cache")
    if auth == "included-hash":
        R.commit_vus(data, manifest_sha256=instances_digest(rel, total), cache=f"/workspace/auth-cache-hash-{relname}")
subs = [(lo, min(lo + per, total)) for lo in range(0, total, per)]
l = R.layout(per).l
batches = [data[lo:hi] for lo, hi in subs]
ids = [range(lo, hi) for lo, hi in subs]
fac = lambda i: protocol_mod.Coins.sample()  # noqa: E731
for _ in range(warm):
    R.prove_vus_many(batches, fac, depth=depth, min_l=l, vu_ids_list=ids)
torch.cuda.synchronize()
with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
    t0 = time.perf_counter()
    _, wall = R.prove_vus_many(batches, fac, depth=depth, min_l=l, vu_ids_list=ids)
    torch.cuda.synchronize()
    t1 = time.perf_counter()
iv, per_name = [], {}
for e in prof.events():
    if e.device_type == torch.autograd.DeviceType.CUDA:
        s, d = e.time_range.start, e.time_range.end
        if d > s:
            iv.append((s, d))
            per_name[e.name] = per_name.get(e.name, 0.0) + (d - s)
iv.sort()
busy, cur_s, cur_e = 0.0, None, None
for s, d in iv:
    if cur_e is None or s > cur_e:
        if cur_e is not None:
            busy += cur_e - cur_s
        cur_s, cur_e = s, d
    else:
        cur_e = max(cur_e, d)
if cur_e is not None:
    busy += cur_e - cur_s
span = (iv[-1][1] - iv[0][0]) if iv else 0.0
print(f"{auth} {relname} depth {depth}: pass wall {wall:.4f} (profiled; host {t1 - t0:.4f}); device span {span / 1e6:.4f} s, "
      f"busy (union) {busy / 1e6:.4f} s, kernel+copy sum {sum(per_name.values()) / 1e6:.4f} s, {len(iv)} activities")
for n, v in sorted(per_name.items(), key=lambda kv: -kv[1])[:25]:
    print(f"  {v / 1e3:8.2f} ms  {n[:110]}")
