"""Monte Carlo check of #556's F1′ (a03b3ed8) against the real forming.

For one row x and one E line, draw fresh F lines (32 uniform nibbles per position, as `basis` makes them), form every
element through the real `noise_atom` and `quantize`, and compare, per 128-window:
  realised = max(0, max(R_24(X), R_skip(N_0, N_1)) − κ)   (the cheater routes after the salt, at F1′'s sorted layout)
  charge   = split_saving(p, κ)                             (#556's formula at this draw's realised κ)
with p_t, the modal bytes and the modal codes from the exact law.  Also counts elements whose realised code at the
modal byte differs from the edge-rule bin of the same noisy FP32 value (ties and RZ, which the law doesn't model).

usage: PYTHONPATH=<pr556 tree paths> python f1prime_mc_check.py --draws 400 --out mc.json
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys

sys.path.insert(0, "/tmp/pr556/protocols/pouw/tests")

from verity_pouw.schemes import pearl_c4 as F  # noqa: E402
import test_pouw_pearl_c4 as T  # noqa: E402

P = F.P
f = F.NVFP4
C = F.FFMA_UNITS / F.SPAN_K
GAIN = [max(0.0, 0.5 - C * x) for x in range(F._EXCESS_MAX + 1)]
VALS = [-6, -4, -3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3, 4, 6]


def gauss_row(i: int, k: int) -> list[int]:
    rng = random.Random(1000 + i)
    return T._row([rng.gauss(0, 1) for _ in range(k)])


def offset_row(i: int, k: int, s: float = 8.0) -> list[int]:
    """Fixed-offset spike rows: 15 entries per block at s, one at a fixed small offset; the family the Gaussian
    under-charged ~20x (fp4-basesplit-fix-review.md)."""
    rs = 1 if i % 2 else -1
    return T._row([rs * (s if t % 16 else 1.0) for t in range(k)])


def tie_row(i: int, k: int) -> list[int]:
    """Dyadic values set half a cell from a code, so noisy values meet bin edges exactly when n hits the lattice."""
    rs = 1 if i % 2 else -1
    return T._row([rs * (8.0 if t % 16 == 0 else [0.25, 0.75, 1.25, 1.75][t % 4] * 8.0 / 6.0) for t in range(k)])


FAMILIES = {
    "spike": lambda i, k: T.spike_row(i, k),
    "spike-top": lambda i, k: T.spike_row(i, k, top=8.9 * 1.3),
    "narrow-cell": lambda i, k: T.narrow_cell_row(i, k),
    "offset-8": lambda i, k: offset_row(i, k),
    "tie": tie_row,
    "gauss": gauss_row,
}


def edge_bin(value: float, vs: float) -> int:
    edges = [-m * vs for m in reversed(F._E2M1_MIDPOINTS)] + [m * vs for m in F._E2M1_MIDPOINTS]
    return sum(1 for e in edges if value >= e)


def model(x, e_row, alpha, ae, dead):
    """p_t, modal bytes, and per element the modal bin (argmax of the law's bin probabilities at the modal byte)."""
    p, modes = F.change_probabilities(f, x, alpha, e_row, ae, dead)
    cdf = F._below_law(tuple(e_row), F._scale_value(F.NVFP4, ae) / 64)
    modal_bin = []
    for b in range(0, len(x), f.block):
        vs = F._scale_value(f, modes[b // f.block])
        edges = [-m * vs for m in reversed(F._E2M1_MIDPOINTS)] + [m * vs for m in F._E2M1_MIDPOINTS]
        for t in range(b, b + f.block):
            vt = P.f32_of_bits(F.fp32.mul(alpha, x[t]))
            c = [0.0] + [cdf(e - vt) for e in edges] + [1.0]
            probs = [c[i + 1] - c[i] for i in range(len(c) - 1)]
            modal_bin.append(max(range(len(probs)), key=lambda i: probs[i]))
    return p, modes, modal_bin


def layout(pw):
    """F1′'s layout per block: indices sorted by p, neighbours paired, pairs dealt round-robin to the 8-chunks."""
    chunks = []
    for b in range(0, len(pw), f.block):
        order = sorted(range(b, b + f.block), key=lambda t: pw[t])
        pairs = [(order[i], order[i + 1]) for i in range(0, len(order), 2)]
        n = len(order) // 8
        chunks += [pairs[c::n] for c in range(n)]
    return chunks


def excess(chunks, changed):
    x = 0
    for ch in chunks:
        js = [changed[a] + changed[b] for a, b in ch]
        dev = sorted(j for j in js if j)
        x += sum(dev[:len(dev) - 2]) if len(dev) > 2 else 0
    return min(x, F._EXCESS_MAX)


def run_row(x, e_row, draws, rng):
    k = len(x)
    _, _, alpha, _, ae = F.stats(f, x)
    dead = F.salt_dead(f, x, alpha, ae)
    p, modes, modal_bin = model(x, e_row, alpha, ae, dead)
    wins = list(range(0, k - k % F.SPAN_K, F.SPAN_K))
    lay = {w: layout(p[w:w + F.SPAN_K]) for w in wins}
    per = F.SPAN_K // f.block
    real_sum = [0.0] * len(wins)
    charge_sum = [0.0] * len(wins)
    diff_sq = [0.0] * len(wins)
    mism = 0
    moved_tot = 0
    for _ in range(draws):
        noisy = [F.noise_atom(F.fp32.mul(alpha, x[t]), e_row, ae, [rng.randrange(16) for _ in range(F.R)])
                 for t in range(k)]
        codes, scales = F.quantize(f, noisy)
        hw = F.hw_scales(f, scales)
        changed = []
        for t in range(k):
            blk = t // f.block
            vs = F._scale_value(f, modes[blk])
            bi = edge_bin(P.f32_of_bits(noisy[t]), vs)
            if hw[blk] == modes[blk]:
                cv = float(F.e2m1_value(codes[t]))
                if cv != VALS[bi]:
                    mism += 1
            changed.append(int(bi != modal_bin[t]))
        for wi, w in enumerate(wins):
            b0 = w // f.block
            moved = sum(hw[b] != modes[b] for b in range(b0, b0 + per))
            moved_tot += moved
            kappa = min(C * moved, F.DENSE_CORRECTION)
            ch = changed[w:w + F.SPAN_K]
            xx = excess(lay[w], ch)
            n0, n1 = min(sum(ch[:F.ATOM]), F._EXCESS_MAX), min(sum(ch[F.ATOM:]), F._EXCESS_MAX)
            r24, rsk = GAIN[xx], GAIN[n0] + GAIN[n1]
            rv, cv_ = max(0.0, max(r24, rsk) - kappa), F.split_saving(f, p[w:w + F.SPAN_K], kappa)
            real_sum[wi] += rv
            charge_sum[wi] += cv_
            diff_sq[wi] += (rv - cv_) ** 2
    se = [math.sqrt(max(0.0, q / draws - ((r - c) / draws) ** 2) / draws) for q, r, c in zip(diff_sq, real_sum, charge_sum)]
    return {"realised": [s / draws for s in real_sum], "charge": [s / draws for s in charge_sum], "diff_se": se,
            "p_mean": sum(p) / k, "edge_vs_quantizer_mismatch": mism, "moved_blocks_per_window_draw": moved_tot / (draws * len(wins))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=300)
    ap.add_argument("--k", type=int, default=256)
    ap.add_argument("--rows", type=int, default=2)
    ap.add_argument("--row0", type=int, default=0)
    ap.add_argument("--family", default="all")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    fams = FAMILIES if a.family == "all" else {a.family: FAMILIES[a.family]}
    out = {}
    for name, fam in fams.items():
        res = []
        for i in range(a.row0, a.row0 + a.rows):
            x = fam(i, a.k)
            e_row = F.line(bytes([0x31 + i]) * 32, F.ROLE_EA, i)
            r = run_row(x, e_row, a.draws, random.Random(97 + i))
            r["row_passes"] = F.row_passes(f, x)
            res.append(r)
        tr = sum(sum(r["realised"]) for r in res)
        tc = sum(sum(r["charge"]) for r in res)
        out[name] = {"rows": res, "realised_total": tr, "charge_total": tc,
                     "ratio_realised_over_charge": (tr / tc) if tc else (math.inf if tr else 0.0)}
        print(name, json.dumps({kk: v for kk, v in out[name].items() if kk != "rows"}), flush=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
