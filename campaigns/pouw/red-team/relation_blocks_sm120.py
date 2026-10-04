"""The relation-breaking argument re-run on rung 3's block rotation (`approved-weights.md` §8j), bit-exact, CPU.

A registrant crafts row3 = row1 + row2 in the code values; the prover derives row 3's words from rows 1 and 2's with FP32
adds (bc-8412d697's `approved-weights/relation-attack.py`, whose chains, quantizers and crafted families this imports).
A rotation keeps the relation exact in the reals; only requantizing generic rotated coordinates breaks it. The block
rotation mixes channels only within each of B blocks, so this checks whether that is still enough:
  none          as registered (the relation transfers: the baseline);
  hadamard      the keyed-sign Hadamard of the earlier rung (RA.rotation);
  haar          a dense keyed Haar rotation over all k channels;
  block8/16     rung 3: the |S| = k/1024 largest channels (by a public calibration vector) unmixed and off the chain; the
                rest grouped into B blocks of consecutive calibrated magnitude, each rotated by its own keyed Haar, and
                every coordinate placed at a keyed position (S off the every-8th positions);
  block8-conc   block8 with the crafted rows supported on ONE block's channels only (the registrant's concentration);
  block8-S      block8 with the crafted rows supported on the unmixed channels S only (they are uncredited, so the
                derived words there earn nothing; reported to show it).
Words are the credited chain over the positions outside S. Reports, per transform: the share of positions where the
requantized relation still holds, and the share of derived words equal to the chain's (FP8 v1 RN, FP8 v2 per atom, NVFP4).
"""
import argparse, importlib.util, json, math, random, time
import numpy as np

RA_PATH = "/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/approved-weights/relation-attack.py"
spec = importlib.util.spec_from_file_location("relation_attack", RA_PATH)
RA = importlib.util.module_from_spec(spec); spec.loader.exec_module(RA)

def haar(n, rng):
    q, r = np.linalg.qr(rng.standard_normal((n, n)))
    return q * np.sign(np.diag(r))

def block_transform(k, B, key, calib):
    """rung 3's block rotation as a function on rows, and the positions S occupies (uncredited)."""
    rng = np.random.default_rng(key)
    nS = max(1, k // 1024)
    order = np.argsort(-calib)
    S = order[:nS]
    rest = np.sort(order[nS:])
    rest = rest[np.argsort(calib[rest])]                    # consecutive calibrated magnitude
    groups = np.array_split(rest, B)
    Qs = [haar(len(g), rng) for g in groups]
    pos = rng.permutation(k)                                # keyed placement
    s_pos = [p for p in pos if p % 8 != 0][:nS]             # S off the every-8th positions
    other = [p for p in pos if p not in set(s_pos)]
    def f(row):
        x = np.asarray(row, np.float64); y = np.zeros(k)
        y[s_pos] = x[S]
        out = np.concatenate([Q @ x[g] for Q, g in zip(Qs, groups)])
        y[other] = out
        return list(y)
    return f, np.array(s_pos), groups, S

def fp8_quant(rows, shared=False):
    al_sh = 448.0 / max(abs(v) for r in rows for v in r)
    out = []
    for r in rows:
        al = al_sh if shared else 448.0 / max(abs(v) for v in r)
        out.append([RA.e4m3_rn(al * v) for v in r])
    return out

def mask(codes, s_pos):
    c = list(codes)
    for p in s_pos: c[p] = 0
    return c

def run(k, nrows, seed):
    t0 = time.time()
    rng = random.Random(seed)
    calib = np.abs(np.random.default_rng(seed + 99).standard_normal(k)) * np.exp(np.random.default_rng(seed + 98).standard_normal(k))
    acts8 = [[RA.e4m3_rn(v) for v in RA.activation_row(k, rng, "gauss", 1.0, 448.0)] for _ in range(nrows)]
    acts4 = [RA.nvfp4_quant(RA.activation_row(k, rng, "gauss", 0.25, 6.0 * 448.0), None) for _ in range(nrows)]
    had = RA.rotation(k, seed + 1)
    Qfull = haar(k, np.random.default_rng(seed + 2))
    b8, s8, g8, S8 = block_transform(k, 8, seed + 3, calib)
    b16, s16, _, _ = block_transform(k, 16, seed + 3, calib)
    base8 = RA.crafted_fp8_wide(k, random.Random(seed + 5))
    (c1, c2, c3), sc = RA.crafted_fp4_wide(k, random.Random(seed + 11))
    base4 = [RA.nvfp4_vals(c, sc) for c in (c1, c2, c3)]
    def restrict(rows, idx):
        keep = np.zeros(k, bool); keep[idx] = True
        return [[v if keep[i] else 0.0 for i, v in enumerate(r)] for r in rows]
    conc_idx, S_idx = g8[len(g8) // 2], S8
    transforms = {
        "none": (lambda r: r, np.array([], int), None),
        "hadamard": (had, np.array([], int), None),
        "haar": (lambda r: list(Qfull @ np.asarray(r, np.float64)), np.array([], int), None),
        "block8": (b8, s8, None),
        "block16": (b16, s16, None),
        "block8-conc": (b8, s8, conc_idx),
        "block8-S": (b8, s8, S_idx),
    }
    cells = []
    for name, (f, s_pos, support) in transforms.items():
        r8 = restrict(base8, support) if support is not None else base8
        r4 = restrict(base4, support) if support is not None else base4
        for shared in (False, True):
            if name == "none" and shared: continue
            b = [[RA.e4m3_rn(v) for v in r] for r in r8] if name == "none" else fp8_quant([f(r) for r in r8], shared)
            b = [mask(c, s_pos) for c in b]
            vals = [[RA.e4m3_val(c) for c in r] for r in b]
            live = [i for i in range(k) if any(v[i] != 0 for v in vals)]
            holds = sum(1 for i in live if vals[0][i] + vals[1][i] == vals[2][i]) / max(1, len(live))
            m1 = m2 = 0
            for a in acts8:
                _, p1 = RA.fp8_v1(a, b[0]); _, p2 = RA.fp8_v1(a, b[1]); t3, _ = RA.fp8_v1(a, b[2])
                m1 += RA.derive_v1(p1, p2, "rn") == t3
                _, q1 = RA.fp8_v2(a, b[0]); _, q2 = RA.fp8_v2(a, b[1]); u3, _ = RA.fp8_v2(a, b[2])
                m2 += RA.derive_v2(q1, q2) == u3
            cells.append({"format": "fp8", "transform": name, "shared_scale": shared, "relation_holds_live": round(holds, 4),
                          "v1_derived_correct": round(m1 / nrows, 4), "v2_derived_correct": round(m2 / nrows, 4)})
            print(json.dumps(cells[-1]), f"{time.time()-t0:.0f}s", flush=True)
        rows4 = [(c, sc) for c in (c1, c2, c3)] if name == "none" else [RA.nvfp4_quant(f(r), None) for r in r4]
        rows4 = [(mask(c, s_pos), s) for c, s in rows4]
        ok = 0
        for ac, asc in acts4:
            t = [RA.BLACKWELL_SM120_NVF4.chain(0, ac, c, asc, s) for c, s in rows4]
            ok += RA.add_rn(t[0], t[1]) == t[2]
        cells.append({"format": "nvfp4", "transform": name, "derived_correct": round(ok / nrows, 4)})
        print(json.dumps(cells[-1]), f"{time.time()-t0:.0f}s", flush=True)
    return cells

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=2048); ap.add_argument("--rows", type=int, default=24)
    ap.add_argument("--seed", type=int, default=20260930); ap.add_argument("--output", default="")
    a = ap.parse_args()
    cells = run(a.k, a.rows, a.seed)
    if a.output:
        json.dump({"k": a.k, "rows": a.rows, "cells": cells}, open(a.output, "w"), indent=1)
