"""The exact tiny wedge: ``I*(C; F, G)`` under the corrected policy (``X = inf``; legal iff ``work(R) <= G`` and
``work(Up_R(g)) <= F``) on the multi-step micro suite, as a table ``(circuit, F, G) -> I*, I*/token, useful
MACs, kappa = MACs / I*``.

Circuits (``accumulation/exact/micro.py``): ``micro_inference`` (one fixed linear layer), ``local_sgd_chain``
(``K`` chained SGD steps on one accumulated weight, the accumulation chain), ``fanout_shared_weight`` (independent
matmuls sharing one produced weight), ``deep_chain`` (serial chain whose fused ``Up`` exceeds ``F``); plus the
registry ``inference-dense`` / ``local-sgd`` at ``tiny`` / ``tiny2`` for the cells the exact solver can settle at
that size (the single-RU cells: optimal by the charged-leaves argument) -- every other registry cell is reported as
"beyond exact scale" with its gate count.

Units.  ``fwd`` = total work of the inference forward of the same layer geometry (``micro_inference`` at the same
``(q, d)``: ``q*d*(d+1)``; for registry circuits the ``inference-dense`` circuit at the same model and ``q``).  Work
is the primitive ``.work`` summed over gates and equals the operator-graph work (``sum(op.work_per_copy * copies)``),
so the bound modules and the solver use the same ``F``/``G`` numbers.  ``F in {1, 1.5, 3} * fwd`` (+ ``inf``),
``G in {1, 4} * fwd`` (+ ``inf``).  Useful MACs: ``adw.all_macs`` for circuits without accumulated/carried roots
(inference: fixed-weight products are the useful work), ``adw.credited_macs`` otherwise (SPEC §6).

Usage::

    PYTHONPATH=. .venv/bin/python -m accumulation.redteam.wedge --time-limit 150
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from typing import Optional

from accumulation.redteam.harness import describe_partition, op_gate_lists, with_timeout, SolverTimeout

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(HERE, "results")

F_MULT = (1.0, 1.5, 3.0, None)
G_MULT = (1.0, 4.0, None)


def _cap(mult: Optional[float], fwd: int) -> Optional[int]:
    return None if mult is None else int(math.ceil(mult * fwd))


def _mult_str(m: Optional[float]) -> str:
    return "inf" if m is None else (f"{m:g}·fwd")


def circuits(*, registry: bool = True) -> list[dict]:
    from accumulation.exact import micro
    out = []
    for q in (1, 2):
        out.append(dict(group="micro inference", bp=micro.micro_inference(q=q), fwd=q * 2 * 3, K=None, q=q))
    for K in (1, 2, 3):
        out.append(dict(group="micro local-sgd chain (d=1, q=1)", bp=micro.local_sgd_chain(K_steps=K, q=1, d=1), fwd=2, K=K, q=1))
    for K in (1, 2, 3):
        out.append(dict(group="micro local-sgd chain (d=1, q=2)", bp=micro.local_sgd_chain(K_steps=K, q=2, d=1), fwd=4, K=K, q=2))
    for K in (1, 2, 3):
        out.append(dict(group="micro local-sgd chain (d=2, q=1)", bp=micro.local_sgd_chain(K_steps=K, q=1), fwd=6, K=K, q=1))
    for K in (1, 2):
        out.append(dict(group="micro local-sgd chain (d=2, q=2)", bp=micro.local_sgd_chain(K_steps=K, q=2), fwd=12, K=K, q=2))
    out.append(dict(group="micro fan-out (shared produced weight)", bp=micro.fanout_shared_weight(n=4), fwd=6, K=None, q=1))
    for depth in (4, 6):
        out.append(dict(group="micro deep chain (fixed weights)", bp=micro.deep_chain(depth=depth), fwd=6, K=None, q=1))
    if registry:
        from accumulation.algorithms.registry import ALGORITHMS
        from accumulation.configs import MODELS, Workload
        from accumulation.exact.solve import flatten
        for m in ("tiny", "tiny2"):
            for q in (2, 3, 4):
                wl = Workload(tokens=q, seq=q, chunk=1, population=1, rank=1, local_steps=1)
                bp = ALGORITHMS["inference-dense"].build(MODELS[m], wl)
                fwd = flatten(bp).total_work()
                out.append(dict(group=f"registry inference-dense @ {m}", bp=bp, fwd=fwd, K=None, q=q, registry=True))
                if q == 2:
                    for K in (1, 2, 3):
                        wlk = Workload(tokens=K * q, seq=q, chunk=1, population=1, rank=1, local_steps=K)
                        bpk = ALGORITHMS["local-sgd"].build(MODELS[m], wlk)
                        out.append(dict(group=f"registry local-sgd @ {m} (q=2)", bp=bpk, fwd=fwd, K=K, q=q, registry=True))
    return out


def _legal_cost(flat, asg, F, G):
    from accumulation.exact.solve import is_legal, partition_cost
    ok, _ = is_legal(flat, asg, F, None, G)
    return partition_cost(flat, asg) if ok else None


def improve_partition(flat, asg: dict, F: Optional[int], G: Optional[int], *, budget_s: float = 30.0) -> dict:
    """Local search on a legal partition: single-gate moves (to another RU or a fresh one) and RU merges while the
    cost drops.  Only a heuristic (an *upper* bound on ``I*``) -- used to tighten unproved MILP incumbents."""
    best = dict(asg)
    cost = _legal_cost(flat, best, F, G)
    if cost is None:
        return best
    t0 = time.perf_counter()
    improved = True
    while improved and time.perf_counter() - t0 < budget_s:
        improved = False
        rus = sorted(set(best.values()))
        fresh = max(rus) + 1
        for gte in flat.gates:
            cur = best[gte]
            for r in rus + [fresh]:
                if r == cur:
                    continue
                trial = dict(best)
                trial[gte] = r
                c = _legal_cost(flat, trial, F, G)
                if c is not None and c < cost:
                    best, cost, improved = trial, c, True
                    break
            if improved:
                break
        if improved:
            continue
        for i, a in enumerate(rus):
            for b in rus[i + 1:]:
                trial = {gg: (a if r == b else r) for gg, r in best.items()}
                c = _legal_cost(flat, trial, F, G)
                if c is not None and c < cost:
                    best, cost, improved = trial, c, True
                    break
            if improved:
                break
    return best


def structured_seeds(flat, g, og: Optional[dict]) -> list[dict]:
    """Legal-or-not starting partitions: one RU per op, one RU per gate, and op-prefix blocks of growing size."""
    seeds = [{gt: gt for gt in flat.gates}]
    if og:
        gate_op = {gt: oid for oid, gl in og.items() for gt in gl}
        seeds.append({gt: gate_op.get(gt, -1 - gt) for gt in flat.gates})
        ops = sorted(og)
        for k in (2, 3, 4, 6):
            seeds.append({gt: (ops.index(gate_op[gt]) // k if gt in gate_op else -1 - gt) for gt in flat.gates})
    return seeds


def cyclic_reference(path: str) -> dict:
    """``(circuit, gates, F, G) -> I*`` proved under the old cyclic-quotient model (a valid lower bound on the
    acyclic ``I*``: used as ``lower_hint`` for the branch and bound and reported as ``Istar_cyclic``)."""
    try:
        with open(path) as f:
            doc = json.load(f)
    except OSError:
        return {}
    return {(r["circuit"], r["gates"], r["F"], r["G"]): r["Istar"] for r in doc.get("rows", [])
            if r.get("optimal") and r.get("Istar") is not None and r.get("model", "cyclic") == "cyclic"}


def run_cell(bp, flat, g, og, F: Optional[int], G: Optional[int], *, time_limit: float, exact_limit: int,
             lower_hint: Optional[int] = None) -> dict:
    from accumulation.exact.solve import Infeasible, exact_min_input, is_legal
    t0 = time.perf_counter()
    cell: dict = {"F": F, "G": G, "Istar": None, "optimal": False, "method": "", "seconds": 0.0, "n_units": None,
                  "status": "", "partition": [], "bound": None, "heuristic": None, "model": "acyclic",
                  "Istar_cyclic": lower_hint, "assignment": None}
    asg = None
    try:
        # HiGHS gets ``time_limit`` (and returns its dual bound); the alarm is only a safety net beyond that
        r = with_timeout(time_limit + 90, exact_min_input, flat, F, None, G, limit=exact_limit, method="auto",
                         time_limit=max(1.0, time_limit), lower_hint=lower_hint)
        cell.update(Istar=int(r.total), optimal=bool(r.optimal), method=r.method, n_units=int(r.n_units),
                    status="optimal" if r.optimal else "found (not proved)", bound=r.bound)
        asg = r.assignment
    except Infeasible:
        cell["status"] = "infeasible"
    except SolverTimeout:
        cell["status"] = "timeout"
    except ValueError as e:
        cell["status"] = f"beyond exact scale ({flat.n_gates} gates)" if "limit" in str(e) else f"error: {e}"
    if cell["bound"] is None and cell["status"] != "infeasible":
        cons = flat.consumers()
        cell["bound"] = sum(flat.bytes_of(v) for v in flat.nonfixed_inputs if cons.get(v))   # every read charged root enters once
    if not cell["optimal"] and og is not None and cell["status"] != "infeasible":
        # tighten the primal side with local search from the incumbent and from structured seeds
        cands = ([asg] if asg is not None else []) + structured_seeds(flat, g, og)
        best, bc = None, None
        for s0 in cands:
            try:
                if not is_legal(flat, s0, F, None, G)[0]:
                    continue
                s1 = improve_partition(flat, s0, F, G, budget_s=max(5.0, time_limit / 10))
                c = _legal_cost(flat, s1, F, G)
            except Exception as e:                                  # noqa: BLE001
                cell["status"] += f" (local search error: {type(e).__name__})"
                continue
            if c is not None and (bc is None or c < bc):
                best, bc = s1, c
        if best is not None:
            cell["heuristic"] = bc
            if cell["Istar"] is None or bc < cell["Istar"]:
                cell.update(Istar=bc, n_units=len(set(best.values())), method=(cell["method"] + "+ls").lstrip("+"),
                            status="found (not proved)")
                asg = best
    if asg is not None and og is not None:
        cell["partition"] = describe_partition(flat, g, og, asg)
    if asg is not None and flat.n_gates <= 2000:
        cell["assignment"] = [int(asg[gt]) for gt in flat.gates]          # RU id per gate, in gate order
    cell["seconds"] = time.perf_counter() - t0
    return cell


def _spec_rows(idx: int, *, time_limit: float, exact_limit: int, registry: bool, verbose: bool, heur_limit: int) -> list[dict]:
    """All cells of circuit ``idx`` of :func:`circuits` (a worker unit for ``--jobs``)."""
    from accumulation.bounds.adw import adw
    from accumulation.exact.solve import flatten
    from accumulation.graph import extract
    spec = circuits(registry=registry)[idx]
    rows: list[dict] = []
    if True:
        bp, fwd = spec["bp"], spec["fwd"]
        flat = flatten(bp)
        g = extract(bp)
        a = adw(g)
        og = None if flat.n_gates > heur_limit else op_gate_lists(bp, g, flat)
        has_state = any(flat.input_role[v] in ("accumulated", "carried") for v in flat.nonfixed_inputs)
        macs = int(a.credited_macs if has_state else a.all_macs)
        tokens = int(bp.workload.tokens)
        charged = sum(flat.bytes_of(v) for v in flat.nonfixed_inputs)
        by_role: dict[str, int] = {}
        for v in flat.nonfixed_inputs:
            by_role[flat.input_role[v]] = by_role.get(flat.input_role[v], 0) + flat.bytes_of(v)
        base = dict(group=spec["group"], circuit=bp.algorithm, gates=flat.n_gates, work=flat.total_work(), fwd=fwd,
                    work_over_fwd=flat.total_work() / fwd, tokens=tokens, K=spec["K"], q=spec["q"], useful_macs=macs,
                    charged_root_bytes=charged, charged_by_role=by_role, registry=bool(spec.get("registry")))
        if verbose:
            print(f"== {bp.algorithm}: {flat.n_gates} gates, work {flat.total_work()} = {flat.total_work()/fwd:.2f} fwd, "
                  f"MACs {macs}, charged roots {charged} B {by_role}", flush=True)
        cyc = cyclic_reference(os.path.join(DEFAULT_OUT, "wedge_exact_cyclic_model.json"))
        for fm in F_MULT:
            for gm in G_MULT:
                F, G = _cap(fm, fwd), _cap(gm, fwd)
                cell = run_cell(bp, flat, g, og, F, G, time_limit=time_limit, exact_limit=exact_limit,
                                lower_hint=cyc.get((bp.algorithm, flat.n_gates, F, G)))
                row = dict(base)
                row.update(F_mult=fm, G_mult=gm, F_label=_mult_str(fm), G_label=_mult_str(gm), **cell)
                I = cell["Istar"]
                row["Istar_per_token"] = None if I is None else I / tokens
                row["kappa"] = None if not I else macs / I
                rows.append(row)
                if verbose:
                    print(f"   [{bp.algorithm}] F={_mult_str(fm):>8s} ({F}) G={_mult_str(gm):>8s} ({G}): I*={I} {cell['status']} "
                          f"bound={cell['bound']} heur={cell['heuristic']} [{cell['method']}, {cell['seconds']:.1f}s] "
                          f"units={cell['n_units']}", flush=True)
    return rows


def _run_subprocesses(n: int, jobs: int, *, registry: bool, time_limit: float, exact_limit: int, heur_limit: int,
                      verbose: bool) -> list[list[dict]]:
    """One subprocess per circuit (``--only i``), at most ``jobs`` at a time, each with a wall-clock cap; a
    crashed or timed-out circuit yields error rows instead of hanging the run (a ``multiprocessing.Pool`` hangs
    forever when a worker dies inside HiGHS)."""
    import subprocess
    import sys
    import tempfile
    order = sorted(range(n), key=lambda i: -circuits(registry=registry)[i]["bp"].program.gates)
    tmp = tempfile.mkdtemp(prefix="wedge_parts_")
    cap = len(F_MULT) * len(G_MULT) * (time_limit + 300) + 120
    procs: dict[int, tuple] = {}
    parts: dict[int, list[dict]] = {}
    pending = list(order)
    env = dict(os.environ, PYTHONPATH=os.environ.get("PYTHONPATH", "."))
    while pending or procs:
        while pending and len(procs) < jobs:
            i = pending.pop(0)
            out = os.path.join(tmp, f"{i}.json")
            cmd = [sys.executable, "-m", "accumulation.redteam.wedge", "--only", str(i), "--part-out", out,
                   "--time-limit", str(time_limit), "--exact-limit", str(exact_limit)] + ([] if registry else ["--no-registry"])                   + ([] if verbose else ["--quiet"])
            procs[i] = (subprocess.Popen(cmd, env=env), time.time(), out)
        time.sleep(2.0)
        for i, (p, t0, out) in list(procs.items()):
            rc = p.poll()
            if rc is None and time.time() - t0 > cap:
                p.kill()
                rc = -9
            if rc is None:
                continue
            del procs[i]
            try:
                with open(out) as f:
                    parts[i] = json.load(f)
            except (OSError, ValueError):
                parts[i] = [_error_row(i, f"subprocess exit code {rc} (crashed or exceeded the wall-clock cap)")]
    return [parts[i] for i in range(n)]


def _error_row(idx: int, msg: str) -> dict:
    return {"group": "error", "circuit": f"circuit #{idx}", "status": f"worker error: {msg}", "Istar": None, "optimal": False,
            "partition": [], "K": None, "F": None, "G": None, "F_label": "", "G_label": "", "gates": 0, "work": 0,
            "work_over_fwd": 0.0, "tokens": 0, "useful_macs": 0, "charged_root_bytes": 0, "charged_by_role": {},
            "Istar_per_token": None, "kappa": None, "n_units": None, "method": "", "seconds": 0.0, "bound": None,
            "heuristic": None, "F_mult": None, "G_mult": None, "q": None, "fwd": 0, "registry": False}


def _worker(args):
    idx, kw = args
    try:
        return idx, _spec_rows(idx, **kw)
    except Exception as e:                                          # noqa: BLE001 - one circuit must not sink the run
        import traceback
        return idx, [{"group": "error", "circuit": f"circuit #{idx}", "status": f"worker error: {type(e).__name__}: {e}",
                      "traceback": traceback.format_exc(), "Istar": None, "optimal": False, "partition": [], "K": None,
                      "F": None, "G": None, "F_label": "", "G_label": "", "gates": 0, "work": 0, "work_over_fwd": 0.0,
                      "tokens": 0, "useful_macs": 0, "charged_root_bytes": 0, "charged_by_role": {}, "Istar_per_token": None,
                      "kappa": None, "n_units": None, "method": "", "seconds": 0.0, "bound": None, "heuristic": None}]


def build_wedge(*, time_limit: float, exact_limit: int, registry: bool, verbose: bool, heur_limit: int = 200,
                jobs: int = 1) -> dict:
    n = len(circuits(registry=registry))
    kw = dict(time_limit=time_limit, exact_limit=exact_limit, registry=registry, verbose=verbose, heur_limit=heur_limit)
    if jobs <= 1:
        parts = [_spec_rows(i, **kw) for i in range(n)]
    else:
        parts = _run_subprocesses(n, jobs, registry=registry, time_limit=time_limit, exact_limit=exact_limit,
                                  heur_limit=heur_limit, verbose=verbose)
    rows = [r for part in parts for r in part]
    return {"meta": {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "time_limit": time_limit, "exact_limit": exact_limit,
                     "F_mult": list(F_MULT), "G_mult": list(G_MULT),
                     "policy": "X = inf; legal iff work(R) <= G and work(Up_R(g)) <= F; charged roles: token, accumulated, carried, seed",
                     "work_measure": "primitive .work summed over gates == OpGraph op work (Mac16 = Round16 = Add16 = Scale16 = Sub16 = 1, Zero32 = 0)"},
            "rows": rows}


# ---------------------------------------------------------------------------------------------------------
# markdown
# ---------------------------------------------------------------------------------------------------------

def _f(v, nd=2) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def _istar(row: dict) -> str:
    if row["Istar"] is None:
        return row["status"]
    if row["optimal"]:
        return str(row["Istar"])
    b = row.get("bound")
    return f"[{b if b is not None else '?'}, {row['Istar']}] (not proved)"


def render_md(doc: dict) -> str:
    rows = doc["rows"]
    L = ["# Exact tiny wedge: `I*(C; F, G)` under the corrected policy (`X = inf`)", ""]
    m = doc["meta"]
    L.append(f"Generated {m['generated']} by `accumulation.redteam.wedge`.  Policy: {m['policy']}.  Work measure: "
             f"{m['work_measure']}.  `fwd` = work of the inference forward of the same layer geometry; `F in "
             f"{{1, 1.5, 3}} fwd` and `inf`, `G in {{1, 4}} fwd` and `inf`.  Exact solver time box {m['time_limit']} s "
             f"per cell; circuits above {m['exact_limit']} gates get the MILP only where the single-RU partition is legal "
             f"(then it is optimal: every partition pays every distinct charged root leaf at least once); otherwise a "
             f"local-search upper value and the trivial charged-root lower bound.  Unproved cells are shown as "
             f"`[lower bound, best found]`.")
    L.append("")
    L.append("## Circuits")
    L.append("")
    L.append("| circuit | gates | work | work/fwd | tokens | useful MACs | charged roots (B) | by role |")
    L.append("|---|---|---|---|---|---|---|---|")
    seen = set()
    for r in rows:
        if r["circuit"] in seen:
            continue
        seen.add(r["circuit"])
        L.append(f"| {r['circuit']} | {r['gates']} | {r['work']} | {_f(r['work_over_fwd'])} | {r['tokens']} | {r['useful_macs']} | "
                 f"{r['charged_root_bytes']} | {r['charged_by_role']} |")
    L.append("")
    L.append("## Table: (circuit, F, G) -> I*")
    L.append("")
    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(r["group"], []).append(r)
    for grp, sel in groups.items():
        L.append(f"### {grp}")
        L.append("")
        L.append("| circuit | F | G | I* (B) | I*/token | useful MACs | kappa = MACs/I* | RUs | solver | s |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        for r in sel:
            L.append(f"| {r['circuit']} | {r['F_label']} ({_f(r['F'])}) | {r['G_label']} ({_f(r['G'])}) | {_istar(r)} | "
                     f"{_f(r['Istar_per_token'])} | {r['useful_macs']} | {_f(r['kappa'])} | {_f(r['n_units'])} | {r['method']} | "
                     f"{r['seconds']:.1f} |")
        L.append("")
    # marginal per step for the chains
    L.append("## Per-step marginal `I*(K) - I*(K-1)` on the local-SGD chains")
    L.append("")
    L.append("| chain | F | G | I*(K=1) | I*(K=2) | I*(K=3) | marginal K=2 | marginal K=3 |")
    L.append("|---|---|---|---|---|---|---|---|")
    chains: dict[tuple, dict[int, dict]] = {}
    for r in rows:
        if r["K"] is not None and "local" in r["group"]:
            chains.setdefault((r["group"], r["F_label"], r["G_label"]), {})[r["K"]] = r
    for (grp, Fl, Gl), byK in chains.items():
        def val(k):
            r = byK.get(k)
            return None if r is None or r["Istar"] is None else r["Istar"]
        def cell(k):
            r = byK.get(k)
            return "-" if r is None else _istar(r)
        i1, i2, i3 = val(1), val(2), val(3)
        m2 = None if i1 is None or i2 is None else i2 - i1
        m3 = None if i2 is None or i3 is None else i3 - i2
        L.append(f"| {grp} | {Fl} | {Gl} | {cell(1)} | {cell(2)} | {cell(3)} | {_f(m2)} | {_f(m3)} |")
    L.append("")
    L.append("## Optimal partitions (micro circuits)")
    L.append("")
    for r in rows:
        if not r["partition"] or r["n_units"] == 1:
            continue
        L.append(f"**{r['circuit']}** at F={r['F_label']} ({_f(r['F'])}), G={r['G_label']} ({_f(r['G'])}): I* = {_istar(r)}, "
                 f"{r['n_units']} RUs")
        groups2: dict[str, list[int]] = {}
        for ru in r["partition"]:
            ops = ", ".join(f"{k} x{v}" for k, v in ru["ops"].items())
            imps = ", ".join(f"{k}={v}B" for k, v in ru["imports"].items()) or "nothing charged"
            key = f"work {ru['work']}, input {ru['in_bytes']} B; ops [{ops}]; imports {imps}"
            groups2.setdefault(key, []).append(ru["ru"])
        for key, rus in groups2.items():
            lab = f"RU{rus[0]}" if len(rus) == 1 else f"{len(rus)} RUs"
            L.append(f"- {lab}: {key}")
        L.append("")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="exact tiny wedge under the corrected (X = inf) policy")
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--time-limit", type=float, default=150.0)
    ap.add_argument("--exact-limit", type=int, default=64, help="MILP only up to this many gates; above: heuristic + trivial bound")
    ap.add_argument("--no-registry", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--jobs", type=int, default=1, help="worker processes (one circuit per task)")
    ap.add_argument("--only", type=int, default=None, help="(worker) run circuit #i only and write its rows to --part-out")
    ap.add_argument("--part-out", default=None)
    a = ap.parse_args(argv)
    if a.only is not None:
        rows = _spec_rows(a.only, time_limit=a.time_limit, exact_limit=a.exact_limit, registry=not a.no_registry,
                          verbose=not a.quiet, heur_limit=200)
        with open(a.part_out, "w") as f:
            json.dump(rows, f, default=str)
        return 0
    doc = build_wedge(time_limit=a.time_limit, exact_limit=a.exact_limit, registry=not a.no_registry, verbose=not a.quiet,
                      jobs=a.jobs)
    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "wedge_exact.json"), "w") as f:
        json.dump(doc, f, indent=1, default=str)
    with open(os.path.join(a.out_dir, "wedge_exact.md"), "w") as f:
        f.write(render_md(doc))
    print(f"wrote {os.path.join(a.out_dir, 'wedge_exact.md')} / .json ({len(doc['rows'])} cells)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
