"""cProfile of steady-state prove_vus (REL+sha256, NVU VUs at their l): where the ~2 s outside the itemized stages goes."""
import cProfile
import os
import pstats
import sys
import time
from types import SimpleNamespace

import torch

sys.path.insert(0, os.getcwd())
from backends.direct.ligero import relchain as rc  # noqa: E402
from backends.direct.ligero.relations import relation  # noqa: E402

rel = relation(os.environ.get("REL", "fp8-hopper-x4"))
n = int(os.environ.get("NVU", "682"))
args = SimpleNamespace(device="cuda", target=-128.0, rate_log2=2, zk=True, mode="interactive", auth="included-hash",
                       leaf=os.environ.get("LEAF", "sha256"))
R = rc.make_runner(args, rel)
data = rc.instances(rel, n, procs=16)
R.commit_vus(data, manifest_sha256=rc.instances_digest(rel, n))
for i in range(2):
    proof, pubs, lay = R.prove_vus(data, check=False, vu_ids=range(n))
torch.cuda.synchronize()
pr = cProfile.Profile()
t0 = time.perf_counter()
pr.enable()
proof, pubs, lay = R.prove_vus(data, check=False, vu_ids=range(n))
torch.cuda.synchronize()
pr.disable()
print(f"prove {time.perf_counter() - t0:.3f}s l={lay.l} {proof.timings}", flush=True)
pstats.Stats(pr).sort_stats("cumulative").print_stats(40)
pstats.Stats(pr).sort_stats("tottime").print_stats(20)
