"""Red-team for `tt-out/pearl-c-*-rev1`: after the first promotion, can any other promotion add be skipped?

rev1 credits k/(32G) − 1 promotions per word. Three ways a prover could still avoid one, each measured on census-formed
operands (the scheme's s5 forming, bit-exact atom, 64 × 64 tiles = 4,096 words, G = 4):
  (a) a promotion into a +0 total after the first (T_{g−1} = +0 makes T_g = S_g, free like the first);
  (b) fusion: feed T_{g−1} to the group's first atom as its accumulator, so the tensor core adds it and no FADD runs. It is
      correct where the fused word equals RNE(T_{g−1} + S_g). An oracle upper bound per (word, group), per 16 × 8 MMA
      fragment (all 128 words at once) and per tile;
  (c) the only way to use (b) without the oracle: a certificate that is cheap per tile, a Cauchy-Schwarz bound on
      |T_{g−1}| + |S_g| against the lowest bit the products can set. When the span fits FP32's 24 bits, every word is exact,
      so the fused and honest words agree. The share of (tile, group) it certifies.
"""
import argparse, importlib.util, json, os, sys
from pathlib import Path

import numpy as np

TREE = Path(os.environ.get("CENSUS_TREE") or f"/workspace/research/src/{os.environ.get('RESEARCH_SOURCE_SHA', '')}")
_spec = importlib.util.spec_from_file_location("pearlc_census", TREE / "benchmarks/pouw/pearlc_census.py")
C = importlib.util.module_from_spec(_spec)
sys.modules["pearlc_census"] = C
_spec.loader.exec_module(C)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rt_result  # noqa: E402

G = 4


def lowbit_exp(codes):
    """Per code: the exponent of its lowest set bit (value = SIG * 2^(EXP1 - 10)); +inf for zero."""
    m = codes.astype(np.int64) & 0x7F
    sig = C.SIG[m]
    low = np.log2(np.maximum(sig & -sig, 1)).astype(np.int64)
    return np.where(sig > 0, C.EXP1[m] - 10 + low, 10 ** 6)


def cell(fam, k, rows, cols):
    XA, XB, _, _ = C.family_rows(fam, k, 1.0, rows, cols, 1)
    FcA, FcB = C.s5_lines(k, 1, 16.0)
    a, _, _, fa, la = C.form_s5(XA, FcA, 1.0, 16.0, C._rng(1, fam, k, 1.0, "unit-A"))
    b, _, _, fb, lb = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, fam, k, 1.0, "unit-B"))
    P = rows * cols
    A, B = np.repeat(a, cols, 0), np.tile(b, (rows, 1))           # word w = (i, j), i = w // cols
    T = k // 32
    ng = T // G
    tot = np.zeros(P, np.float32)
    zero_in = fused_ok = 0
    frag_ok = np.zeros(ng, np.int64)
    tile_ok = np.zeros(ng, bool)
    frag_id = (np.arange(P) // cols // 16) * (cols // 8) + (np.arange(P) % cols) // 8
    nfrag = frag_id.max() + 1
    va, vb = C.val(a), C.val(b)
    la_, lb_ = lowbit_exp(a), lowbit_exp(b)
    cert = np.zeros(ng, bool)
    for g in range(ng):
        ts = list(range(g * G, (g + 1) * G))
        S, _ = C.group_run(A, B, ts)
        new = (tot + S.astype(np.float32)).astype(np.float32)
        new = np.where(new == 0, np.float32(0), new)
        if g >= 1:
            zero_in += int((tot == 0).sum())
            F = tot.astype(np.float64)
            for t in ts:
                F, _ = C.step(F, A[:, 32 * t:32 * t + 32], B[:, 32 * t:32 * t + 32])
            ok = F.astype(np.float32) == new
            fused_ok += int(ok.sum())
            frag_ok[g] = int(np.bincount(frag_id, weights=ok, minlength=nfrag).__eq__(128).sum())
            tile_ok[g] = bool(ok.all())
            hi = 128 * (g + 1)
            ub = np.sqrt((va[:, :hi] ** 2).sum(1)).max() * np.sqrt((vb[:, :hi] ** 2).sum(1)).max()
            grid = la_[:, :hi].min() + lb_[:, :hi].min()
            cert[g] = bool(ub < 2.0 ** (grid + 24))
        tot = new
    n = P * (ng - 1)
    return {"family": fam, "k": k, "in_domain": bool(fa and la and fb and lb), "words": P, "promotions_after_first": n,
            "zero_incoming_share": zero_in / n, "fused_correct_share_oracle": fused_ok / n,
            "fragment_fusable_share_oracle": float(frag_ok[1:].sum()) / ((ng - 1) * nfrag),
            "tile_fusable_groups_oracle": int(tile_ok[1:].sum()), "groups_after_first": ng - 1,
            "tile_certified_groups": int(cert[1:].sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default="gaussian,constant,zero-slices,sparse10,rank1,saturated,grid-aligned,spikes-first,"
                                          "outliers-first,aligned-spikes-r64,aligned-spikes-pm1-r444")
    ap.add_argument("--ks", default="8192,16384")
    ap.add_argument("--tile", default="64x64")
    args = ap.parse_args()
    C.set_atom(os.environ.get("CENSUS_ATOM", "sm120-e4m3-k32"))   # hopper-e4m3-k32 for the H100 rows
    rows, cols = map(int, args.tile.split("x"))
    cells = []
    for k in map(int, args.ks.split(",")):
        for fam in args.families.split(","):
            r = cell(fam, k, rows, cols)
            cells.append(r)
            print(json.dumps(r), flush=True)
    dom = [c for c in cells if c["in_domain"]]
    meas = [("zero_incoming_share_max", max(c["zero_incoming_share"] for c in dom), "fraction"),
            ("fused_correct_share_oracle_max", max(c["fused_correct_share_oracle"] for c in dom), "fraction"),
            ("fragment_fusable_share_oracle_max", max(c["fragment_fusable_share_oracle"] for c in dom), "fraction"),
            ("tile_certified_groups_total", sum(c["tile_certified_groups"] for c in dom), "groups")]
    rt_result.write("rev1-promotions-sm120", meas, {"tile": args.tile, "G": G, "cells": cells},
                    detail="bit-exact sm_120 atom, s5 forming; promotions after the first: +0-incoming, oracle fusion, cheap certificate")


if __name__ == "__main__":
    main()
