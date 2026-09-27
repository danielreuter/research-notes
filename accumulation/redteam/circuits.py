"""Declarative micro Verity programs for the red team.

A :class:`Circuit` is a list of root parameters (:class:`Param`: shape, role, width) and a list of ops
(:class:`Op`: block kind + operand references).  :func:`build` lowers it with the same ``_build`` helper the
exact-solver micro suite uses (:mod:`accumulation.exact.micro`), with ``CH=1`` so every ``MatmulT`` expands
to scalar ``Mac1`` chains the exact solver can enumerate.

Operand references are tuples ``("p", name)`` (root parameter) or ``("o", i)`` (output of op ``i``),
optionally followed by a *view* that is a pure reference rearrangement (no gates):

* ``("rows", lo, hi)`` -- rows ``lo:hi`` of a 2-D tensor;
* ``("reprow", i, n)`` -- row ``i`` repeated ``n`` times (an ``n x cols`` tensor reading one row);
* ``("as2d",)`` -- a 1-D ``(K,)`` tensor viewed as ``(1, K)``.

Shapes are ``()`` (scalar), ``(n,)`` or ``(rows, cols)``; widths 16 (``V16``) or 32 (``V32``: token ids,
learning rate, seeds, hash counters).

Kinds and shape rules (block in :mod:`accumulation.ir.blocks` in brackets)::

    matmul     A (M,K), B (N,K)              -> (M,N)   [AccMatmulT]     M*N*(K+2) gates, work M*N*(K+1)
    matmul_tt  At (K,M), Bt (K,N)            -> (M,N)   [AccMatmulTT]    same gates (transposes are views)
    add | mul  (Q,K), (Q,K)                  -> (Q,K)   [AccAddBatch | AccMulBatch]   Q*K gates
    swiglu     (Q,FF), (Q,FF)                -> (Q,FF)  [AccSwiGluBatch] Q*FF gates, work 2 each
    gain       (Q,K), (K,)                   -> (Q,K)   [AccGainBatch]   Q*K gates
    rowscale   (Q,K), (Q,)                   -> (Q,K)   [AccRowScaleBatch] Q*K gates
    rmsnorm    (Q,K), (K,)                   -> (Q,K)   [AccRmsNormBatch] Q*(4K+2) gates
    softmax    (Q,K)                         -> (Q,K)   [AccSoftmaxBatch] Q*(6K+2) gates
    colsum     (Q,K)                         -> (K,)    [AccColSumBatch]  K*(2Q+2) gates
    embed      toks (Q,)@32, tableT (D,V)    -> (Q,D)   [AccEmbedBatch]   Q*D gates, work ceil(log2 V)
    sgd        W (N,K), G (N,K), lr ()@32    -> (N,K)   [AccSgdUpdate]    2*N*K gates
    perturb    W (N,K), seed ()@32, ctrs (N,K)@32, sigma ()@32 -> (N,K) [AccPerturb] 2*N*K gates
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from verity_ir import Array, bind
from verity_ir.refs import array_of, tuple_of

from accumulation.algorithms.registry import BuiltProgram
from accumulation.exact.micro import _build, _mm
from accumulation.ir import blocks as K
from accumulation.ir.prims import V16, V32

ROLES = ("fixed", "accumulated", "carried", "token", "seed")
KINDS = ("matmul", "matmul_tt", "add", "mul", "swiglu", "gain", "rowscale", "rmsnorm", "softmax", "colsum",
         "embed", "sgd", "perturb")


@dataclass(frozen=True)
class Param:
    name: str
    shape: tuple[int, ...]
    role: str
    width: int = 16

    def __post_init__(self):
        assert self.role in ROLES, self.role
        assert self.width in (16, 32)
        assert 0 <= len(self.shape) <= 2 and all(int(s) >= 1 for s in self.shape), self.shape

    @property
    def leaves(self) -> int:
        return math.prod(self.shape) if self.shape else 1

    @property
    def bytes(self) -> int:
        return self.leaves * self.width // 8

    @property
    def charged(self) -> bool:
        return self.role != "fixed"


@dataclass(frozen=True)
class Op:
    kind: str
    args: tuple[tuple, ...]
    name: str = ""

    def __post_init__(self):
        assert self.kind in KINDS, self.kind


@dataclass
class Circuit:
    params: list[Param]
    ops: list[Op]
    name: str = "redteam"
    notes: dict = field(default_factory=dict)

    # -- helpers ------------------------------------------------------------------------------------------
    def param(self, name: str) -> Param:
        for p in self.params:
            if p.name == name:
                return p
        raise KeyError(name)

    def roles(self) -> dict[str, str]:
        return {p.name: p.role for p in self.params}

    def shapes(self) -> list[tuple[int, ...]]:
        """Output shape of every op (validates the circuit)."""
        out: list[tuple[int, ...]] = []
        for i, o in enumerate(self.ops):
            shp = [self._ref_shape(r, out) for r in o.args]
            out.append(_out_shape(o.kind, shp, i))
        return out

    def _ref_shape(self, ref: tuple, done: list[tuple[int, ...]]) -> tuple[int, ...]:
        base = self.param(ref[1]).shape if ref[0] == "p" else done[ref[1]]
        if ref[0] == "o":
            assert ref[1] < len(done), f"forward reference {ref}"
        return _view_shape(base, ref[2:] if len(ref) > 2 else ())

    def n_gates(self) -> int:
        tot = 0
        shapes = self.shapes()
        for i, o in enumerate(self.ops):
            shp = [self._ref_shape(r, shapes) for r in o.args]
            tot += _gates(o.kind, shp)
        return tot

    def sinks(self) -> list[int]:
        used = {r[1] for o in self.ops for r in o.args if r[0] == "o"}
        return [i for i in range(len(self.ops)) if i not in used]

    def to_python(self, var: str = "circ") -> str:
        lines = ["from accumulation.redteam.circuits import Circuit, Param, Op", f"{var} = Circuit(", "    params=["]
        for p in self.params:
            lines.append(f"        Param({p.name!r}, {p.shape!r}, {p.role!r}" + (f", width={p.width}" if p.width != 16 else "") + "),")
        lines.append("    ],")
        lines.append("    ops=[")
        for i, o in enumerate(self.ops):
            lines.append(f"        Op({o.kind!r}, {o.args!r}),  # {i}")
        lines.append("    ],")
        lines.append(f"    name={self.name!r},")
        lines.append(")")
        return "\n".join(lines)


def _view_shape(base: tuple[int, ...], view: tuple) -> tuple[int, ...]:
    if not view:
        return base
    v = view[0]
    if v == "rows":
        _, lo, hi = view
        assert len(base) == 2 and 0 <= lo < hi <= base[0], (base, view)
        return (hi - lo, base[1])
    if v == "reprow":
        _, i, n = view
        assert len(base) == 2 and 0 <= i < base[0] and n >= 1, (base, view)
        return (n, base[1])
    if v == "as2d":
        assert len(base) == 1, (base, view)
        return (1, base[0])
    raise ValueError(view)


def _out_shape(kind: str, shp: list[tuple[int, ...]], i: int) -> tuple[int, ...]:
    def two(a, b, what):
        assert len(a) == 2 and a == b, f"op {i} {kind}: {what} shapes {a} vs {b}"

    if kind == "matmul":
        (M, Ka), (N, Kb) = shp
        assert Ka == Kb, f"op {i} matmul contraction {Ka} != {Kb}"
        return (M, N)
    if kind == "matmul_tt":
        (Ka, M), (Kb, N) = shp
        assert Ka == Kb, f"op {i} matmul_tt contraction {Ka} != {Kb}"
        return (M, N)
    if kind in ("add", "mul", "swiglu"):
        two(shp[0], shp[1], kind)
        return shp[0]
    if kind in ("gain", "rmsnorm"):
        assert len(shp[0]) == 2 and shp[1] == (shp[0][1],), f"op {i} {kind}: {shp}"
        return shp[0]
    if kind == "rowscale":
        assert len(shp[0]) == 2 and shp[1] == (shp[0][0],), f"op {i} rowscale: {shp}"
        return shp[0]
    if kind == "softmax":
        assert len(shp[0]) == 2, f"op {i} softmax: {shp}"
        return shp[0]
    if kind == "colsum":
        assert len(shp[0]) == 2, f"op {i} colsum: {shp}"
        return (shp[0][1],)
    if kind == "embed":
        (Q,), (D, V) = shp
        return (Q, D)
    if kind == "sgd":
        two(shp[0], shp[1], "sgd")
        assert shp[2] == (), f"op {i} sgd lr must be scalar"
        return shp[0]
    if kind == "perturb":
        assert len(shp[0]) == 2 and shp[1] == () and shp[2] == shp[0] and shp[3] == (), f"op {i} perturb: {shp}"
        return shp[0]
    raise ValueError(kind)


def _gates(kind: str, shp: list[tuple[int, ...]]) -> int:
    if kind == "matmul":
        (M, Kd), (N, _) = shp
        return M * N * (Kd + 2)
    if kind == "matmul_tt":
        (Kd, M), (_, N) = shp
        return M * N * (Kd + 2)
    if kind in ("add", "mul", "swiglu", "gain", "rowscale"):
        return shp[0][0] * shp[0][1]
    if kind == "rmsnorm":
        return shp[0][0] * (4 * shp[0][1] + 2)
    if kind == "softmax":
        return shp[0][0] * (6 * shp[0][1] + 2)
    if kind == "colsum":
        return shp[0][1] * (2 * shp[0][0] + 2)
    if kind == "embed":
        (Q,), (D, _) = shp
        return Q * D
    if kind in ("sgd", "perturb"):
        return 2 * shp[0][0] * shp[0][1]
    raise ValueError(kind)


def _type(shape: tuple[int, ...], width: int):
    v = V16 if width == 16 else V32
    if not shape:
        return v
    if len(shape) == 1:
        return Array(shape[0], v)
    return Array(shape[0], Array(shape[1], v))


def _apply_view(c, view: tuple):
    if not view:
        return c
    v = view[0]
    if v == "rows":
        return c[view[1]:view[2]]
    if v == "reprow":
        return array_of([c[view[1]]] * view[2])
    if v == "as2d":
        return c.reshape(Array(1, c.type))
    raise ValueError(view)


def _block(kind: str, shp: list[tuple[int, ...]]):
    if kind == "matmul":
        (M, Kd), (N, _) = shp
        return _mm(M, N, Kd)
    if kind == "matmul_tt":
        (Kd, M), (_, N) = shp
        return bind(K.MatmulTT, M=M, N=N, K=Kd, CH=1)
    Q, Kc = shp[0] if len(shp[0]) == 2 else (None, None)
    if kind == "add":
        return bind(K.AddBatch, Q=Q, K=Kc)
    if kind == "mul":
        return bind(K.MulBatch, Q=Q, K=Kc)
    if kind == "swiglu":
        return bind(K.SwiGluBatch, Q=Q, FF=Kc)
    if kind == "gain":
        return bind(K.GainBatch, Q=Q, K=Kc)
    if kind == "rowscale":
        return bind(K.RowScaleBatch, Q=Q, K=Kc)
    if kind == "rmsnorm":
        return bind(K.RmsNormBatch, Q=Q, K=Kc)
    if kind == "softmax":
        return bind(K.SoftmaxBatch, Q=Q, K=Kc)
    if kind == "colsum":
        return bind(K.ColSumBatch, Q=Q, K=Kc)
    if kind == "embed":
        (Qe,), (D, V) = shp
        return bind(K.EmbedBatch, Q=Qe, V=V, D=D)
    if kind == "sgd":
        return bind(K.SgdUpdate, N=Q, K=Kc)
    if kind == "perturb":
        return bind(K.Perturb, N=Q, K=Kc)
    raise ValueError(kind)


def build(circ: Circuit) -> BuiltProgram:
    """Lower a :class:`Circuit` to a :class:`BuiltProgram` (roles attached, ``CH=1``)."""
    shapes = circ.shapes()
    params = tuple((p.name, _type(p.shape, p.width)) for p in circ.params)
    sinks = circ.sinks()
    out_types = [_type(shapes[i], 16) for i in sinks]
    ret = out_types[0] if len(sinks) == 1 else __import__("verity_ir").Tuple(*out_types)
    idx = {p.name: i for i, p in enumerate(circ.params)}

    def body(B, *args):
        outs: list[Any] = []
        for i, o in enumerate(circ.ops):
            colls = []
            shp = []
            for r in o.args:
                base = args[idx[r[1]]] if r[0] == "p" else outs[r[1]]
                view = r[2:] if len(r) > 2 else ()
                c = _apply_view(base, view)
                colls.append(c)
                shp.append(circ._ref_shape(r, shapes))
            outs.append(B.call(_block(o.kind, shp), *colls))
        if len(sinks) == 1:
            return outs[sinks[0]]
        return tuple_of(*(outs[i] for i in sinks))

    bp = _build(circ.name, params, circ.roles(), body, ret, 1, dict(circ.notes))
    return bp


__all__ = ["Circuit", "Param", "Op", "build", "KINDS", "ROLES"]
