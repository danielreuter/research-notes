"""The fused witness of REL+sha256: interpreter / level mode, level count, ops per level, and W time at a few l; why the
levels are None when they are (the first row read before written / written twice)."""
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.getcwd())
from backends.direct.ligero import hashchain, witness_device as wd  # noqa: E402
from backends.direct.ligero.relations import relation  # noqa: E402

rel = relation(os.environ.get("REL", "fp8-hopper-x4"))
t0 = time.perf_counter()
hr = hashchain.compose(rel, "sha256")
sys_ = hr.sys
print(f"compose {time.perf_counter() - t0:.1f}s: m={sys_.m} program ops {len(sys_.program)} hints {len(sys_.hints)} "
      f"pins {len(sys_.pins)}", flush=True)
prog = wd._program(sys_)
J, C, ops, opd, sel = wd._interp_tables(sys_, prog)
print(f"interp tables: ops {len(ops)} terms {len(J)} (INTERP_OPS {wd.INTERP_OPS}, levels on {wd.INTERP_LEVELS})", flush=True)
lv = wd._interp_levels(ops, opd, J, sys_.m)
if lv is None:
    m = sys_.m
    written = np.zeros(m, dtype=bool)
    names = {r.idx: r.name for r in sys_.rows}
    for i, o in enumerate(ops):
        kind, idx = int(o[0]), int(o[1])
        reads = () if kind in (0, 1) else (o[2], o[3]) if kind == 2 else (o[3],) if kind in (3, 4) else (o[2],)
        bad = None
        for k in reads:
            off, n = int(opd[k, 0]), int(opd[k, 1])
            js = J[off:off + n]
            nr = js[~written[js]] if n else []
            if len(nr):
                bad = f"op {i} kind {kind} -> row {idx} ({names.get(idx)}) reads unwritten row {int(nr[0])} ({names.get(int(nr[0]))})"
                break
        nw = int(o[2]) if kind in (3, 4) else 1
        if bad is None and written[idx:idx + nw].any():
            bad = f"op {i} kind {kind} writes row {idx} ({names.get(idx)}) twice"
        if bad:
            print("LEVELS NONE:", bad, flush=True)
            break
        written[idx:idx + nw] = True
else:
    order, counts = lv
    nz = counts[counts > 0]
    print(f"levels {len(nz)}; ops per level min {nz.min()} median {int(np.median(nz))} max {nz.max()}", flush=True)
fw = wd.fused_for(sys_, "cuda")
print(f"fused: interp {fw.interp} levels {None if fw.levels is None else len(fw.levels)} hooks {len(fw.hooks)}", flush=True)
for l in (4096, 8192, 16384):
    pub = torch.zeros((len(sys_.pins), l), dtype=torch.int64, device="cuda")
    hints = torch.zeros((len(sys_.hints), l), dtype=torch.int64, device="cuda")
    fw.run(pub, hints)
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(3):
        fw.run(pub, hints)
    torch.cuda.synchronize()
    print(f"W at l={l}: {(time.perf_counter() - t0) / 3 * 1e3:.1f} ms", flush=True)

# one l = 8192 proof (682 VUs): the prover's stage timings twice, then the Python verify under cProfile
import cProfile  # noqa: E402
import pstats  # noqa: E402
from types import SimpleNamespace  # noqa: E402

from backends.direct.ligero import relchain as rc  # noqa: E402

n = int(os.environ.get("NVU", "682"))
args = SimpleNamespace(device="cuda", target=-128.0, rate_log2=2, zk=True, mode="interactive", auth="included-hash",
                       leaf="sha256")
R = rc.make_runner(args, rel)
data = rc.instances(rel, n, procs=16)
R.commit_vus(data, manifest_sha256=rc.instances_digest(rel, n))
for i in range(3):
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    proof, pubs, lay = R.prove_vus(data, check=False, vu_ids=range(n))
    torch.cuda.synchronize()
    print(f"prove {i}: {time.perf_counter() - t0:.3f}s l={lay.l} "
          f"{ {k: round(v, 3) for k, v in proof.timings.items() if isinstance(v, float)} }", flush=True)
pr = cProfile.Profile()
t0 = time.perf_counter()
pr.enable()
ok, why = R.verify_vus(proof, pubs, lay)
pr.disable()
print(f"verify {ok} {why} {time.perf_counter() - t0:.2f}s", flush=True)
pstats.Stats(pr).sort_stats("cumulative").print_stats(25)
pstats.Stats(pr).sort_stats("tottime").print_stats(15)
