"""Timing experiment (outside the repo): today's verity.ir query machinery on a synthetic
planet-scale Program expressed with nested batch/scan (the "bank" style), plus a few worst cases."""
import math, random, sys, time, json, os, gc

REPO = os.environ.get("VERITY_REPO", "/workspace")
sys.path.insert(0, f"{REPO}/packages/verity/src")
sys.path.insert(0, f"{REPO}/integrations/vllm")

from verity.ir import Value, Array, Tuple, Program, bind, primitive, composite
from verity.ir.refs import Coll
from verity.ir import tuple_of
from verity.ir.query_ast import evaluate, default, members, nodes, instances
from verity.ir.codec import encode_program, program_digest, descriptor_size

V = Value(32)
M32 = 0xFFFFFFFF


def rss_mb():
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS"):
                return int(line.split()[1]) / 1024


@primitive("QZero", 1, [], V)
def QZero():
    return 0


@primitive("QMac", 1, [("acc", V), ("x", V), ("w", V)], V)
def QMac(acc, x, w):
    return (acc + x * w) & M32


@primitive("QAct", 1, [("z", V)], V)
def QAct(z):
    return z >> 7


@composite("QMacStep", 1, [], lambda S: ((("acc", V), ("x", V), ("w", V)), Tuple(V, V)))
def QMacStep(B, S, acc, x, w):
    a = B.call(QMac, acc, x, w)
    return tuple_of(a, a)


@composite("QDot", 1, ["K"], lambda S: ((("x", Array(S.K, V)), ("w", Array(S.K, V))), V))
def QDot(B, S, x, w):
    z = B.call(QZero)
    out = B.scan(QMacStep, z, xs=(x, w))
    return out[0]


@composite("QLinear", 1, ["K", "N"], lambda S: ((("x", Array(S.K, V)), ("W", Array(S.N, Array(S.K, V)))), Array(S.N, V)))
def QLinear(B, S, x, W):
    return B.batch(bind(QDot, K=S.K), x, W, axes=(None, 0))


@composite("QLayer", 1, ["d"], lambda S: ((("h", Array(S.d, V)), ("W", Array(S.d, Array(S.d, V)))), Tuple(Array(S.d, V), V)))
def QLayer(B, S, h, W):
    z = B.call(bind(QLinear, K=S.d, N=S.d), h, W)
    a = B.batch(QAct, z, axes=(0,))
    return tuple_of(a, a[0])


def WT(S):
    return Array(S.L, Array(S.d, Array(S.d, V)))


@composite("QModel", 1, ["d", "L"], lambda S: ((("x", Array(S.d, V)), ("W", WT(S))), V))
def QModel(B, S, x, W):
    out = B.scan(bind(QLayer, d=S.d), x, xs=(W,))
    return out[0][0]


@composite("QRequest", 1, ["T", "d", "L"], lambda S: ((("X", Array(S.T, Array(S.d, V))), ("W", WT(S))), Array(S.T, V)))
def QRequest(B, S, X, W):
    return B.batch(bind(QModel, d=S.d, L=S.L), X, W, axes=(0, None))


@composite("QAccel", 1, ["R", "T", "d", "L"],
           lambda S: ((("X", Array(S.R, Array(S.T, Array(S.d, V)))), ("W", WT(S))), Array(S.R, Array(S.T, V))))
def QAccel(B, S, X, W):
    return B.batch(bind(QRequest, T=S.T, d=S.d, L=S.L), X, W, axes=(0, None))


@composite("QDC", 1, ["A", "R", "T", "d", "L"],
           lambda S: ((("X", Array(S.A, Array(S.R, Array(S.T, Array(S.d, V))))), ("W", WT(S))),
                      Array(S.A, Array(S.R, Array(S.T, V)))))
def QDC(B, S, X, W):
    return B.batch(bind(QAccel, R=S.R, T=S.T, d=S.d, L=S.L), X, W, axes=(0, None))


@composite("QPlanet", 1, ["D", "A", "R", "T", "d", "L"],
           lambda S: ((("X", Array(S.D, Array(S.A, Array(S.R, Array(S.T, Array(S.d, V)))))), ("W", WT(S))),
                      Array(S.D, Array(S.A, Array(S.R, Array(S.T, V))))))
def QPlanet(B, S, X, W):
    return B.batch(bind(QDC, A=S.A, R=S.R, T=S.T, d=S.d, L=S.L), X, W, axes=(0, None))


def timeit(fn, n):
    t0 = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - t0) / n


def main():
    out = {}
    params = dict(D=300, A=100_000, R=1_200_000_000, T=1000, d=8192, L=80)
    t0 = time.perf_counter()
    P = Program(bind(QPlanet, **params))
    out["build_s"] = time.perf_counter() - t0
    C = P.circuit
    out["gates"] = P.gates
    out["gates_log10"] = math.log10(P.gates)
    out["input_gates_log10"] = math.log10(P.input_gates)
    rng = random.Random(1)

    # C[i]: random gates over the whole range
    idx = [rng.randrange(P.gates) for _ in range(2000)]
    t0 = time.perf_counter()
    for i in idx:
        g = C.gate(i)
    out["gate_lookup_us"] = (time.perf_counter() - t0) / len(idx) * 1e6
    g = C.gate(idx[0])
    out["sample_gate"] = {"prim": g.prim.id, "depth": len(g.path), "operands": [str(o)[:12] + ".." for o in g.operands]}

    # structural query: every dot product
    t0 = time.perf_counter()
    F = evaluate(P, "//QDot")
    out["plan_dot_s"] = time.perf_counter() - t0
    out["dot_count_log10"] = math.log10(F.count())
    ix = [rng.randrange(F.count()) for _ in range(2000)]
    t0 = time.perf_counter()
    sets = [F.by_index(i) for i in ix]
    out["dot_by_index_us"] = (time.perf_counter() - t0) / len(ix) * 1e6
    t0 = time.perf_counter()
    back = [F.index_of(s) for s in sets[:500]]
    out["dot_index_of_us"] = (time.perf_counter() - t0) / 500 * 1e6
    assert back == ix[:500]
    t0 = time.perf_counter()
    ivs = [s.intervals() for s in sets[:500]]
    out["dot_intervals_us"] = (time.perf_counter() - t0) / 500 * 1e6

    # a VU decomposition: default(32) (one set per <=32-bit member; Input gates one each)
    t0 = time.perf_counter()
    try:
        evaluate(P, default(32))
        out["default32"] = "ok"
    except MemoryError:
        out["default32"] = "MemoryError in member_width -> Type.leaf_widths()"
    out["default32_s"] = time.perf_counter() - t0
    from verity.ir.query_ast import concat, rest
    t0 = time.perf_counter()
    FD = evaluate(P, concat(instances("//QDot"), rest()))
    out["partition_query_plan_s"] = time.perf_counter() - t0
    out["partition_query_sets_log10"] = math.log10(FD.count())
    ix = [rng.randrange(FD.count()) for _ in range(2000)]
    t0 = time.perf_counter()
    for i in ix:
        FD.by_index(i)
    out["partition_query_by_index_us"] = (time.perf_counter() - t0) / len(ix) * 1e6
    t0 = time.perf_counter()
    cls = FD.classes()
    out["partition_query_classes_s"] = time.perf_counter() - t0
    out["partition_query_classes"] = len(cls)

    # partition validation fast path (vLLM's partition.py, tiling induction) and width
    from verity_vllm.query import partition as part
    t0 = time.perf_counter()
    pv = part.validate_partition(P, FD)
    out["validate_partition_s"] = time.perf_counter() - t0
    out["validate_partition"] = {"status": pv.status, "path": pv.detail.get("path")}
    t0 = time.perf_counter()
    rd = part.gate_width_readiness(P, 32)
    out["readiness_s"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    try:
        wv = part.validate_width(P, FD, 32)
        out["validate_width"] = {"status": wv.status, "path": wv.detail.get("path")}
    except Exception as e:  # boundary module may need more
        out["validate_width"] = f"error {type(e).__name__}: {e}"[:200]
    out["validate_width_s"] = time.perf_counter() - t0

    # descriptor and digest
    t0 = time.perf_counter()
    desc = encode_program(P)
    out["encode_s"] = time.perf_counter() - t0
    out["descriptor_bytes"] = descriptor_size(desc)
    t0 = time.perf_counter()
    program_digest(desc)
    out["digest_s"] = time.perf_counter() - t0

    # explicit boundary on a region: refused (explicit_limit)
    try:
        C.region(0, 10).out
        out["region_out"] = "computed"
    except ValueError as e:
        out["region_out"] = str(e)[:100]
    out["rss_mb"] = rss_mb()
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
