"""Staged-store ablations (timing only where marked (!)): where do the ~0.37 ms between staged (1.86) and coset-major (1.49) go?"""
import time, numpy as np, torch, cupy as cp
from backends.direct.ligero import encode_simt as es
from backends.direct.ligero.field import P
dev = torch.device("cuda")
R, l = 3328, 16384
n = 4 * l
g = torch.Generator().manual_seed(3)
W = torch.randint(0, P, (R, l), generator=g).to(dev)
out = torch.empty((R, n), dtype=torch.int32, device=dev)
def timeit(fn, reps=7):
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
    t = timeit(lambda: e.encode(W, out=out))
    same = torch.equal(out, ref)
    print(f"{name:52s} {t*1e3:6.3f} ms  regs={k.num_regs} local={k.local_size_bytes}B blocks={e.blocks} "
          f"{'bit-exact' if same else ('differs (expected)' if not exact else 'DIFFERS !!!')}", flush=True)
run("staged (current default)")
run("unstaged (4-B stores, evict_last)", stage=False)
run("unstaged, grid 132", stage=False, blocks=132)
RB = "const unsigned v0 = sg[i], v1 = sg[K + i], v2 = sg[2 * K + i];"
assert RB in SRC0
run("(!) staged, no read-back (v = r)", lambda s: s.replace(RB, "const unsigned v0 = r[s] ^ 1u, v1 = r[s] ^ 2u, v2 = r[s] ^ 3u;"), exact=False)
ST = 'asm volatile("st.global.L2::cache_hint.u32 [%%0], %%1, %%2;" :: "l"(a), "r"(r[s]), "l"(pol) : "memory");\n                }\n            } else {'
assert ST in SRC0, "staging store anchor"
run("(!) staged, no staging stores (read-back garbage)", lambda s: s.replace(ST, 'if (r[s] == 0xFFFFFFFFu) *a = r[s];\n                }\n            } else {'), exact=False)
# read-back via ld.global.L2::cache_hint evict_first? plain ld with .cg (L2 only)
run("staged, read-back __ldcg", lambda s: s.replace(RB, "const unsigned v0 = __ldcg(sg + i), v1 = __ldcg(sg + K + i), v2 = __ldcg(sg + 2 * K + i);"))
# read-back in 4 groups with the loads hoisted per group
GRP = """#pragma unroll
                for (int s = 0; s < 16; ++s) {
                    const int i = t + THREADS * s;
                    const unsigned v0 = sg[i], v1 = sg[K + i], v2 = sg[2 * K + i];"""
assert GRP in SRC0
run("staged, read-back unroll 1", lambda s: s.replace(GRP, GRP.replace("#pragma unroll\n", "#pragma unroll 1\n")))
run("staged, read-back unroll 4", lambda s: s.replace(GRP, GRP.replace("#pragma unroll\n", "#pragma unroll 4\n")))
# staging stores without the evict_last policy / with plain stores
run("staged, plain staging stores (no policy)", lambda s: s.replace(ST, '*a = r[s];\n                }\n            } else {'))
# final store default policy instead of evict_first
FS = 'asm volatile("st.global.L2::cache_hint.v4.u32 [%%0], {%%1, %%2, %%3, %%4}, %%5;"\n                                 :: "l"(a), "r"(v0), "r"(v1), "r"(v2), "r"(r[s]), "l"(pol) : "memory");'
assert FS in SRC0
run("staged, plain uint4 final store", lambda s: s.replace(FS, "*reinterpret_cast<uint4*>(a) = make_uint4(v0, v1, v2, r[s]);"))
run("(!) staged, no final store", lambda s: s.replace(FS, "if ((v0 ^ v1 ^ v2 ^ r[s]) == 0xFFFFFFFFu) *a = v0;"), exact=False)
