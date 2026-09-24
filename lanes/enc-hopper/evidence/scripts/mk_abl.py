"""Merkle leaves ablation on the H100: is blake3_leaves issue-bound or memory-pattern-bound?"""
import time, numpy as np, torch, cupy as cp
from backends.direct.ligero import commit_gpu as cg
from backends.direct.ligero.field import P
dev = torch.device("cuda")
def timeit(fn, reps=9):
    fn(); torch.cuda.synchronize(); ts = []
    for _ in range(reps):
        torch.cuda.synchronize(); t0 = time.perf_counter(); fn(); torch.cuda.synchronize(); ts.append(time.perf_counter() - t0)
    ts.sort(); return ts[len(ts)//2]
R, N = 3328, 65536
g = torch.Generator().manual_seed(7)
U = torch.randint(0, P, (R, N), generator=g, dtype=torch.int64).to(torch.int32).to(dev)
ref = torch.as_tensor(cg.leaves(U), device=dev).view(torch.int32); torch.cuda.synchronize()
nchunks = (R + 255) // 256
def run(name, src, exact=True, threads=None, blocks=None, prefetch=0):
    try:
        mod = cp.RawModule(code=src, options=("-std=c++17", f"-DPREFETCH={prefetch}")); k = mod.get_function("blake3_leaves")
    except Exception as e:
        print(f"{name:44s} COMPILE FAIL {str(e)[:500]}"); return
    out = torch.empty((N, 8), dtype=torch.int32, device=dev)
    Ucp = cp.asarray(U).view(cp.uint32); O = cp.asarray(out).view(cp.uint32)
    th = threads or 32 * nchunks; bl = blocks or (N + 31) // 32
    go = lambda: k((bl,), (th,), (Ucp, np.int32(R), np.int32(N), np.int32(nchunks), O))
    t = timeit(go); same = bool(torch.equal(out, ref))
    print(f"{name:44s} {t*1e3:7.3f} ms ({R*N*4/t/1e9:6.0f} GB/s) regs={k.num_regs} {'bit-exact' if same else ('differs (expected)' if not exact else 'DIFFERS !!!')}", flush=True)
S = cg._SRC
run("leaves (current)", S)
LD = "for (int j = 0; j < 16; ++j) blk[j] = (j < have) ? __ldg(q + (size_t)j * N) : 0u;"
assert LD in S
run("(!) compute only (no loads)", S.replace(LD, "for (int j = 0; j < 16; ++j) blk[j] = (u32)(b * 16 + j) * 2654435761u ^ (u32)col;"), exact=False)
CM = "compress(cv, blk, (u64)w, (u32)have * 4u, flags);"
assert CM in S
run("(!) loads only (no compress)", S.replace(CM, "for (int j = 0; j < 16; ++j) cv[j & 7] ^= blk[j] + flags;"), exact=False)
# 512-byte rows: lane loads uint4 at columns 4*lane of a 128-column tile (blockIdx * 128), 16 rows -> fold; loads-only, memory-pattern probe
LD512 = """{ const u32* q4 = U + (size_t)(row0 + b * 16) * N + (size_t)blockIdx.x * 128 + 4 * lane;
              #pragma unroll
              for (int j = 0; j < 16; ++j) { uint4 v = (j < have) ? __ldg(reinterpret_cast<const uint4*>(q4 + (size_t)j * N)) : make_uint4(0,0,0,0); blk[j] = v.x ^ v.y ^ v.z ^ v.w; } }"""
run("(!) loads only, 512-B rows (uint4/lane)", S.replace(LD, LD512).replace(CM, "for (int j = 0; j < 16; ++j) cv[j & 7] ^= blk[j] + flags;"), exact=False, blocks=(N + 127) // 128)
run("(!) 512-B rows + compress (wrong msg)", S.replace(LD, LD512), exact=False, blocks=(N + 127) // 128)
# occupancy probe: launch_bounds 416 -> more regs?
run("launch_bounds(416,4)", S.replace("__launch_bounds__(512)", "__launch_bounds__(416, 4)"))
run("PREFETCH=1", S, prefetch=1)
print("--- occupancy variants")
run("launch_bounds(416,3) (48 regs)", S.replace("__launch_bounds__(512)", "__launch_bounds__(416, 3)"))
run("launch_bounds(416,2)", S.replace("__launch_bounds__(512)", "__launch_bounds__(416, 2)"))
run("maxrregcount-ish: launch_bounds(512,3)", S.replace("__launch_bounds__(512)", "__launch_bounds__(512, 3)"))
# rotr 16/8 via byte permute (PRMT) instead of funnel shift: different pipe?
S2 = S.replace("__device__ __forceinline__ u32 rotr32(u32 x, int n) { return __funnelshift_r(x, x, n); }",
 "__device__ __forceinline__ u32 rotr32(u32 x, int n) { return (n == 16) ? __byte_perm(x, x, 0x1032) : (n == 8) ? __byte_perm(x, x, 0x0321) : __funnelshift_r(x, x, n); }")
run("rotr16/8 via PRMT", S2)
run("rotr16/8 via PRMT + (416,3)", S2.replace("__launch_bounds__(512)", "__launch_bounds__(416, 3)"))
