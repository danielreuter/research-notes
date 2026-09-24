"""(!) attribution: are the low-m shared-memory passes bank-conflict bound?  Replace their strided index with a lane-consecutive one
(wrong output, same instruction mix)."""
import sys, time
import numpy as np, torch, cupy as cp
from backends.direct.ligero import encode_simt as es
from backends.direct.ligero.field import P
l, R, tp = 16384, 3328, 0
n = 4 * l; dev = torch.device("cuda")
g = torch.Generator().manual_seed(5)
W = torch.randint(0, P, (R, l), generator=g, dtype=torch.int64).to(torch.int32).to(dev)
sms = cp.cuda.runtime.getDeviceProperties(0)["multiProcessorCount"]
base = es.LigeroEncoderSIMT(l, n, tp, dev)
out_ref = torch.empty((R, n), dtype=torch.int32, device=dev); base.encode(W, out=out_ref)
gb = R * n * 4 / 1e9
def timeit(fn, reps=9):
    fn(); torch.cuda.synchronize(); ts = []
    for _ in range(reps):
        torch.cuda.synchronize(); t0 = time.perf_counter(); fn(); torch.cuda.synchronize(); ts.append(time.perf_counter() - t0)
    ts.sort(); return ts[0], ts[len(ts)//2]
def run(name, src, exact=True):
    params = {"pinv": es._P_INV_MOD_R, "k": l, "logk": l.bit_length() - 1, "threads": 1024, "logt": 10, "tp": tp, "kinv_mont": 1}
    smem = 4 * (2 * l + 32)
    k = cp.RawKernel(src % params, "rs_encode_ligero", options=("-std=c++17",)); k.max_dynamic_shared_size_bytes = smem; k.compile()
    out = torch.empty((R, n), dtype=torch.int32, device=dev)
    Win = cp.asarray(W).view(cp.uint32); O = cp.asarray(out).view(cp.uint32)
    go = lambda: k((sms * 4,), (1024,), (Win, O, np.uint64(0), np.uint64(0), base.tw_inv, base.tw_fwd, base.coset, base.mask_tw, np.int32(R)), shared_mem=smem)
    tmin, tmed = timeit(go); same = bool(torch.equal(out, out_ref))
    print(f"{name:52s} min {tmin*1e3:7.3f} med {tmed*1e3:7.3f} ms regs={k.num_regs} spill={k.local_size_bytes}B {'bit-exact' if same else ('differs (expected)' if not exact else 'DIFFERS !!!')}", flush=True)
S0 = es._SRC
run("candidate (ii)", S0)
# DIT passes: i = ((q >> lm) << (lm + 2)) | tt  ->  lane-consecutive for lm < 5: i = q, strides THREADS*... (wrong math)
DIT_OLD = "const int i = ((q >> lm) << (lm + 2)) | tt;\n                    unsigned a0, a1, a2, a3;\n                    if (lm == 0) {"
DIT_NEW = "const int i = (lm < 5) ? (q + 3 * (q & ~(THREADS - 1))) : (((q >> lm) << (lm + 2)) | tt);\n                    unsigned a0, a1, a2, a3;\n                    if (lm == 0) {"
assert DIT_OLD in S0
S1 = S0.replace(DIT_OLD, DIT_NEW)
# in the conflict-free variant the four elements are at i, i+T, i+2T, i+3T (T = THREADS) instead of i, i+m, i+2m, i+3m
S1 = S1.replace("a0 = x[i]; a1 = x[i + m]; a2 = x[i + m2]; a3 = x[i + m2 + m];", "if (lm < 5) { a0 = x[i]; a1 = x[i + THREADS]; a2 = x[i + 2 * THREADS]; a3 = x[i + 3 * THREADS]; } else { a0 = x[i]; a1 = x[i + m]; a2 = x[i + m2]; a3 = x[i + m2 + m]; }")
S1 = S1.replace("a1 = mont_mul(cf[CFPAD(i + 1)], __ldg(&ct[i + 1]));", "a1 = mont_mul(cf[CFPAD(i + THREADS)], __ldg(&ct[i + 1]));").replace("a2 = mont_mul(cf[CFPAD(i + 2)], __ldg(&ct[i + 2]));", "a2 = mont_mul(cf[CFPAD(i + 2 * THREADS)], __ldg(&ct[i + 2]));").replace("a3 = mont_mul(cf[CFPAD(i + 3)], __ldg(&ct[i + 3]));", "a3 = mont_mul(cf[CFPAD(i + 3 * THREADS)], __ldg(&ct[i + 3]));")
S1 = S1.replace("""                    x[i] = add_p(b0, d2);
                    x[i + m2] = sub_p(b0, d2);
                    x[i + m] = add_p(b1, d3);
                    x[i + m2 + m] = sub_p(b1, d3);""", """                    if (lm < 5) { x[i] = add_p(b0, d2); x[i + 2 * THREADS] = sub_p(b0, d2); x[i + THREADS] = add_p(b1, d3); x[i + 3 * THREADS] = sub_p(b1, d3); }
                    else { x[i] = add_p(b0, d2); x[i + m2] = sub_p(b0, d2); x[i + m] = add_p(b1, d3); x[i + m2 + m] = sub_p(b1, d3); }""")
run("(!) DIT low passes lane-consecutive (no conflicts)", S1, exact=False)
# DIF passes too: i = ((q >> (lm - 1)) << (lm + 1)) | tt ; elements i, i+h, i+m, i+m+h
DIF_OLD = "const int i = ((q >> (lm - 1)) << (lm + 1)) | tt;\n                const unsigned a0 = x[i], a1 = x[i + h], a2 = x[i + m], a3 = x[i + m + h];"
assert DIF_OLD in S1
S2 = S1.replace(DIF_OLD, "const int i = (lm < 6) ? (q + 3 * (q & ~(THREADS - 1))) : (((q >> (lm - 1)) << (lm + 1)) | tt);\n                const int H = (lm < 6) ? THREADS : h, M = (lm < 6) ? 2 * THREADS : m;\n                const unsigned a0 = x[i], a1 = x[i + H], a2 = x[i + M], a3 = x[i + M + H];")
S2 = S2.replace("""                o[last ? CFPAD(i) : i] = add_p(b0, b1);
                o[last ? CFPAD(i + h) : i + h] = mont_mul(sub_p(b0, b1), wh);
                o[last ? CFPAD(i + m) : i + m] = add_p(b2, b3);
                o[last ? CFPAD(i + m + h) : i + m + h] = mont_mul(sub_p(b2, b3), wh);""", """                o[last ? CFPAD(i) : i] = add_p(b0, b1);
                o[last ? CFPAD(i + H) : i + H] = mont_mul(sub_p(b0, b1), wh);
                o[last ? CFPAD(i + M) : i + M] = add_p(b2, b3);
                o[last ? CFPAD(i + M + H) : i + M + H] = mont_mul(sub_p(b2, b3), wh);""")
run("(!) DIT + DIF low passes lane-consecutive", S2, exact=False)
