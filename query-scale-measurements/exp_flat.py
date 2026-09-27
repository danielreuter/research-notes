"""Timing experiment (outside the repo): flat-root (one root node per instance, vLLM "folded" style) vs banks-by-shape, as instances grow."""
import math, random, sys, time, json, gc

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp_nested as E
from verity.ir import Value, Array, Program, bind, composite, array_of
from verity.ir.query_ast import evaluate, instances, concat, rest
from verity.ir.codec import encode_program, descriptor_size

V = E.V
d, L = 8, 2


def WT(S):
    return Array(S.L, Array(S.d, Array(S.d, V)))


@composite("QFlat", 1, ["R", "T", "d", "L"],
           lambda S: ((("X", Array(S.R, Array(S.T, Array(S.d, V)))), ("W", WT(S))), Array(S.R, Array(S.T, V))))
def QFlat(B, S, X, W):
    req = bind(E.QRequest, T=S.T, d=S.d, L=S.L)
    return array_of([B.call(req, X[k], W) for k in range(S.R)])


# heterogeneous: request k has T_k = 1 + (k % S) tokens; X is a flat token array sliced per request
@composite("QFlatHet", 1, ["R", "S", "d", "L"],
           lambda S: ((("X", Array(sum(1 + (k % S.S) for k in range(S.R)), Array(S.d, V))), ("W", WT(S))), Array(S.R, V)))
def QFlatHet(B, S, X, W):
    outs, pos = [], 0
    for k in range(S.R):
        t = 1 + (k % S.S)
        o = B.call(bind(E.QRequest, T=t, d=S.d, L=S.L), X[pos:pos + t], W)
        outs.append(o[t - 1])
        pos += t
    return array_of(outs)


# banks by shape: one batch node per distinct shape, n requests each
@composite("QBanks", 1, ["S", "n", "d", "L"],
           lambda S: ((("X", Array(sum(S.n * (1 + s) for s in range(S.S)), Array(S.d, V))), ("W", WT(S))),
                      Array(S.S * S.n, V)))
def QBanks(B, S, X, W):
    outs, pos = [], 0
    for s in range(S.S):
        t = 1 + s
        seg = X[pos:pos + S.n * t].reshape(Array(S.n, Array(t, Array(S.d, V))))
        outs.append(B.batch(bind(E.QRequest, T=t, d=S.d, L=S.L), seg, W, axes=(0, None)))
        pos += S.n * t
    return _lasts(outs, S)


def _lasts(outs, S):
    from verity.ir.refs import Coll, Strided
    parts = []
    for o in outs:
        t = o.type.elem.n
        r = o.refs  # Affine over the node's n*t leaves
        parts.append(Coll(Array(S.n, V), Strided(r.space, r.idx, r.base + t - 1, 1, t, 0, S.n)))
    from verity.ir.refs import coll_concat
    return coll_concat(Array(S.S * S.n, V), parts)


def measure(make, label, **kw):
    gc.collect()
    r0 = E.rss_mb()
    t0 = time.perf_counter()
    P = Program(make(**kw))
    build = time.perf_counter() - t0
    r1 = E.rss_mb()
    t0 = time.perf_counter()
    F = evaluate(P, concat(instances("//QDot"), rest()))
    plan = time.perf_counter() - t0
    rng = random.Random(2)
    ix = [rng.randrange(F.count()) for _ in range(2000)]
    t0 = time.perf_counter()
    for i in ix:
        F.by_index(i)
    byi = (time.perf_counter() - t0) / len(ix) * 1e6
    gi = [rng.randrange(P.gates) for _ in range(2000)]
    t0 = time.perf_counter()
    for i in gi:
        P.circuit.gate(i)
    gl = (time.perf_counter() - t0) / len(gi) * 1e6
    from verity_vllm.query import partition as part
    t0 = time.perf_counter()
    pv = part.validate_partition(P, F)
    vp = time.perf_counter() - t0
    t0 = time.perf_counter()
    desc = encode_program(P)
    enc = time.perf_counter() - t0
    nbytes = descriptor_size(desc)
    root_nodes = len(P.root.body.nodes)
    specs = len(desc["definitions"])
    res = {"label": label, **kw, "root_nodes": root_nodes, "definitions": specs, "sets_log10": round(math.log10(F.count()), 2),
           "build_s": round(build, 3), "rss_build_mb": round(r1 - r0, 1), "plan_s": round(plan, 4), "by_index_us": round(byi, 1),
           "gate_us": round(gl, 1), "partition_s": round(vp, 3), "partition": pv.status, "encode_s": round(enc, 3),
           "descriptor_kb": round(nbytes / 1024, 1)}
    print(json.dumps(res), flush=True)
    del P, F, desc
    return res


if __name__ == "__main__":
    which = sys.argv[1]
    if which == "flat":
        for R in (1_000, 10_000, 100_000):
            measure(lambda **k: bind(QFlat, **k), "flat-root", R=R, T=4, d=d, L=L)
    elif which == "het":
        for R, S in ((10_000, 10), (10_000, 100), (10_000, 1000), (10_000, 10_000)):
            measure(lambda **k: bind(QFlatHet, **k), "flat-root-heterogeneous", R=R, S=S, d=d, L=L)
    elif which == "banks":
        for S, n in ((100, 10**12), (1000, 10**12), (10_000, 10**11)):
            measure(lambda **k: bind(QBanks, **k), "banks-by-shape", S=S, n=n, d=d, L=L)
