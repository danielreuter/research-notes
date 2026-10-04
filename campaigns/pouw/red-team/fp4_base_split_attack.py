"""TT_OUT-FP4's "salt-live but unchanged" hole, tested on the reference (`pearl_c4`, NVFP4): spike-saturated rows.

A's rows (k = 8,192; B's rows are the census's gaussian by default): N(0, 1) on every position, then 14 spikes per 16-block (every offset but 0 and 8, the every-8th positions
ρ samples) at S·ρ with S just under the dead screen, signed r_i·c_b (row sign times block sign). Every spike is salt-live by
`salt_dead`'s worst-case support (so no debit), but on real draws its code sits at ±6: a block's maximum always casts to ±6,
and the noise (σα = ρα/4) moves a spike by ~1/(4S). So
    A′ = A0 + ΔA,   A0 = the predicted ±6 pattern (E2M1 code 7) (r_i c_b on the spikes, 0 on offsets 0 and 8),
and ΔA is the sampled positions (≤ 1 per 4-group: 2:4-compatible) plus any spike that deviated. Then
    C̃ = A0·B̃ᵀ + ΔA·B̃ᵀ,  with A0·B̃ᵀ = Σ_b s_A,b s_B,b · 6 r_i c_b · (B̃'s block sums over the spikes),
a k/16-deep product, and ΔA·B̃ᵀ a 2:4-sparse (or, gathered, k/8-deep) product.
Checked here, all on the reference's exact functions:
  admission (`row_passes`), D-24 windows (`two_four_windows`), D-SS spread (`spread_ok`), scale bytes (`scale_bytes_ok`);
  codes under two salts (two seed_A): the share of spike codes at ±6 and of codes that change between salts;
  `salt_dead` per element and the 2:4 debit units it implies (`two_four_units`);
  block-scale flatness; ΔA's density and 2:4 compatibility;
  for sample words: the chain (`pearl_c4.chain`) against the exact rational sum, and A0-part + ΔA-part against the chain.
"""
import argparse
import json
import struct
from fractions import Fraction

import numpy as np
from verity_pouw.schemes import pearl_c4 as C4

F = C4.NVFP4


def f32(v):
    return struct.unpack("<I", struct.pack("<f", float(v)))[0]


def build(rows, k, S, rng, rsign, csign):
    x = rng.standard_normal((rows, k))
    offs = [o for o in range(16) if o not in (0, 8)]
    for b in range(k // 16):
        for o in offs:
            x[:, 16 * b + o] = S * np.ravel(rsign) * csign[b]
    return x


def val(code):
    return C4.e2m1_value(code)


def scale_val(byte):
    m, e = C4.scale_dyadic(F, byte)
    return Fraction(m) * Fraction(2) ** e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--rows", type=int, default=4)
    ap.add_argument("--S", type=float, default=8.9)
    ap.add_argument("--words", type=int, default=8)
    ap.add_argument("--b-family", default="gaussian", choices=("gaussian", "spiked"))
    args = ap.parse_args()
    k, R, S = args.k, args.rows, args.S
    rng = np.random.default_rng(20260930)
    rA, rB = rng.choice((-1.0, 1.0), R), rng.choice((-1.0, 1.0), R)
    cA = rng.choice((-1.0, 1.0), k // 16)
    cB = rng.choice((-1.0, 1.0), k // 16)
    XA = build(R, k, S, rng, rA[:, None], cA)
    XB = build(R, k, S, rng, rB[:, None], cB) if args.b_family == "spiked" else rng.standard_normal((R, k))
    WA = [[f32(v) for v in row] for row in XA]
    WB = [[f32(v) for v in row] for row in XB]
    out = {"k": k, "rows": R, "S": S, "b_family": args.b_family}
    out["admission_A"] = [C4.row_passes(F, w) for w in WA]
    out["admission_B"] = [C4.row_passes(F, w) for w in WB]
    seed_b = b"fp4-base-split-B" * 2
    fA, fB = C4.basis(seed_b, C4.ROLE_FA, k), C4.basis(seed_b, C4.ROLE_FB, k)
    forms = {}
    for salt in (b"salt-one", b"salt-two"):
        seed_a = (b"fp4-base-split-A" + salt) * 2
        eA = [C4.line(seed_a, C4.ROLE_EA, i) for i in range(R)]
        eB = [C4.line(seed_b + salt, C4.ROLE_EB, j) for j in range(R)]
        forms[salt] = (C4.form(F, WA, eA, fA), C4.form(F, WB, eB, fB))
    a1, b1 = forms[b"salt-one"]
    a2, _ = forms[b"salt-two"]
    spike = np.array([(t % 16) not in (0, 8) for t in range(k)])
    codes1 = np.array(a1.codes)
    codes2 = np.array(a2.codes)
    mag1 = codes1 & 7
    out["spike_codes_at_6"] = float((mag1[:, spike] == 7).mean())         # E2M1 code 7 is the value 6
    out["spike_code_change_between_salts"] = float((codes1[:, spike] != codes2[:, spike]).mean())
    out["sample_code_change_between_salts"] = float((codes1[:, ~spike] != codes2[:, ~spike]).mean())
    out["D24_windows_A"] = int(sum(sum(C4.two_four_windows(r)) for r in a1.codes))
    out["spread_ok_A"] = all(C4.spread_ok(F, s) for s in a1.scales)
    out["scale_bytes_ok_A"] = all(C4.scale_bytes_ok(F, s) for s in a1.scales)
    dead = [C4.salt_dead(F, WA[i], a1.alpha[i], a1.ae[i]) for i in range(R)]
    out["salt_dead_share_spikes"] = float(np.mean([d for row in dead for t, d in enumerate(row) if spike[t]]))
    out["salt_dead_share_samples"] = float(np.mean([d for row in dead for t, d in enumerate(row) if not spike[t]]))
    out["two_four_debit_units_per_row"] = [C4.two_four_units(d) for d in dead]
    sc = np.array(a1.scales)
    modal = [np.bincount(r).argmax() for r in sc]
    out["modal_scale_share_A"] = float(np.mean([np.mean(r == m) for r, m in zip(sc, modal)]))
    # A0: the predicted pattern (code 6 with the spike's sign on spikes, 0 elsewhere); ΔA = the rest
    pred = np.zeros_like(codes1)
    for i in range(R):
        for t in range(k):
            if spike[t]:
                pred[i, t] = 0x7 if rA[i] * cA[t // 16] > 0 else 0xF
    delta_nz = (codes1 != pred) & ((codes1 & 7) != 0)
    out["deltaA_density"] = float(delta_nz.mean())
    groups = delta_nz.reshape(R, k // 4, 4).sum(2)
    out["deltaA_4groups_over_2"] = float((groups > 2).mean())
    # words: chain vs exact, and A0-part + ΔA-part vs chain
    words = []
    for w in range(min(args.words, R * R)):
        i, j = w // R, w % R
        chain = C4.chain(F, a1.codes[i], b1.codes[j], a1.scales[i], b1.scales[j])
        exact = Fraction(0)
        part0 = Fraction(0)
        for b in range(k // 16):
            sab = scale_val(a1.scales[i][b]) * scale_val(b1.scales[j][b])
            blk = sum(val(a1.codes[i][16 * b + o]) * val(b1.codes[j][16 * b + o]) for o in range(16))
            exact += sab * blk
            p0 = sum(val(int(pred[i, 16 * b + o])) * val(b1.codes[j][16 * b + o]) for o in range(16))
            part0 += sab * p0
        partd = exact - part0
        words.append({"word": [i, j], "chain_equals_exact": Fraction(struct.unpack("<f", struct.pack("<I", chain))[0]) == exact,
                      "A0_part_share": float(part0 / exact) if exact else None})
    out["words"] = words
    deb = C4.tile_debit(F, a1, b1, list(range(R)), list(range(R)), R)
    total = sum(Fraction(v) for v in (deb.two_four, deb.identity, deb.dead_pairs, deb.forming, deb.subgrid, deb.windows)) \
        if hasattr(deb, "two_four") else None
    out["tile_debit_counts"] = deb.counts
    out["tile_debit_units"] = str(total) if total is not None else repr(deb)
    out["tile_chain_credit_units"] = R * R * k
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
