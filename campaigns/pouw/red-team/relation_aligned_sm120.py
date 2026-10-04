"""The relation-breaking check re-run under bc-6289d8b0's 16-aligned placement and keyed zero-fill dither
(`docs/pouw/keyed-transforms.md` §5), bit-exact, CPU. Same crafted relation (row3 = row1 + row2 in code values), same
chains and quantizers as `relation_blocks_sm120.py` (which this imports), with rung 3's block rotation placed on whole
16-position chunks (S on the first chunk off every 8th, each block on whole chunks), optionally followed by a keyed
Gaussian at 2^-16 of each row's max before rounding. Transforms: block8 (rung 3 as adopted, the control), aligned8,
aligned8+dither, and the registrant's concentration (rows on one block's channels only) under each.
"""
import argparse, importlib.util, json, random, time
import numpy as np

spec = importlib.util.spec_from_file_location("rb", "/tmp/kt/relation_blocks_sm120.py")
RB = importlib.util.module_from_spec(spec); spec.loader.exec_module(RB)
RA = RB.RA


def aligned_transform(k, B, key, calib, dither=False):
    rng = np.random.default_rng(key)
    nS = max(1, k // 1024)
    order = np.argsort(-calib)
    S = order[:nS]
    rest = np.sort(order[nS:])
    rest = rest[np.argsort(calib[rest])]
    nch = k // 16
    chunks = rng.permutation(nch)
    pos = np.concatenate([np.arange(c * 16, c * 16 + 16) for c in chunks])
    s_pos = [int(p) for p in pos[:16] if p % 8][:nS]
    sset = set(s_pos)
    other = [int(p) for p in pos if int(p) not in sset]
    kb = [nch // B + (1 if b < nch % B else 0) for b in range(B)]
    sizes = [16 * kb[0] - nS] + [16 * x for x in kb[1:]]
    groups, lo = [], 0
    for b in range(B):
        groups.append(rest[lo:lo + sizes[b]]); lo += sizes[b]
    Qs = [RB.haar(len(g), rng) for g in groups]
    drng = np.random.default_rng(key + 7777)

    def f(row):
        x = np.asarray(row, np.float64); y = np.zeros(k)
        y[s_pos] = x[S]
        y[other] = np.concatenate([Q @ x[g] for Q, g in zip(Qs, groups)])
        if dither:
            y = y + drng.standard_normal(k) * (2.0 ** -16) * np.max(np.abs(y))
        return list(y)
    return f, np.array(s_pos), groups, S


def run(k, nrows, seed):
    t0 = time.time()
    rng = random.Random(seed)
    calib = np.abs(np.random.default_rng(seed + 99).standard_normal(k)) * np.exp(np.random.default_rng(seed + 98).standard_normal(k))
    acts8 = [[RA.e4m3_rn(v) for v in RA.activation_row(k, rng, "gauss", 1.0, 448.0)] for _ in range(nrows)]
    acts4 = [RA.nvfp4_quant(RA.activation_row(k, rng, "gauss", 0.25, 6.0 * 448.0), None) for _ in range(nrows)]
    b8, s8, g8, S8 = RB.block_transform(k, 8, seed + 3, calib)
    a8, sa, ga, _ = aligned_transform(k, 8, seed + 3, calib)
    ad8, sad, gad, _ = aligned_transform(k, 8, seed + 3, calib, dither=True)
    base8 = RA.crafted_fp8_wide(k, random.Random(seed + 5))
    (c1, c2, c3), sc = RA.crafted_fp4_wide(k, random.Random(seed + 11))
    base4 = [RA.nvfp4_vals(c, sc) for c in (c1, c2, c3)]

    def restrict(rows, idx):
        keep = np.zeros(k, bool); keep[idx] = True
        return [[v if keep[i] else 0.0 for i, v in enumerate(r)] for r in rows]
    transforms = {
        "none": (lambda r: r, np.array([], int), None),
        "block8": (b8, s8, None),
        "aligned8": (a8, sa, None),
        "aligned8+dither": (ad8, sad, None),
        "block8-conc": (b8, s8, g8[len(g8) // 2]),
        "aligned8-conc": (a8, sa, ga[len(ga) // 2]),
        "aligned8+dither-conc": (ad8, sad, gad[len(gad) // 2]),
    }
    cells = []
    for name, (f, s_pos, support) in transforms.items():
        r8 = restrict(base8, support) if support is not None else base8
        r4 = restrict(base4, support) if support is not None else base4
        b = [[RA.e4m3_rn(v) for v in r] for r in r8] if name == "none" else RB.fp8_quant([f(r) for r in r8], False)
        b = [RB.mask(c, s_pos) for c in b]
        vals = [[RA.e4m3_val(c) for c in r] for r in b]
        live = [i for i in range(k) if any(v[i] != 0 for v in vals)]
        holds = sum(1 for i in live if vals[0][i] + vals[1][i] == vals[2][i]) / max(1, len(live))
        m1 = m2 = 0
        for a in acts8:
            _, p1 = RA.fp8_v1(a, b[0]); _, p2 = RA.fp8_v1(a, b[1]); t3, _ = RA.fp8_v1(a, b[2])
            m1 += RA.derive_v1(p1, p2, "rn") == t3
            _, q1 = RA.fp8_v2(a, b[0]); _, q2 = RA.fp8_v2(a, b[1]); u3, _ = RA.fp8_v2(a, b[2])
            m2 += RA.derive_v2(q1, q2) == u3
        cells.append({"format": "fp8", "transform": name, "relation_holds_live": round(holds, 4),
                      "v1_derived_correct": round(m1 / nrows, 4), "v2_derived_correct": round(m2 / nrows, 4)})
        print(json.dumps(cells[-1]), f"{time.time()-t0:.0f}s", flush=True)
        rows4 = [(c, sc) for c in (c1, c2, c3)] if name == "none" else [RA.nvfp4_quant(f(r), None) for r in r4]
        rows4 = [(RB.mask(c, s_pos), s) for c, s in rows4]
        ok = 0
        for ac, asc in acts4:
            t = [RA.BLACKWELL_SM120_NVF4.chain(0, ac, c, asc, s) for c, s in rows4]
            ok += RA.add_rn(t[0], t[1]) == t[2]
        zero = sum(1 for c, _ in rows4 for x in c if (x & 7) == 0) / (3 * k)
        cells.append({"format": "nvfp4", "transform": name, "derived_correct": round(ok / nrows, 4), "zero_codes": round(zero, 4)})
        print(json.dumps(cells[-1]), f"{time.time()-t0:.0f}s", flush=True)
    return cells


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=2048); ap.add_argument("--rows", type=int, default=24)
    ap.add_argument("--seed", type=int, default=20260930); ap.add_argument("--output", default="")
    a = ap.parse_args()
    cells = run(a.k, a.rows, a.seed)
    if a.output:
        json.dump({"k": a.k, "rows": a.rows, "seed": a.seed, "cells": cells}, open(a.output, "w"), indent=1)
