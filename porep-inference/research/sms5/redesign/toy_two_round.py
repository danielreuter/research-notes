#!/usr/bin/env python3
"""Toy checks for research/sms5/redesign/redesign.md (design (a): rho_1 -> E -> rho_2).

Rabin-Williams rounds over a toy Williams modulus N = p q (p = 3 mod 8, q = 7 mod 8), E a lazily
sampled random permutation of [0, N).  Chain per block:  y -> (a1, r) = RWInv(y);  v = E^{-1}(r);
(a2, c) = RWInv(v).  Decode: v = a2 c^2, r = E(v), y = a1 r^2.

Checks:
  0. store-the-trapdoor adversary: (p, q) once, every block recomputed with one E^{-1} query;
  1. two-round Coppersmith: top halves of r and of c recover c with one E^{-1} query (storage = w);
  2. an r with a single wrong bit gives a useless E^{-1} output (E enforces exact presentation);
  3. guess-and-Coppersmith: dropping t further bits per root costs 2^t Coppersmith runs per root
     (saving 2t bits at 2 * 2^t runs, against t bits at 2^t evaluations for truncation).

Pure Python (exact-rational LLL) + sympy for primes, Jacobi symbols and polynomial roots.
"""
import random, sys, time
from fractions import Fraction
from sympy import randprime, Poly, symbols, jacobi_symbol

random.seed(20260921)
X = symbols('x')


def lll(B, delta=Fraction(3, 4)):
    """Exact-rational LLL on a list of integer row vectors (small dimensions only)."""
    B = [list(map(int, r)) for r in B]
    n = len(B)

    def dot(u, v):
        return sum(a * b for a, b in zip(u, v))

    def gram_schmidt():
        Bs, mu = [], [[Fraction(0)] * n for _ in range(n)]
        for i in range(n):
            v = [Fraction(x) for x in B[i]]
            for j in range(i):
                mu[i][j] = Fraction(dot(B[i], Bs[j])) / dot(Bs[j], Bs[j])
                v = [a - mu[i][j] * b for a, b in zip(v, Bs[j])]
            Bs.append(v)
        return Bs, mu

    k = 1
    Bs, mu = gram_schmidt()
    while k < n:
        for j in range(k - 1, -1, -1):
            qj = round(mu[k][j])
            if qj:
                B[k] = [a - qj * b for a, b in zip(B[k], B[j])]
                for i in range(j):
                    mu[k][i] -= qj * mu[j][i]
                mu[k][j] -= qj
        if dot(Bs[k], Bs[k]) >= (delta - mu[k][k - 1] ** 2) * dot(Bs[k - 1], Bs[k - 1]):
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            Bs, mu = gram_schmidt()
            k = max(k - 1, 1)
    return B


# ---------------------------------------------------------------- Williams modulus and RW rounds
def williams_modulus(bits):
    half = bits // 2
    while True:
        p = randprime(2 ** (half - 1), 2 ** half)
        if p % 8 == 3:
            break
    while True:
        q = randprime(2 ** (half - 1), 2 ** half)
        if q % 8 == 7:
            break
    return p, q, p * q


def sqrt_mod_prime_3mod4(a, p):
    return pow(a, (p + 1) // 4, p)


def crt(a, p, b, q):
    N = p * q
    return (a * q * pow(q, -1, p) + b * p * pow(p, -1, q)) % N


def rw_inv(y, p, q):
    """Canonical Rabin-Williams root: (a, r) with a in {1,-1,2,-2}, y = a r^2 mod N, jacobi(r,N)=1, r<N/2."""
    N = p * q
    for a in (1, -1, 2, -2):
        u = (y * pow(a % N, -1, N)) % N
        if pow(u, (p - 1) // 2, p) == 1 and pow(u, (q - 1) // 2, q) == 1:
            rp = sqrt_mod_prime_3mod4(u % p, p)
            rq = sqrt_mod_prime_3mod4(u % q, q)
            roots = [crt(rp, p, rq, q), crt(rp, p, q - rq, q), crt(p - rp, p, rq, q), crt(p - rp, p, q - rq, q)]
            cands = [r for r in roots if jacobi_symbol(r, N) == 1 and r < N // 2]
            assert len(cands) == 1
            return a, cands[0]
    raise ValueError("not a unit or bad modulus")


def rw_fwd(a, r, N):
    return (a * r * r) % N


class RandomPermutation:
    """Lazily sampled random permutation of [0, N) with forward and inverse oracles and a query counter."""

    def __init__(self, N):
        self.N, self.fwd, self.inv, self.queries = N, {}, {}, 0

    def E(self, x):
        self.queries += 1
        if x not in self.fwd:
            while True:
                y = random.randrange(self.N)
                if y not in self.inv:
                    break
            self.fwd[x], self.inv[y] = y, x
        return self.fwd[x]

    def Einv(self, y):
        self.queries += 1
        if y not in self.inv:
            while True:
                x = random.randrange(self.N)
                if x not in self.fwd:
                    break
            self.fwd[x], self.inv[y] = y, x
        return self.inv[y]


# ---------------------------------------------------------------- Coppersmith / Howgrave-Graham, degree 2
def coppersmith_low_bits(a_hi, k, u, N, m=3, t=2):
    """Find x in [0, 2^k) with (a_hi 2^k + x)^2 = u mod N, if it exists, via a (2m + t)-dim HG lattice."""
    Xb = 1 << k
    f = Poly((a_hi * Xb + X) ** 2 - u, X)
    polys = []
    for i in range(m):
        for j in range(2):
            polys.append(Poly(X ** j, X) * Poly(N ** (m - i), X) * f ** i)
    for i in range(t):
        polys.append(Poly(X ** i, X) * f ** m)
    dim = len(polys)
    rows = []
    for g in polys:
        coeffs = g.all_coeffs()[::-1]  # low degree first
        row = [int(coeffs[d]) * Xb ** d if d < len(coeffs) else 0 for d in range(dim)]
        rows.append(row)
    Mred = lll(rows)
    for ridx in range(dim):
        vec = Mred[ridx]
        if all(v % (Xb ** d) == 0 for d, v in enumerate(vec)):
            g = Poly(sum((v // (Xb ** d)) * X ** d for d, v in enumerate(vec)), X)
            if g.is_zero:
                continue
            for root in g.ground_roots():          # exact rational roots by factorisation over Z
                if root.is_Integer:
                    cand = int(root)
                    if 0 <= cand < Xb and pow(a_hi * Xb + cand, 2, N) == u % N:
                        return cand
    return None


def recover_root_from_top(r_top, k, u, N, m=3, t=2):
    x = coppersmith_low_bits(r_top, k, u, N, m, t)
    return None if x is None else (r_top << k) + x


# ---------------------------------------------------------------- experiments
def main():
    bits = int(sys.argv[1]) if len(sys.argv) > 1 else 128
    p, q, N = williams_modulus(bits)
    w = N.bit_length()
    E = RandomPermutation(N)
    print(f"N = {N} ({w} bits), p = 3 mod 8, q = 7 mod 8")

    def encode(y):
        a1, r = rw_inv(y, p, q)
        v = E.Einv(r)
        while v % p == 0 or v % q == 0:  # negligible; keep the toy total
            v = E.Einv(r)
        a2, c = rw_inv(v, p, q)
        return (a1, r, v, a2, c)

    def decode(a1, a2, c):
        v = rw_fwd(a2, c, N)
        r = E.E(v)
        return rw_fwd(a1, r, N)

    # --- 0. store-the-trapdoor adversary
    y = random.randrange(2, N)
    a1, r, v, a2, c = encode(y)
    assert decode(a1, a2, c) == y
    q0 = E.queries
    a1_, r_ = rw_inv(y, p, q)          # trapdoor recomputes r from the public target
    v_ = E.Einv(r_)                    # one inverse query
    a2_, c_ = rw_inv(v_, p, q)         # trapdoor recomputes c
    print(f"[0] trapdoor adversary: stores (p,q) = {p.bit_length() + q.bit_length()} bits once, "
          f"recomputed c exactly = {c_ == c} with {E.queries - q0} oracle query. "
          f"No information-theoretic theorem can exclude this: the encoder's secret is short.")

    # --- calibrate the toy Coppersmith bound (fraction of a root recoverable from its square)
    m, t = 2, 2
    best_k = None
    for frac in (0.30, 0.34, 0.38, 0.41, 0.44):
        k = int(frac * w)
        ok = 0
        for _ in range(4):
            yy = random.randrange(2, N)
            aa, rr = rw_inv(yy, p, q)
            u = (yy * pow(aa % N, -1, N)) % N
            got = recover_root_from_top(rr >> k, k, u, N, m, t)
            ok += (got == rr)
        print(f"    Coppersmith (dim {2*m+t}) with k = {k} low bits unknown ({100*k/w:.0f}% of w): {ok}/4")
        if ok == 4:
            best_k = k
    k = best_k
    print(f"    using k = {k} ({100*k/w:.0f}% of w; the asymptotic bound for a monic quadratic is 50%)")

    # --- 1. two-round Coppersmith attack: store top (w-k) bits of r and of c
    trials, ok, tot_q = 8, 0, 0
    for _ in range(trials):
        y = random.randrange(2, N)
        a1, r, v, a2, c = encode(y)
        stored_r, stored_c = r >> k, c >> k                       # 2 (w - k) bits + 4 class bits
        q0 = E.queries
        u1 = (y * pow(a1 % N, -1, N)) % N
        r_hat = recover_root_from_top(stored_r, k, u1, N, m, t)   # zero queries
        v_hat = E.Einv(r_hat)                                     # one inverse query (known input!)
        u2 = (v_hat * pow(a2 % N, -1, N)) % N
        c_hat = recover_root_from_top(stored_c, k, u2, N, m, t)   # zero queries
        tot_q += E.queries - q0
        ok += (c_hat == c)
    print(f"[1] two-round Coppersmith: {ok}/{trials} blocks recovered, {tot_q/trials:.0f} oracle query per block, "
          f"storage 2(w-k) = {2*(w-k)} bits = {2*(w-k)/w:.2f} w  (>= w: nothing saved; -> w exactly as k -> w/2)")

    # --- 2. exactness: one wrong bit of r makes E^{-1} useless
    y = random.randrange(2, N)
    a1, r, v, a2, c = encode(y)
    r_bad = r ^ 1
    v_bad = E.Einv(r_bad)
    u2 = (v_bad * pow(a2 % N, -1, N)) % N
    c_hat = recover_root_from_top(c >> k, k, u2, N, m, t)
    print(f"[2] r with one flipped bit: E^-1 returns an unrelated v; Coppersmith on it with the true top bits of c "
          f"-> {c_hat} (None = failure). E must be presented the exact intermediate.")

    # --- 3. guess-and-Coppersmith: drop t_g more bits per root, 2^t_g Coppersmith runs per root
    t_g = 2
    y = random.randrange(2, N)
    a1, r, v, a2, c = encode(y)
    runs = 0
    r_hat = None
    for g in range(1 << t_g):
        runs += 1
        cand_top = ((r >> (k + t_g)) << t_g) | g
        u1 = (y * pow(a1 % N, -1, N)) % N
        got = recover_root_from_top(cand_top, k, u1, N, m, t)
        if got is not None and rw_fwd(a1, got, N) == y:
            r_hat = got
            break
    v_hat = E.Einv(r_hat)
    c_hat = None
    for g in range(1 << t_g):
        runs += 1
        cand_top = ((c >> (k + t_g)) << t_g) | g
        u2 = (v_hat * pow(a2 % N, -1, N)) % N
        got = recover_root_from_top(cand_top, k, u2, N, m, t)
        if got is not None and rw_fwd(a2, got, N) == v_hat:
            c_hat = got
            break
    print(f"[3] guess-and-Coppersmith with t_g = {t_g}: recovered = {c_hat == c}, {runs} Coppersmith runs "
          f"(<= 2 * 2^t_g = {2 << t_g}), storage 2(w-k-t_g) = {2*(w-k-t_g)} bits: saves 2 t_g bits "
          f"for 2^(t_g+1) runs, i.e. ~2 log2(T) per block against log2(T) for truncation.")


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"({time.time()-t0:.1f} s)")
