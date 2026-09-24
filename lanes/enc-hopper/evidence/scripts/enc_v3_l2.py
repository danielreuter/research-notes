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
l, R = 16384, 3328; n = 4 * l; threads = 1024
g = torch.Generator().manual_seed(5)
W = torch.randint(0, P, (R, l), generator=g, dtype=torch.int64).to(torch.int32).to(dev)
base = es.LigeroEncoderSIMT(l, n, 0, dev)
out_ref = torch.empty((R, n), dtype=torch.int32, device=dev); base.encode(W, out=out_ref)
def run(name, src, exact=True, blocks=None, R_=R):
    params = {"pinv": es._P_INV_MOD_R, "k": l, "logk": 14, "threads": threads, "logt": 10, "tp": 0, "kinv_mont": 1}
    smem = 8 * l
    try:
        k = cp.RawKernel(src % params, "rs_encode_ligero", options=("-std=c++17",)); k.max_dynamic_shared_size_bytes = smem; k.compile()
    except Exception as e:
        print(f"{name:50s} COMPILE FAIL {str(e)[:600]}"); return
    out = torch.empty((R, n), dtype=torch.int32, device=dev)
    Win = cp.asarray(W).view(cp.uint32); O = cp.asarray(out).view(cp.uint32)
    mask = cp.zeros((R, 1), dtype=cp.uint32)
    b = blocks or sms * 4
    go = lambda: k((b,), (threads,), (Win, O, np.uint64(0), mask, base.tw_inv, base.tw_fwd, base.coset, base.mask_tw, np.int32(R_)), shared_mem=smem)
    t = timeit(go); same = bool(torch.equal(out[:R_], out_ref[:R_]))
    print(f"{name:50s} blocks={b:4d} rows={R_} {t*1e3:7.3f} ms  SM-us/row={t*1e6*min(b,sms)/R_:6.1f} {'bit-exact' if same else ('differs (expected)' if not exact else 'DIFFERS !!!')}", flush=True)
S0 = es._SRC
STORE = "for (int s = 0; s < 16; ++s) dst[((size_t)(t + THREADS * s) << 2) | c] = r[s];"
assert STORE in S0
for b in (528, 132, 66, 33):
    run("v3", S0, blocks=b)
for b in (132, 66, 33):
    run("(!) v3 coset-major", S0.replace(STORE, "for (int s = 0; s < 16; ++s) dst[(size_t)c * K + t + THREADS * s] = r[s];"), exact=False, blocks=b)
# evict_last policy on the codeword stores
EL = S0.replace(STORE, """unsigned long long pol; asm volatile("createpolicy.fractional.L2::evict_last.b64 %%0, 1.0;" : "=l"(pol));
            #pragma unroll
            for (int s = 0; s < 16; ++s) { unsigned* a = dst + (((size_t)(t + THREADS * s)) << 2) + c; asm volatile("st.global.L2::cache_hint.u32 [%%0], %%1, %%2;" :: "l"(a), "r"(r[s]), "l"(pol) : "memory"); }""")
run("v3 evict_last stores", EL, blocks=528)
run("v3 evict_last stores", EL, blocks=132)
# evict_first (streaming) on the input row loads + tables stay default
EF = S0.replace(STORE, """#pragma unroll
            for (int s = 0; s < 16; ++s) __stcs(dst + (((size_t)(t + THREADS * s)) << 2) + c, r[s]);""")
run("v3 __stcs stores", EF, blocks=528)
WT = S0.replace(STORE, """#pragma unroll
            for (int s = 0; s < 16; ++s) __stwt(dst + (((size_t)(t + THREADS * s)) << 2) + c, r[s]);""")
run("v3 __stwt stores", WT, blocks=528)
