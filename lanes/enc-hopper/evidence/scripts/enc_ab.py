"""A/B: candidate backends/direct/ligero/encode_simt.py vs the reference copy encode_simt_ref.py (committed kernel)."""
import sys, time, importlib
import numpy as np, torch, cupy as cp
from backends.direct.ligero import encode_simt as cand
from backends.direct.ligero import encode_simt_ref as ref
from backends.direct.ligero.field import P
dev = torch.device("cuda")
def timeit(fn, reps=9):
    fn(); torch.cuda.synchronize(); ts = []
    for _ in range(reps):
        torch.cuda.synchronize(); t0 = time.perf_counter(); fn(); torch.cuda.synchronize(); ts.append(time.perf_counter() - t0)
    ts.sort(); return ts[0], ts[len(ts)//2]
for l, R, tp in [(16384, 3328, 0), (16384, 3328, 256), (8192, 3328, 256), (4096, 1619, 256), (256, 64, 64)]:
    n = 4 * l
    g = torch.Generator().manual_seed(5)
    W = torch.randint(0, P, (R, l), generator=g, dtype=torch.int64).to(torch.int32).to(dev)
    mask = torch.randint(0, P, (R, tp), generator=g, dtype=torch.int64).to(torch.int32).to(dev) if tp else None
    a = ref.LigeroEncoderSIMT(l, n, tp, dev); b = cand.LigeroEncoderSIMT(l, n, tp, dev)
    Ua, Ca = a.encode(W, mask, want_coefs=bool(tp)); Ub, Cb = b.encode(W, mask, want_coefs=bool(tp))
    same = torch.equal(Ua, Ub) and (not tp or torch.equal(Ca, Cb))
    ta = timeit(lambda: a.encode(W, mask, want_coefs=bool(tp))); tb = timeit(lambda: b.encode(W, mask, want_coefs=bool(tp)))
    gb = R * n * 4 / 1e9
    print(f"l={l:5d} R={R:4d} tp={tp:3d}: ref min {ta[0]*1e3:7.3f} med {ta[1]*1e3:7.3f} | cand min {tb[0]*1e3:7.3f} med {tb[1]*1e3:7.3f} ms ({gb/tb[0]:4.0f} GB/s) "
          f"regs={b.kernel.num_regs} spill={b.kernel.local_size_bytes}B smem={b.smem//1024}K {'bit-exact' if same else 'DIFFERS !!!'}", flush=True)
