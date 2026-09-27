#!/usr/bin/env python3
"""Numbers for research/sms5/redesign/redesign.md: per-block loss, maximal answerable fraction, audit k,
and decode cost for design (a) rho_1 -> E -> rho_2 and design (b) three Rabin rounds / two permutations.

Conventions.  S = 0.95 B w bits of state, B = 2^28 records, T public-map evaluations per challenged block,
lambda' = 64.  Loss L per block; g*/B = 0.95 w / (w - L) + (log2 C(B,g) + lambda')/(B (w - L)); k = ceil(ln beta / ln p*).
Losses:
  L_FM  = log2 T + log2 g                    (Theorem A, proved: blocks recovered without an inverse hit)
  L_I   = 2 (log2 T_C)                       (two-root game at the Coppersmith line: guess-and-Coppersmith on both roots;
                                              T_C = T / 2^10 Coppersmith runs, one LLL charged as 2^10 evaluations)
  L_I+  = 2 (log2 T_C + 2 log2 T)            (if the shift-and-kangaroo saving stacks with Coppersmith: unsettled)
Design (b): the three-root strategy costs 3 (w/2 - ...) >= w, so only L_FM remains, under the weaker assumption
that a Rabin root keeps >= w/3 bits given its square.
Costs (int32 per weight byte, anchors from the brief): 2048-bit squaring 50, Montgomery mult 68 (3072: 93 -> squaring 68);
Keccak-f[1600] 17 per state byte (200 B).  E = Feistel over w/2-bit halves with SHAKE round functions:
absorb ceil(h/1088) + squeeze ceil(h/1088) - 1 permutation calls per round, h = w/2 bits.
"""
import math

B = 2 ** 28
LAMBDA = 64


def log2_binom(n, k):
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)) / math.log(2)


def gstar_frac(w, L, s_frac=0.95):
    if L >= w:
        return 1.0
    g = s_frac * B * w / (w - L)
    g = min(g, B)
    return min(1.0, (s_frac * B * w + log2_binom(B, int(g)) + LAMBDA) / (B * (w - L)))


def k_for(pstar, beta):
    if pstar >= 1.0:
        return float('inf')
    return math.ceil(math.log(beta) / math.log(pstar))


def keccak_calls_per_round(w):
    h = w // 2
    blocks = math.ceil(h / 1088)
    return 2 * blocks - 1


def e_cost(w, rounds):
    per_call = 17 * 200  # int32 for one Keccak-f[1600] on a 200-byte state
    return rounds * keccak_calls_per_round(w) * per_call / (w / 8)


def squaring_cost(w):
    return {2048: 50.0, 3072: 93.0 * 50 / 68}[w]


def main():
    print("== per-block loss, answerable fraction p*, audit k (beta = 1e-2 / 1e-6); S = 0.95|C|, B = 2^28 ==")
    print(f"{'w':>5} {'T':>6} {'variant':<26} {'L':>5} {'p*':>8} {'k(1%)':>7} {'k(1e-6)':>8}")
    for w in (2048, 3072):
        for logT in (20, 30):
            logTC = logT - 10
            L_FM = logT + 28
            L_I = 2 * logTC
            L_Ip = 2 * (logTC + 2 * logT)
            rows = [
                ("(a)/(b) FM only, Thm A", L_FM),
                ("(a) 2RG, no stacking", max(L_FM, L_I)),
                ("(a) 2RG, kangaroo stacks", max(L_FM, L_Ip)),
                ("(b) 3 rounds, l <= 2w/3", L_FM),
            ]
            for name, L in rows:
                p = gstar_frac(w, L)
                print(f"{w:>5} 2^{logT:<4} {name:<26} {L:>5} {p:>8.4f} {k_for(p, 1e-2):>7} {k_for(p, 1e-6):>8}")
    print()
    print("== decode cost, int32 per weight byte (budget: 150 prefill-only at 2x, 8 decode-batch at 2x) ==")
    print(f"{'w':>5} {'design':<8} {'squarings':>9} {'E rounds':>8} {'E cost':>7} {'total':>7}")
    for w in (2048, 3072):
        sq = squaring_cost(w)
        for design, nsq, nE in (("(a)", 2, 1), ("(b)", 3, 2)):
            for rounds, tag in ((2, "heur"), (8, "indiff")):
                ec = nE * e_cost(w, rounds)
                print(f"{w:>5} {design:<8} {nsq*sq:>9.0f} {rounds:>3} {tag:<4} {ec:>7.0f} {nsq*sq+ec:>7.0f}")
    print()
    print("== the store-the-trapdoor adversary (why no information-theoretic theorem exists) ==")
    for w in (2048, 3072):
        S_bits = 2 * (w // 2) + 0.0  # p and q
        print(f"  w = {w}: state {2*(w//2)} bits total + (|c| - |m|) ~ 4 bits per block; answers every block with 1 E^-1 query "
              f"and 2 trapdoor root extractions (~{2*w} sequential squarings, far inside Delta).")


if __name__ == "__main__":
    main()
