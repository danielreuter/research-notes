"""wblock.py REL:L... : the fused witness kernel alone at each launch block size (LIGERO_WITNESS_BLOCK): W identical to the
256-thread launch, median time of 20 launches.  Random pub rows (mod p) and hints: the block size only changes which block a
column's thread sits in, so identity on random inputs is the property; the benches' verifiers + Rust check the real path."""
import os, sys, time

import torch

from backends.direct.ligero import witness_device as wd
from backends.direct.ligero.compile import P
from backends.direct.ligero.relations import RELATIONS

for name, l in [(n, int(x)) for n, x in (a.split(":") for a in sys.argv[1:])]:
    rel = RELATIONS[name]
    s = rel.compile(rel.params, True)
    fw = wd.FusedWitness(s, "cuda")
    torch.manual_seed(1)
    pub = torch.randint(0, P, (len(s.pins), l), dtype=torch.int64).cuda()
    hints = torch.randint(-2**20, 2**20, (len(s.hints), l), dtype=torch.int64).cuda()
    ref = None
    for b in (256, 128, 64, 32):
        os.environ["LIGERO_WITNESS_BLOCK"] = str(b)
        W = fw.run(pub, hints)
        torch.cuda.synchronize()
        ref = W if ref is None else ref
        ts = []
        for _ in range(20):
            t0 = time.perf_counter()
            fw.run(pub, hints)
            torch.cuda.synchronize()
            ts.append(time.perf_counter() - t0)
        ts.sort()
        print(f"{name} l={l} m={s.m} block={b:3d} {ts[10] * 1e3:7.3f} ms  equal={torch.equal(W, ref)}", flush=True)
