"""micro.py: hint generation alone, fused vs the torch CUDA graph, one sub-batch at the bench's l (chain mode, real units)."""
import os, sys, time
import torch
from backends.direct.ligero import protocol as protocol_mod
from backends.direct.ligero.relchain import RelationChainRunner, instances
from backends.direct.ligero.relations import RELATIONS

def timeit(fn, reps=20):
    fn(); torch.cuda.synchronize()
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter(); fn(); torch.cuda.synchronize(); ts.append(time.perf_counter() - t0)
    ts.sort(); return ts[len(ts) // 2]

for name, l in [(n, int(x)) for n, x in (a.split(":") for a in sys.argv[1:])]:
    rel = RELATIONS[name]
    R = RelationChainRunner(rel, "cuda", -128.0, 2, zk=True, mode=protocol_mod.MODE_INTERACTIVE)
    per = l // rel.steps
    bd = R.marshal(instances(rel, per, procs=4, cache=os.environ.get("LIGERO_INSTANCES_CACHE")), min_l=l)
    args = (R.p, R.sys, bd["c_d"], bd["a_d"], bd["b_d"], bd["y_d"], "cuda")
    os.environ["LIGERO_FUSED_HINTS"] = "1"; tf = timeit(lambda: rel.hints(*args)); hf = rel.hints(*args)
    os.environ["LIGERO_FUSED_HINTS"] = "0"; tg = timeit(lambda: rel.hints(*args)); hg = rel.hints(*args)
    print(f"{name} l={bd['lay'].l} hints={hf.shape[0]} fused {tf*1e3:.2f} ms  graph {tg*1e3:.2f} ms  x{tg/tf:.1f}  equal={torch.equal(hf, hg)}", flush=True)
