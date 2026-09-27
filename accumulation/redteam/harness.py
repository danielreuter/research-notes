"""One red-team instance = ``(BuiltProgram, F, G, X)`` (``G`` = per-RU total-work cap, ``None`` = unbounded).

:func:`evaluate` runs the whole pipeline on an instance and returns a :class:`Record`:

* ``extract`` -> ``lower_bound(g, F, X, G=).total`` (SPEC §5 contract; ``G`` passed only when the signature
  accepts it -- otherwise ``L`` is the valid-but-looser ``G=None`` value and ``Record.L_G is None``),
* ``upper_bound(g, F, X, G=, program=...)`` twice: ``recompute=True`` (headline ``U``) and ``recompute=False``
  (``U_lit``: a literal partition of ``P``'s gates -- the object the exact solver matches),
* ``exact_min_input(flat, F, X, G)`` (time-boxed with ``SIGALRM``; ``optimal`` and the optimal partition
  recorded),
* the literal plan is **materialised** into an explicit gate -> RU assignment (:func:`materialize`) and
  re-checked with the SPEC §1 definitions ``is_legal`` / ``partition_cost`` -- the only check of ``U`` that
  does not trust ``check_plan``.

Verdicts (``Record.violations``) are the things that must never happen:

* ``L_gt_Istar``        -- ``L > I*`` (also when the solver is not proven optimal: ``L > cost(found)`` still
                           refutes ``L``);
* ``Ulit_lt_Istar``     -- the literal plan claims less than the optimum (only with an optimal solver);
* ``Ulit_illegal``      -- the materialised literal plan violates ``X`` or ``F`` per ``is_legal``;
* ``Ulit_cost_under``   -- ``partition_cost`` of the materialised plan exceeds the plan's own total;
* ``Ulit_ru_over``      -- some materialised RU imports more than its unit's declared ``imports_max``;
* ``Urec_lt_L``         -- headline ``U`` below ``L`` (SPEC says ``L`` holds for the recompute reading too);
* ``Ulit_lt_L``         -- literal ``U`` below ``L``;
* ``U_unavailable``     -- ``upper_bound`` raised although a legal partition exists (solver found one);
* ``U_but_infeasible``  -- ``upper_bound`` produced a plan although the solver proved no legal partition;
* ``L_infeasible_but_Istar`` -- ``L`` reports infeasible although the solver found a legal partition.
"""

from __future__ import annotations

import math
import signal
import time
import traceback
from dataclasses import asdict, dataclass, field
from typing import Optional

from accumulation.algorithms.registry import BuiltProgram
from accumulation.bounds.lower import lower_bound
from accumulation.bounds.upper import Plan, upper_bound
from accumulation.exact.solve import (FlatCircuit, Infeasible, exact_min_input, flatten, is_legal,
                                      partition_cost, ru_imports)
from accumulation.graph import extract
from accumulation.graph.opgraph import OpGraph
from accumulation.graph.validate import _op_key_of_gate

BIG = 1 << 60
INF_SENTINEL = 1 << 62


def _versions() -> dict[str, str]:
    """Short content hashes of the modules under test (``lower.py`` is being rewritten while this runs)."""
    import hashlib
    import os
    out = {}
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for rel in ("bounds/lower.py", "bounds/lower_coarse.py", "bounds/coarse.py", "bounds/upper.py", "graph/opgraph.py", "exact/solve.py"):
        try:
            with open(os.path.join(here, rel), "rb") as f:
                out[rel] = hashlib.sha256(f.read()).hexdigest()[:10]
        except OSError:
            out[rel] = "?"
    return out


VERSIONS = _versions()


class SolverTimeout(Exception):
    pass


def _alarm(signum, frame):  # noqa: ARG001
    raise SolverTimeout()


def with_timeout(seconds: float, fn, *a, **kw):
    """Run ``fn`` with a wall-clock cap (main thread only; ``SIGALRM``)."""
    if seconds is None or seconds <= 0:
        return fn(*a, **kw)
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        return fn(*a, **kw)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


# ---------------------------------------------------------------------------------------------------------
# gate <-> op mapping
# ---------------------------------------------------------------------------------------------------------

def op_gate_lists(bp: BuiltProgram, g: OpGraph, flat: FlatCircuit) -> dict[int, list[int]]:
    """op id -> ascending list of its non-``Input`` gate indices (lowering order = batch order)."""
    prog = bp.program
    circ = prog.circuit
    acc_spec = prog.fn
    n_input_nodes = len(prog.root.body.nodes) - len(acc_spec.body.nodes)
    key_to_op = {o.key: o.id for o in g.ops}
    out: dict[int, list[int]] = {o.id: [] for o in g.ops}
    for i in range(circ.size):
        if flat.is_input[i]:
            continue
        gt = circ.gate(i)
        chain = []
        s = gt.scope
        while s is not None:
            chain.append(s)
            s = s.parent
        chain.reverse()
        k_gate = gt.scope.spec.body.node_at(i - gt.scope.offset)
        key = _op_key_of_gate(chain, k_gate, acc_spec, n_input_nodes)
        out[key_to_op[key]].append(i)
    return out


# ---------------------------------------------------------------------------------------------------------
# plan materialisation (literal plans only)
# ---------------------------------------------------------------------------------------------------------

class Unmaterializable(Exception):
    """The plan uses a unit kind / feature this materialiser does not cover (not a defect)."""


def _mm_gate(N: int, Kd: int, m: int, n: int, j: int) -> int:
    """index within a ``MatmulT{M,N,K,CH=1}`` op of gate ``j`` of output ``(m, n)`` (0 = Zero32, 1..K = MACs,
    K+1 = Round16)."""
    return (m * N + n) * (Kd + 2) + j


def _blocks(R: int, size: int) -> list[tuple[int, int]]:
    out = []
    lo = 0
    while lo < R:
        out.append((lo, min(lo + size, R)))
        lo += size
    return out


def _fused_gates(g: OpGraph, gates: list[int], oid: int, rows: int, L: int, pos: list[tuple[int, int]],
                 rowfull: bool) -> list[int]:
    """Gates of fused op ``oid`` (laid out ``rows x L`` positions) that belong to positions ``pos``
    (``(row, col)`` pairs) -- whole rows when ``rowfull``."""
    op = g.ops[oid]
    n = len(gates)
    if rowfull or op.kind in ("rmsnorm", "softmax", "lossgrad"):
        gpr = n // rows
        assert gpr * rows == n
        rs = sorted({r for r, _ in pos})
        return [gates[r * gpr + t] for r in rs for t in range(gpr)]
    P = rows * L
    if n == P:
        return [gates[r * L + c] for r, c in pos]
    if n == 2 * P and op.kind in ("sgdupdate", "perturb", "esupdate"):
        # per row: L first-stage gates then L second-stage gates (SgdRow: Scale16 x K then Sub16 x K)
        return [gates[r * 2 * L + c] for r, c in pos] + [gates[r * 2 * L + L + c] for r, c in pos]
    raise Unmaterializable(f"fused op {oid} ({op.kind}) has {n} gates for {P} positions")


def materialize(plan: Plan, g: OpGraph, flat: FlatCircuit, op_gates: dict[int, list[int]]) -> tuple[dict[int, int], list[tuple[int, int]]]:
    """Explicit gate -> RU assignment of a literal (``recompute=False``) plan, plus ``(ru, unit_index)``
    pairs so per-RU imports can be compared with the unit's ``imports_max``.  Raises
    :class:`Unmaterializable` for unit kinds it does not cover and ``AssertionError`` when the plan's symbolic
    description does not tile the gates exactly once (that is a defect of the plan or of this mapper --
    the caller reports it)."""
    if plan.recompute:
        raise Unmaterializable("recompute plans are not literal partitions")
    assign: dict[int, int] = {}
    ru_of: list[tuple[int, int]] = []
    ru = 0

    def place(gs: list[int], ui: int) -> None:
        nonlocal ru
        if not gs:
            return
        for x in gs:
            assert x not in assign, f"gate {x} placed twice (unit {ui})"
            assign[x] = ru
        ru_of.append((ru, ui))
        ru += 1

    for ui, u in enumerate(plan.units):
        d = u.detail
        if u.kind == "opset":
            gs = [x for o in u.ops for x in op_gates[o]]
            place(gs, ui)
        elif u.kind == "copies":
            op = g.ops[u.ops[0]]
            gates = op_gates[op.id]
            m = d["per_ru"]
            gpc = len(gates) // op.copies
            assert gpc * op.copies == len(gates)
            for lo, hi in _blocks(op.copies, m):
                place(gates[lo * gpc:hi * gpc], ui)
        elif u.kind == "rows":
            op = g.ops[u.ops[0]]
            gates = op_gates[op.id]
            R, r = d["rows_total"], d["rows_per_ru"]
            if d.get("gen_tids"):
                raise Unmaterializable("rows unit with generation")
            gpr = len(gates) // R
            assert gpr * R == len(gates), (op.kind, len(gates), R)
            for lo, hi in _blocks(R, r):
                place(gates[lo * gpr:hi * gpr], ui)
        elif u.kind == "embed":
            op = g.ops[u.ops[0]]
            gates = op_gates[op.id]
            Qt, D, a, dd = d["rows"], d["cols"], d["a"], d["d"]
            assert len(gates) == Qt * D
            for qlo, qhi in _blocks(Qt, a):
                for dlo, dhi in _blocks(D, dd):
                    place([gates[q * D + c] for q in range(qlo, qhi) for c in range(dlo, dhi)], ui)
        elif u.kind == "tile":
            if d["mode"] != "chain" or any(d["gens"]):
                raise Unmaterializable(f"tile mode {d['mode']} gens {d['gens']}")
            ops = [g.ops[i] for i in u.ops]
            role = d["shared_role"]
            Rs, segR, Kd, copies = d["Rs"], list(d["segR"]), d["K"], d["copies"]
            a, k, nk, bs = d["a"], d["k"], d["nk"], list(d["bs"])
            steps = d.get("steps", ())
            shapes = []
            for o in ops:
                M, N = int(o.statics["M"]), int(o.statics["N"])
                gates = op_gates[o.id]
                assert len(gates) == M * N * (Kd + 2) * copies, (o.id, len(gates), M, N, Kd, copies)
                shapes.append((M, N))
            # fused steps
            fused: list[tuple] = []
            for st in steps:
                if st[0] == "side":
                    _, oid, seg = st
                    p2 = g.ops[oid]
                    M2, N2, K2 = int(p2.statics["M"]), int(p2.statics["N"]), int(p2.statics["K"])
                    assert len(op_gates[oid]) == M2 * N2 * (K2 + 2) * copies
                    fused.append(("side", oid, seg, M2, N2, K2))
                else:
                    _, oid, seg, rf = st
                    c = g.ops[oid]
                    rows_key = {"colsum": "K"}.get(c.kind, "Q" if "Q" in c.statics else "N")
                    rows = int(c.statics[rows_key]) * c.copies
                    P = Rs * segR[seg] * copies
                    assert P % rows == 0
                    fused.append(("ew", oid, seg, rows, P // rows, rf))
            kslabs = _blocks(Kd, k)
            assert len(kslabs) == nk
            for cp in range(copies):
                for slo, shi in _blocks(Rs, a):
                    for j in range(d["c"]):
                        for li, (klo, khi) in enumerate(kslabs):
                            gs: list[int] = []
                            pos_by_seg: list[list[tuple[int, int]]] = []
                            for i, o in enumerate(ops):
                                M, N = shapes[i]
                                base = cp * M * N * (Kd + 2)
                                gates = op_gates[o.id]
                                blo, bhi = j * bs[i], min((j + 1) * bs[i], segR[i])
                                pos: list[tuple[int, int]] = []
                                if blo >= bhi:
                                    pos_by_seg.append(pos)
                                    continue
                                if role == "A":
                                    mn = [(m, n) for m in range(slo, shi) for n in range(blo, bhi)]
                                else:
                                    mn = [(m, n) for n in range(slo, shi) for m in range(blo, bhi)]
                                for m, n in mn:
                                    pos.append((m, n))
                                    if li == 0:
                                        gs.append(gates[base + _mm_gate(N, Kd, m, n, 0)])
                                    gs.extend(gates[base + _mm_gate(N, Kd, m, n, 1 + kk)] for kk in range(klo, khi))
                                    if li == nk - 1:
                                        gs.append(gates[base + _mm_gate(N, Kd, m, n, Kd + 1)])
                                pos_by_seg.append(pos)
                            for fs in fused:
                                if fs[0] == "side":
                                    _, oid, seg, M2, N2, K2 = fs
                                    base2 = cp * M2 * N2 * (K2 + 2)
                                    gates2 = op_gates[oid]
                                    for m, n in pos_by_seg[seg]:
                                        gs.extend(gates2[base2 + _mm_gate(N2, K2, m, n, jj)] for jj in range(K2 + 2))
                                else:
                                    _, oid, seg, rows, L, rf = fs
                                    # positions of the segment's output in row-major (m, n) leaf order
                                    N_seg = shapes[seg][1]
                                    pp = []
                                    for m, n in pos_by_seg[seg]:
                                        leaf = cp * shapes[seg][0] * N_seg + m * N_seg + n
                                        pp.append(divmod(leaf, L))
                                    gs.extend(_fused_gates(g, op_gates[oid], oid, rows, L, pp, rf))
                            place(gs, ui)
        elif u.kind == "attn-fwd":
            sc, sm, pv = (g.ops[i] for i in u.ops)
            if any(d["gens"]):
                raise Unmaterializable("attention unit with generation")
            S, DH = d["S"], d["DH"]
            Nsc = int(sc.statics["N"])
            Npv, Kpv = int(pv.statics["N"]), int(pv.statics["K"])
            gsc, gsm, gpv = op_gates[sc.id], op_gates[sm.id], op_gates[pv.id]
            gpr_sm = len(gsm) // (S * sc.copies)
            for cp in range(sc.copies):
                for lo, hi in _blocks(S, d["a"]):
                    gs = []
                    for m in range(lo, hi):
                        b0 = cp * S * Nsc * (DH + 2)
                        gs.extend(gsc[b0 + m * Nsc * (DH + 2): b0 + (m + 1) * Nsc * (DH + 2)])
                        r0 = (cp * S + m) * gpr_sm
                        gs.extend(gsm[r0:r0 + gpr_sm])
                        p0 = cp * S * Npv * (Kpv + 2)
                        gs.extend(gpv[p0 + m * Npv * (Kpv + 2): p0 + (m + 1) * Npv * (Kpv + 2)])
                    place(gs, ui)
        else:
            raise Unmaterializable(f"unit kind {u.kind}")
    missing = [x for x in flat.gates if x not in assign]
    assert not missing, f"{len(missing)} gates not covered by the plan: {missing[:10]}"
    return assign, ru_of


# ---------------------------------------------------------------------------------------------------------
# record
# ---------------------------------------------------------------------------------------------------------

@dataclass
class Record:
    family: str
    name: str
    F: int
    X: int
    gates: int
    G: Optional[int] = None             # per-RU total-work cap (None = unbounded = the (F, X) policy)
    work: int = 0                       # total work of the circuit (G >= work is non-binding)
    snippet: str = ""
    L: Optional[int] = None
    L_G: Optional[int] = None           # the G actually passed to ``lower_bound`` (None -> row is "L@G=None")
    L_noprog: Optional[int] = None      # contract-only call ``lower_bound(g, F, X)`` (no program attached)
    L_source: Optional[int] = None
    L_cap: Optional[int] = None
    L_infeasible: bool = False
    L_error: str = ""
    L_notes: list[str] = field(default_factory=list)
    L_worst_ru: dict = field(default_factory=dict)
    Istar: Optional[int] = None
    Istar_optimal: bool = False
    Istar_method: str = ""
    Istar_infeasible: bool = False
    Istar_timeout: bool = False
    Istar_error: str = ""
    Istar_seconds: float = 0.0
    Istar_units: int = 0
    Istar_partition: list[dict] = field(default_factory=list)   # the optimal partition (the "attack"), per RU
    U: Optional[int] = None
    U_error: str = ""
    U_units: int = 0
    Ulit: Optional[int] = None
    Ulit_error: str = ""
    Ulit_units: int = 0
    Ulit_kinds: list[str] = field(default_factory=list)
    Ulit_materialized: bool = False
    Ulit_unmat_reason: str = ""
    Ulit_legal: Optional[bool] = None
    Ulit_legal_why: str = ""
    Ulit_cost: Optional[int] = None
    Ulit_ru_over: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    hand: Optional[int] = None          # torture suite: hand-derived value or bound
    hand_kind: str = ""                 # "eq" | "le" | "ge"
    hand_ok: Optional[bool] = None
    seconds: float = 0.0
    versions: dict = field(default_factory=lambda: dict(VERSIONS))

    def to_json(self) -> dict:
        return asdict(self)

    @property
    def clean(self) -> bool:
        return not self.violations


def _accepts(fn, param: str) -> bool:
    import inspect
    try:
        return param in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False


def _accepts_program(fn) -> bool:
    return _accepts(fn, "program")


def _ratio(a: Optional[int], b: Optional[int]) -> Optional[float]:
    if a is None or b is None or b == 0:
        return None
    return a / b


def _value_name(flat: FlatCircuit, g: OpGraph, gate_op: dict[int, int], v: int) -> str:
    if flat.is_input[v]:
        return f"{flat.input_param[v]}[{flat.input_role[v]}]"
    o = gate_op.get(v)
    if o is None:
        return f"gate{v}"
    op = g.ops[o]
    return f"op{o}:{op.kind}.out"


def describe_partition(flat: FlatCircuit, g: OpGraph, op_gates: dict[int, list[int]], assignment: dict[int, int]) -> list[dict]:
    """Human-readable optimal partition: per RU its ops (gate counts), work, and imports grouped by value."""
    gate_op = {x: o for o, gs in op_gates.items() for x in gs}
    imps = ru_imports(flat, assignment)
    out = []
    for r in sorted(set(assignment.values())):
        gates = [x for x in flat.gates if assignment[x] == r]
        ops: dict[str, int] = {}
        for x in gates:
            o = gate_op.get(x)
            key = f"op{o}:{g.ops[o].kind}" if o is not None else "?"
            ops[key] = ops.get(key, 0) + 1
        by: dict[str, int] = {}
        for v in imps.get(r, ()):
            nm = _value_name(flat, g, gate_op, v)
            by[nm] = by.get(nm, 0) + flat.bytes_of(v)
        out.append({"ru": r, "gates": len(gates), "work": sum(flat.work[x] for x in gates),
                    "ops": ops, "in_bytes": sum(by.values()), "imports": dict(sorted(by.items()))})
    return out


def evaluate(bp: BuiltProgram, F: int, X: int, G: Optional[int] = None, *, family: str = "", name: str = "",
             snippet: str = "", time_limit: float = 10.0, exact: bool = True, exact_limit: int = 200,
             g: OpGraph | None = None, flat: FlatCircuit | None = None, op_gates: dict[int, list[int]] | None = None,
             lower_fn=lower_bound, upper_fn=upper_bound, keep_partition: bool = True) -> Record:
    """Evaluate ``(bp, F, G, X)``.  ``G=None`` = unbounded.  ``lower_bound`` receives ``G`` only when its
    signature accepts it; otherwise ``L`` is computed at ``G=None`` (a valid, looser bound for any ``G``) and
    ``Record.L_G`` stays ``None`` so the row can be marked ``L@G=None``."""
    t0 = time.perf_counter()
    F, X = int(F), int(X)
    G = None if G is None else int(G)
    flat = flat if flat is not None else flatten(bp)
    g = g if g is not None else extract(bp)
    rec = Record(family=family, name=name or bp.algorithm, F=F, X=X, G=G, work=flat.total_work(), gates=flat.n_gates,
                 snippet=snippet)

    # -- lower bound -----------------------------------------------------------------------------------------
    # The §5 contract is ``lower_bound(g, F, X, G=)``; the §2.2 implementation additionally takes ``program=``
    # (it certifies in-order row views so credits flow).  ``L`` is the strong (program-attached) value when the
    # function accepts it, ``L_noprog`` the contract-only value; both must be ``<= I*``.
    try:
        lkw = {}
        if G is not None and _accepts(lower_fn, "G"):
            lkw["G"] = G
            rec.L_G = G
        if _accepts_program(lower_fn):
            lb = lower_fn(g, F, X, program=bp.program, **lkw)
            try:
                rec.L_noprog = int(lower_fn(g, F, X, **lkw).total)
            except Exception as e:  # noqa: BLE001
                rec.L_error = f"(no-program call) {type(e).__name__}: {e}"
        else:
            lb = lower_fn(g, F, X, **lkw)
        rec.L = int(lb.total)
        rec.L_source = int(getattr(lb, "source", 0) or 0)
        rec.L_cap = int(getattr(lb, "cap", 0) or 0)
        rec.L_infeasible = bool(getattr(lb, "infeasible", False)) or rec.L >= INF_SENTINEL
        rec.L_notes = [str(n) for n in getattr(lb, "notes", ())][:6]
        wr = getattr(lb, "worst_ru", None)
        if isinstance(wr, dict):
            rec.L_worst_ru = {k: (v if isinstance(v, (int, float, str, bool, type(None))) else str(v)) for k, v in wr.items()}
    except Exception as e:  # noqa: BLE001
        rec.L_error = f"{type(e).__name__}: {e}"

    # -- upper bounds ----------------------------------------------------------------------------------------
    ukw = {"G": G} if (G is not None and _accepts(upper_fn, "G")) else {}
    try:
        ub = upper_fn(g, F, X, program=bp.program, **ukw)
        rec.U = int(ub.total)
        rec.U_units = int(ub.n_units)
    except Exception as e:  # noqa: BLE001
        rec.U_error = f"{type(e).__name__}: {e}"
    ubl = None
    try:
        ubl = upper_fn(g, F, X, program=bp.program, recompute=False, **ukw)
        rec.Ulit = int(ubl.total)
        rec.Ulit_units = int(ubl.n_units)
        rec.Ulit_kinds = sorted({u.kind for u in ubl.plan.units})
    except Exception as e:  # noqa: BLE001
        rec.Ulit_error = f"{type(e).__name__}: {e}"

    # -- materialise the literal plan ------------------------------------------------------------------------
    if op_gates is None:
        op_gates = op_gate_lists(bp, g, flat)
    if ubl is not None:
        try:
            assign, ru_of = materialize(ubl.plan, g, flat, op_gates)
            rec.Ulit_materialized = True
            ok, why = is_legal(flat, assign, F, X, G)
            rec.Ulit_legal, rec.Ulit_legal_why = bool(ok), ("" if ok else why)
            rec.Ulit_cost = int(partition_cost(flat, assign))
            imps = ru_imports(flat, assign)
            for r, ui in ru_of:
                b = sum(flat.bytes_of(v) for v in imps.get(r, ()))
                if b > ubl.plan.units[ui].imports_max:
                    rec.Ulit_ru_over.append(f"RU{r} (unit {ui} {ubl.plan.units[ui].kind}) imports {b} > declared {ubl.plan.units[ui].imports_max}")
            if not ok:
                rec.violations.append("Ulit_illegal")
            if rec.Ulit_cost > rec.Ulit:
                rec.violations.append("Ulit_cost_under")
            if rec.Ulit_ru_over:
                rec.violations.append("Ulit_ru_over")
        except Unmaterializable as e:
            rec.Ulit_unmat_reason = str(e)
        except AssertionError as e:
            rec.Ulit_unmat_reason = "materializer assertion: " + str(e)
            rec.violations.append("Ulit_materialize_assert")
        except Exception as e:  # noqa: BLE001
            rec.Ulit_unmat_reason = f"materializer error {type(e).__name__}: {e}\n" + traceback.format_exc(limit=3)
            rec.violations.append("Ulit_materialize_error")

    # -- exact -----------------------------------------------------------------------------------------------
    if exact and flat.n_gates <= exact_limit:
        t1 = time.perf_counter()
        try:
            r = with_timeout(time_limit, exact_min_input, flat, F, X, G, limit=exact_limit, method="auto",
                             time_limit=max(1.0, time_limit * 0.8))
            rec.Istar = int(r.total)
            rec.Istar_optimal = bool(r.optimal)
            rec.Istar_method = r.method
            rec.Istar_units = int(r.n_units)
            if keep_partition:
                rec.Istar_partition = describe_partition(flat, g, op_gates, r.assignment)
        except Infeasible:
            rec.Istar_infeasible = True
        except SolverTimeout:
            rec.Istar_timeout = True
        except Exception as e:  # noqa: BLE001
            rec.Istar_error = f"{type(e).__name__}: {e}"
        rec.Istar_seconds = time.perf_counter() - t1

    # -- verdicts --------------------------------------------------------------------------------------------
    if rec.L is not None and rec.Istar is not None:
        if rec.L_infeasible:
            rec.violations.append("L_infeasible_but_Istar")
        elif rec.L > rec.Istar:
            rec.violations.append("L_gt_Istar" if rec.Istar_optimal else "L_gt_found")
    if rec.L_noprog is not None and rec.Istar is not None and rec.L_noprog < INF_SENTINEL and rec.L_noprog > rec.Istar:
        rec.violations.append("Lnoprog_gt_Istar" if rec.Istar_optimal else "Lnoprog_gt_found")
    if rec.Ulit is not None and rec.Istar is not None and rec.Istar_optimal and rec.Ulit < rec.Istar:
        rec.violations.append("Ulit_lt_Istar")
    if rec.L is not None and not rec.L_infeasible:
        if rec.U is not None and rec.U < rec.L:
            rec.violations.append("Urec_lt_L")
        if rec.Ulit is not None and rec.Ulit < rec.L:
            rec.violations.append("Ulit_lt_L")
    if rec.Istar is not None and (rec.U_error or rec.Ulit_error):
        rec.violations.append("U_unavailable")
    if rec.Istar_infeasible and (rec.U is not None or rec.Ulit is not None):
        rec.violations.append("U_but_infeasible")
    if rec.L_error and not rec.Istar_infeasible:
        # (a raise on a policy with no legal partition at all, e.g. G below a single gate's work, is consistent)
        rec.violations.append("L_error")
    rec.seconds = time.perf_counter() - t0
    return rec


def _gkey(G: Optional[int]) -> float:
    return math.inf if G is None else G


def monotonicity_violations(recs: list[Record]) -> list[str]:
    """``L``, ``U``, ``U_lit``, ``I*`` must be non-increasing in ``X`` (fixed ``F, G``), in ``F`` (fixed ``X, G``)
    and in ``G`` (fixed ``F, X``; ``G=None`` is the largest ``G``)."""
    out: list[str] = []
    by_FG: dict[tuple, list[Record]] = {}
    by_XG: dict[tuple, list[Record]] = {}
    by_FX: dict[tuple, list[Record]] = {}
    for r in recs:
        by_FG.setdefault((r.F, r.G), []).append(r)
        by_XG.setdefault((r.X, r.G), []).append(r)
        by_FX.setdefault((r.F, r.X), []).append(r)

    def check(seq: list[Record], axis: str) -> None:
        for q in ("L", "U", "Ulit", "Istar"):
            prev = None
            for r in seq:
                v = getattr(r, q)
                if v is None or (q == "L" and r.L_infeasible) or (q == "Istar" and not r.Istar_optimal):
                    continue
                if prev is not None and v > prev[0]:
                    p = prev[1]
                    out.append(f"{q} not monotone in {axis}: {q}={prev[0]} at (F={p.F},G={p.G},X={p.X}) < {v} at (F={r.F},G={r.G},X={r.X})")
                prev = (v, r)

    for seq in by_FG.values():
        check(sorted(seq, key=lambda r: r.X), "X")
    for seq in by_XG.values():
        check(sorted(seq, key=lambda r: r.F), "F")
    for seq in by_FX.values():
        check(sorted(seq, key=lambda r: _gkey(r.G)), "G")
    return out


__all__ = ["Record", "evaluate", "materialize", "op_gate_lists", "monotonicity_violations", "with_timeout",
           "SolverTimeout", "Unmaterializable", "BIG"]
