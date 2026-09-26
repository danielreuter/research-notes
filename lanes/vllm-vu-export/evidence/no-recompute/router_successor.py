"""The router with ONE softmax and successor rounds: round k keeps the experts after round k-1's (p, id) in the kernel's total order
(p descending, index ascending) and takes the same first-max argmax.  Bit equality against MoeRouterTopK[Norm]_v1, and the cut."""
import sys

import numpy as np

sys.path.insert(0, "/tmp/vux")
from router_eq import cases  # noqa: E402

from verity.evaluation import evaluate
from verity.ir.defs import CompositeDefinition, bind
from verity.ir.refs import tuple_of
from verity.ir.types import Array, Tuple
from verity_vllm.program.registry import moe
from verity_vllm.program.registry import prims as P
from verity.ml import scalar as SC
from verity_vllm.program.registry.prims import BF16, F32, I32
from verity_vllm.query import word as W


def successor(E, TOPK, VPT, norm):
    def body(B, S, logits):
        p = list(B.call(bind(moe.MoeRouterProbs, E=E, VPT=VPT), logits))
        neg_big = B.call(moe.NEG_10000)
        consts = [B.call(moe.b1.const(32, i)) for i in range(E)]
        ids, sel = [], []
        q = p
        for k in range(TOPK):
            if k:
                pw, pi = sel[-1], ids[-1]
                q = []
                for i in range(E):
                    after = B.call(SC.BitOr, B.call(moe.F32GtStrict, pw, p[i]),
                                   B.call(SC.BitAnd, B.call(SC.F32Eq, p[i], pw), B.call(SC.BitNot, B.call(P.I32Le, consts[i], pi))))
                    q.append(B.call(P.SelectF32, after, p[i], neg_big))
            res = B.scan(moe.RouterArgmaxStep, tuple_of(q[0], consts[0], consts[1]), xs=(moe._array(q[1:]),))
            ids.append(res[0][1])
            sel.append(moe._gather(B, E, p, ids[-1]))    # p[id_k] from the committed probabilities, not the scan's carry
        w = sel
        if norm:
            acc = B.call(moe.b1.ZERO32)
            for k in range(TOPK):
                acc = B.call(P.F32Add, acc, sel[k])
            one = B.call(moe.ONE32)
            denom = B.call(P.SelectF32, B.call(moe.F32GtStrict, acc, B.call(moe.b1.ZERO32)), acc, one)
            scale = B.call(P.F32Div, one, denom)
            w = [B.call(P.F32Mul, sel[k], scale) for k in range(TOPK)]
        return tuple_of(moe._array(w), moe._array(ids))
    sig = lambda S: ((("logits", Array(E, BF16)),), Tuple(Array(TOPK, F32), Array(TOPK, I32)))
    return bind(CompositeDefinition(f"RouterSuccessor{'Norm' if norm else ''}E{E}", 1, (), sig, body, register=False))


n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
rng = np.random.default_rng(7)
for E, norm in ((64, False), (64, True), (128, False), (128, True)):
    ref = bind(moe.MoeRouterTopKNorm if norm else moe.MoeRouterTopK, E=E, TOPK=8, VPT=8)
    new = successor(E, 8, 8, norm)
    rows = cases(E, rng, n)
    bad = [k for k, r in rows.items() if tuple(evaluate(ref, r)) != tuple(evaluate(new, r))]
    G = W.Graph(new)
    R = W.units(G, 16, 32)
    from collections import Counter
    com = Counter()
    for u, k in enumerate(R["kinds"]):
        if k == "committed":
            com[(G.scope_names[int(R["head_scope"][u])].split("{")[0], G.prim_names[int(R["head_prim"][u])])] += int(R["out_gates"][u])
    print(f"E={E} {'Norm' if norm else 'plain'}: {len(rows)} rows, unequal {len(bad)} {bad[:3]} | computation gates {G.n}, recomputed {len(G.recomputed)}, "
          f"cut ok {R['cut'].ok} {R['cut'].codes} | committed interior {sum(com.values())} | max out {int(R['out_bits'].max())} b, width violations {int((~R['ok']).sum())}",
          flush=True)
    print("    ", com.most_common(8))
