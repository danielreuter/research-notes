import sys, torch
sys.path.insert(0, "/workspace/src-hp2")
from backends.direct.ligero import witness_device as wd
from backends.direct.ligero.relations import relation
from backends.direct.ligero.relchain import RelationChainRunner
R = RelationChainRunner(relation("bf16-hopper"), "cuda", -128.0, 2, n_proofs=1, zk=False, mode="fiat-shamir")
for reg in (False, True):
    wd.REGISTER_ROWS = reg; wd._FW.clear()
    f = wd.fused_for(R.sys, "cuda")
    a = f.kernel.attributes
    print("REGISTER_ROWS", reg, {k: a[k] for k in ("num_regs", "local_size_bytes", "shared_size_bytes", "max_threads_per_block")})
    src = f.src.splitlines()
    print("  lines", len(src), "mulc", f.src.count("mulc("), "addp", f.src.count("addp("), "% P", f.src.count("% P"))
