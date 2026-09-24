"""share-logup-3: which eager ops (with input shapes) dominate the device time of the shared pair's prover, one sub-batch,
tests graph OFF so the ops are attributable.  usage: prof_shapes.py [auth=included-hash-shared] [rel=fp8-ada] [top=30]"""
import sys

import torch
from torch.profiler import ProfilerActivity, profile

from backends.direct.ligero import protocol as protocol_mod
from backends.direct.ligero.relations import RELATIONS
from backends.direct.ligero.relchain import RelationChainRunner, SharedHashedRunner, instances, tile_digest, tile_instances, instances_digest

auth = sys.argv[1] if len(sys.argv) > 1 else "included-hash-shared"
relname = sys.argv[2] if len(sys.argv) > 2 else "fp8-ada"
top = int(sys.argv[3]) if len(sys.argv) > 3 else 30
protocol_mod.TESTS_GRAPH = False
rel = RELATIONS[relname]
batch, total = 16384, 4096
per = batch // rel.steps
n_proofs = -(-total // per)
if auth == "included-hash-shared":
    R = SharedHashedRunner(rel, "cuda", -128.0, 2, n_proofs=n_proofs, zk=False, mode=protocol_mod.MODE_INTERACTIVE)
    data, xr, wc = tile_instances(rel, 64, 64, cache="/workspace/instances-cache")
    dig = tile_digest(rel, 64, 64) if rel.frozen_tier else instances_digest(rel, total)
    R.commit_vus(data, manifest_sha256=dig, cache=f"/workspace/auth-cache-shared-{relname}", tile=(64, 64), x_rows=xr, w_cols=wc)
else:
    R = RelationChainRunner(rel, "cuda", -128.0, 2, n_proofs=n_proofs, zk=False, mode=protocol_mod.MODE_INTERACTIVE)
    data = instances(rel, total, cache="/workspace/instances-cache")
l = R.layout(per).l
fac = lambda i: protocol_mod.Coins.sample()  # noqa: E731
for _ in range(2):
    R.prove_vus_many([data[:per]], fac, depth=1, min_l=l, vu_ids_list=[range(0, per)])
torch.cuda.synchronize()
with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=True) as prof:
    R.prove_vus_many([data[:per]], fac, depth=1, min_l=l, vu_ids_list=[range(0, per)])
    torch.cuda.synchronize()
ka = prof.key_averages(group_by_input_shape=True)
rows = sorted(ka, key=lambda e: -getattr(e, "device_time_total", getattr(e, "cuda_time_total", 0)))
print(f"{auth} {relname}: top ops by device time (one sub-batch, eager tests)")
n = 0
for e in rows:
    if not e.key.startswith("aten::"):
        continue
    dt = getattr(e, "self_device_time_total", getattr(e, "self_cuda_time_total", 0))
    if dt <= 0:
        continue
    print(f"  {dt / 1e3:8.3f} ms  x{e.count:<4d} {e.key:28s} {str(e.input_shapes)[:120]}")
    n += 1
    if n >= top:
        break
