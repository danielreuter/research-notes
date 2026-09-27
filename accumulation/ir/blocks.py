"""Reusable Verity IR composites for training circuits.

Everything here is explicit dataflow over the abstract primitives in ``prims.py``.  The one operator the
whole analysis revolves around is ``MatmulT``: ``C[m][n] = sum_k A[m][k] * B[n][k]`` written as a batch
(over ``m``) of a batch (over ``n``) of a ``Dot`` (a scan over ``K/CH`` chunk transitions).  Every matrix
product in every algorithm — forward projections, activation gradients, weight gradients, attention
scores, attention-times-values, LoRA factors, expert MLPs — is a ``MatmulT`` on suitably *viewed*
operands (transposes and head-major slices are reference rearrangements, never gates), so the operator
graph extractor has exactly one shape of node to recognise.

Static parameters are CAPITALS; ``CH`` is the MAC chunk width (16 mimics the tensor-core transition
gate of the serving vocabulary; 1 gives scalar MAC gates for the exact solver's tiny circuits).
"""

from __future__ import annotations

from verity_ir import Array, Tuple, Value, bind, composite
from verity_ir.refs import Coll, array_of, concat, strided_view, tuple_of

from . import prims as P
from .prims import V16, V32

# ---------------------------------------------------------------------------------------------------------
# views (no gates)
# ---------------------------------------------------------------------------------------------------------


def transpose(c: Coll) -> Coll:
    """``Array<N, Array<K, T>>`` -> ``Array<K, Array<N, T>>`` as a strided view (scalar leaves only)."""
    n, k = c.type.n, c.type.elem.n
    assert isinstance(c.type.elem.elem, Value)
    return Coll(Array(k, Array(n, c.type.elem.elem)), strided_view(c, 0, n, 1, k, n * k))


def head_major(c: Coll, nh: int, dh: int, repeat: int = 1) -> Coll:
    """``Array<S, Array<NH*DH>>`` (token-major) -> ``Array<NH*repeat, Array<S, Array<DH>>>`` (head-major).
    ``repeat`` replicates each head ``repeat`` times (GQA: a K/V head serves ``NH/KVH`` query heads)."""
    s, width = c.type.n, c.type.elem.n
    assert width == nh * dh, (width, nh, dh)
    parts = []
    for h in range(nh):
        v = strided_view(c, h * dh, dh, width, 1, s * dh)
        parts.extend([v] * repeat)
    return Coll(Array(nh * repeat, Array(s, Array(dh, V16))), concat(parts))


def rows(c: Coll, lo: int, hi: int) -> Coll:
    return c[lo:hi]


# ---------------------------------------------------------------------------------------------------------
# dot products and MatmulT
# ---------------------------------------------------------------------------------------------------------


@composite("AccMacStep", 1, ["CH"], lambda S: ((("acc", V32), ("x", Array(S.CH, V16) if S.CH > 1 else V16),
                                                  ("w", Array(S.CH, V16) if S.CH > 1 else V16)), Tuple(V32, V32)))
def MacStep(B, S, acc, x, w):
    """One accumulator transition; the scan output is the carried value itself (no extra gate)."""
    assert S.CH in (1, 16), "chunk width must be 1 (scalar MAC) or 16 (tensor-core-shaped transition)"
    acc2 = B.call(P.Mac16 if S.CH > 1 else P.Mac1, acc, x, w)
    return tuple_of(acc2, acc2)


@composite("AccDot", 1, ["K", "CH"], lambda S: ((("x", Array(S.K, V16)), ("w", Array(S.K, V16))), V32))
def Dot(B, S, x, w):
    """``sum_k x[k]*w[k]`` as ``K/CH`` chained accumulator transitions from a zero accumulator."""
    assert S.K % S.CH == 0, (S.K, S.CH)
    zero = B.call(P.Zero32)
    if S.CH > 1:
        xs = x.reshape(Array(S.K // S.CH, Array(S.CH, V16)))
        ws = w.reshape(Array(S.K // S.CH, Array(S.CH, V16)))
    else:
        xs, ws = x, w
    out = B.scan(bind(MacStep, CH=S.CH), zero, xs=(xs, ws))
    return out[0]


@composite("AccDotRound", 1, ["K", "CH"], lambda S: ((("x", Array(S.K, V16)), ("w", Array(S.K, V16))), V16))
def DotRound(B, S, x, w):
    return B.call(P.Round16, B.call(bind(Dot, K=S.K, CH=S.CH), x, w))


@composite("AccRowT", 1, ["N", "K", "CH"],
           lambda S: ((("a", Array(S.K, V16)), ("Bm", Array(S.N, Array(S.K, V16)))), Array(S.N, V16)))
def RowT(B, S, a, Bm):
    """one row of ``A . B^T``: ``N`` dot products sharing ``a``."""
    return B.batch(bind(DotRound, K=S.K, CH=S.CH), a, Bm, axes=(None, 0))


@composite("AccMatmulT", 1, ["M", "N", "K", "CH"],
           lambda S: ((("A", Array(S.M, Array(S.K, V16))), ("Bm", Array(S.N, Array(S.K, V16)))),
                      Array(S.M, Array(S.N, V16))))
def MatmulT(B, S, A, Bm):
    """``C = A . B^T`` (``M x N``, contraction ``K``), the universal matmul node."""
    return B.batch(bind(RowT, N=S.N, K=S.K, CH=S.CH), A, Bm, axes=(0, None))


@composite("AccMatmulTT", 1, ["M", "N", "K", "CH"],
           lambda S: ((("At", Array(S.K, Array(S.M, V16))), ("Bt", Array(S.K, Array(S.N, V16)))),
                      Array(S.M, Array(S.N, V16))))
def MatmulTT(B, S, At, Bt):
    """``C = At^T . Bt`` (``M x N``, contraction ``K`` over the *leading* axis of both operands): the
    weight-gradient form ``dW = dY^T X`` with token-major operands.  Same gates as ``MatmulT`` -- the
    transposes are views taken inside this body, where both operands are plain parameter ranges, so callers
    never build a strided view over a batched activation at root level (which is not O(1))."""
    return B.call(bind(MatmulT, M=S.M, N=S.N, K=S.K, CH=S.CH), transpose(At), transpose(Bt))


def matmul_gates(M: int, N: int, K: int, CH: int) -> int:
    """gate count of ``MatmulT{M,N,K,CH}``: per output ``K/CH`` MAC gates + zero + round."""
    return M * N * (K // CH + 2)


def matmul_macs(M: int, N: int, K: int) -> int:
    return M * N * K


# ---------------------------------------------------------------------------------------------------------
# elementwise / normalisation / activation
# ---------------------------------------------------------------------------------------------------------


@composite("AccSqAcc", 1, [], lambda S: ((("acc", V32), ("x", V16)), Tuple(V32, V32)))
def SqAcc(B, S, acc, x):
    acc2 = B.call(P.Add32, acc, B.call(P.Sq32, x))
    return tuple_of(acc2, acc2)


@composite("AccRmsNorm", 1, ["K"], lambda S: ((("x", Array(S.K, V16)), ("g", Array(S.K, V16))), Array(S.K, V16)))
def RmsNorm(B, S, x, g):
    """``g * x * rsqrt(mean(x^2))``: reduction scan + one statistic + per-coordinate scale and gain."""
    zero = B.call(P.Zero32)
    ss = B.scan(SqAcc, zero, xs=(x,))[0]
    r = B.call(P.Rsqrt32, ss)
    xn = B.batch(P.Scale16, x, r, axes=(0, None))
    return B.batch(P.Mul16, xn, g, axes=(0, 0))


@composite("AccRmsNormBatch", 1, ["Q", "K"],
           lambda S: ((("X", Array(S.Q, Array(S.K, V16))), ("g", Array(S.K, V16))), Array(S.Q, Array(S.K, V16))))
def RmsNormBatch(B, S, X, g):
    return B.batch(bind(RmsNorm, K=S.K), X, g, axes=(0, None))


@composite("AccAddBatch", 1, ["Q", "K"],
           lambda S: ((("X", Array(S.Q, Array(S.K, V16))), ("Y", Array(S.Q, Array(S.K, V16)))), Array(S.Q, Array(S.K, V16))))
def AddBatch(B, S, X, Y):
    return B.batch(bind(AddRow, K=S.K), X, Y, axes=(0, 0))


@composite("AccAddRow", 1, ["K"], lambda S: ((("x", Array(S.K, V16)), ("y", Array(S.K, V16))), Array(S.K, V16)))
def AddRow(B, S, x, y):
    return B.batch(P.Add16, x, y, axes=(0, 0))


@composite("AccMulRow", 1, ["K"], lambda S: ((("x", Array(S.K, V16)), ("y", Array(S.K, V16))), Array(S.K, V16)))
def MulRow(B, S, x, y):
    return B.batch(P.Mul16, x, y, axes=(0, 0))


@composite("AccMulBatch", 1, ["Q", "K"],
           lambda S: ((("X", Array(S.Q, Array(S.K, V16))), ("Y", Array(S.Q, Array(S.K, V16)))), Array(S.Q, Array(S.K, V16))))
def MulBatch(B, S, X, Y):
    return B.batch(bind(MulRow, K=S.K), X, Y, axes=(0, 0))


@composite("AccSwiGluRow", 1, ["FF"], lambda S: ((("g", Array(S.FF, V16)), ("u", Array(S.FF, V16))), Array(S.FF, V16)))
def SwiGluRow(B, S, g, u):
    return B.batch(P.SiluMul16, g, u, axes=(0, 0))


@composite("AccSwiGluBatch", 1, ["Q", "FF"],
           lambda S: ((("G", Array(S.Q, Array(S.FF, V16))), ("U", Array(S.Q, Array(S.FF, V16)))), Array(S.Q, Array(S.FF, V16))))
def SwiGluBatch(B, S, G, U):
    return B.batch(bind(SwiGluRow, FF=S.FF), G, U, axes=(0, 0))


@composite("AccScaleRow", 1, ["K"], lambda S: ((("x", Array(S.K, V16)), ("s", V32)), Array(S.K, V16)))
def ScaleRow(B, S, x, s):
    return B.batch(P.Scale16, x, s, axes=(0, None))


@composite("AccScaleBatch", 1, ["Q", "K"],
           lambda S: ((("X", Array(S.Q, Array(S.K, V16))), ("s", V32)), Array(S.Q, Array(S.K, V16))))
def ScaleBatch(B, S, X, s):
    return B.batch(bind(ScaleRow, K=S.K), X, s, axes=(0, None))


# ---------------------------------------------------------------------------------------------------------
# softmax (row-wise over K entries given as 16-bit scores)
# ---------------------------------------------------------------------------------------------------------


@composite("AccMaxAcc", 1, [], lambda S: ((("acc", V32), ("x", V16)), Tuple(V32, V32)))
def MaxAcc(B, S, acc, x):
    acc2 = B.call(P.Max32, acc, B.call(P.Widen32, x))
    return tuple_of(acc2, acc2)


@composite("AccSumAcc", 1, [], lambda S: ((("acc", V32), ("x", V32)), Tuple(V32, V32)))
def SumAcc(B, S, acc, x):
    acc2 = B.call(P.Add32, acc, x)
    return tuple_of(acc2, acc2)


@composite("AccExpRow", 1, [], lambda S: ((("x", V16), ("m", V32)), V32))
def ExpRow(B, S, x, m):
    return B.call(P.ExpSub32, B.call(P.Widen32, x), m)


@composite("AccSoftmaxRow", 1, ["K"], lambda S: ((("s", Array(S.K, V16)),), Array(S.K, V16)))
def SoftmaxRow(B, S, s):
    """row softmax: max scan, exp, sum scan, reciprocal, normalise-and-round to 16 bits."""
    zero = B.call(P.Zero32)
    m = B.scan(MaxAcc, zero, xs=(s,))[0]
    e = B.batch(ExpRow, s, m, axes=(0, None))
    tot = B.scan(SumAcc, zero, xs=(e,))[0]
    inv = B.call(P.Rcp32, tot)
    return B.batch(P.Round16Scaled, e, inv, axes=(0, None))


@composite("AccSoftmaxBatch", 1, ["Q", "K"],
           lambda S: ((("Sm", Array(S.Q, Array(S.K, V16))),), Array(S.Q, Array(S.K, V16))))
def SoftmaxBatch(B, S, Sm):
    return B.batch(bind(SoftmaxRow, K=S.K), Sm, axes=(0,))


@composite("AccLossGradRow", 1, ["V"],
           lambda S: ((("logits", Array(S.V, V16)), ("tgt", V32), ("ids", Array(S.V, V32))), Array(S.V, V16)))
def LossGradRow(B, S, logits, tgt, ids):
    """``softmax(logits) - onehot(target)``: the gradient of cross-entropy w.r.t. the logits.  The target
    is a token id; ``ids`` is the constant vector ``0..V-1`` (a fixed input) so the one-hot never has to
    be supplied as a ``V``-wide runtime input."""
    p = B.call(bind(SoftmaxRow, K=S.V), logits)
    return B.batch(P.OneHotSub16, p, ids, tgt, axes=(0, 0, None))


@composite("AccLossGradBatch", 1, ["Q", "V"],
           lambda S: ((("L", Array(S.Q, Array(S.V, V16))), ("T", Array(S.Q, V32)), ("ids", Array(S.V, V32))),
                      Array(S.Q, Array(S.V, V16))))
def LossGradBatch(B, S, L, T, ids):
    return B.batch(bind(LossGradRow, V=S.V), L, T, ids, axes=(0, 0, None))


@composite("AccGainBatch", 1, ["Q", "K"],
           lambda S: ((("X", Array(S.Q, Array(S.K, V16))), ("g", Array(S.K, V16))), Array(S.Q, Array(S.K, V16))))
def GainBatch(B, S, X, g):
    """``X * g`` with a per-column gain shared across rows (norm backward through the gain; also the
    elementwise stand-in for the norm's statistic backward, which is not accumulation-dependent work)."""
    return B.batch(bind(MulRow, K=S.K), X, g, axes=(0, None))


@composite("AccRowScaleBatch", 1, ["Q", "K"],
           lambda S: ((("X", Array(S.Q, Array(S.K, V16))), ("s", Array(S.Q, V16))), Array(S.Q, Array(S.K, V16))))
def RowScaleBatch(B, S, X, s):
    """row ``q`` of ``X`` times the scalar ``s[q]`` (MoE combine: expert output weighted by its router prob)."""
    return B.batch(bind(RowScale, K=S.K), X, s, axes=(0, 0))


@composite("AccRowScale", 1, ["K"], lambda S: ((("x", Array(S.K, V16)), ("s", V16)), Array(S.K, V16)))
def RowScale(B, S, x, s):
    return B.batch(P.Mul16, x, s, axes=(0, None))


@composite("AccRowScaleBroadcastBatch", 1, ["Q", "K"],
           lambda S: ((("x", Array(S.K, V16)), ("s", Array(S.Q, V16))), Array(S.Q, Array(S.K, V16))))
def RowScaleBroadcastBatch(B, S, x, s):
    """outer product ``s[q] * x[k]``: one shared row ``x`` scaled by a per-row scalar (MoE router backward:
    the data gradient a token receives through the router logit of its expert is ``ds[q] * Wr[e]``)."""
    return B.batch(bind(RowScale, K=S.K), x, s, axes=(None, 0))


@composite("AccRowDotBatch", 1, ["Q", "K", "CH"],
           lambda S: ((("X", Array(S.Q, Array(S.K, V16))), ("Y", Array(S.Q, Array(S.K, V16)))), Array(S.Q, V16)))
def RowDotBatch(B, S, X, Y):
    """row-wise dot products ``sum_k X[q,k] Y[q,k]`` (``Q*K`` MACs; MoE combine backward: the gradient of
    the router probability of a slot is ``<dm[q], y_slot[q]>``)."""
    return B.batch(bind(DotRound, K=S.K, CH=S.CH), X, Y, axes=(0, 0))


@composite("AccRowSum", 1, ["K"], lambda S: ((("x", Array(S.K, V16)),), V16))
def RowSum(B, S, x):
    tot = B.scan(SumAcc16, B.call(P.Zero32), xs=(x,))[0]
    return B.call(P.Round16, tot)


@composite("AccSoftmaxBwdRow", 1, ["K"],
           lambda S: ((("p", Array(S.K, V16)), ("dp", Array(S.K, V16))), Array(S.K, V16)))
def SoftmaxBwdRow(B, S, p, dp):
    """``ds = p * (dp - <p, dp>)``: the exact softmax backward for one row."""
    t = B.batch(P.Mul16, p, dp, axes=(0, 0))
    c = B.call(bind(RowSum, K=S.K), t)
    d = B.batch(P.Sub16, dp, c, axes=(0, None))
    return B.batch(P.Mul16, p, d, axes=(0, 0))


@composite("AccSoftmaxBwdBatch", 1, ["Q", "K"],
           lambda S: ((("Pm", Array(S.Q, Array(S.K, V16))), ("dP", Array(S.Q, Array(S.K, V16)))),
                      Array(S.Q, Array(S.K, V16))))
def SoftmaxBwdBatch(B, S, Pm, dP):
    return B.batch(bind(SoftmaxBwdRow, K=S.K), Pm, dP, axes=(0, 0))


@composite("AccSumAcc16", 1, [], lambda S: ((("acc", V32), ("x", V16)), Tuple(V32, V32)))
def SumAcc16(B, S, acc, x):
    acc2 = B.call(P.Add32, acc, B.call(P.Widen32, x))
    return tuple_of(acc2, acc2)


@composite("AccColSum", 1, ["Q"], lambda S: ((("col", Array(S.Q, V16)),), V16))
def ColSum(B, S, col):
    """sum of ``Q`` 16-bit values (a reduction over the token axis, e.g. a gain gradient)."""
    tot = B.scan(SumAcc16, B.call(P.Zero32), xs=(col,))[0]
    return B.call(P.Round16, tot)


@composite("AccColSumBatch", 1, ["Q", "K"],
           lambda S: ((("X", Array(S.Q, Array(S.K, V16))),), Array(S.K, V16)))
def ColSumBatch(B, S, X):
    """column sums of a ``Q x K`` matrix (``K`` reductions over the ``Q`` rows)."""
    return B.batch(bind(ColSum, Q=S.Q), transpose(X), axes=(0,))


# ---------------------------------------------------------------------------------------------------------
# embedding gather
# ---------------------------------------------------------------------------------------------------------


@composite("AccEmbedRow", 1, ["V", "D"],
           lambda S: ((("tok", V32), ("tableT", Array(S.D, Array(S.V, V16)))), Array(S.D, V16)))
def EmbedRow(B, S, tok, tableT):
    """one embedding row: ``D`` gathers, each reading one whole ``V``-entry column of the (transposed) table."""
    return B.batch(P.Gather16(S.V), tok, tableT, axes=(None, 0))


@composite("AccEmbedBatch", 1, ["Q", "V", "D"],
           lambda S: ((("toks", Array(S.Q, V32)), ("tableT", Array(S.D, Array(S.V, V16)))), Array(S.Q, Array(S.D, V16))))
def EmbedBatch(B, S, toks, tableT):
    return B.batch(bind(EmbedRow, V=S.V, D=S.D), toks, tableT, axes=(0, None))


# ---------------------------------------------------------------------------------------------------------
# parameter updates and evolution-strategy perturbations
# ---------------------------------------------------------------------------------------------------------


@composite("AccSgdRow", 1, ["K"], lambda S: ((("w", Array(S.K, V16)), ("g", Array(S.K, V16)), ("lr", V32)), Array(S.K, V16)))
def SgdRow(B, S, w, g, lr):
    return B.batch(P.Sub16, w, B.batch(P.Scale16, g, lr, axes=(0, None)), axes=(0, 0))


@composite("AccSgdUpdate", 1, ["N", "K"],
           lambda S: ((("W", Array(S.N, Array(S.K, V16))), ("G", Array(S.N, Array(S.K, V16))), ("lr", V32)),
                      Array(S.N, Array(S.K, V16))))
def SgdUpdate(B, S, W, G, lr):
    """``W - lr * G`` coordinate-wise (Adam-style optimisers differ only in elementwise work)."""
    return B.batch(bind(SgdRow, K=S.K), W, G, lr, axes=(0, 0, None))


@composite("AccNoiseRow", 1, ["K"], lambda S: ((("seed", V32), ("ctrs", Array(S.K, V32))), Array(S.K, V32)))
def NoiseRow(B, S, seed, ctrs):
    return B.batch(P.Hash32, seed, ctrs, axes=(None, 0))


@composite("AccPerturbRow", 1, ["K"],
           lambda S: ((("w", Array(S.K, V16)), ("noise", Array(S.K, V32)), ("sigma", V32)), Array(S.K, V16)))
def PerturbRow(B, S, w, noise, sigma):
    return B.batch(P.Perturb16, w, noise, sigma, axes=(0, 0, None))


@composite("AccPerturb", 1, ["N", "K"],
           lambda S: ((("W", Array(S.N, Array(S.K, V16))), ("seed", V32), ("ctrs", Array(S.N, Array(S.K, V32))), ("sigma", V32)),
                      Array(S.N, Array(S.K, V16))))
def Perturb(B, S, W, seed, ctrs, sigma):
    """``W + sigma * eps(seed)``: a perturbed copy of a weight matrix, noise regenerated from a seed."""
    noise = B.batch(bind(NoiseRow, K=S.K), seed, ctrs, axes=(None, 0))
    return B.batch(bind(PerturbRow, K=S.K), W, noise, sigma, axes=(0, 0, None))


@composite("AccEsUpdateRow", 1, ["K"],
           lambda S: ((("w", Array(S.K, V16)), ("noise", Array(S.K, V32)), ("coef", V32)), Array(S.K, V16)))
def EsUpdateRow(B, S, w, noise, coef):
    return B.batch(P.EsUpdate16, w, noise, coef, axes=(0, 0, None))


@composite("AccEsUpdate", 1, ["N", "K"],
           lambda S: ((("W", Array(S.N, Array(S.K, V16))), ("seed", V32), ("ctrs", Array(S.N, Array(S.K, V32))), ("coef", V32)),
                      Array(S.N, Array(S.K, V16))))
def EsUpdate(B, S, W, seed, ctrs, coef):
    """``W + coef * eps(seed)``: fold one population member's reward-weighted noise into the weights."""
    noise = B.batch(bind(NoiseRow, K=S.K), seed, ctrs, axes=(None, 0))
    return B.batch(bind(EsUpdateRow, K=S.K), W, noise, coef, axes=(0, 0, None))


__all__ = [n for n in dir() if n[:1].isupper() or n in ("transpose", "head_major", "matmul_gates", "matmul_macs", "rows")]
