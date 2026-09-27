"""Exact minimum runtime input ``I*(P; F, G, X)`` of micro Verity circuits (SPEC §1, §4).

Everything here works on a :class:`FlatCircuit`: the fully expanded gate list of a program.  The two
functions that define the problem are deliberately tiny and literal so that they can be checked against
SPEC §1 by eye -- they are the ground truth every solver (and, through the tests, every bound) is held to:

* :func:`partition_cost` -- ``sum_R in(R)`` for an assignment gate -> RU, where ``in(R)`` is the set of
  *distinct* values entering ``R`` (non-fixed ``Input`` leaves read by some gate of ``R``, plus outputs of
  gates outside ``R`` read by some gate of ``R``), weighted by width in bytes.  Outputs and fixed leaves are
  free.
* :func:`is_legal` -- ``in(R) <= X`` and ``work(R) <= G`` for every RU (``G=None``: no total-work cap) and
  ``work(Up_R(g)) <= F`` for every gate, where ``Up_R(g)`` is ``g`` plus everything reachable backwards from
  ``g`` along operand wires whose both ends lie in ``R`` (``Input`` gates are in no RU, carry no work and stop
  the walk).

Three solvers compute the minimum over all partitions of the non-``Input`` gates (after the lossless
presolve of :func:`_reduce`, which glues zero-work constants to their unique consumer):

* ``brute`` -- branch and bound over set partitions as restricted growth strings in gate order.  Gate order
  is topological, so when a gate is placed all of its operands are already placed; ``in(R)``, the running
  total and ``Up_R(g)`` are therefore exact on the partial assignment and prune immediately.  Two
  admissible bounds on the remaining cost (unseen non-fixed inputs; a packing of forced re-imports) make it
  the fastest method on most cells up to ~30 gates.
* ``milp`` -- a 0/1 program (scipy/HiGHS) in the pairwise "same RU" variables ``s[a, b]`` with
  transitivity, per-gate import indicators and capacity, representative-counted import costs, and
  aggregated "every cut wire is paid" rows that give the LP relaxation real strength.  ``X`` is exact;
  ``F`` is enforced by lazily added no-good cuts (a violating same-RU gate set is forbidden, then re-solved).
* ``milp-assign`` -- the textbook assignment formulation ``x[g, r]`` / ``y[v, r]`` with
  ``y[v, r] >= x[g, r] - x[p, r]``; exact but slow (weak relaxation), kept as an independent cross-check.

``exact_min_input`` is the public entry point; ``method='auto'`` uses brute force for small circuits and
otherwise a node-budgeted branch and bound with the pairwise MILP as fallback.  Every result is re-verified
with :func:`is_legal` / :func:`partition_cost` on the original circuit before it is returned.
"""

from __future__ import annotations

import math
import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from verity_ir.layout import resolve
from verity_ir.program import Program

#: roles whose leaves are charged when they enter an RU (everything that is not ``fixed``)
NONFIXED_ROLES = ("accumulated", "carried", "token", "seed")

#: ``'auto'`` uses brute force up to this many non-``Input`` gates
BRUTE_MAX_GATES = 11
#: above that, ``'auto'`` first tries the branch and bound with this node budget, then the MILP
AUTO_BRUTE_NODES = 3_000_000


class Infeasible(ValueError):
    """No partition satisfies the ``X`` / ``F`` constraints."""


# ---------------------------------------------------------------------------------------------------------
# flattening
# ---------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class FlatCircuit:
    """The expanded gate list of a program.  Index ``i`` is the root-scoped gate index; ``operands[i]`` is
    the *deduplicated* sorted tuple of operand gate indices (a gate reading one value twice imports it
    once).  ``gates`` are the non-``Input`` indices -- the set that gets partitioned -- in ascending order,
    which is a topological order (every operand index is smaller than its consumer's)."""

    n: int
    work: tuple[int, ...]
    width_bits: tuple[int, ...]
    operands: tuple[tuple[int, ...], ...]
    is_input: tuple[bool, ...]
    input_role: tuple[str | None, ...]
    input_param: tuple[str | None, ...]
    prim: tuple[str, ...]
    outputs: tuple[int, ...]
    nonfixed_inputs: frozenset[int]
    gates: tuple[int, ...]

    # -- derived -------------------------------------------------------------------------------------------
    @property
    def n_gates(self) -> int:
        """Number of non-``Input`` gates (the partitioned set)."""
        return len(self.gates)

    @property
    def n_inputs(self) -> int:
        return self.n - len(self.gates)

    def bytes_of(self, v: int) -> int:
        return -(-self.width_bits[v] // 8)

    def total_work(self) -> int:
        return sum(self.work[g] for g in self.gates)

    def nonfixed_input_bytes(self) -> int:
        return sum(self.bytes_of(v) for v in self.nonfixed_inputs)

    def consumers(self) -> dict[int, tuple[int, ...]]:
        """value (gate index) -> ascending tuple of non-``Input`` gates that read it."""
        out: dict[int, list[int]] = {}
        for g in self.gates:
            for o in self.operands[g]:
                out.setdefault(o, []).append(g)
        return {v: tuple(c) for v, c in out.items()}

    def describe(self) -> str:
        lines = []
        for i in range(self.n):
            if self.is_input[i]:
                lines.append(f"{i:4d} Input<{self.width_bits[i]}> {self.input_param[i]} ({self.input_role[i]})")
            else:
                lines.append(f"{i:4d} {self.prim[i]} w={self.work[i]} <{self.width_bits[i]}> ops={list(self.operands[i])}")
        return "\n".join(lines)


def flatten(bp, roles: Mapping[str, str] | None = None) -> FlatCircuit:
    """Expand a :class:`~accumulation.algorithms.registry.BuiltProgram` (or any object with ``.program``,
    ``.roles`` and optionally ``.param_names``; or a bare :class:`verity_ir.Program` plus ``roles``) into a
    :class:`FlatCircuit`.  Every ``Input`` gate must belong to exactly one root parameter and every root
    parameter must have a role (no silent ``fixed`` default: a missing role would make leaves free)."""
    if isinstance(bp, Program):
        prog = bp
        if roles is None:
            raise TypeError("flatten(Program) needs roles={param: role}")
        param_names = tuple(n for n, _ in prog.fn.signature()[0])
    else:
        prog = bp.program
        roles = dict(bp.roles) if roles is None else roles
        param_names = tuple(getattr(bp, "param_names", None) or (n for n, _ in prog.fn.signature()[0]))
    circ = prog.circuit
    n = circ.size
    owner: dict[int, str] = {}
    for pi, name in enumerate(param_names):
        if name not in roles:
            raise KeyError(f"root parameter {name!r} has no role")
        coll = prog.input_coll(pi)
        for j in range(coll.type.leaves):
            g = resolve(circ.root_scope, coll.refs[j])
            if g in owner:
                raise AssertionError(f"Input gate {g} owned by both {owner[g]!r} and {name!r}")
            owner[g] = name
    work: list[int] = []
    width: list[int] = []
    operands: list[tuple[int, ...]] = []
    is_input: list[bool] = []
    input_role: list[str | None] = []
    input_param: list[str | None] = []
    prim: list[str] = []
    gates: list[int] = []
    nonfixed: set[int] = set()
    for i in range(n):
        gt = circ.gate(i)
        fam = getattr(gt.prim, "family", None)
        inp = fam == "Input"
        if inp != (i in owner):
            raise AssertionError(f"gate {i} ({gt.prim.id}): Input-ness {inp} disagrees with parameter ownership")
        ops = tuple(sorted({int(o) for o in gt.operands}))
        if ops and ops[-1] >= i:
            raise AssertionError(f"gate {i} reads a later gate {ops[-1]}: not in topological order")
        if inp:
            if ops:
                raise AssertionError(f"Input gate {i} has operands")
            name = owner[i]
            role = roles[name]
            input_role.append(role)
            input_param.append(name)
            work.append(0)
            if role != "fixed":
                if role not in NONFIXED_ROLES:
                    raise ValueError(f"unknown role {role!r} for parameter {name!r}")
                nonfixed.add(i)
        else:
            input_role.append(None)
            input_param.append(None)
            work.append(int(getattr(gt.prim, "work", 1)))
            gates.append(i)
        width.append(int(gt.prim.ret.w))
        operands.append(ops)
        is_input.append(inp)
        prim.append(gt.prim.name)
    return FlatCircuit(n=n, work=tuple(work), width_bits=tuple(width), operands=tuple(operands),
                       is_input=tuple(is_input), input_role=tuple(input_role), input_param=tuple(input_param),
                       prim=tuple(prim), outputs=tuple(circ.root_outputs()), nonfixed_inputs=frozenset(nonfixed),
                       gates=tuple(gates))


def make_flat(work: Iterable[int], width_bits: Iterable[int], operands: Iterable[Iterable[int]],
              input_role: Iterable[str | None], outputs: Iterable[int] = ()) -> FlatCircuit:
    """Hand-written circuit (tests): ``input_role[i]`` is ``None`` for a computing gate, else the role of the
    ``Input`` gate ``i``.  Operands are deduplicated here exactly as :func:`flatten` does."""
    work, width_bits, input_role = list(work), list(width_bits), list(input_role)
    ops = [tuple(sorted({int(o) for o in os})) for os in operands]
    n = len(work)
    assert len(width_bits) == n and len(ops) == n and len(input_role) == n
    is_input = [r is not None for r in input_role]
    gates = [i for i in range(n) if not is_input[i]]
    for i in range(n):
        assert all(o < i for o in ops[i]), f"gate {i} not topological"
        if is_input[i]:
            assert not ops[i], f"Input gate {i} has operands"
    nonfixed = frozenset(i for i in range(n) if is_input[i] and input_role[i] != "fixed")
    return FlatCircuit(n=n, work=tuple(int(w) for w in work), width_bits=tuple(int(w) for w in width_bits),
                       operands=tuple(ops), is_input=tuple(is_input), input_role=tuple(input_role),
                       input_param=tuple(f"in{i}" if is_input[i] else None for i in range(n)),
                       prim=tuple("Input" if is_input[i] else f"g{i}" for i in range(n)),
                       outputs=tuple(outputs), nonfixed_inputs=nonfixed, gates=tuple(gates))


# ---------------------------------------------------------------------------------------------------------
# the definition (SPEC §1), literally
# ---------------------------------------------------------------------------------------------------------

def _check_assignment(flat: FlatCircuit, assignment: Mapping[int, int]) -> None:
    for g in flat.gates:
        if g not in assignment:
            raise ValueError(f"gate {g} is not assigned to an RU")
    for g in assignment:
        if flat.is_input[g]:
            raise ValueError(f"Input gate {g} cannot be assigned to an RU")


def ru_imports(flat: FlatCircuit, assignment: Mapping[int, int]) -> dict[int, set[int]]:
    """``in(R)`` as a set of value (gate) indices for every RU ``R`` in ``assignment``."""
    _check_assignment(flat, assignment)
    imports: dict[int, set[int]] = {}
    for g in flat.gates:
        r = assignment[g]
        s = imports.setdefault(r, set())
        for v in flat.operands[g]:
            if flat.is_input[v]:
                if v in flat.nonfixed_inputs:      # fixed leaves are free
                    s.add(v)
            elif assignment[v] != r:               # output of a gate outside R
                s.add(v)
    return imports


def partition_cost(flat: FlatCircuit, assignment: Mapping[int, int]) -> int:
    """``sum_R in(R)`` in bytes (distinct values per RU, each at its width in bytes)."""
    return sum(sum(flat.bytes_of(v) for v in s) for s in ru_imports(flat, assignment).values())


def up_set(flat: FlatCircuit, assignment: Mapping[int, int], g: int) -> frozenset[int]:
    """``Up_R(g)``: ``g`` plus every gate reachable backwards from ``g`` through operand wires that stay
    inside ``R = assignment[g]``.  ``Input`` gates are in no RU and stop the walk."""
    r = assignment[g]
    seen = {g}
    stack = [g]
    while stack:
        u = stack.pop()
        for p in flat.operands[u]:
            if not flat.is_input[p] and assignment[p] == r and p not in seen:
                seen.add(p)
                stack.append(p)
    return frozenset(seen)


def up_work(flat: FlatCircuit, assignment: Mapping[int, int], g: int) -> int:
    return sum(flat.work[u] for u in up_set(flat, assignment, g))


def f_violations(flat: FlatCircuit, assignment: Mapping[int, int], F: int) -> list[tuple[int, frozenset[int]]]:
    """All gates ``g`` with ``work(Up_R(g)) > F``, with their ``Up_R(g)``, in gate order."""
    out = []
    for g in flat.gates:
        u = up_set(flat, assignment, g)
        if sum(flat.work[v] for v in u) > F:
            out.append((g, u))
    return out


def ru_work(flat: FlatCircuit, assignment: Mapping[int, int]) -> dict[int, int]:
    """``work(R)`` (total work of the gates of ``R``) for every RU in ``assignment``."""
    out: dict[int, int] = {}
    for g in flat.gates:
        out[assignment[g]] = out.get(assignment[g], 0) + flat.work[g]
    return out


def reach_masks(flat: FlatCircuit) -> tuple[dict[int, int], dict[int, int]]:
    """``(anc, desc)``: for every non-``Input`` gate its strict ancestors / strict descendants among the
    non-``Input`` gates, as bitmasks over gate indices (``1 << gate``).  ``flat.gates`` is topological."""
    anc: dict[int, int] = {}
    for g in flat.gates:
        m = 0
        for o in flat.operands[g]:
            if not flat.is_input[o]:
                m |= (1 << o) | anc[o]
        anc[g] = m
    desc: dict[int, int] = {}
    cons = flat.consumers()
    for g in reversed(flat.gates):
        m = 0
        for c in cons.get(g, ()):
            m |= (1 << c) | desc[c]
        desc[g] = m
    return anc, desc


def quotient_cycle(flat: FlatCircuit, assignment: Mapping[int, int]) -> tuple[int, int, int] | None:
    """SPEC §0 (2026-09-15): the RU quotient graph must be acyclic, equivalently every RU is **convex** in the
    gate DAG.  Returns ``None`` when acyclic, else a witness ``(a, h, b)``: gates ``a, b`` share an RU while
    ``h`` on a path ``a -> ... -> h -> ... -> b`` lies in another RU."""
    anc, desc = reach_masks(flat)
    members: dict[int, int] = {}
    for g in flat.gates:
        members[assignment[g]] = members.get(assignment[g], 0) | (1 << g)
    for r, mem in members.items():
        if mem & (mem - 1) == 0:
            continue                                  # singleton: trivially convex
        d = 0
        a_ = 0
        m = mem
        while m:
            b = m & -m
            g = b.bit_length() - 1
            d |= desc[g]
            a_ |= anc[g]
            m ^= b
        bad = d & a_ & ~mem
        if bad:
            h = (bad & -bad).bit_length() - 1
            # witness endpoints: a member ancestor of h and a member descendant of h
            a = ((anc[h] & mem) & -(anc[h] & mem)).bit_length() - 1
            bb = ((desc[h] & mem) & -(desc[h] & mem)).bit_length() - 1
            return a, h, bb
    return None


def is_legal(flat: FlatCircuit, assignment: Mapping[int, int], F: int | None, X: int | None, G: int | None = None,
             *, acyclic: bool = True) -> tuple[bool, str]:
    """SPEC §0/§1: legal for ``(F, G, X)`` iff ``in(R) <= X`` and ``work(R) <= G`` for every RU, ``work(Up_R(g)) <= F``
    for every gate, and (``acyclic=True``, the protocol model) the RU quotient graph is acyclic -- every RU is
    convex in the gate DAG.  ``None`` for any of ``F``, ``G``, ``X`` = that cap is absent (``X=None`` is the
    corrected policy model: no per-RU input cap).  ``acyclic=False`` is the pre-2026-09-15 model, kept for the
    ``I*_acyclic / I*_cyclic`` comparison."""
    try:
        imports = ru_imports(flat, assignment)
    except ValueError as e:
        return False, str(e)
    if acyclic:
        w = quotient_cycle(flat, assignment)
        if w is not None:
            a, h, b = w
            return False, (f"cyclic RU quotient: gates {a} and {b} share RU {assignment[a]} but gate {h} on a path "
                           f"between them is in RU {assignment[h]}")
    if X is not None:
        for r, s in sorted(imports.items(), key=lambda kv: str(kv[0])):
            b = sum(flat.bytes_of(v) for v in s)
            if b > X:
                return False, f"RU {r} imports {b} bytes > X={X} (values {sorted(s)})"
    if G is not None:
        for r, w in sorted(ru_work(flat, assignment).items(), key=lambda kv: str(kv[0])):
            if w > G:
                return False, f"RU {r} has work {w} > G={G} (gates {sorted(g for g in flat.gates if assignment[g] == r)})"
    if F is not None:
        for g in flat.gates:
            u = up_set(flat, assignment, g)
            w = sum(flat.work[v] for v in u)
            if w > F:
                return False, f"gate {g} has work(Up)={w} > F={F} (Up={sorted(u)}, RU {assignment[g]})"
    return True, "ok"


# ---------------------------------------------------------------------------------------------------------
# result
# ---------------------------------------------------------------------------------------------------------

@dataclass
class ExactResult:
    total: int
    assignment: dict[int, int]
    n_units: int
    method: str
    optimal: bool
    seconds: float = 0.0
    rounds: int = 1              # MILP solves (1 + number of lazy F-cut rounds)
    n_cuts: int = 0              # F no-good cuts in the final model
    notes: list[str] = field(default_factory=list)
    bound: int | None = None     # proven lower bound on I* (== total when optimal; MILP dual bound otherwise)
    acyclic: bool = True         # legality model: RU quotient acyclic (SPEC §0) or the old cyclic-allowed model

    def units(self) -> dict[int, list[int]]:
        out: dict[int, list[int]] = {}
        for g, r in sorted(self.assignment.items()):
            out.setdefault(r, []).append(g)
        return out


def _one_ru_if_legal(flat: FlatCircuit, F: int, X: int, G: int | None) -> ExactResult | None:
    """Fast path valid at any circuit size: if the single-RU partition is legal it is optimal, because every
    partition pays at least the bytes of every distinct charged root leaf (each enters some RU) and one RU pays
    exactly that.  Legality: ``work(C) <= G``, charged leaves ``<= X``, and the full backward cone of every gate
    has work ``<= F`` (cones as bitmasks in topological order).  Returns ``None`` when not legal."""
    total_w = flat.total_work()
    if G is not None and total_w > G:
        return None
    # charged root leaves that some gate actually reads (a dead root parameter costs nothing in any partition)
    cons = flat.consumers()
    leaves = sum(flat.bytes_of(v) for v in flat.nonfixed_inputs if cons.get(v))
    if leaves > X:
        return None
    if F < total_w:
        # cones are monotone along wires (cone(consumer) >= cone(operand)), so the largest cone is at a sink
        cone: dict[int, int] = {}
        has_consumer: set[int] = set()
        for g in flat.gates:                       # ascending = topological
            m = 1 << g
            for o in flat.operands[g]:
                if not flat.is_input[o]:
                    m |= cone[o]
                    has_consumer.add(o)
            cone[g] = m
        by_work: dict[int, int] = {}
        for g in flat.gates:
            if flat.work[g]:
                by_work[flat.work[g]] = by_work.get(flat.work[g], 0) | (1 << g)
        for g in flat.gates:
            if g in has_consumer:
                continue
            if sum(w * (cone[g] & mask).bit_count() for w, mask in by_work.items()) > F:
                return None
    assignment = {g: 0 for g in flat.gates}
    return ExactResult(total=leaves, assignment=assignment, n_units=1 if flat.gates else 0, method="one-ru",
                       optimal=True, notes=["single RU is legal: optimal by the charged-leaves argument"])


def _no_cap_X(flat: FlatCircuit) -> int:
    """An ``X`` no RU can exceed: the bytes of every value that could ever enter an RU."""
    return sum(flat.bytes_of(v) for v in range(flat.n) if (not flat.is_input[v]) or v in flat.nonfixed_inputs) + 1


def _normalise(assignment: Mapping[int, int], gates: Iterable[int]) -> dict[int, int]:
    """Relabel RUs by first appearance in gate order (restricted-growth form)."""
    lab: dict[int, int] = {}
    out = {}
    for g in gates:
        r = assignment[g]
        if r not in lab:
            lab[r] = len(lab)
        out[g] = lab[r]
    return out


# ---------------------------------------------------------------------------------------------------------
# presolve: constants join their unique consumer (WLOG)
# ---------------------------------------------------------------------------------------------------------

def _reduce(flat: FlatCircuit) -> tuple[FlatCircuit, dict[int, int]]:
    """Absorb every gate ``z`` with zero work, no charged operands (no gate operands, no non-fixed ``Input``
    operands) and exactly one consumer ``c`` into ``c``'s RU.  This loses nothing: moving such a ``z`` into
    ``RU(c)`` removes the import of ``out(z)`` from ``RU(c)``, adds no import anywhere (``z`` reads nothing
    that is charged), adds zero work to any ``Up`` set, and leaves every other RU's imports unchanged (the
    only reader of ``out(z)`` is ``c``).  So every legal partition can be rewritten to one that is at least
    as cheap and has ``z`` with ``c``.  In the ``MatmulT`` circuits this removes every ``Zero32``.

    Returns the reduced circuit (``z`` dropped from ``gates``, removed from ``c``'s operands) and the map
    ``z -> c``.  The reduced circuit still indexes gates by their original indices."""
    cons = flat.consumers()
    absorbed: dict[int, int] = {}
    for z in flat.gates:
        if flat.work[z] != 0:
            continue
        if any((not flat.is_input[o]) or (o in flat.nonfixed_inputs) for o in flat.operands[z]):
            continue
        cz = cons.get(z, ())
        if len(cz) == 1:
            absorbed[z] = cz[0]
    if not absorbed:
        return flat, {}
    gates = tuple(g for g in flat.gates if g not in absorbed)
    operands = tuple(tuple(o for o in flat.operands[i] if o not in absorbed) if not flat.is_input[i] else flat.operands[i]
                     for i in range(flat.n))
    red = FlatCircuit(n=flat.n, work=flat.work, width_bits=flat.width_bits, operands=operands, is_input=flat.is_input,
                      input_role=flat.input_role, input_param=flat.input_param, prim=flat.prim, outputs=flat.outputs,
                      nonfixed_inputs=flat.nonfixed_inputs, gates=gates)
    return red, absorbed


def _expand(assignment: dict[int, int], absorbed: dict[int, int]) -> dict[int, int]:
    out = dict(assignment)
    for z, c in absorbed.items():
        out[z] = out[c]
    return out


# ---------------------------------------------------------------------------------------------------------
# brute force
# ---------------------------------------------------------------------------------------------------------

class _Budget(Exception):
    """Node budget of the branch and bound exhausted (``'auto'`` then falls back to the MILP)."""


class _Found(Exception):
    """Incumbent equals a known lower bound: search can stop (optimal)."""


def _solve_brute(flat: FlatCircuit, F: int, X: int, G: int | None = None, node_limit: int | None = None, *,
                 acyclic: bool = True, lower_hint: int | None = None) -> ExactResult:
    t0 = time.perf_counter()
    gates = flat.gates
    n = len(gates)
    pos = {g: i for i, g in enumerate(gates)}
    # convexity (acyclic quotient): placing gate i into RU r is legal iff every ancestor of i that descends from a
    # member of r is itself a member: anc[i] & desc(r) & ~mem(r) == 0 (positions; placements are topological)
    anc_p = [0] * n
    desc_p = [0] * n
    if acyclic:
        anc_g, desc_g = reach_masks(flat)
        for g in gates:
            i = pos[g]
            m = anc_g[g]
            while m:
                b = m & -m
                anc_p[i] |= 1 << pos[b.bit_length() - 1]
                m ^= b
            m = desc_g[g]
            while m:
                b = m & -m
                desc_p[i] |= 1 << pos[b.bit_length() - 1]
                m ^= b
    ru_mem: list[int] = []                        # member mask per RU
    ru_desc: list[int] = []                       # union of members' descendants per RU
    nbytes = [flat.bytes_of(v) for v in range(flat.n)]
    nf_ops = [tuple(o for o in flat.operands[g] if o in flat.nonfixed_inputs) for g in gates]
    gate_ops = [tuple(pos[o] for o in flat.operands[g] if not flat.is_input[o]) for g in gates]
    gate_val = list(gates)                        # position -> value index
    vpos = {g: i for i, g in enumerate(gates)}    # value index -> position (non-Input values only)
    wpos = [flat.work[g] for g in gates]
    check_F = F < flat.total_work()
    check_G = G is not None and G < flat.total_work()
    if G is not None and any(w > G for w in wpos):
        raise Infeasible(f"a single gate has work {max(wpos)} > G={G}")
    ru_work_: list[int] = []                      # total work per RU (for the G cap)
    # nonfixed inputs still to be read by gates at positions >= i (for the admissible remaining bound)
    suffix: list[tuple[int, ...]] = [()] * (n + 1)
    acc: set[int] = set()
    for i in range(n - 1, -1, -1):
        acc |= set(nf_ops[i])
        suffix[i] = tuple(sorted(acc))

    assign = [-1] * n
    ru_imp: list[set[int]] = []
    ru_cost: list[int] = []
    imported_any: dict[int, int] = {}
    up_mask = [0] * n
    best_cost: list[int | None] = [None]
    best_assign: list[list[int] | None] = [None]
    nodes = [0]

    def work_of_mask(m: int) -> int:
        w = 0
        while m:
            b = m & -m
            w += wpos[b.bit_length() - 1]
            m ^= b
        return w

    def packing_bound(i: int, k: int) -> int:
        """Admissible bound on the imports the remaining gates still force, disjoint from the unseen-input
        term: a remaining gate ``j`` whose operands include values already in play (non-fixed inputs some
        RU has imported, or outputs of placed gates) must, in whichever RU it ends up, see each of those
        values imported there; ``m(j)`` is the cheapest option (an existing RU, crediting what it already
        holds, or a fresh RU).  Gates with pairwise disjoint value sets force distinct ``(value, RU)``
        charges, so their ``m`` add up; the greedy picks large ``m`` first."""
        terms = []
        for j in range(i, n):
            vj = [v for v in nf_ops[j] if v in imported_any]
            for p in gate_ops[j]:
                if p < i:
                    vj.append(gate_val[p])
            if not vj:
                continue
            m = sum(nbytes[v] for v in vj)          # fresh RU: everything is new
            for r in range(k):
                imp = ru_imp[r]
                c = 0
                for v in vj:
                    if v in imp:
                        continue
                    vp = vpos.get(v)
                    if vp is not None and assign[vp] == r:
                        continue
                    c += nbytes[v]
                if c < m:
                    m = c
                    if m == 0:
                        break
            if m:
                terms.append((m, vj))
        terms.sort(key=lambda t: -t[0])
        used: set[int] = set()
        lb = 0
        for m, vj in terms:
            if any(v in used for v in vj):
                continue
            used.update(vj)
            lb += m
        return lb

    def rec(i: int, k: int, cost: int) -> None:
        nodes[0] += 1
        if node_limit is not None and nodes[0] > node_limit:
            raise _Budget()
        if i == n:
            if best_cost[0] is None or cost < best_cost[0]:
                best_cost[0] = cost
                best_assign[0] = assign.copy()
                if lower_hint is not None and cost <= lower_hint:
                    raise _Found()
            return
        if best_cost[0] is not None:
            lb = cost + sum(nbytes[v] for v in suffix[i] if v not in imported_any)
            if lb >= best_cost[0]:
                return
            if k >= 1 and lb + packing_bound(i, k) >= best_cost[0]:
                return
        cands = []
        for r in range(k + 1):
            new_ru = r == k
            # values entering RU r because of this gate
            new_vals = list(nf_ops[i])
            for p in gate_ops[i]:
                if assign[p] != r:
                    new_vals.append(gate_val[p])
            if not new_ru:
                cur = ru_imp[r]
                new_vals = [v for v in new_vals if v not in cur]
            delta = sum(nbytes[v] for v in new_vals)
            if (0 if new_ru else ru_cost[r]) + delta > X:
                continue
            if check_G and (0 if new_ru else ru_work_[r]) + wpos[i] > G:
                continue
            if acyclic and not new_ru and anc_p[i] & ru_desc[r] & ~ru_mem[r]:
                continue                              # a gate outside r lies on a path from r into i
            if best_cost[0] is not None and cost + delta >= best_cost[0]:
                continue
            m = 0
            if check_F:
                m = 1 << i
                for p in gate_ops[i]:
                    if assign[p] == r:
                        m |= up_mask[p]
                if work_of_mask(m) > F:
                    continue
            cands.append((delta, r, new_vals, m))
        cands.sort(key=lambda t: (t[0], t[1]))      # cheapest placement first: good incumbents early
        for delta, r, new_vals, m in cands:
            if best_cost[0] is not None and cost + delta >= best_cost[0]:
                break
            new_ru = r == k
            up_mask[i] = m
            # apply
            assign[i] = r
            if new_ru:
                ru_imp.append(set(new_vals))
                ru_cost.append(delta)
                ru_work_.append(wpos[i])
                ru_mem.append(1 << i)
                ru_desc.append(desc_p[i])
            else:
                ru_imp[r].update(new_vals)
                ru_cost[r] += delta
                ru_work_[r] += wpos[i]
                prev_mem, prev_desc = ru_mem[r], ru_desc[r]
                ru_mem[r] |= 1 << i
                ru_desc[r] |= desc_p[i]
            for v in new_vals:
                imported_any[v] = imported_any.get(v, 0) + 1
            rec(i + 1, k + 1 if new_ru else k, cost + delta)
            # undo
            for v in new_vals:
                c = imported_any[v] - 1
                if c:
                    imported_any[v] = c
                else:
                    del imported_any[v]
            if new_ru:
                ru_imp.pop()
                ru_cost.pop()
                ru_work_.pop()
                ru_mem.pop()
                ru_desc.pop()
            else:
                ru_imp[r].difference_update(new_vals)
                ru_cost[r] -= delta
                ru_work_[r] -= wpos[i]
                ru_mem[r], ru_desc[r] = prev_mem, prev_desc
            assign[i] = -1

    notes = []
    try:
        rec(0, 0, 0)
    except _Found:
        notes.append(f"stopped early: incumbent {best_cost[0]} meets the known lower bound {lower_hint}")
    if best_cost[0] is None:
        raise Infeasible(f"no legal partition for F={F}, G={G}, X={X}")
    assignment = {gates[i]: best_assign[0][i] for i in range(n)}
    ok, why = is_legal(flat, assignment, F, X, G, acyclic=acyclic)
    assert ok, why
    total = partition_cost(flat, assignment)
    assert total == best_cost[0], (total, best_cost[0])
    return ExactResult(total=total, assignment=assignment, n_units=len(set(assignment.values())), method="brute",
                       optimal=True, seconds=time.perf_counter() - t0, notes=[f"nodes={nodes[0]}"] + notes, acyclic=acyclic)


# ---------------------------------------------------------------------------------------------------------
# MILP (scipy HiGHS)
# ---------------------------------------------------------------------------------------------------------

def _shrink_cut(flat: FlatCircuit, S: Iterable[int], root: int, F: int) -> frozenset[int]:
    """Strengthen a violating set: ``S`` is ``Up_R(root)`` (every element reachable from ``root`` through
    ``S``) with ``work(S) > F``.  Removing a *source* of ``S`` (an element none of whose operands lies in
    ``S``) other than ``root`` keeps every remaining element reachable from ``root`` inside the remaining
    set, so as long as the work stays ``> F`` the smaller set is still a valid no-good.  Smallest-work
    sources go first (zero-work constants always leave)."""
    S = set(S)
    w = sum(flat.work[u] for u in S)
    while True:
        cands = [u for u in S if u != root and not any(o in S for o in flat.operands[u])]
        cands = [u for u in sorted(cands, key=lambda u: (flat.work[u], u)) if w - flat.work[u] > F]
        if not cands:
            return frozenset(S)
        u = cands[0]
        S.remove(u)
        w -= flat.work[u]


def _seed_cuts(flat: FlatCircuit, F: int) -> set[frozenset[int]]:
    """Cuts from the all-in-one-RU cones: for every gate whose full backward cone exceeds ``F``."""
    cone: dict[int, frozenset[int]] = {}
    cuts: set[frozenset[int]] = set()
    for g in flat.gates:
        c = {g}
        for o in flat.operands[g]:
            if not flat.is_input[o]:
                c |= cone[o]
        cone[g] = frozenset(c)
        if sum(flat.work[u] for u in c) > F:
            cuts.add(_shrink_cut(flat, c, g, F))
    return cuts


def _path_triples(flat: FlatCircuit) -> list[tuple[int, int, int]]:
    """All ``(a, h, b)`` (gate indices) with ``a -> ... -> h -> ... -> b``: convexity forbids ``a, b`` together
    with ``h`` elsewhere."""
    anc, desc = reach_masks(flat)
    out = []
    for h in flat.gates:
        a_m, d_m = anc[h], desc[h]
        if not a_m or not d_m:
            continue
        aa = []
        m = a_m
        while m:
            b = m & -m
            aa.append(b.bit_length() - 1)
            m ^= b
        m = d_m
        while m:
            b = m & -m
            bb = b.bit_length() - 1
            out.extend((a, h, bb) for a in aa)
            m ^= b
    return out


def _solve_milp_assign(flat: FlatCircuit, F: int, X: int, G: int | None = None, *, time_limit: float | None = None,
                       max_rounds: int = 10_000, verbose: bool = False, acyclic: bool = True) -> ExactResult:
    """Assignment formulation: ``x[g, r]`` (gate ``g`` in RU ``r``, ``r <= g`` in restricted-growth order),
    ``y[v, r]`` (value ``v`` imported by RU ``r``) with ``y[v, r] >= x[g, r] - x[p, r]``.  Exact but its LP
    relaxation is weak (gates can be spread fractionally over RUs at zero import cost), so it is slow beyond
    ~20 gates; kept as an independent cross-check of :func:`_solve_milp_pair`."""
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import csr_array

    t0 = time.perf_counter()
    gates = flat.gates
    n = len(gates)
    pos = {g: i for i, g in enumerate(gates)}
    nbytes = [flat.bytes_of(v) for v in range(flat.n)]
    cons = flat.consumers()

    # -- variables: x[i, r] for r <= i (restricted growth), y[v, r] for r <= max consumer position ----------
    xi: dict[tuple[int, int], int] = {}
    for i in range(n):
        for r in range(i + 1):
            xi[(i, r)] = len(xi)
    yi: dict[tuple[int, int], int] = {}
    values = [v for v in sorted(cons) if (v in flat.nonfixed_inputs) or not flat.is_input[v]]
    for v in values:
        rmax = max(pos[g] for g in cons[v])
        for r in range(rmax + 1):
            yi[(v, r)] = len(xi) + len(yi)
    nvar = len(xi) + len(yi)
    c = np.zeros(nvar)
    for (v, r), j in yi.items():
        c[j] = nbytes[v]

    rows: list[int] = []
    cols: list[int] = []
    vals: list[float] = []
    lbs: list[float] = []
    ubs: list[float] = []

    def add_row(entries: list[tuple[int, float]], lb: float, ub: float) -> None:
        k = len(lbs)
        for j, a in entries:
            rows.append(k)
            cols.append(j)
            vals.append(a)
        lbs.append(lb)
        ubs.append(ub)

    # 1. every gate in exactly one RU
    for i in range(n):
        add_row([(xi[(i, r)], 1.0) for r in range(i + 1)], 1, 1)
    # 2. restricted growth: gate i may use RU r >= 1 only if an earlier gate uses RU r-1
    for i in range(1, n):
        for r in range(1, i + 1):
            ent = [(xi[(i, r)], 1.0)] + [(xi[(j, r - 1)], -1.0) for j in range(r - 1, i)]
            add_row(ent, -np.inf, 0)
    # 3. imports: y[v, r] >= x[g, r] - x[p, r]  (p = producer of v; absent for Input values)
    for v in values:
        for g in cons[v]:
            i = pos[g]
            for r in range(i + 1):
                ent = [(yi[(v, r)], 1.0), (xi[(i, r)], -1.0)]
                if not flat.is_input[v] and r <= pos[v]:
                    ent.append((xi[(pos[v], r)], 1.0))
                add_row(ent, 0, np.inf)
    # 4. capacity
    if X < sum(nbytes[v] for v in values):
        for r in range(n):
            ent = [(yi[(v, r)], float(nbytes[v])) for v in values if (v, r) in yi]
            if ent:
                add_row(ent, -np.inf, X)
    # 4b. total work per RU (G cap): sum_i work_i x[i, r] <= G
    if G is not None and G < flat.total_work():
        if any(flat.work[g] > G for g in gates):
            raise Infeasible(f"a single gate has work > G={G}")
        for r in range(n):
            ent = [(xi[(i, r)], float(flat.work[gates[i]])) for i in range(r, n) if flat.work[gates[i]]]
            if ent:
                add_row(ent, -np.inf, G)
    # 4c. convexity (acyclic RU quotient): x[a, r] + x[b, r] - x[h, r] <= 1 for every path triple a -> h -> b
    if acyclic:
        for a, h, b in _path_triples(flat):
            pa, ph, pb = pos[a], pos[h], pos[b]
            for r in range(min(pa, ph, pb) + 1):
                add_row([(xi[(pa, r)], 1.0), (xi[(pb, r)], 1.0), (xi[(ph, r)], -1.0)], -np.inf, 1)
    # 5. F no-goods (seeded from the full cones, then lazily)
    cuts: set[frozenset[int]] = set()
    check_F = F < flat.total_work()

    def add_cut(S: frozenset[int]) -> None:
        cuts.add(S)
        rmax = min(pos[g] for g in S)
        for r in range(rmax + 1):
            add_row([(xi[(pos[g], r)], 1.0) for g in S], -np.inf, len(S) - 1)

    if check_F:
        for S in sorted(_seed_cuts(flat, F), key=lambda s: (len(s), sorted(s))):
            add_cut(S)

    integrality = np.ones(nvar)
    bounds = Bounds(np.zeros(nvar), np.ones(nvar))
    options: dict = {"disp": bool(verbose)}
    if time_limit is not None:
        options["time_limit"] = float(time_limit)

    rounds = 0
    optimal = False
    notes: list[str] = []
    while True:
        rounds += 1
        if rounds > max_rounds:
            raise RuntimeError(f"lazy F loop exceeded {max_rounds} rounds")
        A = csr_array((np.array(vals), (np.array(rows), np.array(cols))), shape=(len(lbs), nvar))
        res = milp(c, constraints=LinearConstraint(A, np.array(lbs), np.array(ubs)), integrality=integrality,
                   bounds=bounds, options=options)
        if res.status == 2:
            raise Infeasible(f"no legal partition for F={F}, G={G}, X={X} (HiGHS: {res.message})")
        if res.x is None:
            raise RuntimeError(f"HiGHS returned no solution: status={res.status} {res.message}")
        optimal = res.status == 0
        assignment = {gates[i]: r for (i, r), j in xi.items() if res.x[j] > 0.5}
        assert len(assignment) == n, "MILP solution does not assign every gate"
        ok, why = is_legal(flat, assignment, F, X, G, acyclic=acyclic)
        if ok:
            break
        viol = f_violations(flat, assignment, F)
        if not viol:
            raise AssertionError(f"MILP solution violates X or G, which are modelled exactly: {why}")
        new = 0
        for g, U in viol:
            S = _shrink_cut(flat, U, g, F)
            if S not in cuts:
                add_cut(S)
                new += 1
        if new == 0:
            raise AssertionError("F violation but every cut already present (solver returned an infeasible point?)")
        if not optimal:
            notes.append(f"round {rounds}: not optimal ({res.message}); continuing with {new} new cuts")
    total = partition_cost(flat, assignment)
    if optimal:
        assert abs(res.fun - total) < 0.5, (res.fun, total)
    return ExactResult(total=total, assignment=_normalise(assignment, gates), n_units=len(set(assignment.values())),
                       method="milp-assign", optimal=optimal, seconds=time.perf_counter() - t0, rounds=rounds,
                       n_cuts=len(cuts), notes=notes, acyclic=acyclic)


def _components(n: int, same: Iterable[tuple[int, int]]) -> list[int]:
    parent = list(range(n))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in same:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    return [find(a) for a in range(n)]


def _solve_milp_pair(flat: FlatCircuit, F: int, X: int, G: int | None = None, *, time_limit: float | None = None,
                     max_rounds: int = 10_000, verbose: bool = False, up_model: bool = True,
                     acyclic: bool = True) -> ExactResult:
    """Pairwise ("clique partitioning") formulation.  Binary ``s[a, b]`` = gates ``a`` and ``b`` share an RU
    (transitivity on every triple), ``w[v, g]`` = value ``v`` enters ``RU(g)`` (``w[v, g] >= s[g, c] - s[g, p]``
    for every consumer ``c`` of ``v`` with producer ``p``; ``s[g, g] = 1``; no ``p`` term for ``Input``
    values), capacity ``sum_v bytes_v w[v, g] <= X`` for every gate ``g``, ``rep[g]`` = ``g`` is the
    lowest-index gate of its RU (``rep[g] >= 1 - sum_{h<g} s[h, g]``), and ``z[v, g] >= w[v, g] + rep[g] - 1``
    so that ``sum_v bytes_v sum_g z[v, g]`` counts each ``(RU, value)`` import exactly once.  The aggregated
    rows ``sum_g z[v, g] >= 1 - s[p, c]`` (``>= 1`` for non-fixed ``Input`` values) make the LP relaxation
    pay for every cut wire, which is what the assignment formulation lacks.  ``F`` is enforced exactly by the
    continuous ``u[g, h]`` model of ``Up_R(g)`` (``up_model=True``; see below) plus seed no-good cuts
    ``sum_{a<b in S} s[a, b] <= C(|S|, 2) - 1`` and a lazy no-good loop as cross-check (the only F mechanism when
    ``up_model=False``)."""
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import csr_array

    t0 = time.perf_counter()
    gates = flat.gates
    n = len(gates)
    pos = {g: i for i, g in enumerate(gates)}
    nbytes = [flat.bytes_of(v) for v in range(flat.n)]
    cons = flat.consumers()
    values = [v for v in sorted(cons) if (v in flat.nonfixed_inputs) or not flat.is_input[v]]
    prod = {v: (None if flat.is_input[v] else pos[v]) for v in values}

    nvar = 0

    def new_vars(k: int) -> int:
        nonlocal nvar
        base = nvar
        nvar += k
        return base

    si: dict[tuple[int, int], int] = {}
    for a in range(n):
        for b in range(a + 1, n):
            si[(a, b)] = new_vars(1)

    def s_of(a: int, b: int) -> int:
        return si[(a, b) if a < b else (b, a)]

    wi: dict[tuple[int, int], int] = {}
    zi: dict[tuple[int, int], int] = {}
    for v in values:
        for g in range(n):
            if prod[v] == g:
                continue                      # a value never enters its producer's RU
            wi[(v, g)] = new_vars(1)
            zi[(v, g)] = new_vars(1)
    ri: dict[int, int] = {g: new_vars(1) for g in range(1, n)}   # rep[0] == 1 (constant)

    c = np.zeros(nvar)
    lo = np.zeros(nvar)
    hi = np.ones(nvar)
    for (v, g), j in zi.items():
        c[j] = nbytes[v]

    rows: list[int] = []
    cols: list[int] = []
    vals: list[float] = []
    lbs: list[float] = []
    ubs: list[float] = []

    def add_row(entries: list[tuple[int, float]], lb: float, ub: float) -> None:
        k = len(lbs)
        for j, a in entries:
            rows.append(k)
            cols.append(j)
            vals.append(a)
        lbs.append(lb)
        ubs.append(ub)

    # transitivity of "same RU"
    for a in range(n):
        for b in range(a + 1, n):
            for d in range(b + 1, n):
                ab, bd, ad = si[(a, b)], si[(b, d)], si[(a, d)]
                add_row([(ab, 1.0), (bd, 1.0), (ad, -1.0)], -np.inf, 1)
                add_row([(ab, 1.0), (ad, 1.0), (bd, -1.0)], -np.inf, 1)
                add_row([(ad, 1.0), (bd, 1.0), (ab, -1.0)], -np.inf, 1)
    # imports: w[v, g] >= s[g, c] - s[g, p]
    for v in values:
        p = prod[v]
        for cg in cons[v]:
            ci = pos[cg]
            for g in range(n):
                if g == p:
                    continue
                w = wi[(v, g)]
                if g == ci:
                    if p is None:
                        lo[w] = 1.0                                   # own non-fixed input: always imported
                    else:
                        add_row([(w, 1.0), (s_of(ci, p), 1.0)], 1, np.inf)   # w >= 1 - s[c, p]
                else:
                    ent = [(w, 1.0), (s_of(g, ci), -1.0)]
                    if p is not None:
                        ent.append((s_of(g, p), 1.0))
                    add_row(ent, 0, np.inf)
    # capacity per gate (its RU's imports)
    if X < sum(nbytes[v] for v in values):
        for g in range(n):
            ent = [(wi[(v, g)], float(nbytes[v])) for v in values if (v, g) in wi]
            if ent:
                add_row(ent, -np.inf, X)
    # total work of RU(g): work[g] + sum_{h != g} work[h] s[g, h] <= G
    if G is not None and G < flat.total_work():
        wg = [flat.work[g] for g in gates]
        if any(w > G for w in wg):
            raise Infeasible(f"a single gate has work > G={G}")
        for g in range(n):
            ent = [(s_of(g, h), float(wg[h])) for h in range(n) if h != g and wg[h]]
            if ent:
                add_row(ent, -np.inf, G - wg[g])
    # representatives and counted imports
    for g in range(1, n):
        add_row([(ri[g], 1.0)] + [(si[(h, g)], 1.0) for h in range(g)], 1, np.inf)
    for (v, g), z in zi.items():
        if g == 0:
            add_row([(z, 1.0), (wi[(v, g)], -1.0)], 0, np.inf)
        else:
            add_row([(z, 1.0), (wi[(v, g)], -1.0), (ri[g], -1.0)], -1, np.inf)
    # every cut wire is paid somewhere (LP strengthening; implied for integer points).  With several
    # consumers, ``v`` enters one RU per distinct consumer RU (minus the producer's): the count of distinct
    # RUs among consumers ``C`` is ``>= |C| - sum_{pairs} s`` and ``>= 2 - s[c1, c2]`` per pair.
    for v in values:
        p = prod[v]
        zs = [(zi[(v, g)], 1.0) for g in range(n) if (v, g) in zi]
        cps = [pos[cg] for cg in cons[v]]
        if p is None:
            add_row(zs, 1, np.inf)
            for a in range(len(cps)):
                for b in range(a + 1, len(cps)):
                    add_row(zs + [(s_of(cps[a], cps[b]), 1.0)], 2, np.inf)
            if len(cps) >= 3:
                add_row(zs + [(s_of(cps[a], cps[b]), 1.0) for a in range(len(cps)) for b in range(a + 1, len(cps))],
                        len(cps), np.inf)
        else:
            for ci in cps:
                add_row(zs + [(s_of(ci, p), 1.0)], 1, np.inf)
            for a in range(len(cps)):
                for b in range(a + 1, len(cps)):
                    # imports >= [c1 not with p] + [c2 not with p] - [c1 with c2]
                    add_row(zs + [(s_of(cps[a], p), 1.0), (s_of(cps[b], p), 1.0), (s_of(cps[a], cps[b]), 1.0)], 2, np.inf)
    # cover cuts: gates whose non-fixed Input operands alone exceed X can never share an RU; a set T that
    # cannot be together has at most C(|T|-1, 2) same-RU pairs (one part of size |T|-1, one singleton).
    if X < sum(nbytes[v] for v in values):
        from itertools import combinations
        own = [frozenset(o for o in flat.operands[g] if o in flat.nonfixed_inputs) for g in gates]
        n_cover = 0
        pair_cover: set[tuple[int, int]] = set()
        for a, b in combinations(range(n), 2):
            if sum(nbytes[v] for v in own[a] | own[b]) > X:
                pair_cover.add((a, b))
                hi[si[(a, b)]] = 0.0
                n_cover += 1
        covers: set[frozenset[int]] = {frozenset(t) for t in pair_cover}
        for size in (3, 4):
            if n_cover > 20_000:
                break
            for T in combinations(range(n), size):
                if any(frozenset(sub) in covers for sub in combinations(T, size - 1)) or \
                        any((T[i], T[j]) in pair_cover for i in range(size) for j in range(i + 1, size)):
                    continue                                       # not minimal
                u: set[int] = set()
                for t in T:
                    u |= own[t]
                if sum(nbytes[v] for v in u) > X:
                    covers.add(frozenset(T))
                    add_row([(si[(T[i], T[j])], 1.0) for i in range(size) for j in range(i + 1, size)], -np.inf,
                            (size - 1) * (size - 2) // 2)
                    n_cover += 1
                    if n_cover > 20_000:
                        break
    # convexity (acyclic RU quotient): a, b together forces every h on a path a -> h -> b into the same RU
    n_convex = 0
    if acyclic:
        for a, h, b in _path_triples(flat):
            add_row([(s_of(pos[a], pos[b]), 1.0), (s_of(pos[a], pos[h]), -1.0)], -np.inf, 0)
            n_convex += 1
    # F no-goods
    cuts: set[frozenset[int]] = set()
    check_F = F < flat.total_work()

    def add_cut(S: frozenset[int]) -> None:
        cuts.add(S)
        ps = sorted(pos[g] for g in S)
        if len(ps) == 1:
            raise Infeasible(f"gate {next(iter(S))} alone has work > F={F}")
        ent = [(si[(ps[i], ps[j])], 1.0) for i in range(len(ps)) for j in range(i + 1, len(ps))]
        add_row(ent, -np.inf, len(ent) - 1)

    if check_F:
        for S in sorted(_seed_cuts(flat, F), key=lambda s: (len(s), sorted(s))):
            add_cut(S)

    # Exact polynomial-size model of ``Up`` (the no-goods above stay as LP strengthening / safety net):
    # continuous ``u[g, h] >= [h in Up_R(g)]`` for every ancestor ``h`` of ``g``: ``u[g, h] >= s[g, h]`` when
    # ``h`` is a direct operand of ``g``, and ``u[g, h] >= u[g, c] + s[g, h] - 1`` for every consumer ``c`` of
    # ``h`` that is itself an ancestor of ``g``; then ``work[g] + sum_h work[h] u[g, h] <= F``.  At an integer
    # ``s`` the minimal feasible ``u`` is exactly the indicator of ``Up_R(g)``, so the F rows are exact and the
    # lazy loop below terminates in one round (it is kept as a cross-check).
    n_up_vars = 0
    if check_F and up_model:
        anc: list[set[int]] = [set() for _ in range(n)]
        for i, g in enumerate(gates):                              # ascending = topological
            for o in flat.operands[g]:
                if not flat.is_input[o]:
                    anc[i].add(pos[o])
                    anc[i] |= anc[pos[o]]
        wg = [flat.work[g] for g in gates]
        for i in range(n):
            if not anc[i]:
                continue
            ui = {h: new_vars(1) for h in anc[i]}
            n_up_vars += len(ui)
            direct = {pos[o] for o in flat.operands[gates[i]] if not flat.is_input[o]}
            for h, uj in ui.items():
                if h in direct:
                    add_row([(uj, 1.0), (s_of(i, h), -1.0)], 0, np.inf)
                for cg in cons[gates[h]]:
                    ci = pos[cg]
                    if ci == i or ci not in anc[i]:
                        continue
                    add_row([(uj, 1.0), (ui[ci], -1.0), (s_of(i, h), -1.0)], -1, np.inf)
            ent = [(uj, float(wg[h])) for h, uj in ui.items() if wg[h]]
            if ent:
                add_row(ent, -np.inf, F - wg[i])
        lo = np.concatenate([lo, np.zeros(nvar - len(lo))])
        hi = np.concatenate([hi, np.ones(nvar - len(hi))])
        c = np.concatenate([c, np.zeros(nvar - len(c))])

    integrality = np.ones(nvar)
    if n_up_vars:
        integrality[nvar - n_up_vars:] = 0                         # u is continuous
    options: dict = {"disp": bool(verbose)}
    if time_limit is not None:
        options["time_limit"] = float(time_limit)

    rounds = 0
    optimal = False
    notes: list[str] = []
    while True:
        rounds += 1
        if rounds > max_rounds:
            raise RuntimeError(f"lazy F loop exceeded {max_rounds} rounds")
        A = csr_array((np.array(vals), (np.array(rows), np.array(cols))), shape=(len(lbs), nvar))
        res = milp(c, constraints=LinearConstraint(A, np.array(lbs), np.array(ubs)), integrality=integrality,
                   bounds=Bounds(lo, hi), options=options)
        if res.status == 2:
            raise Infeasible(f"no legal partition for F={F}, G={G}, X={X} (HiGHS: {res.message})")
        if res.x is None:
            raise RuntimeError(f"HiGHS returned no solution: status={res.status} {res.message}")
        optimal = res.status == 0
        comp = _components(n, ((a, b) for (a, b), j in si.items() if res.x[j] > 0.5))
        # transitivity is modelled, so components must be cliques
        for (a, b), j in si.items():
            assert (res.x[j] > 0.5) == (comp[a] == comp[b]), "non-transitive same-RU relation from the solver"
        assignment = {gates[i]: comp[i] for i in range(n)}
        ok, why = is_legal(flat, assignment, F, X, G, acyclic=acyclic)
        if ok:
            break
        viol = f_violations(flat, assignment, F)
        if not viol:
            raise AssertionError(f"MILP solution violates X, G or convexity, which are modelled exactly: {why}")
        new = 0
        for g, U in viol:
            S = _shrink_cut(flat, U, g, F)
            if S not in cuts:
                add_cut(S)
                new += 1
        if new == 0:
            raise AssertionError("F violation but every cut already present (solver returned an infeasible point?)")
        if not optimal:
            notes.append(f"round {rounds}: not optimal ({res.message}); continuing with {new} new cuts")
    total = partition_cost(flat, assignment)
    if optimal:
        assert abs(res.fun - total) < 0.5, (res.fun, total)
        bound = total
    else:
        # every row is a necessary condition for legality, so the MILP is a relaxation: its dual bound is a
        # valid lower bound on I* (rounded up: all costs are integers)
        db = getattr(res, "mip_dual_bound", None)
        bound = None if db is None or not math.isfinite(db) else int(math.ceil(db - 1e-6))
        if bound is not None:
            bound = min(bound, total)
    if n_convex:
        notes.append(f"{n_convex} convexity rows")
    return ExactResult(total=total, assignment=_normalise(assignment, gates), n_units=len(set(assignment.values())),
                       method="milp", optimal=optimal, seconds=time.perf_counter() - t0, rounds=rounds,
                       n_cuts=len(cuts), notes=notes, bound=bound, acyclic=acyclic)


# ---------------------------------------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------------------------------------

_METHODS = {"brute": _solve_brute, "milp": _solve_milp_pair, "milp-pair": _solve_milp_pair,
            "milp-assign": _solve_milp_assign}


def exact_min_input(bp_or_flat, *args, G: int | None = None, limit: int = 40, method: str = "auto",
                    roles: Mapping[str, str] | None = None, time_limit: float | None = None,
                    verbose: bool = False, presolve: bool = True, acyclic: bool = True,
                    lower_hint: int | None = None) -> ExactResult:
    """``I*(P; F, G, X)``: the minimum over legal partitions of the non-``Input`` gates of ``sum_R in(R)``.

    ``acyclic=True`` (default; SPEC §0, 2026-09-15): the RU quotient graph must be acyclic -- every RU convex in
    the gate DAG (brute force: ``anc(g) & desc(R) <= R`` when placing ``g`` into ``R``; MILPs: one convexity row
    per path triple ``a -> h -> b``); the returned assignment is re-checked with :func:`quotient_cycle`.
    ``acyclic=False`` is the old model (kept for the ``I*_acyclic / I*_cyclic`` comparison; acyclicity only
    removes partitions, so ``I*_acyclic >= I*_cyclic``).  ``lower_hint``: a known lower bound on ``I*`` (e.g. the
    cyclic optimum); the branch and bound stops as soon as an incumbent meets it.

    Call as ``exact_min_input(bp_or_flat, F, X[, G])`` or, per SPEC §5, ``exact_min_input(program, roles, F,
    X[, G])``; ``G`` (total work per RU, ``None`` = unbounded) may also be passed as a keyword.  ``X=None`` = no
    per-RU input cap (the corrected policy model: legality is ``work(R) <= G`` and ``work(Up_R(g)) <= F`` only);
    ``F=None`` = no serial cap.  ``work(R) <= G`` is a linear per-RU constraint in every solver (brute force prunes on the
    running RU work; both MILPs add one row per RU / per gate).

    ``method``: ``'brute'`` (exhaustive branch and bound), ``'milp'`` (HiGHS, pairwise formulation; ``X``
    and ``G`` exact, ``F`` by lazy no-good cuts), ``'milp-assign'`` (HiGHS, the ``x[g, r]`` / ``y[v, r]``
    assignment formulation -- slower, kept as an independent cross-check), ``'auto'`` (brute for
    <= :data:`BRUTE_MAX_GATES` gates, else milp).  ``presolve`` applies the WLOG constant-absorption of
    :func:`_reduce` before solving (zero-work gates: neutral for ``G``).  The returned assignment always
    covers the *original* gates and is re-verified with :func:`is_legal` / :func:`partition_cost` on the
    original circuit.

    Raises ``ValueError`` if the circuit has more than ``limit`` non-``Input`` gates and :class:`Infeasible`
    if no partition is legal.  ``optimal`` is ``True`` only when the search was exhaustive / HiGHS proved
    optimality."""
    args = list(args)
    if args and isinstance(args[0], Mapping):
        roles = args.pop(0)
    if len(args) == 2:
        F, X = args
    elif len(args) == 3:
        F, X, G_pos = args
        if G is not None and G_pos is not None and int(G) != int(G_pos):
            raise TypeError("G given both positionally and as a keyword with different values")
        G = G_pos if G is None else G
    else:
        raise TypeError("exact_min_input(bp_or_flat, F, X[, G]) or exact_min_input(program, roles, F, X[, G])")
    G = None if G is None else int(G)
    flat = bp_or_flat if isinstance(bp_or_flat, FlatCircuit) else flatten(bp_or_flat, roles)
    # ``None`` caps: X=None is the corrected policy (no per-RU input cap); F=None = no serial cap.  Internally
    # they become values that can never bind (every solver skips a constraint that cannot bind).
    X = _no_cap_X(flat) if X is None else int(X)
    F = flat.total_work() if F is None else int(F)
    one = _one_ru_if_legal(flat, F, X, G)
    if one is not None:
        one.acyclic = acyclic                     # a single RU is trivially convex
        return one
    if flat.n_gates > limit:
        raise ValueError(f"circuit has {flat.n_gates} non-Input gates > limit={limit}")
    if flat.n_gates == 0:
        return ExactResult(total=0, assignment={}, n_units=0, method=method, optimal=True)
    auto = method == "auto"
    if auto:
        method = "brute" if flat.n_gates <= BRUTE_MAX_GATES else "milp"
    if method not in _METHODS:
        raise ValueError(f"unknown method {method!r}; one of {sorted(_METHODS)} or 'auto'")
    red, absorbed = _reduce(flat) if presolve else (flat, {})
    if red.n_gates == 0:
        # everything was a constant chain into one gate -- cannot happen (absorption needs a consumer), guard anyway
        red, absorbed = flat, {}
    t0 = time.perf_counter()
    res = None
    if method == "brute":
        res = _solve_brute(red, F, X, G, acyclic=acyclic, lower_hint=lower_hint)
    else:
        if auto:
            # the branch and bound usually wins on these structured circuits; give it a bounded budget first
            try:
                res = _solve_brute(red, F, X, G, node_limit=AUTO_BRUTE_NODES, acyclic=acyclic, lower_hint=lower_hint)
                res.notes.append("auto: branch and bound within budget")
            except _Budget:
                res = None
        if res is None:
            res = _METHODS[method](red, F, X, G, time_limit=time_limit, verbose=verbose, acyclic=acyclic)
    assignment = _normalise(_expand(res.assignment, absorbed), flat.gates)
    ok, why = is_legal(flat, assignment, F, X, G, acyclic=acyclic)   # safety net incl. quotient acyclicity
    if not ok:
        raise AssertionError(f"solver returned an illegal partition on the original circuit: {why}")
    total = partition_cost(flat, assignment)
    if total != res.total:
        raise AssertionError(f"solver total {res.total} != partition_cost {total} on the original circuit")
    res.assignment = assignment
    res.n_units = len(set(assignment.values()))
    if res.optimal:
        res.bound = total
    res.seconds = time.perf_counter() - t0
    if absorbed:
        res.notes.append(f"presolve absorbed {len(absorbed)} constants")
    return res


__all__ = [
    "BRUTE_MAX_GATES",
    "NONFIXED_ROLES",
    "ExactResult",
    "FlatCircuit",
    "Infeasible",
    "exact_min_input",
    "f_violations",
    "flatten",
    "is_legal",
    "make_flat",
    "partition_cost",
    "quotient_cycle",
    "reach_masks",
    "ru_imports",
    "ru_work",
    "up_set",
    "up_work",
]
