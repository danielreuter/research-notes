"""Desk cost model for computing M~_C(r) inside V[B]: (a) the in-circuit private fold, (b) holography over a committed Enc(C)."""
import math
from verity_flock.recursion.session import fast100

SHA = {"sha256": (22573, 64, 9, 32), "sha512": (57947, 128, 17, 64)}   # ANDs, block, pad bytes, digest
GF = 2187


def comp(algo, nbytes):
    ands, blk, pad, _ = SHA[algo]
    return math.ceil((nbytes + pad) / blk)


def ligerito_open(nbits, algo="sha512", salted=False):
    """In-circuit cost of verifying one Ligerito opening of a committed table of nbits (one rep): Merkle hashing,
    cap selection, row combinations. Salted: hm96 leaves at level 0 (+ salt digest and leaf: 4 compressions)."""
    nvars = max(15, math.ceil(math.log2(max(nbits, 1) / 128)))
    extra = max(0, nvars - 28)                    # beyond fast100's table: a longer level-0 path per extra variable
    s = fast100(min(nvars, 28) + 7)
    ands_c, _, _, dg = SHA[algo]
    tot = 0
    for i, L in enumerate(s.levels):
        lanes = 2 ** L.lanes
        leaf = comp(algo, 16 * lanes) + (4 if (salted and i == 0) else 0)
        nodes = 2 * (L.d - L.cap + (extra if i == 0 else 0))
        tot += L.q * ((leaf + nodes) * ands_c + (2 ** L.cap) * 8 * dg + lanes * GF)
    return tot


def waksman(n):
    lg = math.ceil(math.log2(n))
    return n * lg - 2 ** lg + 1


def fold_a(Z, R, reps=2, design="waksman"):
    """(a): the private fold for one wiring of Z entries over R rows; values for `reps` reps (128 bits each)."""
    w = math.ceil(math.log2(R + 1)) + 128 * reps + 1
    n = Z + R + 1
    if design == "benes-pow2":
        N = 2 ** math.ceil(math.log2(n))
        lk = (2 * int(math.log2(N)) - 1) * (N // 2) * w + N * w
        return 2 * lk + Z * reps * GF
    if design == "waksman":
        lk = waksman(n) * w + n * w
        return 2 * lk + Z * reps * GF
    # optimized: unsorted column side by Waksman, sorted row side by an odd-even merge over prefix sums, R products
    wp = math.ceil(math.log2(Z)) + 128 * reps + 2 * math.ceil(math.log2(R + 1)) + 1
    merge = (n // 2) * math.ceil(math.log2(n)) * wp + n * (wp + 2 * math.ceil(math.log2(Z)))
    return waksman(n) * w + n * w + merge + R * reps * GF


def binding_a(Z, R, algo="sha512"):
    """(a): V[B] rehashes the wiring's encoding against c (hm96 over Enc of one unit: Z entries of 2 log R + 1 bits)."""
    nbytes = Z * (2 * math.ceil(math.log2(R)) + 1) / 8
    return (comp(algo, nbytes) + 4) * SHA[algo][0]


def holo_b(n_units, Z, R, reps=2, k=1):
    """(b): one sumcheck of degree ~2 log R + 2 over log(n Z) variables, then one opening of c (salted, SHA-512)."""
    lr = math.ceil(math.log2(R))
    D = 2 * lr + 2
    rounds = math.ceil(math.log2(n_units * Z))
    alg = rounds * (D + 1) * 2 * GF + (D + 64) * GF
    nbits = n_units * Z * (2 * lr + 1)
    return reps * (alg + ligerito_open(nbits, salted=True)), reps * alg, reps * ligerito_open(nbits, salted=True)


def spark_b(n_units, Z, R, reps=2):
    """SPARK (Spartan) for comparison: opening of c (row, col, 4 counter columns) and of the per-run E commitments
    (2 x Z 128-bit values per rep), plus the grand products' sumcheck algebra."""
    lr = math.ceil(math.log2(R))
    nbits_c = n_units * Z * (2 * lr + 2 * math.ceil(math.log2(Z)))
    nbits_e = n_units * Z * 2 * 128
    lg = math.ceil(math.log2(n_units * Z))
    alg = 8 * (lg * (lg + 1) // 2) * 6 * GF
    return reps * (alg + ligerito_open(nbits_c, salted=True) + ligerito_open(nbits_e))


if __name__ == "__main__":
    print("check vs measured: inner Ligerito, m=23, SHA-256 (measured Merkle 0.171 G/rep):",
          "%.3g" % ligerito_open(2 ** 23, "sha256"))
    for Z, R, tag in ((157841, 2 ** 13, "RoPE as is"), (2 ** 18, 2 ** 13, "S: Z=2^18, R=2^13"), (2 ** 18, 2 ** 16, "S: Z=2^18, R=2^16"),
                      (2 ** 20, 2 ** 16, "S: Z=2^20, R=2^16")):
        print(f"\n{tag}")
        for d in ("benes-pow2", "waksman", "optimized"):
            print("  (a) fold %-10s %.3g   + binding %.3g" % (d, fold_a(Z, R, design=d), binding_a(Z, R)))
        for n in (1, 32, 1024):
            t, a, o = holo_b(n, Z, R)
            print("  (b) holography, n=%5d units: %.3g  (algebra %.3g, opening %.3g); SPARK %.3g" % (n, t, a, o, spark_b(n, Z, R)))
