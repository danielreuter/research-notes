# Writer: bc-cb8013f7 (by its own report), an agent the sm_120 PoUW coordinator (bc-2aa33ad8) started by mistake, not the assessor (bc-d7d4b0d1). Not adopted by the assessor as of 30 Sep 2026, 09:20Z.
"""T1's two closures under attack: do Pearl-C4 v2's floors bite? (CPU, bit-exact on the pinned sm_120 NVFP4 atom.)

T1 starts every chain from H = 1.5 * 2^E_H, so the word is H + sum_t floor_G(S_t), G = ulp(H) (`step-floor/nvfp4`).  Two
closures rest on the floors discarding something:
  - X-FP4-1, the salt-free base split: it must fetch one pre-salt partial per atom (28-35 units per MAC), not one per word;
  - D-24's merged k128 route: one align-add over two atoms gives floor(S1 + S2), which differs from floor(S1) + floor(S2).
Where no floor bites, H + sum floor_G(S_t) = H + sum S_t, and both routes (and every exact-sum route) reproduce the word.

E_H rules at hot bits h: `row` (fp4_emulation's calibration: the row's largest RMS atom sum, from the products) and
`forming` (GPU 5's product-free default, fp4-design item 13: e(alpha_i rho_i) + e(alpha_j rho_j) + 3 + 23 - h, with D-NF's
rho over every 8th position).

Families: the census's gaussian, t4 and massive, and three attacks, each admitted by D-NF and D-SS as written (checked):
  coherent   A's rows and B's columns share one direction (rank 1 plus i.i.d.): real atom sums exceed the estimate
  spiky      one large entry per 16-block, the rest small: block scales large against the row's RMS
  stride     positions 0, 8, 16, ... small, the rest large: rho (every 8th position) is about 1/10 of each block's amax,
             inside D-SS's dead-block screen (clean amax_b <= 12 rho), so the noise and the forming estimate shrink

A candidate fix, `unit`: ulp(H) = 2^c times the word's median group-term unit 2^(e_a + e_b - 2), from the block scales'
exponents of row i and column j (product-free and tile-local).  It puts every atom's floor c bits into its own grid.

    uv run --no-project --with numpy python t1_closures_attack.py --emu /tmp/fp4em/benchmarks/pouw --out t1.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

FAMILIES = ("gaussian", "t4", "massive", "coherent", "spiky", "stride")


def load(emu: str):
    spec = importlib.util.spec_from_file_location("fp4_emulation", Path(emu) / "fp4_emulation.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def real(E, fam: str, side: str, n: int, k: int, rng: np.random.Generator) -> np.ndarray:
    if fam in ("gaussian", "t4", "massive"):
        return E.family(fam, side, n, k, rng)
    if fam == "coherent":
        u = np.random.default_rng(11).standard_normal(k)                       # the same direction in A and B
        return rng.standard_normal((n, 1)) * u[None] + 0.5 * rng.standard_normal((n, k))
    if fam == "spiky":
        x = 0.08 * rng.standard_normal((n, k))
        nb = k // 16
        pos = rng.integers(0, 16, (n, nb)) + 16 * np.arange(nb)[None]
        x[np.arange(n)[:, None], pos] = rng.choice([-1.0, 1.0], (n, nb)) * rng.uniform(0.8, 1.0, (n, nb))
        return x
    if fam == "stride":
        x = rng.choice([-1.0, 1.0], (n, k)) * rng.uniform(0.5, 1.0, (n, k))
        x[:, ::8] = rng.standard_normal((n, k // 8)) / 10.0
        return x
    raise ValueError(fam)


def stats(x: np.ndarray, delta: float):
    """D-NF's s, rho (every 8th position), sigma and alpha0, as `quantize_pearl_c4` computes them."""

    s = np.abs(x).max(axis=1, keepdims=True)
    rho = np.sqrt((x[:, ::8] ** 2).mean(axis=1, keepdims=True))
    sigma = delta * rho
    return s, rho, sigma, 2688.0 / np.maximum(s + 4 * sigma, 2.0 ** -32)


def quant(E, x: np.ndarray, delta: float, z: np.ndarray):
    """`quantize_pearl_c4` with its noise draw given (z = 0: the salt-free codes the base split precomputes)."""

    _, _, sigma, alpha0 = stats(x, delta)
    v = alpha0 * (x + sigma * z)
    n, k = v.shape
    sc = np.maximum(E.ue4m3_rn(np.abs(v).reshape(n, k // 16, 16).max(axis=2) / 6.0), 1)
    ma, ea = E.ue4m3_dyadic(sc)
    return E.e2m1_rn(v / np.repeat(ma * np.exp2(ea), 16, axis=1)), sc


def domain(E, x: np.ndarray, delta: float) -> dict:
    """D-NF's admission (a_E normal) and D-SS's dead-block screen, on the clean row."""

    s, rho, sigma, alpha0 = stats(x, delta)
    a_e = E.ue4m3_rn((sigma * alpha0 * np.float32(16 / np.sqrt(2346.125))).ravel())
    amax = np.abs(x).reshape(x.shape[0], -1, 16).max(axis=2)
    dead = (amax ** 2 > 144 * rho ** 2).sum(axis=1)
    per64 = dead / (amax.shape[1] / 64)
    return {"admitted_rows": float((a_e >= 8).mean()), "max_dead_blocks_per_64": float(per64.max()),
            "rows_in_d_ss": float((per64 <= 1).mean()), "amax_over_rho_p50": float(np.median(amax / rho))}


def census(E, x: np.ndarray, delta: float, rng: np.random.Generator) -> dict:
    """The v1 base split's census on A: salted codes against the salt-free ones, and the 2:4-correctable spans."""

    c1, s1 = quant(E, x, delta, rng.standard_normal(x.shape))
    c0, s0 = quant(E, x, delta, np.zeros(x.shape))
    n, k = x.shape
    changed = c1 != c0
    same_scale = np.repeat(s1 == s0, 16, axis=1)
    group_ok = ((changed.reshape(n, k // 4, 4).sum(axis=2) <= 2)
                & same_scale.reshape(n, k // 4, 4).all(axis=2))                  # the correction fits one 2:4 pass
    spans = group_ok[: n - n % 16].reshape(n // 16, 16, k // 128, 32).all(axis=(1, 3))
    return {"code_change_density": float(changed.mean()), "scale_change_share": float((s1 != s0).mean()),
            "group_2of4_share": float(group_ok.mean()), "span_2of4_share": float(spans.mean())}


def forming_hot(E, xa: np.ndarray, xb: np.ndarray, delta: float, h: int) -> np.ndarray:
    """GPU 5's rule: E_H(i, j) = e(alpha_i rho_i) + e(alpha_j rho_j) + 3 + 23 - h, e the exponent of the f32 RN product."""

    def e(x):
        _, rho, _, alpha0 = stats(x, delta)
        prod = (alpha0.astype(np.float32) * rho.astype(np.float32)).ravel()
        return ((prod.view(np.uint32).astype(np.int64) >> 23) & 0xFF) - 127

    eh = e(xa)[:, None] + e(xb)[None, :] + 3 + 23 - h
    return (((eh + 127) << 23) | (1 << 22)).astype(np.uint32)


def unit_hot(p, c: int) -> np.ndarray:
    """The candidate: E_H - 23 = floor(median_b e_a(i, b)) + floor(median_b e_b(j, b)) - 2 + c."""

    ea = np.floor(np.median(p.eaa, axis=1)).astype(np.int64)
    eb = np.floor(np.median(p.eab, axis=1)).astype(np.int64)
    eh = ea[:, None] + eb[None, :] - 2 + c + 23
    return (((eh + 127) << 23) | (1 << 22)).astype(np.uint32)


def merged_one(E, p, c0: np.ndarray, t: int) -> np.ndarray:
    """The chain with only atoms 2t and 2t+1 merged into one align-add: a word with a single 2:4 span."""

    c, s = c0.copy(), 0
    while s < p.nblk // 4:
        width = 2 if s == 2 * t else 1
        b = slice(4 * s, 4 * (s + width))
        c = E.nvf4_step(c, list(p.mant[b]), list(p.x[b]), list(p.part[b]))
        s += width
    return c


def attack(E, p, H: np.ndarray) -> dict:
    hm, he, ef = E.f32_dyadic(H)
    eh = ef - 127
    nat, same = p.native(H, record=True)
    rz, _ = p.exact(H)
    steps = p.nblk // 4
    bites = np.zeros(H.shape, np.int64)
    coarse = 0
    for t in range(steps):
        st = np.zeros(H.shape, np.int64)
        minx = np.full(H.shape, 1 << 40, np.int64)
        for g in range(4 * t, 4 * t + 4):
            st = st + E.trunc0(p.mant[g], p.x[g], eh - 35)
            minx = np.minimum(minx, np.where(p.mant[g] != 0, p.x[g], 1 << 40))
        bites += (st & 0xFFF) != 0                                               # floor_G discards part of the atom
        coarse += int((minx >= eh - 23).sum())                                   # the atom's own grid is at least G
    s = p.step_sums().astype(np.float64) * 2.0 ** -20
    log_rms = np.log2(np.maximum(np.sqrt((s ** 2).mean(axis=0)), 2.0 ** -200))
    h_eff = log_rms - (eh - 23)
    hv = H.view(np.float32).astype(np.float64)
    cv = nat.view(np.float32).astype(np.float64)
    s_exact = s.sum(axis=0)
    err = (cv - hv) - s_exact
    scale = np.sqrt((s_exact ** 2).mean())
    n = H.size
    return {"exact_rz": float((rz == nat).mean()), "step_floor": float((p.step_floor(H) == nat).mean()),
            "merged_k128": float((E.merged_k128(p, H) == nat).mean()),
            "merged_one_span": float((merged_one(E, p, H, steps // 4) == nat).mean()),
            "atoms_bitten": float(bites.sum() / (n * steps)), "words_never_bitten": float((bites == 0).mean()),
            "atoms_coarser_than_G": coarse / (n * steps), "identity_atoms": same / (n * steps),
            "left_H_binade": float((((nat.astype(np.int64) >> 23) & 0xFF) != ef).mean()),
            "peel_inexact": float((np.abs(cv - hv) > hv / 2).mean()),
            "rel_err_rms": float(np.sqrt((err ** 2).mean()) / scale), "rel_bias": float(err.mean() / scale),
            "h_eff": {q: float(np.percentile(h_eff, v)) for q, v in (("p1", 1), ("p50", 50), ("p99", 99))}}


def rms_over_unit(p) -> dict:
    """log2 of each word's RMS atom sum over its median group-term unit 2^x: how many bits a floor can reach into."""

    s = p.step_sums().astype(np.float64) * 2.0 ** -20
    r = np.log2(np.maximum(np.sqrt((s ** 2).mean(axis=0)), 2.0 ** -200)) - np.median(p.x, axis=0)
    return {q: float(np.percentile(r, v)) for q, v in (("p1", 1), ("p50", 50), ("p99", 99))}


def merge(parts: list[str], out: str) -> int:
    """One JSON from per-family parts, and the run's result.json (`rt_result.write`) when under `research run`."""

    res = None
    for part in parts:
        doc = json.loads(Path(part).read_text())
        if res is None:
            res = doc
        else:
            res["families"].update(doc["families"])
    import hashlib

    res["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    Path(out).write_text(json.dumps(res, indent=1))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import rt_result

    meas = [(f"{fam}/{rule}/{metric}", v[rule][metric], "fraction")
            for fam, v in res["families"].items() for rule in ("row/h14", "forming/h14", "unit/c3") if rule in v
            for metric in ("exact_rz", "merged_k128", "atoms_bitten")]
    rt_result.write("t1-closures", meas, res, detail="T1 floors bite? exact-sum and merged-k128 routes against the hot chain")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--emu", help="directory holding fp4_emulation.py (branch cursor/fp4-emulation-cf5b)")
    ap.add_argument("--merge", nargs="+", help="merge these per-family outputs into --out")
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--rows", type=int, default=64)
    ap.add_argument("--cols", type=int, default=64)
    ap.add_argument("--delta", type=float, default=0.25)
    ap.add_argument("--row-bits", default="14")
    ap.add_argument("--forming-bits", default="10,12,14")
    ap.add_argument("--unit-bits", default="1,2,3")
    ap.add_argument("--seed", type=int, default=20260930)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    if args.merge:
        return merge(args.merge, args.out)
    E = load(args.emu)
    res = {"k": args.k, "rows": args.rows, "cols": args.cols, "delta": args.delta, "seed": args.seed,
           "atom": E.BLACKWELL_SM120_NVF4.name, "families": {}}
    for fam in args.families.split(","):
        rng = np.random.default_rng(args.seed)
        xa = real(E, fam, "A", args.rows, args.k, rng)
        xb = real(E, fam, "B", args.cols, args.k, rng)
        ca, sa = E.quantize_pearl_c4(xa, args.delta, rng)
        cb, sb = E.quantize_pearl_c4(xb, args.delta, rng)
        p = E.Problem.from_codes(ca, sa, cb, sb)
        zero = np.zeros((args.rows, args.cols), np.uint32)
        cold = p.native(zero)
        out = {"domain_A": domain(E, xa, args.delta), "domain_B": domain(E, xb, args.delta),
               "census_A": census(E, xa, args.delta, np.random.default_rng(args.seed + 1)),
               "log2_rms_over_unit": rms_over_unit(p),
               "cold": {"exact_rz": float((p.exact()[0] == cold).mean()),
                        "merged_k128": float((E.merged_k128(p, zero) == cold).mean())}}
        for h in (int(v) for v in args.row_bits.split(",") if v):
            out[f"row/h{h}"] = attack(E, p, E.hot_accumulator(p, h, "row"))
        for h in (int(v) for v in args.forming_bits.split(",") if v):
            out[f"forming/h{h}"] = attack(E, p, forming_hot(E, xa, xb, args.delta, h))
        for c in (int(v) for v in args.unit_bits.split(",") if v):
            out[f"unit/c{c}"] = attack(E, p, unit_hot(p, c))
        res["families"][fam] = out
        print(fam, json.dumps(out), flush=True)
    Path(args.out).write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
