"""Constructive upper bound ``U(P; F, X)``: an explicit legal partition of the operator graph into replay
units (RUs) and its honest input cost (SPEC §1, §3).

Construction
------------
Every RU is a *tile* of one op or of a small fused group of ops, described symbolically (a family of
identical RUs = one :class:`Unit` with a ``count``), never enumerated one by one.

* **Matmul tiles.**  A matmul ``C = A . B^T`` (``M x K`` operand ``A``, ``N x K`` operand ``B``, ``copies``
  independent copies) is covered per copy by a grid of rectangular tiles ``(a, b, k)``: ``a`` rows of
  ``A``, ``b`` rows of ``B`` and a contraction slab of ``k`` (a multiple of the chunk width ``CH``).  A
  tile RU imports its ``A`` block (``a*k`` elements at the tensor's width), its ``B`` block (``b*k``) and,
  when the contraction is split (``nk = ceil(K/k) > 1``), the partial accumulators.  Two reduction
  structures are used: ``chain`` (segment ``l`` imports the 32-bit accumulators of segment ``l-1``:
  ``4*a*b`` bytes per RU, ``4*(nk-1)`` bytes per output in total; this is literally a partition of the
  IR's ``MatmulT`` scan chains) and ``star`` (every segment emits a 32-bit partial as a free output and a
  separate *reduction RU* imports the ``nk`` partials of each output: ``4*nk`` bytes per output; needs
  add gates that are not in the IR, so it is only used when ``recompute=True``, see below).  The grid is
  chosen by a search over ``k`` (log grid + analytic optimum), the number of ``B`` blocks and the
  reduction mode, with ``a`` maximal under ``in(R) <= X``.  Fixed root parameters cost 0 bytes.
* **Operand sharing.**  Matmuls that read the *same view of the same tensor* as their ``A`` (or ``B``)
  operand -- e.g. the q/k/v projections reading the normalised residual, the three weight gradients
  reading ``xn^T``, or a LoRA base and adapter product reading the same input -- are tiled as one group:
  a tile imports the shared block once and one block of every other operand.  View identity is decided
  from the program's reference descriptors (``upper_bound(..., program=...)`` or ``g.program``); without
  the program no grouping is done (sound, looser).
* **Row-wise ops** (norm, add, mul, swiglu, softmax, loss-grad, gain, row-scale, SGD/ES updates, column
  sums) are tiled by rows so that imports fit ``X``; imports are the op's non-fixed inputs at their
  widths (per-row operands per row, per-op operands once per RU).  The embedding gather is tiled over
  (rows, columns): a gather gate reads a whole table column, so an RU importing ``d`` columns can serve
  any number of rows.  Ops with an unrecognised structure fall back to one RU per copy (or a few copies
  per RU), importing every non-fixed input of the copy -- always legal.
* **Attention fusion.**  The ``scores -> softmax -> P.V`` chain of ``AccAttnSeq`` is executed per
  (sequence, head) inside one RU that imports only the q/k/v head slices; the ``S x S`` score/probability
  matrices never cross an RU boundary.  The ``AccAttnSeqBwd`` chain (scores, softmax, dP, dS, dQ, dK, dV)
  is executed per (sequence, query head) importing q, k, v and dO head slices; the GQA contraction of
  dK/dV over the ``rep`` query heads sharing a KV head becomes a ``rep``-way partial-sum reduction.
  Both are literal partitions of the IR gates (no recomputation), except the ``star`` reduction of the
  dK/dV partials.  Query rows are split further when the slices do not fit ``X``.
* **Generation instead of import** (``recompute=True`` only).  An op-output tensor whose closure has
  only ``fixed | token | seed`` roots can be *regenerated inside the RU* instead of imported: the RU
  imports the non-fixed roots of the closure (token ids at 4 bytes, seeds) and pays the closure's total
  work ``Wc(t) = g.tensor_ancestor_work(t)`` toward ``F``.  The attention in this IR is *full* (no causal
  mask), so one row of a layer-``l`` activation depends on every position of every earlier layer; the
  whole closure is therefore charged for any row subset (no ``(i+1)/S`` discount -- that would be
  unsound here) and the tile then generates all ``M`` rows of the operand at once.

* **Epilogue fusion.**  An element-wise / row op (add, mul, gain, row-scale, scale, swiglu, SGD/ES
  updates; rms-norm, softmax, loss-grad when a tile holds complete output rows) that reads a matmul's
  output *in order* (verified on the program's reference descriptors, through ``call`` boundaries) is
  executed inside the RUs where those outputs are materialised -- the tile RUs when ``nk == 1``, the
  reduction RUs otherwise.  The fused op's other operands are imported per output position (or whole,
  for small per-op vectors); its output becomes a free RU output.  Operands that are themselves
  materialised in the same RU (``swiglu(gate, up)`` of a shared-``A`` group, the pair of a residual add)
  cost nothing.  A *sidecar* is a small-``K`` matmul (LoRA ``low . B^T``, or any matmul whose output is
  added to a host matmul's output on the same ``(row, col)`` blocks) computed inside the host's tiles on
  the same output blocks; its operand blocks are imported per row / per column (or are free when they
  are the host group's own outputs, e.g. LoRA's ``low = xn . A^T``).  Every fusion is re-optimised and
  accepted only if the fused tiles are not more expensive than tiles + standalone op.
* **Whole-op RUs.**  Finally, an exact DP over the topological sequence of op families merges consecutive
  families into single RUs that import each external tensor once whenever that fits ``X`` and ``F`` and
  is cheaper.  At realistic ``X`` nothing qualifies; on small graphs (or huge ``X``) the plan collapses to
  one RU whose cost is exactly the non-fixed root bytes, so ``U`` meets ``L_source``.

What remains loose: cross-layer fusion (next block's rms-norm reading the residual through a batch or
scan boundary), online-softmax attention when the k/v slices do not fit ``X``, and the reduction of
GQA dK/dV partials (a ``rep``-way star).  ``per_op`` attributes a family's bytes to its host matmuls
(fused ops show 0); ``by_class`` / ``by_kind`` aggregate ``per_op``.

Legality and accounting
-----------------------
* ``in(R) <= X``: every byte that enters an RU is counted: non-fixed root leaves (at their width) and
  outputs of gates outside the RU (activations at their width, partial accumulators at 4 bytes).
  Fixed roots are free; RU outputs are free.  Counting is per RU and per *position* (``a*k`` elements
  for an ``a x k`` block), which is >= the number of distinct leaves, so any repetition in a view only
  makes the bound looser.  A value read by two RUs is paid twice.
* ``F``: SPEC §1 bounds ``work(Up_R(gate))`` -- the work reachable *backwards from a gate inside R*.  In a
  matmul tile RU the only intra-RU wires are the accumulator chains, so for every gate
  ``Up_R(gate) <= k + 1`` (its chain segment plus the final rounding gate) plus whatever the RU generates
  or fuses upstream of the operands.  ``f_mode="upstream"`` (default) enforces exactly that certified
  bound; ``f_mode="work"`` enforces the cruder ``work(R) <= F`` on every RU (strictly more conservative;
  it is what the non-matmul RUs use in both modes).
* ``recompute``: with ``recompute=False`` the plan is a partition of the literal gate set of ``P``
  (chain reductions, no generation, no star reductions), i.e. exactly the object of SPEC §1 and of the
  exact solver.  With ``recompute=True`` (default) the adversary may evaluate an equivalent circuit
  (mod-2^32 accumulation is associative) that duplicates work; ``F`` is what prices the duplication.
* :func:`check_plan` re-derives every unit's imports / work / upstream bound from its symbolic
  description and the graph, checks ``<= X`` / ``<= F``, checks that every matmul's MACs (and every other
  op's work) are covered exactly once, and that every partial sum emitted is consumed by a reduction RU.

``kappa = ADW_matmul / U`` (MACs of accumulation-dependent matmuls per input byte) is reported alongside.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from itertools import product
from typing import Optional

from accumulation.bounds.adw import adw as _adw
from accumulation.graph.opgraph import Op, OpGraph
from verity_ir.refs import Affine

GAMMA = 4                                             # bytes of one 32-bit partial accumulator
GEN_ROLES = frozenset({"fixed", "token", "seed"})     # closures over these roots can be regenerated
F_MODES = ("upstream", "work")


def _ceil(a: int, b: int) -> int:
    return -(-a // b)


# ---------------------------------------------------------------------------------------------------------
# plan data model
# ---------------------------------------------------------------------------------------------------------

@dataclass
class Unit:
    """A family of ``count`` identical (up to ragged last blocks) replay units."""
    kind: str                      # tile | reduce | rows | embed | copies | attn-fwd | attn-bwd
    ops: tuple[int, ...]           # ops whose gates the RUs contain
    count: int                     # number of RUs in the family
    imports_max: int               # bytes entering ONE RU (worst block of the family)
    imports_total: int             # exact sum of imports over the family
    work_max: int                  # total gate work of one RU (incl. generation / fusion)
    up_max: int                    # certified bound on max_gate work(Up_R(gate)) in one RU
    covers: dict[int, int]         # op -> MACs (matmul) / work (other kinds) covered by the whole family
    partial_out: dict[int, int] = field(default_factory=dict)  # op -> partial-sum elements emitted (family)
    partial_in: dict[int, int] = field(default_factory=dict)   # op -> partial-sum elements consumed (family)
    detail: dict = field(default_factory=dict)


@dataclass
class Plan:
    units: list[Unit]
    F: int
    X: int
    recompute: bool
    f_mode: str
    notes: list[str] = field(default_factory=list)
    G: Optional[int] = None          # total work per RU (None = unbounded)

    @property
    def total(self) -> int:
        return sum(u.imports_total for u in self.units)

    @property
    def n_units(self) -> int:
        return sum(u.count for u in self.units)

    def ru_stats(self) -> dict:
        """RU-count diagnostics of the partition (THEORY §0 table): number of RUs, mean/max runtime input per
        RU, mean (upper estimate: every block charged its family's worst block) and max work per RU."""
        n = self.n_units
        return dict(n_ru=n,
                    input_mean=self.total / n if n else 0.0,
                    input_max=max((u.imports_max for u in self.units), default=0),
                    work_mean=sum(u.count * u.work_max for u in self.units) / n if n else 0.0,
                    work_max=max((u.work_max for u in self.units), default=0),
                    up_max=max((u.up_max for u in self.units), default=0))


@dataclass
class UpperBound:
    total: int
    n_units: int
    per_op: dict[int, int]
    plan: Plan
    notes: list[str]
    kappa: float = 0.0
    adw_matmul_macs: int = 0
    by_kind: dict[str, int] = field(default_factory=dict)    # op kind -> bytes
    by_class: dict[str, int] = field(default_factory=dict)   # matmul-fwd / matmul-dgrad / matmul-wgrad / attention / other


# ---------------------------------------------------------------------------------------------------------
# graph-side cost model
# ---------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class _Operand:
    tid: int
    elems_bytes: int      # bytes per element when imported (0 for fixed roots)
    gen: bool             # may be regenerated inside an RU
    gw: int               # generation work (closure work, all copies)
    gb: int               # bytes of non-fixed roots that generation imports


INF_WORK = 1 << 62                                    # "no total-work cap" (G=None)


class _Ctx:
    def __init__(self, g: OpGraph, F: int, X: int, recompute: bool, f_mode: str, program, G=None) -> None:
        self.g, self.F, self.X, self.recompute, self.f_mode, self.program = g, F, X, recompute, f_mode, program
        self.G = INF_WORK if G is None else int(G)    # total work per RU (SPEC: Work(R) <= G), INF_WORK = none
        # cap used wherever a family is sized by *total* work per RU (row/embed/copies/attention tiles treat F
        # as a total-work cap already, which is conservative under f_mode="upstream")
        self.W = min(self.F, self.G)
        self._roots: dict[int, frozenset[int]] = {}
        self._anc_ready = False
        self._tile_memo: dict = {}
        self._view_memo: dict = {}

    # -- tensors ------------------------------------------------------------------------------------------
    def width_bytes(self, tid: int) -> int:
        return _ceil(self.g.tensors[tid].width, 8)

    def import_cost(self, tid: int) -> int:
        """bytes per element when the tensor is imported into an RU (0 for fixed root parameters)."""
        t = self.g.tensors[tid]
        if t.kind == "param" and (t.role or "fixed") == "fixed":
            return 0
        return self.width_bytes(tid)

    def roots(self, tid: int) -> frozenset[int]:
        """root parameter tensor ids in the closure of ``tid`` (iterative, memoised)."""
        memo = self._roots
        if tid in memo:
            return memo[tid]
        g = self.g
        stack = [tid]
        while stack:
            t = stack[-1]
            if t in memo:
                stack.pop()
                continue
            tt = g.tensors[t]
            if tt.kind == "param":
                memo[t] = frozenset([t])
                stack.pop()
                continue
            srcs = [e.src for e in g.ops[tt.producer].inputs]
            pending = [s for s in srcs if s not in memo]
            if pending:
                stack.extend(pending)
                continue
            acc: set[int] = set()
            for s in srcs:
                acc |= memo[s]
            memo[t] = frozenset(acc)
            stack.pop()
        return memo[tid]

    def gen_ok(self, tid: int) -> bool:
        t = self.g.tensors[tid]
        if not self.recompute or t.kind != "op":
            return False
        return all((self.g.tensors[r].role or "fixed") in GEN_ROLES for r in self.roots(tid))

    def gen_bytes(self, tid: int) -> int:
        return sum(self.g.tensors[r].bytes for r in self.roots(tid) if (self.g.tensors[r].role or "fixed") != "fixed")

    def gen_work(self, tid: int) -> int:
        if not self._anc_ready:
            # fill the graph's ancestor memo in id order (ids are topological) so recursion stays shallow
            for o in self.g.ops:
                self.g.ancestors(o.id)
            self._anc_ready = True
        return self.g.tensor_ancestor_work(tid)

    def operand(self, tid: int) -> _Operand:
        gen = self.gen_ok(tid)
        return _Operand(tid, self.import_cost(tid), gen, self.gen_work(tid) if gen else 0,
                        self.gen_bytes(tid) if gen else 0)

    # -- program views --------------------------------------------------------------------------------------
    def view_key(self, op: Op, arg: int):
        """Identity of the leaf view read by argument ``arg`` of ``op`` (None without the program)."""
        if self.program is None:
            return None
        key = (op.id, arg)
        if key in self._view_memo:
            return self._view_memo[key]
        try:
            fn = self.program.fn
            for p in op.key[0]:
                fn = fn.body.nodes[p].fn
            node = fn.body.nodes[op.key[1]]
            res = (op.key[0], json.dumps(node.args[arg].refs.to_json(), sort_keys=True))
        except Exception:  # pragma: no cover - defensive: unknown program layout -> no grouping
            res = None
        self._view_memo[key] = res
        return res

    def _fn(self, path: tuple):
        fn = self.program.fn
        for p in path:
            fn = fn.body.nodes[p].fn
        return fn

    def _node(self, op: Op):
        return self._fn(op.key[0]).body.nodes[op.key[1]]

    def _resolve(self, path: tuple, refs):
        """Follow an affine reference through plain ``call`` boundaries (parameters upwards, returns
        downwards, slicing as needed) until it lands on an op of the graph.  Returns ``(op_key, base, count)``
        or None when the view is not a contiguous in-order window of one op's output."""
        if not hasattr(self, "_op_keys"):
            self._op_keys = {o.key for o in self.g.ops}
        for _ in range(32):
            if not isinstance(refs, Affine) or refs.count <= 0:
                return None
            if refs.space == "p":
                if not path:
                    return None
                call = self._fn(path[:-1]).body.nodes[path[-1]]
                if call.form != "call":
                    return None
                refs = call.args[refs.idx].refs.slice(refs.base, refs.base + refs.count)
                path = path[:-1]
                continue
            if refs.space == "n":
                key = (path, refs.idx)
                if key in self._op_keys:
                    return key, refs.base, refs.count
                node = self._fn(path).body.nodes[refs.idx]
                if node.form != "call":
                    return None
                path = path + (refs.idx,)
                refs = node.fn.body.ret.slice(refs.base, refs.base + refs.count)
                continue
            return None
        return None

    def identity_view(self, c: Op, arg: int, producer: Op) -> bool:
        """True iff argument ``arg`` of ``c`` reads the whole output of ``producer`` in order (element ``j``
        of the argument is leaf ``j`` of the producer's output), possibly through call boundaries.  False
        without the program."""
        if self.program is None:
            return False
        try:
            r = self._resolve(c.key[0], self._node(c).args[arg].refs)
            return r == (producer.key, 0, self._node(producer).out.leaves)
        except Exception:  # pragma: no cover - defensive
            return False

    # -- F rule -------------------------------------------------------------------------------------------
    def up_of(self, up_struct: int, work: int) -> int:
        return up_struct if self.f_mode == "upstream" else work


# ---------------------------------------------------------------------------------------------------------
# matmul tiles
# ---------------------------------------------------------------------------------------------------------

def _log_grid(lo: int, hi: int, ratio: float) -> list[int]:
    out = []
    v = lo
    while v < hi:
        out.append(v)
        v = max(v + 1, int(v * ratio))
    out.append(hi)
    return out


_EW_KINDS = frozenset({"add", "mul", "gain", "rowscale", "scale", "swiglu", "sgdupdate", "esupdate", "perturb"})
_ROWFULL_KINDS = frozenset({"rmsnorm", "softmax", "lossgrad"})


@dataclass(frozen=True)
class _Fus:
    """Epilogue / sidecar parameters of a tile family (derived from the graph by :func:`_fus_params`).

    ``eps[i]``: imported bytes per output position of segment ``i`` (per-element operands of fused ops);
    ``fixed``: bytes per RU holding complete outputs (whole small vectors of fused ops); ``wpp[i]``: extra
    work per output position of segment ``i``; ``rowfull[i]``: segment ``i`` must materialise complete
    output rows (``b_i == R_i``, ``nk == 1``); ``side_row`` / ``side_col[i]``: sidecar operand bytes per
    shared row / per segment-``i`` row; ``joint``: a fused op needs the same position of several segments
    inside one RU."""
    eps: tuple[int, ...]
    fixed: int
    wpp: tuple[int, ...]
    rowfull: tuple[bool, ...]
    side_row: int
    side_col: tuple[int, ...]
    has_side: bool
    joint: bool

    @property
    def any(self) -> bool:
        return bool(any(self.eps) or self.fixed or any(self.wpp) or any(self.rowfull) or self.has_side)


def _no_fus(n: int) -> _Fus:
    return _Fus((0,) * n, 0, (0,) * n, (False,) * n, 0, (0,) * n, False, False)


def _tile_eval(Rs, K, CH, extra, sig, rho, tok, gw, segR, X, F, f_mode, mode, k, c, fus: _Fus, gamma=GAMMA,
               G=INF_WORK):
    """Evaluate one grid choice; returns (cost_per_copy, sol) or None if infeasible.

    ``sig``: import bytes/elem of the shared operand (0 if generated/fixed); ``rho[i]`` for segment i;
    ``tok``/``gw``: per-RU bytes/work of generation; ``segR[i]``: rows of segment i; ``fus``: fused
    epilogue / sidecar parameters (see :class:`_Fus`).  Complete outputs materialise in the tile RU when
    ``nk == 1`` and in the reduction RU otherwise (star); fused ops live where the outputs are."""
    nk = _ceil(K, k)
    bs = [_ceil(R, c) for R in segR]
    sumb = sum(bs)
    sumR = sum(segR)
    n = len(segR)
    fz = fus.any
    if fz:
        if nk > 1 and (mode == "chain" or fus.has_side or any(fus.rowfull)):
            return None
        if any(rf and b != R for rf, b, R in zip(fus.rowfull, bs, segR)):
            return None
        if fus.joint and (len(set(segR)) != 1):
            return None
    in_tile = nk == 1                      # complete outputs (and fused ops) live in the tile RUs
    sum_wpp = sum(fus.wpp)
    Bk = k * sum(r * b for r, b in zip(rho, bs)) + sum(s * b for s, b in zip(fus.side_col, bs))
    chain_part = (gamma * sumb) if (mode == "chain" and nk > 1) else 0
    epi_a = sum(e * b for e, b in zip(fus.eps, bs)) if in_tile else 0
    fx = tok + (fus.fixed if in_tile else 0)
    red = None
    if mode == "star" and nk > 1:
        joint = fz and fus.joint
        pp = (n * gamma * nk + sum(fus.eps)) if joint else (gamma * nk + max(fus.eps))
        red_wpp = sum_wpp
        if pp + fus.fixed > X or nk + red_wpp > F or nk + red_wpp > G:
            return None
        n_out = (X - fus.fixed) // pp
        if f_mode == "work":
            n_out = min(n_out, F // (nk + red_wpp))
        n_out = min(n_out, G // (nk + red_wpp))
        if n_out < 1:
            return None
        n_pos = Rs * (segR[0] if joint else sumR)                   # positions (or position tuples) per copy
        red_total = gamma * nk * Rs * sumR + sum(e * Rs * R for e, R in zip(fus.eps, segR)) + _ceil(n_pos, n_out) * fus.fixed
        red = dict(pp=pp, n_out=n_out, joint=joint, n_pos_pc=n_pos, total_pc=red_total, wpp=red_wpp)
    up_struct = k + extra + gw + (sum_wpp if in_tile else 0)
    if f_mode == "upstream" and up_struct > F:
        return None
    rem = X - Bk - fx
    if rem < 0:
        return None
    denom = sig * k + fus.side_row + chain_part + epi_a
    a = Rs if denom == 0 else min(Rs, rem // denom)
    if a < 1:
        return None
    w_row = sumb * (k + extra) + (sum(w * b for w, b in zip(fus.wpp, bs)) if in_tile else 0)
    wcap = min(G, F if f_mode == "work" else INF_WORK)          # total-work cap on the tile RU
    if wcap < INF_WORK:
        if gw > wcap:
            return None
        cap = (wcap - gw) // w_row if w_row > 0 else Rs
        a = min(a, cap)
        if a < 1:
            return None
    n_s = _ceil(Rs, a)
    imports_max = sig * a * k + fus.side_row * a + Bk + fx + chain_part * a + epi_a * a
    if imports_max > X:
        return None
    work_max = a * w_row + gw
    cost = (sig * Rs * K * c + n_s * K * sum(r * R for r, R in zip(rho, segR)) + n_s * c * nk * tok
            + Rs * c * fus.side_row + n_s * sum(s * R for s, R in zip(fus.side_col, segR)))
    if in_tile:
        cost += sum(e * Rs * R for e, R in zip(fus.eps, segR)) + n_s * c * fus.fixed
    if nk > 1:
        cost += gamma * (nk - 1) * Rs * sumR if mode == "chain" else red["total_pc"]
    sol = dict(mode=mode, k=k, nk=nk, a=a, n_s=n_s, c=c, bs=tuple(bs), imports_max=imports_max,
               work_max=work_max, up_max=up_struct if f_mode == "upstream" else work_max, count=n_s * c * nk,
               cost=cost, red=red)
    return cost, sol


def _tile_search(ctx: _Ctx, Rs: int, shared: _Operand, segs: tuple[tuple[int, _Operand], ...], K: int,
                 CH: int, extra: int, copies: int, fus: _Fus):
    """Best tile grid for a (possibly grouped) matmul.  ``shared`` is the operand common to all ops of the
    group (``Rs`` rows); ``segs`` are ``(rows, operand)`` of the other operand of every op.  Returns the
    solution dict (per copy) or None when no legal tile exists."""
    X, F, f_mode = ctx.X, ctx.F, ctx.f_mode
    key = (Rs, shared, segs, K, CH, extra, X, F, f_mode, ctx.recompute, fus, ctx.G)
    if key in ctx._tile_memo:
        return ctx._tile_memo[key]
    segR = [R for R, _ in segs]
    modes = ("chain", "star") if ctx.recompute else ("chain",)
    gen_axes = [(False, True) if shared.gen else (False,)] + [(False, True) if o.gen else (False,) for _, o in segs]
    best = None
    kmax_units = K // CH if K % CH == 0 else K
    CHe = CH if K % CH == 0 else 1
    k_grid = sorted({CHe * m for m in _log_grid(1, kmax_units, 1.5)})
    kstar = max(1, int(math.sqrt(max(X, 1) / 4.0) // CHe))
    k_grid = sorted(set(k_grid) | {CHe * kstar, min(K, CHe * (kstar + 1))})
    Rmax = max(segR)
    c_grid = _log_grid(1, Rmax, 1.4)

    def run(gens, modes_, kg, cg):
        nonlocal best
        gS = gens[0]
        sig = 0 if gS else shared.elems_bytes
        rho = [0 if gi else o.elems_bytes for gi, (_, o) in zip(gens[1:], segs)]
        tok = (shared.gb if gS else 0) + sum(o.gb for gi, (_, o) in zip(gens[1:], segs) if gi)
        gw = (shared.gw if gS else 0) + sum(o.gw for gi, (_, o) in zip(gens[1:], segs) if gi)
        for mode in modes_:
            for k in kg:
                if k < 1 or k > K:
                    continue
                for c in cg:
                    if c < 1 or c > Rmax:
                        continue
                    r = _tile_eval(Rs, K, CHe, extra, sig, rho, tok, gw, segR, X, F, f_mode, mode, k, c, fus, G=ctx.G)
                    if r is None:
                        continue
                    cost, sol = r
                    if best is None or (cost, sol["count"]) < (best[0], best[1]["count"]):
                        sol["gens"] = tuple(gens)
                        best = (cost, sol)

    for gens in product(*gen_axes):
        run(gens, modes, k_grid, c_grid)
    if best is not None:
        # local refinement around the coarse optimum
        _, s = best
        k0, c0 = s["k"], s["c"]
        kg = sorted({min(K, max(CHe, CHe * int(round(k0 / CHe * f)))) for f in _fine_factors()})
        cg = sorted({min(Rmax, max(1, int(round(c0 * f)))) for f in _fine_factors()})
        run(s["gens"], (s["mode"],), kg, cg)
    res = None if best is None else best[1]
    ctx._tile_memo[key] = res
    return res


def _fine_factors():
    return [0.6, 0.7, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.3, 1.45, 1.6]


def _matmul_shape(op: Op) -> tuple[int, int, int, int, int]:
    s = op.statics
    M, N, K = int(s["M"]), int(s["N"]), int(s["K"])
    CH = int(s.get("CH", 1))
    wpo = _ceil(op.work_per_copy, M * N)
    extra = max(0, wpo - K)
    return M, N, K, CH, extra


def _attn_square(sc: Op, pv: Op) -> bool:
    """True when the attention pattern is square: the score matmul has as many key rows (``N``) as query rows
    (``M``) and the PV contraction runs over those keys.  The fused attention units size the K/V slice and the
    per-row work by the query count, which is only sound in this case (decode attention has ``T`` queries
    against ``S`` cached keys and would under-count the cache import by ``S/T``)."""
    Msc, Nsc, _, _, _ = _matmul_shape(sc)
    _, _, Kpv, _, _ = _matmul_shape(pv)
    return Msc == Nsc == Kpv


def _matmul_operand_tids(op: Op) -> tuple[int, int]:
    if len(op.inputs) == 2:
        return op.inputs[0].src, op.inputs[1].src
    if len(op.inputs) == 1:            # A and B are views of the same tensor
        return op.inputs[0].src, op.inputs[0].src
    raise ValueError(f"matmul op {op.id} has {len(op.inputs)} input edges")


def _group_geometry(ctx: _Ctx, ops: list[Op], shared_role: str):
    """``(Rs, shared_tid, segR, seg_tids, K, CH, extra, copies)`` of a matmul group."""
    M0, N0, K, CH, _ = _matmul_shape(ops[0])
    copies = ops[0].copies
    a_t, b_t = _matmul_operand_tids(ops[0])
    if shared_role == "A":
        Rs, shared_tid = M0, a_t
        segR = tuple(_matmul_shape(o)[1] for o in ops)
        seg_tids = tuple(_matmul_operand_tids(o)[1] for o in ops)
    else:
        Rs, shared_tid = N0, b_t
        segR = tuple(_matmul_shape(o)[0] for o in ops)
        seg_tids = tuple(_matmul_operand_tids(o)[0] for o in ops)
    extra = max(_matmul_shape(o)[4] for o in ops)
    return Rs, shared_tid, segR, seg_tids, K, CH if K % CH == 0 else 1, extra, copies


def _fus_params(ctx: _Ctx, ops: list[Op], shared_role: str, Rs: int, segR: tuple[int, ...], copies: int,
                steps: tuple) -> tuple[_Fus, dict[int, tuple[str, int]], list[int]]:
    """Derive the fusion parameters of ``steps`` from the graph, asserting every structural precondition.

    ``steps`` is a tuple of ``("side", op_id, seg)`` (a small-``K`` matmul computed on the same output blocks
    as segment ``seg``) and ``("ew", op_id, seg, rowfull)`` (a row-model op whose materialised inputs are
    read element-wise).  Returns ``(fus, covers, materialised)`` where ``covers[op] = (where, amount)``
    with ``where`` in ``{"tile", "pos"}`` (``"pos"``: wherever complete outputs live)."""
    g = ctx.g
    n = len(ops)
    pos = [Rs * R * copies for R in segR]
    mat: dict[int, int] = {o.out: i for i, o in enumerate(ops)}     # tensor -> segment whose positions it has
    eps, wpp, side_col = [0] * n, [0] * n, [0] * n
    rowfull = [False] * n
    side_row = fixed = 0
    joint = has_side = False
    covers: dict[int, tuple[str, int]] = {}
    for st in steps:
        if st[0] == "side":
            _, oid, seg = st
            p2 = g.ops[oid]
            assert p2.kind == "matmul" and p2.copies == copies and oid not in covers, f"bad sidecar {oid}"
            M2, N2, K2, _, ex2 = _matmul_shape(p2)
            a2, b2 = _matmul_operand_tids(p2)
            s2, t2, Ms, Mt = (a2, b2, M2, N2) if shared_role in ("A", None) else (b2, a2, N2, M2)
            assert Ms == Rs and Mt == segR[seg], f"sidecar {oid} shape {(M2, N2)} does not match segment {seg}"
            if s2 in mat:
                j = mat[s2]
                assert j < n and segR[j] == K2, f"sidecar {oid}: materialised operand {s2} is not a full-row segment output"
                if ctx.program is not None:
                    assert ctx.identity_view(p2, 0, g.ops[g.tensors[s2].producer]), f"sidecar {oid} reads {s2} out of order"
                rowfull[j] = True
            else:
                side_row += K2 * ctx.import_cost(s2)
            assert t2 not in mat, f"sidecar {oid}: segment-row operand {t2} cannot be materialised"
            side_col[seg] += K2 * ctx.import_cost(t2)
            wpp[seg] += K2 + ex2
            has_side = True
            covers[oid] = ("tile", M2 * N2 * K2 * copies)
            mat[p2.out] = seg
        else:
            _, oid, seg, rf = st
            c = g.ops[oid]
            assert oid not in covers, f"op {oid} fused twice"
            rm = _row_model(c)
            assert rm is not None, f"fused op {oid} ({c.kind}) has no row model"
            rows_pc, edges = rm
            rows = rows_pc * c.copies
            P = pos[seg]
            assert rows > 0 and P % rows == 0, f"fused op {oid}: {rows} rows do not tile {P} positions"
            L = P // rows
            n_mat = 0
            for idx, (role_, lv, e) in enumerate(edges):
                if e.src in mat:
                    assert role_ == "row" and lv == L, f"fused op {oid} must read materialised tensor {e.src} element-wise"
                    if ctx.program is not None:
                        assert ctx.identity_view(c, idx, g.ops[g.tensors[e.src].producer]), \
                            f"fused op {oid} does not read tensor {e.src} in order"
                    if mat[e.src] != seg:
                        joint = True
                    n_mat += 1
                elif role_ == "row" and lv == L:
                    eps[seg] += ctx.import_cost(e.src)
                else:
                    fixed += g.tensors[e.src].leaves * ctx.import_cost(e.src)
            assert n_mat >= 1, f"fused op {oid} reads nothing materialised"
            if rf:
                assert c.kind in _ROWFULL_KINDS and shared_role in ("A", None) and L == segR[seg], \
                    f"fused op {oid} needs complete rows of segment {seg}"
                rowfull[seg] = True
            else:
                assert c.kind in _EW_KINDS, f"op kind {c.kind} is not element-wise fusable"
            wpp[seg] += _ceil(c.work, P)
            covers[oid] = ("pos", c.work)
            mat[c.out] = seg
    fus = _Fus(tuple(eps), fixed, tuple(wpp), tuple(rowfull), side_row, tuple(side_col), has_side, joint)
    return fus, covers, list(mat)


def _tile_units(ctx: _Ctx, ops: list[Op], shared_role: str, steps: tuple = ()) -> Optional[list[Unit]]:
    """Units for a group of matmuls sharing operand ``shared_role`` ('A' or 'B'); a single op is a group of
    one (the shared operand is then just its A).  ``steps``: fused epilogue / sidecar ops (see
    :func:`_fus_params`).  Returns None when no legal tile exists."""
    Rs, shared_tid, segR, seg_tids, K, CH, extra, copies = _group_geometry(ctx, ops, shared_role)
    shared = ctx.operand(shared_tid)
    segs = tuple((R, ctx.operand(t)) for R, t in zip(segR, seg_tids))
    fus, fcov, _ = _fus_params(ctx, ops, shared_role, Rs, segR, copies, steps)
    sol = _tile_search(ctx, Rs, shared, segs, K, CH, extra, copies, fus)
    if sol is None:
        return None
    sumR = sum(segR)
    in_tile = sol["nk"] == 1
    covers = {o.id: Rs * R * K * copies for o, R in zip(ops, segR)}
    red_cov = {}
    for oid, (where, amt) in fcov.items():
        (covers if (where == "tile" or in_tile) else red_cov)[oid] = amt
    detail = dict(shared_role=shared_role, shared_tid=shared_tid, seg_tids=seg_tids, Rs=Rs, segR=tuple(segR),
                  K=K, CH=CH, extra=extra, copies=copies, steps=tuple(steps),
                  **{k: sol[k] for k in ("mode", "k", "nk", "a", "n_s", "c", "bs", "gens")})
    units = [Unit(kind="tile", ops=tuple(o.id for o in ops), count=sol["count"] * copies,
                  imports_max=sol["imports_max"], imports_total=sol["cost"] * copies, work_max=sol["work_max"],
                  up_max=sol["up_max"], covers=covers, detail=detail)]
    if sol["mode"] == "star" and sol["nk"] > 1:
        nk, red = sol["nk"], sol["red"]
        partial = {o.id: nk * Rs * R * copies for o, R in zip(ops, segR)}
        units[0].partial_out = dict(partial)
        units[0].imports_total -= red["total_pc"] * copies          # reduction imports live in the reduce unit
        n_pos = red["n_pos_pc"] * copies
        count = _ceil(n_pos, red["n_out"])
        total = (GAMMA * nk * Rs * sumR + sum(e * Rs * R for e, R in zip(fus.eps, segR))) * copies + count * fus.fixed
        work = red["n_out"] * (nk + red["wpp"])
        units.append(Unit(kind="reduce", ops=tuple(o.id for o in ops), count=count,
                          imports_max=red["n_out"] * red["pp"] + fus.fixed, imports_total=total, work_max=work,
                          up_max=ctx.up_of(nk + red["wpp"], work), covers=red_cov, partial_in=partial,
                          detail=dict(nk=nk, n_out=red["n_out"], n_pos=n_pos, pp=red["pp"], joint=red["joint"],
                                      shared_role=shared_role, Rs=Rs, segR=tuple(segR), copies=copies,
                                      steps=tuple(steps))))
    return units


def _reduce_unit(ctx: _Ctx, ops: list[int], partial_in: dict[int, int], n_elems: int, nk: int) -> Unit:
    """Plain reduction RUs (no epilogue) summing ``nk`` 32-bit partials for each of ``n_elems`` outputs."""
    n_out = min(n_elems, ctx.X // (GAMMA * nk))
    if ctx.f_mode == "work":
        n_out = min(n_out, ctx.F // nk)
    n_out = min(n_out, ctx.G // nk)
    assert n_out >= 1
    count = _ceil(n_elems, n_out)
    return Unit(kind="reduce", ops=tuple(ops), count=count, imports_max=GAMMA * nk * n_out,
                imports_total=GAMMA * nk * n_elems, work_max=n_out * nk, up_max=ctx.up_of(nk, n_out * nk),
                covers={}, partial_in=dict(partial_in), detail=dict(nk=nk, n_out=n_out, n_elems=n_elems, plain=True))


def _reduce_unit_check(ctx: _Ctx, u: Unit):
    """Re-derivation of a reduce unit (see :func:`_rederive`)."""
    g = ctx.g
    d = u.detail
    if d.get("plain"):
        nk, n_out, n_elems = d["nk"], d["n_out"], d["n_elems"]
        assert ctx.recompute, "reduction RUs require recompute=True"
        assert sum(u.partial_in.values()) == nk * n_elems and u.count == _ceil(n_elems, n_out) and not u.covers
        return GAMMA * nk * n_out, GAMMA * nk * n_elems, n_out * nk, ctx.up_of(nk, n_out * nk)
    ops = [g.ops[i] for i in u.ops]
    nk, n_out, n_pos, pp, joint = d["nk"], d["n_out"], d["n_pos"], d["pp"], d["joint"]
    Rs, segR, copies = d["Rs"], d["segR"], d["copies"]
    assert ctx.recompute, "reduction RUs require recompute=True"
    fus, fcov, _ = _fus_params(ctx, ops, d["shared_role"], Rs, segR, copies, d["steps"])
    n = len(segR)
    sumR = sum(segR)
    exp_pp = (n * GAMMA * nk + sum(fus.eps)) if joint else (GAMMA * nk + max(fus.eps))
    assert pp >= exp_pp, "reduce unit: per-position bytes understated"
    if joint:
        assert len(set(segR)) == 1
    else:
        assert not fus.joint, "joint epilogue in a per-position reduction"
    assert n_pos == Rs * (segR[0] if joint else sumR) * copies and u.count == _ceil(n_pos, n_out)
    for o, R in zip(ops, segR):
        assert u.partial_in.get(o.id, 0) == nk * Rs * R * copies
    exp_cov = {oid: amt for oid, (where, amt) in fcov.items() if where == "pos"}
    assert u.covers == exp_cov, "reduce unit: fused-op coverage mismatch"
    total = (GAMMA * nk * Rs * sumR + sum(e * Rs * R for e, R in zip(fus.eps, segR))) * copies + u.count * fus.fixed
    work = n_out * (nk + sum(fus.wpp))
    return n_out * pp + fus.fixed, total, work, ctx.up_of(nk + sum(fus.wpp), work)



# ---------------------------------------------------------------------------------------------------------
# row-wise ops, embedding, generic fallback
# ---------------------------------------------------------------------------------------------------------

# kind -> (rows static, [(edge role, leaves static or int), ...]) in argument order (see accumulation/ir/blocks.py)
_ROW_MODELS: dict[str, tuple[str, list[tuple[str, object]]]] = {
    "rmsnorm": ("Q", [("row", "K"), ("shared", "K")]),
    "add": ("Q", [("row", "K"), ("row", "K")]),
    "mul": ("Q", [("row", "K"), ("row", "K")]),
    "swiglu": ("Q", [("row", "FF"), ("row", "FF")]),
    "scale": ("Q", [("row", "K"), ("shared", 1)]),
    "softmax": ("Q", [("row", "K")]),
    "lossgrad": ("Q", [("row", "V"), ("row", 1), ("shared", "V")]),
    "gain": ("Q", [("row", "K"), ("shared", "K")]),
    "rowscale": ("Q", [("row", "K"), ("row", 1)]),
    "sgdupdate": ("N", [("row", "K"), ("row", "K"), ("shared", 1)]),
    "perturb": ("N", [("row", "K"), ("shared", 1), ("row", "K"), ("shared", 1)]),
    "esupdate": ("N", [("row", "K"), ("shared", 1), ("row", "K"), ("shared", 1)]),
    "colsum": ("K", [("row", "Q")]),      # "rows" are the K output columns, each reading Q leaves
    "rowdot": ("Q", [("row", "K"), ("row", "K")]),
    "rowscalebroadcast": ("Q", [("shared", "K"), ("row", 1)]),
}


def _row_model(op: Op):
    """``(rows_per_copy, [(role, leaves, edge)])`` if the op matches its known row structure, else None."""
    m = _ROW_MODELS.get(op.kind)
    if m is None:
        return None
    rows_key, spec = m
    st = op.statics
    if rows_key not in st:
        return None
    rows = int(st[rows_key])
    if len(op.inputs) == 1 and len(spec) > 1 and all(role == "row" for role, _ in spec):
        # all row operands are views of one tensor (e.g. ``acc = t[a:b] + t[c:d]``): the extractor merges
        # them into a single edge whose leaves are the sum, so one "row" of the op reads the summed leaves
        if any(isinstance(lv, str) and lv not in st for _, lv in spec):
            return None
        leaves = sum(int(st[lv]) if isinstance(lv, str) else int(lv) for _, lv in spec)
        e = op.inputs[0]
        if e.leaves_per_copy != rows * leaves or rows <= 0 or op.work_per_copy % rows:
            return None
        return rows, [("row", leaves, e)]
    if len(op.inputs) != len(spec):
        return None
    out = []
    for (role, lv), e in zip(spec, op.inputs):
        if isinstance(lv, str) and lv not in st:
            return None
        leaves = int(st[lv]) if isinstance(lv, str) else int(lv)
        expect = rows * leaves if role == "row" else leaves
        if e.leaves_per_copy != expect:
            return None
        out.append((role, leaves, e))
    if rows <= 0 or op.work_per_copy % rows:
        return None
    return rows, out


def _rows_unit(ctx: _Ctx, op: Op) -> Unit:
    g = ctx.g
    rm = _row_model(op)
    if rm is None:
        return _copies_unit(ctx, op)
    rows_pc, edges = rm
    R = rows_pc * op.copies
    wpr = op.work_per_copy // rows_pc
    # generation options for row operands that are op outputs with a free closure
    gen_cands = [i for i, (role, _, e) in enumerate(edges) if role == "row" and ctx.gen_ok(e.src)]
    best = None
    for gens in product(*[(False, True)] * len(gen_cands)):
        gen_set = {gen_cands[i] for i, f in enumerate(gens) if f}
        row_bytes = shared_bytes = tok = gw = 0
        gen_tids = []
        for i, (role, leaves, e) in enumerate(edges):
            if i in gen_set:
                tok += ctx.gen_bytes(e.src)
                gw += ctx.gen_work(e.src)
                gen_tids.append(e.src)
                continue
            b = leaves * ctx.import_cost(e.src)
            if role == "row":
                row_bytes += b
            else:
                shared_bytes += b
        fixed = shared_bytes + tok
        if fixed > ctx.X or gw > ctx.W:
            continue
        r = R if row_bytes == 0 else min(R, (ctx.X - fixed) // row_bytes)
        if wpr > 0:
            r = min(r, (ctx.W - gw) // wpr)
        if r < 1:
            continue
        count = _ceil(R, r)
        total = R * row_bytes + count * fixed
        if best is None or total < best[0]:
            best = (total, r, count, row_bytes, fixed, gw, tuple(gen_tids))
    if best is None:
        raise ValueError(f"no legal row tile for op {op.id} ({op.kind} {op.statics}) under X={ctx.X}, F={ctx.F}")
    total, r, count, row_bytes, fixed, gw, gen_tids = best
    work = r * wpr + gw
    return Unit(kind="rows", ops=(op.id,), count=count, imports_max=r * row_bytes + fixed, imports_total=total,
                work_max=work, up_max=work, covers={op.id: op.work},
                detail=dict(rows_total=R, rows_per_ru=r, row_bytes=row_bytes, fixed_bytes=fixed, wpr=wpr,
                            gen_tids=gen_tids, gen_work=gw))


# row-model kinds whose every output row is a plain sum over its row operand and may therefore be split into
# 32-bit partial sums (a circuit rewrite, hence only under recompute=True), exactly like split-K matmul tiles
_SPLIT_ROW_KINDS = frozenset({"colsum"})


def _split_rows_units(ctx: _Ctx, op: Op) -> list[Unit]:
    """Fallback for a single-operand reduction row op whose one row (``Q`` leaves) does not fit in ``X``.

    Each output row is cut into ``s`` segments of ``q`` leaves; one RU imports one segment and emits one
    32-bit partial; a plain reduce unit (see :func:`_reduce_unit`) sums the ``s`` partials of every row.
    Imports: every leaf once (``R * row_bytes``) plus ``GAMMA * R * s`` partial bytes.
    """
    if not ctx.recompute:
        raise ValueError(f"row op {op.id} ({op.kind}) needs a partial-sum split, which requires recompute=True")
    rm = _row_model(op)
    assert rm is not None and op.kind in _SPLIT_ROW_KINDS and len(rm[1]) == 1 and rm[1][0][0] == "row"
    rows_pc, edges = rm
    (_, Lr, e), = edges
    R = rows_pc * op.copies
    ic = ctx.import_cost(e.src)
    wpr = op.work_per_copy // rows_pc
    wpe = _ceil(wpr, Lr)
    q = Lr if ic == 0 else min(Lr, ctx.X // ic)
    if wpe > 0 and (ctx.f_mode == "work" or ctx.G < INF_WORK):
        q = min(q, ctx.W // wpe)
    if q < 1:
        raise ValueError(f"no legal segment for row op {op.id} ({op.kind} {op.statics}) under X={ctx.X}, F={ctx.F}")
    s = _ceil(Lr, q)
    work = q * wpe
    seg = Unit(kind="rows-split", ops=(op.id,), count=R * s, imports_max=q * ic, imports_total=R * Lr * ic,
               work_max=work, up_max=ctx.up_of(q, work), covers={op.id: op.work}, partial_out={op.id: R * s},
               detail=dict(rows_total=R, row_leaves=Lr, seg_leaves=q, segments=s, src=e.src, wpe=wpe))
    return [seg, _reduce_unit(ctx, [op.id], {op.id: R * s}, R, s)]


def _embed_unit(ctx: _Ctx, op: Op) -> Unit:
    st = op.statics
    if not all(k in st for k in ("Q", "V", "D")) or len(op.inputs) != 2:
        return _copies_unit(ctx, op)
    Q, V, D = int(st["Q"]), int(st["V"]), int(st["D"])
    e_tok, e_tab = op.inputs
    if e_tok.leaves_per_copy != Q or e_tab.leaves_per_copy != D * V or op.work_per_copy % (Q * D):
        return _copies_unit(ctx, op)
    Qt = Q * op.copies
    tokb, tb = ctx.import_cost(e_tok.src), ctx.import_cost(e_tab.src)
    wpe = op.work_per_copy // (Q * D)
    best = None
    for a in sorted(set(_log_grid(1, Qt, 1.3))):
        rem = ctx.X - a * tokb
        if rem < 0:
            continue
        d = D if tb == 0 else min(D, rem // (V * tb))
        if d < 1:
            continue
        if wpe > 0:
            d = min(d, ctx.W // (a * wpe))
            if d < 1:
                continue
        n_a, n_d = _ceil(Qt, a), _ceil(D, d)
        total = n_d * Qt * tokb + n_a * D * V * tb
        if best is None or (total, n_a * n_d) < (best[0], best[1] * best[2]):
            best = (total, n_a, n_d, a, d)
    if best is None:
        raise ValueError(f"no legal tile for embed op {op.id} under X={ctx.X}, F={ctx.F}")
    total, n_a, n_d, a, d = best
    work = a * d * wpe
    return Unit(kind="embed", ops=(op.id,), count=n_a * n_d, imports_max=a * tokb + d * V * tb, imports_total=total,
                work_max=work, up_max=work, covers={op.id: op.work},
                detail=dict(rows=Qt, cols=D, V=V, a=a, d=d, tok_tid=e_tok.src, table_tid=e_tab.src, wpe=wpe))


def _copies_unit(ctx: _Ctx, op: Op) -> Unit:
    """Fallback: whole copies of the op per RU, importing every non-fixed input of each copy."""
    if any((not e.exact) and ctx.import_cost(e.src) > 0 for e in op.inputs):
        # members of a batched op reading different tensors have floor-divided per-copy leaf counts; an RU
        # cost built from them could under-count, so refuse rather than certify a possibly illegal partition
        raise ValueError(f"op {op.id} ({op.kind}) has inexact per-copy leaf counts; no certified tile")
    imp = sum(e.leaves_per_copy * ctx.import_cost(e.src) for e in op.inputs)
    if imp > ctx.X or op.work_per_copy > ctx.W:
        raise ValueError(f"op {op.id} ({op.kind}) cannot be split below one copy: imports {imp} B, work {op.work_per_copy}")
    m = op.copies
    if imp > 0:
        m = min(m, ctx.X // imp)
    if op.work_per_copy > 0:
        m = min(m, ctx.W // op.work_per_copy)
    m = max(1, m)
    count = _ceil(op.copies, m)
    return Unit(kind="copies", ops=(op.id,), count=count, imports_max=m * imp, imports_total=op.copies * imp,
                work_max=m * op.work_per_copy, up_max=m * op.work_per_copy, covers={op.id: op.work},
                detail=dict(copies=op.copies, per_ru=m, imp_copy=imp))


# ---------------------------------------------------------------------------------------------------------
# attention fusion
# ---------------------------------------------------------------------------------------------------------

def _consumers(g: OpGraph, cons_map: dict[int, list[int]], tid: int) -> list[Op]:
    return [g.ops[i] for i in cons_map.get(tid, ())]


def _detect_attn_fwd(ctx: _Ctx, sm: Op, cons_map) -> Optional[dict]:
    g = ctx.g
    if sm.kind != "softmax" or len(sm.inputs) != 1 or "Q" not in sm.statics or "K" not in sm.statics:
        return None
    sc = g.producer(sm.inputs[0].src)
    if sc is None or sc.kind != "matmul" or len(sc.inputs) != 2 or sc.key[0] != sm.key[0]:
        return None
    S_q, S_k = int(sm.statics["Q"]), int(sm.statics["K"])
    Msc, Nsc, Ksc, _, _ = _matmul_shape(sc)
    if Nsc != S_k or Msc * sc.copies != S_q * sm.copies or sm.inputs[0].leaves_per_copy != S_q * S_k:
        return None
    if sm.work_per_copy % S_q:
        return None
    cons = _consumers(g, cons_map, sm.out)
    if len(cons) != 1:
        return None
    pv = cons[0]
    if pv.kind != "matmul" or len(pv.inputs) != 2 or pv.inputs[0].src != sm.out or pv.key[0] != sm.key[0]:
        return None
    Mpv, Npv, Kpv, _, _ = _matmul_shape(pv)
    if pv.copies != sc.copies or Mpv != Msc or Kpv != Nsc or pv.inputs[0].leaves_per_copy != Mpv * Kpv:
        return None
    return dict(sc=sc, sm=sm, pv=pv)


def _gqa_rep(ctx: _Ctx, sc: Op, pv: Op) -> int:
    """Number of query-head copies of ``sc`` that read the same K (and V) head slice (GQA), derived from the
    statics of the K projection producing the key operand; 1 whenever that structure cannot be verified."""
    g = ctx.g
    S, _, DH, _, _ = _matmul_shape(sc)
    _, DHv, _, _, _ = _matmul_shape(pv)
    ek, ev = sc.inputs[1] if len(sc.inputs) == 2 else None, pv.inputs[1] if len(pv.inputs) == 2 else None
    if ek is None or ev is None or not (ek.exact and ev.exact):
        return 1
    if ek.leaves_per_copy != S * DH or ev.leaves_per_copy != DHv * S:
        return 1
    tk, tv = g.tensors[ek.src], g.tensors[ev.src]
    if tk.kind != "op" or tv.kind != "op":
        return 1
    pk, pvp = g.producer(ek.src), g.producer(ev.src)
    if pk is None or pvp is None or pk.kind != "matmul" or pvp.kind != "matmul":
        return 1
    Mk, Nk, _, _, _ = _matmul_shape(pk)
    Mv, Nv, _, _, _ = _matmul_shape(pvp)
    q_tot = Mk * pk.copies                       # token rows projected to keys
    if Mv * pvp.copies != q_tot or Nk % DH or Nv % DHv or Nk // DH != Nv // DHv:
        return 1
    kvh = Nk // DH
    if q_tot % S or sc.copies % (q_tot // S):
        return 1
    nh = sc.copies // (q_tot // S)               # query heads per sequence
    if nh % kvh or tk.leaves != q_tot * Nk or tv.leaves != q_tot * Nv:
        return 1
    return nh // kvh


def _attn_fwd_unit(ctx: _Ctx, pat: dict):
    """Fused attention forward: a ``Unit`` (row mode) or ``[Unit, Unit]`` (key-split mode + merge), or None.
    ``rep`` query heads sharing one KV head (GQA) are placed in the same RU so the K/V slice is imported once."""
    sc, sm, pv = pat["sc"], pat["sm"], pat["pv"]
    S, Nsc, DH, _, ex_sc = _matmul_shape(sc)
    if not _attn_square(sc, pv):
        return None                                    # non-square (decode: T queries x S keys): per-op tiles
    _, DHv, _, _, ex_pv = _matmul_shape(pv)
    copies = sc.copies
    wpr_sm = sm.work_per_copy // int(sm.statics["Q"])
    q_o, k_o = (ctx.operand(t) for t in _matmul_operand_tids(sc))
    v_o = ctx.operand(_matmul_operand_tids(pv)[1])
    ops_ = (q_o, k_o, v_o)
    rep_max = _gqa_rep(ctx, sc, pv)
    # per-RU (query block of a rows x rep heads): q block rep*a*DH, full k slice S*DH, full v slice DHv*S
    best = None
    for rep in sorted({1, rep_max}):
        for gens in product(*[(False, True) if o.gen else (False,) for o in ops_]):
            gq, gk, gv = gens
            tok = sum(o.gb for o, f in zip(ops_, gens) if f)
            gw = sum(o.gw for o, f in zip(ops_, gens) if f)
            row_bytes = 0 if gq else DH * q_o.elems_bytes
            fixed = tok + (0 if gk else S * DH * k_o.elems_bytes) + (0 if gv else DHv * S * v_o.elems_bytes)
            if fixed > ctx.X:
                continue
            a = S if row_bytes == 0 else min(S, (ctx.X - fixed) // (rep * row_bytes))
            if a < 1:
                continue
            wpr = S * (DH + ex_sc) + wpr_sm + DHv * (S + ex_pv)     # work per query row (sc row, softmax row, pv row)
            a = min(a, (ctx.W - gw) // (rep * wpr)) if wpr > 0 else a
            if a < 1:
                continue
            n_a = _ceil(S, a)
            total = copies * S * row_bytes + (copies // rep) * n_a * fixed
            if best is None or total < best[0]:
                best = (total, a, n_a, row_bytes, fixed, gw, gens, wpr, rep)
    split = _attn_fwd_kvsplit(ctx, pat, rep_max) if ctx.recompute else None
    if best is None:
        return split
    total, a, n_a, row_bytes, fixed, gw, gens, wpr, rep = best
    if split is not None and sum(u.imports_total for u in split) < total:
        return split
    work = rep * a * wpr + gw
    covers = {sc.id: sc.macs(), sm.id: sm.work, pv.id: pv.macs()}
    return Unit(kind="attn-fwd", ops=(sc.id, sm.id, pv.id), count=(copies // rep) * n_a,
                imports_max=rep * a * row_bytes + fixed, imports_total=total, work_max=work, up_max=work, covers=covers,
                detail=dict(S=S, DH=DH, DHv=DHv, copies=copies, a=a, n_a=n_a, rep=rep, q_tid=q_o.tid, k_tid=k_o.tid,
                            v_tid=v_o.tid, gens=gens, wpr=wpr, row_bytes=row_bytes, fixed_bytes=fixed, gen_work=gw))


def _attn_kvsplit_shape(ctx: _Ctx, S: int, DH: int, DHv: int, ex_sc: int, ex_pv: int, wpr_sm: int,
                        row_bytes: int, kv_bytes: int, a: int, s: int, rep: int = 1):
    """Per-RU quantities of one (``rep * a`` query rows) x (``s`` keys) attention block; None if illegal."""
    n_k = _ceil(S, s)
    w_rk = (DH + ex_sc) + _ceil(wpr_sm, S) + (DHv + ex_pv)     # work per (row, key): score, softmax share, pv
    work = rep * a * (s * w_rk + DHv + 2)                      # + per-row partial (m, l, acc) bookkeeping
    imp = rep * a * row_bytes + s * kv_bytes
    if imp > ctx.X or work > ctx.W or work > ctx.F:
        return None
    if n_k > 1 and (GAMMA * n_k * 1 > ctx.X or n_k > ctx.W):    # the merge unit must hold >= 1 element
        return None
    return n_k, work, imp


def _attn_fwd_kvsplit(ctx: _Ctx, pat: dict, rep_max: int = 1) -> Optional[list[Unit]]:
    """Key-split ("flash") attention: an RU holds ``rep * a`` query rows (``rep`` GQA heads sharing the KV
    head) and ``s`` keys/values, emits per row an unnormalised 32-bit partial ``(m, l, acc[DHv])``; a plain
    reduce unit merges the ``n_k`` partials of every row (online-softmax identity -- a circuit rewrite, hence
    ``recompute=True`` only).  Operands are imported (no regeneration in this mode).  Imports per copy:
    ``n_k * S * row_bytes + n_a * S * kv_bytes / rep`` plus ``GAMMA * n_k * S * (DHv + 2)`` merge bytes."""
    sc, sm, pv = pat["sc"], pat["sm"], pat["pv"]
    if not _attn_square(sc, pv):
        return None
    S, _, DH, _, ex_sc = _matmul_shape(sc)
    _, DHv, _, _, ex_pv = _matmul_shape(pv)
    copies = sc.copies
    wpr_sm = sm.work_per_copy // int(sm.statics["Q"])
    q_o, k_o = (ctx.operand(t) for t in _matmul_operand_tids(sc))
    v_o = ctx.operand(_matmul_operand_tids(pv)[1])
    row_bytes = DH * q_o.elems_bytes
    kv_bytes = DH * k_o.elems_bytes + DHv * v_o.elems_bytes
    if kv_bytes == 0:
        return None                                    # fixed k/v: the row mode is already optimal
    n_el = S * copies * (DHv + 2)                      # partial elements per row-chunk, all rows and copies
    best = None
    grid = sorted(set(_log_grid(1, S, 1.3)))
    for rep in sorted({1, rep_max}):
        for s in grid:
            if s >= S:
                continue                               # n_k == 1 is the row mode
            for a in grid:
                r = _attn_kvsplit_shape(ctx, S, DH, DHv, ex_sc, ex_pv, wpr_sm, row_bytes, kv_bytes, a, s, rep)
                if r is None:
                    continue
                n_k, work, imp = r
                n_a = _ceil(S, a)
                total = copies * n_k * S * row_bytes + (copies // rep) * n_a * S * kv_bytes + GAMMA * n_k * n_el
                if best is None or total < best[0]:
                    best = (total, a, s, n_k, n_a, work, imp, rep)
    if best is None:
        return None
    total, a, s, n_k, n_a, work, imp, rep = best
    covers = {sc.id: sc.macs(), sm.id: sm.work, pv.id: pv.macs()}
    part = copies * n_k * S * row_bytes + (copies // rep) * n_a * S * kv_bytes
    u = Unit(kind="attn-fwd", ops=(sc.id, sm.id, pv.id), count=(copies // rep) * n_a * n_k, imports_max=imp,
             imports_total=part, work_max=work, up_max=work, covers=covers, partial_out={pv.id: n_el * n_k},
             detail=dict(mode="kv-split", S=S, DH=DH, DHv=DHv, copies=copies, a=a, s=s, n_a=n_a, n_k=n_k, rep=rep,
                         q_tid=q_o.tid, k_tid=k_o.tid, v_tid=v_o.tid, row_bytes=row_bytes, kv_bytes=kv_bytes))
    return [u, _reduce_unit(ctx, [pv.id], {pv.id: n_el * n_k}, n_el, n_k)]


def _detect_attn_bwd(ctx: _Ctx, ds: Op, cons_map) -> Optional[dict]:
    g = ctx.g
    if ds.kind != "mul" or len(ds.inputs) != 2 or "Q" not in ds.statics or "K" not in ds.statics:
        return None
    p0, p1 = g.producer(ds.inputs[0].src), g.producer(ds.inputs[1].src)
    if p0 is None or p1 is None:
        return None
    if p0.kind == "matmul" and p1.kind == "softmax":
        dP, sm = p0, p1
    elif p1.kind == "matmul" and p0.kind == "softmax":
        dP, sm = p1, p0
    else:
        return None
    scope = ds.key[0]
    if dP.key[0] != scope or sm.key[0] != scope or len(sm.inputs) != 1 or len(dP.inputs) != 2:
        return None
    sc = g.producer(sm.inputs[0].src)
    if sc is None or sc.kind != "matmul" or len(sc.inputs) != 2 or sc.key[0] != scope:
        return None
    S, Nsc, DH, _, _ = _matmul_shape(sc)
    if Nsc != S or sc.copies != dP.copies or _matmul_shape(dP)[:3] != (S, S, DH):
        return None
    S_q, S_k = int(sm.statics["Q"]), int(sm.statics["K"])
    if S_k != S or S_q * sm.copies != S * sc.copies or sm.work_per_copy % S_q:
        return None
    if int(ds.statics["K"]) != S or int(ds.statics["Q"]) * ds.copies != S * sc.copies or ds.work_per_copy % int(ds.statics["Q"]):
        return None
    sm_cons = _consumers(g, cons_map, sm.out)
    ds_cons = _consumers(g, cons_map, ds.out)
    if len(sm_cons) != 2 or len(ds_cons) != 2:
        return None
    dV = next((o for o in sm_cons if o is not ds), None)
    if dV is None or dV.kind != "matmul" or len(dV.inputs) != 2 or dV.inputs[0].src != sm.out or dV.key[0] != scope:
        return None
    dQ = dK = None
    for o in ds_cons:
        if o.kind != "matmul" or len(o.inputs) != 2 or o.inputs[0].src != ds.out or o.key[0] != scope:
            return None
        if o.copies == sc.copies:
            dQ = o
        else:
            dK = o
    if dQ is None or dK is None:
        return None
    if _matmul_shape(dQ)[:3] != (S, DH, S) or dQ.inputs[1].src != sc.inputs[1].src:
        return None
    if sc.copies % dK.copies:
        return None
    rep = sc.copies // dK.copies
    if _matmul_shape(dK)[:3] != (S, DH, rep * S) or dK.inputs[1].src != sc.inputs[0].src:
        return None
    if dV.copies != dK.copies or _matmul_shape(dV)[:3] != (S, DH, rep * S) or dV.inputs[1].src != dP.inputs[0].src:
        return None
    return dict(sc=sc, sm=sm, dP=dP, ds=ds, dQ=dQ, dK=dK, dV=dV, rep=rep)


def _attn_bwd_units(ctx: _Ctx, pat: dict) -> Optional[list[Unit]]:
    sc, sm, dP, ds, dQ, dK, dV, rep = (pat[k] for k in ("sc", "sm", "dP", "ds", "dQ", "dK", "dV", "rep"))
    S, _, DH, _, ex_sc = _matmul_shape(sc)
    ex_dP, ex_dQ, ex_dK, ex_dV = (_matmul_shape(o)[4] for o in (dP, dQ, dK, dV))
    copies = sc.copies
    wpr_sm = sm.work_per_copy // int(sm.statics["Q"])
    wpr_ds = ds.work_per_copy // int(ds.statics["Q"])
    q_o, k_o = (ctx.operand(t) for t in _matmul_operand_tids(sc))
    dO_o, v_o = (ctx.operand(t) for t in _matmul_operand_tids(dP))
    row_bytes = DH * (q_o.elems_bytes + dO_o.elems_bytes)          # q_j and dO_j rows of the query block
    fixed = S * DH * (k_o.elems_bytes + v_o.elems_bytes)             # k_h and v_h slices
    # per query row: sc row, softmax row, dP row, dS row, dQ row, dK/dV segment of one row
    wpr = S * (DH + ex_sc) + wpr_sm + S * (DH + ex_dP) + wpr_ds + DH * (S + ex_dQ) + 2 * S * DH
    modes = ("star", "chain") if ctx.recompute else ("chain",)
    best = None
    for mode in modes:
        chain_part = 2 * GAMMA * S * DH if mode == "chain" else 0   # dK and dV accumulators of the previous segment
        fx = fixed + chain_part
        if fx > ctx.X:
            continue
        a = S if row_bytes == 0 else min(S, (ctx.X - fx) // row_bytes)
        w_extra = 2 * S * DH * max(ex_dK, ex_dV)                  # per-RU accumulator work (see ``work`` below)
        if w_extra > ctx.W:
            continue
        a = min(a, (ctx.W - w_extra) // wpr) if wpr > 0 else a
        if a < 1:
            continue
        n_a = _ceil(S, a)
        nseg = rep * n_a                       # k-segments of the dK/dV contraction per kv-head
        if nseg == 1:
            chain_part = 0
            fx = fixed
        if mode == "star" and nseg > 1 and (GAMMA * nseg > ctx.X or nseg > ctx.W):
            continue
        n_ru = copies * n_a
        total = copies * (S * row_bytes + n_a * fx)
        if mode == "star" and nseg > 1:
            total += GAMMA * nseg * S * DH * 2 * dK.copies      # reduction RUs import all partials
        if best is None or total < best[0]:
            best = (total, mode, a, n_a, nseg, fx, n_ru)
    if best is None:
        return None
    total, mode, a, n_a, nseg, fx, n_ru = best
    work = a * wpr + 2 * S * DH * max(ex_dK, ex_dV)
    covers = {sc.id: sc.macs(), sm.id: sm.work, dP.id: dP.macs(), ds.id: ds.work, dQ.id: dQ.macs(),
              dK.id: dK.macs(), dV.id: dV.macs()}
    imports_max = a * row_bytes + fx
    units = [Unit(kind="attn-bwd", ops=(sc.id, sm.id, dP.id, ds.id, dQ.id, dK.id, dV.id), count=n_ru,
                  imports_max=imports_max, imports_total=copies * (S * row_bytes + n_a * fx), work_max=work, up_max=work,
                  covers=covers,
                  detail=dict(S=S, DH=DH, rep=rep, copies=copies, a=a, n_a=n_a, nseg=nseg, mode=mode, q_tid=q_o.tid,
                              k_tid=k_o.tid, v_tid=v_o.tid, dO_tid=dO_o.tid, wpr=wpr, row_bytes=row_bytes, fixed_bytes=fx,
                              kv_copies=dK.copies))]
    if mode == "star" and nseg > 1:
        units[0].partial_out = {dK.id: n_ru * S * DH, dV.id: n_ru * S * DH}
        for o in (dK, dV):
            units.append(_reduce_unit(ctx, [o.id], {o.id: n_ru * S * DH}, S * DH * o.copies, nseg))
    return units


# ---------------------------------------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------------------------------------

def _operand_groups(ctx: _Ctx, ops: list[Op]) -> list[tuple[str, list[Op]]]:
    """Groups of matmuls sharing the same view of the same tensor as A (preferred) or B."""
    out: list[tuple[str, list[Op]]] = []
    if ctx.program is None:
        return out
    taken: set[int] = set()
    for role, arg in (("A", 0), ("B", 1)):
        buckets: dict[tuple, list[Op]] = {}
        for o in ops:
            if o.id in taken or len(o.inputs) != 2:
                continue
            M, N, K, CH, _ = _matmul_shape(o)
            vk = ctx.view_key(o, arg)
            if vk is None:
                continue
            rows = M if role == "A" else N
            buckets.setdefault((o.inputs[arg].src, rows, K, CH, o.copies, vk), []).append(o)
        for lst in buckets.values():
            if len(lst) > 1:
                out.append((role, lst))
                taken.update(o.id for o in lst)
    return out


def _consumer_map(g: OpGraph) -> dict[int, list[int]]:
    m: dict[int, list[int]] = {}
    for o in g.ops:
        for e in o.inputs:
            m.setdefault(e.src, []).append(o.id)
    return m


def _fusion_pass(ctx: _Ctx, jobs: list[tuple[list[Op], str]], job_units: list[list[Unit]],
                 claimed: set[int]) -> tuple[int, int]:
    """Fuse element-wise / row consumers (and LoRA-style sidecar matmuls) into the matmul jobs that
    materialise their inputs, whenever the re-optimised tiles are cheaper than tiles + standalone ops.
    Mutates ``job_units`` / ``claimed``; returns ``(n_fused_ops, n_sidecars)``."""
    g = ctx.g
    mat: dict[int, tuple[int, int]] = {}                       # tensor -> (job, segment whose positions it has)
    for j, (ops, _) in enumerate(jobs):
        for i, o in enumerate(ops):
            mat[o.out] = (j, i)
    single_job = {ops[0].id: j for j, (ops, _) in enumerate(jobs) if len(ops) == 1}
    geo = [_group_geometry(ctx, ops, role) for ops, role in jobs]
    steps: list[list[tuple]] = [[] for _ in jobs]
    absorbed: dict[int, int] = {}                              # sidecar job -> host job
    tentative: set[int] = set()
    for c in g.ops:
        if c.id in claimed or c.id in tentative or (c.kind not in _EW_KINDS and c.kind not in _ROWFULL_KINDS):
            continue
        rm = _row_model(c)
        if rm is None:
            continue
        rows_pc, edges = rm
        rows = rows_pc * c.copies
        hosts = [mat[e.src] for _, _, e in edges if e.src in mat]
        if not hosts:
            continue
        j, seg = hosts[0]
        if j in absorbed:
            continue
        ops_j, role_j = jobs[j]
        Rs, _, segR, _, K, CH, extra, copies = geo[j]
        P = Rs * segR[seg] * copies
        if rows <= 0 or P % rows:
            continue
        L = P // rows
        ok = True
        for idx, (role_, lv, e) in enumerate(edges):
            if e.src in mat and mat[e.src][0] == j:
                p_op = g.ops[g.tensors[e.src].producer]
                if role_ != "row" or lv != L or not ctx.identity_view(c, idx, p_op):
                    ok = False
                    break
                if mat[e.src][1] != seg and len(set(segR)) != 1:
                    ok = False
                    break
        if not ok:
            continue
        rf = c.kind in _ROWFULL_KINDS
        if rf and (role_j not in ("A", None) or L != segR[seg]):
            continue
        # sidecar: add(materialised, p2.out) with p2 an unfused single-matmul job on the same output blocks
        side = None
        if c.kind == "add":
            others = [(idx, e) for idx, (_, _, e) in enumerate(edges) if not (e.src in mat and mat[e.src][0] == j)]
            if len(others) == 1:
                idx2, e2 = others[0]
                prod = g.tensors[e2.src].producer
                j2 = single_job.get(prod) if prod is not None else None
                if j2 is not None and j2 != j and j2 not in absorbed and not steps[j2]:
                    p2 = g.ops[prod]
                    M2, N2, K2, _, _ = _matmul_shape(p2)
                    a2, b2 = _matmul_operand_tids(p2)
                    s_arg = 0 if role_j in ("A", None) else 1
                    s2, t2, Ms, Mt = (a2, b2, M2, N2) if s_arg == 0 else (b2, a2, N2, M2)
                    if (p2.copies == copies and Ms == Rs and Mt == segR[seg] and t2 not in mat
                            and ctx.identity_view(c, idx2, p2)):
                        s2_ok = True
                        if s2 in mat:
                            js, ss = mat[s2]
                            s2_ok = (js == j and s_arg == 0 and segR[ss] == K2
                                     and ctx.identity_view(p2, 0, g.ops[g.tensors[s2].producer]))
                        if s2_ok:
                            side = ("side", p2.id, seg)
        if side is not None:
            steps[j].append(side)
            absorbed[single_job[side[1]]] = j
            tentative.add(side[1])
            mat[g.ops[side[1]].out] = (j, seg)
        steps[j].append(("ew", c.id, seg, rf))
        tentative.add(c.id)
        mat[c.out] = (j, seg)

    def standalone(st_list) -> float:
        tot = 0.0
        for s in st_list:
            if s[0] == "side":
                tot += sum(u.imports_total for u in job_units[single_job[s[1]]])
            else:
                try:
                    tot += _rows_unit(ctx, g.ops[s[1]]).imports_total
                except ValueError:
                    tot += math.inf
        return tot

    def build_incremental(ops, role, cands):
        acc: list[tuple] = []
        us = None
        for s in cands:
            try:
                trial = _tile_units(ctx, ops, role, tuple(acc + [s]))
            except AssertionError:
                trial = None
            if trial is not None:
                acc.append(s)
                us = trial
        return acc, us

    n_fused = n_side = 0
    for j, st in enumerate(steps):
        if not st:
            continue
        ops, role = jobs[j]
        base_cost = sum(u.imports_total for u in job_units[j])
        chosen = None
        for cands in (st, [s for s in st if s[0] == "ew" and not s[3]]):
            if not cands:
                continue
            acc, us = build_incremental(ops, role, cands)
            if us is not None and sum(u.imports_total for u in us) <= base_cost + standalone(acc):
                chosen = (acc, us)
                break
        if chosen is None:
            continue
        acc, us = chosen
        job_units[j] = us
        for s in acc:
            claimed.add(s[1])
            if s[0] == "side":
                job_units[single_job[s[1]]] = []
                n_side += 1
            else:
                n_fused += 1
    return n_fused, n_side


def _ext_bytes(ctx: _Ctx, ops: set[int]) -> int:
    """Bytes of every tensor read by ``ops`` and produced outside them (whole tensors; non-fixed only)."""
    g = ctx.g
    seen: set[int] = set()
    tot = 0
    for oid in ops:
        for e in g.ops[oid].inputs:
            t = g.tensors[e.src]
            if e.src in seen or (t.producer is not None and t.producer in ops):
                continue
            seen.add(e.src)
            tot += t.leaves * ctx.import_cost(e.src)
    return tot


def _opset_unit(ctx: _Ctx, ops: set[int]) -> Unit:
    g = ctx.g
    work = sum(g.ops[o].work for o in ops)
    ext = _ext_bytes(ctx, ops)
    covers = {o: (g.ops[o].macs() if g.ops[o].kind == "matmul" else g.ops[o].work) for o in sorted(ops)}
    return Unit(kind="opset", ops=tuple(sorted(ops)), count=1, imports_max=ext, imports_total=ext, work_max=work,
                up_max=work, covers=covers, detail={})


def _opset_pass(ctx: _Ctx, units: list[Unit]) -> tuple[list[Unit], int, int]:
    """Greedily merge runs of neighbouring op families (in topological order) into single whole-op RUs
    whenever the merged RU satisfies ``X`` / ``F`` and is not more expensive than the families it replaces.
    Only bites at large ``X`` (tiny graphs, sweeps); at realistic scale every family alone exceeds ``X``."""
    g = ctx.g
    X, F = ctx.X, ctx.W
    parent: dict[int, int] = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def unit_ops(u: Unit):
        return set(u.ops) | set(u.covers)          # fused / sidecar ops live in ``covers`` only

    for u in units:
        for o in unit_ops(u):
            parent[find(o)] = find(u.ops[0])
    clusters: dict[int, list[Unit]] = {}
    for u in units:
        clusters.setdefault(find(u.ops[0]), []).append(u)
    cl = []
    for us in clusters.values():
        ops = set().union(*(unit_ops(u) for u in us))
        cl.append((min(ops), ops, us, sum(u.imports_total for u in us), sum(g.ops[o].work for o in ops)))
    cl.sort(key=lambda t: t[0])
    n = len(cl)
    # exact DP over partitions of the cluster sequence into consecutive runs: best[i] = cheapest cost of
    # clusters i.. ; a run is either one cluster kept as its families or a feasible whole-op RU
    best = [0.0] * (n + 1)
    choice: list[tuple[int, bool]] = [(0, False)] * n
    for i in range(n - 1, -1, -1):
        best[i] = cl[i][3] + best[i + 1]
        choice[i] = (i + 1, False)
        ext_map: dict[int, int] = {}
        produced: set[int] = set()
        ext = work = 0
        j = i
        while j < n and j - i < _MAX_OPSET_RUN:
            ops_j, work_j = cl[j][1], cl[j][4]
            work += work_j
            if work > F:
                break
            for oid in sorted(ops_j):
                o = g.ops[oid]
                for e in o.inputs:
                    if e.src not in produced and e.src not in ext_map:
                        b = g.tensors[e.src].leaves * ctx.import_cost(e.src)
                        ext_map[e.src] = b
                        ext += b
                produced.add(o.out)
                ext -= ext_map.pop(o.out, 0)
            j += 1
            if ext > X:
                break
            cand = ext + best[j]
            if cand < best[i] or (cand == best[i] and (j - i > 1 or len(cl[i][2]) > 1)):
                best[i] = cand
                choice[i] = (j, True)
    out: list[Unit] = []
    n_sets = n_merged = 0
    i = 0
    while i < n:
        j, merged = choice[i]
        if merged:
            ops = set().union(*(cl[t][1] for t in range(i, j)))
            out.append(_opset_unit(ctx, ops))
            n_sets += 1
            n_merged += j - i
        else:
            out.extend(cl[i][2])
        i = j
    return out, n_sets, n_merged


_MAX_OPSET_RUN = 1024


def upper_bound(g: OpGraph, F: int, X: int, *, G: Optional[int] = None, workload=None, program=None,
                recompute: bool = True, f_mode: str = "upstream", fuse_attention: bool = True,
                group_operands: bool = True, fuse_epilogue: bool = True, fuse_opsets: bool = True) -> UpperBound:
    """Explicit legal partition of ``g`` and its input cost (see the module docstring).

    ``program``: the Verity ``Program`` the graph was extracted from (or set ``g.program``); enables
    operand-sharing groups.  ``recompute``: allow regeneration / star reductions (adversary evaluates an
    equivalent circuit).  ``f_mode``: ``"upstream"`` (SPEC §1 ``Up_R``) or ``"work"`` (``work(R) <= F``).
    ``G``: total-work cap per RU (``Work(R) <= G``, THEORY §0); ``None`` = unbounded."""
    if f_mode not in F_MODES:
        raise ValueError(f"f_mode must be one of {F_MODES}")
    F, X = int(F), int(X)
    G = None if G is None else int(G)
    if G is not None and G < 1:
        raise ValueError("G must be a positive work cap or None")
    program = program if program is not None else getattr(g, "program", None)
    ctx = _Ctx(g, F, X, recompute, f_mode, program, G)
    notes: list[str] = []
    units: list[Unit] = []
    claimed: set[int] = set()
    cons_map = _consumer_map(g)

    # 1. attention fusion
    n_fwd = n_bwd = 0
    if fuse_attention:
        for o in g.ops:
            if o.kind == "mul" and o.id not in claimed:
                pat = _detect_attn_bwd(ctx, o, cons_map)
                if pat and all(p.id not in claimed for p in pat.values() if isinstance(p, Op)):
                    us = _attn_bwd_units(ctx, pat)
                    if us is not None:
                        units.extend(us)
                        claimed.update(p.id for p in pat.values() if isinstance(p, Op))
                        n_bwd += 1
        for o in g.ops:
            if o.kind == "softmax" and o.id not in claimed:
                pat = _detect_attn_fwd(ctx, o, cons_map)
                if pat and all(p.id not in claimed for p in pat.values()):
                    u = _attn_fwd_unit(ctx, pat)
                    if u is not None:
                        units.extend(u if isinstance(u, list) else [u])
                        claimed.update(p.id for p in pat.values())
                        n_fwd += 1
    if n_fwd or n_bwd:
        notes.append(f"attention fusion: {n_fwd} forward and {n_bwd} backward patterns fused")

    # 2. matmul jobs: operand-sharing groups + single matmuls
    mms = [o for o in g.ops if o.kind == "matmul" and o.id not in claimed]
    jobs: list[tuple[list[Op], str]] = []
    if group_operands:
        groups = _operand_groups(ctx, mms)
        jobs.extend((lst, role) for role, lst in groups)
        claimed.update(o.id for _, lst in groups for o in lst)
        if program is None:
            notes.append("operand-sharing groups disabled: pass program= (or set g.program) to enable")
        elif groups:
            notes.append(f"operand-sharing groups: {len(groups)} groups covering {sum(len(l) for _, l in groups)} matmuls")
    for o in mms:
        if o.id not in claimed:
            jobs.append(([o], "A"))
            claimed.add(o.id)
    job_units: list[list[Unit]] = []
    for ops, role in jobs:
        us = _tile_units(ctx, ops, role)
        if us is None:
            raise ValueError(f"no legal tile for matmul op(s) {[o.id for o in ops]} under X={X}, F={F}")
        job_units.append(us)

    # 3. epilogue / sidecar fusion into the matmul jobs (needs the program for view identity)
    if fuse_epilogue and program is not None:
        n_fused, n_side = _fusion_pass(ctx, jobs, job_units, claimed)
        if n_fused or n_side:
            notes.append(f"epilogue fusion: {n_fused} element-wise/row ops and {n_side} sidecar matmuls fused into tiles")
    for us in job_units:
        units.extend(us)

    # 4. everything else, op by op
    n_fallback = n_split_rows = 0
    for o in g.ops:
        if o.id in claimed:
            continue
        if o.kind == "embed":
            units.append(_embed_unit(ctx, o))
        elif o.kind in _ROW_MODELS:
            try:
                u = _rows_unit(ctx, o)
            except ValueError:
                if o.kind not in _SPLIT_ROW_KINDS or _row_model(o) is None:
                    raise
                units.extend(_split_rows_units(ctx, o))
                n_split_rows += 1
                claimed.add(o.id)
                continue
            n_fallback += u.kind == "copies"
            units.append(u)
        else:
            units.append(_copies_unit(ctx, o))
            n_fallback += 1
        claimed.add(o.id)
    if n_fallback:
        notes.append(f"{n_fallback} ops handled by the per-copy fallback")
    if n_split_rows:
        notes.append(f"{n_split_rows} reduction row ops split into partial sums (row does not fit X)")
    n_gen = sum(1 for u in units if u.detail.get("gen_work", 0) or any(u.detail.get("gens", ())))
    if n_gen:
        notes.append(f"{n_gen} unit families regenerate a free-closure operand instead of importing it")

    # 5. coarse pass: merge whole neighbouring op families into single RUs when that fits X and F
    if fuse_opsets:
        units, n_sets, n_merged = _opset_pass(ctx, units)
        if n_sets:
            notes.append(f"opset fusion: {n_merged} op families merged into {n_sets} whole-op RUs")

    plan = Plan(units=units, F=F, X=X, recompute=recompute, f_mode=f_mode, notes=list(notes), G=G)
    check_plan(plan, g, F, X, G)

    # attribution
    per_op = {o.id: 0 for o in g.ops}
    for u in units:
        # fused epilogue / sidecar ops (in ``covers`` but not in ``ops``) are attributed to their host matmuls
        host = {k: v for k, v in u.covers.items() if k in u.ops} if u.kind in ("tile", "reduce") else u.covers
        tot_cov = sum(host.values())
        if tot_cov <= 0:
            # reduction units: attribute to their ops by partials consumed
            keys = list(u.partial_in) or list(u.ops)
            w = {k: u.partial_in.get(k, 1) for k in keys}
            tot_cov = sum(w.values())
            shares = w
        else:
            shares = host
        acc = 0
        items = list(shares.items())
        for i, (oid, cov) in enumerate(items):
            b = u.imports_total - acc if i == len(items) - 1 else u.imports_total * cov // tot_cov
            per_op[oid] += b
            acc += b
    total = plan.total
    by_kind: dict[str, int] = {}
    by_class: dict[str, int] = {}
    attn_ops = {oid for u in units if u.kind.startswith("attn") for oid in u.ops}
    grad_dep = _grad_dependent(g)
    for o in g.ops:
        by_kind[o.kind] = by_kind.get(o.kind, 0) + per_op[o.id]
        cls = classify_op(g, o, attn_ops, grad_dep)
        by_class[cls] = by_class.get(cls, 0) + per_op[o.id]
    a = _adw(g)
    kappa = a.matmul_macs / total if total else float("inf")
    return UpperBound(total=total, n_units=plan.n_units, per_op=per_op, plan=plan, notes=notes, kappa=kappa,
                      adw_matmul_macs=a.matmul_macs, by_kind=by_kind, by_class=by_class)


def _grad_dependent(g: OpGraph) -> dict[int, bool]:
    """op id -> whether the op is (or depends on) a loss-gradient op (ops are in topological order)."""
    dep: dict[int, bool] = {}
    for o in g.ops:
        d = o.kind == "lossgrad"
        for e in o.inputs:
            p = g.tensors[e.src].producer
            if p is not None and dep.get(p, False):
                d = True
        dep[o.id] = d
    return dep


def classify_op(g: OpGraph, o: Op, attn_ops: set[int] | None = None, grad_dep: dict[int, bool] | None = None) -> str:
    """Reporting class: matmul-fwd / matmul-dgrad / matmul-wgrad / attention / <other kinds>."""
    if o.kind != "matmul":
        return "attention" if attn_ops and o.id in attn_ops else o.kind
    if attn_ops and o.id in attn_ops:
        return "attention"
    if grad_dep is None:
        grad_dep = _grad_dependent(g)
    a_t, b_t = _matmul_operand_tids(o)
    A, B = g.tensors[a_t], g.tensors[b_t]

    def weight_like(t):      # a root param, or a perturbed / updated copy of one (ES, local-SGD)
        return t.kind == "param" or (t.producer is not None and g.ops[t.producer].kind in ("perturb", "sgdupdate", "esupdate"))
    if not weight_like(A) and not weight_like(B):
        return "attention" if o.copies > 1 else "matmul-wgrad"
    if weight_like(B) or weight_like(A):
        act = A if weight_like(B) else B
        if act.kind == "op" and grad_dep.get(act.producer, False):
            return "matmul-dgrad"
        return "matmul-fwd"
    return "matmul-other"


# ---------------------------------------------------------------------------------------------------------
# independent legality check
# ---------------------------------------------------------------------------------------------------------

def check_plan(plan: Plan, g: OpGraph, F: int, X: int, G: Optional[int] = None) -> None:
    """Re-derive every unit from its symbolic description and assert legality (``X``, ``F`` and, when given,
    the total-work cap ``G``).  Raises AssertionError."""
    F, X = int(F), int(X)
    G = plan.G if G is None else int(G)
    # with the program attached to the graph the in-order-view claims of fused ops are re-verified too
    ctx = _Ctx(g, F, X, plan.recompute, plan.f_mode, getattr(g, "program", None), G)
    covered: dict[int, int] = {}
    p_out: dict[int, int] = {}
    p_in: dict[int, int] = {}
    for ui, u in enumerate(plan.units):
        assert u.count >= 1, f"unit {ui}: empty family"
        rec = _rederive(ctx, u)
        if rec is not None:
            imp_max, imp_tot, work, up = rec
            assert u.imports_max >= imp_max, f"unit {ui} ({u.kind}): declared imports {u.imports_max} < re-derived {imp_max}"
            assert u.imports_total >= imp_tot, f"unit {ui} ({u.kind}): declared total {u.imports_total} < re-derived {imp_tot}"
            assert u.up_max >= up, f"unit {ui} ({u.kind}): declared upstream bound {u.up_max} < re-derived {up}"
            assert u.work_max >= work, f"unit {ui} ({u.kind}): declared work {u.work_max} < re-derived {work}"
        assert u.imports_max <= X, f"unit {ui} ({u.kind}, ops {u.ops}): RU input {u.imports_max} B > X={X}"
        assert u.up_max <= F, f"unit {ui} ({u.kind}, ops {u.ops}): RU upstream work {u.up_max} > F={F}"
        if G is not None:
            assert u.work_max <= G, f"unit {ui} ({u.kind}, ops {u.ops}): RU total work {u.work_max} > G={G}"
        assert u.imports_total <= u.count * u.imports_max, f"unit {ui}: total {u.imports_total} exceeds count*max"
        for oid, c in u.covers.items():
            covered[oid] = covered.get(oid, 0) + c
        for oid, c in u.partial_out.items():
            p_out[oid] = p_out.get(oid, 0) + c
        for oid, c in u.partial_in.items():
            p_in[oid] = p_in.get(oid, 0) + c
    for o in g.ops:
        need = o.macs() if o.kind == "matmul" else o.work
        got = covered.get(o.id, 0)
        assert got == need, f"op {o.id} ({o.kind}): covered {got} of {need} {'MACs' if o.kind == 'matmul' else 'work'}"
    for oid in set(p_out) | set(p_in):
        assert p_out.get(oid, 0) == p_in.get(oid, 0), (f"op {oid}: {p_out.get(oid, 0)} partial sums emitted but "
                                                       f"{p_in.get(oid, 0)} reduced")


def _rederive(ctx: _Ctx, u: Unit):
    """``(imports_max, imports_total, work_max, up_max)`` recomputed from ``u.detail`` and the graph."""
    d = u.detail
    g = ctx.g
    if u.kind == "tile":
        ops = [g.ops[i] for i in u.ops]
        role = d["shared_role"]
        Rs, shared_tid, segR, seg_tids, K, CH, extra, copies = _group_geometry(ctx, ops, role)
        assert (Rs, shared_tid, tuple(segR), tuple(seg_tids), K, CH, copies) == \
            (d["Rs"], d["shared_tid"], tuple(d["segR"]), tuple(d["seg_tids"]), d["K"], d["CH"], d["copies"]), \
            f"tile geometry mismatch for ops {u.ops}"
        assert extra <= d["extra"], "per-output extra work understated"
        a, k, c, bs, nk, mode, gens = d["a"], d["k"], d["c"], d["bs"], d["nk"], d["mode"], d["gens"]
        assert mode == "chain" or ctx.recompute, "star reduction requires recompute=True"
        assert nk == _ceil(K, k) and tuple(bs) == tuple(_ceil(R, c) for R in segR)
        assert k % CH == 0 or k == K

        def cost(tid, gen):
            if gen:
                assert ctx.gen_ok(tid), f"tensor {tid} is not regenerable"
                return 0, ctx.gen_bytes(tid), ctx.gen_work(tid)
            return ctx.import_cost(tid), 0, 0
        sig, tok, gw = cost(shared_tid, gens[0])
        rhos = []
        for tid, gflag in zip(seg_tids, gens[1:]):
            r, tb, w = cost(tid, gflag)
            rhos.append(r)
            tok += tb
            gw += w
        fus, fcov, _ = _fus_params(ctx, ops, role, Rs, tuple(segR), copies, d["steps"])
        r = _tile_eval(Rs, K, CH, d["extra"], sig, rhos, tok, gw, list(segR), ctx.X, ctx.F, ctx.f_mode, mode, k, c, fus,
                       G=ctx.G)
        assert r is not None, f"tile ({mode}, k={k}, c={c}) for ops {u.ops} is infeasible on re-derivation"
        _, sol = r
        assert sol["a"] == a and sol["nk"] == nk and tuple(sol["bs"]) == tuple(bs), "tile block sizes do not re-derive"
        assert u.count == sol["count"] * copies
        total = sol["cost"] * copies
        exp_cov = {o.id: Rs * R * K * copies for o, R in zip(ops, segR)}
        for oid, (where, amt) in fcov.items():
            if where == "tile" or nk == 1:
                exp_cov[oid] = amt
        assert u.covers == exp_cov, f"tile coverage mismatch for ops {u.ops}"
        if mode == "star" and nk > 1:
            for o, R in zip(ops, segR):
                assert u.partial_out.get(o.id, 0) == nk * Rs * R * copies
            total -= sol["red"]["total_pc"] * copies
        else:
            assert not u.partial_out
        return sol["imports_max"], total, sol["work_max"], sol["up_max"]
    if u.kind == "reduce":
        return _reduce_unit_check(ctx, u)
    if u.kind == "opset":
        ops = set(u.ops)
        assert u.count == 1 and len(ops) == len(u.ops)
        work = sum(g.ops[o].work for o in ops)
        ext = _ext_bytes(ctx, ops)
        assert u.covers == {o: (g.ops[o].macs() if g.ops[o].kind == "matmul" else g.ops[o].work) for o in u.ops}
        return ext, ext, work, work
    if u.kind == "rows":
        op = g.ops[u.ops[0]]
        rm = _row_model(op)
        assert rm is not None
        rows_pc, edges = rm
        R, r = rows_pc * op.copies, d["rows_per_ru"]
        assert R == d["rows_total"] and u.count == _ceil(R, r) and u.covers == {op.id: op.work}
        gen_tids = set(d["gen_tids"])
        row_b = fixed = gw = 0
        for role, leaves, e in edges:
            if e.src in gen_tids:
                assert role == "row" and ctx.gen_ok(e.src)
                fixed += ctx.gen_bytes(e.src)
                gw += ctx.gen_work(e.src)
            elif role == "row":
                row_b += leaves * ctx.import_cost(e.src)
            else:
                fixed += leaves * ctx.import_cost(e.src)
        work = r * (op.work_per_copy // rows_pc) + gw
        return r * row_b + fixed, R * row_b + u.count * fixed, work, work
    if u.kind == "rows-split":
        op = g.ops[u.ops[0]]
        assert ctx.recompute, "partial-sum row splits require recompute=True"
        assert op.kind in _SPLIT_ROW_KINDS
        rm = _row_model(op)
        assert rm is not None and len(rm[1]) == 1 and rm[1][0][0] == "row"
        rows_pc, edges = rm
        (_, Lr, e), = edges
        R, q, s = rows_pc * op.copies, d["seg_leaves"], d["segments"]
        assert R == d["rows_total"] and Lr == d["row_leaves"] and e.src == d["src"]
        assert 1 <= q <= Lr and s == _ceil(Lr, q) and u.count == R * s
        assert u.covers == {op.id: op.work} and u.partial_out == {op.id: R * s} and not u.partial_in
        ic = ctx.import_cost(e.src)
        wpe = _ceil(op.work_per_copy // rows_pc, Lr)
        work = q * wpe
        return q * ic, R * Lr * ic, work, ctx.up_of(q, work)
    if u.kind == "embed":
        op = g.ops[u.ops[0]]
        Qt, D, V, a, dd = d["rows"], d["cols"], d["V"], d["a"], d["d"]
        e_tok, e_tab = op.inputs
        assert e_tok.src == d["tok_tid"] and e_tab.src == d["table_tid"] and Qt == int(op.statics["Q"]) * op.copies
        assert e_tok.leaves_per_copy == int(op.statics["Q"]) and e_tab.leaves_per_copy == D * V
        tokb, tb = ctx.import_cost(e_tok.src), ctx.import_cost(e_tab.src)
        n_a, n_d = _ceil(Qt, a), _ceil(D, dd)
        assert u.count == n_a * n_d and u.covers == {op.id: op.work}
        wpe = _ceil(op.work_per_copy, int(op.statics["Q"]) * D)
        work = a * dd * wpe
        return a * tokb + dd * V * tb, n_d * Qt * tokb + n_a * D * V * tb, work, work
    if u.kind == "copies":
        op = g.ops[u.ops[0]]
        imp = sum(e.leaves_per_copy * ctx.import_cost(e.src) for e in op.inputs)
        m = d["per_ru"]
        assert u.count == _ceil(op.copies, m) and u.covers == {op.id: op.work}
        return m * imp, op.copies * imp, m * op.work_per_copy, m * op.work_per_copy
    if u.kind == "attn-fwd":
        sc, sm, pv = (g.ops[i] for i in u.ops)
        cons = _consumer_map(g)
        pat = _detect_attn_fwd(ctx, sm, cons)
        assert pat is not None and pat["sc"] is sc and pat["pv"] is pv, "attention forward pattern not re-detected"
        assert _attn_square(sc, pv), "fused attention units assume square attention (queries == keys)"
        S, _, DH, _, ex_sc = _matmul_shape(sc)
        _, DHv, _, _, ex_pv = _matmul_shape(pv)
        tids = (d["q_tid"], d["k_tid"], d["v_tid"])
        assert tids == (_matmul_operand_tids(sc) + (_matmul_operand_tids(pv)[1],))
        rep = d.get("rep", 1)
        assert rep in (1, _gqa_rep(ctx, sc, pv)) and sc.copies % rep == 0, "GQA sharing factor not re-derived"
        if d.get("mode") == "kv-split":
            assert ctx.recompute, "key-split attention requires recompute=True"
            a, s, n_k, n_a = d["a"], d["s"], d["n_k"], d["n_a"]
            row_b = DH * ctx.import_cost(tids[0])
            kv_b = DH * ctx.import_cost(tids[1]) + DHv * ctx.import_cost(tids[2])
            assert row_b == d["row_bytes"] and kv_b == d["kv_bytes"] and n_k == _ceil(S, s) and n_a == _ceil(S, a)
            assert 1 <= s < S and n_k > 1 and u.count == (sc.copies // rep) * n_a * n_k
            assert u.covers == {sc.id: sc.macs(), sm.id: sm.work, pv.id: pv.macs()}
            n_el = S * sc.copies * (DHv + 2)
            assert u.partial_out == {pv.id: n_el * n_k} and not u.partial_in
            r = _attn_kvsplit_shape(ctx, S, DH, DHv, ex_sc, ex_pv, sm.work_per_copy // int(sm.statics["Q"]),
                                    row_b, kv_b, a, s, rep)
            assert r is not None, "key-split attention block is not legal"
            _, work, imp = r
            return imp, sc.copies * n_k * S * row_b + (sc.copies // rep) * n_a * S * kv_b, work, work
        a, gens = d["a"], d["gens"]
        tok = gw = 0
        for tid, f in zip(tids, gens):
            if f:
                assert ctx.gen_ok(tid)
                tok += ctx.gen_bytes(tid)
                gw += ctx.gen_work(tid)
        row_b = 0 if gens[0] else DH * ctx.import_cost(tids[0])
        fixed = tok + (0 if gens[1] else S * DH * ctx.import_cost(tids[1])) + (0 if gens[2] else DHv * S * ctx.import_cost(tids[2]))
        n_a = _ceil(S, a)
        assert u.count == (sc.copies // rep) * n_a
        assert u.covers == {sc.id: sc.macs(), sm.id: sm.work, pv.id: pv.macs()}
        wpr = S * (DH + ex_sc) + sm.work_per_copy // int(sm.statics["Q"]) + DHv * (S + ex_pv)
        work = rep * a * wpr + gw
        return rep * a * row_b + fixed, sc.copies * S * row_b + (sc.copies // rep) * n_a * fixed, work, work
    if u.kind == "attn-bwd":
        sc, sm, dP, ds, dQ, dK, dV = (g.ops[i] for i in u.ops)
        cons = _consumer_map(g)
        pat = _detect_attn_bwd(ctx, ds, cons)
        assert pat is not None and all(pat[k] is o for k, o in zip(("sc", "sm", "dP", "dQ", "dK", "dV"), (sc, sm, dP, dQ, dK, dV))), \
            "attention backward pattern not re-detected"
        S, _, DH, _, ex_sc = _matmul_shape(sc)
        ex_dP, ex_dQ, ex_dK, ex_dV = (_matmul_shape(o)[4] for o in (dP, dQ, dK, dV))
        a, mode, nseg = d["a"], d["mode"], d["nseg"]
        assert mode == "chain" or ctx.recompute
        n_a = _ceil(S, a)
        assert nseg == pat["rep"] * n_a and u.count == sc.copies * n_a
        q_t, k_t = _matmul_operand_tids(sc)
        dO_t, v_t = _matmul_operand_tids(dP)
        assert (q_t, k_t, v_t, dO_t) == (d["q_tid"], d["k_tid"], d["v_tid"], d["dO_tid"])
        row_b = DH * (ctx.import_cost(q_t) + ctx.import_cost(dO_t))
        fixed = S * DH * (ctx.import_cost(k_t) + ctx.import_cost(v_t))
        if mode == "chain" and nseg > 1:
            fixed += 2 * GAMMA * S * DH
        if mode == "star" and nseg > 1:
            assert u.partial_out == {dK.id: u.count * S * DH, dV.id: u.count * S * DH}
        assert u.covers == {sc.id: sc.macs(), sm.id: sm.work, dP.id: dP.macs(), ds.id: ds.work, dQ.id: dQ.macs(),
                            dK.id: dK.macs(), dV.id: dV.macs()}
        wpr = (S * (DH + ex_sc) + sm.work_per_copy // int(sm.statics["Q"]) + S * (DH + ex_dP)
               + ds.work_per_copy // int(ds.statics["Q"]) + DH * (S + ex_dQ) + 2 * S * DH)
        work = a * wpr + 2 * S * DH * max(ex_dK, ex_dV)
        return a * row_b + fixed, sc.copies * (S * row_b + n_a * fixed), work, work
    return None


__all__ = ["upper_bound", "check_plan", "UpperBound", "Plan", "Unit", "classify_op", "GAMMA"]
