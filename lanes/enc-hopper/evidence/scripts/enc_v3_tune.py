import sys, time, re
import numpy as np, torch, cupy as cp
from backends.direct.ligero import encode_simt as es
from backends.direct.ligero.field import P
dev = torch.device("cuda")
sms = cp.cuda.runtime.getDeviceProperties(0)["multiProcessorCount"]
def timeit(fn, reps=7):
    fn(); torch.cuda.synchronize(); ts = []
    for _ in range(reps):
        torch.cuda.synchronize(); t0 = time.perf_counter(); fn(); torch.cuda.synchronize(); ts.append(time.perf_counter() - t0)
    ts.sort(); return ts[0]
def run(name, src, l=16384, R=3328, tp=0, exact=True, bps=4):
    n = 4 * l; threads = l // 16
    g = torch.Generator().manual_seed(5)
    W = torch.randint(0, P, (R, l), generator=g, dtype=torch.int64).to(torch.int32).to(dev)
    base = es.LigeroEncoderSIMT(l, n, 0, dev)
    out_ref = torch.empty((R, n), dtype=torch.int32, device=dev); base.encode(W, out=out_ref)
    params = {"pinv": es._P_INV_MOD_R, "k": l, "logk": l.bit_length() - 1, "threads": threads, "logt": threads.bit_length() - 1, "tp": tp, "kinv_mont": 1}
    smem = 8 * l
    try:
        k = cp.RawKernel(src % params, "rs_encode_ligero", options=("-std=c++17",)); k.max_dynamic_shared_size_bytes = smem; k.compile()
    except Exception as e:
        print(f"{name:50s} COMPILE FAIL {str(e)[:400]}"); return
    out = torch.empty((R, n), dtype=torch.int32, device=dev)
    Win = cp.asarray(W).view(cp.uint32); O = cp.asarray(out).view(cp.uint32)
    mask = cp.zeros((R, max(tp, 1)), dtype=cp.uint32)
    go = lambda: k((min(sms * bps, R),), (threads,), (Win, O, np.uint64(0), mask, base.tw_inv, base.tw_fwd, base.coset, base.mask_tw, np.int32(R)), shared_mem=smem)
    t = timeit(go); same = bool(torch.equal(out, out_ref))
    print(f"{name:50s} l={l:5d} {t*1e3:7.3f} ms regs={k.num_regs} spill={k.local_size_bytes}B {'bit-exact' if same else ('differs (expected)' if not exact else 'DIFFERS !!!')}", flush=True)
S0 = es._SRC
run("v3", S0)
run("v3 blocks=1xSM", S0, bps=1)
run("v3 blocks=2xSM", S0, bps=2)
run("v3 blocks=8xSM", S0, bps=8)
run("v3 groups unroll 2", S0.replace("#pragma unroll 1          /* unrolled", "#pragma unroll 2          /* unrolled"))
run("v3 __ldg twiddles", S0.replace("const unsigned w = ldtw(&tw[m + (idx & (m - 1))]);", "const unsigned w = __ldg(&tw[m + (idx & (m - 1))]);"))
run("(!) v3 no store", S0.replace("for (int s = 0; s < 16; ++s) dst[((size_t)(t + THREADS * s) << 2) | c] = r[s];", "for (int s = 0; s < 16; ++s) if (r[s] == 0xFFFFFFFFu) dst[0] = 1;"), exact=False)
run("(!) v3 coset-major store", S0.replace("for (int s = 0; s < 16; ++s) dst[((size_t)(t + THREADS * s) << 2) | c] = r[s];", "for (int s = 0; s < 16; ++s) dst[(size_t)c * K + t + THREADS * s] = r[s];"), exact=False)
LB = S0.replace("extern \"C\" __global__ void __launch_bounds__(THREADS)", "extern \"C\" __global__ void __launch_bounds__(THREADS, (THREADS <= 512 ? 2 : 1))")
run("v3 l=8192", S0, l=8192)
run("v3 l=8192 launch_bounds(T,2)", LB, l=8192)
run("v3 l=4096", S0, l=4096, R=1619)
run("v3 l=4096 launch_bounds(T,2)", LB, l=4096, R=1619)
run("v3 l=4096 launch_bounds(T,4)", S0.replace("extern \"C\" __global__ void __launch_bounds__(THREADS)", "extern \"C\" __global__ void __launch_bounds__(THREADS, (THREADS <= 256 ? 4 : 1))"), l=4096, R=1619)
