import sys, time, torch
sys.path.insert(0, "/workspace/src-hp2")
from backends.direct.ligero import witness_device as wd
from backends.direct.ligero.relations import relation
from backends.direct.ligero.relchain import RelationChainRunner, instances
from torch.profiler import profile, ProfilerActivity
def sub_batch(rel_name, n_vus):
    rel = relation(rel_name)
    R = RelationChainRunner(rel, "cuda", -128.0, 2, n_proofs=1, zk=False, mode="fiat-shamir")
    data = instances(rel, n_vus, cache="/workspace/instances-cache")
    bd = R.marshal(data, 16384)
    hints = rel.hints(R.p, R.sys, bd["c_d"], bd["a_d"], bd["b_d"], bd["y_d"], "cuda")
    pub_rows = torch.stack([bd["pub"][name].to("cuda") for _, name in R.sys.pins]) % 2013265921
    return R, pub_rows, hints
for rel_name, n_vus in (("bf16-hopper", 170), ("fp8-hopper", 341)):
    R, pub_rows, hints = sub_batch(rel_name, n_vus)
    ref = None
    for reg in (False, True):
        wd.REGISTER_ROWS = reg; wd._FW.clear()
        t0 = time.perf_counter(); f = wd.fused_for(R.sys, "cuda"); tc = time.perf_counter() - t0
        W = f.run(pub_rows, hints); torch.cuda.synchronize()
        if ref is None: ref = W.clone()
        ok = torch.equal(W, ref)
        with profile(activities=[ProfilerActivity.CUDA]) as prof:
            for _ in range(10): f.run(pub_rows, hints)
            torch.cuda.synchronize()
        t = [e for e in prof.key_averages() if "witness_program" in e.key]
        us = (t[0].device_time_total if hasattr(t[0], "device_time_total") else t[0].cuda_time_total) / 10
        print(f"{rel_name} l={hints.shape[1]} m={R.sys.m} REGISTER_ROWS={reg}: {us/1e3:.3f} ms  equal={ok}  compile {tc:.1f}s  src {len(f.src)/1e6:.1f} MB")
