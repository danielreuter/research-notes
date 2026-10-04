"""Red-team for `known-weights/sm120-*` and `structure-free/rot-*`: does the beacon-keyed rotation really leave the
registered codes structure-free, over the key, so that knowing the fixed weights in advance buys a prover nothing?

The approved-weights fork fixes the weights and publishes them before any salt, so a prover preprocesses freely against the
codes the chain multiplies. That is safe only if the codes have no exploitable exact structure. The defence is a
beacon-keyed randomized Hadamard rotation folded into the weights, then per-row E4M3 (or NVFP4) rounding, with the verifier
uncrediting near-duplicate rows/blocks. This reuses the lane's own transform and chains (`relation-attack.py`) and adds the
assessor's three independent tests:

  (1) validation: the derived-word transfer on a crafted master (row3 = row1 + row2), as registered and after `rot`/`rot-sr`
      -- reproduces the lane's 100% -> 0%;
  (2) epsilon_T over the key: for S independent keys and each master, a structure census of the rotated codes -- the worst
      near-duplicate agreement per 128-group and 32-atom against the break-even margins d* (112/128, 29/32), any exact
      row/group duplicate, any exact two-row sum e4m3(row_i + row_j) matching a registered group, 2:4-compatible 64-slices,
      all-zero atoms, and max/RMS -- so the share of keys that leak exploitable structure;
  (3) key transfer: near-duplicate row pairs found under a decoy key do not recur under the real key;
  (4) known-weights low rank: the rotation preserves the master's rank, but the E4M3 residual R = codes - rot(W) is dense,
      so the low-rank-weight shortcut fails as it does for the noise core (rank-32 residual reported).
"""
import argparse, importlib.util, json, os, random, sys, time
from pathlib import Path

import numpy as np

AW = Path(os.environ.get("AW_DIR", "/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/approved-weights"))
_spec = importlib.util.spec_from_file_location("relation_attack", AW / "relation-attack.py")
RA = importlib.util.module_from_spec(_spec)
sys.modules["relation_attack"] = RA
_spec.loader.exec_module(RA)
TREE = Path(os.environ.get("CENSUS_TREE") or f"/workspace/research/src/{os.environ.get('RESEARCH_SOURCE_SHA', '')}")
_cs = importlib.util.spec_from_file_location("pearlc_census", TREE / "benchmarks/pouw/pearlc_census.py")
CE = importlib.util.module_from_spec(_cs)
sys.modules["pearlc_census"] = CE
_cs.loader.exec_module(CE)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rt_result  # noqa: E402

D_STAR_128, D_STAR_32 = 112, 29         # structure-free clause (a) break-evens: a derived group/atom pays below these


def real_master(n, k, rng, heavy):
    """A trained-weight stand-in: Gaussian rows, a `heavy` fraction with a few large outliers (spikes)."""
    W = rng.standard_normal((n, k))
    for i in range(n):
        if rng.random() < heavy:
            W[i, rng.integers(0, k, 3)] = rng.choice([-1, 1], 3) * rng.uniform(15, 40, 3)
    return W


TRANSFORM = "hadamard"          # set by --transform: hadamard (rung 2), haar (dense keyed Haar), block8 (rung 3, §8j)


def rotation_of(k, key):
    if TRANSFORM == "hadamard":
        return RA.rotation(k, key)
    if TRANSFORM == "haar":
        from relation_blocks_sm120 import haar
        Q = haar(k, np.random.default_rng(key))
        return lambda r: list(Q @ np.asarray(r, np.float64))
    from relation_blocks_sm120 import block_transform
    calib = np.abs(np.random.default_rng(99).standard_normal(k)) * np.exp(np.random.default_rng(98).standard_normal(k))
    return block_transform(k, int(TRANSFORM[5:]), key, calib)[0]


def rotate(W, key):
    rot = rotation_of(W.shape[1], key)
    return np.array([rot(list(map(float, r))) for r in W])


def e4m3_codes(W, sr_key=None, scale=True):
    """Per-row E4M3 as the transform requantizes (scale 448/max); `scale=False` is a registrant's own codes, unscaled."""
    al = 448.0 / np.abs(W).max(1, keepdims=True) if scale else np.ones((W.shape[0], 1))
    if sr_key is None:
        return CE.enc(al * W)
    srng = random.Random(sr_key)
    return np.array([[RA.e4m3_sr(float(v), srng) for v in r] for r in al * W], np.uint8)


def census(codes):
    n, k = codes.shape
    vals = CE.val(codes)
    G = k // 128
    g128 = codes.reshape(n, G, 128)
    a32 = codes.reshape(n, k // 32, 32)
    near128 = near32 = 0
    dup_rows = sum(int((codes[i] == codes[j]).all()) for i in range(n) for j in range(i + 1, n))
    sum_rel = 0
    grp_hashes = [set(map(lambda x: x.tobytes(), g128[:, g, :])) for g in range(G)]
    for i in range(n):
        for j in range(i + 1, n):
            eq128 = (g128[i] == g128[j]).sum(1).max()
            near128 = max(near128, int(eq128))
            eq32 = (a32[i] == a32[j]).sum(1).max()
            near32 = max(near32, int(eq32))
    for i in range(n):
        s = np.clip(vals[i][None, :] + vals[i + 1:], -448, 448)          # every j > i at once
        if s.size == 0:
            continue
        sc = CE.enc(s).reshape(-1, G, 128)
        for jj in range(sc.shape[0]):
            for g in range(G):
                if sc[jj, g].tobytes() in grp_hashes[g]:
                    sum_rel += 1
    zero_atoms = float(((a32 & 0x7F) == 0).all(-1).mean())
    z = (codes & 0x7F) == 0
    slice24 = float((z.reshape(n, k // 4, 4).sum(-1) >= 2).reshape(n, k // 64, 16).all(-1).mean())
    rms = np.sqrt((vals ** 2).mean(1))
    return {"near_dup_max_of_128": near128, "near_dup_max_of_32": near32, "dup_rows": dup_rows,
            "exact_two_row_sum_groups": sum_rel, "zero_atoms": zero_atoms, "slices_2to4": slice24,
            "spike_max_over_rms": float((np.abs(vals).max(1) / np.maximum(rms, 1e-9)).max()),
            "caught_by_rule": bool(near128 > D_STAR_128 or near32 > D_STAR_32 or dup_rows),
            "leaks": bool(sum_rel or slice24 or zero_atoms)}


def rank_residual(M, r=32):
    s = np.linalg.svd(M.astype(np.float64), compute_uv=False)
    return float(np.sqrt((s[r:] ** 2).sum() / (s ** 2).sum())) if s.size > r else 0.0


def validation(k, seed):
    """Reproduce the derived-word transfer on the wide crafted master, as registered and after rot/rot-sr (gauss acts)."""
    rng = random.Random(seed)
    acts = [[RA.e4m3_rn(v) for v in RA.activation_row(k, rng, "gauss", 1.0, 448.0)] for _ in range(16)]
    base = RA.crafted_fp8_wide(k, random.Random(seed + 5))
    out = {}
    rot = rotation_of(k, seed + 1)
    for transform in ("none", "rot-rn", "rot-sr"):
        if transform == "none":
            b = [[RA.e4m3_rn(v) for v in r] for r in base]
        else:
            srng = random.Random(seed + 7)
            b = []
            for rr in (rot(r) for r in base):
                al = 448.0 / max(abs(v) for v in rr)
                b.append([RA.e4m3_sr(al * v, srng) if transform == "rot-sr" else RA.e4m3_rn(al * v) for v in rr])
        m = 0
        for a in acts:
            _, p1 = RA.fp8_v1(a, b[0])
            _, p2 = RA.fp8_v1(a, b[1])
            t3, _ = RA.fp8_v1(a, b[2])
            m += RA.derive_v1(p1, p2, "rn") == t3
        out[transform] = round(m / len(acts), 4)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--k", type=int, default=2048)
    ap.add_argument("--keys", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20260930)
    ap.add_argument("--transform", default="hadamard", choices=("hadamard", "haar", "block8", "block16"))
    args = ap.parse_args()
    global TRANSFORM
    TRANSFORM = args.transform
    t0 = time.time()
    rng = np.random.default_rng(args.seed)
    masters = {"real-heavy": real_master(args.n, args.k, rng, 0.3),
               "crafted-relation": None}
    cr = RA.crafted_fp8_wide(args.k, random.Random(args.seed + 5))
    rest = [list(map(float, real_master(1, args.k, rng, 0.3)[0])) for _ in range(args.n - 4)]
    masters["crafted-relation"] = np.array([cr[0], cr[1], cr[2], cr[0]] + rest)      # row3 = row1 + row2, row4 = row1
    cells = []
    for name, W in masters.items():
        raw = census(e4m3_codes(W, scale=False))
        raw["master"], raw["transform"], raw["key"] = name, "none", -1
        cells.append(raw)
        print(json.dumps(raw), flush=True)
        for key in range(args.keys):
            Wr = rotate(W, args.seed + 100 + key)
            for tf, sr in (("rot-rn", None), ("rot-sr", args.seed + 200 + key)):
                codes = e4m3_codes(Wr, sr)
                c = census(codes)
                c["master"], c["transform"], c["key"] = name, tf, key
                c["rot_rank32_residual"] = rank_residual(CE.val(codes))
                cells.append(c)
                print(json.dumps({k: c[k] for k in ("master", "transform", "key", "near_dup_max_of_128", "near_dup_max_of_32",
                                                     "dup_rows", "exact_two_row_sum_groups", "slices_2to4", "caught_by_rule", "leaks",
                                                     "rot_rank32_residual", "spike_max_over_rms")}), flush=True)
    # key transfer: near-dup top pairs under a decoy key vs the real key
    W = masters["real-heavy"]
    def top_pairs(codes, m=20):
        n, k = codes.shape
        g128 = codes.reshape(n, k // 128, 128)
        sc = []
        for i in range(n):
            for j in range(i + 1, n):
                sc.append((int((g128[i] == g128[j]).sum(1).max()), i, j))
        return [(i, j) for _, i, j in sorted(sc, reverse=True)[:m]]
    decoy = e4m3_codes(rotate(W, args.seed + 100))
    real = e4m3_codes(rotate(W, args.seed + 999))
    g_real = real.reshape(args.n, args.k // 128, 128)
    dp = top_pairs(decoy)
    transfer = [int((g_real[i] == g_real[j]).sum(1).max()) for i, j in dp]
    val = {k: validation(args.k, args.seed) for k in ("crafted",)}["crafted"]
    keyed = [c for c in cells if c["key"] >= 0]
    summ = {"derived_words_correct_by_transform": val,
            "keys_with_leak": sum(c["leaks"] for c in keyed), "keyed_cells": len(keyed),
            "raw_crafted": {k: [c for c in cells if c["master"] == "crafted-relation" and c["key"] < 0][0][k]
                            for k in ("exact_two_row_sum_groups", "dup_rows", "leaks", "caught_by_rule")},
            "caught_by_rule_rot_rn": sum(c["caught_by_rule"] for c in keyed if c["transform"] == "rot-rn" and c["master"] == "crafted-relation"),
            "caught_by_rule_rot_sr": sum(c["caught_by_rule"] for c in keyed if c["transform"] == "rot-sr" and c["master"] == "crafted-relation"),
            "near_dup_128_max_over_keys": max(c["near_dup_max_of_128"] for c in keyed if c["master"] == "real-heavy"),
            "exact_two_row_sum_over_keys": sum(c["exact_two_row_sum_groups"] for c in keyed),
            "transfer_max_of_128_real_key": max(transfer), "transfer_decoy_pairs": len(dp),
            "rot_rank32_residual_min": min(c["rot_rank32_residual"] for c in keyed)}
    print(json.dumps({"summary": summ}), flush=True)
    meas = [("derived_none", val["none"], "fraction"), ("derived_rot_rn", val["rot-rn"], "fraction"),
            ("derived_rot_sr", val["rot-sr"], "fraction"), ("keys_with_leak", summ["keys_with_leak"], "keys"),
            ("near_dup_128_max_over_keys", summ["near_dup_128_max_over_keys"], "codes"),
            ("exact_two_row_sum_over_keys", summ["exact_two_row_sum_over_keys"], "groups"),
            ("transfer_max_of_128_real_key", summ["transfer_max_of_128_real_key"], "codes")]
    rt_result.write("known-weights-sm120", meas, {"n": args.n, "k": args.k, "keys": args.keys, "summary": summ,
                    "d_star": [D_STAR_128, D_STAR_32], "cells": cells}, detail="structure-free over the key; derived-word validation; key transfer",
                    status="passed" if summ["keys_with_leak"] == 0 and val["rot-rn"] == 0 else "failed")
    print(f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
