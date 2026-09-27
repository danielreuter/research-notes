"""Operator graph of a Verity IR program.

The accumulation analysis needs a *tensor-operator* view of the circuit: which matmuls / reductions /
element-wise blocks exist, how much work each performs, what its operands are and where they come from
(a root parameter with a role, or another operator's output).  The Verity program already contains this
hierarchically -- every block of :mod:`accumulation.ir.blocks` is a composite whose name starts with
``Acc`` -- so extraction is a walk of the hierarchy that stops at the *terminal* composites (the vocabulary
blocks) and records one :class:`Op` per terminal node.  Batching is kept symbolic: a ``batch`` of a terminal
composite (or a terminal inside an enclosing batch) is one ``Op`` with ``copies > 1`` and the aggregate
output tensor of all members; only member 0 is walked.  Operands are resolved through parameter bindings,
batch slicing and composite returns back to the producing terminal op or root parameter, so the resulting
graph is exact dataflow at operator granularity (no gate expansion).

Nothing here is adversary-specific: the graph is a property of the *declared* circuit.  The bounds in
:mod:`accumulation.bounds` consume it.

Usage::

    from accumulation.graph import extract
    g = extract(built_program)          # BuiltProgram from the registry
    g.summary()                         # work by class, ADW, bytes, ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Optional

from verity_ir.defs import CompositeDefinition, PrimitiveDefinition, SpecializedDefinition, Node
from verity_ir.refs import Affine, Concat, Explicit, Refs, Strided, compose_view, concat, strided_view

# ---------------------------------------------------------------------------------------------------------
# data model
# ---------------------------------------------------------------------------------------------------------

#: composites treated as one operator each (their interior is never walked)
TERMINAL_PREFIXES = ("AccMatmulT", "AccRmsNormBatch", "AccAddBatch", "AccMulBatch", "AccSwiGluBatch",
                     "AccScaleBatch", "AccSoftmaxBatch", "AccLossGradBatch", "AccGainBatch", "AccRowScaleBatch",
                     "AccColSumBatch", "AccEmbedBatch", "AccSgdUpdate", "AccPerturb", "AccEsUpdate",
                     "AccSwiGluBwdBatch", "AccSoftmaxBwdBatch", "AccRmsNormBwdBatch", "AccScatterAddBatch",
                     "AccGatherRowsBatch", "AccRouterBatch", "AccTopkBatch", "AccCombineBatch", "AccMaskBatch",
                     "AccSumBatch", "AccMeanBatch", "AccCausalMaskBatch", "AccRewardBatch", "AccNoise",
                     "AccRowDotBatch", "AccRowScaleBroadcastBatch")


@dataclass
class Tensor:
    """A value tensor: a root parameter (``kind='param'``) or the aggregate output of an op (``kind='op'``)."""
    id: int
    kind: str                 # 'param' | 'op'
    name: str
    leaves: int               # total leaves (all copies)
    width: int                # bits per leaf
    role: Optional[str] = None  # params only: fixed | accumulated | carried | token | seed
    producer: Optional[int] = None  # op id for kind == 'op'

    @property
    def bytes(self) -> int:
        return self.leaves * self.width // 8


@dataclass
class Edge:
    src: int                  # tensor id
    leaves_per_copy: int      # leaves read by one copy of the op (with repeats)
    exact: bool = True        # False when the source set is a range over-approximation
    # Bounding leaf intervals ``[lo, hi)`` of the source tensor touched by one canonical instance of the op,
    # widened over the members of an enclosing axis-0 batch (each expert / sequence reads its own window)
    # (merged, at most ``_MAX_RANGES``).  Over-approximate by construction (bounding boxes of structured
    # parts, union over probed members), so overlap counts derived from them are upper bounds -- the safe
    # direction for per-element sharing (see :meth:`OpGraph.share`).  Empty means "unknown: whole tensor".
    ranges: tuple[tuple[int, int], ...] = ()

    def covers(self, leaves: int) -> int:
        """Number of leaves of the source (of ``leaves`` total) inside the recorded ranges."""
        if not self.ranges:
            return leaves
        return sum(min(hi, leaves) - lo for lo, hi in self.ranges if lo < leaves)


_MAX_RANGES = 32


def _merge_ranges(rs: list[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    """Union of intervals; coalesces the closest neighbours until at most ``_MAX_RANGES`` remain (coarsening
    only ever enlarges the union)."""
    if not rs:
        return ()
    rs = sorted(rs)
    out = [list(rs[0])]
    for lo, hi in rs[1:]:
        if lo <= out[-1][1]:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    while len(out) > _MAX_RANGES:
        gaps = [(out[i + 1][0] - out[i][1], i) for i in range(len(out) - 1)]
        _, i = min(gaps)
        out[i][1] = out[i + 1][1]
        del out[i + 1]
    return tuple((lo, hi) for lo, hi in out)


@dataclass
class Op:
    id: int
    key: tuple                # structural key: (scope path of node indices, node index)
    fn_id: str                # specialized definition id, e.g. AccMatmulT_v1{M=..,N=..,K=..,CH=..}
    kind: str                 # short kind: matmul | norm | add | ... | prim:<name> | scan:<fn>
    statics: dict
    work_per_copy: int        # MAC-equivalent work of one copy (sum of primitive .work)
    copies: int
    out: int                  # output tensor id
    inputs: list[Edge] = field(default_factory=list)
    name: Optional[str] = None  # node annotation (e.g. 'wgrad'), if the factory gave one

    @property
    def work(self) -> int:
        return self.work_per_copy * self.copies

    def macs(self) -> int:
        """MACs of a matmul op (all copies); 0 for non-matmuls."""
        if self.kind != "matmul":
            return 0
        s = self.statics
        return s["M"] * s["N"] * s["K"] * self.copies


class OpGraph:
    def __init__(self) -> None:
        self.tensors: list[Tensor] = []
        self.ops: list[Op] = []
        self.params: dict[str, int] = {}     # root param name -> tensor id
        self.root_param_index: dict[int, int] = {}  # param position -> tensor id
        self.outputs: list[int] = []         # tensor ids returned by the root

    # -- construction -------------------------------------------------------------------------------------
    def add_tensor(self, **kw) -> Tensor:
        t = Tensor(id=len(self.tensors), **kw)
        self.tensors.append(t)
        return t

    # -- queries -------------------------------------------------------------------------------------------
    def producer(self, tid: int) -> Optional[Op]:
        t = self.tensors[tid]
        return self.ops[t.producer] if t.producer is not None else None

    def consumers(self, tid: int) -> list[Op]:
        return [o for o in self.ops if any(e.src == tid for e in o.inputs)]

    def share(self, tid: int) -> int:
        """Maximum, over the leaves of tensor ``tid``, of the number of *distinct consumer ops* that read the
        leaf (sweep line over the consumers' recorded ranges; a consumer without ranges counts everywhere).
        This is the per-element sharing factor a sound operand charge must divide by: an RU that imports the
        element once may feed it to every one of those ops.  Ranges are over-approximate, so this is an
        upper bound on the true multiplicity (the safe direction).  At least 1 for any tensor with a consumer;
        0 for a tensor nobody reads."""
        cons = self.consumers(tid)
        if not cons:
            return 0
        leaves = self.tensors[tid].leaves
        events: list[tuple[int, int]] = []
        for o in cons:
            rs = [r for e in o.inputs if e.src == tid for r in e.ranges]
            if not rs or any(not e.ranges for e in o.inputs if e.src == tid):
                events += [(0, 1), (leaves, -1)]
                continue
            for lo, hi in _merge_ranges(rs):   # one op counts once per leaf even if it reads it twice
                events += [(lo, 1), (min(hi, leaves), -1)]
        events.sort(key=lambda e: (e[0], e[1]))  # process -1 before +1 at equal positions
        best = cur = 0
        for _, d in events:
            cur += d
            best = max(best, cur)
        return max(best, 1)

    def ancestors(self, op: Op | int, _memo: dict | None = None) -> frozenset[int]:
        """Set of op ids in the transitive input closure of ``op`` (excluding itself)."""
        if _memo is None:
            _memo = getattr(self, "_anc_memo", None)
            if _memo is None:
                _memo = self._anc_memo = {}
        oid = op if isinstance(op, int) else op.id
        if oid in _memo:
            return _memo[oid]
        out: set[int] = set()
        for e in self.ops[oid].inputs:
            p = self.tensors[e.src].producer
            if p is not None:
                out.add(p)
                out |= self.ancestors(p, _memo)
        res = frozenset(out)
        _memo[oid] = res
        return res

    def tensor_ancestor_work(self, tid: int) -> int:
        """Total work (all copies) of every op that ``tid`` transitively depends on, including its producer."""
        p = self.tensors[tid].producer
        if p is None:
            return 0
        ids = set(self.ancestors(p)) | {p}
        return sum(self.ops[i].work for i in ids)

    def root_roles_upstream(self, tid: int) -> frozenset[str]:
        """Roles of root parameters that ``tid`` transitively depends on (memoised)."""
        memo = getattr(self, "_role_memo", None)
        if memo is None:
            memo = self._role_memo = {}
        if tid in memo:
            return memo[tid]
        t = self.tensors[tid]
        if t.kind == "param":
            res = frozenset([t.role or "fixed"])
        else:
            res: set[str] = set()
            for e in self.ops[t.producer].inputs:
                res |= self.root_roles_upstream(e.src)
            res = frozenset(res)
        memo[tid] = res
        return res

    def total_work(self) -> int:
        return sum(o.work for o in self.ops)

    def by_kind(self) -> dict[str, int]:
        d: dict[str, int] = {}
        for o in self.ops:
            d[o.kind] = d.get(o.kind, 0) + o.work
        return d

    def summary(self) -> dict:
        return {"ops": len(self.ops), "tensors": len(self.tensors), "work": self.total_work(),
                "work_by_kind": self.by_kind(),
                "macs": sum(o.macs() for o in self.ops)}


# ---------------------------------------------------------------------------------------------------------
# walking the hierarchy
# ---------------------------------------------------------------------------------------------------------

def _is_terminal(fn) -> bool:
    if isinstance(fn, PrimitiveDefinition):
        return True
    return any(fn.name.startswith(p) for p in TERMINAL_PREFIXES)


_WORK_MEMO: dict = {}


def work_of(fn) -> int:
    """MAC-equivalent work of one call of ``fn`` (sum of primitive ``.work`` over the expansion)."""
    if isinstance(fn, PrimitiveDefinition):
        return int(getattr(fn, "work", 1))
    key = fn.id
    if key in _WORK_MEMO:
        return _WORK_MEMO[key]
    tot = 0
    for nd in fn.body.nodes:
        tot += work_of(nd.fn) * (nd.n if nd.form in ("batch", "scan") else 1)
    _WORK_MEMO[key] = tot
    return tot


def _kind_of(fn) -> str:
    if isinstance(fn, PrimitiveDefinition):
        return "prim:" + fn.name
    n = fn.name
    if n.startswith("AccMatmulT"):
        return "matmul"
    if n.startswith("Acc"):
        n = n[3:]
    if n.endswith("Batch"):
        n = n[:-5]
    return n.lower()


class _Scope:
    """A position in the hierarchy: the specialized definition whose body we are in, the parent scope, the
    node (in the parent body) that instantiates it and the member index within that node."""
    __slots__ = ("spec", "parent", "node_idx", "member", "path")

    def __init__(self, spec, parent, node_idx, member):
        self.spec, self.parent, self.node_idx, self.member = spec, parent, node_idx, member
        self.path = () if parent is None else parent.path + (node_idx,)


def _leaf_range(part: Refs) -> tuple[int, int]:
    if isinstance(part, Affine):
        return part.base, part.base + part.count - 1
    if isinstance(part, Strided):
        q = -(-part.count // part.inner)
        r = min(part.inner, part.count)
        pos = [part.base, part.base + (q - 1) * part.outer_stride, part.base + (r - 1) * part.inner_stride,
               part.base + (q - 1) * part.outer_stride + (r - 1) * part.inner_stride]
        return min(pos), max(pos)
    if isinstance(part, Explicit):
        leaves = [it[2] for it in part.items]
        return min(leaves), max(leaves)
    raise TypeError(type(part))


def _shift(part: Refs, d: int) -> Refs:
    if isinstance(part, Affine):
        return Affine(part.space, part.idx, part.base + d, part.count)
    if isinstance(part, Strided):
        return Strided(part.space, part.idx, part.base + d, part.inner, part.outer_stride, part.inner_stride, part.count)
    if isinstance(part, Explicit):
        return Explicit(tuple((s, i, l + d) for s, i, l in part.items))
    raise TypeError(type(part))


_BIG = 1 << 18


def _restrict(part: Refs, lo: int, hi: int) -> Refs:
    """The sub-sequence of ``part`` whose leaf positions lie in ``[lo, hi)``, re-based so that ``lo`` maps to
    ``0`` (i.e. positions inside one batch member's leaf window).  Order of the retained positions is
    preserved.  Structured (``Affine``/``Strided``) whenever the retained runs are, else ``Explicit``."""
    if isinstance(part, Affine):
        a, b = max(part.base, lo), min(part.base + part.count, hi)
        return Affine(part.space, part.idx, a - lo, max(0, b - a))
    if isinstance(part, Explicit):
        return Explicit(tuple((s, i, l - lo) for s, i, l in part.items if lo <= l < hi))
    assert isinstance(part, Strided)
    inner, os, is_ = part.inner, part.outer_stride, part.inner_stride
    nouter = -(-part.count // inner)
    span_lo = min(0, (inner - 1) * is_)          # run extent relative to its start
    span_hi = max(0, (inner - 1) * is_)
    # only runs whose extent meets [lo, hi) can contribute: solve for the run index range analytically
    if os > 0:
        q_lo = max(0, -(-(lo - span_hi - part.base) // os))
        q_hi = min(nouter - 1, (hi - 1 - span_lo - part.base) // os)
    elif os < 0:
        q_lo = max(0, -(-(part.base + span_lo - (hi - 1)) // (-os)))
        q_hi = min(nouter - 1, (part.base + span_hi - lo) // (-os))
    else:
        q_lo, q_hi = 0, nouter - 1
    if q_hi < q_lo:
        return Explicit(())
    full: list[int] = []   # run indices q fully inside the window
    partial: list[tuple] = []  # (space, idx, leaf) for elements of runs straddling the window
    for q in range(q_lo, q_hi + 1):
        n_q = min(inner, part.count - q * inner)
        r0 = part.base + q * os
        r_lo, r_hi = min(r0, r0 + (n_q - 1) * is_), max(r0, r0 + (n_q - 1) * is_)
        if r_hi < lo or r_lo >= hi:
            continue
        if lo <= r_lo and r_hi < hi and n_q == inner:
            full.append(q)
        else:
            partial.extend((part.space, part.idx, r0 + t * is_ - lo) for t in range(n_q) if lo <= r0 + t * is_ < hi)
    if not full and not partial:
        return Explicit(())
    if not partial and full == list(range(full[0], full[0] + len(full))):
        q0 = full[0]
        return Strided(part.space, part.idx, part.base + q0 * os - lo, inner, os, is_, len(full) * inner)
    if not full:
        return Explicit(tuple(partial))
    # mixed: keep the contiguous full runs symbolic and the straddling elements explicit
    pieces: list[Refs] = []
    q = full[0]
    q0, n = q, 0
    for q in full:
        if q == q0 + n:
            n += 1
        else:
            pieces.append(Strided(part.space, part.idx, part.base + q0 * os - lo, inner, os, is_, n * inner))
            q0, n = q, 1
    pieces.append(Strided(part.space, part.idx, part.base + q0 * os - lo, inner, os, is_, n * inner))
    if partial:
        pieces.append(Explicit(tuple(partial)))
    return concat(pieces) if len(pieces) > 1 else pieces[0]


def _periodic(part: Refs, L: int) -> bool:
    """Whether restricting ``part`` to each member window of width ``L`` gives the same pattern in every
    window touched (so one member is representative)."""
    if isinstance(part, Affine):
        return (part.base % L == 0) and (part.count % L == 0)
    if isinstance(part, Strided):
        inner, os, is_ = part.inner, part.outer_stride, part.inner_stride
        run_span = (inner - 1) * abs(is_) + 1
        if part.count % inner != 0 or run_span > L:
            return False
        if (part.base % L) + run_span > L:
            return False
        return os > 0 and (os % L == 0 or (L % os == 0 and (part.base % L) % os == 0 and ((part.count // inner) % (L // os) == 0)))
    return False


_SMALL = 1 << 12   # largest reference sequence we are willing to materialise element by element
_MAX_RUNS = 1 << 16


def _symbolic_view(base: Refs, b0: int, inner: int, os: int, is_: int, count: int) -> Optional[Refs]:
    """`strided_view` restricted to the cases that stay symbolic (no per-element materialisation); ``None``
    when an explicit tuple would be needed.  Mirrors :func:`verity_ir.refs.strided_view`."""
    if count <= 0:
        return Explicit(())
    if isinstance(base, Affine):
        return Strided(base.space, base.idx, base.base + b0, inner, os, is_, count)
    if isinstance(base, Strided):
        return compose_view(base, b0, inner, os, is_, count)
    if isinstance(base, Concat):
        nouter = -(-count // inner)
        if nouter > _MAX_RUNS:
            return None
        import bisect
        out: list[Refs] = []
        for q in range(nouter):
            n_here = min(inner, count - q * inner)
            p0 = b0 + q * os
            p1 = p0 + (n_here - 1) * is_
            k = bisect.bisect_right(base.starts, min(p0, p1)) - 1
            st, part = base.starts[k], base.parts[k]
            if min(p0, p1) < st or max(p0, p1) >= st + part.count:
                return None            # a run straddles two parts
            sub = _symbolic_view(part, p0 - st, n_here, 0, is_, n_here)
            if sub is None:
                return None
            out.append(sub)
        return concat(out)
    if isinstance(base, Explicit) and count <= _SMALL:
        return Explicit(tuple(base[b0 + (j // inner) * os + (j % inner) * is_] for j in range(count)))
    return None


def _compose(base: Refs, part: Refs) -> tuple[Refs, bool]:
    """Positions of ``part`` (indices into ``base``'s leaf sequence) read through ``base``.  Returns the
    composed refs and whether they are exact (``False`` for the range over-approximation, whose count is
    then larger than ``part.count`` -- callers rescale)."""
    if isinstance(part, Affine):
        return base.slice(part.base, part.base + part.count), True
    if isinstance(part, Explicit):
        if part.count > _SMALL:
            lo, hi = _leaf_range(part)
            return base.slice(lo, hi + 1), False
        return Explicit(tuple(base[it[2]] for it in part.items)), True
    assert isinstance(part, Strided)
    if part.count <= _SMALL:
        return strided_view(base, part.base, part.inner, part.outer_stride, part.inner_stride, part.count), True
    r = _symbolic_view(base, part.base, part.inner, part.outer_stride, part.inner_stride, part.count)
    if r is not None:
        return r, True
    lo, hi = _leaf_range(part)
    return base.slice(lo, hi + 1), False


def _parts(refs: Refs) -> list[Refs]:
    """Split a reference sequence into parts that each address a single ``(space, idx)``."""
    if isinstance(refs, Concat):
        out: list[Refs] = []
        for p in refs.parts:
            out.extend(_parts(p))
        return out
    if isinstance(refs, Explicit):
        if refs.count == 0:
            return []
        groups: dict[tuple, list] = {}
        for s, i, l in refs.items:
            groups.setdefault((s, i), []).append((s, i, l))
        return [Explicit(tuple(v)) for v in groups.values()]
    return [refs]


def _sig(part: Refs) -> tuple:
    """Hashable identity of a structured part (an ``Explicit`` is identified by its items)."""
    if isinstance(part, Affine):
        return ("a", part.space, part.idx, part.base, part.count)
    if isinstance(part, Strided):
        return ("s", part.space, part.idx, part.base, part.inner, part.outer_stride, part.inner_stride, part.count)
    if isinstance(part, Explicit):
        return ("e", part.items)
    return ("c", tuple(_sig(p) for p in part.parts))


def _space_idx(part: Refs) -> tuple[str, int]:
    if isinstance(part, Explicit):
        return part.items[0][0], part.items[0][1]
    return part.space, part.idx


class _Extractor:
    def __init__(self, program, roles: dict[str, str]):
        self.g = OpGraph()
        self.program = program
        self.roles = roles
        self.op_by_key: dict[tuple, int] = {}
        self._ret_cache: dict[tuple, list] = {}
        root = program.fn
        params, _ = root.signature()
        for i, (name, t) in enumerate(params):
            tt = self.g.add_tensor(kind="param", name=name, leaves=t.leaves, width=t.homogeneous_width() or 16,
                                   role=roles.get(name, "fixed"))
            self.g.params[name] = tt.id
            self.g.root_param_index[i] = tt.id
        self.root_scope = _Scope(root, None, None, 0)

    # -- op bookkeeping -----------------------------------------------------------------------------------
    def _op_for(self, scope: _Scope, node_idx: int, mult: int) -> Op:
        key = (scope.path, node_idx)
        if key in self.op_by_key:
            return self.g.ops[self.op_by_key[key]]
        node = scope.spec.body.nodes[node_idx]
        fn = node.fn
        n = node.n if node.form in ("batch", "scan") else 1
        if node.form == "scan":
            kind, work, copies, out_leaves = "scan:" + _kind_of(fn), work_of(fn) * n, mult, node.out.leaves * mult
        else:
            kind, work, copies, out_leaves = _kind_of(fn), work_of(fn), n * mult, node.out.leaves * mult
        width = node.out.homogeneous_width() or 16
        fid = fn.id if isinstance(fn, SpecializedDefinition) else fn.name
        statics = dict(fn.bindings) if isinstance(fn, SpecializedDefinition) else {}
        name = node.name
        if name is None:   # inherit the nearest annotation up the scope chain (e.g. a 'recompute' batch node)
            s = scope
            while s is not None and s.parent is not None and name is None:
                name = s.parent.spec.body.nodes[s.node_idx].name
                s = s.parent
        op = Op(id=len(self.g.ops), key=key, fn_id=fid, kind=kind, statics=statics, work_per_copy=work,
                copies=copies, out=-1, name=name)
        t = self.g.add_tensor(kind="op", name=f"{kind}#{op.id}", leaves=out_leaves, width=width, producer=op.id)
        op.out = t.id
        self.g.ops.append(op)
        self.op_by_key[key] = op.id
        return op

    # -- walk ----------------------------------------------------------------------------------------------
    def run(self) -> OpGraph:
        self._walk(self.root_scope, 1)
        # root outputs
        for part in _parts(self.root_scope.spec.body.ret):
            for tid, _ in self._resolve_part(self.root_scope, part):
                if tid not in self.g.outputs:
                    self.g.outputs.append(tid)
        return self.g

    def _walk(self, scope: _Scope, mult: int) -> None:
        body = scope.spec.body
        for k, node in enumerate(body.nodes):
            if node.form == "scan" or _is_terminal(node.fn):
                op = self._op_for(scope, k, mult)
                self._fill_inputs(scope, node, op)
            elif node.form == "call":
                self._walk(_Scope(node.fn, scope, k, 0), mult)
            elif node.form == "batch":
                self._walk(_Scope(node.fn, scope, k, 0), mult * node.n)
            else:
                raise ValueError(node.form)

    def _fill_inputs(self, scope: _Scope, node: Node, op: Op) -> None:
        if op.inputs:
            return
        acc: dict[int, tuple[int, bool]] = {}
        rng: dict[int, list[tuple[int, int]]] = {}
        for pi, a in enumerate(node.args):
            # axis-0 batch arguments: resolve the whole argument (the union over members) and divide the
            # counts by the member count, so members reading *different* tensors are all recorded
            if node.form == "batch" and node.axes[pi] == 0 and node.n > 1:
                refs, div = a.refs, node.n
            else:
                refs, div = self._member_arg_refs(node, pi, 0), 1
            local: dict[int, tuple[int, bool]] = {}
            for part in _parts(refs):
                for tid, sub in self._resolve_part(scope, part):
                    c, ex = local.get(tid, (0, True))
                    local[tid] = (c + sub[1], ex and sub[0])
                    rs = rng.setdefault(tid, [])
                    rs.append((sub[2], sub[3] + 1))      # resolution bounds are inclusive; Edge.ranges are [lo, hi)
                    if len(rs) > 4 * _MAX_RANGES:
                        rs[:] = list(_merge_ranges(rs))
            for tid, (c, ex) in local.items():
                c0, ex0 = acc.get(tid, (0, True))
                acc[tid] = (c0 + (c // div if div > 1 else c), ex0 and ex and (div == 1 or c % div == 0))
        op.inputs = [Edge(src=tid, leaves_per_copy=c, exact=ex, ranges=_merge_ranges(rng.get(tid, [])))
                     for tid, (c, ex) in acc.items()]

    @staticmethod
    def _member_arg_refs(node: Node, pi: int, m: int) -> Refs:
        a = node.args[pi]
        if node.form in ("primitive", "call"):
            return a.refs
        if node.form == "batch":
            ax = node.axes[pi]
            if ax is None:
                return a.refs
            if ax == 0:
                L = a.type.elem.leaves
                return a.refs.slice(m * L, (m + 1) * L)
            return a.take(ax, m).refs
        # scan: (init, *xs, *shared) -- treat as reading everything once (conservative for sources)
        return a.refs

    # Resolution results are ``(tensor_id, (exact, leaves_read, lo, hi))`` where ``[lo, hi)`` is a bounding
    # interval of the leaf positions read in that tensor (see :class:`Edge.ranges`).
    def _whole_return(self, scope: _Scope) -> list[tuple[int, tuple[bool, int, int, int]]]:
        """Sources of the *entire* return of the composite instantiated at ``scope``, memoised by scope path
        (all members of a batch resolve to the same ops / root tensors with the same counts)."""
        key = scope.path
        hit = self._ret_cache.get(key)
        if hit is None:
            ret = scope.spec.body.ret
            hit = [(tid, ex_c) for sub in _parts(ret) for tid, ex_c in self._resolve_part(scope, sub)]
            self._ret_cache[key] = hit
        return hit

    def _through(self, scope: _Scope, base: Refs, part: Refs) -> Iterator[tuple[int, tuple[bool, int]]]:
        """Resolve ``part`` (positions into ``base``) in ``scope``.  When the composition had to fall back to
        a range over-approximation the counts are rescaled so that they still sum to ``part.count``.
        Windows into a composite's return are memoised by (scope path, window): every member of a batch
        resolves the same window to the same ops / root tensors."""
        if base is scope.spec.body.ret:
            if isinstance(part, Affine) and part.base == 0 and part.count == base.count:
                yield from self._whole_return(scope)
                return
            key = (scope.path, _sig(part))
            hit = self._ret_cache.get(key)
            if hit is None:
                hit = list(self._through_uncached(scope, base, part))
                self._ret_cache[key] = hit
            yield from hit
            return
        yield from self._through_uncached(scope, base, part)

    def _through_uncached(self, scope: _Scope, base: Refs, part: Refs) -> Iterator[tuple[int, tuple[bool, int]]]:
        composed, ok = _compose(base, part)
        if ok:
            for sub in _parts(composed):
                yield from self._resolve_part(scope, sub)
            return
        agg: dict[int, list[int]] = {}
        for sub in _parts(composed):
            for tid, (_, c, lo, hi) in self._resolve_part(scope, sub):
                a = agg.get(tid)
                if a is None:
                    agg[tid] = [c, lo, hi]
                else:
                    a[0] += c
                    a[1] = min(a[1], lo)
                    a[2] = max(a[2], hi)
        tot = sum(a[0] for a in agg.values())
        for tid, (c, lo, hi) in agg.items():
            yield tid, (False, c * part.count // max(tot, 1), lo, hi)

    def _resolve_part(self, scope: _Scope, part: Refs) -> Iterator[tuple[int, tuple[bool, int]]]:
        """Yield ``(tensor_id, (exact, leaves_read, lo, hi))`` for the leaves ``part`` denotes in ``scope``."""
        exact = True
        space, idx = _space_idx(part)
        if space == "p":
            if scope.parent is None:
                yield self.g.root_param_index[idx], (True, part.count, *_leaf_range(part))
                return
            pnode = scope.parent.spec.body.nodes[scope.node_idx]
            base = self._member_arg_refs(pnode, idx, scope.member)
            if pnode.form == "batch" and pnode.axes[idx] == 0 and pnode.n > 1:
                # An axis-0 batched argument: every member reads its own window (an expert's weight slice, a
                # sequence's rows).  The canonical member gives the tensor set and the per-copy counts; the
                # ranges are widened to the bounding box over the members (all of them when few, else the
                # first / middle / last probes) so that ``Edge.ranges`` covers what the op's copies read.
                hits = list(self._through(scope.parent, base, part))
                box: dict[int, list[int]] = {}
                members = range(pnode.n) if pnode.n <= 64 else sorted({0, pnode.n // 2, pnode.n - 1})
                for m in members:
                    if m == scope.member:
                        continue
                    for tid, (_, _, lo, hi) in self._through(scope.parent, self._member_arg_refs(pnode, idx, m), part):
                        b = box.get(tid)
                        if b is None:
                            box[tid] = [lo, hi]
                        else:
                            b[0], b[1] = min(b[0], lo), max(b[1], hi)
                for tid, (ex, c, lo, hi) in hits:
                    b = box.get(tid)
                    yield tid, (ex, c, lo if b is None else min(lo, b[0]), hi if b is None else max(hi, b[1]))
                return
            yield from self._through(scope.parent, base, part)
            return
        node = scope.spec.body.nodes[idx]
        if node.form == "scan" or _is_terminal(node.fn):
            op = self._op_for(scope, idx, self._mult_of(scope))
            yield op.out, (exact, part.count, *_leaf_range(part))
            return
        if node.form == "call":
            yield from self._through(_Scope(node.fn, scope, idx, 0), node.fn.body.ret, part)
            return
        assert node.form == "batch"
        L = node.fn.out_leaves
        lo, hi = _leaf_range(part)
        m0, m1 = lo // L, hi // L
        if m0 == m1:
            yield from self._through(_Scope(node.fn, scope, idx, m0), node.fn.body.ret, _shift(part, -m0 * L))
            return
        # spans several members: restrict the part to each member's leaf window and resolve through that
        # member's return.  Members of one batch share producing ops (by construction of `_op_for`), so
        # for large spans a few representative members are resolved and the counts are scaled.
        n_members = m1 - m0 + 1

        def member(m: int, sub: Refs) -> Iterator[tuple[int, tuple[bool, int]]]:
            child = _Scope(node.fn, scope, idx, m)
            for sp in _parts(sub):
                yield from self._through(child, node.fn.body.ret, sp)

        if n_members > 64:
            # All members of a batch resolve to the same producing ops / root tensors (same body, and
            # `_op_for` keys ops by node position), so the tensor *set* is that of any interior member;
            # the edge members may see a truncated pattern.  Probe first / middle / last, take the union of
            # tensors and distribute the total count in proportion to the probes (exact iff periodic).
            exact_all = _periodic(part, L)
            probes = sorted({m0, (m0 + m1) // 2, m1})
            agg: dict[int, list[int]] = {}
            for m in probes:
                sub = _restrict(part, m * L, (m + 1) * L)
                if sub.count == 0:
                    continue
                for tid, (ex, c, lo, hi) in member(m, sub):
                    a = agg.get(tid)
                    if a is None:
                        agg[tid] = [c, lo, hi]
                    else:
                        a[0] += c
                        a[1] = min(a[1], lo)
                        a[2] = max(a[2], hi)
            per = sum(a[0] for a in agg.values())
            for tid, (c, lo, hi) in agg.items():
                # unprobed members lie between the probes: the bounding box of the probes covers them
                yield tid, (exact_all, c * part.count // max(per, 1), lo, hi)
            return
        for m in range(m0, m1 + 1):
            sub = _restrict(part, m * L, (m + 1) * L)
            if sub.count == 0:
                continue
            yield from member(m, sub)

    @staticmethod
    def _mult_of(scope: _Scope) -> int:
        m, s = 1, scope
        while s.parent is not None:
            pnode = s.parent.spec.body.nodes[s.node_idx]
            if pnode.form == "batch":
                m *= pnode.n
            s = s.parent
        return m


def extract(bp) -> OpGraph:
    """Operator graph of a :class:`accumulation.algorithms.registry.BuiltProgram` (or any object with
    ``.program`` and ``.roles``)."""
    return _Extractor(bp.program, bp.roles).run()
