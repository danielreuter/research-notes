"""Timing experiment (outside the repo): worst-case paths and sampler/opening costs."""
import math, random, sys, time, json, hashlib

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_nested as E
from verity.ir import Value, Array, Program, bind, composite
from verity.ir.query_ast import evaluate, nodes, members

V = E.V


# column-major consumer: batch of dots over axis 1 of W (Array<K, Array<N, V>>)
@composite("QLinearCols", 1, ["K", "N"], lambda S: ((("x", Array(S.K, V)), ("W", Array(S.K, Array(S.N, V)))), Array(S.N, V)))
def QLinearCols(B, S, x, W):
    return B.batch(bind(E.QDot, K=S.K), x, W, axes=(None, 1))


def col_major(K):
    P = Program(bind(QLinearCols, K=K, N=64))
    C = P.circuit
    rng = random.Random(3)
    first = P.input_gates
    idx = [rng.randrange(first, P.gates) for _ in range(50)]
    t0 = time.perf_counter()
    for i in idx:
        C.gate(i)
    return (time.perf_counter() - t0) / len(idx) * 1e6


def whole_entry(N):
    P = Program(bind(E.QLinear, K=4, N=N))
    F = evaluate(P, nodes(".", "@batch:QDot"))
    t0 = time.perf_counter()
    s = F.by_index(0)
    s.intervals()
    return (time.perf_counter() - t0) * 1e3


def float_gaps(N, p, n):
    """float64 inverse-CDF geometric gaps (the naive implementation)"""
    rng = random.Random(5)
    lq = math.log1p(-p)
    i, out = -1, []
    for _ in range(n):
        g = int(math.log(1.0 - rng.random()) / lq) + 1
        i += g
        if i >= N:
            break
        out.append(i)
    return out


def verify_depth(depth):
    from verity.commitments.merkle import CommitmentDomain, Commitment, Opening, verify_opening
    from verity.commitments.indexed import RangeIndexedDomain
    from verity.commitments.limits import VerificationLimits
    count = 1 << depth
    dom = CommitmentDomain(b"\x11" * 32, -1, RangeIndexedDomain(count))
    pos = random.Random(7).randrange(count)
    value = b"\x00" * 4
    leaf = dom.leaf(pos, pos, "u32", value)
    path, cur, cursor = [], leaf, pos
    rng = random.Random(8)
    for level in range(depth):
        sib = rng.randbytes(32)
        path.append(sib)
        pair = (cur, sib) if cursor % 2 == 0 else (sib, cur)
        cur = dom.node(level, cursor >> 1, *pair)
        cursor >>= 1
    c = Commitment(cur, count)
    o = Opening(pos, value, tuple(path))
    lim = VerificationLimits()
    t0 = time.perf_counter()
    for _ in range(200):
        ok = verify_opening(dom, c, o, "u32", lim)
    assert ok
    return (time.perf_counter() - t0) / 200 * 1e6


if __name__ == "__main__":
    out = {}
    out["col_major_gate_us"] = {K: round(col_major(K), 1) for K in (256, 2048, 16384)}
    out["whole_entry_by_index_ms"] = {N: round(whole_entry(N), 2) for N in (10_000, 100_000, 1_000_000)}
    N = 10**25
    p = 1e-19
    xs = float_gaps(N, p, 200_000)
    lows = {x % 4096 for x in xs}
    gaps = [b - a for a, b in zip(xs, xs[1:])]
    out["float_gap_sampler"] = {"N": "1e25", "p": p, "draws": len(xs), "distinct_residues_mod_4096": len(lows),
                                "gaps_divisible_by_4096": sum(1 for g in gaps if (g - 1) % 4096 == 0)}
    rng = random.Random(9)
    t0 = time.perf_counter()
    for _ in range(200_000):
        rng.randrange(N)
    out["exact_uniform_draw_us"] = round((time.perf_counter() - t0) / 200_000 * 1e6, 2)
    t0 = time.perf_counter()
    for _ in range(20_000):
        hashlib.sha256(b"x" * 64).digest()
    out["sha256_64B_us"] = round((time.perf_counter() - t0) / 20_000 * 1e6, 2)
    pop = list(range(2_000_000))
    t0 = time.perf_counter()
    random.Random(1).sample(pop, 1000)
    out["materialized_sample_2e6_ms"] = round((time.perf_counter() - t0) * 1e3, 2)
    out["verify_opening_us"] = {dep: round(verify_depth(dep), 1) for dep in (20, 64, 87, 100)}
    print(json.dumps(out, indent=1))
