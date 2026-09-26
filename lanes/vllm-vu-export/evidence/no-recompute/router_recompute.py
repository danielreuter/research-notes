"""Is PR #86's router a recompute?  Hash-cons the computation gates (same primitive, same canonical operands, in order = same value) and
count the gates that recompute an earlier one; then partition a router with ONE shared softmax and rounds reading it."""
import numpy as np

from verity.ir.defs import CompositeDefinition, bind
from verity.ir.refs import tuple_of
from verity.ir.types import Array, Tuple
from verity_vllm.program.registry import moe
from verity_vllm.program.registry.prims import BF16, F32, I32
from verity_vllm.query import word as W


def recomputes(G):
    ops = [[] for _ in range(G.n)]
    for s, d in zip(G.src.tolist(), G.dst.tolist()):
        ops[d].append(s)
    inp = [[] for _ in range(G.n)]
    for i, q in G.input_reads:
        inp[q].append(-1 - i)
    canon, seen, dup = list(range(G.n)), {}, 0
    from collections import Counter
    by = Counter()
    for g in range(G.n):
        key = (int(G.prim[g]), tuple(canon[o] for o in ops[g]), tuple(inp[g]))
        if not ops[g] and not inp[g]:
            key = key + (g,)                     # reads only structure (a constant): not hash-consed here
        if key in seen:
            canon[g] = seen[key]
            dup += 1
            by[(G.prim_names[int(G.prim[g])], G.scope_names[int(G.scope[g])].split("{")[0])] += 1
        else:
            seen[key] = g
    recomputes.by = by.most_common(6)
    return dup


def shared_softmax(E, TOPK, VPT, norm):
    """The rounds construction with the softmax computed ONCE (one MoeRouterProbs call) and every round / weight reading its p."""
    def body(B, S, logits):
        p = list(B.call(bind(moe.MoeRouterProbs, E=E, VPT=VPT), logits))
        neg_big = B.call(moe.NEG_10000)
        consts = [B.call(moe.b1.const(32, i)) for i in range(E)]
        ids = []
        for k in range(TOPK):
            q = p
            for cid in ids:
                q = [B.call(moe.P.SelectF32, B.call(moe.P.I32Eq, consts[i], cid), neg_big, q[i]) for i in range(E)]
            res = B.scan(moe.RouterArgmaxStep, tuple_of(q[0], consts[0], consts[1]), xs=(moe._array(q[1:]),))
            ids.append(res[0][1])
        w = [moe._gather(B, E, p, ids[k]) for k in range(TOPK)]
        if norm:
            acc = B.call(moe.b1.ZERO32)
            for k in range(TOPK):
                acc = B.call(moe.P.F32Add, acc, w[k])
            one = B.call(moe.ONE32)
            denom = B.call(moe.P.SelectF32, B.call(moe.F32GtStrict, acc, B.call(moe.b1.ZERO32)), acc, one)
            scale = B.call(moe.P.F32Div, one, denom)
            w = [B.call(moe.P.F32Mul, w[k], scale) for k in range(TOPK)]
        return tuple_of(moe._array(w), moe._array(ids))
    sig = lambda S: ((("logits", Array(E, BF16)),), Tuple(Array(TOPK, F32), Array(TOPK, I32)))
    return bind(CompositeDefinition(f"RouterShared{'Norm' if norm else ''}", 1, (), sig, body, register=False))


for E, norm in ((64, False), (128, True)):
    rows = []
    for name, fn in (("kernel order (record)", bind(moe.MoeRouterTopKNorm if norm else moe.MoeRouterTopK, E=E, TOPK=8, VPT=8)),
                     ("PR #86 rounds", bind(moe.MoeRouterTopKRoundsNorm if norm else moe.MoeRouterTopKRounds, E=E, TOPK=8, VPT=8)),
                     ("rounds, one shared softmax", shared_softmax(E, 8, 8, norm))):
        G = W.Graph(fn)
        R = W.units(G, 16, 32)
        committed = sum(1 for k in R["kinds"] if k == "committed")
        viol = [int(i) for i in np.flatnonzero(~R["ok"])]
        print(f"E={E} {'Norm ' if norm else ''}{name:28s} computation gates {G.n:6d}  recomputed gates {recomputes(G):6d}  units {len(R['kinds']):5d}  "
              f"committed interior {committed:5d}  max out {int(R['out_bits'].max())} b  width violations {len(viol)}  cut ok {R['cut'].ok}", recomputes.by)
