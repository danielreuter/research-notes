import time, numpy as np, torch, cupy as cp
from backends.direct.ligero import encode_simt as es
from backends.direct.ligero.field import P
dev = torch.device("cuda")
R, l = 3328, 16384
n = 4 * l
g = torch.Generator().manual_seed(3)
W = torch.randint(0, P, (R, l), generator=g).to(dev)
out = torch.empty((R, n), dtype=torch.int32, device=dev)
def timeit(fn, reps=9):
    fn(); torch.cuda.synchronize(); ts = []
    for _ in range(reps):
        torch.cuda.synchronize(); t0 = time.perf_counter(); fn(); torch.cuda.synchronize(); ts.append(time.perf_counter() - t0)
    ts.sort(); return ts[len(ts) // 2]
base = es.LigeroEncoderSIMT(l, n, 0, dev, stage=True)
ref = base.encode(W, out=torch.empty_like(out))[0].clone()
SRC0 = es._SRC
def run(name, patch=lambda s: s, exact=True, blocks=None, stage=True):
    es._SRC = patch(SRC0)
    try:
        e = es.LigeroEncoderSIMT(l, n, 0, dev, stage=stage)
    except Exception as ex:
        print(f"{name:52s} COMPILE FAIL {str(ex)[:400]}"); es._SRC = SRC0; return
    es._SRC = SRC0
    if blocks: e.blocks = blocks
    k = e.kernel
    out.zero_()
    t = timeit(lambda: e.encode(W, out=out))
    same = torch.equal(out, ref)
    print(f"{name:52s} {t*1e3:6.3f} ms  regs={k.num_regs} local={k.local_size_bytes}B blocks={e.blocks} "
          f"{'bit-exact' if same else ('differs (expected)' if not exact else 'DIFFERS !!!')}", flush=True)
GRP = """#pragma unroll
                for (int s = 0; s < 16; ++s) {
                    const int i = t + THREADS * s;
                    const unsigned v0 = sg[i], v1 = sg[K + i], v2 = sg[2 * K + i];"""
assert GRP in SRC0
U = lambda k: (lambda s: s.replace(GRP, GRP.replace("#pragma unroll\n", f"#pragma unroll {k}\n")))
FS = 'asm volatile("st.global.L2::cache_hint.v4.u32 [%%0], {%%1, %%2, %%3, %%4}, %%5;"\n                                 :: "l"(a), "r"(v0), "r"(v1), "r"(v2), "r"(r[s]), "l"(pol) : "memory");'
UNST = 'asm volatile("st.global.L2::cache_hint.u32 [%%0], %%1, %%2;" :: "l"(a), "r"(r[s]), "l"(pol) : "memory");\n            }\n#else'
assert UNST in SRC0
for rep in range(2):
    run("unstaged (4-B stores, evict_last)", stage=False)
    run("(!) unstaged, coset-major store", lambda s: s.replace(UNST, 'dst[c * K + t + THREADS * s] = r[s];\n            }\n#else'), exact=False, stage=False)
    run("staged, read-back unroll 2", U(2))
    run("staged, read-back unroll 4", U(4))
    run("staged, read-back unroll 8", U(8))
    run("staged, unroll 4, final store plain uint4", lambda s: U(4)(s).replace(FS, "*reinterpret_cast<uint4*>(a) = make_uint4(v0, v1, v2, r[s]);"))
