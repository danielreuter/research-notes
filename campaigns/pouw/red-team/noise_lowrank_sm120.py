"""Red-team for `pearl-quantized-subspace-hardness` (Pearl's Assumption 1): is the product of quantized rank-32 noise any
cheaper to produce, bit for bit, than a generic FP8 product?

The noise is N = E·Fᵀ with E (rows × 32) and F (k × 32), so N has rank 32 before it is quantized. Without quantization the
product N_A·N_Bᵀ = E_A·(F_Aᵀ F_B)·E_Bᵀ costs rows·32·cols plus one 32 × 32 Gram per job, against rows·k·cols for the honest
FP8 product. Quantization is the only thing standing between the two. For each setting this script measures, on the
bit-exact sm_120 atom:

  (1) the low-rank route: the exact rank-32 predictor P = E_A G E_Bᵀ against the honest ticket word C̃ (bit-exact matches,
      relative error, error in ulps of C̃);
  (2) whether quantization keeps the low rank: the Frobenius share of the code matrix A′ outside its best rank-32 part,
      against the unquantized N (which is exactly rank 32);
  (3) reuse and caching: code, 32-slice (atom) and whole-row repeats of A′ across two salts (fresh E, F) and across rows;
      the distinct codes per row (the quantization classes a lookup table would key on);
  (4) E2M1 (FP4): the same rank test under an NVFP4-style cast (E2M1 values with a UE4M3 scale per 16), labelled a model.

Settings: `noise` is Pearl's Assumption 1 (zero input, the noise alone at a fixed scale); `s5` is Pearl-C's in-domain forming
(census `form_s5`, signal plus rank-32 noise), where the signal is full rank and the noise can't be split off before the cast.
"""
import argparse, importlib.util, json, os, sys
from pathlib import Path

import numpy as np

TREE = Path(os.environ.get("CENSUS_TREE") or f"/workspace/research/src/{os.environ.get('RESEARCH_SOURCE_SHA', '')}")
_spec = importlib.util.spec_from_file_location("pearlc_census", TREE / "benchmarks/pouw/pearlc_census.py")
C = importlib.util.module_from_spec(_spec)
sys.modules["pearlc_census"] = C
_spec.loader.exec_module(C)
C.set_atom("sm120-e4m3-k32")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rt_result  # noqa: E402

R = 32
E2M1 = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])


def ticket(a, b, G=4):
    """The honest promoted ticket word of every (i, j) pair, a (rows, k) and b (cols, k) codes."""
    A, B = np.repeat(a, b.shape[0], 0), np.tile(b, (a.shape[0], 1))
    return C.ticket(A, B, G).reshape(a.shape[0], b.shape[0])


def rank_residual(M, r=R):
    s = np.linalg.svd(M.astype(np.float64), compute_uv=False)
    return float(np.sqrt((s[r:] ** 2).sum() / (s ** 2).sum())) if s.size > r else 0.0


def e2m1_nvfp4(x, block=16):
    """An NVFP4-style cast (a model): per 16-element block a UE4M3 scale = amax/6, then RNE onto the E2M1 grid."""
    r, k = x.shape
    xb = x.reshape(r, k // block, block)
    amax = np.abs(xb).max(-1, keepdims=True)
    scale = C.val(C.enc(np.where(amax > 0, amax / 6.0, 1.0)))
    scale = np.where(scale > 0, scale, 1.0)
    y = np.abs(xb) / scale
    idx = np.abs(y[..., None] - E2M1).argmin(-1)
    return (np.sign(xb) * E2M1[idx] * scale).reshape(r, k)


def noise_codes(rows, k, rng, scale=64.0):
    E = rng.standard_normal((rows, R))
    F = rng.standard_normal((k, R))
    N = (E @ F.T) * (scale / np.sqrt(R))
    return E * (scale / np.sqrt(R)), F, N, C.enc(N)


def ulp32(x):
    x = np.abs(x.astype(np.float32))
    return np.spacing(np.where(x > 0, x, np.float32(1e-30)))


def sig_bits_of_residual(D, codes):
    """R = e4m3(D) − D for FP32 D: exact as an integer multiple of ulp(D); returns R's significant-bit spans (0 if exact)."""
    D32 = D.astype(np.float32)
    n = np.rint((C.val(codes) - D32.astype(np.float64)) / ulp32(D32).astype(np.float64)).astype(np.int64)
    a = np.abs(n)
    low = np.where(a > 0, np.log2((a & -a).astype(np.float64)).astype(np.int64), 0)
    top = np.where(a > 0, np.floor(np.log2(np.maximum(a, 1).astype(np.float64))).astype(np.int64), -1)
    return np.where(a > 0, top - low + 1, 0)


def form_s5_D(X, Fc, rng, delta=1.0, line_norm=16.0):
    """`pearlc_census.form_s5`'s forming with the pre-cast FP32 atom output D kept: A′ = e4m3(D)."""
    rows, k = X.shape
    s, rho = np.abs(X).max(1), np.sqrt((X[:, ::8] ** 2).mean(1))
    sig = delta * rho
    alpha = np.where(s + 4 * sig > 0, C.Q_MAX / np.maximum(s + 4 * sig, 1e-300), 0.0)
    Cacc = (alpha[:, None] * X).astype(np.float32).astype(np.float64)
    Ec = C.enc(C.unit_lines(rows, rng) * (sig * alpha / line_norm)[:, None])
    D = np.empty(rows * k)
    for lo in range(0, rows * k, 1 << 17):
        r_, l_ = np.divmod(np.arange(lo, min(lo + (1 << 17), rows * k)), k)
        D[lo:lo + r_.size], _ = C.step(Cacc[r_, l_], Ec[r_], Fc[l_])
    D = D.reshape(rows, k)
    return D, C.enc(D)


def setting_noise(k, rows, cols, seed):
    rng = np.random.default_rng(seed)
    EA, FA, NA, a = noise_codes(rows, k, rng)
    EB, FB, NB, b = noise_codes(cols, k, rng)
    _, _, NA128, a128 = noise_codes(128, k, np.random.default_rng(seed + 7))
    Ct = ticket(a, b)
    P = (EA @ (FA.T @ FB) @ EB.T)                            # the rank-32 predictor, exact reals
    Pw = P.astype(np.float32)
    exact = float((Pw == Ct.astype(np.float32)).mean())
    rel = np.abs(Ct - P) / np.maximum(np.abs(Ct), 1e-30)
    ulps = np.abs(Ct - P) / ulp32(Ct)
    a2 = C.enc(noise_codes(rows, k, np.random.default_rng(seed + 1))[2])   # a second salt: fresh E, F
    same = (a == a2)
    atom_same = same.reshape(rows, k // 32, 32).all(-1)
    rows_eq = sum(int((a[i] == a[j]).all()) for i in range(rows) for j in range(i + 1, rows))
    q4 = e2m1_nvfp4(NA128)
    return {"setting": "noise", "k": k, "tile": f"{rows}x{cols}",
            "lowrank_exact_match": exact, "lowrank_rel_err_median": float(np.median(rel)),
            "lowrank_err_ulps_median": float(np.median(ulps)), "lowrank_err_ulps_min": float(ulps.min()),
            "noise_rank32_residual": rank_residual(NA128), "aprime_rank32_residual": rank_residual(C.val(a128)),
            "aprime_e2m1_rank32_residual": rank_residual(q4),
            "cast_exact_share": float((C.val(a128) == NA128).mean()), "e2m1_cast_exact_share": float((q4 == NA128).mean()),
            "salt_code_repeat": float(same.mean()), "salt_atom_repeat": float(atom_same.mean()),
            "row_pairs_identical": rows_eq, "row_code_repeat": float(np.mean([(a[i] == a[i + 1]).mean() for i in range(rows - 1)])),
            "distinct_codes_per_row_mean": float(np.mean([np.unique(a[i]).size for i in range(rows)]))}


def residual_fp4_limbs(D, codes, block=16):
    """A lower bound on the E2M1 limbs per (row, 16-block) that hold R = e4m3(D) − D exactly under one block scale each:
    a limb holds at most two adjacent set bits per value inside its scale's window of four bit positions, so a block needs
    at least ceil(max popcount / 2) limbs and at least the fewest 4-wide windows covering every occupied bit position."""
    D32 = D.astype(np.float32)
    ulp = ulp32(D32).astype(np.float64)
    n = np.rint((C.val(codes) - D32.astype(np.float64)) / ulp).astype(np.int64)
    e = np.log2(ulp).astype(np.int64)
    rows, k = D.shape
    out = np.empty((rows, k // block), np.int64)
    for r in range(rows):
        for q in range(k // block):
            occ, pop = set(), 0
            for v, ee in zip(n[r, q * block:(q + 1) * block], e[r, q * block:(q + 1) * block]):
                v = abs(int(v))
                pop = max(pop, bin(v).count("1"))
                while v:
                    lo = (v & -v).bit_length() - 1
                    occ.add(int(ee) + lo)
                    v &= v - 1
            win, nxt = 0, None
            for p in sorted(occ):
                if nxt is None or p > nxt:
                    win, nxt = win + 1, p + 3
            out[r, q] = max(1, win, -(-pop // 2))
    return out


def setting_s5(fam, k, rows, cols):
    """Pearl-C in domain: A′ = e4m3(D), D = α·x + E′·Fᵀ through the atom. The split attack writes A′ = D + R, with D of rank
    rank(X) + 32 (cheap product through its factors) and R = e4m3(D) − D; it pays only if R's product is cheap, i.e. if R
    is sparse or needs few significant bits."""
    XA, XB, _, _ = C.family_rows(fam, k, 1.0, rows, cols, 1)
    FcA, FcB = C.s5_lines(k, 1, 16.0)
    DA, a = form_s5_D(XA, FcA, C._rng(1, fam, k, 1.0, "unit-A"))
    DB, b = form_s5_D(XB, FcB, C._rng(1, fam, k, 1.0, "unit-B"))
    bits = sig_bits_of_residual(DA, a)
    nz = bits[bits > 0]
    Ct = ticket(a[:16], b[:16])
    P = DA[:16] @ DB[:16].T                                  # the pre-cast product (what the factors give exactly)
    Xw = (XA / np.abs(XA).max()).astype(np.float64)
    limbs = residual_fp4_limbs(DA[:8], a[:8])
    return {"setting": "s5", "family": fam, "k": k, "rows": rows,
            "residual_fp4_limbs_mean": float(limbs.mean()), "residual_fp4_one_limb_share": float((limbs == 1).mean()),
            "split_nvfp4_residual_cost_lb": float(limbs.mean() ** 2 * 0.5),
            "aprime_rank32_residual": rank_residual(C.val(a)), "signal_rank32_residual": rank_residual(Xw),
            "precast_rank32_residual": rank_residual(DA),
            "cast_exact_share": float((bits == 0).mean()),
            "residual_sig_bits_median": float(np.median(nz)) if nz.size else 0.0,
            "residual_sig_bits_p10": float(np.percentile(nz, 10)) if nz.size else 0.0,
            "residual_fits_bf16": float((bits <= 8).mean()), "residual_fits_fp16": float((bits <= 11).mean()),
            "precast_predictor_exact_match": float((P.astype(np.float32) == Ct.astype(np.float32)).mean()),
            "precast_predictor_rel_err_median": float(np.median(np.abs(Ct - P) / np.maximum(np.abs(Ct), 1e-30)))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ks", default="1024,4096,8192")
    ap.add_argument("--tile", default="32x32")
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--families", default="gaussian,rank1,constant,in-span-FA")
    args = ap.parse_args()
    rows, cols = map(int, args.tile.split("x"))
    cells = []
    for k in map(int, args.ks.split(",")):
        for s in range(args.seeds):
            r = setting_noise(k, rows, cols, 1000 + s)
            cells.append(r)
            print(json.dumps(r), flush=True)
        for fam in args.families.split(","):
            r = setting_s5(fam, k, 128, 16)
            cells.append(r)
            print(json.dumps(r), flush=True)
    noise = [c for c in cells if c["setting"] == "noise"]
    meas = [("lowrank_exact_match_max", max(c["lowrank_exact_match"] for c in noise), "fraction"),
            ("lowrank_err_ulps_median_min", min(c["lowrank_err_ulps_median"] for c in noise), "ulps"),
            ("aprime_rank32_residual_min", min(c["aprime_rank32_residual"] for c in noise), "fraction"),
            ("salt_atom_repeat_max", max(c["salt_atom_repeat"] for c in noise), "fraction")]
    rt_result.write("noise-lowrank-sm120", meas, {"cells": cells},
                    detail="Pearl's Assumption 1: rank-32 predictor vs the honest ticket, rank kept after E4M3/E2M1, reuse")


if __name__ == "__main__":
    main()
