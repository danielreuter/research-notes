import time, torch, numpy as np
from backends.direct.ligero import hashchain, witness as wmod
from backends.direct.ligero.relations import relation
from backends.direct.ligero.relchain import HashedRelationRunner, make_runner
import sys as _s
name = _s.argv[1] if len(_s.argv) > 1 else "fp8-ada"
rel = relation(name)
hr = hashchain.compose(rel)
print("hooks", hr.sys.witness_hooks, "rows", len(hr.sys.witness_hooks[0].rows))
# random hint/pub rows of a small l: the witness program for random *bits* is well defined (bits are booleans, caps arbitrary)
l = 2048
g = torch.Generator(device="cpu").manual_seed(1)
pub = {name: torch.randint(0, 2, (l,), generator=g).to(torch.int64) for _, name in hr.sys.pins}
hints = []
for _, nm in hr.sys.hints:
    if ".b" in nm and nm.split(".")[-1][1:].isdigit():
        hints.append(torch.randint(0, 2, (l,), generator=g))
    else:
        hints.append(torch.randint(0, 2**31 - 2**27, (l,), generator=g))
hints = torch.stack(hints).to(torch.int64)
pub_c = {k: v.cuda() for k, v in pub.items()}
hints_c = hints.cuda()
wmod.IMPL = "legacy"; wmod.USE_CUDA_GRAPH = False
t = time.time(); W_ref = wmod.build_witness(hr.sys, pub_c, hints_c, "cuda"); torch.cuda.synchronize(); print("torch program", round(time.time() - t, 2))
wmod.IMPL = "device"
from backends.direct.ligero import witness_device as wd
t = time.time(); f = wd.fused_for(hr.sys, "cuda"); torch.cuda.synchronize(); print("compile fused", round(time.time() - t, 1), "tables", f.tables is not None, "src kB", len(f.src) // 1000)
t = time.time(); W_dev = wmod.build_witness(hr.sys, pub_c, hints_c, "cuda"); torch.cuda.synchronize(); print("fused+hook first", round(time.time() - t, 2))
torch.cuda.synchronize(); t = time.time()
for _ in range(5): W_dev = wmod.build_witness(hr.sys, pub_c, hints_c, "cuda")
torch.cuda.synchronize(); print("fused+hook per call (l=%d)" % l, round((time.time() - t) / 5 * 1000, 2), "ms")
eq = torch.equal(W_ref.to(torch.int64), W_dev.to(torch.int64))
print("EQUAL", eq)
if not eq:
    bad = (W_ref.to(torch.int64) != W_dev.to(torch.int64)).any(dim=1).nonzero().flatten()
    print("bad rows", bad[:10].tolist(), "n", len(bad), [hr.sys.rows[i].name for i in bad[:5].tolist()])
# l = 16384 timing
l2 = 16384
pub2 = {k: torch.randint(0, 2, (l2,), device="cuda", dtype=torch.int64) for k in pub}
h2 = torch.stack([torch.randint(0, 2, (l2,), device="cuda", dtype=torch.int64) if (".b" in nm and nm.split(".")[-1][1:].isdigit()) else torch.randint(0, 2**31 - 2**27, (l2,), device="cuda", dtype=torch.int64) for _, nm in hr.sys.hints])
wmod.build_witness(hr.sys, pub2, h2, "cuda"); torch.cuda.synchronize(); t = time.time()
for _ in range(10): wmod.build_witness(hr.sys, pub2, h2, "cuda")
torch.cuda.synchronize(); print("fused+hook per call (l=16384)", round((time.time() - t) / 10 * 1000, 2), "ms")
