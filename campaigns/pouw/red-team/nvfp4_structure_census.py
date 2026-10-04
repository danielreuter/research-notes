"""`known-weights/sm120-nvfp4` and `structure-free/rot-nvfp4` on rung 3's block rotation: the NVFP4 structural census,
clause by clause (`approved-weights-rows.md`, `structure-free/rot-*`), over independent keys.

Masters (n rows × k, committed before the key):
  real-heavy     Gaussian rows, 30% with three 15–40σ outliers (a trained-weight stand-in);
  crafted        bc-8412d697's crafted E2M1 families (row3 = row1 + row2 and differences, shared block scales), plus a duplicate
                 row, a near-duplicate (15/16 of positions equal) and a doubled row (2·row1), then real-heavy rows;
  concentrated   every row's energy in the channels of ONE rotation block (the registrant's concentration against B blocks).
Transforms: hadamard (rung 2), haar (dense keyed), block8 (rung 3, `relation_blocks_sm120.block_transform`). Each rotated row is
requantized to NVFP4 by RN (UE4M3 block scales, E2M1 codes; `relation-attack.nvfp4_quant`). Per cell, the census:
  (a) the most (code, scale)-equal positions between two rows (d* = k − k/16) and between two (row, 64-block) blocks;
  (b) 64-slices meeting the hardware's sparse rule (≤ 2 of each 8-chunk's 4 aligned pairs nonzero), and all-zero 64-slices;
  (c) exact short relations on whole rows, by value: v_i ± v_j = v_l, v_i = ±v_j, 2·v_i = v_j;
  (d) max/RMS (R* = 16);
plus the per-row modal UE4M3 byte share (F2's statistic) and the key transfer of near-duplicate pairs.
"""
import argparse, importlib.util, json, random, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from relation_blocks_sm120 import RA, haar, block_transform  # noqa: E402

def masters(n, k, rng):
    W = rng.standard_normal((n, k))
    for i in range(n):
        if rng.random() < 0.3:
            W[i, rng.integers(0, k, 3)] = rng.choice([-1, 1], 3) * rng.uniform(15, 40, 3)
    (c1, c2, c3), sc = RA.crafted_fp4_wide(k, random.Random(11))
    v = [np.array(RA.nvfp4_vals(c, sc)) for c in (c1, c2, c3)]
    near = v[0].copy(); idx = rng.choice(k, k // 16, replace=False); near[idx] = -near[idx]
    crafted = np.array([v[0], v[1], v[2], v[0], near, 2 * v[0]] + list(W[6:]))
    return {"real-heavy": W, "crafted": crafted}

def concentrated(n, k, rng, groups):
    g = groups[len(groups) // 2]
    W = np.zeros((n, k)); W[:, g] = rng.standard_normal((n, len(g)))
    return W

def quant(Wr):
    out = [RA.nvfp4_quant(list(map(float, r)), None) for r in Wr]
    codes = np.array([c for c, _ in out], np.int64)
    scales = np.array([s for _, s in out], np.int64)
    return codes, scales

MAG = np.array([0, .5, 1, 1.5, 2, 3, 4, 6, 0, -.5, -1, -1.5, -2, -3, -4, -6])

def census(codes, scales):
    n, k = codes.shape
    sfull = np.repeat(scales, 16, axis=1)
    key = codes * 256 + sfull
    vals = MAG[codes] * np.vectorize(RA.ue4m3_val)(sfull)
    row_eq = blk_eq = 0
    for i in range(n):
        eq = key[i][None, :] == key[i + 1:]
        if eq.size:
            row_eq = max(row_eq, int(eq.sum(1).max()))
            blk_eq = max(blk_eq, int(eq.reshape(eq.shape[0], k // 64, 64).sum(2).max()))
    nzpair = (codes.reshape(n, k // 2, 2) & 7).any(2).reshape(n, k // 8, 4).sum(2) <= 2      # (n, k/8) chunks
    slice24 = float(nzpair.reshape(n, k // 64, 8).all(2).mean())
    zero64 = float(((codes & 7) == 0).reshape(n, k // 64, 64).all(2).mean())
    rows = {vals[i].tobytes(): i for i in range(n)}
    rel = 0
    for i in range(n):
        for j in range(i + 1, n):
            for w in (vals[i] + vals[j], vals[i] - vals[j], vals[j] - vals[i]):
                l = rows.get(w.tobytes())
                if l is not None and l not in (i, j): rel += 1
            if np.array_equal(vals[i], vals[j]) or np.array_equal(vals[i], -vals[j]) or \
               np.array_equal(2 * vals[i], vals[j]) or np.array_equal(vals[i], 2 * vals[j]): rel += 1
    rms = np.sqrt((vals ** 2).mean(1))
    modal = float(np.mean([np.bincount(s).max() / s.size for s in scales]))
    return {"row_eq_max": row_eq, "row_d_star": k - k // 16, "blk64_eq_max": blk_eq, "slices_2to4": slice24,
            "zero_slices64": zero64, "short_relations": rel,
            "max_over_rms": float((np.abs(vals).max(1) / np.maximum(rms, 1e-30)).max()), "modal_byte_share": modal}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=64); ap.add_argument("--k", type=int, default=2048)
    ap.add_argument("--keys", type=int, default=6); ap.add_argument("--seed", type=int, default=20260930)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    calib = np.abs(np.random.default_rng(99).standard_normal(a.k)) * np.exp(np.random.default_rng(98).standard_normal(a.k))
    M = masters(a.n, a.k, rng)
    _, _, groups, _ = block_transform(a.k, 8, a.seed, calib)
    M["concentrated"] = concentrated(a.n, a.k, rng, groups)
    cells = []
    for name, W in M.items():
        for tf in ("none", "hadamard", "haar", "block8"):
            for key in (range(1) if tf == "none" else range(a.keys)):
                if tf == "none": Wr = W
                elif tf == "hadamard":
                    rot = RA.rotation(a.k, a.seed + 100 + key); Wr = np.array([rot(list(map(float, r))) for r in W])
                elif tf == "haar":
                    Q = haar(a.k, np.random.default_rng(a.seed + 100 + key)); Wr = W @ Q.T
                else:
                    f = block_transform(a.k, 8, a.seed + 100 + key, calib)[0]; Wr = np.array([f(list(map(float, r))) for r in W])
                c, s = quant(Wr)
                cc = census(c, s); cc.update(master=name, transform=tf, key=key)
                cells.append(cc); print(json.dumps(cc), flush=True)
    json.dump(cells, open("nvfp4_structure_census.json", "w"), indent=1)

if __name__ == "__main__":
    main()
