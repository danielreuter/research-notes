"""The base-split break end to end, part 1 (CPU, the exact reference `pearl_c4`, NVFP4): build A's rows, admit and debit
them, form A′ and B̃, split A′ = A0 + ΔA, and write the operands the device replay reads (`basesplit_e2e_sm120.cu`).

Families (A's rows; B's rows are the census's gaussian):
  gauss: N(0, 1) everywhere, 14 spikes per 16-block (every offset but 0 and 8) at S·ρ, signed r_i·c_b.
  flat:  the same spikes, with every-8th positions pinned to ±1 (ρ = 1 exactly) and one row-max entry in the row's last
         block (screened and debited), which sets α so that the spike blocks' scale lands in one UE4M3 bucket.
The attacker's split:
  A0[i, t] = the predicted spike code, ±6 with sign r_i·c_b, on spike positions of every block but the screened last one;
  ΔA = A′ − A0, as E2M1 codes in A′'s own block scales. A spike that deviated by a non-E2M1 amount is a hole: A0 = 0 there
  and ΔA carries the code. ΔA must meet the hardware's sparse rule (at most two of each 8-chunk's four aligned pairs
  nonzero); pairs beyond two move to a patch the CUDA cores compute.
  A0·B̃ᵀ is computed the fast way: per row, (6·s*_i·r_i) ⊗ u_j with u_j = Σ_b c_b·Y[b, j], Y[b, j] = s_B,b(j)·(B̃ row j's
  spike sum in block b), plus a correction per defect block (s_A,b(i) ≠ s*_i) and per hole. The check
  (`basesplit_e2e_check.py`) verifies honest word = sparse word + fast A0 part + patch, bit for bit.
Outputs in --out/<family>/: dims.txt, A.codes, A.scales, DA.codes, B.codes, B.scales (uint8), C.f32 (the fast A0 part as
float32, for the timed beta = 1 arm), split.npz (the pieces the check needs), reference.json (admission, debit, counts).
"""
import argparse
import json
import os
import struct
import time
from fractions import Fraction

import numpy as np
from verity_pouw.schemes import pearl_c4 as C4

F = C4.NVFP4
SPIKE_OFFS = tuple(o for o in range(16) if o not in (0, 8))
E2M1_MAG = {Fraction(0): 0, Fraction(1, 2): 1, Fraction(1): 2, Fraction(3, 2): 3, Fraction(2): 4, Fraction(3): 5,
            Fraction(4): 6, Fraction(6): 7}
HALF = np.array([0, 1, 2, 3, 4, 6, 8, 12, 0, -1, -2, -3, -4, -6, -8, -12], dtype=np.int64)   # 2·value per code


def f32(v):
    return struct.unpack("<I", struct.pack("<f", float(v)))[0]


def build(family, rows, k, S, rowmax, rng, rsign, csign):
    x = rng.standard_normal((rows, k))
    if family == "flat":
        x[:, ::8] = rng.choice((-1.0, 1.0), (rows, k // 8))
    for o in SPIKE_OFFS:
        x[:, o::16] = S * rsign[:, None] * csign[None, :]
    if family == "flat":
        x[:, k - 15] = rowmax
    return x


def enc(v):
    """E2M1 code of the value v, or None."""
    m = E2M1_MAG.get(abs(v))
    return None if m is None else (m | (8 if v < 0 else 0)) if m else 0


def scale_int(bytes_):
    """Per scale byte: (m, e) with value m·2^e, from the reference's own decoder."""
    m = np.zeros(256, dtype=np.int64)
    e = np.zeros(256, dtype=np.int64)
    for byte in range(0x7F):
        mm, ee = C4.scale_dyadic(F, byte)
        m[byte], e[byte] = mm, ee
    return m[bytes_], e[bytes_]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", choices=("gauss", "flat"), required=True)
    ap.add_argument("--rows", type=int, default=256)
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--S", type=float, default=8.9)
    ap.add_argument("--rowmax", type=float, default=936.0)
    ap.add_argument("--debit-tiles", type=int, default=2)
    ap.add_argument("--debit-size", type=int, default=8)
    ap.add_argument("--chain-words", type=int, default=16)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    R, k, nb = a.rows, a.k, a.k // 16
    out = os.path.join(a.out, a.family)
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(20260930)
    rA = rng.choice((-1.0, 1.0), R)
    cA = rng.choice((-1.0, 1.0), nb)
    XA = build(a.family, R, k, a.S, a.rowmax, rng, rA, cA)
    XB = rng.standard_normal((R, k))
    WA = [[f32(v) for v in row] for row in XA]
    WB = [[f32(v) for v in row] for row in XB]
    ref = {"family": a.family, "rows": R, "k": k, "S": a.S, "rowmax": a.rowmax if a.family == "flat" else None,
           "tree": "bfd950d81d3b78fdcd680adb1dd881910e8340f4"}
    ref["admitted_A"] = sum(C4.row_passes(F, w) for w in WA)
    ref["admitted_B"] = sum(C4.row_passes(F, w) for w in WB)
    seed_b = b"basesplit-e2e-B!" * 2
    seed_a = b"basesplit-e2e-A!" * 2
    fA, fB = C4.basis(seed_b, C4.ROLE_FA, k), C4.basis(seed_b, C4.ROLE_FB, k)
    eA = [C4.line(seed_a, C4.ROLE_EA, i) for i in range(R)]
    eB = [C4.line(seed_b, C4.ROLE_EB, j) for j in range(R)]
    a1, b1 = C4.form(F, WA, eA, fA), C4.form(F, WB, eB, fB)
    ref["t_form_s"] = round(time.time() - t0, 1)
    codes = np.array(a1.codes, dtype=np.int64)
    bcodes = np.array(b1.codes, dtype=np.int64)
    sA = np.array(a1.scales, dtype=np.int64)
    sB = np.array(b1.scales, dtype=np.int64)
    ref["D24_windows_A"] = int(sum(sum(C4.two_four_windows(r)) for r in a1.codes))
    ref["spread_ok_A"] = bool(all(C4.spread_ok(F, s) for s in a1.scales))
    ref["scale_bytes_ok"] = bool(all(C4.scale_bytes_ok(F, s) for s in a1.scales + b1.scales))
    blocks_used = nb - 1 if a.family == "flat" else nb
    modal = np.array([np.bincount(r[:blocks_used]).argmax() for r in sA])
    ref["modal_scale_share_A"] = float(np.mean(sA[:, :blocks_used] == modal[:, None]))

    # the split
    spike = np.zeros(k, dtype=bool)
    for o in SPIKE_OFFS:
        spike[o::16] = True
    if a.family == "flat":
        spike[k - 16:] = False
    sign = (rA[:, None] * np.repeat(cA, 16)[None, :]) > 0
    pred = np.where(spike[None, :], np.where(sign, 7, 15), 0)
    val = HALF[codes]                                      # 2·value
    pval = HALF[pred]
    DA = np.zeros_like(codes)
    holes = np.zeros_like(codes, dtype=bool)
    same = codes == pred
    DA[~spike[None, :].repeat(R, 0)] = codes[~spike[None, :].repeat(R, 0)]
    dev = spike[None, :] & ~same
    for i, t in zip(*np.nonzero(dev)):
        c = enc(Fraction(int(val[i, t] - pval[i, t]), 2))
        if c is None:
            holes[i, t] = True
            DA[i, t] = codes[i, t]
        else:
            DA[i, t] = c
    A0 = np.where(holes, 0, pred)
    assert np.array_equal(HALF[A0] + HALF[DA], val), "A0 + ΔA != A′"
    # hardware sparse rule: at most two nonzero aligned pairs per 8-chunk; excess pairs -> patch
    nzp = (DA.reshape(R, k // 2, 2) & 7).any(2).reshape(R, k // 8, 4)
    patch = np.zeros_like(codes, dtype=bool)
    for i, c in zip(*np.nonzero(nzp.sum(2) > 2)):
        for p in np.nonzero(nzp[i, c])[0][2:]:
            patch[i, 8 * c + 2 * p: 8 * c + 2 * p + 2] = True
    DAs = np.where(patch, 0, DA)
    ref["counts"] = {"spike_at_pred": float(same[:, spike].mean()), "deviated": int(dev.sum()), "holes": int(holes.sum()),
                     "patch_elements": int((patch & ((DA & 7) != 0)).sum()),
                     "chunks_over_two_pairs": int((nzp.sum(2) > 2).sum()), "chunks": int(R * k // 8),
                     "deltaA_density": float(((DAs & 7) != 0).mean())}

    # the fast A0 part, exact, in integer units: value = m·2^e, element = HALF/2 · m·2^e
    mA, eA_ = scale_int(sA)
    mB, eB_ = scale_int(sB)
    EA, EB = int(eA_.min()), int(eB_.min())
    Bint = (HALF[bcodes].reshape(R, nb, 16) * (mB << (eB_ - EB))[:, :, None]).reshape(R, k)     # 2·value·2^-EB
    Y = np.stack([Bint.reshape(R, nb, 16)[:, :, o] for o in SPIKE_OFFS], 0).sum(0)             # (j, b): spike sum
    if a.family == "flat":
        Y[:, nb - 1] = 0
    sAint = mA << (eA_ - EA)                                                                      # (i, b)
    smod = np.array([sAint[i, np.nonzero(sA[i] == modal[i])[0][0]] for i in range(R)])
    six = 12                                                                                      # 2·6
    csgn = cA.astype(np.int64)
    u = (Y * csgn[None, :]).sum(1)                                                                # (j,)
    rank1 = np.outer(six * smod * rA.astype(np.int64), u)                                         # (i, j)
    dsc = (sAint - smod[:, None]) * (sAint != smod[:, None])
    if a.family == "flat":
        dsc[:, nb - 1] = 0
    corr = (six * rA.astype(np.int64))[:, None] * ((dsc * csgn[None, :]) @ Y.T)                   # defect blocks
    hole_corr = np.zeros((R, R), dtype=np.int64)
    for i, t in zip(*np.nonzero(holes)):
        hole_corr[i] -= HALF[pred[i, t]] * sAint[i, t // 16] * Bint[:, t]
    A0fast = rank1 + corr + hole_corr                          # units 2^(EA+EB-2): (2·a)(2·b) m_A m_B 2^(eA+eB)/4
    Aint0 = (HALF[A0].reshape(R, nb, 16) * sAint[:, :, None]).reshape(R, k)
    assert np.array_equal(A0fast, Aint0 @ Bint.T), "fast A0 part != A0·B̃ᵀ"
    Pint = (np.where(patch, HALF[DA], 0).reshape(R, nb, 16) * sAint[:, :, None]).reshape(R, k)
    patch_words = Pint @ Bint.T
    ref["counts"].update({"defect_blocks": int((dsc != 0).sum()), "blocks": int(R * blocks_used),
                          "exp_span_A": int(eA_.max() - EA), "exp_span_B": int(eB_.max() - EB)})
    ref["t_split_s"] = round(time.time() - t0, 1)

    # the reference chain on sample words, and the debit on sample tiles
    words = []
    for w in range(a.chain_words):
        i, j = int(rng.integers(R)), int(rng.integers(R))
        words.append([i, j, C4.chain(F, a1.codes[i], b1.codes[j], a1.scales[i], b1.scales[j])])
    ref["chain_words"] = words
    debits = []
    for _ in range(a.debit_tiles):
        r0 = int(rng.integers(R // a.debit_size)) * a.debit_size
        c0 = int(rng.integers(R // a.debit_size)) * a.debit_size
        rows, cols = list(range(r0, r0 + a.debit_size)), list(range(c0, c0 + a.debit_size))
        d = C4.tile_debit(F, a1, b1, rows, cols, a.debit_size)
        fields = getattr(d, "_fields", None) or list(getattr(d, "__dataclass_fields__", {}))
        units = {f: str(getattr(d, f)) for f in fields if f != "counts"} or {"repr": repr(d)}
        debits.append({"rows": [r0, r0 + a.debit_size], "cols": [c0, c0 + a.debit_size], "units": units,
                       "counts": d.counts, "credit_units": len(rows) * len(cols) * k})
    ref["tile_debits"] = debits
    ref["t_total_s"] = round(time.time() - t0, 1)

    with open(os.path.join(out, "dims.txt"), "w") as fh:
        fh.write(f"{R} {R} {k}\n")
    codes.astype(np.uint8).tofile(os.path.join(out, "A.codes"))
    sA.astype(np.uint8).tofile(os.path.join(out, "A.scales"))
    DAs.astype(np.uint8).tofile(os.path.join(out, "DA.codes"))
    bcodes.astype(np.uint8).tofile(os.path.join(out, "B.codes"))
    sB.astype(np.uint8).tofile(os.path.join(out, "B.scales"))
    shift = EA + EB - 2
    (A0fast.astype(np.float64) * 2.0 ** shift).astype(np.float32).tofile(os.path.join(out, "C.f32"))
    np.savez(os.path.join(out, "split.npz"), A0fast=A0fast, patch_words=patch_words, shift=shift, EA=EA, EB=EB,
             sAint=sAint, sBint=mB << (eB_ - EB),
             chain_words=np.array([[i, j, c] for i, j, c in words], dtype=np.int64))
    with open(os.path.join(out, "reference.json"), "w") as fh:
        json.dump(ref, fh, indent=1, default=str)
    print(json.dumps(ref, indent=1, default=str))


if __name__ == "__main__":
    main()
