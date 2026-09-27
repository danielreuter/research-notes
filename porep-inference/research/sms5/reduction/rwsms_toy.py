#!/usr/bin/env python3
"""
Toy-scale checks for research/sms5/reduction/reduction.md (RW-SMS v1).

Pure Python (sympy is used only to find integer roots of the degree-4 polynomials
in experiment B; a brute-force fallback is used if sympy is missing).

Experiments
  0. Sanity: Williams modulus, selector classes, RWInv bijection, encode/decode,
     fibre of a target has exactly 16 records of which exactly ONE passes the
     public canonical check (uniqueness used by Theorem 2 of the memo).
  A. "Half-bits" attack: store the top bits of r AND the top bits of c, recover
     the low t_r bits of r from y (3-dim Coppersmith), then v, then the low t_c
     bits of c from v (3-dim Coppersmith). Works, but storage 2w - t_r - t_c > w.
  B. Mixing layer: with AFFINE mixing (v = r + K mod N) the low bits of c are a
     small root of a degree-4 univariate polynomial in c alone (y, K public) and
     are recovered with NO stored bits of r. With XOR mixing the same lattice
     yields nothing. (Basic Hastad lattice of dimension 5 => X < N^(1/10);
     asymptotically N^(1/4) with Coppersmith's multiplicity trick.)
  C. Linearising the XOR costs popcount(K) ~ w/2 unknown bits.
"""
import random, math, sys
from fractions import Fraction

try:
    import sympy
    HAVE_SYMPY = True
except Exception:
    HAVE_SYMPY = False

# ---------------------------------------------------------------- number theory
def is_probable_prime(n, k=32):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else:
            return False
    return True

def rand_prime(bits, residue, mod):
    while True:
        p = random.getrandbits(bits) | (1 << (bits - 1))
        p -= (p - residue) % mod
        if p.bit_length() == bits and is_probable_prime(p):
            return p

def jacobi(a, n):
    a %= n; result = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5): result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3: result = -result
        a %= n
    return result if n == 1 else 0

def williams_modulus(w):
    """N = pq with p = 3 mod 8, q = 7 mod 8 and N of exactly w bits."""
    while True:
        p = rand_prime(w // 2, 3, 8)
        q = rand_prime(w - w // 2, 7, 8)
        N = p * q
        if N.bit_length() == w and p != q:
            return N, p, q

class Trapdoor:
    def __init__(self, N, p, q):
        self.N, self.p, self.q = N, p, q
        self.A = [1, N - 1, 2, N - 2]          # selectors {1, -1, 2, -2}
    def is_qr(self, u):
        return pow(u, (self.p - 1) // 2, self.p) == 1 and pow(u, (self.q - 1) // 2, self.q) == 1
    def roots(self, u):
        """all four square roots of a QR u mod N (p, q = 3 mod 4)."""
        p, q, N = self.p, self.q, self.N
        rp = pow(u % p, (p + 1) // 4, p); rq = pow(u % q, (q + 1) // 4, q)
        out = []
        for sp in (rp, p - rp):
            for sq in (rq, q - rq):
                # CRT
                x = (sp * q * pow(q, -1, p) + sq * p * pow(p, -1, q)) % N
                out.append(x)
        return out
    def rwinv(self, y):
        """(a, r) with y = a r^2, r in J_N^+ (Jacobi +1, r <= (N-1)/2)."""
        N = self.N
        for a in self.A:
            u = y * pow(a, -1, N) % N
            if self.is_qr(u):
                for r in self.roots(u):
                    if r <= (N - 1) // 2 and jacobi(r, N) == 1:
                        return a, r
        raise ValueError("y not in Z_N^* or no class matched")

# ---------------------------------------------------------------- RW-SMS v1
def encode(td, m, t, K, w):
    N = td.N
    y = (m + t) % N
    a1, r = td.rwinv(y)
    z = r ^ K
    h = 1 if z >= N else 0
    v = z - h * N
    if math.gcd(v, N) != 1: return None
    a2, c = td.rwinv(v)
    return (c, a1, a2, h)

def decode(N, rec, t, K):
    c, a1, a2, h = rec
    v = a2 * c * c % N
    z = v + h * N
    r = z ^ K
    y = a1 * r * r % N
    return (y - t) % N

def canonical_check(N, w, rec, t, K, m):
    """Public (trapdoor-free) predicate: is rec THE honest record of m?"""
    c, a1, a2, h = rec
    A = (1, N - 1, 2, N - 2)
    if a1 not in A or a2 not in A or h not in (0, 1): return False
    if not (1 <= c <= (N - 1) // 2) or jacobi(c, N) != 1: return False
    v = a2 * c * c % N
    z = v + h * N
    if z >= (1 << w): return False
    r = z ^ K
    if not (1 <= r <= (N - 1) // 2) or jacobi(r, N) != 1: return False
    return (a1 * r * r - t) % N == m

def fibre(td, w, m, t, K):
    """All records (c, a1, a2, h) that decode to m (needs the trapdoor to list)."""
    N = td.N
    y = (m + t) % N
    out = []
    for a1 in td.A:
        u = y * pow(a1, -1, N) % N
        if not td.is_qr(u): continue
        for r in td.roots(u):
            z = r ^ K
            if z >= (1 << w): continue
            h = 1 if z >= N else 0
            v = z - h * N
            if math.gcd(v, N) != 1: continue
            for a2 in td.A:
                u2 = v * pow(a2, -1, N) % N
                if not td.is_qr(u2): continue
                for c in td.roots(u2):
                    rec = (c, a1, a2, h)
                    assert decode(N, rec, t, K) == m
                    out.append(rec)
    return out

# ---------------------------------------------------------------- LLL / Coppersmith
def lll(B, delta=Fraction(3, 4)):
    B = [list(map(int, row)) for row in B]
    n = len(B)
    def dot(u, v): return sum(a * b for a, b in zip(u, v))
    def gso():
        Bs, mu = [], [[Fraction(0)] * n for _ in range(n)]
        for i in range(n):
            v = [Fraction(x) for x in B[i]]
            for j in range(i):
                mu[i][j] = Fraction(dot(B[i], Bs[j])) / dot(Bs[j], Bs[j])
                v = [a - mu[i][j] * b for a, b in zip(v, Bs[j])]
            Bs.append(v)
        return Bs, mu
    k = 1
    while k < n:
        Bs, mu = gso()
        for j in range(k - 1, -1, -1):
            q = round(mu[k][j])
            if q:
                B[k] = [a - q * b for a, b in zip(B[k], B[j])]
                Bs, mu = gso()
        if dot(Bs[k], Bs[k]) >= (delta - mu[k][k - 1] ** 2) * dot(Bs[k - 1], Bs[k - 1]):
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            k = max(k - 1, 1)
    return B

def int_roots(coeffs, X):
    """Integer roots in [0, X) of sum coeffs[i] x^i (coeffs over Z)."""
    d = len(coeffs) - 1
    while d > 0 and coeffs[d] == 0: d -= 1
    coeffs = coeffs[:d + 1]
    if d <= 0: return []
    if d == 1:
        return [-coeffs[0] // coeffs[1]] if (-coeffs[0]) % coeffs[1] == 0 else []
    if d == 2:
        c2, c1, c0 = coeffs[2], coeffs[1], coeffs[0]
        D = c1 * c1 - 4 * c2 * c0
        if D < 0: return []
        s = math.isqrt(D)
        if s * s != D: return []
        return [num // (2 * c2) for num in (-c1 + s, -c1 - s) if num % (2 * c2) == 0]
    if HAVE_SYMPY:
        x = sympy.Symbol('x')
        poly = sympy.Poly(sum(sympy.Integer(c) * x ** i for i, c in enumerate(coeffs)), x)
        return [int(r) for r in poly.ground_roots() if r.is_integer]
    return [x0 for x0 in range(X) if sum(c * x0 ** i for i, c in enumerate(coeffs)) == 0]

def coppersmith_basic(f, N, X):
    """Hastad lattice for a monic f (list of coeffs, f[d] = 1) mod N, root |x0| < X.
    Dimension d + 1; succeeds roughly when X < N^(2/(d(d+1)))."""
    d = len(f) - 1
    rows = []
    for i in range(d):
        row = [0] * (d + 1); row[i] = N * X ** i; rows.append(row)
    rows.append([f[i] * X ** i for i in range(d + 1)])
    red = lll(rows)
    for v in red:
        if any(v[i] % X ** i for i in range(d + 1)): continue
        g = [v[i] // X ** i for i in range(d + 1)]
        for x0 in int_roots(g, X):
            if 0 <= x0 < X:
                yield x0

def monic_mod(f, N):
    inv = pow(f[-1] % N, -1, N)
    return [c * inv % N for c in f]

def polymul(a, b, N):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % N
    return out

def recover_low_bits_sqrt(a, target, hi, t, N):
    """x0 = low t bits of s where a*s^2 = target mod N and s = hi*2^t + x0 (3-dim lattice)."""
    X = 1 << t
    ainv = pow(a, -1, N)
    # (hi 2^t + x)^2 - target/a = x^2 + 2 hi 2^t x + (hi^2 2^{2t} - target/a)
    f = [((hi * X) ** 2 - target * ainv) % N, (2 * hi * X) % N, 1]
    for x0 in coppersmith_basic(f, N, X):
        if a * (hi * X + x0) ** 2 % N == target % N:
            return x0
    return None

# ---------------------------------------------------------------- experiments
def exp0(td, w, trials=200):
    N = td.N
    # selector classes are the four cosets of squares
    sig = set()
    for a in td.A:
        sig.add((pow(a, (td.p - 1) // 2, td.p) == 1, pow(a, (td.q - 1) // 2, td.q) == 1))
    assert len(sig) == 4, "selectors do not cover the four classes"
    ok = 0; fib_sizes = set(); canon_counts = set()
    for _ in range(trials):
        m = random.randrange(N); t = random.randrange(N); K = random.getrandbits(w)
        rec = encode(td, m, t, K, w)
        if rec is None: continue
        assert decode(N, rec, t, K) == m
        assert canonical_check(N, w, rec, t, K, m)
        F = fibre(td, w, m, t, K)
        fib_sizes.add(len(F))
        canon_counts.add(sum(canonical_check(N, w, R, t, K, m) for R in F))
        assert rec in F
        ok += 1
    print(f"[0] w={w}: {ok} blocks encode/decode/canonical OK; fibre sizes seen {sorted(fib_sizes)}; "
          f"canonical records per fibre {sorted(canon_counts)}")

def expA(td, w, t_r, t_c, trials=100):
    N = td.N; succ = 0; n = 0
    for _ in range(trials):
        m = random.randrange(N); t = random.randrange(N); K = random.getrandbits(w)
        rec = encode(td, m, t, K, w)
        if rec is None: continue
        n += 1
        c, a1, a2, h = rec
        y = (m + t) % N
        v = a2 * c * c % N; z = v + h * N; r = z ^ K
        # stored: r >> t_r, c >> t_c, a1, a2, h
        xr = recover_low_bits_sqrt(a1, y, r >> t_r, t_r, N)
        if xr is None or xr != r & ((1 << t_r) - 1): continue
        r_rec = (r >> t_r) << t_r | xr
        v_rec = (r_rec ^ K) - h * N
        xc = recover_low_bits_sqrt(a2, v_rec, c >> t_c, t_c, N)
        if xc is not None and xc == c & ((1 << t_c) - 1): succ += 1
    stored = 2 * w - t_r - t_c + 5
    print(f"[A] w={w}: drop t_r={t_r} bits of r and t_c={t_c} bits of c -> recovered {succ}/{n}; "
          f"storage {stored} bits = {stored / w:.2f} w (baseline: store c, {w + 4} bits)")

def encode_affine(td, m, t, K):
    N = td.N
    y = (m + t) % N
    a1, r = td.rwinv(y)
    v = (r + K) % N
    if math.gcd(v, N) != 1: return None
    a2, c = td.rwinv(v)
    return (c, a1, a2)

def expB(td, w, t_c, trials=100):
    """store only c >> t_c (plus a1, a2, h); recover the low t_c bits of c from y, K."""
    N = td.N; X = 1 << t_c
    succ_aff = 0; succ_xor = 0; n_aff = 0; n_xor = 0
    for _ in range(trials):
        m = random.randrange(N); t = random.randrange(N); K = random.randrange(N)
        y = (m + t) % N
        # affine mixing: y = a1 (a2 c^2 - K)^2
        rec = encode_affine(td, m, t, K)
        if rec is not None:
            n_aff += 1
            c, a1, a2 = rec
            hi = c >> t_c
            # polynomial in x: a1 * (a2 (hi X + x)^2 - K)^2 - y
            lin = [(hi * X) % N, 1]                       # hi X + x
            sq = polymul(lin, lin, N)                     # (hi X + x)^2
            inner = [(a2 * s) % N for s in sq]; inner[0] = (inner[0] - K) % N
            f = polymul(inner, inner, N); f = [(a1 * s) % N for s in f]; f[0] = (f[0] - y) % N
            f = monic_mod(f, N)
            for x0 in coppersmith_basic(f, N, X):
                if a1 * ((a2 * (hi * X + x0) ** 2 - K) % N) ** 2 % N == y:
                    succ_aff += 1; break
        # XOR mixing (the real scheme), same stored data, same lattice pretending z = r + K
        Kw = random.getrandbits(w)
        rec = encode(td, m, t, Kw, w)
        if rec is not None:
            n_xor += 1
            c, a1, a2, h = rec
            hi = c >> t_c
            # true relation: y = a1 (((a2 c^2 + hN) XOR K))^2 ; no polynomial in c.
            # try the affine surrogate with constant -K (and +K): both must fail.
            found = False
            for sgn in (1, -1):
                lin = [(hi * X) % N, 1]; sq = polymul(lin, lin, N)
                inner = [(a2 * s) % N for s in sq]; inner[0] = (inner[0] + sgn * (Kw % N)) % N
                f = polymul(inner, inner, N); f = [(a1 * s) % N for s in f]; f[0] = (f[0] - y) % N
                f = monic_mod(f, N)
                for x0 in coppersmith_basic(f, N, X):
                    if decode(N, (hi * X + x0, a1, a2, h), t, Kw) == m:
                        found = True
            succ_xor += found
    print(f"[B] w={w}: store c>>{t_c} only. affine mixing: low {t_c} bits of c recovered {succ_aff}/{n_aff} "
          f"(dim-5 lattice, bound N^(1/10) = {w / 10:.0f} bits; asymptotic N^(1/4) = {w / 4:.0f}). "
          f"XOR mixing, same lattice: {succ_xor}/{n_xor}.")

def expC(w, trials=1000):
    pops = [bin(random.getrandbits(w)).count('1') for _ in range(trials)]
    mu = sum(pops) / trials; sd = (sum((p - mu) ** 2 for p in pops) / trials) ** 0.5
    print(f"[C] w={w}: popcount(K) = {mu:.1f} +- {sd:.1f} unknown bits to linearise r XOR K (w/2 = {w / 2})")

if __name__ == "__main__":
    random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
    for w in (64, 96):
        N, p, q = williams_modulus(w); td = Trapdoor(N, p, q)
        exp0(td, w, trials=60)
    w = 128
    N, p, q = williams_modulus(w); td = Trapdoor(N, p, q)
    print(f"    N has {w} bits, p = {p % 8} mod 8, q = {q % 8} mod 8, (-1|N) = {jacobi(N - 1, N)}, (2|N) = {jacobi(2, N)}")
    for (t_r, t_c) in ((32, 32), (40, 40), (42, 42)):
        expA(td, w, t_r, t_c, trials=60)
    w = 160
    N, p, q = williams_modulus(w); td = Trapdoor(N, p, q)
    for t_c in (10, 14, 16):
        expB(td, w, t_c, trials=60)
    for w in (2048, 3072):
        expC(w)
