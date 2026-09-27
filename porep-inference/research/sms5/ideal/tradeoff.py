#!/usr/bin/env python3
"""Numbers for research/sms5/ideal/tradeoff.md (ideal-model completion bound, RW-SMS raw-block audit).

Everything is derived from Theorem 1 of tradeoff.md (the per-block-oracle restatement of
tdp.md Theorem B1, with R3's F1/F2 tightenings) and its k-block plug-in.  stdlib only.
Run: python3 tradeoff.py            (prints the tables; < 1 s)
     python3 tradeoff.py --all      (also prints the S = 18/19 rows and the simultaneous-reveal table)

Conventions (section 0 of the memo):
  w        = log2 N, the incompressible width charged per block (w' = log2 phi(N) = w - 2e-6)
  record   = w + 8 stored bits (5 flag bits a1, a2, h and 3 padding bits; not charged)
  payload  = w - 16 bits per block; B = ceil(70e9 * 8 / (w - 16)) blocks
  S        = (1 - eps_c) * (w + 8) * B with eps_c = eps - tau (tau = tiering allowance)
  T        = total online budget in modular squarings for the whole audit (one M1 query = 2 squarings,
             charged as 1: conservative by one bit)
  L_M1     = log2 T + log2 e             proved in M1 (independent per-block oracles); equals Conjecture B1' for M2
  L_M2     = log2 T + log2 g*            proved in M2/M3 (shared squaring oracle(s), other-hits pay an identity)
  L_att    = log2(T / k)                 truncation attack with the total budget split over the k challenged blocks
  g*       = least g with  g (w - L(g)) >= S + log2 C(B, g) + lambda' + k log2 B + 2.5
  audit    = sequential reveal, pass probability <= (g*/B)^k + 2^-lambda'
"""
import math
import sys

LOG2E = math.log2(math.e)
LAMBDA = 64
MODEL_BYTES = 70e9
PAD_BITS = 8          # 5 flag bits + 3 padding bits per record
PAYLOAD_SLACK = 16    # payload is w - 16 bits
T_LIST = (20, 24, 28, 34)
W_LIST = (2048, 3072)
EPS_LIST = ((0.05, "0.95"), (1 / 19, "18/19"))
TAU_LIST = (0.0, 0.025)


def log2binom(n, k):
    if k <= 0 or k >= n:
        return 0.0
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)) / math.log(2)


def blocks(w):
    return math.ceil(MODEL_BYTES * 8 / (w - PAYLOAD_SLACK))


def loss(model, log2T, g, k):
    if model == "M1":
        return log2T + LOG2E
    if model == "M2":
        return log2T + math.log2(max(g, 2.0))
    if model == "att":
        return log2T - math.log2(k)
    raise ValueError(model)


def gstar(w, B, S, log2T, model, k, extra=0.0):
    """least g with g (w - L(g) - extra) >= S + log2 C(B,g) + lambda' + k log2 B + 2.5 (fixed point)."""
    g = 0.9 * B
    for _ in range(200):
        L = loss(model, log2T, g, k) + extra
        if L >= w:
            return float("inf")
        rhs = S + log2binom(B, min(g, B - 1)) + LAMBDA + k * math.log2(B) + 2.5
        g_new = rhs / (w - L)
        if abs(g_new - g) < 1e-9 * B:
            return g_new
        g = g_new
    return g


def k_for(p, beta, extra=0.0):
    """least k with p^k + extra <= beta (None if p >= 1 or impossible)."""
    if p >= 1 or beta <= extra:
        return None
    k = max(1, math.ceil(math.log(beta - extra) / math.log(p)))
    while p ** k + extra > beta:
        k += 1
    return k


def attack_p(w, S, B, log2T, k):
    """truncation attack: drop a fraction of blocks, store the rest with t = log2(T/k) bits removed."""
    t = log2T - math.log2(k)
    return (S / B) / (w - t)


def solve_seq(w, B, S, log2T, model, beta):
    """iterate k (it enters the union bound and, for the attack, the loss)."""
    k = 300
    for _ in range(50):
        if model == "att":
            p = attack_p(w, S, B, log2T, k)
            L = loss("att", log2T, None, k)
        else:
            g = gstar(w, B, S, log2T, model, k)
            p = g / B
            L = loss(model, log2T, g, k)
        k_new = k_for(p, beta, extra=2.0 ** -LAMBDA)
        if k_new is None:
            return {"L": L, "p": p, "u": 1 - p, "k": None}
        if k_new == k:
            break
        k = k_new
    return {"L": L, "p": p, "u": 1 - p, "k": k}


def solve_sim(w, B, S, log2T, model, beta):
    """simultaneous reveal: L_joint = L + log2 R, bound (g*/B)^k + k eta + 2k 2^-lambda'; optimise eta."""
    best = None
    for e in range(6, 60):
        eta = 2.0 ** -e
        R = math.ceil((LAMBDA + math.log2(B)) * math.log(2) / eta)
        k = 300
        ok = True
        for _ in range(50):
            g = gstar(w, B, S, log2T, model, k, extra=math.log2(R))
            p = g / B
            k_new = k_for(p, beta, extra=k * eta + 2 * k * 2.0 ** -LAMBDA)
            if k_new is None:
                ok = False
                break
            if k_new == k:
                break
            k = k_new
        if not ok:
            continue
        if best is None or k < best["k"]:
            best = {"k": k, "log2eta": -e, "log2R": math.log2(R), "L": loss(model, log2T, g, k) + math.log2(R),
                    "p": p, "u": 1 - p}
    return best


def fmt_k(k):
    return "-" if k is None else str(k)


def main():
    show_all = "--all" in sys.argv
    print("Blocks and budgets")
    for w in W_LIST:
        B = blocks(w)
        C_bits = B * (w + PAD_BITS)
        print(f"  w={w}: B={B:,} (2^{math.log2(B):.2f}), |C|={C_bits/8/1e9:.2f} GB, "
              f"padding gift = {PAD_BITS}(1-eps) bits/block")
        for eps, tag in EPS_LIST:
            for tau in TAU_LIST:
                eps_c = eps - tau
                budget = eps_c * w - PAD_BITS * (1 - eps_c)
                print(f"    S={tag}|C|, tau={tau}: eps_c={eps_c:.4f}, loss budget (u=0 at L=) {budget:.1f} bits")
    print()
    hdr = (f"{'w':>5} {'S/|C|':>6} {'tau':>5} {'eps_c':>6} {'log2T':>5} | "
           f"{'L_M2':>6} {'u_M2':>7} {'k6_M2':>6} {'k2_M2':>6} | "
           f"{'L_M1':>6} {'u_M1':>7} {'k6_M1':>6} {'k2_M1':>6} | "
           f"{'L_att':>6} {'u_att':>7} {'k6_att':>6}")
    print("Sequential reveal (Theorem 1). M2 = proved, shared oracle(s); M1 = proved, independent oracles "
          "= Conjecture B1' for M2; att = truncation attack floor.")
    print(hdr)
    print("-" * len(hdr))
    for w in W_LIST:
        B = blocks(w)
        for eps, tag in EPS_LIST:
            if tag == "18/19" and not show_all:
                continue
            for tau in TAU_LIST:
                eps_c = eps - tau
                S = (1 - eps_c) * (w + PAD_BITS) * B
                for log2T in T_LIST:
                    r2 = solve_seq(w, B, S, log2T, "M2", 1e-6)
                    r2b = solve_seq(w, B, S, log2T, "M2", 1e-2)
                    r1 = solve_seq(w, B, S, log2T, "M1", 1e-6)
                    r1b = solve_seq(w, B, S, log2T, "M1", 1e-2)
                    ra = solve_seq(w, B, S, log2T, "att", 1e-6)
                    print(f"{w:>5} {tag:>6} {tau:>5} {eps_c:>6.4f} {log2T:>5} | "
                          f"{r2['L']:>6.1f} {r2['u']:>7.4f} {fmt_k(r2['k']):>6} {fmt_k(r2b['k']):>6} | "
                          f"{r1['L']:>6.1f} {r1['u']:>7.4f} {fmt_k(r1['k']):>6} {fmt_k(r1b['k']):>6} | "
                          f"{ra['L']:>6.1f} {ra['u']:>7.4f} {fmt_k(ra['k']):>6}")
            print()
    if show_all:
        print("Simultaneous reveal (Theorem 2), beta = 1e-6 and 1e-2, eps = 0.05, tau = 0")
        print(f"{'w':>5} {'log2T':>5} {'model':>5} | {'beta':>5} {'log2eta':>7} {'log2R':>5} {'L_joint':>7} {'u':>7} {'k':>6}")
        for w in W_LIST:
            B = blocks(w)
            S = 0.95 * (w + PAD_BITS) * B
            for log2T in (20, 34):
                for model in ("M2", "M1"):
                    for beta in (1e-6, 1e-2):
                        b = solve_sim(w, B, S, log2T, model, beta)
                        if b is None:
                            print(f"{w:>5} {log2T:>5} {model:>5} | {beta:>5.0e}  vacuous")
                        else:
                            print(f"{w:>5} {log2T:>5} {model:>5} | {beta:>5.0e} {b['log2eta']:>7} {b['log2R']:>5.1f} "
                                  f"{b['L']:>7.1f} {b['u']:>7.4f} {b['k']:>6}")
        print()
        print("Padding fix (records packed, 0 uncharged bits per block), eps = 0.05, tau = 0.025, w = 2048, M2 and M1")
        w = 2048
        B = blocks(w)
        S = (1 - 0.025) * w * B
        for log2T in T_LIST:
            r2 = solve_seq(w, B, S, log2T, "M2", 1e-6)
            r1 = solve_seq(w, B, S, log2T, "M1", 1e-6)
            print(f"  log2T={log2T}: M2 u={r2['u']:.4f} k6={fmt_k(r2['k'])}; M1 u={r1['u']:.4f} k6={fmt_k(r1['k'])}")


if __name__ == "__main__":
    main()
