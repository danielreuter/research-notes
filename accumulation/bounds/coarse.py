"""Coarse constructive upper bounds ``U >= I*(C; F, G)`` under the corrected policy (no per-RU input cap).

Policy.  An RU ``R`` is legal iff ``Work(R) <= G`` and ``Work(Up_R(g)) <= F`` for every gate ``g`` of ``R``
(``Up_R(g)``: ``g`` plus everything upstream of it along wires whose both ends lie in ``R``).  A partition is
legal iff every RU is legal **and the RU quotient graph is acyclic** (SPEC §0 / ``docs/PROTOCOL.md``: every RU
is replayed against its committed inputs, so its inputs must exist before it runs; equivalently every RU is
convex in the gate DAG).  Its runtime input ``I(R)`` is the width of every value produced outside ``R`` and
consumed inside plus the exogenous ingress it reads; ``fixed`` root leaves are free, every other root leaf
(``accumulated`` / ``carried`` / ``token`` / ``seed``) and every cross-RU op output is charged once per RU that
reads it.  ``I(Pi) = sum_R I(R)``.

Unit model.  A *member* is ``(op, mode, lo, hi)``:

* ``whole`` -- every copy of the op;
* ``rows``  -- rows ``[lo, hi)`` of a row-parallel kernel (one ``batch`` over rows; the row model is *derived
  from the kernel's definition*, not from a table): row ``r`` reads row ``r`` of each axis-0 operand and the whole
  of each shared operand, and produces output row ``r``;
* ``inst``  -- scope instances ``[lo, hi)`` of an op that lives inside enclosing ``batch`` scopes (attention per
  sequence / per head): one instance is the op node for one member of every enclosing batch;
* ``irows`` -- instance rows ``[lo, hi)`` of a row-parallel kernel inside a batch, in instance-major global
  row coordinates (``instance * rows + row``): the rows of expert ``e`` (instance ``e`` of the batched
  ``ExpertMlp``) that belong to a token chunk;
* ``red``   -- rows ``[lo, hi)`` of the *contraction* axis of a token reduction (``AccMatmulTT`` -- the weight
  gradient ``dW = dY^T X`` -- and ``AccColSumBatch``).  The kernel's per-output accumulation chain is cut at the
  slice boundaries: the unit holding slice ``j > 0`` imports the 32-bit running accumulator from the unit
  holding slice ``j - 1`` (free when it is the same unit) and the unit holding the last slice produces the op's
  (rounded) output.

A unit is a set of members; a plan is a list of units that must cover every op of the graph exactly once
(``rows`` / ``inst`` / ``red`` slices of one op must tile its rows / instances / contraction axis).

Checker.  :func:`check_coarse_plan` recomputes everything from the :class:`OpGraph` and the program:

* the leaves each member reads are obtained by *resolving the member's argument windows through the program*
  (the same machinery the extractor uses, kept exact per scope instance) to ``(tensor, instance, [lo, hi))``
  boxes; a box is internal iff the producing ``(op, instance)`` rows are produced by a member of the same unit,
  otherwise the whole box is imported (over-approximation is the safe direction; an unresolvable window is
  charged as the whole tensor);
* ``Work(unit) = sum`` of sliced member work (``rows``/``inst``: exact fraction; ``red``: fraction plus the
  accumulator init / round of every partial);
* ``Up`` is bounded at member granularity by the total work of the member's ancestors in the DAG of *internal*
  edges (a whole ancestor member is counted even when only part of it feeds the gate -- conservative; every
  member overlapping an imported window is an ancestor too, so a partly internal window never hides work).
  The planner cuts every unit's members per sequence (``c = 1``), so a unit holding ``m`` layers x all
  tokens has ``Work = m`` layers x ``Q`` but ``Up = m`` layers x one sequence -- exactly the gate-level truth
  for a forward pass (attention couples tokens within a sequence only), and what lets whole-token layer
  chunks be legal under ``F`` while ``G`` alone bounds their size;
* the RU quotient (unit ``u -> v`` iff ``v`` imports an output of ``u``; every imported box and every crossing
  accumulator is traced to the member(s) producing it) is topologically sorted; a cycle is rejected by name;
* ``AssertionError`` on any coverage / tiling / ``G`` / ``F`` / acyclicity violation.

Planner.  :func:`upper_coarse` recognises the circuit's top-level structure generically (root body nodes:
embedding, transformer blocks and their backward composites matched by shared weight windows, LM head, weight
updates -- steps are delimited by the embedding nodes; an MoE forward layer, which the registry inlines at the
root as norm / q k v / attention / o / add / norm / ``AccMoeMlp`` [/ shared expert / add] / add, is the run
of root nodes from the previous layer up to the norm after the MoE MLP) and searches, per policy point, the
*convex* block family (every unit convex by construction, so the quotient is acyclic), per training step:

* forward units: ``m_f`` consecutive layers x ``s_f`` sequences (import the chunk's weights and its bottom
  activation rows; in an MoE layer a token chunk takes, per expert, the ``irows`` of the tokens routed to it
  -- the routing is read off the program by resolving each expert's row blocks to token rows -- so a chunk
  imports the attention / router weights and only the experts its tokens hit); the step's embedding is
  either its own unit or fused into the first layer chunk's units (``emb``);
* backward units: ``m_b`` layers x ``s_b`` sequences (import the chunk's weights, the top gradient rows and --
  because ``AccBlockBwd`` recomputes each layer from its own checkpoint -- one checkpoint row set per layer;
  the recompute gates live in the unit);
* a top-stack unit per sequence chunk: layers ``[L - T, L)`` forward + LM head (+ loss gradient, head dgrad /
  wgrad) + the backward of those layers (``T = 0``: head only) -- the only place a layer's forward and
  backward share a unit, legal because the unit holds everything between them; its forward may start lower
  (``af < L - T``: a forward tail whose backward stays in bwd units -- convex, saves an activation boundary
  while ``F`` is slack);
* weight gradients ``chain`` (``red`` slices in the bwd / top units; the running accumulators cross between
  consecutive sequence units, always forward in sequence order) or ``separate`` (whole per chunk);
  updates ``fused-bwd`` (in the unit completing ``dW``), ``fused-next`` (in the next step's unit first reading
  the new weights) or ``standalone``;
* ``kf > 1`` only as whole-step units (``T = L``, ``s_t = nseq``): fusing steps ``k, k+1`` of a *chunk* is a
  cycle through the rest of step ``k``.

A sequence split of a chunk is offered only when every op of the chunk slices by sequence (or by expert
rows); the parts are additive and optimised independently per ``(T, wgrad, upd, emb)``.  Embeddings of all
steps share one unit when no embedding reads an earlier step's output.  Inference: the whole circuit as one
unit when legal (its only input is the token ids), else the same family without backward (``T = L``: token
chunks through the whole model).  Circuits without recognisable blocks (and block searches that find no legal
candidate) fall back to the cheapest legal partition into contiguous bands of root nodes (a dynamic programme
over the cut positions; contiguous bands of a topological order are convex), then to one op slice per unit;
small forward circuits (<= 64 root nodes) also try the bands as a competitor, since whole-token bands cut
inside a layer can beat layer x token tiles at exact-solver scale.  Every candidate is costed with the
checker's own unit evaluator on representative units (legality is monotone under member inclusion, so the
search prunes upward from the first illegal candidate) and the chosen plan is fully expanded and re-checked,
acyclicity included.  ``plan.detail['anatomy']`` summarises what the adversary does (RU count, work / layers
/ tokens / dynamic-weight / activation / partial bytes per RU, dominant strategy; active experts for MoE; per
unit class -- fwd / top / head / bwd / wgrad / update -- max ``Work`` and ``Up``, ``Up/Work``, imports and
which cap binds: for training the F-bound ``dW`` reduction shows as bwd / top units with ``Up = Work``).  The
search memoises unit evaluations by structure (label + candidate fields), so member lists are only
materialised on a miss; the chosen plan's memoised estimate is recorded as ``detail['planner_cost']`` and
compared with the checked total.

The superseded cyclic family (``fb='joint'`` chunk units -- 2-cycles with the units above them -- and
``kf``-fused chunks) is kept for the comparison table only: ``search=dict(acyclic=False)`` searches it, prints a
loud note, marks the plan ``detail['acyclic'] = False`` / ``detail['checked'] = None``, and the public checker
rejects such plans.

Calibration remark: ``Work`` counts every primitive (softmax, rmsnorm, ... included), so ``fwd`` is calibrated as
the inference circuit's *total work* (SPEC §0; the sweep driver's ``all_work``) -- the whole honest session is
then one legal RU at ``G_hat = 1`` (``adw.all_macs`` is 0.7 % smaller at 8B, 2.3x smaller on tiny2).
"""

from __future__ import annotations

import bisect
import hashlib
import itertools
import math
import sys
from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

from accumulation.graph.opgraph import (Op, OpGraph, _Extractor, _Scope, _compose, _is_terminal, _leaf_range, _parts,
                                        _restrict, _sig, _space_idx)
from verity_ir.defs import SpecializedDefinition
from verity_ir.refs import Affine

ACC_BYTES = 4                     # a running 32-bit accumulator crossing an RU boundary
MODES = ("whole", "rows", "inst", "red", "irows")
_SPAN_CAP = 4096                  # members of one batch a single window may be resolved through exactly
_READS_CACHE_BOXES = 3_000_000   # ~250 MB of (tid, inst, lo, hi) boxes; the planner's candidate slices would otherwise grow the memo without bound
_RES_CACHE_KEYS = 2_000_000      # ~600 MB; resolve() keys are per (scope path, instance, window) so they scale with tokens x candidates
_RES_CACHE_HARD = 3_000_000      # ~900 MB: mid-unit clear (time for memory) so a 131k-token unit stays under the 2.4 GB machine cap
_REDUCE_KERNELS = ("AccMatmulTT", "AccColSumBatch")
_UPDATE_KINDS = frozenset({"sgdupdate", "esupdate", "perturb"})


def _ceil(a: int, b: int) -> int:
    return -(-a // b)


# ---------------------------------------------------------------------------------------------------------
# plan data model
# ---------------------------------------------------------------------------------------------------------

Member = tuple[int, str, int, int]      # (op id, mode, lo, hi)


@dataclass
class CoarseUnit:
    """One replay unit: an explicit set of members.  The statistics are filled in by the checker."""
    members: tuple[Member, ...]
    label: str = ""
    imports_total: int = 0
    work_max: int = 0
    up_max: int = 0
    by_class: dict[str, int] = field(default_factory=dict)
    detail: dict = field(default_factory=dict)
    count: int = 1                      # every coarse unit is explicit (interface parity with ``upper.Unit``)

    @property
    def imports_max(self) -> int:
        return self.imports_total

    @property
    def ops(self) -> tuple[int, ...]:
        return tuple(sorted({m[0] for m in self.members}))

    @property
    def work(self) -> int:
        return self.work_max


@dataclass
class CoarsePlan:
    units: list[CoarseUnit]
    F: int
    G: Optional[int]
    notes: list[str] = field(default_factory=list)
    detail: dict = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(u.imports_total for u in self.units)

    @property
    def n_units(self) -> int:
        return len(self.units)

    @property
    def by_class(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for u in self.units:
            for k, v in u.by_class.items():
                out[k] = out.get(k, 0) + v
        return out

    def ru_stats(self) -> dict:
        """RU-count diagnostics: number of RUs, mean / max runtime input, mean / max work, max ``Up`` bound."""
        n = self.n_units
        return dict(n_ru=n,
                    input_mean=self.total / n if n else 0.0,
                    input_max=max((u.imports_total for u in self.units), default=0),
                    work_mean=sum(u.work_max for u in self.units) / n if n else 0.0,
                    work_max=max((u.work_max for u in self.units), default=0),
                    up_max=max((u.up_max for u in self.units), default=0))


# ---------------------------------------------------------------------------------------------------------
# kernel row models (derived from the kernel definitions)
# ---------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class _RowModel:
    kind: str                              # rows | red | none
    rows: int = 0                          # row count (rows) / contraction length (red)
    args: tuple[tuple[str, int], ...] = () # per kernel argument: ('row', leaves per row) | ('shared', 0)
    out_per_row: int = 0                   # output leaves per row (rows only)


_NO_MODEL = _RowModel("none")


def _row_model_of(spec) -> _RowModel:
    """Row structure of a terminal kernel, read off its body.  ``rows``: the body is a single ``batch`` over
    ``R`` members whose arguments are the kernel's parameters (axis 0 -> row operand, ``None`` -> shared) and
    whose output is the batch output.  ``red``: the two token reductions of the vocabulary (contraction over
    the leading axis of every operand).  Anything else: ``none`` (only ``whole`` / ``inst`` members)."""
    if not isinstance(spec, SpecializedDefinition):
        return _NO_MODEL
    name = spec.name
    b = spec.bindings
    if name.startswith("AccMatmulTT"):
        return _RowModel("red", int(b["K"]), (("row", int(b["M"])), ("row", int(b["N"]))), 0)
    if name.startswith("AccColSumBatch"):
        return _RowModel("red", int(b["Q"]), (("row", int(b["K"])),), 0)
    try:
        body = spec.body
    except Exception:  # pragma: no cover - defensive
        return _NO_MODEL
    if len(body.nodes) != 1 or body.nodes[0].form != "batch":
        return _NO_MODEL
    nd = body.nodes[0]
    R = int(nd.n)
    if R <= 0:
        return _NO_MODEL
    params = body.params
    ret = body.ret
    if not (isinstance(ret, Affine) and ret.space == "n" and ret.idx == 0 and ret.base == 0
            and ret.count == nd.out.leaves):
        return _NO_MODEL
    args: list[tuple[str, int]] = [("shared", 0)] * len(params)
    seen = set()
    for pi, (a, ax) in enumerate(zip(nd.args, nd.axes)):
        r = a.refs
        if not (isinstance(r, Affine) and r.space == "p" and r.base == 0):
            return _NO_MODEL
        j = r.idx
        if j in seen or j >= len(params) or r.count != params[j][1].leaves:
            return _NO_MODEL
        seen.add(j)
        if ax == 0:
            if r.count % R:
                return _NO_MODEL
            args[j] = ("row", r.count // R)
        elif ax is None:
            args[j] = ("shared", 0)
        else:
            return _NO_MODEL
    if len(seen) != len(params) or nd.out.leaves % R:
        return _NO_MODEL
    return _RowModel("rows", R, tuple(args), nd.out.leaves // R)


# ---------------------------------------------------------------------------------------------------------
# per-op structural information and window resolution through the program
# ---------------------------------------------------------------------------------------------------------

@dataclass
class _OpInfo:
    node: object                 # the body node the op was extracted from
    path: tuple[int, ...]        # scope path (node indices)
    dims: tuple[int, ...]        # member counts of the enclosing batch scopes along ``path`` (outer first)
    mult: int                    # product of ``dims``
    rm: _RowModel                # row model of the kernel (``rows``/``red`` only used for form 'call', mult 1)
    out_leaves: int              # aggregate output leaves (all instances)
    inst_leaves: int             # output leaves of one instance


class _Ctx:
    """Graph + program: op structure, row models, window resolution and member read sets (all memoised)."""

    def __init__(self, g: OpGraph, program) -> None:
        if program is None:
            raise ValueError("upper_coarse / check_coarse_plan need the Verity program (program= or g.program)")
        self.g, self.program = g, program
        self.root = _Scope(program.fn, None, None, 0)
        self.op_by_key = {op.key: op.id for op in g.ops}
        self.info: list[_OpInfo] = [self._info_of(op) for op in g.ops]
        self._res_cache: dict = {}
        self._reads_cache: dict = {}
        self._reads_boxes = 0          # boxes held by _reads_cache; the memo is dropped past _READS_CACHE_BOXES (memory cap)
        self._prefix_cache: dict = {}
        self._term_cache: dict = {}
        self._role = {t.id: (t.role or "fixed") for t in g.tensors if t.kind == "param"}
        # op id -> row granularity at which row / red slices are resolved and cached (set by the planner to the
        # sequence length and by the checker to the gcd of the plan's slice boundaries); a slice is the union
        # of its chunks, so decomposing changes nothing but lets the chunks be reused across slices
        self.row_chunk: dict[int, int] = {}
        self._inst_seq_cache: dict[tuple[int, int, int], bool] = {}
        self._irows_map_cache: dict = {}

    def terminal(self, fn) -> bool:
        key = id(fn)
        hit = self._term_cache.get(key)
        if hit is None:
            hit = self._term_cache[key] = _is_terminal(fn)
        return hit

    # -- structure ------------------------------------------------------------------------------------------
    def _info_of(self, op: Op) -> _OpInfo:
        path, idx = op.key
        scope = self.root
        dims: list[int] = []
        for k in path:
            nd = scope.spec.body.nodes[k]
            if nd.form == "batch":
                dims.append(int(nd.n))
            scope = _Scope(nd.fn, scope, k, 0)
        node = scope.spec.body.nodes[idx]
        mult = 1
        for d in dims:
            mult *= d
        rm = _row_model_of(node.fn) if (node.form == "call" and _is_terminal(node.fn)) else _NO_MODEL
        out_leaves = self.g.tensors[op.out].leaves
        return _OpInfo(node, path, tuple(dims), mult, rm, out_leaves, out_leaves // max(mult, 1))

    def scope_for(self, oid: int, inst: int) -> _Scope:
        """Scope object of instance ``inst`` (outer-major mixed radix over the enclosing batch scopes)."""
        info = self.info[oid]
        members: list[int] = []
        rem = inst
        for d in reversed(info.dims):
            members.append(rem % d)
            rem //= d
        members.reverse()
        scope = self.root
        di = 0
        for k in info.path:
            nd = scope.spec.body.nodes[k]
            m = 0
            if nd.form == "batch":
                m = members[di]
                di += 1
            scope = _Scope(nd.fn, scope, k, m)
        return scope

    @staticmethod
    def _instance_of(scope: _Scope) -> int:
        idx, mul, s = 0, 1, scope
        while s.parent is not None:
            pnode = s.parent.spec.body.nodes[s.node_idx]
            if pnode.form == "batch":
                idx += s.member * mul
                mul *= int(pnode.n)
            s = s.parent
        return idx

    def ops_under(self, prefix: tuple[int, ...]) -> list[int]:
        hit = self._prefix_cache.get(prefix)
        if hit is None:
            n = len(prefix)
            hit = [o.id for o in self.g.ops if o.key[0][:n] == prefix]
            self._prefix_cache[prefix] = hit
        return hit

    def member_work(self, m: Member) -> int:
        oid, mode, lo, hi = m
        op, info = self.g.ops[oid], self.info[oid]
        if mode == "whole":
            return op.work
        if mode == "rows":
            return op.work * (hi - lo) // info.rm.rows
        if mode == "inst":
            return op.work * (hi - lo) // info.mult
        if mode == "irows":
            return op.work * (hi - lo) // (info.mult * info.rm.rows)
        # red: the fraction of the chain plus an accumulator init / round per output of the partial
        return _ceil(op.work * (hi - lo), info.rm.rows) + 2 * info.out_leaves

    # -- resolution -----------------------------------------------------------------------------------------
    def resolve(self, scope: _Scope, part) -> list[tuple[int, Optional[int], int, int]]:
        """``[(tensor id, instance | None, lo, hi)]`` boxes of the leaves ``part`` denotes in ``scope``
        (``instance None``: every instance of the op, whole -- the conservative fallback)."""
        key = (scope.path, self._instance_of(scope), _sig(part))
        hit = self._res_cache.get(key)
        if hit is None:
            hit = list(self._resolve_part(scope, part))
            if len(self._res_cache) >= _RES_CACHE_HARD:     # one huge unit (members x rows) can exceed the between-unit cap: hard stop
                self._res_cache.clear()
            self._res_cache[key] = hit
        return hit

    def _resolve_part(self, scope: _Scope, part):
        space, idx = _space_idx(part)
        lo, hi = _leaf_range(part)
        if space == "p":
            if scope.parent is None:
                yield self.g.root_param_index[idx], 0, lo, hi + 1
                return
            pnode = scope.parent.spec.body.nodes[scope.node_idx]
            base = _Extractor._member_arg_refs(pnode, idx, scope.member)
            yield from self._through(scope.parent, base, part)
            return
        node = scope.spec.body.nodes[idx]
        if node.form == "scan" or self.terminal(node.fn):
            oid = self.op_by_key[(scope.path, idx)]
            yield self.g.ops[oid].out, self._instance_of(scope), lo, hi + 1
            return
        if node.form == "call":
            yield from self._through(_Scope(node.fn, scope, idx, 0), node.fn.body.ret, part)
            return
        assert node.form == "batch", node.form
        L = node.fn.out_leaves
        m0, m1 = lo // L, hi // L
        if m1 - m0 + 1 > _SPAN_CAP:
            for o in self.ops_under(scope.path + (idx,)):
                yield self.g.ops[o].out, None, 0, self.info[o].out_leaves
            return
        for m in range(m0, m1 + 1):
            sub = _restrict(part, m * L, (m + 1) * L)
            if sub.count == 0:
                continue
            child = _Scope(node.fn, scope, idx, m)
            for sp in _parts(sub):
                yield from self._through(child, node.fn.body.ret, sp)

    def _through(self, scope: _Scope, base, part):
        composed, _ok = _compose(base, part)     # inexact composition = bounding window: boxes stay sound
        for sub in _parts(composed):
            yield from self.resolve(scope, sub)

    # -- member read sets -----------------------------------------------------------------------------------
    def reads(self, m: Member, params_only: bool = False) -> list[tuple[int, Optional[int], int, int]]:
        """Boxes read by member ``m`` (all arguments, all instances in its range).  ``params_only``: keep
        only root-parameter boxes (used for ``whole`` members, whose op-output sources are charged whole)."""
        key = (m, params_only)
        hit = self._reads_cache.get(key)
        if hit is not None:
            return hit
        oid, mode, lo, hi = m
        info = self.info[oid]
        node = info.node
        out: list[tuple[int, Optional[int], int, int]] = []
        ch = self.row_chunk.get(oid)
        if mode in ("rows", "red") and ch and hi - lo > ch and lo % ch == 0 and hi % ch == 0:
            for a in range(lo, hi, ch):
                out.extend(self.reads((oid, mode, a, a + ch), params_only))
            return out                 # not memoised: the chunks are, and the concatenation would duplicate them per slice
        if mode in ("rows", "red"):
            scope = self.scope_for(oid, 0)
            for pi, a in enumerate(node.args):
                role, L = info.rm.args[pi]
                refs = a.refs.slice(lo * L, hi * L) if role == "row" else a.refs
                for part in _parts(refs):
                    out.extend(self.resolve(scope, part))
        elif mode == "irows":
            R = info.rm.rows
            if ch and hi - lo > ch and lo % ch == 0 and hi % ch == 0 and R % ch == 0:
                for a in range(lo, hi, ch):
                    out.extend(self.reads((oid, mode, a, a + ch), params_only))
                return out
            for i in range(lo // R, _ceil(hi, R)):
                r0, r1 = max(lo, i * R) - i * R, min(hi, (i + 1) * R) - i * R
                scope = self.scope_for(oid, i)
                for pi, a in enumerate(node.args):
                    role, L = info.rm.args[pi]
                    refs = a.refs.slice(r0 * L, r1 * L) if role == "row" else a.refs
                    for part in _parts(refs):
                        out.extend(self.resolve(scope, part))
        else:
            insts = range(lo, hi) if mode == "inst" else range(info.mult)
            for i in insts:
                scope = self.scope_for(oid, i)
                for a in node.args:
                    for part in _parts(a.refs):
                        out.extend(self.resolve(scope, part))
        if params_only:
            out = [b for b in out if self.g.tensors[b[0]].kind == "param"]
        out = _compact(out)
        if self._reads_boxes + len(out) > _READS_CACHE_BOXES:
            self._reads_cache.clear()
            self._reads_boxes = 0
        self._reads_cache[key] = out
        self._reads_boxes += len(out)
        return out

    def role(self, tid: int) -> Optional[str]:
        return self._role.get(tid)


# ---------------------------------------------------------------------------------------------------------
# unit evaluation and the checker
# ---------------------------------------------------------------------------------------------------------

def _compact(boxes: list[tuple[int, Optional[int], int, int]]) -> list[tuple[int, Optional[int], int, int]]:
    """Merge touching / overlapping boxes of the same ``(tensor, instance)`` (the union is unchanged; a window
    resolved through a batch of per-row pieces comes back as thousands of adjacent boxes)."""
    if len(boxes) < 2:
        return boxes
    by: dict[tuple[int, Optional[int]], list[tuple[int, int]]] = {}
    for tid, inst, a, b in boxes:
        by.setdefault((tid, inst), []).append((a, b))
    out: list[tuple[int, Optional[int], int, int]] = []
    for (tid, inst), iv in by.items():
        if len(iv) == 1:
            out.append((tid, inst, iv[0][0], iv[0][1]))
            continue
        iv.sort()
        lo, hi = iv[0]
        for a, b in iv[1:]:
            if a > hi:
                out.append((tid, inst, lo, hi))
                lo, hi = a, b
            elif b > hi:
                hi = b
        out.append((tid, inst, lo, hi))
    return out


def _merge_iv(iv: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Union of half-open intervals as a sorted disjoint list."""
    iv = sorted(iv)
    out: list[tuple[int, int]] = []
    for a, b in iv:
        if out and a <= out[-1][1]:
            if b > out[-1][1]:
                out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


def _merge(iv: list[tuple[int, int]]) -> int:
    """Total length of the union of half-open intervals."""
    if not iv:
        return 0
    iv.sort()
    tot, lo, hi = 0, iv[0][0], iv[0][1]
    for a, b in iv[1:]:
        if a > hi:
            tot += hi - lo
            lo, hi = a, b
        else:
            hi = max(hi, b)
    return tot + hi - lo


@dataclass
class _RedEnv:
    """Which unit holds the last slice (and therefore produces the rounded output) of every ``red`` op, and --
    when built by :func:`_coverage` -- which unit holds every member of every op (``slices``: op ->
    ``[(lo, hi, unit)]``; ``(0, 0, unit)`` for a ``whole`` member), so that a unit's imports can be traced to the
    units producing them (the RU quotient graph)."""
    last_unit: dict[int, int]                      # op -> unit index holding the last slice
    slices: Optional[dict[int, list[tuple[int, int, int]]]] = None
    modes: Optional[dict[int, str]] = None

    def producers(self, ctx: "_Ctx", tid: int, inst: Optional[int], a: int, b: int) -> set[int]:
        """Units producing (any part of) the box ``(tid, inst, [a, b))`` of an op output."""
        p = ctx.g.tensors[tid].producer
        if p is None or self.slices is None:
            return set()
        sl, mode = self.slices[p], self.modes[p]
        if mode == "whole":
            return {sl[0][2]}
        if inst is None:
            return {ui for _, _, ui in sl}
        if mode == "red":
            return {self.last_unit[p]}
        if mode == "inst":
            return {ui for lo, hi, ui in sl if lo <= inst < hi}
        opr = ctx.info[p].rm.out_per_row or 1                            # rows slices (output-leaf coordinates)
        if mode == "irows":
            off = inst * ctx.info[p].rm.rows
            r0, r1 = off + a // opr, off + _ceil(b, opr)
        else:
            r0, r1 = a // opr, _ceil(b, opr)
        return {ui for lo, hi, ui in sl if lo < r1 and hi > r0}

    def partial_producer(self, oid: int, lo: int) -> set[int]:
        """Unit holding the contraction slice of ``oid`` that ends at ``lo``."""
        if self.slices is None:
            return set()
        return {ui for l, h, ui in self.slices[oid] if h == lo}


@dataclass
class _UnitStats:
    imports: int
    work: int
    up: int
    by_class: dict[str, int]
    sources: frozenset[int] = frozenset()          # units whose outputs this unit imports (needs ``_RedEnv.slices``)


def _class_of(ctx: _Ctx, tid: int) -> str:
    t = ctx.g.tensors[tid]
    if t.kind == "param":
        r = t.role or "fixed"
        return "tokens" if r == "token" else ("weights" if r in ("accumulated", "carried") else "other")
    p = ctx.g.ops[t.producer]
    return "weights" if p.kind in _UPDATE_KINDS else "activations"


def _validate_member(ctx: _Ctx, m: Member) -> None:
    oid, mode, lo, hi = m
    assert 0 <= oid < len(ctx.g.ops), f"unknown op {oid}"
    assert mode in MODES, f"op {oid}: unknown member mode {mode!r}"
    info = ctx.info[oid]
    if mode == "whole":
        return
    assert 0 <= lo < hi, f"op {oid}: empty slice [{lo}, {hi})"
    if mode == "inst":
        assert info.mult > 1 and hi <= info.mult, f"op {oid}: instance slice [{lo}, {hi}) outside [0, {info.mult})"
    elif mode == "rows":
        assert info.rm.kind == "rows" and info.mult == 1, f"op {oid} ({ctx.g.ops[oid].fn_id}) has no row model"
        assert hi <= info.rm.rows, f"op {oid}: row slice [{lo}, {hi}) outside [0, {info.rm.rows})"
    elif mode == "irows":
        assert info.rm.kind == "rows" and info.mult > 1, f"op {oid} ({ctx.g.ops[oid].fn_id}) is not a batched row kernel"
        assert hi <= info.mult * info.rm.rows, \
            f"op {oid}: instance-row slice [{lo}, {hi}) outside [0, {info.mult * info.rm.rows})"
    else:
        assert info.rm.kind == "red" and info.mult == 1, f"op {oid} ({ctx.g.ops[oid].fn_id}) is not a token reduction"
        assert hi <= info.rm.rows, f"op {oid}: contraction slice [{lo}, {hi}) outside [0, {info.rm.rows})"
        ch = ctx.g.ops[oid].statics.get("CH")
        if ch:
            assert lo % int(ch) == 0 and (hi % int(ch) == 0 or hi == info.rm.rows), \
                f"op {oid}: contraction slice [{lo}, {hi}) not aligned to CH={ch}"


def _eval_unit(ctx: _Ctx, unit: CoarseUnit, uidx: int, red: _RedEnv, F: Optional[int] = None) -> _UnitStats:
    """Recompute imports / work / Up bound of one unit from the graph (see the module docstring)."""
    g = ctx.g
    if len(ctx._res_cache) > _RES_CACHE_KEYS:     # per-instance resolve keys scale with tokens x candidates: bound the memo between units
        ctx._res_cache.clear()
    members = list(unit.members)
    # canonical order: op id (topological), then slice start -- every internal predecessor precedes its consumer
    members.sort(key=lambda m: (m[0], m[2]))
    n = len(members)
    produced_all: dict[int, int] = {}                 # op -> member index producing its whole output here
    rows_by_op: dict[int, list[tuple[int, int, int]]] = {}
    irows_by_op: dict[int, list[tuple[int, int, int]]] = {}
    inst_by_op: dict[int, list[tuple[int, int, int]]] = {}
    red_end: dict[tuple[int, int], int] = {}          # (op, hi) -> member holding the slice ending at hi
    for mi, (oid, mode, lo, hi) in enumerate(members):
        info = ctx.info[oid]
        if mode == "whole":
            assert oid not in produced_all, f"unit {uidx}: op {oid} appears twice"
            produced_all[oid] = mi
        elif mode == "rows":
            rows_by_op.setdefault(oid, []).append((lo * info.rm.out_per_row, hi * info.rm.out_per_row, mi))
        elif mode == "irows":       # global (instance-major) output-leaf coordinates
            irows_by_op.setdefault(oid, []).append((lo * info.rm.out_per_row, hi * info.rm.out_per_row, mi))
        elif mode == "inst":
            inst_by_op.setdefault(oid, []).append((lo, hi, mi))
        else:
            red_end[(oid, hi)] = mi
            if red.last_unit.get(oid) == uidx and hi == info.rm.rows:
                produced_all[oid] = mi
    work = [ctx.member_work(m) for m in members]
    preds: list[set[int]] = [set() for _ in range(n)]
    ext: dict[tuple[int, Optional[int]], list[tuple[int, int]]] = {}
    ext_whole: set[int] = set()
    by_class: dict[str, int] = {}
    sources: set[int] = set()

    def charge(tid: int, inst: Optional[int], a: int, b: int) -> None:
        if inst is None:
            ext_whole.add(tid)
        else:
            ext.setdefault((tid, inst), []).append((a, b))

    starts: dict[int, list[int]] = {}
    for d in (rows_by_op, irows_by_op, inst_by_op):
        for sl in d.values():
            sl.sort()
    for d in (rows_by_op, irows_by_op, inst_by_op):
        for p, sl in d.items():
            starts[id(sl)] = [r0 for r0, _, _ in sl]

    def covered(sl: list[tuple[int, int, int]], a: int, b: int, mi: int) -> bool:
        """Is ``[a, b)`` covered by the union of the (disjoint, sorted) slices ``sl``?  Every overlapping
        member becomes a predecessor of ``mi`` (sound ``Up`` even when the window is only partly produced
        here -- the uncovered rest is then charged as an import); a unit's members tile the op, so a window
        produced by several of them (every sequence of a whole-token unit cut per sequence) is internal."""
        i = bisect.bisect_right(starts[id(sl)], a) - 1
        if i < 0:
            i = 0
        cur = a
        full = True
        for r0, r1, mj in sl[i:]:
            if r0 >= b:
                break
            if r1 <= cur:
                continue
            if r0 > cur:
                full = False
            preds[mi].add(mj)
            cur = max(cur, r1)
        return full and cur >= b

    def internal(tid: int, inst: Optional[int], a: int, b: int, mi: int) -> bool:
        p = g.tensors[tid].producer
        if p is None:
            return False
        pm = produced_all.get(p)
        if pm is not None:
            preds[mi].add(pm)
            return True
        pinfo = ctx.info[p]
        if inst is None:                      # the whole tensor: every instance / every row must be here
            if p in rows_by_op:
                return pinfo.mult == 1 and covered(rows_by_op[p], 0, pinfo.out_leaves, mi)
            if p in irows_by_op:
                return covered(irows_by_op[p], 0, pinfo.out_leaves, mi)
            if p in inst_by_op:
                return covered(inst_by_op[p], 0, pinfo.mult, mi)
            return False
        sl = rows_by_op.get(p)
        if sl and inst == 0 and covered(sl, a, b, mi):
            return True
        ir = irows_by_op.get(p)
        if ir:
            off = inst * pinfo.inst_leaves
            if covered(ir, off + a, off + b, mi):
                return True
        il = inst_by_op.get(p)
        if il and covered(il, inst, inst + 1, mi):
            return True
        return False

    for mi, m in enumerate(members):
        oid, mode, lo, hi = m
        op = g.ops[oid]
        if mode == "whole":
            need_params = False
            for e in op.inputs:
                t = g.tensors[e.src]
                if t.kind == "param":
                    if (t.role or "fixed") != "fixed":
                        need_params = True
                    continue
                if not internal(e.src, None, 0, t.leaves, mi):
                    charge(e.src, None, 0, t.leaves)
            if need_params:
                for tid, inst, a, b in ctx.reads(m, params_only=True):
                    if (g.tensors[tid].role or "fixed") != "fixed":
                        charge(tid, 0, a, b)
            continue
        for tid, inst, a, b in ctx.reads(m):
            t = g.tensors[tid]
            if t.kind == "param":
                if (t.role or "fixed") != "fixed":
                    charge(tid, 0, a, b)
                continue
            if not internal(tid, inst, a, b, mi):
                charge(tid, inst, a, b)
        if mode == "red" and lo > 0:
            # the running accumulator of the previous contraction slice: internal iff that slice is here
            pm = red_end.get((oid, lo))
            if pm is not None:
                preds[mi].add(pm)
            else:
                bytes_ = ctx.info[oid].out_leaves * ACC_BYTES
                by_class["partials"] = by_class.get("partials", 0) + bytes_
                sources |= red.partial_producer(oid, lo)
    imports = 0
    trace = red.slices is not None
    for (tid, inst), iv in ext.items():
        if tid in ext_whole:
            continue
        merged = _merge_iv(iv)
        b = sum(hi - lo for lo, hi in merged) * g.tensors[tid].width // 8
        imports += b
        c = _class_of(ctx, tid)
        by_class[c] = by_class.get(c, 0) + b
        if trace:
            for a, bb in merged:
                sources |= red.producers(ctx, tid, inst, a, bb)
    for tid in ext_whole:
        b = g.tensors[tid].bytes
        imports += b
        c = _class_of(ctx, tid)
        by_class[c] = by_class.get(c, 0) + b
        if trace:
            sources |= red.producers(ctx, tid, None, 0, g.tensors[tid].leaves)
    imports += by_class.get("partials", 0)
    sources.discard(uidx)
    total_work = sum(work)
    # Up bound: ancestors in the internal DAG; the maximum is attained at sinks
    up = total_work
    if F is None or total_work > F:
        succ = [False] * n
        anc = [0] * n
        for mi in range(n):
            a = 0
            for pj in preds[mi]:
                a |= anc[pj] | (1 << pj)
                succ[pj] = True
            anc[mi] = a
        up = 0
        for mi in range(n):
            if succ[mi]:
                continue
            a, tot = anc[mi], work[mi]
            while a:
                low = a & -a
                tot += work[low.bit_length() - 1]
                a ^= low
            up = max(up, tot)
    return _UnitStats(imports, total_work, up, by_class, frozenset(sources))


def _coverage(ctx: _Ctx, plan: CoarsePlan) -> _RedEnv:
    """Every op exactly once (tiled slices); build the reduction-chain environment."""
    g = ctx.g
    seen: dict[int, list[tuple[str, int, int, int]]] = {}
    for ui, u in enumerate(plan.units):
        assert u.members, f"unit {ui} is empty"
        for m in u.members:
            _validate_member(ctx, m)
            seen.setdefault(m[0], []).append((m[1], m[2], m[3], ui))
    last_unit: dict[int, int] = {}
    slices: dict[int, list[tuple[int, int, int]]] = {}
    modes: dict[int, str] = {}
    for op in g.ops:
        sl = seen.get(op.id)
        assert sl, f"op {op.id} ({op.fn_id}) is not covered by any unit"
        ms = {s[0] for s in sl}
        assert len(ms) == 1, f"op {op.id}: mixed member modes {sorted(ms)}"
        mode = sl[0][0]
        modes[op.id] = mode
        if mode == "whole":
            assert len(sl) == 1, f"op {op.id}: whole member in {len(sl)} units"
            slices[op.id] = [(0, 0, sl[0][3])]
            continue
        info = ctx.info[op.id]
        total = info.mult if mode == "inst" else (info.mult * info.rm.rows if mode == "irows" else info.rm.rows)
        sl.sort(key=lambda s: s[1])
        pos = 0
        for _, lo, hi, ui in sl:
            assert lo == pos, f"op {op.id}: {mode} slices do not tile (gap/overlap at {pos}, next slice starts {lo})"
            pos = hi
        assert pos == total, f"op {op.id}: {mode} slices cover [0, {pos}) of {total}"
        slices[op.id] = [(lo, hi, ui) for _, lo, hi, ui in sl]
        if mode == "red":
            last_unit[op.id] = sl[-1][3]
    return _RedEnv(last_unit, slices, modes)


def _find_cycle(n: int, succ: list[set[int]]) -> list[int]:
    """One directed cycle of the unit quotient (unit indices, first == last); ``[]`` if acyclic."""
    indeg = [0] * n
    for u in range(n):
        for v in succ[u]:
            indeg[v] += 1
    stack = [u for u in range(n) if indeg[u] == 0]
    seen = 0
    while stack:
        u = stack.pop()
        seen += 1
        for v in succ[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                stack.append(v)
    if seen == n:
        return []
    alive = {u for u in range(n) if indeg[u] > 0}    # every surviving node has a surviving predecessor
    pred: dict[int, list[int]] = {u: [] for u in alive}
    for u in alive:
        for v in succ[u]:
            if v in alive:
                pred[v].append(u)
    start = min(alive)
    path, on_path = [start], {start: 0}
    u = start
    while True:                                       # walk predecessors until a node repeats: that is a cycle
        v = min(pred[u])
        if v in on_path:
            cyc = path[on_path[v]:] + [v]
            cyc.reverse()                             # predecessor walk -> edge order
            return cyc
        on_path[v] = len(path)
        path.append(v)
        u = v


def _assert_acyclic(plan: CoarsePlan, sources: list[frozenset[int]]) -> list[int]:
    """The RU quotient (unit ``u`` -> unit ``v`` iff ``v`` imports an output of ``u``) must be acyclic:
    every RU is replayed against its committed inputs, so its inputs must exist before it runs (SPEC §0,
    ``docs/PROTOCOL.md``).  Returns a topological order of the units."""
    n = len(plan.units)
    succ: list[set[int]] = [set() for _ in range(n)]
    for v, src in enumerate(sources):
        for u in src:
            if u != v:
                succ[u].add(v)
    cyc = _find_cycle(n, succ)
    if cyc:
        names = " -> ".join(f"{u} ({plan.units[u].label})" if plan.units[u].label else str(u) for u in cyc)
        raise AssertionError(f"RU quotient is cyclic ({len(cyc) - 1} units): {names}")
    indeg = [0] * n
    for u in range(n):
        for v in succ[u]:
            indeg[v] += 1
    order, stack = [], [u for u in range(n) if indeg[u] == 0]
    while stack:
        u = stack.pop()
        order.append(u)
        for v in succ[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                stack.append(v)
    return order


def _evaluate_plan(ctx: _Ctx, plan: CoarsePlan, F: int, G: Optional[int], *, legality: bool = True,
                   acyclic: bool = True) -> None:
    """Shared body of :func:`check_coarse_plan`: coverage, per-unit statistics, ``G`` / ``F`` legality
    (``legality``) and acyclicity of the RU quotient (``acyclic``; disabled only by the planner's explicit
    ``search=dict(acyclic=False)`` comparison mode, never by the public checker)."""
    red = _coverage(ctx, plan)
    sources: list[frozenset[int]] = []
    for ui, u in enumerate(plan.units):
        st = _eval_unit(ctx, u, ui, red, F)
        if legality:
            assert G is None or st.work <= G, f"unit {ui} ({u.label}): work {st.work} > G={G}"
            assert st.up <= F, f"unit {ui} ({u.label}): Up bound {st.up} > F={F}"
        u.imports_total, u.work_max, u.up_max, u.by_class = st.imports, st.work, st.up, st.by_class
        sources.append(st.sources)
    if acyclic:
        _assert_acyclic(plan, sources)
        plan.detail["acyclic"] = True
    else:
        try:
            _assert_acyclic(plan, sources)
            plan.detail["acyclic"] = True
        except AssertionError as e:
            plan.detail["acyclic"] = False
            plan.detail["cycle"] = str(e)


def check_coarse_plan(g: OpGraph, plan: CoarsePlan, F: int, G: Optional[int], *, program=None, _ctx: Optional[_Ctx] = None) -> None:
    """Recompute every unit's inputs / work / ``Up`` bound from the graph and assert legality: ``Work <= G``
    and ``Up <= F`` per unit **and an acyclic RU quotient** (unit -> unit edges from cross-unit reads, traced
    to the producing members; a cycle is reported by name).  Fills in the unit statistics and
    ``plan.detail['checked']``.  ``AssertionError`` on any violation.  ``_ctx``: reuse a resolver context (its
    caches hold graph-derived windows only; nothing planner-side is trusted).

    **What the ``Up`` check trusts.**  Nothing planner-side except the *cut*: the plan says which
    ``(op, slice)`` members exist and in which unit.  The dependency edges between members are *not* taken
    from the plan -- every member's operand windows are resolved through the program to the producing
    ``(op, instance, rows)`` (attention's within-sequence coupling, the residual stream, router / expert
    gathers included: these are the real operand reads of the kernels, not a per-sequence assumption), and
    a member that produces any part of a window read by ``u`` is an ancestor of ``u``.  ``Up(u)`` is the
    total work of ``u`` and its ancestors in that DAG; a unit's ``Up`` is the maximum over its members.  This
    dominates the gate-level ``work(Up_R(g))`` for every gate ``g`` of the unit: a gate upstream of ``g``
    inside ``R`` lies in some member, and the wire that reaches it is one of the resolved reads, so its
    whole member is counted.  The cut only sets the *granularity* -- a coarser cut (whole ops) counts more
    ancestors, never fewer -- so a plan with per-sequence members is tighter but exactly as sound as one
    with whole-op members.  :func:`gate_level_up` is the independent path: it expands a unit to gates and
    takes ``max_g`` of a BFS over the flattened circuit's real operand wires (the exact module's ``up_set``);
    ``results/up_independence.md`` records checker ``Up >= `` gate-level ``Up`` on every tiny2 / tiny-moe
    rollout and local-sgd cell tried (1.3-40x conservative), with ``Work`` equal to the gate sum up to the
    accumulator inits / rounds the checker adds for cut ``red`` chains.

    When ``F`` binds.  A forward unit of ``m`` layers x ``s`` sequences has ``Up = m`` layers x *one*
    sequence (attention never couples sequences), so ``F`` binds a forward RU iff
    ``seq * m * w_layer(per token) [+ head] > F``, i.e. ``m / L > F_hat * Q_inf / seq``; at
    ``F = 1.5 fwd(Q_inf)`` with ``seq = Q_inf`` that is ``m > 1.5 L``: never, and ``G`` alone sizes forward
    tiles (``F`` starts to bind only when one sequence is longer than ``F_hat * Q_inf`` tokens, e.g.
    ``seq >= 12288`` at the default point with ``m = L``).  A training unit holding a weight-gradient
    reduction (``dW = dY^T X`` over its tokens) couples every sequence it holds: ``Up`` of that gate is the
    whole unit's upstream (all sequences' backward + recompute, the top gradient, everything the chain reads),
    so ``F`` binds a bwd / top unit as soon as its tokens x layers of backward work exceed ``F``; splitting
    the chain by sequence (``red`` slices, ``wgrad='chain'``) moves the coupling into the running
    accumulator, which the next slice's unit imports -- the structural cost of training under ``F``."""
    ctx = _ctx if _ctx is not None else _Ctx(g, program if program is not None else getattr(g, "program", None))
    Gi = None if G is None else int(G)
    Fi = int(F)
    _evaluate_plan(ctx, plan, Fi, Gi, legality=True, acyclic=True)
    plan.detail["checked"] = {"F": Fi, "G": Gi, "total": plan.total, "n_units": plan.n_units, "acyclic": True}


def check_plan(plan: CoarsePlan, g: OpGraph, *, F: int, G: Optional[int] = None, X=None, program=None) -> None:
    """Keyword-style alias of :func:`check_coarse_plan` (the sweep driver's calling convention; ``X`` ignored)."""
    check_coarse_plan(g, plan, F, G, program=program)


# ---------------------------------------------------------------------------------------------------------
# circuit structure (root body)
# ---------------------------------------------------------------------------------------------------------

@dataclass
class _Layer:
    fwd: list[int]                 # root node indices (forward composite(s))
    bwd: list[int] = field(default_factory=list)
    upd: list[int] = field(default_factory=list)


@dataclass
class _Step:
    embed: list[int]
    layers: list[_Layer]
    head: list[int]                # root nodes between the last forward block and the first backward block
    head_upd: list[int]
    other: list[int]               # anything else inside the step (whole units of their own)
    Q: int
    S: int

    @property
    def nseq(self) -> int:
        return max(1, self.Q // self.S) if self.S else 1


@dataclass
class _Struct:
    steps: list[_Step]
    prologue: list[int]
    ops_by_root: dict[int, list[int]]
    names: list[str]
    generic: bool                  # True when no transformer blocks were recognised (band fallback)


def _root_name(nd) -> str:
    fn = nd.fn
    return getattr(fn, "name", None) or getattr(fn, "id", "?")


def _discover(ctx: _Ctx) -> _Struct:
    g, fn = ctx.g, ctx.program.fn
    nodes = fn.body.nodes
    names = [_root_name(nd) for nd in nodes]
    ops_by_root: dict[int, list[int]] = {i: [] for i in range(len(nodes))}
    for op in g.ops:
        r = op.key[0][0] if op.key[0] else op.key[1]
        ops_by_root[r].append(op.id)
    is_embed = [n.startswith("AccEmbed") for n in names]
    is_fwd = [("Block" in n and "Bwd" not in n) for n in names]
    is_bwd = [("Block" in n and "Bwd" in n) for n in names]
    is_upd = [n.startswith(("AccSgdUpdate", "AccEsUpdate")) for n in names]
    # an MoE forward layer is inlined at the root (norm, q/k/v, attention, o, add, norm, AccMoeMlp, [shared
    # expert, add], add): the run of root nodes from the previous layer / embedding up to the norm that
    # follows the MoE MLP is one layer
    is_moe = [(n.startswith("AccMoeMlp") and "Bwd" not in n) for n in names]
    if not any(is_fwd) and not any(is_moe):
        return _Struct([], list(range(len(nodes))), ops_by_root, names, True)
    starts = [i for i, e in enumerate(is_embed) if e] or [0]
    # a step must contain forward blocks; embeddings without blocks after them are merged into the next segment
    segs: list[tuple[int, int]] = []
    for si, a in enumerate(starts):
        b = starts[si + 1] if si + 1 < len(starts) else len(nodes)
        if segs and not any(is_fwd[segs[-1][0]:segs[-1][1]]) and not any(is_moe[segs[-1][0]:segs[-1][1]]):
            segs[-1] = (segs[-1][0], b)
        else:
            segs.append((a, b))
    prologue = list(range(0, segs[0][0]))
    steps: list[_Step] = []
    for a, b in segs:
        fwd = [i for i in range(a, b) if is_fwd[i]]
        bwd = [i for i in range(a, b) if is_bwd[i]]
        emb = [i for i in range(a, b) if is_embed[i]]
        upd = [i for i in range(a, b) if is_upd[i]]
        groups: list[tuple[int, int]] = []
        cursor = a
        for m in [i for i in range(a, b) if is_moe[i]]:
            st_ = max([cursor] + [i + 1 for i in range(a, m) if is_fwd[i] or is_embed[i] or is_bwd[i]])
            en = next((i for i in range(m + 1, b) if names[i].startswith("AccRmsNormBatch") or is_fwd[i]
                       or is_embed[i] or is_bwd[i] or is_upd[i]), b)
            groups.append((st_, en))
            cursor = en
        if not fwd and not groups:
            steps.append(_Step(emb, [], [], [], [i for i in range(a, b) if not is_embed[i]], 0, 0))
            continue
        layers = sorted([_Layer([f]) for f in fwd] + [_Layer(list(range(s_, e_))) for s_, e_ in groups],
                        key=lambda L: L.fwd[0])
        fwd = sorted(fwd + [i for s_, e_ in groups for i in range(s_, e_)])
        # match backward composites to forward blocks by shared weight argument windows
        wsig = [frozenset(_sig(x.refs) for r in L.fwd for x in nodes[r].args[1:]) for L in layers]
        unmatched = []
        for bi in bwd:
            bs = frozenset(_sig(x.refs) for x in nodes[bi].args)
            best, score = None, 0
            for li, ws in enumerate(wsig):
                sc = len(ws & bs)
                if sc > score:
                    best, score = li, sc
            if best is None:
                unmatched.append(bi)
            else:
                layers[best].bwd.append(bi)
        if unmatched:   # fall back to reverse program order
            for li, bi in zip(reversed(range(len(layers))), unmatched):
                layers[li].bwd.append(bi)
        first_bwd = min(bwd) if bwd else b
        last_fwd = max(fwd)
        head = [i for i in range(last_fwd + 1, first_bwd) if not (is_upd[i] or is_embed[i])]
        root_of_layer = {}
        for li, L in enumerate(layers):
            for r in L.fwd + L.bwd:
                root_of_layer[r] = li
        head_set = set(head)
        head_upd: list[int] = []
        other: list[int] = []
        for ui in upd:
            src = None
            for x in nodes[ui].args:
                r = x.refs
                if isinstance(r, Affine) and r.space == "n" and (r.idx in root_of_layer or r.idx in head_set):
                    src = r.idx
                    break
            if src is None:
                other.append(ui)
            elif src in root_of_layer:
                layers[root_of_layer[src]].upd.append(ui)
            else:
                head_upd.append(ui)
        known = set(fwd) | set(bwd) | set(emb) | set(upd) | head_set
        other += [i for i in range(a, b) if i not in known]
        Q, S = 0, 0
        for r in layers[0].fwd:                                   # a composite block carries Q and S (T: decode)
            st = nodes[r].fn.bindings if isinstance(nodes[r].fn, SpecializedDefinition) else {}
            if not Q and "Q" in st:
                Q = int(st["Q"])
            if not S and ("T" in st or "S" in st):
                S = int(st["T"]) if "T" in st else int(st["S"])
        if Q <= 0 or S <= 0 or Q % S:
            S = max(Q, 1)
        steps.append(_Step(emb, layers, head, head_upd, other, Q, S))
    return _Struct(steps, prologue, ops_by_root, names, False)


# ---------------------------------------------------------------------------------------------------------
# unit construction
# ---------------------------------------------------------------------------------------------------------

def _slice_op(ctx: _Ctx, oid: int, s0: int, s1: int, S: int, nseq: int, first: bool) -> list[Member]:
    """Members of op ``oid`` restricted to sequences ``[s0, s1)`` (``S`` rows each, ``nseq`` total); ``[]``
    when the op cannot be sliced and this is not the first sequence unit (which then takes it whole).
    Batched row kernels whose instances are not sequences (MoE experts: instance ``e`` = expert ``e`` over the
    tokens routed to it) are cut by instance rows: the rows of every expert that belong to the chunk's
    sequences (possibly several members)."""
    if s0 == 0 and s1 >= nseq:
        return [(oid, "whole", 0, 0)]
    info = ctx.info[oid]
    if info.mult > 1:
        if info.mult % nseq == 0 and _inst_is_seq(ctx, oid, S, nseq):
            per = info.mult // nseq
            return [(oid, "inst", s0 * per, min(s1, nseq) * per)]
        if info.rm.kind == "rows":
            ms = _irows_members(ctx, oid, s0, s1, S, nseq)
            if ms is not None:
                return ms
        return [(oid, "whole", 0, 0)] if first else []
    rm = info.rm
    Q = S * nseq
    if rm.kind in ("rows", "red") and rm.rows == Q:
        ctx.row_chunk.setdefault(oid, S)
    if rm.kind == "rows" and rm.rows == Q:
        return [(oid, "rows", s0 * S, min(s1, nseq) * S)]
    if rm.kind == "red" and rm.rows == Q:
        lo, hi = s0 * S, min(s1, nseq) * S
        if _red_aligned(ctx, oid, lo) and (hi == Q or _red_aligned(ctx, oid, hi)):
            return [(oid, "red", lo, hi)]
    return [(oid, "whole", 0, 0)] if first else []


def _irows_seq_map(ctx: _Ctx, oid: int, S: int, nseq: int) -> Optional[list[list[tuple[int, int, int]]]]:
    """Per instance of the batched row kernel ``oid``: runs ``(r0, r1, seq)`` of instance rows whose token-row
    operands all lie in sequence ``seq`` (derived by resolving the reads of ``S``-row blocks; an op that reads
    only intra-batch tensors inherits the map of the producer with the same instance rows).  ``None`` when the
    rows are not sequence-aligned at ``S`` granularity or a read is unresolvable."""
    key = (oid, S, nseq)
    hit = ctx._irows_map_cache.get(key, "miss")
    if hit != "miss":
        return hit
    info = ctx.info[oid]
    R, Q = info.rm.rows, S * nseq
    result: Optional[list[list[tuple[int, int, int]]]] = None
    if R % S == 0 and R >= S:
        ctx.row_chunk.setdefault(oid, S)
        result = []
        ok = True
        for e in range(info.mult):
            runs: list[tuple[int, int, int]] = []
            for r in range(0, R, S):
                seqs: set[int] = set()
                inherit: Optional[int] = None
                for tid, inst, a, b in ctx.reads((oid, "irows", e * R + r, e * R + r + S)):
                    t = ctx.g.tensors[tid]
                    if t.kind == "param" or t.producer is None:
                        continue
                    if inst is None:
                        ok = False
                        break
                    pinfo = ctx.info[t.producer]
                    if pinfo.mult == 1 and pinfo.rm.kind == "rows" and pinfo.rm.rows == Q:
                        opr = pinfo.rm.out_per_row or 1
                        seqs |= set(range((a // opr) // S, _ceil(_ceil(b, opr), S)))
                    elif pinfo.mult == info.mult and pinfo.rm.kind == "rows" and pinfo.rm.rows == R and inst == e:
                        inherit = t.producer
                if not ok:
                    break
                if not seqs and inherit is not None:
                    sub = _irows_seq_map(ctx, inherit, S, nseq)
                    if sub is None:
                        ok = False
                        break
                    for r0, r1, sq in sub[e]:
                        if r0 <= r < r1:
                            seqs = {sq}
                            break
                if len(seqs) != 1:
                    ok = False
                    break
                sq = seqs.pop()
                if runs and runs[-1][1] == r and runs[-1][2] == sq:
                    runs[-1] = (runs[-1][0], r + S, sq)
                else:
                    runs.append((r, r + S, sq))
            if not ok:
                break
            result.append(runs)
        if not ok:
            result = None
    ctx._irows_map_cache[key] = result
    return result


def _irows_members(ctx: _Ctx, oid: int, s0: int, s1: int, S: int, nseq: int) -> Optional[list[Member]]:
    """``irows`` members of ``oid`` covering exactly the instance rows that belong to sequences ``[s0, s1)``."""
    smap = _irows_seq_map(ctx, oid, S, nseq)
    if smap is None:
        return None
    R = ctx.info[oid].rm.rows
    out: list[Member] = []
    for e, runs in enumerate(smap):
        for r0, r1, sq in runs:
            if s0 <= sq < s1:
                g0, g1 = e * R + r0, e * R + r1
                if out and out[-1][3] == g0:
                    out[-1] = (oid, "irows", out[-1][2], g1)
                else:
                    out.append((oid, "irows", g0, g1))
    return out


def _inst_is_seq(ctx: _Ctx, oid: int, S: int, nseq: int) -> bool:
    """Are the scope instances of ``oid`` aligned with sequences (instance block ``i`` reads only rows of
    sequence ``i`` from every token-row operand)?  Per-head attention is; per-expert MoE kernels (whose
    instance count may coincidentally divide by ``nseq``) are not -- they gather tokens of every sequence."""
    key = (oid, S, nseq)
    hit = ctx._inst_seq_cache.get(key)
    if hit is not None:
        return hit
    per = ctx.info[oid].mult // nseq
    Q = S * nseq
    ok = True
    for tid, inst, a, b in ctx.reads((oid, "inst", 0, per)):
        t = ctx.g.tensors[tid]
        if t.kind == "param" or t.producer is None:
            continue
        pinfo = ctx.info[t.producer]
        if pinfo.mult > 1:
            if pinfo.mult == ctx.info[oid].mult and inst is not None and inst < per:
                if not _inst_is_seq(ctx, t.producer, S, nseq):     # same batch: inherit (expert chains are not sequences)
                    ok = False
                    break
                continue
            if pinfo.mult % nseq == 0 and inst is not None and inst >= pinfo.mult // nseq:
                ok = False
                break
            continue
        if pinfo.rm.kind in ("rows", "red") and pinfo.rm.rows == Q:
            opr = pinfo.rm.out_per_row or 1
            if inst is None or b > S * opr:
                ok = False
                break
    ctx._inst_seq_cache[key] = ok
    return ok


def _red_step(ctx: _Ctx, oid: int) -> int:
    """Granularity of the contraction chain (one ``Mac`` gate consumes ``CH`` elements)."""
    ch = ctx.g.ops[oid].statics.get("CH")
    return int(ch) if ch else 1


def _red_aligned(ctx: _Ctx, oid: int, pos: int) -> bool:
    return pos % _red_step(ctx, oid) == 0


def _members_for(ctx: _Ctx, ops: Iterable[int], s0: int, s1: int, S: int, nseq: int, *,
                 exclude: Iterable[int] = ()) -> list[Member]:
    ex = set(exclude)
    out: list[Member] = []
    for o in ops:
        if o in ex:
            continue
        out.extend(_slice_op(ctx, o, s0, s1, S, nseq, first=(s0 == 0)))
    return out


def _seq_chunks(nseq: int, s: int) -> list[tuple[int, int]]:
    return [(a, min(a + s, nseq)) for a in range(0, nseq, s)]


def _layer_chunks(n: int, m: int) -> list[tuple[int, int]]:
    return [(a, min(a + m, n)) for a in range(0, n, m)]


def _candidates(n: int, cap: int = 64) -> list[int]:
    base = {1, n}
    base |= {d for d in range(1, n + 1) if n % d == 0}
    base |= {v for v in (2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 48, 64, 96, 128) if v < n}
    out = sorted(base)
    if len(out) > cap:   # thin out geometrically
        keep = {out[0], out[-1]}
        step = len(out) / cap
        keep |= {out[int(i * step)] for i in range(cap)}
        out = sorted(keep)
    return out


def _red_ops(ctx: _Ctx, ops: Iterable[int], Q: int) -> list[int]:
    return [o for o in ops if ctx.info[o].rm.kind == "red" and ctx.info[o].mult == 1 and ctx.info[o].rm.rows == Q]


@dataclass
class _Cand:
    """Candidate of the superseded *cyclic* block family (``search=dict(acyclic=False)`` only)."""
    m: int
    s: int
    wgrad: str        # chain | separate
    fb: str           # joint | split
    upd: str          # standalone | fused-bwd | fused-next
    kf: int = 1       # consecutive steps fused per chunk unit
    s_head: int = 0
    cost: int = 0
    legal: bool = True
    note: str = ""


@dataclass
class _CCand:
    """Candidate of the convex block family (default).  Forward units ``m_f`` layers x ``s_f`` sequences,
    backward units ``m_b`` x ``s_b``, top-stack unit (layers ``[L - T, L)`` + head + their backward) with
    ``s_t`` sequences (``T = 0``: head only), weight-gradient handling, update placement, ``kf`` whole steps
    per unit (``kf > 1`` only when the whole step is one unit)."""
    m_f: int
    s_f: int
    m_b: int
    s_b: int
    T: int
    s_t: int
    wgrad: str        # chain | separate
    upd: str          # fused-bwd | fused-next | standalone
    kf: int = 1
    c: int = 1        # sequences per member group inside a unit (Up granularity; 0 = one group)
    emb: str = "separate"   # separate | fused: the step's embedding in the first layer chunk's units
    af: Optional[int] = None   # top unit's forward starts at layer ``af`` (< L - T: its forward reaches below
    #                            its backward; the layers [af, L - T) get their backward in bwd units); None = L - T
    cost: int = 0
    legal: bool = True
    note: str = ""

    def as_dict(self) -> dict:
        return dict(m_f=self.m_f, s_f=self.s_f, m=self.m_b, s=self.s_b, T=self.T, s_t=self.s_t, af=self.af, wgrad=self.wgrad,
                    upd=self.upd, kf=self.kf, c=self.c, emb=self.emb, cost=self.cost, legal=self.legal, part=self.note)


# ---------------------------------------------------------------------------------------------------------
# the planner
# ---------------------------------------------------------------------------------------------------------

class _Planner:
    def __init__(self, ctx: _Ctx, F: int, G: Optional[int]) -> None:
        self.ctx, self.F, self.G = ctx, F, G
        self.struct = _discover(ctx)
        self.g = ctx.g
        self._rep_cache: dict = {}
        self._unit_cache: dict = {}    # convex family: (label, cand fields, red_last) -> (stats | None, nonconvex)

    # -- evaluation helpers ---------------------------------------------------------------------------------
    def eval_members(self, members: list[Member], red_last: Iterable[int] = ()) -> _UnitStats:
        """Cost / legality of one hypothetical unit (representative evaluation; the ``red`` slices of the
        ``red_last`` ops are the last of their chains, so the unit produces those ops' outputs)."""
        # memo keyed by a digest of the member list (a per-sequence unit at 4M tokens has ~1e5 members; keeping
        # the tuples of every candidate would dominate memory); a digest collision could only mislead the
        # search -- the chosen plan is always fully re-checked
        h = hashlib.blake2b(digest_size=16)
        for m in sorted(members):
            h.update(b"%d,%s,%d,%d;" % (m[0], m[1].encode(), m[2], m[3]))
        key = (h.digest(), frozenset(red_last))
        hit = self._rep_cache.get(key)
        if hit is not None:
            return hit
        unit = CoarseUnit(tuple(members))
        st = _eval_unit(self.ctx, unit, 0, _RedEnv({o: 0 for o in red_last}), self.F)
        self._rep_cache[key] = st
        return st

    def legal(self, st: _UnitStats) -> bool:
        return (self.G is None or st.work <= self.G) and st.up <= self.F

    def ops_of(self, roots: Iterable[int]) -> list[int]:
        out: list[int] = []
        for r in roots:
            out.extend(self.struct.ops_by_root[r])
        return out

    # -- inference: one unit --------------------------------------------------------------------------------
    def single_unit(self) -> Optional[CoarsePlan]:
        members = [(o.id, "whole", 0, 0) for o in self.g.ops]
        st = self.eval_members(members)
        if not self.legal(st):
            return None
        u = CoarseUnit(tuple(members), "whole-circuit")
        return CoarsePlan([u], self.F, self.G, ["single unit: the whole circuit is one legal RU"],
                          {"family": "single", "fallback": False})

    # -- block family ---------------------------------------------------------------------------------------
    def block_plan(self, cand: _Cand, *, expand: bool) -> tuple[int, bool, list[CoarseUnit], dict]:
        """Cost of a block-partition candidate.  ``expand=False``: representative units only (fast cost and
        legality); ``expand=True``: every unit, ready for the checker."""
        ctx, S_ = self.ctx, self.struct
        units: list[CoarseUnit] = []
        total = 0
        legal = True
        info: dict = {"steps": []}

        def add(members: list[Member], label: str, mult: int = 1, red_last=()) -> None:
            nonlocal total, legal
            if not members:
                return
            if expand:
                units.append(CoarseUnit(tuple(members), label))
            else:
                st = self.eval_members(members, red_last)
                total += st.imports * mult
                if not self.legal(st):
                    legal = False

        # embeddings of every step in one unit (the table enters once); prologue nodes join it
        emb_ops = self.ops_of(S_.prologue) + [o for stp in S_.steps for o in self.ops_of(stp.embed)]
        if emb_ops:
            st = self.eval_members([(o, "whole", 0, 0) for o in emb_ops])
            if self.legal(st):
                add([(o, "whole", 0, 0) for o in emb_ops], "embed+prologue")
            else:
                for stp in S_.steps:
                    for r in stp.embed:
                        add([(o, "whole", 0, 0) for o in self.ops_of([r])], f"embed[{r}]")
                for r in S_.prologue:
                    add([(o, "whole", 0, 0) for o in self.ops_of([r])], f"prologue[{r}]")
        K = len(S_.steps)
        steps = S_.steps

        def chunk_ops(k: int, l0: int, l1: int) -> tuple[list[int], list[int], list[int]]:
            lay = steps[k].layers[l0:l1]
            return (self.ops_of([r for Lr in lay for r in Lr.fwd]), self.ops_of([r for Lr in lay for r in Lr.bwd]),
                    self.ops_of([r for Lr in lay for r in Lr.upd]))

        def sliced(k: int, ops: list[int], s0: int, s1: int, exclude=()) -> list[Member]:
            stp = steps[k]
            return _members_for(ctx, ops, s0, s1, stp.S, stp.nseq, exclude=exclude)

        # update placement: 'standalone' (own unit), 'fused-next' (with the first unit of the next step group
        # that reads the new weights), 'fused-bwd' (with the unit producing the gradient: dW never crosses).
        # fb: 'joint' (fwd + bwd of a chunk in one unit) or 'split' (two units; kf == 1 only).
        # kf: consecutive steps fused per chunk unit -- the chunk's weights of the whole group enter once and the
        # inner updates stay inside (the F cap on the last update's upstream work bounds kf * m).
        def compatible(a: int, b: int) -> bool:
            return (len(steps[a].layers) == len(steps[b].layers) and steps[a].nseq == steps[b].nseq
                    and steps[a].S == steps[b].S)

        groups: list[tuple[int, int]] = []
        k = 0
        while k < K:
            k1 = k + 1
            while k1 < K and k1 - k < cand.kf and compatible(k, k1):
                k1 += 1
            groups.append((k, k1))
            k = k1
        info["groups"] = groups
        carry_upd: dict[tuple[int, int], list[int]] = {}    # chunk -> update ops to fuse into the next group
        carry_head: list[int] = []
        for gidx, (k0, k1) in enumerate(groups):
            stp = steps[k0]
            nseq, Q = stp.nseq, stp.Q
            L = len(stp.layers)
            chunks = _layer_chunks(L, cand.m) if L else []
            sch = _seq_chunks(nseq, cand.s)
            hch = _seq_chunks(nseq, cand.s_head or cand.s)
            info["steps"].append({"k": k0, "steps": k1 - k0, "chunks": len(chunks), "seq_units": len(sch),
                                  "head_units": len(hch)})
            same_next = k1 < K and compatible(k1 - 1, k1)
            next_carry: dict[tuple[int, int], list[int]] = {}
            last_j = len(sch) - 1
            tag = f"step{k0}" if k1 == k0 + 1 else f"steps{k0}-{k1 - 1}"
            for (l0, l1) in chunks:
                per_k = [chunk_ops(k, l0, l1) for k in range(k0, k1)]
                separate = {k: (_red_ops(ctx, per_k[k - k0][1], Q) if cand.wgrad == "separate" else [])
                            for k in range(k0, k1)}
                fused_in = carry_upd.get((l0, l1), [])
                last_upd = per_k[-1][2]
                # updates of the inner steps: with the wgrad unit if separate, else with the block unit
                inner_upd = {k: per_k[k - k0][2] for k in range(k0, k1 - 1)}
                if cand.fb == "joint" or k1 - k0 > 1:
                    reds: set[int] = set()
                    for k in range(k0, k1):
                        reds |= set(_red_ops(ctx, per_k[k - k0][0] + per_k[k - k0][1], Q)) - set(separate[k])
                    host_last = cand.upd == "fused-bwd" and last_upd and not separate[k1 - 1]
                    for j, (s0, s1) in enumerate(sch):
                        if not expand and 1 < j < last_j:
                            continue
                        members: list[Member] = []
                        for k in range(k0, k1):
                            members += sliced(k, per_k[k - k0][0] + per_k[k - k0][1], s0, s1, exclude=separate[k])
                        if j == 0:
                            members += [(o, "whole", 0, 0) for o in fused_in]
                        if j == last_j:
                            for k, ops in inner_upd.items():
                                if not separate[k]:
                                    members += [(o, "whole", 0, 0) for o in ops]
                            if host_last:
                                members += [(o, "whole", 0, 0) for o in last_upd]
                        mult = 1 if (expand or j in (0, last_j)) else max(1, len(sch) - 2)
                        add(members, f"{tag}:blk[{l0}:{l1}]seq[{s0}:{s1}]", mult, red_last=(reds if j == last_j else ()))
                else:
                    fwd_ops, bwd_ops, _ = per_k[0]
                    sep = separate[k0]
                    for gi, (gname, gops) in enumerate([("fwd", fwd_ops), ("bwd", bwd_ops)]):
                        if not gops:
                            continue
                        greds = set(_red_ops(ctx, gops, Q)) - set(sep)
                        host_upd = cand.upd == "fused-bwd" and gi == 1 and last_upd and not sep
                        for j, (s0, s1) in enumerate(sch):
                            if not expand and 1 < j < last_j:
                                continue
                            members = sliced(k0, gops, s0, s1, exclude=sep)
                            if j == 0 and gi == 0:
                                members += [(o, "whole", 0, 0) for o in fused_in]
                            if host_upd and j == last_j:
                                members += [(o, "whole", 0, 0) for o in last_upd]
                            mult = 1 if (expand or j in (0, last_j)) else max(1, len(sch) - 2)
                            add(members, f"{tag}:{gname}[{l0}:{l1}]seq[{s0}:{s1}]", mult,
                                red_last=(greds if j == last_j else ()))
                for k in range(k0, k1):
                    if separate[k]:
                        members = [(o, "whole", 0, 0) for o in separate[k]]
                        if k < k1 - 1 or cand.upd == "fused-bwd":
                            members += [(o, "whole", 0, 0) for o in per_k[k - k0][2]]
                        add(members, f"step{k}:wgrad[{l0}:{l1}]")
                if last_upd and cand.upd != "fused-bwd":
                    if cand.upd == "fused-next" and same_next:
                        next_carry[(l0, l1)] = last_upd
                    else:
                        add([(o, "whole", 0, 0) for o in last_upd], f"step{k1 - 1}:update[{l0}:{l1}]")
            # LM head: its own layer with its own sequence split, fused over the group's steps like a chunk
            head_ops = [self.ops_of(steps[k].head) for k in range(k0, k1)]
            head_upd = [self.ops_of(steps[k].head_upd) for k in range(k0, k1)]
            if any(head_ops):
                reds = set()
                for k in range(k0, k1):
                    reds |= set(_red_ops(ctx, head_ops[k - k0], Q))
                hl = len(hch) - 1
                host_bwd = cand.upd == "fused-bwd"
                for j, (s0, s1) in enumerate(hch):
                    if not expand and 1 < j < hl:
                        continue
                    members = []
                    for k in range(k0, k1):
                        members += sliced(k, head_ops[k - k0], s0, s1)
                    if j == 0:
                        members += [(o, "whole", 0, 0) for o in carry_head]
                    if j == hl:
                        for k in range(k0, k1 - 1):
                            members += [(o, "whole", 0, 0) for o in head_upd[k - k0]]
                        if host_bwd:
                            members += [(o, "whole", 0, 0) for o in head_upd[-1]]
                    mult = 1 if (expand or j in (0, hl)) else max(1, len(hch) - 2)
                    add(members, f"{tag}:head seq[{s0}:{s1}]", mult, red_last=(reds if j == hl else ()))
                carry_head = []
                if head_upd[-1] and not host_bwd:
                    if cand.upd == "fused-next" and k1 < K and steps[k1].head:
                        carry_head = head_upd[-1]
                    else:
                        add([(o, "whole", 0, 0) for o in head_upd[-1]], f"step{k1 - 1}:head-update")
            else:
                for k in range(k0, k1):
                    if head_upd[k - k0]:
                        add([(o, "whole", 0, 0) for o in head_upd[k - k0]], f"step{k}:head-update")
            for k in range(k0, k1):
                for r in steps[k].other:
                    add([(o, "whole", 0, 0) for o in self.ops_of([r])], f"step{k}:other[{r}]")
            carry_upd = next_carry
        for (l0, l1), ops in carry_upd.items():       # fused-next but no compatible next group
            add([(o, "whole", 0, 0) for o in ops], f"update[{l0}:{l1}]")
        if carry_head:
            add([(o, "whole", 0, 0) for o in carry_head], "head-update")
        return total, legal, units, info

    def search_block(self, search: Optional[dict]) -> tuple[Optional[_Cand], list[_Cand]]:
        S_ = self.struct
        L = max((len(s.layers) for s in S_.steps), default=0)
        nseq = max((s.nseq for s in S_.steps), default=1)
        train = any(l.bwd for s in S_.steps for l in s.layers)
        K = len(S_.steps)
        multi = K > 1
        opts = dict(m=_candidates(L) if L else [1], s=_candidates(nseq), s_head=None,
                    wgrad=["chain", "separate"] if train else ["chain"],
                    fb=["joint", "split"] if train else ["joint"],
                    upd=(["standalone", "fused-bwd"] + (["fused-next"] if multi else [])) if train else ["standalone"],
                    kf=_candidates(K) if (train and multi) else [1])
        if search:
            for k, v in search.items():
                if k in opts and v is not None:
                    opts[k] = list(v) if isinstance(v, (list, tuple, set)) else [v]
                    if k == "upd":
                        opts[k] = ["fused-next" if x == "fused" else x for x in opts[k]]
        # work pre-filter against G only (unit work is additive: m layers x s sequences x kf steps of one layer's
        # fwd + bwd).  F caps the Up bound, which can be well below the unit's work (sibling wgrads are not
        # upstream of each other), so it is pruned by monotonicity instead: a unit is a superset of every unit
        # with smaller (m, s, kf), so once a candidate is illegal all larger s (and, if it was the smallest s,
        # all larger m) in the same family are too.
        per_layer_work = 0
        for stp in S_.steps:
            if stp.layers:
                w = sum(self.g.ops[o].work for o in self.ops_of(stp.layers[0].fwd + stp.layers[0].bwd))
                per_layer_work = max(per_layer_work, w)
        tried: list[_Cand] = []
        best: Optional[_Cand] = None
        heads = opts["s_head"] if opts["s_head"] else _candidates(nseq)
        for wgrad in opts["wgrad"]:
            for fb in opts["fb"]:
                for upd in opts["upd"]:
                    for kf in (opts["kf"] if fb == "joint" else [1]):
                        for m in opts["m"]:
                            first_illegal = False
                            for si, s in enumerate(opts["s"]):
                                smallest = m == opts["m"][0] and s == opts["s"][0] and kf == opts["kf"][0]
                                if (not smallest and per_layer_work and nseq and self.G is not None
                                        and per_layer_work * m * kf * s / nseq > 1.05 * self.G * (2 if fb == "split" else 1)):
                                    break
                                c = _Cand(m, s, wgrad, fb, upd, kf=kf)
                                cost, legal, _, _ = self.block_plan(c, expand=False)
                                c.cost, c.legal = cost, legal
                                tried.append(c)
                                if legal:
                                    if best is None or cost < best.cost:
                                        best = c
                                else:
                                    first_illegal = si == 0
                                    break
                            if first_illegal:
                                break
        if best is None:
            return None, tried
        # head split: independent of the block choice -> pick the cheapest legal one
        base = best
        for sh in heads:
            c = _Cand(base.m, base.s, base.wgrad, base.fb, base.upd, kf=base.kf, s_head=sh)
            cost, legal, _, _ = self.block_plan(c, expand=False)
            c.cost, c.legal = cost, legal
            tried.append(c)
            if legal and cost < best.cost:
                best = c
        return best, tried

    # -- convex block family (acyclic RU quotient) ----------------------------------------------------------
    def _embed_units(self, add: Callable, steps_embed: bool = True) -> None:
        """Embeddings of every step (and the prologue) in one unit when that is legal and convex (no embedding
        reads an output of an earlier step), else one unit per embedding node.  ``steps_embed=False``: the
        steps' embeddings live in the first layer chunk's units (``emb='fused'``); only the prologue here."""
        S_ = self.struct
        emb_roots = list(S_.prologue) + ([r for stp in S_.steps for r in stp.embed] if steps_embed else [])
        emb_ops = self.ops_of(emb_roots)
        if not emb_ops:
            return
        eset = set(emb_ops)
        convex = True
        for o in emb_ops:
            for e in self.g.ops[o].inputs:
                p = self.g.tensors[e.src].producer
                if p is not None and p not in eset:
                    convex = False
        if convex:
            st = self.eval_members([(o, "whole", 0, 0) for o in emb_ops])
            if self.legal(st):
                add([(o, "whole", 0, 0) for o in emb_ops], "embed+prologue")
                return
        for r in S_.prologue:
            add([(o, "whole", 0, 0) for o in self.ops_of([r])], f"prologue[{r}]")
        if steps_embed:
            for stp in S_.steps:
                for r in stp.embed:
                    add([(o, "whole", 0, 0) for o in self.ops_of([r])], f"embed[{r}]")

    def convex_plan(self, cand: "_CCand", *, expand: bool, parts: Iterable[str] = ("fixed", "fwd", "top", "bwd")
                    ) -> tuple[dict[str, int], dict[str, bool], list[CoarseUnit], dict]:
        """Cost of a convex block-partition candidate (see :class:`_CCand`).  Units, per training step:

        * ``fwd``: forward of ``m_f`` consecutive layers x ``s_f`` sequences (imports the chunk's weights and
          the bottom activation rows);
        * ``top``: layers ``[L - T, L)`` + LM head (+ loss gradient, head dgrad / wgrad) + their backward for
          ``s_t`` sequences -- the only place forward and backward of a layer share a unit (convex because the
          unit holds everything between them); ``T = 0``: head-only units; ``af < L - T``: the unit's forward
          starts lower, at layer ``af`` (a forward tail under the head / top stack; the bwd units of
          ``[af, L - T)`` read its checkpoint and gradient rows -- convex, saves one activation boundary and
          lets the head unit absorb forward work while ``F`` is slack);
        * ``bwd``: backward of ``m_b`` layers x ``s_b`` sequences (imports the chunk's weights, the top gradient
          rows and, because the backward composite recomputes each layer from its own checkpoint, one row set of
          checkpoint activations per layer);
        * ``fixed``: embeddings, weight updates (per placement), separate wgrad units, unrecognised nodes.

        Weight gradients: ``chain`` (``red`` slices with the bwd / top unit; the running accumulator crosses
        between consecutive sequence units, always in ascending order) or ``separate`` (whole per chunk).
        Update of a layer: ``fused-bwd`` (in the unit that completes its ``dW``), ``fused-next`` (in the next
        step's unit that first reads the new weights: fwd / top unit of the layer at ``j = 0``) or ``standalone``
        (one unit per chunk).  ``kf > 1`` only when the whole step is one unit (``T = L``, ``s_t = nseq``):
        ``kf`` consecutive whole steps then form one unit.  Every unit is convex by construction; the expanded
        plan is nevertheless passed through the checker's acyclicity test.  ``parts`` restricts the costed
        parts (they are additive; ``expand=True`` always builds every unit)."""
        ctx, S_ = self.ctx, self.struct
        parts = set(parts) if not expand else {"fixed", "fwd", "top", "bwd"}
        units: list[CoarseUnit] = []
        cost: dict[str, int] = {p: 0 for p in ("fixed", "fwd", "top", "bwd")}
        legal: dict[str, bool] = {p: True for p in cost}
        info: dict = {"steps": []}

        # Structural memo of unit evaluations: the members of a unit are a function of its label (step, layer
        # chunk, sequence range) and the candidate fields below, so during the search the (expensive)
        # per-sequence member lists are only materialised on a miss -- most evaluations of a search share
        # units across ``T`` / ``wgrad`` / ``emb`` / the other part's ``(m, s)``.  The entry also remembers
        # whether ``sliced`` flagged the unit non-convex.  ``expand=True`` always materialises.
        ukey_base = (cand.c, cand.emb, cand.upd, cand.wgrad, cand.kf)
        ucache = self._unit_cache

        def add(members, label: str, mult: int = 1, red_last=(), part: str = "fixed") -> None:
            """``members``: a list, or a thunk returning one (evaluated lazily under the structural memo)."""
            if part not in parts:
                return
            if expand:
                ms_ = members() if callable(members) else members
                if ms_:
                    units.append(CoarseUnit(tuple(ms_), label))
                return
            key = (label, ukey_base, frozenset(red_last))
            hit = ucache.get(key)
            if hit is None:
                before = set(info.get("nonconvex", ()))
                ms_ = members() if callable(members) else members
                nonconvex = set(info.get("nonconvex", ())) - before
                st = self.eval_members(ms_, red_last) if ms_ else None
                hit = (st, frozenset(nonconvex))
                ucache[key] = hit
            st, nonconvex = hit
            if nonconvex:
                info.setdefault("nonconvex", set()).update(nonconvex)
            if st is None:
                return
            cost[part] += st.imports * mult
            if not self.legal(st):
                legal[part] = False

        steps = S_.steps
        K = len(steps)

        def compatible(a: int, b: int) -> bool:
            return (len(steps[a].layers) == len(steps[b].layers) and steps[a].nseq == steps[b].nseq
                    and steps[a].S == steps[b].S)

        def lay_ops(k: int, l0: int, l1: int, which: str) -> list[int]:
            return self.ops_of([r for Lr in steps[k].layers[l0:l1] for r in getattr(Lr, which)])

        def sliced(k: int, ops: list[int], s0: int, s1: int, exclude=(), part: str = "fixed") -> list[Member]:
            """Members of ``ops`` for sequences ``[s0, s1)``, cut into groups of ``cand.c`` sequences (the
            ``Up`` bound follows the member DAG, so a unit whose members are per-sequence has ``Up`` = the
            work of one sequence through its layers while ``Work`` and the imports are those of the whole
            unit; ``c = 0``: one group).  An op that cannot be cut by sequence would have to go whole into the
            first sequence unit, where it may read the other sequence units' outputs (a cycle); a sequence
            split of a chunk is therefore only offered when every op of the chunk slices."""
            stp = steps[k]
            c = cand.c if cand.c else s1 - s0
            if c >= s1 - s0:
                out = _members_for(ctx, ops, s0, s1, stp.S, stp.nseq, exclude=exclude)
            else:
                out = []
                for a in range(s0, s1, c):
                    out += _members_for(ctx, ops, a, min(a + c, s1), stp.S, stp.nseq, exclude=exclude)
            if not (s0 == 0 and s1 >= stp.nseq) and any(m[1] == "whole" for m in out):
                info.setdefault("nonconvex", set()).add(part)
                if expand:
                    raise ValueError(f"convex family: chunk ops {[o for o, md, _, _ in out if md == 'whole'][:4]} "
                                     f"cannot be cut by sequence (planner bug: such a candidate must not be chosen)")
            return out

        whole_step = cand.kf > 1
        if whole_step:
            # kf consecutive whole steps per unit (each step's embed included): convex, legal only when tiny
            groups: list[tuple[int, int]] = []
            k = 0
            while k < K:
                k1 = k + 1
                while k1 < K and k1 - k < cand.kf and compatible(k, k1):
                    k1 += 1
                groups.append((k, k1))
                k = k1
            info["groups"] = groups
            for r in S_.prologue:
                add([(o, "whole", 0, 0) for o in self.ops_of([r])], f"prologue[{r}]")
            carry: list[int] = []
            for (k0, k1) in groups:
                members = [(o, "whole", 0, 0) for o in carry]
                carry = []
                for k in range(k0, k1):
                    stp = steps[k]
                    roots = list(stp.embed) + [r for Lr in stp.layers for r in Lr.fwd + Lr.bwd] + list(stp.head) + list(stp.other)
                    members += [(o, "whole", 0, 0) for o in self.ops_of(roots)]
                    upd = self.ops_of([r for Lr in stp.layers for r in Lr.upd] + list(stp.head_upd))
                    if k < k1 - 1 or cand.upd == "fused-bwd":
                        members += [(o, "whole", 0, 0) for o in upd]
                    elif cand.upd == "fused-next" and k1 < K:
                        carry = upd
                    else:
                        add([(o, "whole", 0, 0) for o in upd], f"step{k}:update", part="fixed")
                add(members, f"steps{k0}-{k1 - 1}:whole", part="top")
            if carry:
                add([(o, "whole", 0, 0) for o in carry], f"step{K - 1}:update", part="fixed")
            return cost, legal, units, info

        fused_emb = cand.emb == "fused"
        self._embed_units(add, steps_embed=not fused_emb)
        carry_upd: dict[int, list[int]] = {}       # layer index -> update ops of the previous step (fused-next)
        carry_head: list[int] = []
        for k, stp in enumerate(steps):
            nseq, Q = stp.nseq, stp.Q
            L = len(stp.layers)
            T = min(cand.T, L)
            Lb = L - T                                  # layers below the top-stack unit's backward
            A = Lb if cand.af is None else max(0, min(cand.af, Lb))   # ... and below its forward
            emb_ops = self.ops_of(stp.embed) if fused_emb else []
            if fused_emb and not stp.layers:
                add([(o, "whole", 0, 0) for o in emb_ops], f"step{k}:embed", part="fixed")
                emb_ops = []
            chunks_f = _layer_chunks(A, cand.m_f) if A else []
            chunks_b = _layer_chunks(Lb, cand.m_b) if Lb else []
            sch_f, sch_b = _seq_chunks(nseq, cand.s_f), _seq_chunks(nseq, cand.s_b)
            sch_t = _seq_chunks(nseq, cand.s_t or cand.s_b)
            info["steps"].append({"k": k, "L": L, "T": T, "fwd_chunks": len(chunks_f), "bwd_chunks": len(chunks_b),
                                  "fwd_seq_units": len(sch_f), "bwd_seq_units": len(sch_b), "top_seq_units": len(sch_t)})
            same_next = k + 1 < K and compatible(k, k + 1)
            next_carry: dict[int, list[int]] = {}
            next_head: list[int] = []
            tag = f"step{k}"
            has_bwd = any(Lr.bwd for Lr in stp.layers)
            # forward units (layers below the top stack)
            for (l0, l1) in chunks_f:
                fops = lay_ops(k, l0, l1, "fwd")
                if not fops:
                    continue
                if l0 == 0 and emb_ops:
                    fops = emb_ops + fops
                last_j = len(sch_f) - 1
                for j, (s0, s1) in enumerate(sch_f):
                    if not expand and 1 < j < last_j:
                        continue

                    def members(fops=fops, s0=s0, s1=s1, j=j, l0=l0, l1=l1, carry_upd=carry_upd):
                        out = sliced(k, fops, s0, s1, part="fwd")
                        if j == 0:
                            for l in range(l0, l1):
                                out += [(o, "whole", 0, 0) for o in carry_upd.get(l, ())]
                        return out
                    mult = 1 if (expand or j in (0, last_j)) else max(1, len(sch_f) - 2)
                    add(members, f"{tag}:fwd[{l0}:{l1}]seq[{s0}:{s1}]", mult, part="fwd")
            # top-stack unit: layers [A, L) fwd + head + bwd of layers [Lb, L) (head-only at T = 0, A = L); with
            # A < Lb its forward reaches below its backward -- convex (the bwd units of [A, Lb) read its
            # checkpoints and gradient rows, it reads nothing of theirs)
            head_ops = self.ops_of(stp.head)
            head_upd = self.ops_of(stp.head_upd)
            top_f = lay_ops(k, A, L, "fwd") if A < L else []
            top_b = lay_ops(k, Lb, L, "bwd") if T else []
            top_u = self.ops_of([r for Lr in stp.layers[Lb:L] for r in Lr.upd]) if T else []
            top_all = top_f + head_ops + top_b
            if A == 0 and emb_ops:
                top_all = emb_ops + top_all
            top_tag = (f"{tag}:head" if A == L else f"{tag}:head+fwd[{A}:{L}]" if not T
                       else f"{tag}:top[{Lb}:{L}]+head" if A == Lb else f"{tag}:top[fwd {A}:{L} bwd {Lb}:{L}]+head")
            sep_top = _red_ops(ctx, top_all, Q) if cand.wgrad == "separate" else []
            if top_all:
                reds = set(_red_ops(ctx, top_all, Q)) - set(sep_top)
                hl = len(sch_t) - 1
                host = cand.upd == "fused-bwd" and not sep_top
                for j, (s0, s1) in enumerate(sch_t):
                    if not expand and 1 < j < hl:
                        continue

                    def members(s0=s0, s1=s1, j=j, top_all=top_all, sep_top=sep_top, carry_head=carry_head,
                                carry_upd=carry_upd, Lb=Lb, L=L, hl=hl, host=host, head_upd=head_upd, top_u=top_u):
                        out = sliced(k, top_all, s0, s1, exclude=sep_top, part="top")
                        if j == 0:
                            out += [(o, "whole", 0, 0) for o in carry_head]
                            for l in range(A, L):
                                out += [(o, "whole", 0, 0) for o in carry_upd.get(l, ())]
                        if j == hl and host:
                            out += [(o, "whole", 0, 0) for o in head_upd + top_u]
                        return out
                    mult = 1 if (expand or j in (0, hl)) else max(1, len(sch_t) - 2)
                    add(members, f"{top_tag} seq[{s0}:{s1}]", mult, red_last=(reds if j == hl else ()), part="top")
                if sep_top:
                    members = [(o, "whole", 0, 0) for o in sep_top]
                    if cand.upd == "fused-bwd":
                        members += [(o, "whole", 0, 0) for o in head_upd + top_u]
                    add(members, f"{tag}:wgrad[top {Lb}:{L}]", part="top")
                if cand.upd != "fused-bwd" and (head_upd or top_u):
                    if cand.upd == "fused-next" and same_next:
                        next_head = head_upd
                        for l in range(Lb, L):
                            next_carry[l] = self.ops_of(stp.layers[l].upd)
                    else:
                        add([(o, "whole", 0, 0) for o in head_upd + top_u], f"{tag}:update[top {Lb}:{L}]", part="top")
            elif head_upd:
                add([(o, "whole", 0, 0) for o in head_upd], f"{tag}:head-update", part="fixed")
            # backward units (layers below the top stack)
            if has_bwd:
                for (l0, l1) in chunks_b:
                    bops = lay_ops(k, l0, l1, "bwd")
                    uops = lay_ops(k, l0, l1, "upd")
                    sep = _red_ops(ctx, bops, Q) if cand.wgrad == "separate" else []
                    reds = set(_red_ops(ctx, bops, Q)) - set(sep)
                    host = cand.upd == "fused-bwd" and not sep
                    last_j = len(sch_b) - 1
                    for j, (s0, s1) in enumerate(sch_b):
                        if not expand and 1 < j < last_j:
                            continue

                        def members(s0=s0, s1=s1, j=j, bops=bops, sep=sep, last_j=last_j, host=host, uops=uops):
                            out = sliced(k, bops, s0, s1, exclude=sep, part="bwd")
                            if j == last_j and host:
                                out += [(o, "whole", 0, 0) for o in uops]
                            return out
                        mult = 1 if (expand or j in (0, last_j)) else max(1, len(sch_b) - 2)
                        add(members, f"{tag}:bwd[{l0}:{l1}]seq[{s0}:{s1}]", mult,
                            red_last=(reds if j == last_j else ()), part="bwd")
                    if sep:
                        members = [(o, "whole", 0, 0) for o in sep]
                        if cand.upd == "fused-bwd":
                            members += [(o, "whole", 0, 0) for o in uops]
                        add(members, f"{tag}:wgrad[{l0}:{l1}]", part="bwd")
                    if uops and cand.upd != "fused-bwd":
                        if cand.upd == "fused-next" and same_next:
                            for l in range(l0, l1):
                                next_carry[l] = self.ops_of(stp.layers[l].upd)
                        else:
                            add([(o, "whole", 0, 0) for o in uops], f"{tag}:update[{l0}:{l1}]", part="bwd")
            else:
                for (l0, l1) in chunks_b:                     # forward-only circuits with per-layer update nodes
                    uops = lay_ops(k, l0, l1, "upd")
                    if uops:
                        add([(o, "whole", 0, 0) for o in uops], f"{tag}:update[{l0}:{l1}]", part="fixed")
            for r in stp.other:
                add([(o, "whole", 0, 0) for o in self.ops_of([r])], f"{tag}:other[{r}]", part="fixed")
            carry_upd, carry_head = next_carry, next_head
        for l, ops in sorted(carry_upd.items()):
            add([(o, "whole", 0, 0) for o in ops], f"update[layer {l}]", part="fixed")
        if carry_head:
            add([(o, "whole", 0, 0) for o in carry_head], "head-update", part="fixed")
        return cost, legal, units, info

    def search_convex(self, search: Optional[dict]) -> tuple[Optional["_CCand"], list["_CCand"]]:
        """Minimise the convex family's cost.  The parts are additive and independent given ``T`` and the
        update placement, so forward ``(m_f, s_f)``, backward ``(m_b, s_b)`` and top ``s_t`` are optimised
        separately per ``(T, wgrad, upd)``; legality is monotone under member inclusion (prune upward from
        the first illegal ``s``, and from the first illegal ``m`` at the smallest ``s``)."""
        S_ = self.struct
        L = max((len(s.layers) for s in S_.steps), default=0)
        nseq = max((s.nseq for s in S_.steps), default=1)
        train = any(l.bwd for s in S_.steps for l in s.layers)
        K = len(S_.steps)
        multi = K > 1
        ms = _candidates(L) if L else [1]
        ss = _candidates(nseq)
        opts = dict(m=ms, s=ss, m_f=None, s_f=None, s_t=None, T=[0] + [t for t in ms if t <= L],
                    wgrad=["chain", "separate"] if train else ["chain"],
                    upd=(["fused-bwd", "fused-next", "standalone"] if multi else ["fused-bwd", "standalone"]) if train else ["standalone"],
                    kf=_candidates(K) if (train and multi) else [1], c=[1], emb=["separate", "fused"], af=None)
        if search:
            for k, v in search.items():
                if k in opts and v is not None:
                    opts[k] = list(v) if isinstance(v, (list, tuple, set)) else [v]
                    if k == "upd":
                        opts[k] = ["fused-next" if x == "fused" else x for x in opts[k]]
        ms, ss = opts["m"], opts["s"]
        # forward tail below the top unit's backward: geometric depths (plus the whole stack) keep the extra
        # search dimension cheap; `search=dict(af=[...])` pins the depths
        af_ms = opts["af"] if opts.get("af") else sorted({m for m in ms if m & (m - 1) == 0} | {L})
        m_f_opts = opts["m_f"] or opts["m"]
        s_f_opts = opts["s_f"] or opts["s"]
        s_t_opts = opts["s_t"] or opts["s"]
        cg = int(opts["c"][0])
        tried: list[_CCand] = []
        best: Optional[_CCand] = None

        def part_search(base: _CCand, part: str, m_opts: list[int], s_opts: list[int], mkey: str, skey: str
                        ) -> Optional[_CCand]:
            bestp = None
            for m in m_opts:
                first_illegal = False
                for si, s in enumerate(s_opts):
                    c = _CCand(**{**base.__dict__, mkey: m, skey: s})
                    cost, legal, _, inf = self.convex_plan(c, expand=False, parts=(part,))
                    if part in inf.get("nonconvex", ()):
                        c.cost, c.legal, c.note = cost[part], False, part + ":nonconvex"
                        tried.append(c)
                        continue                    # a coarser sequence split may slice every op
                    c.cost, c.legal, c.note = cost[part], legal[part], part
                    tried.append(c)
                    if legal[part]:
                        if bestp is None or cost[part] < bestp.cost:
                            bestp = c
                    else:
                        first_illegal = si == 0
                        break
                if first_illegal:
                    break
            return bestp

        for wgrad, upd, emb in itertools.product(opts["wgrad"], opts["upd"], opts["emb"]):
                base = _CCand(m_f=m_f_opts[0], s_f=s_f_opts[0], m_b=ms[0], s_b=ss[0], T=0, s_t=s_t_opts[0], wgrad=wgrad,
                              upd=upd, c=cg, emb=emb)
                fixed_cost, fixed_legal, _, _ = self.convex_plan(base, expand=False, parts=("fixed",))
                if not fixed_legal["fixed"]:
                    continue
                for T in opts["T"]:
                    if T > L:
                        continue
                    bT = _CCand(**{**base.__dict__, "T": T})
                    # the top unit's forward may start below its backward: af in {L - T} u {L - T - m}, largest
                    # (smallest unit) first so part_search's monotone pruning applies
                    af_opts = sorted({L - T} | {L - T - m for m in af_ms if 0 <= L - T - m}, reverse=True)
                    bwd = None
                    if T < L and train:
                        bwd = part_search(bT, "bwd", ms, ss, "m_b", "s_b")     # bwd units cover [0, L - T) for every af
                        if bwd is None:
                            break
                    stop_T = False
                    for af in af_opts:
                        bA = _CCand(**{**bT.__dict__, "af": af})
                        top = part_search(bA, "top", [af], s_t_opts, "af", "s_t")
                        if top is None:
                            stop_T = af == af_opts[0]   # plain top illegal: a taller top stack is a superset at every s_t
                            break                       # a lower af is a superset of this one
                        total = fixed_cost["fixed"] + top.cost
                        c = _CCand(**{**top.__dict__})
                        if af > 0:
                            fwd = part_search(bA, "fwd", m_f_opts, s_f_opts, "m_f", "s_f")   # chunks cover [0, af)
                            if fwd is None:
                                stop_T = True           # the smallest fwd unit is the same for every T
                                break
                            c.m_f, c.s_f = fwd.m_f, fwd.s_f
                            total += fwd.cost
                        if bwd is not None:
                            c.m_b, c.s_b = bwd.m_b, bwd.s_b
                            total += bwd.cost
                        c.cost, c.legal, c.note = total, True, "total"
                        tried.append(c)
                        if best is None or total < best.cost:
                            best = c
                    if stop_T:
                        break
                # whole steps fused (kf > 1): convex only as whole-step units, i.e. T = L and s_t = nseq legal
                if train and multi and L in opts["T"] and any(k > 1 for k in opts["kf"]):
                    cw = _CCand(**{**base.__dict__, "T": L, "s_t": nseq})
                    _, lw, _, _ = self.convex_plan(cw, expand=False, parts=("top",))
                    if lw["top"]:
                        for kf in sorted(k for k in opts["kf"] if k > 1):
                            ck = _CCand(**{**cw.__dict__, "kf": kf})
                            cost, legal, _, _ = self.convex_plan(ck, expand=False)
                            ck.cost, ck.legal, ck.note = sum(cost.values()), all(legal.values()), "whole-step"
                            tried.append(ck)
                            if not ck.legal:
                                break
                            if best is None or ck.cost < best.cost:
                                best = ck
        return best, tried

    # -- generic bands (no recognisable blocks) --------------------------------------------------------------
    def band_dp(self, max_roots: int = 400) -> Optional[tuple[int, list[tuple[int, int]]]]:
        """Cheapest legal partition of the root-node sequence into contiguous bands (dynamic programme over the
        cut positions; a band's imports depend on its own members only, so band costs are additive).  Returns
        ``(cost, bands)`` or ``None`` when some single root node is already illegal.  Above ``max_roots`` root
        nodes only uniform widths are tried."""
        roots = [r for r in range(len(self.struct.names)) if self.struct.ops_by_root[r]]
        n = len(roots)
        if n == 0:
            return None
        cache: dict[tuple[int, int], Optional[int]] = {}

        def band_cost(i: int, j: int) -> Optional[int]:
            key = (i, j)
            if key not in cache:
                st = self.eval_members([(o, "whole", 0, 0) for o in self.ops_of(roots[i:j])])
                cache[key] = st.imports if self.legal(st) else None
            return cache[key]

        if n > max_roots:
            best = None
            for b in _candidates(n):
                total, ok, bands = 0, True, []
                for a in range(0, n, b):
                    c = band_cost(a, min(a + b, n))
                    if c is None:
                        ok = False
                        break
                    total += c
                    bands.append((roots[a], roots[min(a + b, n) - 1] + 1))
                if ok and (best is None or total < best[0]):
                    best = (total, bands)
            return best
        INF = float("inf")
        cost = [0] + [INF] * n
        prev = [-1] * (n + 1)
        for j in range(1, n + 1):
            for i in range(j - 1, -1, -1):
                if cost[i] == INF:
                    continue
                c = band_cost(i, j)
                if c is None:
                    break               # a superset band is illegal too (legality is monotone under inclusion)
                if cost[i] + c < cost[j]:
                    cost[j], prev[j] = cost[i] + c, i
        if cost[n] == INF:
            return None
        bands, j = [], n
        while j > 0:
            i = prev[j]
            bands.append((roots[i], roots[j - 1] + 1))
            j = i
        bands.reverse()
        return int(cost[n]), bands

    def band_units(self, bands: list[tuple[int, int]]) -> list[CoarseUnit]:
        units = []
        for (a, b) in bands:
            ops = self.ops_of(range(a, b))
            if ops:
                units.append(CoarseUnit(tuple((o, "whole", 0, 0) for o in ops), f"band[{a}:{b}]"))
        return units

    # -- last resort: one op (slice) per unit ----------------------------------------------------------------
    def fine_plan(self) -> list[CoarseUnit]:
        """Every op alone, cut into the largest slices whose work fits ``min(F, G)`` (a single-member unit has
        ``Up = Work``).  Row-parallel kernels may be cut at any row, reductions at ``CH`` multiples, batched ops
        per scope instance; an op that does not fit even at its finest slice is a genuine infeasibility."""
        cap = min(self.F, self.G) if self.G is not None else self.F
        units: list[CoarseUnit] = []
        for op in self.g.ops:
            info, w = self.ctx.info[op.id], op.work
            if w <= cap:
                units.append(CoarseUnit(((op.id, "whole", 0, 0),), f"op{op.id}"))
                continue
            if info.mult > 1:
                per_inst = w // info.mult
                n = cap // per_inst if per_inst else info.mult
                if n < 1:
                    raise ValueError(f"op {op.id} ({op.fn_id}): one scope instance has work {per_inst} > min(F, G)={cap}")
                for a in range(0, info.mult, n):
                    units.append(CoarseUnit(((op.id, "inst", a, min(a + n, info.mult)),), f"op{op.id}[{a}:{a + n}]"))
                continue
            rm = info.rm
            if rm.kind == "rows":
                per_row = w // rm.rows
                n = cap // per_row if per_row else rm.rows
                if n < 1:
                    raise ValueError(f"op {op.id} ({op.fn_id}): one row has work {per_row} > min(F, G)={cap}")
                for a in range(0, rm.rows, n):
                    units.append(CoarseUnit(((op.id, "rows", a, min(a + n, rm.rows)),), f"op{op.id}[{a}:{a + n}]"))
                continue
            if rm.kind == "red":
                step = _red_step(self.ctx, op.id)
                n = step
                while n + step <= rm.rows and self.ctx.member_work((op.id, "red", 0, n + step)) <= cap:
                    n += step
                if self.ctx.member_work((op.id, "red", 0, min(n, rm.rows))) > cap:
                    raise ValueError(f"op {op.id} ({op.fn_id}): one contraction chunk exceeds min(F, G)={cap}")
                for a in range(0, rm.rows, n):
                    units.append(CoarseUnit(((op.id, "red", a, min(a + n, rm.rows)),), f"op{op.id}[{a}:{a + n}]"))
                continue
            raise ValueError(f"op {op.id} ({op.fn_id}) has work {w} > min(F, G)={cap} and cannot be sliced")
        return units


def upper_coarse(g: OpGraph, F: int, G: Optional[int], *, program=None, search: Optional[dict] = None,
                 check: bool = True, fwd: Optional[int] = None) -> CoarsePlan:
    """Coarse constructive upper bound on ``I*(C; F, G)``: a legal partition of the circuit into explicit
    units (see the module docstring for the families searched).  ``search`` may pin / restrict the block
    family's knobs: ``{"m": [...], "s": [...], "s_head": [...], "wgrad": [...], "fb": [...], "upd": [...]}``.
    The returned plan has been passed through :func:`check_coarse_plan` (``check=False`` skips the final
    full re-check; the statistics are then those of the planner's own evaluation of every unit).  ``fwd``:
    the calibration work of one honest inference session, only used to express the per-RU work of
    ``plan.detail['anatomy']`` in fwd units (it is always given in MACs and as a fraction of ``G``)."""
    program = program if program is not None else getattr(g, "program", None)
    ctx = _Ctx(g, program)
    F = int(F)
    G = None if G is None else int(G)
    acyclic = not (search is not None and search.get("acyclic") is False)
    pl = _Planner(ctx, F, G)
    notes: list[str] = []
    plan: Optional[CoarsePlan] = None
    train = any(l.bwd for s in pl.struct.steps for l in s.layers)
    if not train:
        plan = pl.single_unit()
    if plan is None and pl.struct.generic:
        hit = pl.band_dp()
        if hit is not None:
            cost, bands = hit
            plan = CoarsePlan(pl.band_units(bands), F, G,
                              [f"generic band partition (no transformer blocks recognised): {len(bands)} contiguous root-node bands"],
                              {"family": "bands", "bands": bands, "fallback": True})
    elif plan is None and acyclic:
        best, tried = pl.search_convex(search)
        if best is not None:
            _, _, units, info = pl.convex_plan(best, expand=True)
            if best.kf > 1:
                notes.append(f"convex family: whole-step units, kf={best.kf} steps per unit, update={best.upd}")
            else:
                notes.append(f"convex family: fwd units m_f={best.m_f} layers x s_f={best.s_f} sequences, "
                             f"bwd units m={best.m_b} x s={best.s_b}, top stack T={best.T} layers + head x s_t={best.s_t}"
                             f"{'' if best.af is None or best.af >= max((len(s.layers) for s in pl.struct.steps), default=0) - best.T else f' (forward from layer {best.af})'}, "
                             f"wgrad={best.wgrad}, update={best.upd}, embed={best.emb}, Up granularity c={best.c} seq")
            plan = CoarsePlan(units, F, G, notes,
                              {"family": "convex-block", "m": best.m_b, "s": best.s_b, "m_f": best.m_f, "s_f": best.s_f,
                               "T": best.T, "s_t": best.s_t, "af": best.af, "s_head": best.s_t, "wgrad": best.wgrad, "fb": "convex",
                               "upd": best.upd, "kf": best.kf, "c": best.c, "emb": best.emb, "fallback": False, "steps": info["steps"],
                               "planner_cost": best.cost,
                               "groups": info.get("groups"), "n_candidates": len(tried),
                               "candidates": [c.as_dict() for c in tried if c.note in ("total", "whole-step")]})
            if not train and len(pl.struct.names) <= 64:
                # small forward circuits: whole-token bands cut inside a layer can beat layer x token tiles
                # (weights enter once); at scale the activation boundaries make them hopeless, so only try
                # them when the root body is small
                hit = pl.band_dp()
                if hit is not None and hit[0] < best.cost:
                    cost, bands = hit
                    plan = CoarsePlan(pl.band_units(bands), F, G,
                                      [f"band partition ({len(bands)} contiguous root-node bands) beat the convex block "
                                       f"family ({best.cost} B)"],
                                      {"family": "bands", "bands": bands, "fallback": False,
                                       "convex_block_total": best.cost})
        else:
            notes.append(f"no legal convex block partition (tried {len(tried)} part candidates)")
            hit = pl.band_dp()
            if hit is not None:
                cost, bands = hit
                notes.append(f"band fallback: {len(bands)} contiguous root-node bands")
                plan = CoarsePlan(pl.band_units(bands), F, G, notes, {"family": "bands", "bands": bands, "fallback": True})
    elif plan is None:
        print("[coarse] *** search=dict(acyclic=False): searching the SUPERSEDED cyclic block family (joint fwd+bwd, "
              "kf-fused chunks); its plans are NOT legal partitions and must not be reported as U ***", file=sys.stderr, flush=True)
        best, tried = pl.search_block(search)
        if best is not None:
            _, _, units, info = pl.block_plan(best, expand=True)
            notes.append(f"CYCLIC block family: m={best.m} layers x s={best.s} sequences x kf={best.kf} steps per unit, "
                         f"wgrad={best.wgrad}, fb={best.fb}, update={best.upd}, head split s_head={best.s_head or best.s}")
            plan = CoarsePlan(units, F, G, notes,
                              {"family": "block-cyclic", "m": best.m, "s": best.s, "s_head": best.s_head or best.s,
                               "wgrad": best.wgrad, "fb": best.fb, "upd": best.upd, "kf": best.kf, "fallback": False,
                               "steps": info["steps"], "groups": info.get("groups"), "n_candidates": len(tried),
                               "candidates": [dict(m=c.m, s=c.s, wgrad=c.wgrad, fb=c.fb, upd=c.upd, kf=c.kf, s_head=c.s_head,
                                                   cost=c.cost, legal=c.legal) for c in tried]})
        else:
            notes.append(f"no legal block partition (tried {len(tried)} candidates)")
            hit = pl.band_dp()
            if hit is not None:
                cost, bands = hit
                notes.append(f"band fallback: {len(bands)} contiguous root-node bands")
                plan = CoarsePlan(pl.band_units(bands), F, G, notes, {"family": "bands", "bands": bands, "fallback": True})
    if plan is None:
        units = pl.fine_plan()      # raises ValueError when even single op slices do not fit
        notes.append("fine fallback: one op slice per unit (largest slices that fit min(F, G))")
        plan = CoarsePlan(units, F, G, notes, {"family": "fine", "fallback": True})
    plan.detail.setdefault("structure", {
        "steps": len(pl.struct.steps),
        "layers": [len(s.layers) for s in pl.struct.steps],
        "Q": [s.Q for s in pl.struct.steps], "S": [s.S for s in pl.struct.steps],
        "generic": pl.struct.generic})
    if acyclic:
        if check:
            check_coarse_plan(g, plan, F, G, program=program, _ctx=ctx)
        else:               # statistics only -- but a cyclic plan is never returned as a bound
            _evaluate_plan(ctx, plan, F, G, legality=False, acyclic=True)
    else:
        _evaluate_plan(ctx, plan, F, G, legality=check, acyclic=False)
        note = ("CYCLIC COMPARISON MODE (search=dict(acyclic=False)): the RU quotient of this plan "
                + ("IS CYCLIC -- " if not plan.detail.get("acyclic") else "happens to be acyclic -- ")
                + "this is NOT a legal partition under SPEC §0 and must not be reported as U")
        plan.notes.append(note)
        plan.detail["checked"] = None
        print(f"[coarse] *** {note} ***", file=sys.stderr, flush=True)
    est = plan.detail.get("planner_cost")
    if est is not None and plan.total and abs(est - plan.total) > 0.01 * plan.total:
        plan.notes.append(f"planner estimate {est} differs from the checked total {plan.total} (search may be suboptimal)")
        print(f"[coarse] warning: planner estimate {est} != checked total {plan.total} ({plan.detail.get('family')})",
              file=sys.stderr, flush=True)
    try:
        plan.detail["anatomy"] = _anatomy(ctx, pl.struct, plan, fwd)
    except Exception as e:  # pragma: no cover - diagnostics must never invalidate a checked plan
        plan.detail["anatomy"] = {"error": repr(e)[:200]}
    return plan


def _median(xs: list) -> Optional[float]:
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return float(s[n // 2]) if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def _anatomy(ctx: _Ctx, struct: _Struct, plan: CoarsePlan, fwd: Optional[int]) -> dict:
    """What the plan's adversary does (``plan.detail['anatomy']``, jsonable, O(members)): RU count, work per
    RU (MACs, fraction of ``G`` and -- when the calibration ``fwd`` is given -- fwd units), layers / tokens /
    dynamic-weight / activation / partial-sum bytes per RU (median, max), the dominant strategy, and for MoE
    circuits the active experts per RU, their dynamic parameter bytes and the tokens per active expert."""
    g = ctx.g
    fam = plan.detail.get("family")
    # op -> (step, layer) and the token-row count of its step; expert ops (batched row kernels under an MoE MLP)
    lay_of: dict[int, tuple[int, int]] = {}
    q_of: dict[int, int] = {}
    for k, stp in enumerate(struct.steps):
        for li, L in enumerate(stp.layers):
            for r in L.fwd + L.bwd + L.upd:
                for o in struct.ops_by_root[r]:
                    lay_of[o] = (k, li)
        for r in stp.embed + [r for L in stp.layers for r in L.fwd + L.bwd + L.upd] + stp.head + stp.head_upd + stp.other:
            for o in struct.ops_by_root[r]:
                q_of[o] = stp.Q
    names = struct.names
    moe_roots = {r for r, n in enumerate(names) if n.startswith("AccMoeMlp")}
    irows_ops = {o for (o, _S, _n), v in ctx._irows_map_cache.items() if v is not None}
    seq_inst_ops = {o for (o, _S, _n), v in ctx._inst_seq_cache.items() if v}

    def is_expert_op(o: int) -> bool:
        info = ctx.info[o]
        if info.mult <= 1 or info.rm.kind != "rows":
            return False
        op = g.ops[o]
        r = op.key[0][0] if op.key[0] else op.key[1]
        return r in moe_roots or o in irows_ops

    n_layers_per, tokens_per, w_per, a_per, p_per, works = [], [], [], [], [], []
    experts_per, expert_bytes_per, tok_per_expert = [], [], []
    is_moe = False
    for u in plan.units:
        layers: set[tuple[int, int]] = set()
        rows_of: dict[int, int] = {}                      # token-row op -> rows covered by this unit's members
        experts: dict[tuple[int, int, int], int] = {}     # (step, layer, expert) -> rows
        ebytes: set[tuple[int, int, int]] = set()
        for (oid, mode, lo, hi) in u.members:
            info = ctx.info[oid]
            if oid in lay_of:
                layers.add(lay_of[oid])
            Q = q_of.get(oid, 0)
            if mode in ("rows", "red") and info.rm.rows == Q:
                rows_of[oid] = rows_of.get(oid, 0) + (hi - lo)
            elif mode == "whole" and Q and ((info.rm.kind in ("rows", "red") and info.rm.rows == Q) or info.mult > 1):
                rows_of[oid] = Q
            elif mode == "inst" and Q and info.mult and oid in seq_inst_ops:
                rows_of[oid] = rows_of.get(oid, 0) + Q * (hi - lo) // info.mult
            if is_expert_op(oid):
                is_moe = True
                R = info.rm.rows
                lay = lay_of.get(oid, (0, 0))
                if mode == "irows":
                    for e in range(lo // R, _ceil(hi, R)):
                        r0, r1 = max(lo, e * R) - e * R, min(hi, (e + 1) * R) - e * R
                        key = (lay[0], lay[1], e)
                        experts[key] = experts.get(key, 0) + (r1 - r0)
                elif mode == "inst":
                    for e in range(lo, hi):
                        experts[(lay[0], lay[1], e)] = R
                else:
                    for e in range(info.mult):
                        experts[(lay[0], lay[1], e)] = R
                for tid, inst, a, b in ctx.reads((oid, mode, lo, hi), params_only=True):
                    if ctx.role(tid) in ("accumulated", "carried"):
                        ebytes.add((tid, a, b))
        n_layers_per.append(len(layers))
        tokens_per.append(max(rows_of.values(), default=0))
        w_per.append(u.by_class.get("weights", 0))
        a_per.append(u.by_class.get("activations", 0))
        p_per.append(u.by_class.get("partials", 0))
        works.append(u.work_max)
        if experts:
            experts_per.append(len(experts))
            expert_bytes_per.append(sum((b - a) * g.tensors[tid].width // 8 for tid, a, b in ebytes))
            tok_per_expert.extend(experts.values())
    G = plan.G
    if fam == "single":
        dominant = "whole-model"
    elif fam == "convex-block":
        L = max((len(s.layers) for s in struct.steps), default=0)
        nseq = max((s.nseq for s in struct.steps), default=1)
        T = plan.detail.get("T", 0)
        if plan.detail.get("kf", 1) > 1 or (T >= L and plan.detail.get("s_t") == nseq) \
                or (plan.detail.get("m_f") == L and plan.detail.get("s_f") == nseq):
            dominant = "whole-model"
        elif T >= L:
            dominant = "whole-model x token-chunk"
        elif plan.detail.get("s_f", nseq) >= nseq:
            dominant = "layer-chunk"
        else:
            dominant = "layer-chunk x token-chunk"
    elif fam == "bands":
        dominant = "band"
    elif fam == "fine":
        dominant = "fine"
    else:
        dominant = str(fam)
    out = {
        "n_ru": plan.n_units,
        "work_median_macs": _median(works), "work_max_macs": max(works, default=0),
        "work_median_over_G": (_median(works) / G) if (G and works) else None,
        "work_max_over_G": (max(works) / G) if (G and works) else None,
        "work_median_fwd": (_median(works) / fwd) if (fwd and works) else None,
        "work_max_fwd": (max(works) / fwd) if (fwd and works) else None,
        "layers_per_ru": {"median": _median(n_layers_per), "max": max(n_layers_per, default=0)},
        "tokens_per_ru": {"median": _median(tokens_per), "max": max(tokens_per, default=0)},
        "dyn_weight_bytes_per_ru": {"median": _median(w_per), "max": max(w_per, default=0)},
        "activation_bytes_per_ru": {"median": _median(a_per), "max": max(a_per, default=0)},
        "partial_bytes_per_ru": {"median": _median(p_per), "max": max(p_per, default=0)},
        "dominant": dominant,
    }
    if is_moe:
        out["active_experts_per_ru"] = {"median": _median(experts_per), "max": max(experts_per, default=0)}
        out["active_dyn_param_bytes_per_ru"] = {"median": _median(expert_bytes_per), "max": max(expert_bytes_per, default=0)}
        out["tokens_per_active_expert"] = {"median": _median(tok_per_expert), "max": max(tok_per_expert, default=0)}
    # per unit class (fwd / top / bwd / wgrad / update / embed / head / other, from the label): count, Work and
    # Up (max, in fwd units when calibrated, else MACs), Up/Work, imports and which cap binds -- for training
    # this shows the F-bound dW reduction (bwd / top units with Up = Work) against the G-bound forward tiles
    classes: dict[str, dict] = {}
    for u in plan.units:
        cls = _unit_class(u.label)
        c = classes.setdefault(cls, {"n": 0, "work_max": 0, "up_max": 0, "imports": 0, "up_over_work_max": 0.0})
        c["n"] += 1
        c["work_max"] = max(c["work_max"], u.work_max)
        c["up_max"] = max(c["up_max"], u.up_max)
        c["imports"] += u.imports_total
        if u.work_max:
            c["up_over_work_max"] = max(c["up_over_work_max"], u.up_max / u.work_max)
    for c in classes.values():
        if fwd:
            c["work_max_fwd"], c["up_max_fwd"] = c["work_max"] / fwd, c["up_max"] / fwd
        c["G_slack"] = (c["work_max"] / G) if G else None
        c["F_slack"] = (c["up_max"] / plan.F) if plan.F else None
        c["binds"] = ("F" if (plan.F and c["F_slack"] is not None and c["F_slack"] >= 0.9 and (c["G_slack"] or 0) < c["F_slack"])
                      else "G" if (c["G_slack"] or 0) >= 0.9 else "none")
    out["by_unit_class"] = classes
    return out


def _unit_class(label: str) -> str:
    body = label.split(":", 1)[1] if ":" in label and label.split(":", 1)[0].startswith("step") else label
    for tag in ("wgrad", "update", "top", "fwd", "bwd", "head", "embed", "prologue", "band", "fine", "whole", "steps", "other"):
        if body.startswith(tag):
            return tag
    return "other"


# ---------------------------------------------------------------------------------------------------------
# validation helper: a plan as a gate -> RU assignment of the flattened circuit
# ---------------------------------------------------------------------------------------------------------

def plan_gate_assignment(g: OpGraph, plan: CoarsePlan, program=None) -> dict[int, int]:
    """Expand a coarse plan to a gate-level assignment ``{root gate index: unit index}`` of the program's
    canonical circuit (every non-``Input`` gate), so that the plan can be judged by the exact module's literal
    :func:`accumulation.exact.solve.partition_cost` / :func:`is_legal` -- the ground truth the checker's
    accounting must dominate.  ``rows`` members map to the kernel's row members, ``inst`` members to scope
    instances, ``red`` members to the contraction iterations ``[lo, hi)`` of every output's accumulation chain
    (the zero-init gates go with the first slice, the rounding gates with the last)."""
    from verity_ir.defs import PrimitiveDefinition
    program = program if program is not None else getattr(g, "program", None)
    ctx = _Ctx(g, program)
    circ = program.circuit
    # the canonical root body = one Input node per root parameter, then the program function's body nodes
    shift = len(program.root.body.nodes) - len(program.fn.body.nodes)
    assign: dict[int, int] = {}

    def lscope(oid: int, inst: int):
        info = ctx.info[oid]
        members: list[int] = []
        rem = inst
        for d in reversed(info.dims):
            members.append(rem % d)
            rem //= d
        members.reverse()
        s, di = circ.root_scope, 0
        for depth, k in enumerate(info.path):
            kk = k + shift if depth == 0 else k
            nd = s.spec.body.nodes[kk]
            m = 0
            if nd.form == "batch":
                m, di = members[di], di + 1
            s = s.child(kk, m)
        return s

    def node_index(oid: int) -> int:
        idx = g.ops[oid].key[1]
        return idx + shift if not ctx.info[oid].path else idx

    def put(lo: int, hi: int, ui: int) -> None:
        for gate in range(lo, hi):
            assign[gate] = ui

    def walk_red(scope, rows: int, lo: int, hi: int, ui: int, inside_scan: bool) -> None:
        """Assign the gates of a reduction kernel's activation ``scope`` that belong to contraction slice
        ``[lo, hi)`` to unit ``ui``: scan iterations by contraction position, zero-inits with the first slice,
        everything else (rounding) with the last slice."""
        body = scope.spec.body
        for k, nd in enumerate(body.nodes):
            off = scope.offset + body.offsets[k]
            if nd.form == "scan":
                for i in range(nd.n):
                    if lo <= i * rows // nd.n < hi:
                        walk_red(scope.child(k, i), rows, lo, hi, ui, True)
                continue
            n = nd.n if nd.form == "batch" else 1
            if nd.form == "primitive" or isinstance(nd.fn, PrimitiveDefinition):
                if inside_scan or ("Zero" in nd.fn.name and lo == 0) or ("Zero" not in nd.fn.name and hi == rows):
                    put(off, off + n, ui)
                continue
            for m in range(n):
                walk_red(scope.child(k, m), rows, lo, hi, ui, inside_scan)

    for ui, u in enumerate(plan.units):
        for (oid, mode, lo, hi) in u.members:
            info = ctx.info[oid]
            idx = node_index(oid)
            node = info.node
            if mode in ("whole", "inst"):
                insts = range(lo, hi) if mode == "inst" else range(info.mult)
                for i in insts:
                    s = lscope(oid, i)
                    off = s.offset + s.spec.body.offsets[idx]
                    put(off, off + node.gates, ui)
            elif mode == "rows":
                ks = lscope(oid, 0).child(idx)
                kb = ks.spec.body
                bn = kb.nodes[0]
                off = ks.offset + kb.offsets[0]
                put(off + lo * bn.fn.gates, off + hi * bn.fn.gates, ui)
            elif mode == "irows":
                R = info.rm.rows
                for i in range(lo // R, _ceil(hi, R)):
                    r0, r1 = max(lo, i * R) - i * R, min(hi, (i + 1) * R) - i * R
                    ks = lscope(oid, i).child(idx)
                    kb = ks.spec.body
                    bn = kb.nodes[0]
                    off = ks.offset + kb.offsets[0]
                    put(off + r0 * bn.fn.gates, off + r1 * bn.fn.gates, ui)
            else:
                walk_red(lscope(oid, 0).child(idx), info.rm.rows, lo, hi, ui, False)
    return assign


def gate_level_up(g: OpGraph, plan: CoarsePlan, program=None, *, unit: Optional[int] = None,
                  max_sinks: int = 4096, seed: int = 0) -> dict:
    """Independent ``Up`` check for one unit (default: the unit with the largest checker ``Up``): expand the
    plan to a gate assignment (:func:`plan_gate_assignment`), then compute ``max_g work(Up_R(g))`` by BFS over
    the *real operand wires* of the flattened circuit (the exact module's :func:`up_set` -- attention's
    within-sequence coupling, the residual stream, every gate).  ``Up_R`` is monotone along in-RU wires, so
    the maximum is attained at the RU's sinks (gates with no in-RU consumer); every sink is walked when there
    are at most ``max_sinks``, else a seeded sample (reported).  Returns the gate-level maximum, the checker's
    member-level bound and their ratio; the checker's bound must be ``>=`` the gate-level truth."""
    import random
    from accumulation.exact.solve import flatten, up_set
    program = program if program is not None else getattr(g, "program", None)
    if unit is None:
        unit = max(range(plan.n_units), key=lambda i: plan.units[i].up_max)
    roles = {name: (g.tensors[tid].role or "fixed") for name, tid in g.params.items()}
    flat = flatten(program, roles)
    asg = plan_gate_assignment(g, plan, program)
    mine = [x for x in flat.gates if asg[x] == unit]
    inside = set(mine)
    has_consumer: set[int] = set()
    for x in mine:
        for p in flat.operands[x]:
            if p in inside:
                has_consumer.add(p)
    sinks = [x for x in mine if x not in has_consumer]
    sampled = len(sinks) > max_sinks
    if sampled:
        sinks = random.Random(seed).sample(sinks, max_sinks)
    best, best_gate = 0, None
    for s in sinks:
        w = sum(flat.work[v] for v in up_set(flat, asg, s))
        if w > best:
            best, best_gate = w, s
    u = plan.units[unit]
    wg = sum(flat.work[x] for x in mine)
    # the checker's Work adds an accumulator init / round per partial of every cut ``red`` chain (>= gate level)
    return {"unit": unit, "label": u.label, "gates": len(mine), "sinks": len(sinks), "sinks_sampled": sampled,
            "work_gate_level": wg, "work_checker": u.work_max,
            "up_gate_level": best, "up_checker": u.up_max,
            "ratio_checker_over_gate": (u.up_max / best) if best else None, "argmax_gate": best_gate,
            "sound": u.up_max >= best and u.work_max >= wg}


__all__ = ["CoarseUnit", "CoarsePlan", "Member", "upper_coarse", "check_coarse_plan", "check_plan",
           "plan_gate_assignment", "gate_level_up", "ACC_BYTES"]
