"""Transformer building blocks as Verity IR composites (forward and backward).

Everything here is explicit dataflow over the abstract primitives in ``accumulation.ir``: a
``MatmulT`` node per matrix product, elementwise/normalisation/softmax blocks between them, and static
*views* (``transpose``, ``head_major``, strided slices) where a real implementation would reshape.
Weights are ordinary composite parameters (``Array<N, Array<K, V16>>``, out-major), so a factory decides
per tensor whether it is a fixed input, accumulated state, or an activation-carried adapter.

Simplifications (they change operator shapes only, never the analysis method):

* attention is full (no causal mask): the score/PV matmuls are ``S x S`` per head;
* the softmax and RMS-norm *backward* passes are represented by their elementwise parts (the small
  per-row statistic corrections are dropped); neither is accumulation-dependent work;
* MoE routing uses a static balanced assignment of token blocks to experts in place of the data-dependent
  gather (the router matmul and the probability-weighted combine are present).
"""

from __future__ import annotations

from verity_ir import Array, bind, composite
from verity_ir.refs import Coll, concat, strided_view

from accumulation.ir import blocks as K
from accumulation.ir import prims as P
from accumulation.ir.blocks import head_major, transpose
from accumulation.ir.prims import V16, V32


def _mm(M, N, Kd, CH):
    return bind(K.MatmulT, M=M, N=N, K=Kd, CH=CH if Kd % 16 == 0 and CH == 16 else 1)


def _mmT(M, N, Kd, CH):
    """weight-gradient matmul ``At^T . Bt`` with token-major operands (``At: K x M``, ``Bt: K x N``)."""
    return bind(K.MatmulTT, M=M, N=N, K=Kd, CH=CH if Kd % 16 == 0 and CH == 16 else 1)


def _chunk(Kd, CH):
    return CH if Kd % 16 == 0 and CH == 16 else 1


def _vt_heads(V: Coll, kvh: int, dh: int, repeat: int) -> Coll:
    """``Array<S, Array<KVH*DH>>`` -> ``Array<KVH*repeat, Array<DH, Array<S>>>``: per query head, the
    transposed value matrix of its KV head (GQA replicates KV heads ``repeat`` times)."""
    s, width = V.type.n, V.type.elem.n
    parts = []
    for h in range(kvh):
        v = strided_view(V, h * dh, s, 1, width, dh * s)
        parts.extend([v] * repeat)
    return Coll(Array(kvh * repeat, Array(dh, Array(s, V16))), concat(parts))


def _token_major(O: Coll, nh: int, dh: int) -> Coll:
    """``Array<NH, Array<S, Array<DH>>>`` -> ``Array<S, Array<NH*DH>>``."""
    s = O.type.elem.n
    parts = [strided_view(O, t * dh, dh, s * dh, 1, nh * dh) for t in range(s)]
    return Coll(Array(s, Array(nh * dh, V16)), concat(parts))


# --- attention -------------------------------------------------------------------------------------------

@composite("AccAttnSeq", 1, ["S", "NH", "KVH", "DH", "CH"],
           lambda S: ((("Q", Array(S.S, Array(S.NH * S.DH, V16))), ("Kc", Array(S.S, Array(S.KVH * S.DH, V16))),
                       ("Vc", Array(S.S, Array(S.KVH * S.DH, V16)))), Array(S.S, Array(S.NH * S.DH, V16))))
def AttnSeq(B, S, Q, Kc, Vc):
    """scores = Q K^T per head, softmax over keys, O = P V; heads regrouped token-major."""
    rep = S.NH // S.KVH
    Qh = head_major(Q, S.NH, S.DH)
    Kh = head_major(Kc, S.KVH, S.DH, repeat=rep)
    sc = B.batch(_mm(S.S, S.S, S.DH, S.CH), Qh, Kh, axes=(0, 0))                    # NH x S x S
    pr = B.call(bind(K.SoftmaxBatch, Q=S.NH * S.S, K=S.S), sc.reshape(Array(S.NH * S.S, Array(S.S, V16))))
    pr = pr.reshape(Array(S.NH, Array(S.S, Array(S.S, V16))))
    Vt = _vt_heads(Vc, S.KVH, S.DH, rep)                                              # NH x DH x S
    O = B.batch(_mm(S.S, S.DH, S.S, S.CH), pr, Vt, axes=(0, 0))                      # NH x S x DH
    return _token_major(O, S.NH, S.DH)


@composite("AccAttnDecodeSeq", 1, ["T", "S", "NH", "KVH", "DH", "CH"],
           lambda S: ((("Q", Array(S.T, Array(S.NH * S.DH, V16))), ("Kc", Array(S.S, Array(S.KVH * S.DH, V16))),
                       ("Vc", Array(S.S, Array(S.KVH * S.DH, V16)))), Array(S.T, Array(S.NH * S.DH, V16))))
def AttnDecodeSeq(B, S, Q, Kc, Vc):
    """KV-cache decode attention for one sequence: ``T`` new queries attend over ``S`` cached keys/values.
    scores = ``Q Kc^T`` (``T x S`` per head), softmax over the ``S`` cached positions, ``O = P Vc``; GQA head
    grouping and token-major regrouping exactly as in :func:`AttnSeq`.

    Every matmul operand is a view of a single tensor (the query rows of one head; the cached key / value rows
    of the matching KV head), which is what ``bounds/upper.py`` needs to tile the pattern.  The cache must be
    one tensor, so the new tokens' own keys/values are *not* attended over (they are the entries appended to
    the cache for the next step): a stated simplification worth ``T/(S+T)`` of the attention work."""
    rep = S.NH // S.KVH
    Qh = head_major(Q, S.NH, S.DH)                                                    # NH x T x DH
    Kh = head_major(Kc, S.KVH, S.DH, repeat=rep)                                      # NH x S x DH
    sc = B.batch(_mm(S.T, S.S, S.DH, S.CH), Qh, Kh, axes=(0, 0))                     # NH x T x S
    pr = B.call(bind(K.SoftmaxBatch, Q=S.NH * S.T, K=S.S), sc.reshape(Array(S.NH * S.T, Array(S.S, V16))))
    pr = pr.reshape(Array(S.NH, Array(S.T, Array(S.S, V16))))
    Vt = _vt_heads(Vc, S.KVH, S.DH, rep)                                              # NH x DH x S
    O = B.batch(_mm(S.T, S.DH, S.S, S.CH), pr, Vt, axes=(0, 0))                      # NH x T x DH
    return _token_major(O, S.NH, S.DH)


def _gqa_lhs(T3: Coll, h: int, rep: int, s: int) -> Coll:
    """head-major ``Array<NH, Array<S, Array<S>>>`` -> ``Array<S, Array<rep*S>>`` with
    ``A[s'][(j, t)] = T3[h*rep + j][t][s']``: the transposes of the ``rep`` per-head matrices sharing KV head
    ``h``, concatenated along the contraction axis (one strided view over the node output)."""
    return Coll(Array(s, Array(rep * s, V16)), strided_view(T3, h * rep * s * s, rep * s, 1, s, s * rep * s))


def _gqa_rhs(X: Coll, h: int, rep: int, s: int, dh: int) -> Coll:
    """token-major ``Array<S, Array<NH*DH>>`` -> ``Array<DH, Array<rep*S>>`` with
    ``B[d][(j, t)] = X[t][(h*rep + j)*DH + d]`` (one strided view per output coordinate ``d``)."""
    width = X.type.elem.n
    parts = [strided_view(X, h * rep * dh + d, s, dh, width, rep * s) for d in range(dh)]
    return Coll(Array(dh, Array(rep * s, V16)), concat(parts))


def _attn_bwd_sig(S):
    from verity_ir import Tuple
    AO, KW = S.NH * S.DH, S.KVH * S.DH
    return ((("Q", Array(S.S, Array(AO, V16))), ("Kc", Array(S.S, Array(KW, V16))), ("Vc", Array(S.S, Array(KW, V16))),
             ("dO", Array(S.S, Array(AO, V16)))),
            Tuple(Array(S.S, Array(AO, V16)), Array(S.S, Array(KW, V16)), Array(S.S, Array(KW, V16))))


@composite("AccAttnSeqBwd", 1, ["S", "NH", "KVH", "DH", "CH"], _attn_bwd_sig)
def AttnSeqBwd(B, S, Q, Kc, Vc, dO):
    """``(dQ, dK, dV)`` for one sequence.  ``P`` is recomputed (activation checkpointing).  The GQA reduction
    (the ``NH/KVH`` query heads sharing one KV head) is folded into the ``dK``/``dV`` matmuls' contraction
    axis: ``dK_h = sum_j dS_{hj}^T Q_{hj}`` is one ``MatmulT`` with contraction ``rep * S``."""
    from verity_ir.refs import tuple_of
    rep = S.NH // S.KVH
    Qh = head_major(Q, S.NH, S.DH)
    Kh = head_major(Kc, S.KVH, S.DH, repeat=rep)
    Vh = head_major(Vc, S.KVH, S.DH, repeat=rep)
    dOh = head_major(dO, S.NH, S.DH)
    sc = B.batch(_mm(S.S, S.S, S.DH, S.CH), Qh, Kh, axes=(0, 0))                    # NH x S x S  (Q K^T)
    pr = B.call(bind(K.SoftmaxBatch, Q=S.NH * S.S, K=S.S), sc.reshape(Array(S.NH * S.S, Array(S.S, V16))))
    pr3 = pr.reshape(Array(S.NH, Array(S.S, Array(S.S, V16))))
    dP = B.batch(_mm(S.S, S.S, S.DH, S.CH), dOh, Vh, axes=(0, 0))                    # NH x S x S  (dO V^T)
    dS = B.call(bind(K.MulBatch, Q=S.NH * S.S, K=S.S), dP.reshape(Array(S.NH * S.S, Array(S.S, V16))), pr)
    dS3 = dS.reshape(Array(S.NH, Array(S.S, Array(S.S, V16))))                       # softmax bwd (elementwise part)
    dQ = B.batch(_mm(S.S, S.DH, S.S, S.CH), dS3, transposes(Kh), axes=(0, 0))        # NH x S x DH  (dS K)
    lhsK = Coll(Array(S.KVH, Array(S.S, Array(rep * S.S, V16))), concat([_gqa_lhs(dS3, h, rep, S.S).refs for h in range(S.KVH)]))
    rhsK = Coll(Array(S.KVH, Array(S.DH, Array(rep * S.S, V16))), concat([_gqa_rhs(Q, h, rep, S.S, S.DH).refs for h in range(S.KVH)]))
    dK = B.batch(_mm(S.S, S.DH, rep * S.S, S.CH), lhsK, rhsK, axes=(0, 0))          # KVH x S x DH (sum_j dS^T Q)
    lhsV = Coll(Array(S.KVH, Array(S.S, Array(rep * S.S, V16))), concat([_gqa_lhs(pr3, h, rep, S.S).refs for h in range(S.KVH)]))
    rhsV = Coll(Array(S.KVH, Array(S.DH, Array(rep * S.S, V16))), concat([_gqa_rhs(dO, h, rep, S.S, S.DH).refs for h in range(S.KVH)]))
    dV = B.batch(_mm(S.S, S.DH, rep * S.S, S.CH), lhsV, rhsV, axes=(0, 0))          # KVH x S x DH (sum_j P^T dO)
    return tuple_of(_token_major(dQ, S.NH, S.DH), _token_major(dK, S.KVH, S.DH), _token_major(dV, S.KVH, S.DH))


def transposes(c: Coll) -> Coll:
    """``Array<H, Array<N, Array<K>>>`` -> ``Array<H, Array<K, Array<N>>>`` (a transpose per head)."""
    h = c.type.n
    parts = [transpose(c[i]).refs for i in range(h)]
    return Coll(Array(h, Array(c.type.elem.elem.n, Array(c.type.elem.n, V16))), concat(parts))


# --- dense transformer block -----------------------------------------------------------------------------

def _block_sig(S):
    D, F, AO, KW = S.D, S.FF, S.NH * S.DH, S.KVH * S.DH
    W = lambda n, k: Array(n, Array(k, V16))
    return ((("x", W(S.Q, D)), ("g1", Array(D, V16)), ("Wq", W(AO, D)), ("Wk", W(KW, D)), ("Wv", W(KW, D)),
             ("Wo", W(D, AO)), ("g2", Array(D, V16)), ("Wg", W(F, D)), ("Wu", W(F, D)), ("Wd", W(D, F))),
            W(S.Q, D))


@composite("AccBlock", 1, ["Q", "S", "D", "FF", "NH", "KVH", "DH", "CH"], _block_sig)
def Block(B, S, x, g1, Wq, Wk, Wv, Wo, g2, Wg, Wu, Wd):
    """pre-norm transformer layer over ``Q`` tokens (``Q/S`` sequences of length ``S``)."""
    D, F, AO, KW, CH = S.D, S.FF, S.NH * S.DH, S.KVH * S.DH, S.CH
    nseq = S.Q // S.S
    xn = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x, g1)
    q = B.call(_mm(S.Q, AO, D, CH), xn, Wq)
    k = B.call(_mm(S.Q, KW, D, CH), xn, Wk)
    v = B.call(_mm(S.Q, KW, D, CH), xn, Wv)
    att = B.batch(bind(AttnSeq, S=S.S, NH=S.NH, KVH=S.KVH, DH=S.DH, CH=CH),
                  q.reshape(Array(nseq, Array(S.S, Array(AO, V16)))), k.reshape(Array(nseq, Array(S.S, Array(KW, V16)))),
                  v.reshape(Array(nseq, Array(S.S, Array(KW, V16)))), axes=(0, 0, 0))
    att = att.reshape(Array(S.Q, Array(AO, V16)))
    o = B.call(_mm(S.Q, D, AO, CH), att, Wo)
    x2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), x, o)
    xn2 = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x2, g2)
    gg = B.call(_mm(S.Q, F, D, CH), xn2, Wg)
    uu = B.call(_mm(S.Q, F, D, CH), xn2, Wu)
    h = B.call(bind(K.SwiGluBatch, Q=S.Q, FF=F), gg, uu)
    dd = B.call(_mm(S.Q, D, F, CH), h, Wd)
    return B.call(bind(K.AddBatch, Q=S.Q, K=D), x2, dd)


def _block_kv_sig(S):
    from verity_ir import Tuple
    params, _ = _block_sig(S)
    W = lambda n, k: Array(n, Array(k, V16))
    return (params, Tuple(W(S.Q, S.D), W(S.Q, S.KVH * S.DH), W(S.Q, S.KVH * S.DH)))


@composite("AccBlockKV", 1, ["Q", "S", "D", "FF", "NH", "KVH", "DH", "CH"], _block_kv_sig)
def BlockKV(B, S, x, g1, Wq, Wk, Wv, Wo, g2, Wg, Wu, Wd):
    """:func:`Block` (same ops, same order) that also returns its ``k`` / ``v`` projections: the prefill layer
    of a session, whose key/value rows are the KV cache the decode layer attends over.  Returns ``(x_out, k, v)``."""
    from verity_ir.refs import tuple_of
    D, F, AO, KW, CH = S.D, S.FF, S.NH * S.DH, S.KVH * S.DH, S.CH
    nseq = S.Q // S.S
    xn = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x, g1)
    q = B.call(_mm(S.Q, AO, D, CH), xn, Wq)
    k = B.call(_mm(S.Q, KW, D, CH), xn, Wk)
    v = B.call(_mm(S.Q, KW, D, CH), xn, Wv)
    att = B.batch(bind(AttnSeq, S=S.S, NH=S.NH, KVH=S.KVH, DH=S.DH, CH=CH),
                  q.reshape(Array(nseq, Array(S.S, Array(AO, V16)))), k.reshape(Array(nseq, Array(S.S, Array(KW, V16)))),
                  v.reshape(Array(nseq, Array(S.S, Array(KW, V16)))), axes=(0, 0, 0))
    att = att.reshape(Array(S.Q, Array(AO, V16)))
    o = B.call(_mm(S.Q, D, AO, CH), att, Wo)
    x2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), x, o)
    xn2 = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x2, g2)
    gg = B.call(_mm(S.Q, F, D, CH), xn2, Wg)
    uu = B.call(_mm(S.Q, F, D, CH), xn2, Wu)
    h = B.call(bind(K.SwiGluBatch, Q=S.Q, FF=F), gg, uu)
    dd = B.call(_mm(S.Q, D, F, CH), h, Wd)
    return tuple_of(B.call(bind(K.AddBatch, Q=S.Q, K=D), x2, dd), k, v)


def _decode_block_sig(S):
    """``Block`` signature plus this layer's KV cache (``NB = Q/T`` sequences x ``S`` cached rows); returns
    ``(x_out, k_new, v_new)`` -- the new tokens' keys/values are the cache entries appended for the next step."""
    from verity_ir import Tuple
    params, _ = _block_sig(S)
    D, KW = S.D, S.KVH * S.DH
    W = lambda n, k: Array(n, Array(k, V16))
    cache = Array(S.Q // S.T, Array(S.S, Array(KW, V16)))
    return (params + (("Kc", cache), ("Vc", cache)), Tuple(W(S.Q, D), W(S.Q, KW), W(S.Q, KW)))


@composite("AccDecodeBlock", 1, ["Q", "T", "S", "D", "FF", "NH", "KVH", "DH", "CH"], _decode_block_sig)
def DecodeBlock(B, S, x, g1, Wq, Wk, Wv, Wo, g2, Wg, Wu, Wd, Kc, Vc):
    """pre-norm transformer layer in KV-cache decode mode over ``Q = NB * T`` new tokens (``NB`` sequences,
    ``T`` teacher-forced new tokens each): the same norms / projections / MLP as :func:`Block` on the ``Q``
    new rows, attention through :func:`AttnDecodeSeq` against the ``S`` cached rows of each sequence."""
    from verity_ir.refs import tuple_of
    D, F, AO, KW, CH = S.D, S.FF, S.NH * S.DH, S.KVH * S.DH, S.CH
    nb = S.Q // S.T
    xn = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x, g1)
    q = B.call(_mm(S.Q, AO, D, CH), xn, Wq)
    k = B.call(_mm(S.Q, KW, D, CH), xn, Wk)
    v = B.call(_mm(S.Q, KW, D, CH), xn, Wv)
    att = B.batch(bind(AttnDecodeSeq, T=S.T, S=S.S, NH=S.NH, KVH=S.KVH, DH=S.DH, CH=CH),
                  q.reshape(Array(nb, Array(S.T, Array(AO, V16)))), Kc, Vc, axes=(0, 0, 0))
    att = att.reshape(Array(S.Q, Array(AO, V16)))
    o = B.call(_mm(S.Q, D, AO, CH), att, Wo)
    x2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), x, o)
    xn2 = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x2, g2)
    gg = B.call(_mm(S.Q, F, D, CH), xn2, Wg)
    uu = B.call(_mm(S.Q, F, D, CH), xn2, Wu)
    h = B.call(bind(K.SwiGluBatch, Q=S.Q, FF=F), gg, uu)
    dd = B.call(_mm(S.Q, D, F, CH), h, Wd)
    return tuple_of(B.call(bind(K.AddBatch, Q=S.Q, K=D), x2, dd), k, v)


def _block_bwd_sig(S):
    params, _ = _block_sig(S)
    D, F, AO, KW = S.D, S.FF, S.NH * S.DH, S.KVH * S.DH
    W = lambda n, k: Array(n, Array(k, V16))
    extra = (("dy", W(S.Q, D)),)
    # returns: dx, then the gradients of the 9 weight tensors in signature order (g1, Wq, Wk, Wv, Wo, g2, Wg, Wu, Wd)
    rets = [W(S.Q, D), Array(D, V16), W(AO, D), W(KW, D), W(KW, D), W(D, AO), Array(D, V16), W(F, D), W(F, D), W(D, F)]
    from verity_ir import Tuple
    return (params + extra, Tuple(*rets))


@composite("AccBlockBwd", 1, ["Q", "S", "D", "FF", "NH", "KVH", "DH", "CH"], _block_bwd_sig)
def BlockBwd(B, S, x, g1, Wq, Wk, Wv, Wo, g2, Wg, Wu, Wd, dy):
    """backward of ``Block``: recomputes the forward activations (activation checkpointing), then the
    data-gradient (``dgrad``, weight operand = the same accumulated weights, transposed view) and the
    weight-gradient (``wgrad``, contraction over the ``Q`` tokens) matmuls."""
    from verity_ir.refs import tuple_of
    D, F, AO, KW, CH = S.D, S.FF, S.NH * S.DH, S.KVH * S.DH, S.CH
    nseq = S.Q // S.S
    mmQ = lambda n, k: _mm(S.Q, n, k, CH)
    # forward recompute (annotated 'recompute': duplicates of forward products, not credited as target work)
    R = "recompute"
    xn = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x, g1, name=R)
    q = B.call(mmQ(AO, D), xn, Wq, name=R)
    k = B.call(mmQ(KW, D), xn, Wk, name=R)
    v = B.call(mmQ(KW, D), xn, Wv, name=R)
    att = B.batch(bind(AttnSeq, S=S.S, NH=S.NH, KVH=S.KVH, DH=S.DH, CH=CH),
                  q.reshape(Array(nseq, Array(S.S, Array(AO, V16)))), k.reshape(Array(nseq, Array(S.S, Array(KW, V16)))),
                  v.reshape(Array(nseq, Array(S.S, Array(KW, V16)))), axes=(0, 0, 0), name=R).reshape(Array(S.Q, Array(AO, V16)))
    o = B.call(mmQ(D, AO), att, Wo, name=R)
    x2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), x, o, name=R)
    xn2 = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x2, g2, name=R)
    gg = B.call(mmQ(F, D), xn2, Wg, name=R)
    uu = B.call(mmQ(F, D), xn2, Wu, name=R)
    h = B.call(bind(K.SwiGluBatch, Q=S.Q, FF=F), gg, uu, name=R)
    # MLP backward
    dH = B.call(mmQ(F, D), dy, transpose(Wd))                                  # dgrad: dy Wd
    dWd = B.call(_mmT(D, F, S.Q, CH), dy, h)              # wgrad: dy^T h
    dG = B.call(bind(K.MulBatch, Q=S.Q, K=F), dH, uu)                        # d silu(g) (elementwise part)
    dU = B.call(bind(K.MulBatch, Q=S.Q, K=F), dH, gg)
    dXn2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), B.call(mmQ(D, F), dG, transpose(Wg)), B.call(mmQ(D, F), dU, transpose(Wu)))
    dWg = B.call(_mmT(F, D, S.Q, CH), dG, xn2)
    dWu = B.call(_mmT(F, D, S.Q, CH), dU, xn2)
    dg2 = B.call(bind(K.ColSumBatch, Q=S.Q, K=D), B.call(bind(K.MulBatch, Q=S.Q, K=D), dXn2, xn2))
    dx2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), dy, B.call(bind(K.GainBatch, Q=S.Q, K=D), dXn2, g2))
    # attention backward
    dAtt = B.call(mmQ(AO, D), dx2, transpose(Wo))                               # dgrad
    dWo = B.call(_mmT(D, AO, S.Q, CH), dx2, att)          # wgrad
    dqkv = B.batch(bind(AttnSeqBwd, S=S.S, NH=S.NH, KVH=S.KVH, DH=S.DH, CH=CH),
                   q.reshape(Array(nseq, Array(S.S, Array(AO, V16)))), k.reshape(Array(nseq, Array(S.S, Array(KW, V16)))),
                   v.reshape(Array(nseq, Array(S.S, Array(KW, V16)))), dAtt.reshape(Array(nseq, Array(S.S, Array(AO, V16)))),
                   axes=(0, 0, 0, 0))
    dQ, dK, dV = _pick(dqkv, 0, nseq, AO, S.Q), _pick(dqkv, 1, nseq, KW, S.Q), _pick(dqkv, 2, nseq, KW, S.Q)
    dXn1 = B.call(mmQ(D, AO), dQ, transpose(Wq))
    dXn1 = B.call(bind(K.AddBatch, Q=S.Q, K=D), dXn1, B.call(mmQ(D, KW), dK, transpose(Wk)))
    dXn1 = B.call(bind(K.AddBatch, Q=S.Q, K=D), dXn1, B.call(mmQ(D, KW), dV, transpose(Wv)))
    dWq = B.call(_mmT(AO, D, S.Q, CH), dQ, xn)
    dWk = B.call(_mmT(KW, D, S.Q, CH), dK, xn)
    dWv = B.call(_mmT(KW, D, S.Q, CH), dV, xn)
    dg1 = B.call(bind(K.ColSumBatch, Q=S.Q, K=D), B.call(bind(K.MulBatch, Q=S.Q, K=D), dXn1, xn))
    dx = B.call(bind(K.AddBatch, Q=S.Q, K=D), dx2, B.call(bind(K.GainBatch, Q=S.Q, K=D), dXn1, g1))
    return tuple_of(dx, dg1, dWq, dWk, dWv, dWo, dg2, dWg, dWu, dWd)


def _pick(dqkv: Coll, which: int, nseq: int, width: int, q: int) -> Coll:
    """component ``which`` of the per-sequence ``(dQ, dK, dV)`` tuples, regrouped ``Array<Q, Array<width>>``."""
    parts = [dqkv[i][which].refs for i in range(nseq)]
    return Coll(Array(q, Array(width, V16)), concat(parts))


# --- mixture of experts ----------------------------------------------------------------------------------

def _moe_sig(S):
    D, F, E = S.D, S.FF, S.E
    W = lambda n, k: Array(n, Array(k, V16))
    return ((("xn", W(S.Q, D)), ("Wr", W(E, D)), ("Wg", Array(E, W(F, D))), ("Wu", Array(E, W(F, D))), ("Wd", Array(E, W(D, F)))),
            W(S.Q, D))


@composite("AccExpertMlp", 1, ["M", "D", "FF", "CH"],
           lambda S: ((("x", Array(S.M, Array(S.D, V16))), ("Wg", Array(S.FF, Array(S.D, V16))), ("Wu", Array(S.FF, Array(S.D, V16))),
                       ("Wd", Array(S.D, Array(S.FF, V16)))), Array(S.M, Array(S.D, V16))))
def ExpertMlp(B, S, x, Wg, Wu, Wd):
    gg = B.call(_mm(S.M, S.FF, S.D, S.CH), x, Wg)
    uu = B.call(_mm(S.M, S.FF, S.D, S.CH), x, Wu)
    h = B.call(bind(K.SwiGluBatch, Q=S.M, FF=S.FF), gg, uu)
    return B.call(_mm(S.M, S.D, S.FF, S.CH), h, Wd)


@composite("AccMoeMlp", 1, ["Q", "D", "FF", "E", "TOPK", "CH"], _moe_sig)
def MoeMlp(B, S, xn, Wr, Wg, Wu, Wd):
    """router matmul + softmax; ``E`` expert MLPs each over ``Q*TOPK/E`` tokens (static balanced routing:
    token block ``b`` (of ``E`` blocks) goes to experts ``(b + j*E/TOPK) mod E``, ``j < TOPK``); outputs
    are weighted by the router probability of the chosen expert and summed over the ``TOPK`` slots."""
    Q, D, E, T, CH = S.Q, S.D, S.E, S.TOPK, S.CH
    assert Q % E == 0 and E % T == 0, (Q, E, T)
    blk = Q // E
    rl = B.call(_mm(Q, E, D, CH), xn, Wr)
    pr = B.call(bind(K.SoftmaxBatch, Q=Q, K=E), rl)
    # expert e's rows: blocks b with (b + j*E/T) mod E == e  <=>  b = (e - j*E/T) mod E
    rows_e = []
    for e in range(E):
        parts = [xn[((e - j * (E // T)) % E) * blk:((e - j * (E // T)) % E + 1) * blk].refs for j in range(T)]
        rows_e.append(concat(parts))
    rows = Coll(Array(E, Array(T * blk, Array(D, V16))), concat(rows_e))
    out = B.batch(bind(ExpertMlp, M=T * blk, D=D, FF=S.FF, CH=CH), rows, Wg, Wu, Wd, axes=(0, 0, 0, 0))  # E x (T*blk) x D
    # combine: slot j of token block b sits in expert e=(b+j*E/T)%E at chunk j
    acc = None
    for j in range(T):
        y_parts, p_parts = [], []
        for b in range(E):
            e = (b + j * (E // T)) % E
            y_parts.append(out[e][j * blk:(j + 1) * blk].refs)
            p_parts.append(strided_view(pr, b * blk * E + e, blk, 0, E, blk))
        y = Coll(Array(Q, Array(D, V16)), concat(y_parts))
        p = Coll(Array(Q, V16), concat(p_parts))
        term = B.call(bind(K.RowScaleBatch, Q=Q, K=D), y, p)
        acc = term if acc is None else B.call(bind(K.AddBatch, Q=Q, K=D), acc, term)
    return acc


def _expert_rows(E: int, T: int, blk: int):
    """static balanced routing: expert ``e`` serves, at slot ``j``, token block ``b = (e - j*E/T) mod E``;
    conversely token block ``b`` sits in expert ``(b + j*E/T) mod E`` at chunk ``j``."""
    return [[((e - j * (E // T)) % E) for j in range(T)] for e in range(E)]


def _gather_by_expert(src: Coll, E: int, T: int, blk: int, elem):
    """rows of ``src`` (``Array<Q, elem>``) regrouped ``Array<E, Array<T*blk, elem>>`` in expert order."""
    parts = []
    for blocks in _expert_rows(E, T, blk):
        parts.append(concat([src[b * blk:(b + 1) * blk].refs for b in blocks]))
    return Coll(Array(E, Array(T * blk, elem)), concat(parts))


def _slot_view(per_expert: Coll, j: int, E: int, T: int, blk: int, q: int, elem):
    """chunk ``j`` of every expert's rows, regrouped in token order (``Array<Q, elem>``)."""
    parts = []
    for b in range(E):
        e = (b + j * (E // T)) % E
        parts.append(per_expert[e][j * blk:(j + 1) * blk].refs)
    return Coll(Array(q, elem), concat(parts))


def _expert_bwd_sig(S):
    W = lambda n, k: Array(n, Array(k, V16))
    from verity_ir import Tuple
    params = (("x", W(S.M, S.D)), ("Wg", W(S.FF, S.D)), ("Wu", W(S.FF, S.D)), ("Wd", W(S.D, S.FF)), ("dy", W(S.M, S.D)))
    return (params, Tuple(W(S.M, S.D), W(S.FF, S.D), W(S.FF, S.D), W(S.D, S.FF), W(S.M, S.D)))


@composite("AccExpertMlpBwd", 1, ["M", "D", "FF", "CH"], _expert_bwd_sig)
def ExpertMlpBwd(B, S, x, Wg, Wu, Wd, dy):
    """backward of ``ExpertMlp`` with full forward recompute (the expert output ``y`` is needed by the
    router backward, so unlike ``BlockBwd`` the last product is recomputed too).  Returns
    ``(dx, dWg, dWu, dWd, y)``."""
    from verity_ir.refs import tuple_of
    M, D, F, CH = S.M, S.D, S.FF, S.CH
    R = "recompute"
    gg = B.call(_mm(M, F, D, CH), x, Wg, name=R)
    uu = B.call(_mm(M, F, D, CH), x, Wu, name=R)
    h = B.call(bind(K.SwiGluBatch, Q=M, FF=F), gg, uu, name=R)
    y = B.call(_mm(M, D, F, CH), h, Wd, name=R)
    dH = B.call(_mm(M, F, D, CH), dy, transpose(Wd))                     # dgrad
    dWd = B.call(_mmT(D, F, M, CH), dy, h)                               # wgrad
    dG = B.call(bind(K.MulBatch, Q=M, K=F), dH, uu)
    dU = B.call(bind(K.MulBatch, Q=M, K=F), dH, gg)
    dx = B.call(bind(K.AddBatch, Q=M, K=D), B.call(_mm(M, D, F, CH), dG, transpose(Wg)),
                B.call(_mm(M, D, F, CH), dU, transpose(Wu)))
    dWg = B.call(_mmT(F, D, M, CH), dG, x)
    dWu = B.call(_mmT(F, D, M, CH), dU, x)
    return tuple_of(dx, dWg, dWu, dWd, y)


def _moe_bwd_sig(S):
    params, _ = _moe_sig(S)
    D, F, E = S.D, S.FF, S.E
    W = lambda n, k: Array(n, Array(k, V16))
    from verity_ir import Tuple
    return (params + (("dm", W(S.Q, D)),),
            Tuple(W(S.Q, D), W(E, D), Array(E, W(F, D)), Array(E, W(F, D)), Array(E, W(D, F))))


@composite("AccMoeMlpBwd", 1, ["Q", "D", "FF", "E", "TOPK", "CH"], _moe_bwd_sig)
def MoeMlpBwd(B, S, xn, Wr, Wg, Wu, Wd, dm):
    """backward of ``MoeMlp``: recomputes the router, runs ``ExpertMlpBwd`` per expert on the probability-
    scaled output gradient, and backpropagates through the combine (``dp_slot = <dm, y_slot>``), the exact
    softmax backward restricted to the ``TOPK`` chosen slots, and the router matmul (``dWr`` per expert as
    a token-contraction product; the token gradient ``ds[q] * Wr[e]`` as a broadcast row scale).  Returns
    ``(dxn, dWr, dWg, dWu, dWd)``."""
    from verity_ir.refs import tuple_of
    Q, D, E, T, CH, F = S.Q, S.D, S.E, S.TOPK, S.CH, S.FF
    assert Q % E == 0 and E % T == 0, (Q, E, T)
    blk = Q // E
    M = T * blk
    row = Array(D, V16)
    # router recompute
    rl = B.call(_mm(Q, E, D, CH), xn, Wr, name="recompute")
    pr = B.call(bind(K.SoftmaxBatch, Q=Q, K=E), rl, name="recompute")
    p_slot = []
    for j in range(T):
        parts = [strided_view(pr, b * blk * E + (b + j * (E // T)) % E, blk, 0, E, blk) for b in range(E)]
        p_slot.append(Coll(Array(Q, V16), concat(parts)))
    # expert backward on dy_slot = dm * p_slot, gathered per expert.  All T slots are scaled by ONE op over
    # slot-stacked rows so that the per-expert gather reads a single tensor (a matmul operand assembled
    # from several producer tensors is not tileable by bounds/upper.py).
    dm_stack = Coll(Array(T * Q, row), concat([dm.refs] * T))
    p_all = Coll(Array(T * Q, V16), concat([p_slot[j].refs for j in range(T)]))
    dy_all = B.call(bind(K.RowScaleBatch, Q=T * Q, K=D), dm_stack, p_all)
    dy_slots = [dy_all[j * Q:(j + 1) * Q] for j in range(T)]
    dy_rows = Coll(Array(E, Array(M, row)),
                   concat([concat([dy_slots[j][b * blk:(b + 1) * blk].refs for j, b in enumerate(blocks)])
                           for blocks in _expert_rows(E, T, blk)]))
    x_rows = _gather_by_expert(xn, E, T, blk, row)
    out = B.batch(bind(ExpertMlpBwd, M=M, D=D, FF=F, CH=CH), x_rows, Wg, Wu, Wd, dy_rows, axes=(0, 0, 0, 0, 0))
    dx_rows = Coll(Array(E, Array(M, row)), concat([out[e][0].refs for e in range(E)]))
    dWg = Coll(Array(E, Array(F, row)), concat([out[e][1].refs for e in range(E)]))
    dWu = Coll(Array(E, Array(F, row)), concat([out[e][2].refs for e in range(E)]))
    dWd = Coll(Array(E, Array(D, Array(F, V16))), concat([out[e][3].refs for e in range(E)]))
    y_rows = Coll(Array(E, Array(M, row)), concat([out[e][4].refs for e in range(E)]))
    # combine backward: dp_slot[q] = <dm[q], y_slot[q]>; softmax backward on the chosen slots:
    # ds_slot = p_slot * (dp_slot - c), c[q] = sum_slots p_slot * dp_slot  (dp is zero off the chosen slots)
    # (slot-stacked single ops throughout, see dy_all: ds_slot feeds the dWr matmul as a gathered operand,
    # and a batched prim whose members read different tensors gets inexact per-copy leaf counts)
    y_all = Coll(Array(T * Q, row), concat([_slot_view(y_rows, j, E, T, blk, Q, row).refs for j in range(T)]))
    dp_all = B.call(bind(K.RowDotBatch, Q=T * Q, K=D, CH=_chunk(D, CH)), dm_stack, y_all)
    pdp = B.batch(P.Mul16, p_all, dp_all, axes=(0, 0))
    c = pdp[0:Q]
    for j in range(1, T):
        c = B.batch(P.Add16, c, pdp[j * Q:(j + 1) * Q], axes=(0, 0))
    c_stack = Coll(Array(T * Q, V16), concat([c.refs] * T))
    ds_all = B.batch(P.Mul16, p_all, B.batch(P.Sub16, dp_all, c_stack, axes=(0, 0)), axes=(0, 0))
    ds_slot = [ds_all[j * Q:(j + 1) * Q] for j in range(T)]
    # router backward: dWr[e] = sum over e's tokens of ds * xn  (M-contraction per expert); dxn += ds * Wr[e]
    ds_rows = Coll(Array(E, Array(M, V16)),
                   concat([concat([ds_slot[j][b * blk:(b + 1) * blk].refs for j, b in enumerate(blocks)])
                           for blocks in _expert_rows(E, T, blk)]))
    dWr = B.batch(_mmT(1, D, M, CH), ds_rows.reshape(Array(E, Array(M, Array(1, V16)))), x_rows, axes=(0, 0))
    dWr = dWr.reshape(Array(E, row))
    dx_router = B.batch(bind(K.RowScaleBroadcastBatch, Q=M, K=D), Wr, ds_rows, axes=(0, 0))   # E x M x D
    dx_rows = B.batch(bind(K.AddBatch, Q=M, K=D), dx_rows, dx_router, axes=(0, 0))
    # scatter the per-expert token gradients back to token order and sum over slots
    acc = None
    for j in range(T):
        term = _slot_view(dx_rows, j, E, T, blk, Q, row)
        acc = term if acc is None else B.call(bind(K.AddBatch, Q=Q, K=D), acc, term)
    return tuple_of(acc, dWr, dWg, dWu, dWd)


def _moe_block_sig(S):
    D, AO, KW = S.D, S.NH * S.DH, S.KVH * S.DH
    W = lambda n, k: Array(n, Array(k, V16))
    return ((("x", W(S.Q, D)), ("g1", Array(D, V16)), ("Wq", W(AO, D)), ("Wk", W(KW, D)), ("Wv", W(KW, D)),
             ("Wo", W(D, AO)), ("g2", Array(D, V16)), ("Wr", W(S.E, D)), ("Wg", Array(S.E, W(S.FF, D))),
             ("Wu", Array(S.E, W(S.FF, D))), ("Wd", Array(S.E, W(D, S.FF)))), W(S.Q, D))


@composite("AccMoeBlock", 1, ["Q", "S", "D", "FF", "NH", "KVH", "DH", "E", "TOPK", "CH"], _moe_block_sig)
def MoeBlock(B, S, x, g1, Wq, Wk, Wv, Wo, g2, Wr, Wg, Wu, Wd):
    D, AO, KW, CH = S.D, S.NH * S.DH, S.KVH * S.DH, S.CH
    nseq = S.Q // S.S
    xn = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x, g1)
    q = B.call(_mm(S.Q, AO, D, CH), xn, Wq)
    k = B.call(_mm(S.Q, KW, D, CH), xn, Wk)
    v = B.call(_mm(S.Q, KW, D, CH), xn, Wv)
    att = B.batch(bind(AttnSeq, S=S.S, NH=S.NH, KVH=S.KVH, DH=S.DH, CH=CH),
                  q.reshape(Array(nseq, Array(S.S, Array(AO, V16)))), k.reshape(Array(nseq, Array(S.S, Array(KW, V16)))),
                  v.reshape(Array(nseq, Array(S.S, Array(KW, V16)))), axes=(0, 0, 0)).reshape(Array(S.Q, Array(AO, V16)))
    o = B.call(_mm(S.Q, D, AO, CH), att, Wo)
    x2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), x, o)
    xn2 = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x2, g2)
    m = B.call(bind(MoeMlp, Q=S.Q, D=D, FF=S.FF, E=S.E, TOPK=S.TOPK, CH=CH), xn2, Wr, Wg, Wu, Wd)
    return B.call(bind(K.AddBatch, Q=S.Q, K=D), x2, m)


def _moe_block_bwd_sig(S):
    D, AO, KW, F, E = S.D, S.NH * S.DH, S.KVH * S.DH, S.FF, S.E
    W = lambda n, k: Array(n, Array(k, V16))
    from verity_ir import Tuple
    params = [("x", W(S.Q, D)), ("g1", Array(D, V16)), ("Wq", W(AO, D)), ("Wk", W(KW, D)), ("Wv", W(KW, D)),
              ("Wo", W(D, AO)), ("g2", Array(D, V16)), ("Wr", W(E, D)), ("Wg", Array(E, W(F, D))),
              ("Wu", Array(E, W(F, D))), ("Wd", Array(E, W(D, F)))]
    rets = [W(S.Q, D), Array(D, V16), W(AO, D), W(KW, D), W(KW, D), W(D, AO), Array(D, V16), W(E, D),
            Array(E, W(F, D)), Array(E, W(F, D)), Array(E, W(D, F))]
    if S.SX:
        params += [("Wsg", W(S.SX * F, D)), ("Wsu", W(S.SX * F, D)), ("Wsd", W(D, S.SX * F))]
        rets += [W(S.SX * F, D), W(S.SX * F, D), W(D, S.SX * F)]
    params.append(("dy", W(S.Q, D)))
    return (tuple(params), Tuple(*rets))


@composite("AccMoeBlockBwd", 1, ["Q", "S", "D", "FF", "NH", "KVH", "DH", "E", "TOPK", "SX", "CH"], _moe_block_bwd_sig)
def MoeBlockBwd(B, S, x, g1, Wq, Wk, Wv, Wo, g2, Wr, Wg, Wu, Wd, *rest):
    """backward of a MoE layer (``SX`` shared experts, 0 for none): attention part as in ``BlockBwd``
    (forward recompute, dgrad, wgrad), MLP part through ``MoeMlpBwd`` (+ ``ExpertMlpBwd`` for the shared
    experts).  Returns ``(dx, dg1, dWq, dWk, dWv, dWo, dg2, dWr, dWg, dWu, dWd[, dWsg, dWsu, dWsd])``."""
    from verity_ir.refs import tuple_of
    if S.SX:
        Wsg, Wsu, Wsd, dy = rest
    else:
        (dy,) = rest
    D, F, AO, KW, CH = S.D, S.FF, S.NH * S.DH, S.KVH * S.DH, S.CH
    nseq = S.Q // S.S
    mmQ = lambda n, k: _mm(S.Q, n, k, CH)
    # attention forward recompute (annotated 'recompute')
    R = "recompute"
    xn = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x, g1, name=R)
    q = B.call(mmQ(AO, D), xn, Wq, name=R)
    k = B.call(mmQ(KW, D), xn, Wk, name=R)
    v = B.call(mmQ(KW, D), xn, Wv, name=R)
    att = B.batch(bind(AttnSeq, S=S.S, NH=S.NH, KVH=S.KVH, DH=S.DH, CH=CH),
                  q.reshape(Array(nseq, Array(S.S, Array(AO, V16)))), k.reshape(Array(nseq, Array(S.S, Array(KW, V16)))),
                  v.reshape(Array(nseq, Array(S.S, Array(KW, V16)))), axes=(0, 0, 0), name=R).reshape(Array(S.Q, Array(AO, V16)))
    o = B.call(mmQ(D, AO), att, Wo, name=R)
    x2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), x, o, name=R)
    xn2 = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x2, g2, name=R)
    # MoE MLP backward (the MoE forward is recomputed inside)
    mo = B.call(bind(MoeMlpBwd, Q=S.Q, D=D, FF=F, E=S.E, TOPK=S.TOPK, CH=CH), xn2, Wr, Wg, Wu, Wd, dy)
    dXn2, dWr, dWg, dWu, dWd = mo[0], mo[1], mo[2], mo[3], mo[4]
    extra = []
    if S.SX:
        so = B.call(bind(ExpertMlpBwd, M=S.Q, D=D, FF=S.SX * F, CH=CH), xn2, Wsg, Wsu, Wsd, dy)
        dXn2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), dXn2, so[0])
        extra = [so[1], so[2], so[3]]
    dg2 = B.call(bind(K.ColSumBatch, Q=S.Q, K=D), B.call(bind(K.MulBatch, Q=S.Q, K=D), dXn2, xn2))
    dx2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), dy, B.call(bind(K.GainBatch, Q=S.Q, K=D), dXn2, g2))
    # attention backward
    dAtt = B.call(mmQ(AO, D), dx2, transpose(Wo))
    dWo = B.call(_mmT(D, AO, S.Q, CH), dx2, att)
    dqkv = B.batch(bind(AttnSeqBwd, S=S.S, NH=S.NH, KVH=S.KVH, DH=S.DH, CH=CH),
                   q.reshape(Array(nseq, Array(S.S, Array(AO, V16)))), k.reshape(Array(nseq, Array(S.S, Array(KW, V16)))),
                   v.reshape(Array(nseq, Array(S.S, Array(KW, V16)))), dAtt.reshape(Array(nseq, Array(S.S, Array(AO, V16)))),
                   axes=(0, 0, 0, 0))
    dQ, dK, dV = _pick(dqkv, 0, nseq, AO, S.Q), _pick(dqkv, 1, nseq, KW, S.Q), _pick(dqkv, 2, nseq, KW, S.Q)
    dXn1 = B.call(mmQ(D, AO), dQ, transpose(Wq))
    dXn1 = B.call(bind(K.AddBatch, Q=S.Q, K=D), dXn1, B.call(mmQ(D, KW), dK, transpose(Wk)))
    dXn1 = B.call(bind(K.AddBatch, Q=S.Q, K=D), dXn1, B.call(mmQ(D, KW), dV, transpose(Wv)))
    dWq = B.call(_mmT(AO, D, S.Q, CH), dQ, xn)
    dWk = B.call(_mmT(KW, D, S.Q, CH), dK, xn)
    dWv = B.call(_mmT(KW, D, S.Q, CH), dV, xn)
    dg1 = B.call(bind(K.ColSumBatch, Q=S.Q, K=D), B.call(bind(K.MulBatch, Q=S.Q, K=D), dXn1, xn))
    dx = B.call(bind(K.AddBatch, Q=S.Q, K=D), dx2, B.call(bind(K.GainBatch, Q=S.Q, K=D), dXn1, g1))
    return tuple_of(dx, dg1, dWq, dWk, dWv, dWo, dg2, dWr, dWg, dWu, dWd, *extra)


# --- LoRA block (frozen base + rank-r adapters on every projection) ---------------------------------------

def _lora_block_sig(S):
    D, F, AO, KW, r = S.D, S.FF, S.NH * S.DH, S.KVH * S.DH, S.R
    W = lambda n, k: Array(n, Array(k, V16))
    base = (("x", W(S.Q, D)), ("g1", Array(D, V16)), ("Wq", W(AO, D)), ("Wk", W(KW, D)), ("Wv", W(KW, D)),
            ("Wo", W(D, AO)), ("g2", Array(D, V16)), ("Wg", W(F, D)), ("Wu", W(F, D)), ("Wd", W(D, F)))
    ad = (("Aq", W(r, D)), ("Bq", W(AO, r)), ("Ak", W(r, D)), ("Bk", W(KW, r)), ("Av", W(r, D)), ("Bv", W(KW, r)),
          ("Ao", W(r, AO)), ("Bo", W(D, r)), ("Ag", W(r, D)), ("Bg", W(F, r)), ("Au", W(r, D)), ("Bu", W(F, r)),
          ("Ad", W(r, F)), ("Bd", W(D, r)))
    return (base + ad, W(S.Q, D))


LORA_ADAPTER_NAMES = ("Aq", "Bq", "Ak", "Bk", "Av", "Bv", "Ao", "Bo", "Ag", "Bg", "Au", "Bu", "Ad", "Bd")


@composite("AccLoraBlock", 1, ["Q", "S", "D", "FF", "NH", "KVH", "DH", "R", "CH"], _lora_block_sig)
def LoraBlock(B, S, x, g1, Wq, Wk, Wv, Wo, g2, Wg, Wu, Wd, Aq, Bq, Ak, Bk, Av, Bv, Ao, Bo, Ag, Bg, Au, Bu, Ad, Bd):
    D, F, AO, KW, CH, r = S.D, S.FF, S.NH * S.DH, S.KVH * S.DH, S.CH, S.R
    nseq = S.Q // S.S

    def proj(inp, W, A, Bm, n, kd):
        base = B.call(_mm(S.Q, n, kd, CH), inp, W)
        low = B.call(_mm(S.Q, r, kd, CH), inp, A)            # Q x r   (activation x adapter A)
        up = B.call(_mm(S.Q, n, r, CH), low, Bm)              # Q x n   (contraction over the rank)
        return B.call(bind(K.AddBatch, Q=S.Q, K=n), base, up)

    xn = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x, g1)
    q = proj(xn, Wq, Aq, Bq, AO, D)
    k = proj(xn, Wk, Ak, Bk, KW, D)
    v = proj(xn, Wv, Av, Bv, KW, D)
    att = B.batch(bind(AttnSeq, S=S.S, NH=S.NH, KVH=S.KVH, DH=S.DH, CH=CH),
                  q.reshape(Array(nseq, Array(S.S, Array(AO, V16)))), k.reshape(Array(nseq, Array(S.S, Array(KW, V16)))),
                  v.reshape(Array(nseq, Array(S.S, Array(KW, V16)))), axes=(0, 0, 0)).reshape(Array(S.Q, Array(AO, V16)))
    o = proj(att, Wo, Ao, Bo, D, AO)
    x2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), x, o)
    xn2 = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x2, g2)
    gg = proj(xn2, Wg, Ag, Bg, F, D)
    uu = proj(xn2, Wu, Au, Bu, F, D)
    h = B.call(bind(K.SwiGluBatch, Q=S.Q, FF=F), gg, uu)
    dd = proj(h, Wd, Ad, Bd, D, F)
    return B.call(bind(K.AddBatch, Q=S.Q, K=D), x2, dd)


def _lora_bwd_sig(S):
    params, _ = _lora_block_sig(S)
    D, F, AO, KW, r = S.D, S.FF, S.NH * S.DH, S.KVH * S.DH, S.R
    W = lambda n, k: Array(n, Array(k, V16))
    from verity_ir import Tuple
    rets = [W(S.Q, D), W(r, D), W(AO, r), W(r, D), W(KW, r), W(r, D), W(KW, r), W(r, AO), W(D, r), W(r, D), W(F, r),
            W(r, D), W(F, r), W(r, F), W(D, r)]
    return (params + (("dy", W(S.Q, D)),), Tuple(*rets))


@composite("AccLoraBlockBwd", 1, ["Q", "S", "D", "FF", "NH", "KVH", "DH", "R", "CH"], _lora_bwd_sig)
def LoraBlockBwd(B, S, x, g1, Wq, Wk, Wv, Wo, g2, Wg, Wu, Wd, Aq, Bq, Ak, Bk, Av, Bv, Ao, Bo, Ag, Bg, Au, Bu, Ad, Bd, dy):
    """backward of ``LoraBlock``: data gradients flow through the frozen base (fixed-weight dgrad, not
    accumulation-dependent) and through the adapters; only adapter weight-gradients are formed."""
    from verity_ir.refs import tuple_of
    D, F, AO, KW, CH, r = S.D, S.FF, S.NH * S.DH, S.KVH * S.DH, S.CH, S.R
    nseq = S.Q // S.S
    mmQ = lambda n, k: _mm(S.Q, n, k, CH)

    R = "recompute"

    def proj(inp, W, A, Bm, n, kd):   # forward recompute of a LoRA projection (not credited as target work)
        base = B.call(mmQ(n, kd), inp, W, name=R)
        low = B.call(mmQ(r, kd), inp, A, name=R)
        up = B.call(mmQ(n, r), low, Bm, name=R)
        return B.call(bind(K.AddBatch, Q=S.Q, K=n), base, up, name=R), low

    def proj_bwd(dout, inp, low, W, A, Bm, n, kd):
        """returns (dinp, dA, dB)"""
        d_in = B.call(mmQ(kd, n), dout, transpose(W))                        # fixed-weight dgrad
        d_low = B.call(mmQ(r, n), dout, transpose(Bm))                       # dgrad through B (accumulated)
        dB = B.call(_mmT(n, r, S.Q, CH), dout, low)     # wgrad B
        d_in2 = B.call(mmQ(kd, r), d_low, transpose(A))                      # dgrad through A (accumulated)
        dA = B.call(_mmT(r, kd, S.Q, CH), d_low, inp)   # wgrad A
        return B.call(bind(K.AddBatch, Q=S.Q, K=kd), d_in, d_in2), dA, dB

    xn = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x, g1, name=R)
    q, lq = proj(xn, Wq, Aq, Bq, AO, D)
    k, lk = proj(xn, Wk, Ak, Bk, KW, D)
    v, lv = proj(xn, Wv, Av, Bv, KW, D)
    att = B.batch(bind(AttnSeq, S=S.S, NH=S.NH, KVH=S.KVH, DH=S.DH, CH=CH),
                  q.reshape(Array(nseq, Array(S.S, Array(AO, V16)))), k.reshape(Array(nseq, Array(S.S, Array(KW, V16)))),
                  v.reshape(Array(nseq, Array(S.S, Array(KW, V16)))), axes=(0, 0, 0), name=R).reshape(Array(S.Q, Array(AO, V16)))
    o, lo = proj(att, Wo, Ao, Bo, D, AO)
    x2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), x, o, name=R)
    xn2 = B.call(bind(K.RmsNormBatch, Q=S.Q, K=D), x2, g2, name=R)
    gg, lg = proj(xn2, Wg, Ag, Bg, F, D)
    uu, lu = proj(xn2, Wu, Au, Bu, F, D)
    h = B.call(bind(K.SwiGluBatch, Q=S.Q, FF=F), gg, uu, name=R)
    _, ld = proj(h, Wd, Ad, Bd, D, F)
    dH, dAd, dBd = proj_bwd(dy, h, ld, Wd, Ad, Bd, D, F)
    dG = B.call(bind(K.MulBatch, Q=S.Q, K=F), dH, uu)
    dU = B.call(bind(K.MulBatch, Q=S.Q, K=F), dH, gg)
    dXn2a, dAg, dBg = proj_bwd(dG, xn2, lg, Wg, Ag, Bg, F, D)
    dXn2b, dAu, dBu = proj_bwd(dU, xn2, lu, Wu, Au, Bu, F, D)
    dXn2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), dXn2a, dXn2b)
    dx2 = B.call(bind(K.AddBatch, Q=S.Q, K=D), dy, B.call(bind(K.GainBatch, Q=S.Q, K=D), dXn2, g2))
    dAtt, dAo, dBo = proj_bwd(dx2, att, lo, Wo, Ao, Bo, D, AO)
    dqkv = B.batch(bind(AttnSeqBwd, S=S.S, NH=S.NH, KVH=S.KVH, DH=S.DH, CH=CH),
                   q.reshape(Array(nseq, Array(S.S, Array(AO, V16)))), k.reshape(Array(nseq, Array(S.S, Array(KW, V16)))),
                   v.reshape(Array(nseq, Array(S.S, Array(KW, V16)))), dAtt.reshape(Array(nseq, Array(S.S, Array(AO, V16)))),
                   axes=(0, 0, 0, 0))
    dQ, dK, dV = _pick(dqkv, 0, nseq, AO, S.Q), _pick(dqkv, 1, nseq, KW, S.Q), _pick(dqkv, 2, nseq, KW, S.Q)
    dXn1a, dAq, dBq = proj_bwd(dQ, xn, lq, Wq, Aq, Bq, AO, D)
    dXn1b, dAk, dBk = proj_bwd(dK, xn, lk, Wk, Ak, Bk, KW, D)
    dXn1c, dAv, dBv = proj_bwd(dV, xn, lv, Wv, Av, Bv, KW, D)
    dXn1 = B.call(bind(K.AddBatch, Q=S.Q, K=D), B.call(bind(K.AddBatch, Q=S.Q, K=D), dXn1a, dXn1b), dXn1c)
    dx = B.call(bind(K.AddBatch, Q=S.Q, K=D), dx2, B.call(bind(K.GainBatch, Q=S.Q, K=D), dXn1, g1))
    return tuple_of(dx, dAq, dBq, dAk, dBk, dAv, dBv, dAo, dBo, dAg, dBg, dAu, dBu, dAd, dBd)


__all__ = ["AttnSeq", "AttnDecodeSeq", "AttnSeqBwd", "Block", "BlockKV", "DecodeBlock", "BlockBwd", "MoeMlp", "MoeMlpBwd", "MoeBlock", "MoeBlockBwd", "ExpertMlp",
           "ExpertMlpBwd", "LoraBlock", "LoraBlockBwd",
           "LORA_ADAPTER_NAMES", "transposes"]
