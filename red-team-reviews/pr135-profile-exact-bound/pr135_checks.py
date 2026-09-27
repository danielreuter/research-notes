#!/usr/bin/env python3
"""red-team-flock-3: independent checks of PR #135 (core IntegrityProfile: log-space rho, one-pass worst_case).

  pr135_checks.py NEW_TREE OLD_TREE      rho and worst_case of the new profile (NEW_TREE) against the old pairwise one
                                          (OLD_TREE) and an exact reference (Decimal, 60 digits, my own LP); a
                                          non-monotone input against a brute-force LP; the underflow regime
  pr135_checks.py MERGED_TREE compose     the combined #121 + #135 tree: TOY, the mixed class, the 750-point attack grid
"""
import importlib
import json
import math
import random
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from itertools import combinations
from math import comb

getcontext().prec = 60


def load(tree):
    for m in [k for k in sys.modules if k.startswith(("verity", "verity_sampled_proofs"))]:
        del sys.modules[m]
    sys.path[:0] = [f"{tree}/packages/verity/src", f"{tree}/protocols/sampled_proofs"]
    mod = importlib.import_module("verity.proofs.profile")
    sys.path[:2] = []
    return mod


def exact_rhos(n, k, p):
    """rho(m) = ln(den C(n, k)) - ln((den - num) C(n, k) + num C(n - m, k)) in 60-digit Decimal; None for inf."""
    num, den, top = p.numerator, p.denominator, comb(n, k)
    whole = Decimal(den * top).ln()
    out = []
    for m in range(n + 1):
        a = (den - num) * top + num * comb(n - m, k)
        out.append(None if a == 0 else whole - Decimal(a).ln())
    return out


def exact_lp(rhos, utility, members, delta):
    """The LP optimum, exactly: members * max over [0, t] of the upper concave envelope of (0, 0) and (rho(m), u(m)),
    t = ln(1/delta)/members.  For up to 400 points, brute force: every chord straddling t and every point below it.
    Above that, my own exact upper hull in Decimal (monotone chain), evaluated at t; the two agree where both run."""
    if members == 0:
        return Decimal(0)
    t = (Decimal(1) / Decimal(delta)).ln() / Decimal(members)
    pts = [(Decimal(0), Decimal(0))] + [(r, Decimal(utility(m))) for m, r in enumerate(rhos) if m >= 1 and r is not None
                                         and utility(m) > 0]
    if len(pts) <= 400:
        best = max((u for r, u in pts if r <= t), default=Decimal(0))
        lo = [(r, u) for r, u in pts if r <= t]
        hi = [(r, u) for r, u in pts if r > t]
        for (ra, ua) in lo:
            for (rb, ub) in hi:
                best = max(best, ua + (ub - ua) * (t - ra) / (rb - ra))
        return best * members
    return hull_value(pts, t) * members


def hull_value(pts, t):
    """max over [0, t] of the upper concave envelope of `pts`, exactly (Decimal)."""
    pts = sorted(pts)
    hull = []
    for p in pts:
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) >= 0:
                hull.pop()
            else:
                break
        hull.append(p)
    best = Decimal(0)
    for i, (x, y) in enumerate(hull):
        if x <= t:
            best = max(best, y)
            if i + 1 < len(hull) and hull[i + 1][0] > t:
                (xb, yb) = hull[i + 1]
                best = max(best, y + (yb - y) * (t - x) / (xb - x))
    return best


def old_worst_case(prof_old, utility):
    return prof_old.worst_case(utility)


def check(new_tree, old_tree):
    NEW, OLD = load(new_tree), load(old_tree)
    rng = random.Random(20260927)
    utilities = {"m": lambda m: m, "one": lambda m: 1, "m2": lambda m: m * m, "sqrt": lambda m: m ** 0.5,
                 "step": lambda m: 1 if m >= 3 else 0}
    rows, rho_rows = [], []
    for case in range(400):
        n = rng.choice([1, 2, 3, 5, 8, 16, 40, 100, 250])
        k = rng.randint(0, n)
        p = rng.choice([Fraction(1), Fraction(1, 2), Fraction(1, 7), Fraction(3, 4), Fraction(1, 1000), Fraction(99, 100)])
        members = rng.choice([1, 3, 10, 100, 1000, 10**6])
        delta = rng.choice([1e-2, 2.0 ** -20, 1e-9, 0.5])
        draws = lambda M: {"b": M.Bernoulli(p), "c": M.Subset(k)}  # noqa: E731
        pn = NEW.IntegrityProfile(("b", "c"), (members, n), draws(NEW), delta)
        po = OLD.IntegrityProfile(("b", "c"), (members, n), draws(OLD), delta)
        ex = exact_rhos(n, k, p)
        for m in range(n + 1):
            e = ex[m]
            rn = pn.rho(m)
            if e is None:
                rho_rows.append((rn == math.inf, 0.0, 0.0))
                continue
            ro = po.rho(m)
            rel = lambda r: float((Decimal(r) - e) / e) if e != 0 else float(Decimal(r) - e)  # noqa: E731
            rho_rows.append((True, rel(rn), rel(ro)))
        for name, u in utilities.items():
            wn, wo = pn.worst_case(u), po.worst_case(u)
            we = exact_lp(ex, u, members, delta)
            rows.append((case, name, n, k, str(p), members, delta, wn, wo, float(we)))
    d_new_old = [(r[7] - r[8]) / r[8] for r in rows if r[8] > 0]
    d_new_ex = [(r[7] - r[9]) / r[9] for r in rows if r[9] > 0]
    d_old_ex = [(r[8] - r[9]) / r[9] for r in rows if r[9] > 0]
    zero_mismatch = [r for r in rows if (r[8] == 0) != (r[7] == 0) or (r[9] == 0) != (r[7] == 0)]
    print("WORST_CASE\t" + json.dumps({"profiles": 400, "cases": len(rows),
                                       "new_vs_old_min_rel": min(d_new_old), "new_vs_old_max_rel": max(d_new_old),
                                       "new_below_old_by_more_than_1e-12": sum(d < -1e-12 for d in d_new_old),
                                       "new_vs_exact_min_rel": min(d_new_ex), "new_below_exact_count": sum(d < 0 for d in d_new_ex),
                                       "old_vs_exact_min_rel": min(d_old_ex), "old_below_exact_count": sum(d < 0 for d in d_old_ex),
                                       "zero_pattern_mismatches": len(zero_mismatch)}))
    rel_new = [r[1] for r in rho_rows if r[0]]
    rel_old = [r[2] for r in rho_rows if r[0]]
    print("RHO\t" + json.dumps({"values": len(rho_rows), "inf_agree": all(r[0] for r in rho_rows),
                                "new_max_over_rel": max(rel_new), "new_over_count": sum(x > 0 for x in rel_new),
                                "new_min_rel": min(rel_new), "old_max_over_rel": max(rel_old), "old_over_count": sum(x > 0 for x in rel_old)}))
    # a non-monotone risk sequence: the one-pass envelope sorts its points, so the order of m cannot shrink the bound
    pn = NEW.IntegrityProfile(("b", "c"), (1000, 40), {"b": NEW.Bernoulli(Fraction(1, 2)), "c": NEW.Subset(5)}, 1e-3)
    base = pn._rhos()
    shuffled = [base[0]] + rng.sample(base[1:], len(base) - 1)
    pn2 = NEW.IntegrityProfile(("b", "c"), (1000, 40), {"b": NEW.Bernoulli(Fraction(1, 2)), "c": NEW.Subset(5)}, 1e-3)
    object.__setattr__(pn2, "_rhos", lambda: shuffled) if False else None
    cls = type(pn2)
    orig = cls._rhos
    worst = []
    for name, u in utilities.items():
        cls._rhos = lambda self, s=shuffled: s
        w_shuf = pn2.worst_case(u)
        cls._rhos = orig
        # brute force: the LP over the same (shuffled) risks by pairwise vertices, in floats
        members, t = 1000, math.log(1e3) / 1000
        pts = [(0.0, 0.0)] + [(shuffled[m], float(u(m))) for m in range(1, 41) if u(m) > 0 and shuffled[m] < math.inf]
        b = max(uu for r, uu in pts if r <= t)
        for (ra, ua), (rb, ub) in combinations(pts, 2):
            if ra > rb:
                (ra, ua), (rb, ub) = (rb, ub), (ra, ua)
            if ra <= t < rb:
                b = max(b, ua + (ub - ua) * (t - ra) / (rb - ra))
        worst.append((name, w_shuf, b * members))
    cls._rhos = orig
    print("NONMONOTONE\t" + json.dumps({"cases": [(n, round(a, 9), round(b, 9)) for n, a, b in worst],
                                        "all_equal_1e-9": all(abs(a - b) <= 1e-9 * max(1, b) for _, a, b in worst)}))
    # the underflow regime: old arithmetic fails; new against exact
    out = {}
    for n, k, p, members, delta in ((4000, 256, Fraction(1), 1, 2.0 ** -20), (20000, 256, Fraction(1), 1, 2.0 ** -20),
                                    (183680, 256, Fraction(1), 1, 2.0 ** -20), (4000, 256, Fraction(1, 2), 50, 1e-6)):
        pn = NEW.IntegrityProfile(("b", "c"), (members, n), {"b": NEW.Bernoulli(p), "c": NEW.Subset(k)}, delta)
        w = pn.worst_case(lambda m: m)
        try:
            po = OLD.IntegrityProfile(("b", "c"), (members, n), {"b": OLD.Bernoulli(p), "c": OLD.Subset(k)}, delta)
            wo = po.worst_case(lambda m: m)
        except Exception as x:  # noqa: BLE001
            wo = f"{type(x).__name__}"
        ex = exact_rhos(n, k, p)
        we = float(exact_lp(ex, lambda m: m, members, delta))
        out[f"n={n},k={k},p={p},members={members}"] = {"new": w, "old": wo, "exact": we,
                                                        "new_minus_exact_rel": (w - we) / we if we else None}
    print("UNDERFLOW\t" + json.dumps(out))


def compose(tree):
    sys.path[:0] = [f"{tree}/packages/verity/src", f"{tree}/protocols/sampled_proofs"]
    from verity_sampled_proofs.law import ReplayUnit, Stage, TwoStageLaw
    toy = TwoStageLaw({"u": Stage(Fraction(1, 2), 2)})
    a = toy.profile("u", n_r=512, n_v=4, delta=0.01)
    units = [ReplayUnit(i, "u", 4) for i in range(200)] + [ReplayUnit(200 + i, "u", 8) for i in range(200)]
    b = toy.profile("u", units, delta=0.01)
    print("COMPOSE\t" + json.dumps({"toy_wrong_RUs": a.worst_case(lambda m: 1), "toy_work_VUs": a.worst_case(lambda m: 4 * m),
                                    "toy_attack": [16, 64], "mixed_n_v": b.sizes, "mixed_rate": str(b.draws["replay"].p),
                                    "mixed_wrong_RUs": b.worst_case(lambda m: 1), "mixed_attack": 34}))


if __name__ == "__main__":
    if sys.argv[2] == "compose":
        compose(sys.argv[1])
    else:
        check(sys.argv[1], sys.argv[2])
