"""what the prover's ZK 'encode' lap spends besides the SIMT kernel (bf16-hopper shape: m=3292, Mrows=3328, l=16384, k=16640)"""
import time, torch
from backends.direct.ligero import encode_simt as es
from backends.direct.ligero.field import P, eval_on_coset, intt
from backends.direct.ligero.protocol import _add_zh_times
dev = torch.device("cuda")
def timeit(fn, reps=7):
    fn(); torch.cuda.synchronize(); ts = []
    for _ in range(reps):
        torch.cuda.synchronize(); t0 = time.perf_counter(); fn(); torch.cuda.synchronize(); ts.append(time.perf_counter() - t0)
    ts.sort(); return ts[len(ts)//2] * 1e3
m, Mrows, l, TP = 3292, 3328, 16384, 256
k, n = l + TP, 4 * l
g = torch.Generator().manual_seed(3)
W = torch.randint(0, P, (m, l), generator=g, dtype=torch.int64).to(dev)
SW = torch.randint(0, P, (m, TP), generator=g, dtype=torch.int64).to(dev)
maskrows = torch.randint(0, P, (Mrows - m, k), generator=g, dtype=torch.int64).to(dev)
enc = es.LigeroEncoderSIMT(l, n, TP, dev)
U = torch.empty((Mrows, n), dtype=torch.int32, device=dev)
print("zeros coefs (Mrows,k) int64      %.3f ms" % timeit(lambda: torch.zeros((Mrows, k), dtype=torch.int64, device=dev)))
coefs = torch.zeros((Mrows, k), dtype=torch.int64, device=dev)
print("kernel encode(W, SW, coefs, out)  %.3f ms" % timeit(lambda: enc.encode(W, SW, want_coefs=True, out=U[:m])))
_, C = enc.encode(W, SW, want_coefs=True, out=U[:m])
print("coefs[:m,:l] = C (int32->int64)   %.3f ms" % timeit(lambda: coefs.__setitem__((slice(0, m), slice(0, l)), C)))
print("_add_zh_times                     %.3f ms" % timeit(lambda: _add_zh_times(coefs[:m], SW, l)))
print("mask rows -> coefs                %.3f ms" % timeit(lambda: coefs.__setitem__((slice(m, Mrows), slice(0, k)), maskrows)))
print("eval_on_coset(coefs[m:]) 36 rows  %.3f ms" % timeit(lambda: eval_on_coset(coefs[m:], n)))
print("U[m:] = eval(...).to(int32)       %.3f ms" % timeit(lambda: U.__setitem__(slice(m, Mrows), eval_on_coset(coefs[m:], n).to(torch.int32))))
# what an all-kernel path would cost: the 36 mask rows via the SIMT encoder if fed as evaluations (upper bound: one more encode call of 36 rows)
Wm = torch.randint(0, P, (Mrows - m, l), generator=g, dtype=torch.int64).to(dev)
print("kernel encode 36 rows             %.3f ms" % timeit(lambda: enc.encode(Wm, maskrows[:, l:l + TP].contiguous(), out=U[m:])))
print("W int64 -> int32 contiguous       %.3f ms" % timeit(lambda: W.to(torch.int32).contiguous()))
print("U.to(int32).contiguous (no-op?)   %.3f ms" % timeit(lambda: U.to(torch.int32).contiguous()))
