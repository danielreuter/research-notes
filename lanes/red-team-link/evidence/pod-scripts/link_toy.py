#!/usr/bin/env python3
"""red-team-link: toy harness for Link L (Project store docs/flock-link-protocol.md).

Idealised sub-proofs, real link arithmetic:
  * binary side: the verifier learns y^k and accepts iff y^k == zhat(r^k), computed from the committed z
    (an ideal PCS; variant E models the claim reduction instead);
  * prime side: constraints (i) booleanity, (ii) u range, (iii) the parity identity mod p are checked directly
    on the committed (b, u) (an ideal P_F).
Each scenario runs the spec verifier and one flawed variant and prints ACCEPT / REJECT. Pure Python, no deps.
"""
import json
import random
import sys

BABYBEAR = 2**31 - 2**27 + 1


class GF2n:
    def __init__(self, n, poly):
        self.n, self.poly, self.size = n, poly, 1 << n

    def mul(self, a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if (a >> self.n) & 1:
                a ^= self.poly
        return r

    def rand(self, rng):
        return rng.randrange(self.size)


K128 = GF2n(128, (1 << 128) | 0x87)  # x^128 + x^7 + x^2 + x + 1
K8 = GF2n(8, 0x11B)                  # toy field for rate measurements


def eq_table(K, r):
    """eq(r, i) for all i in {0,1}^m; coordinate k of r is bit k of i."""
    t = [1]
    for rk in r:
        t = [K.mul(e, 1 ^ rk) for e in t] + [K.mul(e, rk) for e in t]
    return t


def mle(eqt, bits):
    y = 0
    for i, v in enumerate(bits):
        if v:
            y ^= eqt[i]
    return y


def sigmas(K, eqt, b, lam):
    """sigma[t] = sum_c b_c * bit_t(eq(r, lam[c])) as an integer (b_c taken as given integers)."""
    s = [0] * K.n
    for c, v in enumerate(b):
        if v:
            e = eqt[lam[c]]
            t = 0
            while e:
                if e & 1:
                    s[t] += v
                e >>= 1
                t += 1
    return s


def honest_u(K, eqs, b, lam, ys):
    """u[k][t] = (sigma - bit_t(y)) / 2 over the integers, or None if a parity mismatches."""
    out = []
    for eqt, y in zip(eqs, ys):
        s = sigmas(K, eqt, b, lam)
        row = []
        for t in range(K.n):
            d = s[t] - ((y >> t) & 1)
            if d % 2:
                return None
            row.append(d // 2)
        out.append(row)
    return out


def prime_accepts(K, p, eqs, b, u, lam, ys, w, check_bool=True, check_range=True):
    if check_bool and any(v % p not in (0, 1) for v in b):
        return False
    for k, (eqt, y) in enumerate(zip(eqs, ys)):
        s = sigmas(K, eqt, [v % p for v in b], lam)
        for t in range(K.n):
            ukt = u[k][t]
            if check_range and not (0 <= ukt < 2**w):
                return False
            if (s[t] - 2 * ukt - ((y >> t) & 1)) % p:
                return False
    return True


def binary_accepts(eqs, z, ys):
    return all(mle(eqt, z) == y for eqt, y in zip(eqs, ys))


def admissible(p, n_cells, w, lam, spec=True):
    if not spec:
        return True
    return n_cells <= p - 1 and 2 ** (w + 1) <= p - 1 and len(set(lam)) == len(lam)


def w_of(n):
    return (n // 2 + 1 - 1).bit_length() if n // 2 + 1 > 1 else 1


def verdict(x):
    return "ACCEPT" if x else "REJECT"


def main(seed=20260925):
    rng = random.Random(seed)
    K, p = K128, BABYBEAR
    m = 12
    N = 1 << m
    w = w_of(N)
    lam = list(range(N))
    res = {}

    def points(npts=2):
        rs = [[K.rand(rng) for _ in range(m)] for _ in range(npts)]
        return [eq_table(K, r) for r in rs]

    z = [rng.randrange(2) for _ in range(N)]
    eqs = points()

    # A. honest
    ys = [mle(e, z) for e in eqs]
    u = honest_u(K, eqs, z, lam, ys)
    res["A_honest"] = verdict(admissible(p, N, w, lam) and binary_accepts(eqs, z, ys)
                              and prime_accepts(K, p, eqs, z, u, lam, ys, w))

    # B. b != z, the prover tries both consistent choices of y
    i0 = rng.randrange(N)
    b = list(z)
    b[i0] ^= 1
    y_z = [mle(e, z) for e in eqs]
    y_b = [mle(e, b) for e in eqs]
    u_b = honest_u(K, eqs, b, lam, y_b)
    res["B_diff_y_from_z"] = verdict(binary_accepts(eqs, z, y_z) and honest_u(K, eqs, b, lam, y_z) is not None)
    res["B_diff_y_from_b"] = verdict(binary_accepts(eqs, z, y_b) and prime_accepts(K, p, eqs, b, u_b, lam, y_b, w))

    # C. A6: u not range-checked: u = (sigma - bit) / 2 mod p exists for any parity
    inv2 = pow(2, p - 2, p)
    u_c = []
    for eqt, y in zip(eqs, y_z):
        s = sigmas(K, eqt, b, lam)
        u_c.append([((s[t] - ((y >> t) & 1)) * inv2) % p for t in range(K.n)])
    res["C_unranged_u_spec"] = verdict(binary_accepts(eqs, z, y_z) and prime_accepts(K, p, eqs, b, u_c, lam, y_z, w))
    res["C_unranged_u_flawed"] = verdict(binary_accepts(eqs, z, y_z)
                                        and prime_accepts(K, p, eqs, b, u_c, lam, y_z, w, check_range=False))

    # D. A4: non-boolean cell b = z + 2 keeps every parity; the recomposed word moves by 2^(j+1)
    b_d = list(z)
    b_d[i0] = z[i0] + 2
    u_d = honest_u(K, eqs, b_d, lam, y_z)
    ok_range = u_d is not None and all(0 <= x < 2**w for row in u_d for x in row)
    res["D_nonboolean_spec"] = verdict(u_d is not None and prime_accepts(K, p, eqs, b_d, u_d, lam, y_z, w))
    res["D_nonboolean_flawed"] = verdict(ok_range and binary_accepts(eqs, z, y_z)
                                        and prime_accepts(K, p, eqs, b_d, u_d, lam, y_z, w, check_bool=False))
    j0 = i0 % 16
    word_hashed = sum(z[(i0 - j0) + j] << j for j in range(16))
    word_used = sum(b_d[(i0 - j0) + j] << j for j in range(16))
    res["D_word_hashed_vs_used"] = [word_hashed, word_used]

    # F. Lambda_F not injective: two prime cells on one position where z = 0, both b = 1
    zeros = [i for i in range(N) if z[i] == 0]
    i1 = zeros[0]
    lam_f = lam + [i1]
    b_f = list(z) + [1]
    b_f[i1] = 1
    u_f = honest_u(K, eqs, b_f, lam_f, y_z)
    res["F_noninjective_spec"] = verdict(admissible(p, len(b_f), w, lam_f) and u_f is not None)
    res["F_noninjective_flawed"] = verdict(u_f is not None and binary_accepts(eqs, z, y_z)
                                          and prime_accepts(K, p, eqs, b_f, u_f, lam_f, y_z, w))

    # G. R1-style remap: two 64-bit "VU rows"; the relation consumes row B at VU A's cells and vice versa.
    #    The verifier either derives Lambda_F from the public layout (spec) or takes the prover's (flawed).
    L = 64
    b_g = z[L:2 * L] + z[0:L] + z[2 * L:]
    lam_prover = list(range(L, 2 * L)) + list(range(0, L)) + list(range(2 * L, N))
    u_g_spec = honest_u(K, eqs, b_g, lam, y_z)
    u_g = honest_u(K, eqs, b_g, lam_prover, y_z)
    res["G_remap_spec"] = verdict(u_g_spec is not None and prime_accepts(K, p, eqs, b_g, u_g_spec, lam, y_z, w))
    res["G_remap_flawed"] = verdict(u_g is not None and prime_accepts(K, p, eqs, b_g, u_g, lam_prover, y_z, w))

    # H. u range wider than admissible (e.g. two 16-bit limbs, w = 32, over BabyBear): 2^(w+1) > p - 1 lets
    #    bit' + 2u wrap. Sparse data so sigma is small, one bit flipped between the two copies.
    z_h = [0] * N
    for i in rng.sample(range(N), 12):
        z_h[i] = 1
    b_h = list(z_h)
    b_h[next(i for i in range(N) if z_h[i] == 0)] = 1
    y_h = [mle(e, z_h) for e in eqs]

    def forge_u(wide):
        out = []
        for eqt, y in zip(eqs, y_h):
            s = sigmas(K, eqt, b_h, lam)
            row = []
            for t in range(K.n):
                d = s[t] - ((y >> t) & 1)
                if d % 2 == 0:
                    row.append(d // 2)
                elif (d + p) // 2 < 2**wide:
                    row.append((d + p) // 2)
                else:
                    return None
            out.append(row)
        return out

    u_h32 = forge_u(32)
    u_hw = forge_u(w)
    res["H_wrap_w32"] = verdict(u_h32 is not None and admissible(p, N, 32, lam, spec=False)
                                and binary_accepts(eqs, z_h, y_h) and prime_accepts(K, p, eqs, b_h, u_h32, lam, y_h, 32))
    res["H_wrap_w32_admissible"] = admissible(p, N, 32, lam)
    res["H_wrap_spec_w"] = verdict(u_hw is not None and prime_accepts(K, p, eqs, b_h, u_hw, lam, y_h, w))

    # I. sigma in the clear (no u, no second commitment; NON_ZK only): prime side proves sum C b = sigma mod p,
    #    verifier checks sigma mod 2 = bit_t(y). The spec reduces sigma canonically and requires sigma <= N.
    def sigma_accepts(bvec, sig, ys_, spec):
        for k, (eqt, y) in enumerate(zip(eqs, ys_)):
            s = sigmas(K, eqt, bvec, lam)
            for t in range(K.n):
                st = sig[k][t]
                if spec and not (0 <= st <= N):
                    return False
                if (s[t] - st) % p or st % 2 != ((y >> t) & 1):
                    return False
        return True

    sig_h = [sigmas(K, e, z, lam) for e in eqs]
    res["I_sigma_honest"] = verdict(sigma_accepts(z, sig_h, y_z, True))
    sig_b = [sigmas(K, e, b, lam) for e in eqs]
    sig_forged = [[s + p if (s % 2) != ((y >> t) & 1) else s for t, s in enumerate(row)]
                  for row, y in zip(sig_b, y_z)]
    res["I_sigma_forged_spec"] = verdict(sigma_accepts(b, sig_forged, y_z, True))
    res["I_sigma_forged_flawed"] = verdict(sigma_accepts(b, sig_forged, y_z, False))

    # E. two link claims: independent verification vs one random combination (batched reduction), measured in
    #    GF(2^8) with m = 8 against the Schwartz-Zippel-extremal difference delta = e_(1...1), deltahat(r) = prod r_k.
    trials = 200000
    Kt, mt = K8, 8
    rng_e = random.Random(seed + 1)

    def dhat(r):
        v = 1
        for rk in r:
            v = Kt.mul(v, rk)
        return v

    one = both = batched = 0
    for _ in range(trials):
        d1 = dhat([Kt.rand(rng_e) for _ in range(mt)])
        d2 = dhat([Kt.rand(rng_e) for _ in range(mt)])
        l1, l2 = Kt.rand(rng_e), Kt.rand(rng_e)
        one += d1 == 0
        both += d1 == 0 and d2 == 0
        batched += (Kt.mul(l1, d1) ^ Kt.mul(l2, d2)) == 0
    res["E_rates_GF256_m8"] = {
        "trials": trials,
        "one_point_miss": one / trials,
        "two_points_independent_miss": both / trials,
        "two_points_batched_miss": batched / trials,
        "sz_one": 1 - (1 - 1 / 256) ** mt,
        "sz_two": (1 - (1 - 1 / 256) ** mt) ** 2,
    }

    json.dump(res, sys.stdout, indent=1)
    print()
    expect = {
        "A_honest": "ACCEPT", "B_diff_y_from_z": "REJECT", "B_diff_y_from_b": "REJECT",
        "C_unranged_u_spec": "REJECT", "C_unranged_u_flawed": "ACCEPT",
        "D_nonboolean_spec": "REJECT", "D_nonboolean_flawed": "ACCEPT",
        "F_noninjective_spec": "REJECT", "F_noninjective_flawed": "ACCEPT",
        "G_remap_spec": "REJECT", "G_remap_flawed": "ACCEPT",
        "H_wrap_w32": "ACCEPT", "H_wrap_spec_w": "REJECT",
        "I_sigma_honest": "ACCEPT", "I_sigma_forged_spec": "REJECT", "I_sigma_forged_flawed": "ACCEPT",
    }
    bad = {k: (res[k], v) for k, v in expect.items() if res[k] != v}
    print("EXPECTATIONS", "OK" if not bad else f"MISMATCH {bad}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
