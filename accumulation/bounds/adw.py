"""Accumulation-dependent work (ADW) of an operator graph.

``ADW(P)`` is the total work of the ops that depend on non-fixed *state*: an op contributes iff some root
parameter in the transitive closure of its inputs has role ``accumulated`` or ``carried`` (SPEC §1).  Work on
frozen weights applied to activations that already depend on an adapter counts (the activations carry the
accumulated information); the frozen prefix of a LoRA forward before the first adapter does not.

``ADW_matmul`` restricts to matmul ops; it is the quantity the lower bounds charge.

``credited_macs`` is the target work ``|M(C)|`` of THEORY.md §0: the accumulation-dependent matmul MACs of
ops NOT annotated ``recompute`` (a recomputed product is the same target multiplication performed again and
earns no credit; its work still counts in ``all_work``, the efficiency denominator).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from accumulation.graph.opgraph import OpGraph

STATE_ROLES = frozenset({"accumulated", "carried"})
NONFIXED_ROLES = frozenset({"accumulated", "carried", "token", "seed"})


@dataclass
class ADW:
    total: int                      # work (MAC-eq) of accumulation-dependent ops
    matmul: int                     # ... restricted to kind == 'matmul'
    matmul_macs: int                # M*N*K*copies of those matmuls (excludes chunk/reduction overhead)
    all_work: int                   # total work of the program
    all_macs: int                   # all matmul MACs
    credited_macs: int = 0          # |M(C)|: ADW matmul MACs excluding ops annotated 'recompute'
    recompute_macs: int = 0         # ADW matmul MACs of ops annotated 'recompute'
    by_kind: dict[str, int] = field(default_factory=dict)
    per_op: dict[int, bool] = field(default_factory=dict)  # op id -> depends on state

    @property
    def fraction(self) -> float:
        return self.total / self.all_work if self.all_work else 0.0


def depends_on_state(g: OpGraph, op_id: int) -> bool:
    return any(g.root_roles_upstream(e.src) & STATE_ROLES for e in g.ops[op_id].inputs)


def adw(g: OpGraph) -> ADW:
    per_op: dict[int, bool] = {}
    total = mm = macs = recomp = 0
    by_kind: dict[str, int] = {}
    for o in g.ops:
        dep = depends_on_state(g, o.id)
        per_op[o.id] = dep
        if dep:
            total += o.work
            by_kind[o.kind] = by_kind.get(o.kind, 0) + o.work
            if o.kind == "matmul":
                mm += o.work
                macs += o.macs()
                if o.name == "recompute":
                    recomp += o.macs()
    return ADW(total=total, matmul=mm, matmul_macs=macs, all_work=g.total_work(),
               all_macs=sum(o.macs() for o in g.ops), by_kind=by_kind, per_op=per_op,
               credited_macs=macs - recomp, recompute_macs=recomp)
