"""lane fp4-decode-3: time the hashed pipeline test's _setup steps on the pod, dumping every thread's stack every 15 s."""
import faulthandler
import sys
import time

faulthandler.dump_traceback_later(15, repeat=True, file=sys.stderr)
t0 = time.perf_counter()
import torch  # noqa: E402

from backends.direct.ligero import protocol as protocol_mod  # noqa: E402
from backends.direct.ligero.fp4.hashed import FP4_HASHED  # noqa: E402
from backends.direct.ligero.relchain import HashedRelationRunner, instances  # noqa: E402

print(f"imports {time.perf_counter() - t0:.1f}s cuda={torch.cuda.get_device_name(0)}", flush=True)
t = time.perf_counter()
R = HashedRelationRunner(FP4_HASHED, "cuda", -128.0, 2, n_proofs=5, zk=False, mode=protocol_mod.MODE_INTERACTIVE)
print(f"runner {time.perf_counter() - t:.1f}s", flush=True)
t = time.perf_counter()
data = instances(FP4_HASHED, 171)
print(f"instances(171) {time.perf_counter() - t:.1f}s", flush=True)
t = time.perf_counter()
R.commit_vus(data)
print(f"commit_vus {time.perf_counter() - t:.1f}s", flush=True)
per = 1024 // FP4_HASHED.steps
subs = [(lo, min(lo + per, 171)) for lo in range(0, 171, per)]
l = R.layout(per).l
for k in range(2):
    t = time.perf_counter()
    lo, hi = subs[0]
    proof, pubs, lay = R.prove_vus(data[lo:hi], check=False, min_l=l, coins=protocol_mod.Coins.sample(), vu_ids=range(lo, hi))
    torch.cuda.synchronize()
    print(f"prove_vus seq #{k} {time.perf_counter() - t:.1f}s", flush=True)
if len(sys.argv) > 1:
    for k in range(2):
        t = time.perf_counter()
        R.prove_vus_many([data[lo:hi] for lo, hi in subs], lambda i: protocol_mod.Coins.sample(), depth=4, min_l=l,
                         vu_ids=[range(lo, hi) for lo, hi in subs])
        torch.cuda.synchronize()
        print(f"prove_vus_many depth 4 #{k} {time.perf_counter() - t:.1f}s", flush=True)
