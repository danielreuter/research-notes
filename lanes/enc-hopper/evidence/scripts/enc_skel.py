"""Skeleton decomposition of the v3 encoder (timing only, (!) = wrong output): what the 1.77 ms at l=16384 is made of."""
import time, re, torch, cupy as cp
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
SRC0 = es._SRC
def run(name, patch=lambda s: s, **kw):
    es._SRC = patch(SRC0)
    try:
        e = es.LigeroEncoderSIMT(l, n, 0, dev, **kw)
    except Exception as ex:
        print(f"{name:56s} COMPILE FAIL {str(ex)[:300]}"); es._SRC = SRC0; return
    es._SRC = SRC0
    k = e.kernel
    t = timeit(lambda: e.encode(W, out=out))
    print(f"{name:56s} {t*1e3:6.3f} ms  regs={k.num_regs} local={k.local_size_bytes}B", flush=True)
def sub(a, b, count=None):
    def f(s):
        assert a in s, a[:60]
        return s.replace(a, b) if count is None else s.replace(a, b, count)
    return f
def chain(*fs):
    def f(s):
        for g_ in fs: s = g_(s)
        return s
    return f
run("v3 + STAGE (current)")
# no barriers at all
run("(!) no __syncthreads", lambda s: s.replace("__syncthreads();", "/*sync*/;"))
# no shared-memory passes (B', C', B, C) -- register stages + contiguous pass only
PB = "if constexpr (LOGT > 8) { pass_strided<LOGT - 8, 8, true>(x, tw_inv, t); __syncthreads(); }"
PC = "if constexpr (LOGT > 4) { pass_strided<(LOGT < 8 ? LOGT - 4 : 4), 4, true>(x, tw_inv, t); __syncthreads(); }"
PB2 = "if constexpr (LOGT > 4) { pass_strided<(LOGT < 8 ? LOGT - 4 : 4), 4, false>(x, tw_fwd, t); __syncthreads(); }"
PC2 = "if constexpr (LOGT > 8) { pass_strided<LOGT - 8, 8, false>(x, tw_fwd, t); __syncthreads(); }"
run("(!) no strided smem passes (4 of 15 passes)", chain(sub(PB, ""), sub(PC, ""), sub(PB2, ""), sub(PC2, "")))
run("(!) no strided DIT passes (8 of 15)", chain(sub(PB2, ""), sub(PC2, "")))
# no register-stage butterflies (loads/stores kept): stages_dif/dit on r
run("(!) register stages -> identity", lambda s: re.sub(r"stages_dif<4, LOGT, LOGK - 1, true>\(r, t, tw_inv\);", "", s).replace("stages_dit<4, LOGT, LOGT, false>(r, t, tw_fwd);", ""))
# only one coset instead of four
run("(!) 1 coset NTT instead of 4", sub("for (int c = 0; c < 4; ++c) {", "for (int c = 3; c < 4; ++c) {"))
# no INTT: cf <- input
run("(!) no INTT (cf = raw input)", sub("stages_dif<4, LOGT, LOGK - 1, true>(r, t, tw_inv);", ""), )
# twiddles: constant instead of table loads in the register stages (the L1/LDG cost)
run("(!) all twiddles constant (no ldtw)", sub("const unsigned w = ldtw(&tw[m + (idx & (m - 1))]);", "const unsigned w = 0x1234567u + (unsigned)(idx & (m - 1)) * 0u;"))
run("(!) all butterflies -> xor (loads/stores/barriers kept)", chain(sub("if (DIF) { const unsigned a = e[k], c = e[k + step]; e[k] = add_p(a, c); e[k + step] = mont_mul(sub_p(a, c), w); }", "if (DIF) { const unsigned a = e[k], c = e[k + step]; e[k] = a ^ c; e[k + step] = a ^ w; }"), sub("else     { const unsigned a = e[k], c = mont_mul(e[k + step], w); e[k] = add_p(a, c); e[k + step] = sub_p(a, c); }", "else     { const unsigned a = e[k], c = e[k + step]; e[k] = a ^ c; e[k + step] = a ^ w; }")))
run("(!) mont_mul -> xor only (adds kept)", sub("return min(r, r + P);\n}", "return a ^ w;\n}"))
# no input load
run("(!) no input load (r = t)", sub("r[s] = __ldg(&src[(t + THREADS * s) << in_wide]);", "r[s] = (unsigned)(t + s) * 2654435761u %% P;"))
