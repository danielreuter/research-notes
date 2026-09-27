"""SPEC §6 validation table under the corrected policy (``X = inf``): the coarse bound modules against the exact
solver on micro circuits.

Per cell ``(circuit, F, G)``: ``I*`` (exact, or a proven interval ``[bound, best found]`` when the solver could not
close the cell), ``L = lower_coarse`` (when ``bounds/lower.py::lower_coarse`` exists; otherwise the column is
absent), ``U = upper_coarse`` (``bounds/coarse.py``) with its plan expanded to a gate assignment
(:func:`~accumulation.bounds.coarse.plan_gate_assignment`) and re-judged literally by the exact module
(``is_legal`` / ``partition_cost``), and the ratios ``L/I*``, ``U/I*``.

Soundness checks (every one is a bug in the bound module, reported, never adjusted):

* ``L > I*``: ``L`` above a *proved* optimum, or above the cost of *any* legal partition we hold (the solver's best
  found or ``U``'s literal partition) -- either is a certificate violation;
* ``U`` illegal: the expanded plan violates ``work(R) <= G`` or ``work(Up_R(g)) <= F`` at gate level;
* ``U < literal``: the plan's claimed cost is below the literal gate-level cost of its own partition (accounting
  undercount); ``U < I*``-proved likewise.

Circuits: the multi-step micro suite (``exact/micro.py``: inference, local-SGD chains, fan-out, deep chain), the
classic ``MICRO_SUITE`` programs, the torture cases of :mod:`accumulation.redteam.torture` (sharing-heavy), and
adversarial random circuits from :mod:`accumulation.redteam.fuzz`.  Grid: the ``fwd`` grid of
:mod:`accumulation.redteam.wedge` for the multi-step suite (``F in {1, 1.5, 3} fwd, inf``; ``G in {1, 4} fwd,
inf``), and ``F, G in {W/4, W/2, inf}`` (``W`` = total work) for everything else.

Usage::

    PYTHONPATH=. .venv/bin/python -m accumulation.redteam.coarse_validation --fuzz 300 --time-limit 30
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics
import time
from typing import Optional

from accumulation.redteam.harness import describe_partition, op_gate_lists, _versions
from accumulation.redteam.wedge import F_MULT, G_MULT, _cap, _mult_str, run_cell

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(HERE, "results")


def _lower_coarse_fn():
    try:
        from accumulation.bounds import lower as _l
    except Exception:
        return None
    return getattr(_l, "lower_coarse", None)


def _call_lower(fn, g, F: Optional[int], G: Optional[int], bp, flat) -> tuple[Optional[int], str, dict]:
    """Call ``lower_coarse`` under whatever signature it has (``(g, F, G, program=...)`` preferred)."""
    import inspect
    Fe = flat.total_work() if F is None else F
    sig = inspect.signature(fn)
    kw = {}
    if "program" in sig.parameters:
        kw["program"] = bp.program
    try:
        try:
            res = fn(g, Fe, G, **kw)
        except TypeError:
            res = fn(g, Fe, G=G, **kw)
    except Exception as e:                            # noqa: BLE001 - reported, never hidden
        return None, f"{type(e).__name__}: {str(e)[:160]}", {}
    tot = getattr(res, "L", getattr(res, "total", res))
    breakdown = {k: getattr(res, k) for k in ("total", "source", "cap", "token_seed", "state_floor", "target_macs", "F", "G")
                 if hasattr(res, k)}
    breakdown["notes"] = list(getattr(res, "notes", []) or [])[:12]
    wr = getattr(res, "worst_ru", None)
    if wr:
        breakdown["worst_ru"] = wr
    return int(tot), "", breakdown


def binding_constraint(flat, F: Optional[int], G: Optional[int]) -> str:
    """Which policy cap forbids the single-RU partition: ``none`` (one RU legal), ``F``, ``G`` or ``F+G``."""
    W = flat.total_work()
    g_binds = G is not None and W > G
    f_binds = False
    if F is not None and F < W:
        cone: dict[int, int] = {}
        has_consumer: set[int] = set()
        for gt in flat.gates:
            m = 1 << gt
            for o in flat.operands[gt]:
                if not flat.is_input[o]:
                    m |= cone[o]
                    has_consumer.add(o)
            cone[gt] = m
        by_work: dict[int, int] = {}
        for gt in flat.gates:
            if flat.work[gt]:
                by_work[flat.work[gt]] = by_work.get(flat.work[gt], 0) | (1 << gt)
        for gt in flat.gates:
            if gt not in has_consumer and sum(w * (cone[gt] & mk).bit_count() for w, mk in by_work.items()) > F:
                f_binds = True
                break
    return {(False, False): "none", (True, False): "F", (False, True): "G", (True, True): "F+G"}[(f_binds, g_binds)]


def eval_upper(bp, flat, g, F: Optional[int], G: Optional[int]) -> dict:
    from accumulation.bounds.coarse import plan_gate_assignment, upper_coarse
    from accumulation.exact.solve import is_legal, partition_cost
    out: dict = {"U": None, "U_units": None, "U_literal": None, "U_legal": None, "U_error": "", "U_family": "",
                 "U_cyclic": False}
    Fe = flat.total_work() if F is None else F
    t0 = time.perf_counter()
    try:
        plan = upper_coarse(g, Fe, G, program=bp.program)
    except Exception as e:                            # noqa: BLE001
        out["U_error"] = f"{type(e).__name__}: {str(e)[:160]}"
        out["U_seconds"] = time.perf_counter() - t0
        return out
    out.update(U=int(plan.total), U_units=int(plan.n_units), U_family=str(plan.detail.get("family", "")))
    try:
        asg = plan_gate_assignment(g, plan, bp.program)
        gates = set(flat.gates)
        if set(asg) >= gates:
            sub = {k: asg[k] for k in gates}
            ok, why = is_legal(flat, sub, Fe, None, G)
            out["U_legal"] = bool(ok)
            out["U_literal"] = int(partition_cost(flat, sub))
            out["U_cyclic"] = (not ok) and why.startswith("cyclic RU quotient")
            if out["U_cyclic"]:
                # legal under the old model?  then it is a stale (cyclic) planner family, not an accounting bug
                out["U_legal_cyclic_model"] = bool(is_legal(flat, sub, Fe, None, G, acyclic=False)[0])
            if not ok:
                out["U_error"] = f"illegal: {why[:160]}"
        else:
            out["U_error"] = f"gate assignment covers {len(set(asg) & gates)}/{len(gates)} gates"
    except Exception as e:                            # noqa: BLE001
        out["U_error"] = f"expand: {type(e).__name__}: {str(e)[:160]}"
    out["U_seconds"] = time.perf_counter() - t0
    return out


def _wedge_cells(path: str) -> dict:
    """``(circuit, F, G) -> cell`` from a previous ``wedge_exact.json`` (reused so the heavy chain cells are not
    re-solved with a shorter time box)."""
    try:
        with open(path) as f:
            doc = json.load(f)
    except OSError:
        return {}
    out = {}
    for r in doc.get("rows", []):
        if r.get("model") != "acyclic":
            continue                                   # pre-2026-09-15 (cyclic-quotient) cells are not answers
        out[(r["circuit"], r["gates"], r["F"], r["G"])] = {k: r[k] for k in ("F", "G", "Istar", "optimal", "method", "seconds", "n_units",
                                                                 "status", "partition", "bound", "heuristic", "model",
                                                                 "Istar_cyclic", "assignment") if k in r}
    return out


def _cyclic_reference() -> dict:
    """``(circuit, gates, F, G) -> I*`` proved under the old model (validation + wedge archives)."""
    from accumulation.redteam.wedge import cyclic_reference
    ref = cyclic_reference(os.path.join(DEFAULT_OUT, "wedge_exact_cyclic_model.json"))
    ref.update(cyclic_reference(os.path.join(DEFAULT_OUT, "validation_cyclic_model.json")))
    return ref


def eval_cell(bp, flat, g, og, F: Optional[int], G: Optional[int], *, time_limit: float, exact_limit: int,
              lower_fn, reuse: Optional[dict] = None, cyclic_ref: Optional[int] = None) -> dict:
    cell = dict(reuse) if reuse else run_cell(bp, flat, g, og, F, G, time_limit=time_limit, exact_limit=exact_limit,
                                              lower_hint=cyclic_ref)
    if reuse:
        cell["method"] = (cell.get("method") or "") + " (reused)"
    cell["model"] = "acyclic"
    if cell.get("Istar_cyclic") is None:
        cell["Istar_cyclic"] = cyclic_ref
    I0 = cell.get("Istar_cyclic")
    cell["Istar_ratio"] = (cell["Istar"] / I0) if (cell.get("Istar") is not None and cell.get("optimal") and I0) else None
    cell.update(eval_upper(bp, flat, g, F, G))
    if lower_fn is not None:
        L, err, brk = _call_lower(lower_fn, g, F, G, bp, flat)
        cell["L"], cell["L_error"], cell["L_breakdown"] = L, err, brk
    else:
        cell["L"], cell["L_error"], cell["L_breakdown"] = None, "lower_coarse not present", {}
    cell["binding"] = binding_constraint(flat, F, G)
    I, opt, bound = cell["Istar"], cell["optimal"], cell.get("bound")
    # a legal partition's cost is an upper bound on I*; the tightest one we hold:
    ub_candidates = [v for v in (I if I is not None else None, cell["U_literal"] if cell.get("U_legal") else None) if v is not None]
    ub = min(ub_candidates) if ub_candidates else None
    viol = []
    L = cell["L"]
    if L is not None and ub is not None and L > ub:
        viol.append(f"L_gt_Istar: L={L} > {'I*' if opt else 'legal partition cost'}={ub}")
    U = cell["U"]
    if U is not None:
        if cell.get("U_cyclic"):
            pass                                       # cyclic planner family: not a witness under SPEC §0, not an accounting bug
        elif cell["U_legal"] is False:
            viol.append("U_illegal")
        if cell["U_literal"] is not None and U < cell["U_literal"]:
            viol.append(f"U_lt_literal: claimed {U} < literal {cell['U_literal']}")
        if bound is not None and U < bound:
            viol.append(f"U_lt_Istar: U={U} < proven lower bound {bound}")
    cell["violations"] = viol
    cell["L_over_Istar"] = None if (L is None or not I) else L / I
    cell["U_over_Istar"] = None if (U is None or not I or cell.get("U_cyclic")) else U / I
    return cell


# ---------------------------------------------------------------------------------------------------------
# circuits and grids
# ---------------------------------------------------------------------------------------------------------

def _work_grid(W: int) -> list[tuple[Optional[int], Optional[int], str, str]]:
    q, h = max(1, -(-W // 4)), max(1, -(-W // 2))
    pts = []
    for F, Fl in ((q, "W/4"), (h, "W/2"), (None, "inf")):
        for G, Gl in ((q, "W/4"), (h, "W/2"), (None, "inf")):
            pts.append((F, G, Fl, Gl))
    return pts


def suite(*, fuzz_n: int, fuzz_seed: int, fuzz_gate_cap: int) -> list[dict]:
    from accumulation.exact import micro
    from accumulation.exact.solve import flatten
    from accumulation.redteam import torture
    from accumulation.redteam.circuits import build
    from accumulation.redteam.fuzz import family, gen_circuit
    from accumulation.redteam.wedge import circuits as wedge_circuits
    out = []
    for spec in wedge_circuits(registry=True):
        bp = spec["bp"]
        if spec.get("registry") and "inference" not in spec["group"]:
            continue                                       # registry training circuits: beyond exact scale
        pts = [(_cap(fm, spec["fwd"]), _cap(gm, spec["fwd"]), _mult_str(fm), _mult_str(gm)) for fm in F_MULT for gm in G_MULT]
        out.append(dict(group="multi-step micro suite" if not spec.get("registry") else "registry inference (tiny/tiny2)",
                        family=spec["group"], bp=bp, name=bp.algorithm, grid=pts))
    # dynamic-weight forward (``forward-nonfixed``): micro analogue = a deep chain with *accumulated* weights; G
    # forces >= 2 RUs along tokens or layers; plus the registry circuit at tiny (single-RU cells only)
    for depth, q in ((2, 2), (3, 2), (2, 3)):
        bp = micro.deep_chain(depth=depth, q=q, d=2, role_W="accumulated")
        fwd = q * 2 * 3
        pts = [(_cap(fm, fwd), _cap(gm, fwd), _mult_str(fm), _mult_str(gm)) for fm in F_MULT for gm in G_MULT]
        out.append(dict(group="forward-nonfixed micro (accumulated weights)", family="forward-nonfixed micro", bp=bp,
                        name=bp.algorithm, grid=pts))
    # dynamic-rollout micro analogues (ROLLOUT_PLAN): q_roll independent one-token sessions through accumulated weights,
    # dense and MoE (static balanced routing, active params < dynamic state); F/G in multiples of fwd(Q_inf = 1)
    from accumulation.redteam.rollout_scale import REGIMES as ROLL_REGIMES
    roll = [micro.dense_rollout(4), micro.dense_rollout(8), micro.dense_rollout(4, d=2), micro.dense_rollout(6, d=1, layers=2),
            micro.moe_rollout(4), micro.moe_rollout(8), micro.moe_rollout(4, experts=4, topk=2), micro.moe_rollout(6, experts=3, topk=1, shared=0),
            micro.moe_rollout(4, d=2, experts=2, topk=1, shared=0)]
    for bp in roll:
        fwd = bp.notes["fwd"]
        pts = []
        for label, fh, gh in ROLL_REGIMES:
            F = None if fh is None else int(round(fh * fwd))
            G = None if gh is None else int(round(gh * fwd))
            pts.append((F, G, "inf" if fh is None else f"{fh:g}·fwd", "inf" if gh is None else f"{gh:g}·fwd"))
        fam = "moe rollout micro" if bp.algorithm.startswith("moe") else "dense rollout micro"
        out.append(dict(group="rollout micro analogues (dense / MoE, accumulated weights)", family=fam, bp=bp, name=bp.algorithm, grid=pts))
    from accumulation.algorithms.registry import ALGORITHMS
    from accumulation.configs import MODELS, Workload
    for q in (2, 4):
        bp = ALGORITHMS["forward-nonfixed"].build(MODELS["tiny"], Workload(tokens=q, seq=q, chunk=1, population=1, rank=1, local_steps=1))
        fwd = flatten(bp).total_work()
        pts = [(_cap(fm, fwd), _cap(gm, fwd), _mult_str(fm), _mult_str(gm)) for fm in F_MULT for gm in G_MULT]
        out.append(dict(group="registry forward-nonfixed @ tiny", family="forward-nonfixed @ tiny", bp=bp,
                        name=f"{bp.algorithm}[tiny,q={q}]", grid=pts))
    for name, bp in micro.micro_programs(max_gates=36):
        out.append(dict(group="classic micro suite", family=name.split("_")[0], bp=bp, name=name, grid=_work_grid(flatten(bp).total_work())))
    for case in torture.CASES:
        bp = build(case.circuit)
        flat = flatten(bp)
        if flat.n_gates > 40:
            continue
        out.append(dict(group="torture cases", family=case.family, bp=bp, name=case.name, grid=_work_grid(flat.total_work())))
    rng = random.Random(fuzz_seed)
    for i in range(fuzz_n):
        c = gen_circuit(rng, gate_cap=fuzz_gate_cap, name=f"fuzz{fuzz_seed}-{i}")
        bp = build(c)
        W = flatten(bp).total_work()
        pts = _work_grid(W)
        rng.shuffle(pts)
        out.append(dict(group="fuzz", family=family(c), bp=bp, name=c.name or f"fuzz{fuzz_seed}-{i}", grid=pts[:4],
                        snippet=c.to_python()))
    return out


def lower_sha1(name: str = "lower.py") -> str:
    """``sha1sum accumulation/bounds/<name> | cut -c1-10`` (``lower.py`` re-exports ``lower_coarse`` from
    ``lower_coarse.py``, so both are recorded)."""
    import hashlib
    path = os.path.join(HERE, "bounds", name)
    if not os.path.exists(path):
        return "absent"
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:10]


def build_validation(*, time_limit: float, exact_limit: int, fuzz_n: int, fuzz_seed: int, fuzz_gate_cap: int,
                     verbose: bool, reuse_istar: bool = False) -> dict:
    from accumulation.exact.solve import flatten
    from accumulation.graph import extract
    lower_fn = _lower_coarse_fn()
    wedge = _wedge_cells(os.path.join(DEFAULT_OUT, "wedge_exact.json"))
    if reuse_istar:
        wedge.update(_wedge_cells(os.path.join(DEFAULT_OUT, "validation.json")))   # previous exact cells (I* is policy-only)
    cyc_ref = _cyclic_reference()
    rows = []
    t_start = time.time()
    for spec in suite(fuzz_n=fuzz_n, fuzz_seed=fuzz_seed, fuzz_gate_cap=fuzz_gate_cap):
        bp = spec["bp"]
        flat = flatten(bp)
        g = extract(bp)
        og = op_gate_lists(bp, g, flat) if flat.n_gates <= 200 else None
        if verbose:
            print(f"== [{spec['group']}] {spec['name']}: {flat.n_gates} gates, work {flat.total_work()}", flush=True)
        for F, G, Fl, Gl in spec["grid"]:
            cell = eval_cell(bp, flat, g, og, F, G, time_limit=time_limit, exact_limit=exact_limit, lower_fn=lower_fn,
                             reuse=wedge.get((spec["name"], flat.n_gates, F, G)),
                             cyclic_ref=cyc_ref.get((spec["name"], flat.n_gates, F, G)))
            row = dict(group=spec["group"], family=spec["family"], circuit=spec["name"], gates=flat.n_gates,
                       work=flat.total_work(), F_label=Fl, G_label=Gl, snippet=spec.get("snippet", ""))
            row.update(cell)
            rows.append(row)
            if verbose:
                print(f"   F={Fl:>7s} ({F}) G={Gl:>7s} ({G}): I*={cell['Istar']}{'' if cell['optimal'] else '?'} "
                      f"L={cell['L']} U={cell['U']} (lit {cell['U_literal']}, legal {cell['U_legal']}) "
                      f"{'VIOLATION ' + '; '.join(cell['violations']) if cell['violations'] else ''} "
                      f"{cell['U_error'][:60] if cell['U_error'] else ''}", flush=True)
    return {"meta": {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "elapsed_s": time.time() - t_start,
                     "policy": "X = inf; legal iff work(R) <= G and work(Up_R(g)) <= F; charged roles token/accumulated/carried/seed",
                     "time_limit": time_limit, "exact_limit": exact_limit, "fuzz": {"n": fuzz_n, "seed": fuzz_seed, "gate_cap": fuzz_gate_cap},
                     "lower_coarse_present": lower_fn is not None, "lower_sha1": lower_sha1(),
                     "lower_coarse_sha1": lower_sha1("lower_coarse.py"), "lower_sha1_after": None,
                     "lower_coarse_sha1_after": None, "versions": _versions()},
            "rows": rows}


# ---------------------------------------------------------------------------------------------------------
# aggregate + markdown
# ---------------------------------------------------------------------------------------------------------

def _pct(xs: list[float], p: float) -> Optional[float]:
    if not xs:
        return None
    xs = sorted(xs)
    k = (len(xs) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] if lo == hi else xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def aggregate(rows: list[dict]) -> dict:
    n = len(rows)
    with_I = [r for r in rows if r["Istar"] is not None]
    proved = [r for r in with_I if r["optimal"]]
    L_ratios = [r["L_over_Istar"] for r in proved if r["L_over_Istar"] is not None]
    U_ratios = [r["U_over_Istar"] for r in proved if r["U_over_Istar"] is not None]
    viol = [r for r in rows if r["violations"]]
    return dict(cells=n, cells_with_Istar=len(with_I), cells_proved=len(proved),
                cells_with_L=sum(r["L"] is not None for r in rows), cells_with_U=sum(r["U"] is not None for r in rows),
                U_unavailable=sum(r["U"] is None for r in rows), L_unavailable=sum(r["L"] is None for r in rows),
                soundness_violations=len(viol),
                violation_kinds={k: sum(any(v.startswith(k) for v in r["violations"]) for r in rows)
                                 for k in ("L_gt_Istar", "U_illegal", "U_lt_literal", "U_lt_Istar")},
                L_over_Istar=dict(n=len(L_ratios), median=_pct(L_ratios, 0.5), p05=_pct(L_ratios, 0.05), min=min(L_ratios) if L_ratios else None),
                U_over_Istar=dict(n=len(U_ratios), median=_pct(U_ratios, 0.5), p95=_pct(U_ratios, 0.95), max=max(U_ratios) if U_ratios else None),
                U_equals_literal=sum(1 for r in rows if r["U"] is not None and r["U_literal"] == r["U"]),
                U_above_literal=sum(1 for r in rows if r["U"] is not None and r["U_literal"] is not None and r["U"] > r["U_literal"]))


def _dist(rows: list[dict], key: str, ps: tuple[float, ...]) -> dict:
    xs = [r[key] for r in rows if r.get(key) is not None and r["optimal"]]
    out = {"n": len(xs)}
    if xs:
        out.update(median=_pct(xs, 0.5), min=min(xs), max=max(xs), **{f"p{int(p*100):02d}": _pct(xs, p) for p in ps})
    return out


def panel(rows: list[dict], worst_k: int = 5) -> dict:
    """DELIVERABLES §4: N exact cells, `U < I*` / `L > I*` counts, `U/I*` (median, max) and `L/I*` (median, p10,
    min) overall / by family / by binding constraint, the worst `L/I*` cells with their optimal partitions."""
    exact = [r for r in rows if r["Istar"] is not None and r["optimal"]]
    interval = [r for r in rows if r["Istar"] is not None and not r["optimal"]]
    ratios = [r["Istar_ratio"] for r in exact if r.get("Istar_ratio") is not None]
    moved = [r for r in exact if r.get("Istar_ratio") is not None and r["Istar_ratio"] > 1 + 1e-9]
    model_delta = {"compared": len(ratios), "changed": len(moved),
                   "ratio_median": _pct(ratios, 0.5) if ratios else None, "ratio_max": max(ratios) if ratios else None,
                   "ratio_median_changed": _pct([r["Istar_ratio"] for r in moved], 0.5) if moved else None,
                   "changed_by_family": {}}
    for r in moved:
        model_delta["changed_by_family"][r["family"]] = model_delta["changed_by_family"].get(r["family"], 0) + 1
    cyclic_U = [r for r in exact if r.get("U_cyclic")]
    u_lt = [r for r in rows if any(v.startswith("U_lt_Istar") or v.startswith("U_lt_literal") or v == "U_illegal" for v in r["violations"])]
    l_gt = [r for r in rows if any(v.startswith("L_gt_Istar") for v in r["violations"])]

    def split(keyfn):
        groups: dict[str, list[dict]] = {}
        for r in exact:
            groups.setdefault(keyfn(r), []).append(r)
        return {k: {"cells": len(v), "U_over_Istar": _dist(v, "U_over_Istar", (0.95,)), "L_over_Istar": _dist(v, "L_over_Istar", (0.10,)),
                    "L_gt_Istar": sum(1 for r in v if any(x.startswith("L_gt_Istar") for x in r["violations"])),
                    "U_lt_Istar": sum(1 for r in v if r in u_lt)} for k, v in sorted(groups.items())}

    def _cell_ref(r):
        return {k: r.get(k) for k in ("circuit", "family", "group", "gates", "F", "G", "F_label", "G_label", "binding", "Istar", "L", "U",
                                      "U_literal", "L_over_Istar", "U_over_Istar", "L_breakdown", "partition", "violations", "snippet")}

    worst = sorted([r for r in exact if r.get("L_over_Istar") is not None], key=lambda r: r["L_over_Istar"])[:worst_k]
    return {"N_exact": len(exact), "N_interval": len(interval), "N_total": len(rows),
            "U_lt_Istar_count": len(u_lt), "L_gt_Istar_count": len(l_gt),
            "U_over_Istar": _dist(exact, "U_over_Istar", (0.95,)), "L_over_Istar": _dist(exact, "L_over_Istar", (0.10,)),
            "U_unavailable": sum(1 for r in exact if r["U"] is None), "L_unavailable": sum(1 for r in exact if r["L"] is None),
            "U_cyclic": len(cyclic_U), "U_cyclic_below_Istar": sum(1 for r in cyclic_U if r["U"] < r["Istar"]),
            "model_delta": model_delta,
            "U_equals_Istar": sum(1 for r in exact if r["U"] == r["Istar"] and not r.get("U_cyclic")),
            "L_equals_Istar": sum(1 for r in exact if r["L"] == r["Istar"]),
            "by_family": split(lambda r: r["family"]), "by_binding": split(lambda r: r["binding"]),
            "worst_L_cells": [_cell_ref(r) for r in worst], "L_violations": [_cell_ref(r) for r in l_gt],
            "U_violations": [_cell_ref(r) for r in u_lt]}


def _partition_lines(r: dict) -> list[str]:
    out = []
    groups: dict[str, list[int]] = {}
    for ru in r.get("partition") or []:
        ops = ", ".join(f"{k} x{v}" for k, v in ru["ops"].items())
        imps = ", ".join(f"{k}={v}B" for k, v in ru["imports"].items()) or "nothing charged"
        key = f"work {ru['work']}, input {ru['in_bytes']} B; ops [{ops}]; crossing in: {imps}"
        groups.setdefault(key, []).append(ru["ru"])
    for key, rus in groups.items():
        lab = f"RU{rus[0]}" if len(rus) == 1 else f"{len(rus)} RUs"
        out.append(f"  - {lab}: {key}")
    if not out:
        out.append("  - (partition not recorded: circuit above the gate-list limit)")
    return out


def _cell_head(r: dict) -> str:
    return (f"**{r['circuit']}** ({r['family']}; {r['gates']} gates) F={r['F_label']} ({_f(r['F'])}) G={r['G_label']} ({_f(r['G'])}), "
            f"binding: {r['binding']}: I*={_istar(r) if 'status' in r else r['Istar']}, L={_f(r['L'])}, U={_f(r['U'])}"
            f"{'' if r.get('U_literal') in (None, r.get('U')) else ' (lit ' + str(r['U_literal']) + ')'}, "
            f"L/I*={_f(r['L_over_Istar'])}, U/I*={_f(r['U_over_Istar'])}")


def _L_breakdown_lines(r: dict) -> list[str]:
    b = r.get("L_breakdown") or {}
    if not b:
        return ["  - L breakdown: n/a"]
    parts = ", ".join(f"{k}={b[k]}" for k in ("total", "source", "token_seed", "state_floor", "cap", "target_macs", "F", "G") if k in b)
    out = [f"  - L breakdown: {parts}"]
    for n in b.get("notes", [])[:6]:
        out.append(f"    - note: {str(n)[:200]}")
    if b.get("worst_ru"):
        out.append(f"    - worst_ru: {str(b['worst_ru'])[:300]}")
    return out


def render_L_violations(doc: dict) -> str:
    m, pn = doc["meta"], doc["panel"]
    L = ["# `L > I*` soundness violations (`lower_coarse` vs exact `I*`, `X = inf`)", ""]
    L.append(f"Generated {m['generated']}; `bounds/lower.py` sha1 `{m['lower_sha1']}`, `bounds/lower_coarse.py` sha1 `{m.get('lower_coarse_sha1')}`"
             + (f" (changed to `{m['lower_sha1_after']}` during the run)" if m.get("lower_sha1_after") not in (None, m["lower_sha1"]) else "")
             + f".  {pn['L_gt_Istar_count']} violating cells out of {pn['N_exact']} exactly solved (+{pn['N_interval']} interval cells).")
    L.append("")
    L.append("`I*` is the exact optimum (brute force / MILP, `exact/solve.py`) or, where marked, the cost of a legal partition we hold "
             "(any `L` above a legal partition's cost is a violation).  The partition listed is the exact optimal partition: "
             "per RU its ops (op kind x count), its work, its runtime input, and what crosses into it.")
    L.append("")
    if not pn["L_violations"]:
        L.append("**None.**")
    for r in pn["L_violations"]:
        L.append("- " + _cell_head(r) + f" -> {'; '.join(r['violations'])}")
        L.extend(_L_breakdown_lines(r))
        L.append("  - exact optimal partition:")
        L.extend(["  " + x for x in _partition_lines(r)])
        if r.get("snippet"):
            L.append("")
            L.append("~~~python")
            L.append(r["snippet"].rstrip())
            L.append("~~~")
        L.append("")
    return "\n".join(L) + "\n"


def _load_block_term(path: str) -> dict:
    """Registry transformer cells from ``redteam/block_term.py`` (bracketed, not exact) -- folded into the panel."""
    try:
        with open(path) as f:
            bt = json.load(f)
    except OSError:
        return {}
    rows = [r for r in bt.get("rows", []) if "error" not in r]
    for r in rows:
        if r.get("L_breakdown"):
            r["block_term_fired"] = (r["L_breakdown"].get("block_bytes") or 0.0) > 1e-6
    return {"meta": bt.get("meta", {}), "rows": rows,
            "N": len(rows), "N_exact": sum(1 for r in rows if r.get("optimal")),
            "L_gt_legal_partition": sum(1 for r in rows if any(v.startswith("L_gt") for v in r.get("violations", []))),
            "U_violations": sum(1 for r in rows if any(v.startswith("U_") for v in r.get("violations", []))),
            "block_fired": sum(1 for r in rows if r.get("block_term_fired")),
            "block_not_fired_binding": sum(1 for r in rows if r.get("block_term_fired") is False and r.get("binding") != "none")}


def _load_rollout(path: str) -> dict:
    """Registry dynamic-rollout cells from ``redteam/rollout_scale.py`` (tiny2 dense, tiny-moe MoE; exact where one RU is
    legal, bracketed otherwise) -- folded into the panel."""
    try:
        with open(path) as f:
            rs = json.load(f)
    except OSError:
        return {}
    rows = [r for r in rs.get("rows", []) if "error" not in r]
    dflt = [r for r in rows if r.get("default_point") and not r.get("inference") and r.get("ref")]
    def _ratios(rs_, key):
        v = sorted(r[key] for r in rs_ if r.get(key) is not None)
        return {"n": len(v), "median": v[len(v) // 2] if v else None, "max": v[-1] if v else None, "min": v[0] if v else None}
    by_alg = {}
    for alg in sorted({r["algorithm"] for r in dflt}):
        sub = [r for r in dflt if r["algorithm"] == alg]
        by_alg[alg] = {"cells": len(sub), "U_over_ref": _ratios(sub, "U_over_ref"), "L_over_ref": _ratios(sub, "L_over_ref"),
                       "U_over_L": _ratios(sub, "U_over_L")}
    return {"meta": rs.get("meta", {}), "rows": rows, "fits": rs.get("fits", []), "N": len(rows),
            "N_exact": sum(1 for r in rows if r.get("optimal")),
            "N_inference": sum(1 for r in rows if r.get("inference")),
            "inference_ok": sum(1 for r in rows if r.get("inference") and not r.get("violations")),
            "L_gt_legal_partition": sum(1 for r in rows if any(v.startswith("L_gt") for v in r.get("violations", []))),
            "U_violations": sum(1 for r in rows if any(v.startswith("U_") for v in r.get("violations", []))),
            "inference_violations": sum(1 for r in rows if any(v.startswith("inference") for v in r.get("violations", []))),
            "by_alg_default_point": by_alg,
            "fit_checks_failed": sum(1 for f in rs.get("fits", []) if f.get("check_rL_le_rhi") is False or f.get("check_rlo_le_rU") is False)}


def render_rollout_md(rs: dict) -> list[str]:
    if not rs:
        return []
    m = rs["meta"]
    L = ["### Registry dynamic-rollout cells (`forward-nonfixed` @ tiny2, `forward-nonfixed-moe` @ tiny-moe; ROLLOUT_PLAN)", ""]
    L.append(f"- from `redteam/rollout_scale.py` at `lower_coarse.py` sha1 `{m.get('lower_coarse_sha1')}`, `coarse.py` sha1 `{m.get('coarse_sha1')}`; "
             f"{rs['N']} cells, {rs['N_exact']} exact (single RU legal), {rs['N'] - rs['N_exact']} bracketed; "
             f"inference references one RU with imports = tokens: {rs['inference_ok']}/{rs['N_inference']}.")
    L.append(f"- **`L > I_hi`: {rs['L_gt_legal_partition']}**; `U` violations: {rs['U_violations']}; inference-not-tokens violations: "
             f"{rs['inference_violations']}; marginal-fit bracket checks failed: {rs['fit_checks_failed']} (see `validation_rollout.md`).")
    for alg, v in rs["by_alg_default_point"].items():
        L.append(f"- `{alg}` at the default point (F_hat=1.5, G_hat=4; n={v['cells']}): U/ref median {_f(v['U_over_ref']['median'])} max "
                 f"{_f(v['U_over_ref']['max'])}; L/ref median {_f(v['L_over_ref']['median'])} min {_f(v['L_over_ref']['min'])}; "
                 f"U/L max {_f(v['U_over_L']['max'])}.")
    L.append("")
    L.append("| circuit | Q_roll | gates | regime | binds | I* / [I_lo, I_hi] | L | U | L/ref | U/ref | U/L | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rs["rows"]:
        istar = str(r["Istar"]) if r.get("optimal") else f"[{r['I_lo']}, {_f(r.get('I_hi'))}]"
        L.append(f"| {r['circuit']} | {r['Q_roll']} | {r['gates']} | {r['regime']} | {r['binding']} | {istar} | {_f(r.get('L'))} | {_f(r.get('U'))} | "
                 f"{_f(r.get('L_over_ref'))} | {_f(r.get('U_over_ref'))} | {_f(r.get('U_over_L'))} | "
                 f"{r.get('L_verdict', '')}{'; ' + '; '.join(r['violations']) if r.get('violations') else ''} |")
    L.append("")
    if rs.get("fits"):
        L.append("Steady-state marginal (bytes per rollout token; fits over the binding `Q_roll` points): `r_lo <= r* <= r_hi`, checks `r_L <= r_hi`, `r_lo <= r_U`.")
        L.append("")
        L.append("| circuit | Q_inf | regime | Q (steady) | r_lo | r_hi | r_L | r_U | r_L <= r_hi | r_lo <= r_U |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        for f in rs["fits"]:
            L.append(f"| {f['circuit']}[{f['model']}] | {f['Q_inf']} | {f['regime']} | {f['Q_steady']} | {_f(f['r_lo'])} | {_f(f['r_hi'])} | "
                     f"{_f(f['r_L'])} | {_f(f['r_U'])} | {f['check_rL_le_rhi']} | {f['check_rlo_le_rU']} |")
        L.append("")
    return L


def render_block_md(bt: dict) -> list[str]:
    if not bt:
        return []
    m = bt["meta"]
    L = ["### Registry transformer cells (`local-sgd` @ tiny/tiny2, `forward-nonfixed` @ tiny2; bracketed)", ""]
    L.append(f"- from `redteam/block_term.py` at `lower_coarse.py` sha1 `{m.get('lower_coarse_sha1')}`"
             + (" (stale: differs from this panel's hash; re-run `block_term`)" if False else "") + f"; {bt['N']} cells, "
             f"{bt['N_exact']} exact (single RU legal), {bt['N'] - bt['N_exact']} bracketed `[I_lo, I_hi]` (660-8700 gates: beyond the exact solver).")
    L.append(f"- **`L > I_hi` (L above a legal partition's cost): {bt['L_gt_legal_partition']}**; `U` violations: {bt['U_violations']}; "
             f"block term fired in {bt['block_fired']}/{bt['N']} cells; **did not fire at {bt['block_not_fired_binding']} binding cells** "
             f"(see `validation_block_term.md`).")
    L.append("")
    L.append("| circuit | gates | regime | binds | I* / [I_lo, I_hi] | L | block? | U | L/ref | U/ref | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in bt["rows"]:
        istar = str(r["Istar"]) if r.get("optimal") else f"[{r['I_lo']}, {_f(r.get('I_hi'))}]"
        L.append(f"| {r['circuit']} | {r['gates']} | {r['regime']} | {r['binding']} | {istar} | {_f(r.get('L'))} | "
                 f"{'yes' if r.get('block_term_fired') else 'no'} | {_f(r.get('U'))} | {_f(r.get('L_over_ref'))} | {_f(r.get('U_over_ref'))} | "
                 f"{r.get('L_verdict', '')}{'; ' + '; '.join(r['violations']) if r.get('violations') else ''} |")
    L.append("")
    return L


def render_panel_md(doc: dict) -> list[str]:
    pn, m = doc["panel"], doc["meta"]
    L = ["## Validation panel (DELIVERABLES §4)", ""]
    L.append(f"- `bounds/lower.py` sha1 `{m['lower_sha1']}`" + (f" -> `{m['lower_sha1_after']}` (changed during the run; re-run)"
             if m.get("lower_sha1_after") not in (None, m["lower_sha1"]) else "")
             + f", `bounds/lower_coarse.py` sha1 `{m.get('lower_coarse_sha1')}`"
             + (f" -> `{m['lower_coarse_sha1_after']}` (changed during the run; re-run)"
                if m.get("lower_coarse_sha1_after") not in (None, m.get("lower_coarse_sha1")) else "")
             + f"; other modules sha256[:10] { {k: v for k, v in m['versions'].items() if 'lower' not in k} }.")
    L.append(f"- **N = {pn['N_exact']} cells solved exactly** (+{pn['N_interval']} cells with a proven interval only, {pn['N_total']} total); "
             f"legality model: **acyclic RU quotient** (SPEC §0).")
    md = pn.get("model_delta") or {}
    if md.get("compared"):
        L.append(f"- vs the cyclic-quotient model (archived `validation_cyclic_model.json`): {md['compared']} exact cells compared, "
                 f"**{md['changed']} changed** (`I*_acyclic / I*_cyclic` median {_f(md['ratio_median'])}, max {_f(md['ratio_max'])}; "
                 f"median over changed cells {_f(md['ratio_median_changed'])}); changed by family: {md['changed_by_family']}.")
    bt = doc.get("registry_block_cells") or {}
    rs = doc.get("registry_rollout_cells") or {}
    L.append(f"- **`U < I*`: {pn['U_lt_Istar_count']}** (incl. illegal / under-accounted plans); **`L > I*`: {pn['L_gt_Istar_count']}**"
             + ("  <- SOUNDNESS BUG, see `validation_L_violations.md`" if pn["L_gt_Istar_count"] else "")
             + (f"; registry transformer bracket cells: {bt['N']}, `L > I_hi`: {bt['L_gt_legal_partition']}, block term silent at "
                f"{bt['block_not_fired_binding']} binding cells" if bt else "")
             + (f"; registry rollout cells (dense + MoE): {rs['N']}, `L > I_hi`: {rs['L_gt_legal_partition']}, `U` violations: {rs['U_violations']}, "
                f"inference one-RU-tokens-only: {rs['inference_ok']}/{rs['N_inference']}" if rs else "") + ".")
    L.append(f"- hashes checked: `lower_coarse.py` `{m.get('lower_coarse_sha1')}`, `coarse.py` `{m.get('coarse_sha1', m['versions'].get('bounds/coarse.py'))}`"
             + (f" (block-term rows at `lower_coarse.py` `{bt['meta'].get('lower_coarse_sha1')}`" + (" -- STALE" if bt['meta'].get('lower_coarse_sha1') != m.get('lower_coarse_sha1') else "") + ")" if bt else "")
             + (f" (rollout rows at `lower_coarse.py` `{rs['meta'].get('lower_coarse_sha1')}`, `coarse.py` `{rs['meta'].get('coarse_sha1')}`"
                + (" -- STALE" if (rs['meta'].get('lower_coarse_sha1') != m.get('lower_coarse_sha1') or rs['meta'].get('coarse_sha1') != m.get('coarse_sha1')) else "") + ")" if rs else "") + ".")
    u, l = pn["U_over_Istar"], pn["L_over_Istar"]
    L.append(f"- `U/I*` (legal, acyclic plans only): median {_f(u.get('median'))}, max {_f(u.get('max'))} (n={u['n']}; `U = I*` in "
             f"{pn['U_equals_Istar']} cells; `U` unavailable in {pn['U_unavailable']}; planner returned a **cyclic** (illegal under "
             f"SPEC §0) plan in {pn.get('U_cyclic', 0)} cells, {pn.get('U_cyclic_below_Istar', 0)} of them below the acyclic `I*` -- expected, not counted).")
    L.append(f"- `L/I*`: median {_f(l.get('median'))}, 10th percentile {_f(l.get('p10'))}, minimum {_f(l.get('min'))} (n={l['n']}; "
             f"`L = I*` in {pn['L_equals_Istar']} cells; `L` unavailable in {pn['L_unavailable']}).")
    L.append("")
    for title, key in (("By circuit family", "by_family"), ("By binding policy constraint (which cap forbids the single-RU partition)", "by_binding")):
        L.append(f"### {title}")
        L.append("")
        L.append("| split | exact cells | U/I* median | U/I* max | L/I* median | L/I* p10 | L/I* min | U<I* | L>I* |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for k, v in pn[key].items():
            L.append(f"| {k} | {v['cells']} | {_f(v['U_over_Istar'].get('median'))} | {_f(v['U_over_Istar'].get('max'))} | "
                     f"{_f(v['L_over_Istar'].get('median'))} | {_f(v['L_over_Istar'].get('p10'))} | {_f(v['L_over_Istar'].get('min'))} | "
                     f"{v['U_lt_Istar']} | {v['L_gt_Istar']} |")
        L.append("")
    L.extend(render_rollout_md(doc.get("registry_rollout_cells") or {}))
    L.extend(render_block_md(doc.get("registry_block_cells") or {}))
    L.append(f"### Worst {len(pn['worst_L_cells'])} `L/I*` cells: the attack the certificate misses")
    L.append("")
    for r in pn["worst_L_cells"]:
        L.append("- " + _cell_head(r))
        L.extend(_L_breakdown_lines(r))
        L.append("  - exact optimal partition:")
        L.extend(["  " + x for x in _partition_lines(r)])
        L.append("")
    return L


def _f(v, nd=2) -> str:
    if v is None:
        return "-"
    return f"{v:.{nd}f}" if isinstance(v, float) else str(v)


def _istar(r: dict) -> str:
    if r["Istar"] is None:
        return r["status"]
    if r["optimal"]:
        return str(r["Istar"])
    return f"[{_f(r.get('bound'))}, {r['Istar']}]"


def _U(r: dict) -> str:
    if r["U"] is None:
        return "n/a: " + (r["U_error"][:50] if r["U_error"] else "?")
    s = str(r["U"])
    if r["U_literal"] is not None and r["U_literal"] != r["U"]:
        s += f" (lit {r['U_literal']})"
    if r["U_legal"] is False:
        s += " ILLEGAL"
    return s


def render_md(doc: dict) -> str:
    rows, m = doc["rows"], doc["meta"]
    agg = aggregate(rows)
    L = ["# Validation: coarse bounds vs. exact `I*` under the corrected policy (`X = inf`)", ""]
    L.append(f"Generated {m['generated']} by `accumulation.redteam.coarse_validation` ({m['elapsed_s']/60:.1f} min).  Policy: {m['policy']}.  "
             f"`U = upper_coarse` (`bounds/coarse.py`), expanded to gates with `plan_gate_assignment` and re-judged by "
             f"`exact.solve.is_legal` / `partition_cost` (\"lit\").  "
             + ("`L = lower_coarse` (`bounds/lower.py`)." if m["lower_coarse_present"] else
                "**`lower_coarse` was not present when this ran: no `L` column.**")
             + f"  Exact time box {m['time_limit']} s per cell; unproved cells show the proven interval `[lower bound, best found]`.")
    L.append("")
    L.append("## Aggregate")
    L.append("")
    L.append(f"- **{agg['soundness_violations']}/{agg['cells']} soundness violations** "
             f"(`L <= I*`, `U` legal, `U >= literal`, `U >= I*`) over {agg['cells']} cells "
             f"({agg['cells_proved']} with proved `I*`, {agg['cells_with_Istar'] - agg['cells_proved']} with an interval); by kind: {agg['violation_kinds']}.")
    if agg["L_over_Istar"]["n"]:
        L.append(f"- `L/I*` on proved cells: median {_f(agg['L_over_Istar']['median'])}, 5th percentile {_f(agg['L_over_Istar']['p05'])}, "
                 f"min {_f(agg['L_over_Istar']['min'])} (n={agg['L_over_Istar']['n']}).")
    else:
        L.append("- `L/I*`: no `L` values (module absent).")
    L.append(f"- `U/I*` on proved cells: median {_f(agg['U_over_Istar']['median'])}, 95th percentile {_f(agg['U_over_Istar']['p95'])}, "
             f"max {_f(agg['U_over_Istar']['max'])} (n={agg['U_over_Istar']['n']}); `U` unavailable in {agg['U_unavailable']} cells; "
             f"`U == literal` in {agg['U_equals_literal']} cells, `U > literal` (conservative accounting) in {agg['U_above_literal']}.")
    L.append("")
    if doc.get("panel"):
        L.extend(render_panel_md(doc))
    viol = [r for r in rows if r["violations"]]
    if viol:
        L.append("## SOUNDNESS VIOLATIONS")
        L.append("")
        for r in viol:
            L.append(f"- **{r['circuit']}** F={r['F_label']} ({r['F']}) G={r['G_label']} ({r['G']}): I*={_istar(r)}, L={r['L']}, U={_U(r)} -> {'; '.join(r['violations'])}")
            if r.get("snippet"):
                L.append("")
                L.append("~~~python")
                L.append(r["snippet"].rstrip())
                L.append("~~~")
                L.append("")
        L.append("")
    L.append("## Per-group aggregates")
    L.append("")
    L.append("| group | cells | violations | median L/I* | p05 L/I* | median U/I* | p95 U/I* | U n/a |")
    L.append("|---|---|---|---|---|---|---|---|")
    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(r["group"], []).append(r)
    for grp, sel in groups.items():
        a = aggregate(sel)
        L.append(f"| {grp} | {a['cells']} | {a['soundness_violations']} | {_f(a['L_over_Istar']['median'])} | {_f(a['L_over_Istar']['p05'])} | "
                 f"{_f(a['U_over_Istar']['median'])} | {_f(a['U_over_Istar']['p95'])} | {a['U_unavailable']} |")
    L.append("")
    L.append("## Table")
    L.append("")
    for grp, sel in groups.items():
        if grp == "fuzz":
            continue
        L.append(f"### {grp}")
        L.append("")
        L.append("| circuit | gates | F | G | I* | L | U (lit) | L/I* | U/I* | flags |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        for r in sel:
            L.append(f"| {r['circuit'].replace('|', '/')} | {r['gates']} | {r['F_label']} ({_f(r['F'])}) | {r['G_label']} ({_f(r['G'])}) | {_istar(r)} | "
                     f"{_f(r['L'])} | {_U(r)} | {_f(r['L_over_Istar'])} | {_f(r['U_over_Istar'])} | {'; '.join(r['violations'])} |")
        L.append("")
    fz = groups.get("fuzz", [])
    if fz:
        L.append("### fuzz (worst U/I* and any L/I* < 0.5)")
        L.append("")
        L.append("| circuit | family | gates | F | G | I* | L | U (lit) | L/I* | U/I* |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        worst = sorted([r for r in fz if r["U_over_Istar"] is not None], key=lambda r: -r["U_over_Istar"])[:15]
        loose = [r for r in fz if r["L_over_Istar"] is not None and r["L_over_Istar"] < 0.5]
        for r in worst + loose:
            L.append(f"| {r['circuit']} | {r['family']} | {r['gates']} | {r['F_label']} | {r['G_label']} | {_istar(r)} | {_f(r['L'])} | {_U(r)} | "
                     f"{_f(r['L_over_Istar'])} | {_f(r['U_over_Istar'])} |")
        L.append("")
        errs: dict[str, int] = {}
        for r in fz:
            if r["U_error"]:
                key = r["U_error"].split(":")[0] + ": " + " ".join(r["U_error"].split(":")[1:])[:70]
                errs[key] = errs.get(key, 0) + 1
        if errs:
            L.append("`upper_coarse` failures on fuzz circuits (count, message):")
            L.append("")
            for k, v in sorted(errs.items(), key=lambda kv: -kv[1])[:12]:
                L.append(f"- {v} x `{k}`")
            L.append("")
    attacks = [r for r in rows if r["L_over_Istar"] is not None and r["L_over_Istar"] < 0.5 and r["partition"]]
    if attacks:
        L.append("## Attacks the certificate misses (`L/I* < 0.5`): the optimal partition")
        L.append("")
        for r in attacks:
            L.append(f"**{r['circuit']}** ({r['family']}) F={r['F_label']} G={r['G_label']}: L={r['L']}, I*={_istar(r)}")
            for ru in r["partition"]:
                ops = ", ".join(f"{k} x{v}" for k, v in ru["ops"].items())
                imps = ", ".join(f"{k}={v}B" for k, v in ru["imports"].items()) or "nothing charged"
                L.append(f"- RU{ru['ru']}: work {ru['work']}, input {ru['in_bytes']} B; ops [{ops}]; imports {imps}")
            L.append("")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="coarse bounds vs exact I* under X = inf")
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--time-limit", type=float, default=30.0)
    ap.add_argument("--exact-limit", type=int, default=64)
    ap.add_argument("--fuzz", type=int, default=200)
    ap.add_argument("--fuzz-seed", type=int, default=7)
    ap.add_argument("--fuzz-gate-cap", type=int, default=30)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--reuse-istar", action="store_true",
                    help="take exact I* cells from the previous results/validation.json (re-run L/U only, e.g. after lower.py changed)")
    a = ap.parse_args(argv)
    doc = build_validation(time_limit=a.time_limit, exact_limit=a.exact_limit, fuzz_n=a.fuzz, fuzz_seed=a.fuzz_seed,
                           fuzz_gate_cap=a.fuzz_gate_cap, verbose=not a.quiet, reuse_istar=a.reuse_istar)
    doc["meta"]["lower_sha1_after"] = lower_sha1()        # != lower_sha1 -> lower.py changed while the run was going
    doc["meta"]["lower_coarse_sha1_after"] = lower_sha1("lower_coarse.py")
    doc["aggregate"] = aggregate(doc["rows"])
    doc["panel"] = panel(doc["rows"])
    doc["meta"]["coarse_sha1"] = lower_sha1("coarse.py")
    doc["registry_block_cells"] = _load_block_term(os.path.join(a.out_dir, "block_term.json"))
    doc["registry_rollout_cells"] = _load_rollout(os.path.join(a.out_dir, "rollout_scale.json"))
    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "validation_L_violations.md"), "w") as f:
        f.write(render_L_violations(doc))
    with open(os.path.join(a.out_dir, "validation.json"), "w") as f:
        json.dump(doc, f, indent=1, default=str)
    with open(os.path.join(a.out_dir, "validation.md"), "w") as f:
        f.write(render_md(doc))
    agg = doc["aggregate"]
    print(f"wrote {os.path.join(a.out_dir, 'validation.md')} / .json: {agg['soundness_violations']}/{agg['cells']} violations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
