"""Abstract arithmetic primitives for the training-circuit registry.

The bounded-accumulation analysis is about the *structure* of a circuit: which gates exist, what they
consume, how wide their values are, and how much work they represent.  It does not depend on the exact
floating-point semantics of any GPU.  We therefore register a small vocabulary of primitives with
simple, total, deterministic integer semantics (arithmetic modulo ``2**w``) and the same *shapes and
widths* as the B1 serving vocabulary (``verity_ir.registry.prims``):

* ``V16`` (``Value<16>``) plays the role of a BF16 operand/activation/weight;
* ``V32`` (``Value<32>``) plays the role of an FP32 accumulator / statistic / token id.

Every primitive carries a ``work`` attribute: the number of MAC-equivalent operations it stands for.
Gate work is what the ``F`` (upstream-work) rule and the accumulation-dependent-work resource count.

Swapping these primitives for the registered hardware-exact ones (``AmpereBF16TcDot16`` etc.) changes
only numerical semantics, never the operator graph the calculator analyses.  The ``Mac16`` primitive is
shaped exactly like ``AmpereBF16TcDot16`` (one accumulator transition over a 16-wide chunk).
"""

from __future__ import annotations

from verity_ir import Array, Value, primitive

V16 = Value(16)
V32 = Value(32)
A16 = Array(16, V16)
M16 = 0xFFFF
M32 = 0xFFFFFFFF


def _mark(p, work: int, family: str):
    p.work = work            # MAC-equivalent work of one gate
    p.family = family        # coarse role used by the operator-graph extractor
    return p


# --- multiply-accumulate -------------------------------------------------------------------------------

@primitive("AccMac16", 1, [("acc", V32), ("x", A16), ("w", A16)], V32, conformance="exact-model-tested")
def Mac16(acc: int, *xw: int) -> int:
    """acc + sum_{t<16} x[t]*w[t] (mod 2^32): one 16-wide accumulator transition (16 MACs).
    Array operands arrive flattened (x[0..16), w[0..16)), as for ``AmpereBF16TcDot16``."""
    s = acc
    for a, b in zip(xw[:16], xw[16:32]):
        s = (s + a * b) & M32
    return s


_mark(Mac16, 16, "mac")


@primitive("AccMac1", 1, [("acc", V32), ("x", V16), ("w", V16)], V32, conformance="exact-model-tested")
def Mac1(acc: int, x: int, w: int) -> int:
    """acc + x*w (mod 2^32): a scalar MAC (used by the tiny circuits the exact solver enumerates)."""
    return (acc + x * w) & M32


_mark(Mac1, 1, "mac")


@primitive("AccZero32", 1, [], V32, conformance="exact-model-tested")
def Zero32() -> int:
    return 0


_mark(Zero32, 0, "const")


@primitive("AccZero16", 1, [], V16, conformance="exact-model-tested")
def Zero16() -> int:
    return 0


_mark(Zero16, 0, "const")


@primitive("AccRound16", 1, [("a", V32)], V16, conformance="exact-model-tested")
def Round16(a: int) -> int:
    """32-bit accumulator -> 16-bit value (truncation stands in for RN rounding)."""
    return (a >> 16) & M16


_mark(Round16, 1, "cast")


@primitive("AccWiden32", 1, [("a", V16)], V32, conformance="exact-model-tested")
def Widen32(a: int) -> int:
    return a & M32


_mark(Widen32, 1, "cast")


# --- elementwise ----------------------------------------------------------------------------------------

@primitive("AccAdd16", 1, [("a", V16), ("b", V16)], V16, conformance="exact-model-tested")
def Add16(a: int, b: int) -> int:
    return (a + b) & M16


_mark(Add16, 1, "ew")


@primitive("AccSub16", 1, [("a", V16), ("b", V16)], V16, conformance="exact-model-tested")
def Sub16(a: int, b: int) -> int:
    return (a - b) & M16


_mark(Sub16, 1, "ew")


@primitive("AccMul16", 1, [("a", V16), ("b", V16)], V16, conformance="exact-model-tested")
def Mul16(a: int, b: int) -> int:
    return (a * b) & M16


_mark(Mul16, 1, "ew")


@primitive("AccScale16", 1, [("a", V16), ("s", V32)], V16, conformance="exact-model-tested")
def Scale16(a: int, s: int) -> int:
    """a * s with a 32-bit statistic (norm factor, softmax normaliser, learning rate...)."""
    return (a * (s & M16)) & M16


_mark(Scale16, 1, "ew")


@primitive("AccAdd32", 1, [("a", V32), ("b", V32)], V32, conformance="exact-model-tested")
def Add32(a: int, b: int) -> int:
    return (a + b) & M32


_mark(Add32, 1, "ew")


@primitive("AccSq32", 1, [("a", V16)], V32, conformance="exact-model-tested")
def Sq32(a: int) -> int:
    return (a * a) & M32


_mark(Sq32, 1, "ew")


@primitive("AccRsqrt32", 1, [("a", V32)], V32, conformance="exact-model-tested")
def Rsqrt32(a: int) -> int:
    """stand-in for rsqrt(mean + eps): total integer function."""
    return (M32 // (a | 1)) & M32


_mark(Rsqrt32, 1, "ew")


@primitive("AccSilu16", 1, [("g", V16), ("u", V16)], V16, conformance="exact-model-tested")
def SiluMul16(g: int, u: int) -> int:
    """silu(g) * u (integer stand-in)."""
    return ((g * u) ^ (g >> 1)) & M16


_mark(SiluMul16, 2, "ew")


@primitive("AccExp32", 1, [("a", V32), ("m", V32)], V32, conformance="exact-model-tested")
def ExpSub32(a: int, m: int) -> int:
    """exp(a - m) stand-in (softmax numerator)."""
    return ((a - m) * 0x9E3779B1) & M32


_mark(ExpSub32, 2, "ew")


@primitive("AccMax32", 1, [("a", V32), ("b", V32)], V32, conformance="exact-model-tested")
def Max32(a: int, b: int) -> int:
    return a if a >= b else b


_mark(Max32, 1, "ew")


@primitive("AccRcp32", 1, [("a", V32)], V32, conformance="exact-model-tested")
def Rcp32(a: int) -> int:
    return (M32 // (a | 1)) & M32


_mark(Rcp32, 1, "ew")


@primitive("AccMul32", 1, [("a", V32), ("b", V32)], V32, conformance="exact-model-tested")
def Mul32(a: int, b: int) -> int:
    return (a * b) & M32


_mark(Mul32, 1, "ew")


@primitive("AccRound16Scaled", 1, [("a", V32), ("s", V32)], V16, conformance="exact-model-tested")
def Round16Scaled(a: int, s: int) -> int:
    """(a * s) -> 16 bits: softmax normalisation / attention finalisation."""
    return (((a * s) & M32) >> 16) & M16


_mark(Round16Scaled, 1, "ew")


# --- gather / one-hot -----------------------------------------------------------------------------------

@primitive("AccSelect16", 1, [("tok", V32), ("idx", V32), ("a", V16), ("acc", V16)], V16,
           conformance="exact-model-tested")
def Select16(tok: int, idx: int, a: int, acc: int) -> int:
    """acc + [tok == idx] * a : one step of an embedding gather written as a select-accumulate scan."""
    return (acc + (a if tok == idx else 0)) & M16


_mark(Select16, 1, "gather")


@primitive("AccOneHotSub16", 1, [("p", V16), ("idx", V32), ("tgt", V32)], V16, conformance="exact-model-tested")
def OneHotSub16(p: int, idx: int, tgt: int) -> int:
    """p - [idx == tgt] : softmax probability minus the one-hot target, without materialising the one-hot."""
    return (p - (1 if idx == tgt else 0)) & M16


_mark(OneHotSub16, 1, "ew")


@primitive("AccConst32", 1, [], V32, conformance="exact-model-tested")
def Const32() -> int:
    return 0


_mark(Const32, 0, "const")


_GATHER: dict[int, object] = {}


def Gather16(V: int):
    """``col[tok]`` for a column of ``V`` 16-bit entries: one gate with fan-in ``V+1`` (the static circuit
    cannot index by a runtime value, so the gate reads the whole column; its *work* is that of a mux tree,
    ``ceil(log2 V)`` MAC-equivalents). Definitions are created lazily per ``V`` and cached."""
    if V not in _GATHER:
        def ev(tok: int, *col: int) -> int:
            return col[tok] if 0 <= tok < len(col) else 0

        p = primitive(f"AccGather16_{V}", 1, [("tok", V32), ("col", Array(V, V16))], V16,
                      doc=f"embedding gather over a {V}-entry column", conformance="exact-model-tested")(ev)
        _mark(p, max(1, (V - 1).bit_length()), "gather")
        _GATHER[V] = p
    return _GATHER[V]


# --- pseudo-randomness (evolution strategies) ------------------------------------------------------------

@primitive("AccHash32", 1, [("seed", V32), ("ctr", V32)], V32, conformance="exact-model-tested")
def Hash32(seed: int, ctr: int) -> int:
    """counter-based PRNG step (stand-in for a Philox/Threefry round)."""
    x = (seed ^ (ctr * 0x9E3779B1)) & M32
    x = ((x ^ (x >> 16)) * 0x85EBCA6B) & M32
    return (x ^ (x >> 13)) & M32


_mark(Hash32, 8, "prng")


@primitive("AccPerturb16", 1, [("w", V16), ("noise", V32), ("sigma", V32)], V16, conformance="exact-model-tested")
def Perturb16(w: int, noise: int, sigma: int) -> int:
    """w + sigma * eps(noise) : perturbed weight coordinate."""
    return (w + ((noise & M16) * (sigma & M16))) & M16


_mark(Perturb16, 2, "ew")


@primitive("AccEsUpdate16", 1, [("w", V16), ("noise", V32), ("coef", V32)], V16, conformance="exact-model-tested")
def EsUpdate16(w: int, noise: int, coef: int) -> int:
    """w + coef * eps(noise): one population member's contribution to an ES update."""
    return (w + ((noise & M16) * (coef & M16))) & M16


_mark(EsUpdate16, 2, "ew")


__all__ = [n for n in dir() if n[:1].isupper()]
