"""A/B on the committed encode_simt kernel (lane enc-hopper): store strategy, grid, variants.  (!) = wrong output, attribution."""
import re, sys, time
import numpy as np
import torch
import cupy as cp
from backends.direct.ligero import encode_simt as es
from backends.direct.ligero.field import P

l = int(sys.argv[1]) if len(sys.argv) > 1 else 16384
R = int(sys.argv[2]) if len(sys.argv) > 2 else 3328
n = 4 * l
dev = torch.device("cuda")
g = torch.Generator().manual_seed(5)
W = torch.randint(0, P, (R, l), generator=g, dtype=torch.int64).to(torch.int32).to(dev)
sms = cp.cuda.runtime.getDeviceProperties(0)["multiProcessorCount"]
base = es.LigeroEncoderSIMT(l, n, 0, dev)
out_ref = torch.empty((R, n), dtype=torch.int32, device=dev); base.encode(W, out=out_ref)
gb = R * n * 4 / 1e9


def timeit(fn, reps=9):
    fn(); torch.cuda.synchronize()
    ts = []
    for _ in range(reps):
        torch.cuda.synchronize(); t0 = time.perf_counter(); fn(); torch.cuda.synchronize(); ts.append(time.perf_counter() - t0)
    ts.sort(); return ts[0], ts[len(ts) // 2]


def run(name, src, threads=1024, smem=None, exact=True, blocks_per_sm=4, tp=0):
    params = {"pinv": es._P_INV_MOD_R, "k": l, "logk": l.bit_length() - 1, "threads": threads, "logt": threads.bit_length() - 1,
              "tp": tp, "kinv_mont": 1}
    smem = smem or 4 * (3 * l + 32)
    try:
        k = cp.RawKernel(src % params, "rs_encode_ligero", options=("-std=c++17",))
        k.max_dynamic_shared_size_bytes = smem
        k.compile()
    except Exception as e:  # noqa
        print(f"{name:44s} COMPILE FAIL: {str(e)[:300]}"); return None
    blocks = min(sms * blocks_per_sm, R)
    out = torch.empty((R, n), dtype=torch.int32, device=dev)
    Win = cp.asarray(W).view(cp.uint32); O = cp.asarray(out).view(cp.uint32)
    def go():
        k((blocks,), (threads,), (Win, O, np.uint64(0), np.uint64(0), base.tw_inv, base.tw_fwd, base.coset, base.mask_tw, np.int32(R)), shared_mem=smem)
    try:
        tmin, tmed = timeit(go)
    except Exception as e:  # noqa
        print(f"{name:44s} RUN FAIL: {str(e)[:200]}"); return None
    same = bool(torch.equal(out, out_ref))
    print(f"{name:44s} min {tmin*1e3:7.3f} med {tmed*1e3:7.3f} ms ({gb/tmin:5.0f} GB/s) regs={k.num_regs} spill={k.local_size_bytes}B smem={smem//1024}K "
          f"{'bit-exact' if same else ('differs (expected)' if not exact else 'DIFFERS !!!')}", flush=True)
    return tmin


S0 = es._SRC
PAIRED = """            if ((c & 1) == 0) {
                #pragma unroll
                for (int s = 0; s < PER; ++s) y[t + THREADS * s] = r[s];
            } else {
                #pragma unroll
                for (int s = 0; s < PER; ++s) {
                    const int j = t + THREADS * s;
                    const uint2 v = make_uint2(y[j], r[s]);
                    *reinterpret_cast<uint2*>(dst + (((size_t)j) << 2) + (c - 1)) = v;
                }
            }"""
assert PAIRED in S0
DIRECT = """            #pragma unroll
            for (int s = 0; s < PER; ++s) dst[((size_t)(t + THREADS * s) << 2) | c] = r[s];"""
NOSTORE = """            #pragma unroll
            for (int s = 0; s < PER; ++s) if (r[s] == 0xFFFFFFFFu) dst[0] = 1;"""
COSETMAJOR = """            #pragma unroll
            for (int s = 0; s < PER; ++s) dst[(size_t)c * K + t + THREADS * s] = r[s];"""
if __name__ == "__main__":
    print(f"l={l} R={R} sms={sms}")
    run("committed (paired 8B stores, y)", S0)
    run("committed, blocks=1xSM", S0, blocks_per_sm=1)
    run("committed, blocks=2xSM", S0, blocks_per_sm=2)
    run("direct 4B stores (no y)", S0.replace(PAIRED, DIRECT), smem=4 * (2 * l + 32))
    run("(!) no store", S0.replace(PAIRED, NOSTORE), smem=4 * (2 * l + 32), exact=False)
    run("(!) coset-major coalesced store", S0.replace(PAIRED, COSETMAJOR), smem=4 * (2 * l + 32), exact=False)
    run("committed tp=256", S0, tp=256)
