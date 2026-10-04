"""Independent red-team attack on `no-exact-rewrite/sm120-e4m3` (a component of tt-out/pearl-c-sm120).

Question. On sm_120 the FP8 mma.sync atom uses a 26-bit truncating adder, so (per the coordinator's
first cut) ~98-99% of k32 atoms are "exact" (the output word equals the exact aligned integer sum of the
32 products plus the incoming accumulator). If C-tilde were an *exact integer matrix product* of the
noisy E4M3 codes, then a bilinear (Strassen/Winograd) or integer-MMA rewrite might reproduce the bound
words for fewer MACs at sm_120 prices, reopening X-PC-8 which the H100 had closed.

This script tests the claim carefully, distinguishing three very different notions of "exact":
  (1) atom-exact:   one k32 step loses no bits.
  (2) group-exact:  a G-atom promotion group's FP32 running total equals the exact integer sum of all
                    G*32 products (i.e. the FP32 adds between atoms in the group also lose no bits).
  (3) chain-exact:  the whole length-k dot product word equals the exact integer sum of all k products
                    (i.e. C-tilde is literally an integer matmul entry).
Only (3) would license a Strassen rewrite over the full inner dimension; (1)/(2) are much weaker.

It also measures the bit-width of the aligned integer sums, which decides whether a fast int8 IMMA path
(<=8-bit limbs) is even available to an attacker, and reports a Strassen break-even at sm_120 prices.

CPU only; the atom is bit-exact (matches the captured BLACKWELL_SM120_E4M3_M16N8K32 fit params). The
Pearl-C forming here is a labelled STAND-IN (Gaussian activations, headroom alpha, noise at the floor);
the exactness structure depends on the E4M3 code distribution and the adder width, not on the exact XOF.
"""
import argparse, json, random, struct, sys

sys.path.insert(0, "/workspace/packages/verity/src")
sys.path.insert(0, "/home/ubuntu/redteam")
import rt_result
from verity.ml.tc.models import GroupSum, HOPPER_E4M3_K32
from verity.ml.tc.term import term_value, fp32_term, e4m3_product
from verity.ml.tc.cast import f32_to_e4m3_sat_word

SM120 = GroupSum(name="sm120", arch="sm_120", dtype="e4m3", operand_bits=8, groups=(32,),
                 width=26, zero_exponent=-133, validated="matches BLACKWELL_SM120_E4M3_M16N8K32 fit")
MODELS = {"sm120_w26": SM120, "hopper_w14": HOPPER_E4M3_K32}


def f32w(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


def f32v(w):
    return struct.unpack("<f", struct.pack("<I", w))[0]


def quant_row(x, rng, delta=1.0):
    """Pearl-C-like forming (STAND-IN): headroom alpha, noise at the floor sigma*alpha ~ 1 code unit."""
    s = max(abs(v) for v in x)
    rho = (sum(x[i] ** 2 for i in range(0, len(x), 8)) / max(1, len(x) // 8)) ** 0.5
    alpha = 448.0 / (s + 4 * delta * rho)
    sigma_alpha = delta * rho * alpha  # >= 1 code unit at the noise floor
    out = []
    for v in x:
        noise = rng.gauss(0, max(sigma_alpha, 1.0))
        out.append(f32_to_e4m3_sat_word(f32w(alpha * v + noise)))
    return out


def make_row(kind, k, rng, delta=1.0):
    x = [rng.gauss(0, 1) for _ in range(k)]
    if kind == "spike300":
        for g in range(0, k, 128):
            for off in (3, 67):
                x[g + off] = 300.0 * (1 if rng.random() < 0.5 else -1)
    elif kind == "narrowband":
        # adversarial: compress the dynamic range so aligned integers are small (favours int8 IMMA)
        x = [rng.uniform(0.9, 1.1) * (1 if rng.random() < 0.5 else -1) for _ in range(k)]
    return quant_row(x, rng, delta)


def sig_bits(total):
    """True significant span of an integer: leading set bit down to lowest set bit (ignores trailing 0s)."""
    if total == 0:
        return 0
    t = abs(total)
    return t.bit_length() - ((t & -t).bit_length() - 1)


def aligned_sum(acc_word, a, b):
    """Exact integer sum of the incoming accumulator and the 32 products, and its TRUE significant span."""
    terms = [term_value(fp32_term(acc_word))] + [term_value(e4m3_product(p, q)) for p, q in zip(a, b)]
    nz = [(n, t) for (n, t) in terms if n != 0]
    if not nz:
        return 0, 0, 0
    e = min(t for _, t in nz)
    total = sum(n << (t - e) for n, t in nz)
    return total, e, sig_bits(total)


def e4m3_exp(word):
    """Unbiased exponent of an E4M3 code (None for zero). E4M3: sign|4-bit exp (bias 7)|3-bit mantissa."""
    w = word & 0x7F
    if w == 0:
        return None
    exp = (w >> 3) & 0xF
    return (exp - 7) if exp else -6  # subnormals share the minimum exponent


def op_exp_span(codes):
    """Per 32-slice: max-min unbiased exponent of the nonzero E4M3 codes (int8 needs span <= 3)."""
    spans = []
    for s in range(0, len(codes), 32):
        es = [e for e in (e4m3_exp(c) for c in codes[s:s + 32]) if e is not None]
        if es:
            spans.append(max(es) - min(es))
    return spans


def analyse(model, A, B, G):
    """Per output word (dot product of A row and B row), classify exactness at the 3 levels."""
    k = len(A)
    steps = k // 32
    acc = 0
    atom_exact = 0
    widths = []
    # group tracking
    group_exact = 0
    n_groups = 0
    group_int = 0  # exact integer sum accumulated over the current group (aligned to a common exp)
    # chain tracking (exact integer sum over all products, ignoring FP32 rounding)
    for s in range(steps):
        if G and s % G == 0:
            acc = 0
            group_int = 0
            n_groups += 1
        a, b = A[32 * s:32 * s + 32], B[32 * s:32 * s + 32]
        out = model.step(acc, a, b)
        total, e, width = aligned_sum(acc, a, b)
        widths.append(width)
        on, oe = term_value(fp32_term(out))
        # atom-exact: output equals the exact aligned sum
        if total == 0:
            atom_ok = (on == 0)
        else:
            # compare output integer (scaled to e) to total
            atom_ok = (oe >= e) and ((on << (oe - e)) == total)
        if atom_ok:
            atom_exact += 1
        # group-exact check: at the last atom of a group, is the FP32 total the exact sum of the group's products?
        if G:
            # exact integer sum of just this atom's 32 products (no incoming acc), aligned
            prod_terms = [term_value(e4m3_product(p, q)) for p, q in zip(a, b)]
            nz = [(n, t) for (n, t) in prod_terms if n != 0]
            if nz:
                pe = min(t for _, t in nz)
                psum = sum(n << (t - pe) for n, t in nz)
            else:
                pe, psum = 0, 0
            # accumulate exact group integer in a common fine scale (track min exponent seen)
            if s % G == 0:
                group_min_e = pe if nz else 0
                group_int = psum
                group_scale = pe if nz else 0
            else:
                if nz and pe < group_scale:
                    group_int = (group_int << (group_scale - pe)) + psum
                    group_scale = pe
                elif nz:
                    group_int += psum << (pe - group_scale)
            if s % G == G - 1 or s == steps - 1:
                # compare FP32 running total 'out' to the exact group integer
                gon, goe = term_value(fp32_term(out))
                if group_int == 0:
                    if gon == 0:
                        group_exact += 1
                else:
                    if goe >= group_scale and (gon << (goe - group_scale)) == group_int:
                        group_exact += 1
        acc = out
    # The whole-chain word (FP32 sum of per-group totals under promotion) is reconstructed in honest_word().
    return atom_exact, steps, widths, group_exact, max(1, n_groups)


def honest_word(model, A, B, G):
    """The bit-exact C-tilde word under the honest atom-then-FP32 schedule (promotion every G atoms)."""
    k = len(A)
    steps = k // 32
    if not G:
        acc = 0
        for s in range(steps):
            acc = model.step(acc, A[32 * s:32 * s + 32], B[32 * s:32 * s + 32])
        return acc
    total = 0.0  # FP32 running total of promotion-group results
    acc = 0
    for s in range(steps):
        if s % G == 0:
            acc = 0
        acc = model.step(acc, A[32 * s:32 * s + 32], B[32 * s:32 * s + 32])
        if s % G == G - 1 or s == steps - 1:
            total = f32v(f32w(total + f32v(acc)))  # FP32 add of the group result into the running total
    return f32w(total)


def chain_exact_int(A, B):
    """Exact integer sum over all k products, and whether it fits FP32's 24-bit significand exactly."""
    prod_terms = [term_value(e4m3_product(p, q)) for p, q in zip(A, B)]
    nz = [(n, t) for (n, t) in prod_terms if n != 0]
    if not nz:
        return 0, 0, 0
    e = min(t for _, t in nz)
    total = sum(n << (t - e) for n, t in nz)
    return total, e, abs(total).bit_length()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--rows", type=int, default=48)
    ap.add_argument("--delta", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=20260930)
    ap.add_argument("--json", type=str, default="")
    args = ap.parse_args()

    results = {}
    for kind in ("gauss", "spike300", "narrowband"):
        for G in (4, 0):
            for name, model in MODELS.items():
                rng = random.Random(args.seed)
                atom_ex = atom_tot = grp_ex = grp_tot = 0
                widths_all = []
                chain_ex = chain_tot = 0
                chain_bits = []
                spans = []
                for _ in range(args.rows):
                    A = make_row(kind, args.k, rng, args.delta)
                    B = make_row(kind, args.k, rng, args.delta)
                    spans.extend(op_exp_span(A))
                    spans.extend(op_exp_span(B))
                    ae, st, widths, ge, ng = analyse(model, A, B, G)
                    atom_ex += ae
                    atom_tot += st
                    grp_ex += ge
                    grp_tot += ng
                    widths_all.extend(widths)
                    # chain-exact: does the honest word equal the exact integer chain sum?
                    hw = honest_word(model, A, B, G)
                    total, e, bits = chain_exact_int(A, B)
                    chain_bits.append(bits)
                    hon, hoe = term_value(fp32_term(hw))
                    if total == 0:
                        ok = (hon == 0)
                    else:
                        ok = (hoe >= e) and ((hon << (hoe - e)) == total)
                    chain_ex += 1 if ok else 0
                    chain_tot += 1
                key = f"{kind}|G={G or 'none'}|{name}"
                results[key] = {
                    "atom_exact_frac": atom_ex / max(1, atom_tot),
                    "group_exact_frac": grp_ex / max(1, grp_tot),
                    "chain_exact_frac": chain_ex / max(1, chain_tot),
                    "atom_width_max": max(widths_all) if widths_all else 0,
                    "atom_width_p50": sorted(widths_all)[len(widths_all) // 2] if widths_all else 0,
                    "chain_int_bits_max": max(chain_bits) if chain_bits else 0,
                    "op_span_p50": sorted(spans)[len(spans) // 2] if spans else 0,
                    "op_span_min": min(spans) if spans else 0,
                    "op_span_le3_frac": (sum(1 for s in spans if s <= 3) / len(spans)) if spans else 0.0,
                }
                r = results[key]
                print(f"{key:30s} atom {r['atom_exact_frac']:6.2%} grp {r['group_exact_frac']:6.2%} "
                      f"chain {r['chain_exact_frac']:6.2%} | atom_sig(max/p50) {r['atom_width_max']:2d}/{r['atom_width_p50']:2d} "
                      f"| op_span p50 {r['op_span_p50']:2d} min {r['op_span_min']:2d} le3 {r['op_span_le3_frac']:5.1%}")
    meas = []
    for key, r in results.items():
        for m in ("atom_exact_frac", "group_exact_frac", "chain_exact_frac", "op_span_le3_frac"):
            meas.append((f"{key}.{m}", r[m], "fraction"))
    rt_result.write("exact-chain-sm120", meas, {"params": vars(args), "results": results},
                    detail="bit-exact sm_120 atom (w26) vs Hopper (w14); stand-in Pearl-C forming")
    if args.json:
        with open(args.json, "w") as f:
            json.dump({"params": vars(args), "results": results}, f, indent=2)


if __name__ == "__main__":
    main()
