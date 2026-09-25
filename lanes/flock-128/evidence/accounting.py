#!/usr/bin/env python3
"""flock-128: whole-proof soundness ledger of one Flock b684b12 union proof, with NO proof-of-work credit.

Inputs: a challenge-site census (census/*.tsv, from pod-scripts/site_census.rs: every squeeze the prover makes, with
its call site) and the embedded Ligerito TOML the proof used (configs/m<m>_<profile>.toml, whose expected_eps_*_bits
are Flock's own raw per-level bounds, i.e. before the grinding bits are added).

Per-site rule: a nonzero degree-D bad-event polynomial at a fresh uniform F128 challenge fails with prob <= D/2^128.
Degrees are the ones in flock docs/128-bit-grinding-audit.md "Implemented schedules" (b684b12).
Usage: accounting.py census.tsv configs/m33_fast.toml [--reps 2] [--fs-queries-log2 60]
"""
import math
import sys
import tomllib

PIOP = {  # call site (file:line prefix) -> (label, degree per call); either the PoW or the plain line of a site
    "zerocheck.rs:704": ("zerocheck initial eq point (skip coords)", "M"),
    "zerocheck.rs:708": ("zerocheck initial eq point (skip coords)", "M"),
    "zerocheck.rs:710": ("zerocheck initial eq point (outer coords, same vector)", 0),
    "zerocheck.rs:758": ("zerocheck univariate-skip point", 127),
    "zerocheck.rs:762": ("zerocheck univariate-skip point", 127),
    "zerocheck.rs:863": ("zerocheck multilinear rounds", 2),
    "zerocheck.rs:867": ("zerocheck multilinear rounds", 2),
    "lincheck/union.rs:308": ("lincheck batching alpha", 1),
    "lincheck/union.rs:312": ("lincheck batching alpha", 1),
    "lincheck/union.rs:371": ("lincheck per-circuit beta", 1),
    "lincheck/union.rs:375": ("lincheck per-circuit beta", 1),
    "lincheck.rs:1898": ("lincheck column-sumcheck rounds", 2),
    "lincheck.rs:1902": ("lincheck column-sumcheck rounds", 2),
    "lincheck.rs:1937": ("lincheck final skip point", 63),
    "lincheck.rs:1226": ("lincheck final skip point", 63),
    "pcs/ring_switch.rs:2579": ("ring-switch point in F128^7", 7),
    "pcs/ring_switch.rs:2581": ("ring-switch point in F128^7", 7),
    "pcs.rs:2040": ("opening batching gamma (vector, total degree 1)", 1),
    "pcs.rs:2044": ("opening batching gamma (vector, total degree 1)", 1),
    "pcs.rs:574": ("combined-basis gamma", 1),
    "pcs.rs:1898": ("merged opening sumcheck rounds", 2),
    "pcs.rs:1902": ("merged opening sumcheck rounds", 2),
    "pcs/jagged.rs:3005": ("multipoint gamma (degree K-1)", 255),
    "pcs/jagged.rs:3007": ("multipoint gamma (degree K-1)", 255),
    "pcs/jagged.rs:3246": ("multipoint two-product sumcheck rounds", 2),
    "pcs/jagged.rs:3250": ("multipoint two-product sumcheck rounds", 2),
    "pcs/jagged.rs:2032": ("Frobenius-anchor assist rounds (a)", 2),
    "pcs/jagged.rs:2036": ("Frobenius-anchor assist rounds (a)", 2),
    "pcs/jagged.rs:2057": ("Frobenius-anchor assist rounds (b)", 2),
    "pcs/jagged.rs:2061": ("Frobenius-anchor assist rounds (b)", 2),
    "pcs.rs:2282": ("transcript fork seed (no identity tested)", 0),
}
LIGERITO_SITES = ("ligerito/extension.rs", "ligerito.rs:4523")


def site_key(frame):
    loc = frame.split(" ")[0]
    for k in PIOP:
        if loc.startswith("flock-core/src/" + k + ":"):
            return k
    return None


def lg(x):
    return math.log2(x) if x > 0 else float("-inf")


def ledger(census_path, toml_path, reps=1, fs_q_log2=0):
    rows = [l.rstrip("\n").split("\t") for l in open(census_path) if l.startswith("SITE")]
    cfg = tomllib.load(open(toml_path, "rb"))
    m = cfg["m"]
    M = m + 1  # M_bool of the union zerocheck (dense_m + 1 for these two-table unions)
    terms = {}
    unknown = []
    for _, kind, calls, elems, bits, frame in rows:
        calls = int(calls)
        if any(s in frame.split(" ")[0] for s in LIGERITO_SITES):
            continue
        k = site_key(frame)
        if k is None:
            unknown.append(frame)
            continue
        label, deg = PIOP[k]
        deg = M if deg == "M" else deg
        t = terms.setdefault(("F128 PIOP/opening", label), [0, 0.0, bits])
        t[0] += calls
        t[1] += calls * deg / 2.0**128
    lv = cfg["levels"]
    n = len(lv)
    # claim batching: 1 call at L0 (its OOD) + (ood_samples[l] + 1) calls at each deeper level + 1 final
    claim = 2.0 ** -lv[0]["expected_eps_claim_batch_bits"]
    for l in range(1, n):
        claim += (lv[l]["ood_samples"] + 1) * 2.0 ** -lv[l]["expected_eps_claim_batch_bits"]
    claim += 2.0 ** -lv[-1]["expected_eps_claim_batch_bits"]
    terms[("Ligerito F128", "claim batching beta (list-unioned)")] = [
        1 + sum(lv[l]["ood_samples"] + 1 for l in range(1, n)) + 1, claim, "claim_batch_grinding_bits"]
    terms[("Ligerito F128", "queried-consistency batching alpha")] = [
        n, sum(2.0 ** -x["expected_eps_consistency_batch_bits"] for x in lv), "consistency_batch_grinding_bits"]
    terms[("Ligerito queries", "Johnson-regime consistency queries (raw, eta=0.02)")] = [
        sum(x["queries"] for x in lv), sum(2.0 ** -x["expected_eps_query_bits"] for x in lv), "grinding_bits"]
    terms[("Ligerito F256", "MCA / proximity gaps (BCH+25 list decoding)")] = [
        n, sum(2.0 ** -x["expected_eps_pg_bits"] for x in lv), "-"]
    terms[("Ligerito F256", "list-unioned quadratic fold sumcheck")] = [
        n, sum(2.0 ** -x["expected_eps_sumcheck_bits"] for x in lv), "-"]
    terms[("Ligerito F128", "two-point OOD binding")] = [
        n, sum(2.0 ** -x["expected_eps_ood_bits"] for x in lv), "-"]
    total = sum(v[1] for v in terms.values())
    fs = 2.0 ** fs_q_log2
    return m, cfg, terms, total, unknown, [x["queries"] for x in lv], [x["grinding_bits"] for x in lv]


def main():
    a = sys.argv[1:]
    reps = int(a[a.index("--reps") + 1]) if "--reps" in a else 1
    fsq = int(a[a.index("--fs-queries-log2") + 1]) if "--fs-queries-log2" in a else 60
    m, cfg, terms, total, unknown, qs, gb = ledger(a[0], a[1])
    print(f"# {a[0]}  {a[1]}  m={m}  queries/level={qs}  query PoW bits/level={gb}")
    print("| group | term | challenges | log2 eps (raw, no PoW credit) |")
    print("|---|---|---|---|")
    for (g, lab), (calls, e, _) in terms.items():
        print(f"| {g} | {lab} | {calls} | {lg(e):.1f} |")
    print(f"| total | one run, interactive coins | | **{lg(total):.1f}** |")
    print(f"| total | one run, Fiat-Shamir (x2^{fsq} state restoration) | | {lg(total) + fsq:.1f} |")
    grp = {}
    for (g, _), (_, e, _) in terms.items():
        grp[g] = grp.get(g, 0.0) + e
    print("groups: " + ", ".join(f"{g} {lg(e):.1f}" for g, e in grp.items()))
    if reps > 1:
        print(f"| total | {reps} sequential runs, independent interactive coins (product) | | **{reps * lg(total):.1f}** |")
    if unknown:
        print("UNMAPPED:", *unknown, sep="\n  ")


if __name__ == "__main__":
    main()
