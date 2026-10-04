"""FP4's int8 closure (`int8-preadd-budget/fp4`, the 1.34× floor "with every scale equal"): does the budget bind on data the
adversary shapes, and how flat can NVFP4's block scales be made?

The budget ℓ1·12 ≤ 127 takes every pre-added code at E2M1's largest (±6, 12 in half-units). A rewrite needs only its own
data to fit. Rows here: Gaussian background (RMS ρ, which is also every-8th ρ), one spike per 16-block at S·ρ (S below the
dead screen), at within-block offset 1 (off the every-8th sample positions), signed by the recursive checkerboard that makes
every Strassen pre-add's spike part 0 or ±12 at any depth (A: s11 = s21 = +, s12 = s22 = −; B: t11 = t21 = +, t12 = t22 = −,
per level, as a product over levels). Reported:
  - admission (`pearl_c4.row_passes`, exact) on sampled rows, and the exact forming's code/scale statistics on a few rows
    (to validate the vectorized forming used for the large matrices);
  - NVFP4 scale flatness: the share of blocks at the modal scale byte, and of depth-L pre-add operands whose blocks all
    share one byte (the rewrite's exactness condition for integer pre-adds);
  - with scales equal (the floor's own assumption): the largest |pre-added code| per Strassen depth L on A and on B, and the
    share of depth-L sub-products whose operands fit s8 (|v| ≤ 127).
"""
import argparse
import json
import struct
import sys

import numpy as np

sys.setrecursionlimit(10000)

E2M1 = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])
UE4M3 = np.array(sorted({(1 + m / 8) * 2.0 ** (e - 7) for e in range(1, 16) for m in range(8) if not (e == 15 and m == 7)}
                        | {m * 2.0 ** -9 for m in range(1, 8)}))


def rne_grid(v, grid):
    """Nearest-even onto a sorted positive grid (index parity breaks ties), saturating at the top; v ≥ 0."""
    i = np.clip(np.searchsorted(grid, v), 1, len(grid) - 1)
    lo, hi = grid[i - 1], grid[i]
    pick = np.where(v - lo < hi - v, i - 1, np.where(v - lo > hi - v, i, np.where((i - 1) % 2 == 0, i - 1, i)))
    return np.where(v >= grid[-1], len(grid) - 1, pick)


def form_vec(x, rng, fmt="nvfp4"):
    """Vectorized Pearl-C4 forming (rows of x): α = 2688/(s + ρ), noise N(0, (ρα/4)²), per-16 block scale, E2M1 cast.
    Returns (codes in half-units, int, -12..12) and scale bytes (index into UE4M3, or the UE8M0 exponent for mxfp4)."""
    s = np.abs(x).max(1, keepdims=True)
    rho = np.sqrt((x[:, ::8] ** 2).mean(1, keepdims=True))
    alpha = 2688.0 / (s + rho)
    d = alpha * x + rng.standard_normal(x.shape) * (rho * alpha / 4)
    rows, k = x.shape
    blk = np.abs(d).reshape(rows, k // 16, 16).max(2)
    if fmt == "nvfp4":
        sb = rne_grid(blk / 6.0, UE4M3)
        scale = UE4M3[sb]
    else:
        sb = np.ceil(np.log2(np.maximum(blk / 6.0, 2.0 ** -126))).astype(int)
        scale = 2.0 ** sb
    v = d.reshape(rows, k // 16, 16) / scale[:, :, None]
    mag = E2M1[rne_grid(np.abs(v), E2M1)]
    codes = (2 * mag * np.sign(v)).astype(int).reshape(rows, k)
    return codes, sb


def checker(n, L, pattern):
    """±1 per index over depth L: the product over levels of pattern[bit] (the top-level quadrant bit first)."""
    idx = np.arange(n)
    out = np.ones(n, int)
    for lvl in range(L):
        bit = (idx // (n >> (lvl + 1))) & 1
        out *= np.where(bit == 0, pattern[0], pattern[1])
    return out


OFFSETS = {1: (1,), 4: (1, 5, 9, 13), 14: tuple(o for o in range(16) if o not in (0, 8))}   # never an every-8th position


def build_rows(rows, k, S, rng, L, row_pat, col_pat, side, spikes=1, rowmax=None):
    """Background N(0, 1); `spikes` spikes of size S per 16-block at OFFSETS, checkerboard-signed; optionally one entry of
    size `rowmax` per row in the row's last block (a screened block, debited, not banned), which sets α."""
    x = rng.standard_normal((rows, k))
    r = checker(rows, L, row_pat)[:, None]
    blocks = np.arange(k // 16)
    c = checker(k // 16, L, col_pat)[None, :]
    for off in OFFSETS[spikes]:
        x[:, blocks * 16 + off] = S * r * c
    if rowmax is not None:
        x[:, k - 15] = rowmax
    return x


def tuned_S(rowmax, target=1.125 * 2 ** 2, top=8.95):
    """The spike size whose clean block amax / 6 lands on UE4M3 value `target` (the widest relative bucket, mantissa 1.125),
    given α = 2688 / (rowmax + ρ) with ρ ≈ 1; scaled by powers of two to stay at or below `top`."""
    alpha = 2688.0 / (rowmax + 1.0)
    S = 6 * target / alpha
    while S > top:
        S /= 2
    while S * 2 <= top:
        S *= 2
    return S


A_FORMS = [((0, 0), (1, 1)), ((1, 0), (1, 1)), ((0, 0),), ((1, 1),), ((0, 0), (0, 1)), ((1, 0), (0, 0)), ((0, 1), (1, 1))]
A_SIGNS = [(1, 1), (1, 1), (1,), (1,), (1, 1), (1, -1), (1, -1)]
B_FORMS = [((0, 0), (1, 1)), ((0, 0),), ((0, 1), (1, 1)), ((1, 0), (0, 0)), ((1, 1),), ((0, 0), (0, 1)), ((1, 0), (1, 1))]
B_SIGNS = [(1, 1), (1,), (1, -1), (1, -1), (1,), (1, 1), (1, 1)]


def operand(X, path, forms, signs):
    """The pre-added operand reached by a path of form indices (one per level)."""
    for fi in path:
        h, w = X.shape[0] // 2, X.shape[1] // 2
        q = {(0, 0): X[:h, :w], (0, 1): X[:h, w:], (1, 0): X[h:, :w], (1, 1): X[h:, w:]}
        X = sum(sg * q[bk] for bk, sg in zip(forms[fi], signs[fi]))
    return X


def strassen_max(M, forms, signs, L, full=4, samples=3000, seed=1):
    """Per depth 1..L: the largest |entry| over the depth's pre-added operands (all of them up to depth `full`, then
    `samples` random paths), and the share of operands with max ≤ 127 (s8)."""
    rng = np.random.default_rng(seed)
    out, cur = [], [M.astype(np.int32)]
    for depth in range(1, L + 1):
        if depth <= full:
            nxt = []
            for X in cur:
                for fi in range(7):
                    nxt.append(operand(X, [fi], forms, signs))
            cur = nxt
            mx = np.array([np.abs(X).max() for X in cur])
            how = "all"
        else:
            mx = np.array([np.abs(operand(cur[rng.integers(len(cur))], list(rng.integers(0, 7, depth - full)), forms,
                                          signs)).max() for _ in range(samples)])
            how = f"{samples} sampled (random paths below depth {full})"
        out.append({"depth": depth, "operands": how, "max": int(mx.max()), "p99": float(np.percentile(mx, 99)),
                    "median": float(np.median(mx)), "fit_s8": float((mx <= 127).mean())})
    return out


def exact_check(k, S, rows, seed, spikes=1, rowmax=None):
    """Admission and the exact forming on a few rows, with pearl_c4 itself (validates `form_vec`)."""
    from verity_pouw.schemes import pearl_c4 as C4
    from verity_pouw.schemes import pearl_kw as P
    rng = np.random.default_rng(seed)
    x = build_rows(rows, k, S, rng, 2, (1, -1), (1, -1), "A", spikes, rowmax)
    words = [[struct.unpack("<I", struct.pack("<f", float(v)))[0] for v in row] for row in x]
    passes = [C4.row_passes(C4.NVFP4, w) for w in words]
    seed_a, seed_b = b"fp4-int8-depth-A" * 2, b"fp4-int8-depth-B" * 2
    e = [C4.line(seed_a, C4.ROLE_EA, i) for i in range(rows)]
    f = C4.basis(seed_b, C4.ROLE_FA, k)
    formed = C4.form(C4.NVFP4, words, e, f)
    codes = np.array([[2 * float(C4.e2m1_value(c)) for c in row] for row in formed.codes])
    scales = np.array(formed.scales)
    modal = [np.bincount(r).argmax() for r in scales]
    return {"rows": rows, "k": k, "S": S, "passes": int(sum(passes)), "code_abs_mean": float(np.abs(codes).mean()),
            "code_abs_max_nonspike": float(np.abs(np.delete(codes, np.arange(1, k, 16), axis=1)).max()),
            "modal_scale_share": float(np.mean([np.mean(r == m) for r, m in zip(scales, modal)])),
            "distinct_scales_per_row": float(np.mean([len(set(r)) for r in scales]))}


def mixed_depth_cost(fa, fb, Lmax):
    """Relative int8 work per MAC of the best mixed-depth Strassen: at each level a sub-product recurses (7/8 of the work)
    only if all its operands' blocks share one scale, else it is done directly; flatness of the 2^l blocks behind a depth-l
    operand is fa^(2^l) (A) and fb^(2^l) (B), independent per block."""
    cost = 1.0
    for l in range(Lmax, 0, -1):
        q = (fa * fb) ** (2 ** (l - 1))          # both operands' new blocks flat, given the parent's are
        cost = q * (7 / 8) * cost + (1 - q) * 1.0
    return cost


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--S", type=float, default=6.0)
    ap.add_argument("--L", type=int, default=7)
    ap.add_argument("--exact-rows", type=int, default=4)
    ap.add_argument("--spikes", type=int, default=1)
    ap.add_argument("--rowmax", type=float, default=None)
    ap.add_argument("--flat-only", action="store_true", help="skip the Strassen enumeration (flatness sweep)")
    ap.add_argument("--keep-S", action="store_true", help="with --rowmax, keep --S instead of tuning it")
    args = ap.parse_args()
    L = args.L
    if args.rowmax is not None and not args.keep_S:
        args.S = tuned_S(args.rowmax)
    rng = np.random.default_rng(20260930)
    out = {"S": args.S, "spikes": args.spikes, "rowmax": args.rowmax,
           "exact": exact_check(1024, args.S, args.exact_rows, 7, args.spikes, args.rowmax)}
    M = 16 * 2 ** L                                   # A: M x K, B: K x N (stored as N rows of K), K = 32 * 2^L
    K = 32 * 2 ** L
    xa = build_rows(M, K, args.S, rng, L, (1, 1), (1, -1), "A", args.spikes, args.rowmax)
    xb = build_rows(M // 2, K, args.S, rng, L, (1, -1), (1, 1), "B", args.spikes, args.rowmax)
    for fmt in ("nvfp4", "mxfp4"):
        ca, sa = form_vec(xa, rng, fmt)
        cb, sb = form_vec(xb, rng, fmt)
        modal_a = np.bincount(sa.ravel() - sa.min()).argmax() + sa.min()
        modal_b = np.bincount(sb.ravel() - sb.min()).argmax() + sb.min()
        flat_a, flat_b = float((sa == modal_a).mean()), float((sb == modal_b).mean())
        out[fmt] = {"A_modal_scale_share": flat_a, "B_modal_scale_share": flat_b,
                    "A_code_abs_mean": float(np.abs(ca).mean()), "B_code_abs_mean": float(np.abs(cb).mean()),
                    "operand_all_modal_share_by_depth": {d: [flat_a ** (2 ** d), flat_b ** (2 ** d)] for d in range(1, L + 1)},
                    "mixed_depth_int8_cost_vs_honest": 2 * mixed_depth_cost(flat_a, flat_b, L)}
    if args.flat_only:
        print(json.dumps(out))
        return
    ca, _ = form_vec(xa, rng, "nvfp4")
    cb, _ = form_vec(xb, rng, "nvfp4")
    # A as an M x K matrix; B as K x N (transpose of the stored N x K rows)
    out["scales_equal_A"] = strassen_max(ca, A_FORMS, A_SIGNS, L)
    out["scales_equal_B"] = strassen_max(cb.T.copy(), B_FORMS, B_SIGNS, L)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
