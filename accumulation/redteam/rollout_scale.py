"""Dynamic-rollout cells on the *registry* circuits at exact-solver scale (``ROLLOUT_PLAN.md``): dense
``forward-nonfixed`` @ tiny2 and MoE ``forward-nonfixed-moe`` @ tiny-moe, plus their fixed-weight references
``inference-dense`` / ``inference-moe`` which must be ONE legal RU with imports = token bytes at the default policy
point ``F_hat = 1.5, G_hat = 4``.

Cells mirror the sweeps exactly (``sweeps.coarse_run.Cell`` -> ``make_workload``; ``F = F_hat * fwd(Q_inf)``,
``G = G_hat * fwd(Q_inf)`` with ``fwd = adw(inference graph at Q_inf, seq = Q_inf).all_work`` as in
``sweeps.calibration``): the rollout has ``Q_roll`` tokens in ``Q_roll / Q_inf`` independent sequences of
``seq = Q_inf`` and the same dynamic weights.  ``Q_roll`` grows ``Q_inf, 2 Q_inf, 4 Q_inf, ...`` until the graph
is beyond what the heuristics tolerate.

Per cell: ``L = lower_coarse`` (+ breakdown), ``U = upper_coarse`` (literal cost of the expanded plan, re-checked
with ``is_legal`` under the acyclic RU quotient), and ``I*`` exact where the single RU is legal, else the bracket
``[I_lo, I_hi]`` (``I_lo`` = read charged roots + tokens; ``I_hi`` = cheapest legal partition constructed from the
planner's plans at ``(F, G)`` and at tighter ``G' in {G/2, G/4}`` and from per-op seeds, each greedily merged
under the true caps).  Registry graphs have 660-28000 gates; the gate-level exact solver only decides the
single-RU cells, so the bracket is the honest object (the *micro* analogues ``exact.micro.dense_rollout`` /
``moe_rollout`` carry the true exact ``I*`` in ``coarse_validation``).

Steady-state marginal (ROLLOUT_PLAN P1): per ``(model, regime)`` the points with ``Q_roll`` beyond the one-RU
range are fitted as ``X(Q) ~ a + r Q`` for ``X in {I_lo, I_hi (or I*), L, U}``; ``r_L <= r_hi`` and
``r_lo <= r_U`` are the checkable brackets of the marginal (``r_lo <= r* <= r_hi``).

Outputs ``results/rollout_scale.json`` + ``results/validation_rollout.md``; ``coarse_validation`` folds the rows
into ``results/validation.{md,json}``.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

from accumulation.redteam.block_term import _Fast, _lower, block_fired, greedy_merge, seeds
from accumulation.redteam.harness import _versions, describe_partition, op_gate_lists

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(HERE, "results")

DEFAULT_POINT = (1.5, 4.0)
# (label, F_hat, G_hat) -- multiples of fwd(Q_inf); None = no cap
REGIMES = [("default: F_hat=1.5, G_hat=4", 1.5, 4.0),
           ("G_hat=2 (F_hat=1.5)", 1.5, 2.0),
           ("G_hat=1 (one session per RU; F_hat=1.5)", 1.5, 1.0),
           ("G-only: G_hat=1, F=inf", None, 1.0),
           ("F_hat=0.5 (session cone does not fit), G_hat=4", 0.5, 4.0)]


@dataclass
class Spec:
    model: str
    circuit: str
    Q_inf: int
    mults: tuple[int, ...]                 # Q_roll = m * Q_inf
    regimes: list = field(default_factory=lambda: list(REGIMES))
    inference: bool = False                # fixed-weight reference: Q_roll = Q_inf only, default point only

    def name(self, Q_roll: int) -> str:
        return f"{self.circuit}[{self.model},Q_inf={self.Q_inf},Q_roll={Q_roll}]"


def specs(max_gates: int = 30_000) -> list[Spec]:
    return [
        Spec("tiny2", "inference-dense", 1, (1,), [REGIMES[0]], inference=True),
        Spec("tiny2", "inference-dense", 2, (1,), [REGIMES[0]], inference=True),
        Spec("tiny2", "inference-dense", 4, (1,), [REGIMES[0]], inference=True),
        Spec("tiny2", "forward-nonfixed", 1, (1, 2, 4, 8, 16, 32, 64)),
        Spec("tiny2", "forward-nonfixed", 2, (1, 2, 4, 8, 16, 32)),
        Spec("tiny-moe", "inference-moe", 4, (1,), [REGIMES[0]], inference=True),
        Spec("tiny-moe", "inference-moe", 8, (1,), [REGIMES[0]], inference=True),
        Spec("tiny-moe", "forward-nonfixed-moe", 4, (1, 2, 4, 8, 16)),
    ]


def all_cells() -> list[tuple[int, int, int]]:
    """(spec index, multiplier index, regime index)."""
    return [(i, mi, ri) for i, s in enumerate(specs()) for mi in range(len(s.mults)) for ri in range(len(s.regimes))]


# ---------------------------------------------------------------------------------------------------------
# building (identical to the sweeps)
# ---------------------------------------------------------------------------------------------------------

def fwd_work(model: str, Q_inf: int) -> tuple[int, str]:
    """``fwd(Q_inf)`` exactly as ``sweeps.calibration``: checker work of the calibration circuit at ``tokens = seq = Q_inf``."""
    from accumulation.algorithms.registry import ALGORITHMS
    from accumulation.bounds.adw import adw
    from accumulation.configs import Workload
    from accumulation.graph.opgraph import extract
    from accumulation.sweeps.calibration import calibration_alg
    from accumulation.sweeps.synthetic import model_cfg
    alg = calibration_alg(model)
    bp = ALGORITHMS[alg].build(model_cfg(model), Workload(tokens=Q_inf, seq=Q_inf))
    return int(adw(extract(bp)).all_work), alg


def build(spec: Spec, Q_roll: int):
    from accumulation.algorithms.registry import ALGORITHMS
    from accumulation.sweeps.coarse_run import Cell, make_workload
    from accumulation.sweeps.synthetic import model_cfg
    if spec.inference:
        c = Cell(model=spec.model, circuit=spec.circuit, Q_inf=spec.Q_inf, F_hat=1.5, G_hat=4.0, Q_step=None, K=None, seq=spec.Q_inf)
    else:
        c = Cell(model=spec.model, circuit=spec.circuit, Q_inf=spec.Q_inf, F_hat=1.5, G_hat=4.0, Q_step=Q_roll, K=1,
                 seq=min(Q_roll, spec.Q_inf))
    wl = make_workload(c)
    cfg = model_cfg(spec.model)
    why = ALGORITHMS[spec.circuit].supports(cfg, wl)
    if why:
        raise ValueError(f"{spec.circuit} @ {spec.model} {wl}: {why}")
    return ALGORITHMS[spec.circuit].build(cfg, wl), wl


# ---------------------------------------------------------------------------------------------------------
# one cell
# ---------------------------------------------------------------------------------------------------------

def _plan_seeds(g, flat, bp, F: Optional[int], G: Optional[int]) -> list[tuple[str, dict]]:
    """The planner's own tilings at the true caps and at tighter ``G``: finer legal starting points for merging."""
    from accumulation.bounds.coarse import plan_gate_assignment, upper_coarse
    out = []
    Fe = flat.total_work() if F is None else F
    Gs = [("G", G)]
    if G is not None:
        Gs += [("G/2", G // 2), ("G/4", G // 4)]
    else:
        W = flat.total_work()
        Gs += [("W/2", W // 2), ("W/4", W // 4)]
    for lab, Gp in Gs:
        try:
            plan = upper_coarse(g, Fe, Gp, program=bp.program)
            asg = plan_gate_assignment(g, plan, bp.program)
            if set(asg) >= set(flat.gates):
                out.append((f"upper_coarse plan @ {lab}", {k: asg[k] for k in flat.gates}))
        except Exception:                      # noqa: BLE001
            continue
    return out


def previous_rows(path: str) -> dict:
    """``(circuit, regime) -> row`` of a previous run (brackets depend only on the circuit and ``(F, G)``, not on the
    bound modules, so they can be reused when only ``lower_coarse`` / ``coarse`` changed)."""
    try:
        with open(path) as f:
            doc = json.load(f)
    except OSError:
        return {}
    return {(r["circuit"], r["regime"]): r for r in doc.get("rows", []) if "error" not in r}


def run_cell(spec: Spec, Q_roll: int, regime: tuple, *, budget_s: float, verbose: bool, prev: Optional[dict] = None) -> dict:
    from accumulation.exact.solve import flatten, is_legal, partition_cost
    from accumulation.graph.opgraph import extract
    from accumulation.redteam.coarse_validation import binding_constraint, eval_upper

    t0 = time.perf_counter()
    bp, wl = build(spec, Q_roll)
    flat = flatten(bp)
    g = extract(bp)
    og = op_gate_lists(bp, g, flat)
    fwd, cal_alg = fwd_work(spec.model, spec.Q_inf)
    label, fh, gh = regime
    F = None if fh is None else int(round(fh * fwd))
    G = None if gh is None else int(round(gh * fwd))
    W = flat.total_work()
    tokens = int(wl.tokens)
    cell: dict = dict(circuit=spec.name(Q_roll), model=spec.model, algorithm=spec.circuit, inference=spec.inference,
                      Q_inf=spec.Q_inf, Q_roll=Q_roll, mult=Q_roll // spec.Q_inf, seq=int(wl.seq), tokens=tokens,
                      gates=flat.n_gates, ops=len(g.ops), work=W, fwd=fwd, fwd_alg=cal_alg, work_over_fwd=W / fwd,
                      regime=label, F_hat=fh, G_hat=gh, F=F, G=G, default_point=(fh, gh) == DEFAULT_POINT,
                      P=int(bp.state_bytes()), token_bytes=int(bp.param_bytes("token")), model_type="acyclic")
    cell["binding"] = binding_constraint(flat, F, G)
    cons = flat.consumers()
    floor = sum(flat.bytes_of(v) for v in flat.nonfixed_inputs if cons.get(v))
    cell.update(I_lo=floor, I_hi=None, I_hi_source="", Istar=None, optimal=False, partition=[], n_units_hi=None)
    if cell["binding"] == "none":
        one = {gt: 0 for gt in flat.gates}
        ok, why = is_legal(flat, one, F, None, G)
        assert ok, why
        c1 = partition_cost(flat, one)
        assert c1 == floor
        cell.update(Istar=c1, optimal=True, I_hi=c1, I_hi_source="single RU", n_units_hi=1)
    cell.update(eval_upper(bp, flat, g, F, G))
    L, err, brk = _lower(g, F, G, bp)
    cell.update(L=L, L_error=err, L_breakdown=brk, block_term_fired=block_fired(brk) if brk else None)
    reuse = (prev is not None and prev.get("I_hi") is not None and prev.get("F") == F and prev.get("G") == G
             and prev.get("gates") == flat.n_gates and prev.get("I_lo") == floor)
    if not cell["optimal"] and reuse:
        cell.update(I_hi=prev["I_hi"], I_hi_source=prev["I_hi_source"] + " (reused bracket)", n_units_hi=prev.get("n_units_hi"),
                    partition=prev.get("partition", []), I_hi_candidates=prev.get("I_hi_candidates", []))
        # a fresh legal planner plan may beat the stored bracket
        if cell.get("U_legal") and cell.get("U_literal") is not None and cell["U_literal"] < cell["I_hi"]:
            cell.update(I_hi=cell["U_literal"], I_hi_source="upper_coarse plan (literal)", n_units_hi=cell.get("U_units"))
    elif not cell["optimal"]:
        fast = _Fast(flat)
        best, best_cost, src = None, None, ""
        cands = _plan_seeds(g, flat, bp, F, G) + [s for s in seeds(flat, og) if s[0] != "per-gate" or flat.n_gates <= 1500]
        per = max(5.0, budget_s / max(1, len(cands)))
        tried = []
        for name, s0 in cands:
            if time.perf_counter() - t0 > budget_s * 1.5:
                break
            if not fast.legal(s0, F, G):
                tried.append(f"{name}: illegal seed")
                continue
            asg, c = greedy_merge(flat, fast, s0, F, G, budget_s=per)
            ok, why = is_legal(flat, asg, F, None, G)
            if not ok:
                tried.append(f"{name}: merged partition illegal ({why[:60]})")
                continue
            c = partition_cost(flat, asg)
            tried.append(f"{name}: {c} B, {len(set(asg.values()))} RUs")
            if best_cost is None or c < best_cost:
                best, best_cost, src = asg, c, f"{name} + greedy merge"
        cell["I_hi_candidates"] = tried
        if best is not None:
            n_ru = len(set(best.values()))
            cell.update(I_hi=best_cost, I_hi_source=src, n_units_hi=n_ru,
                        partition=describe_partition(flat, g, og, best) if n_ru <= 40 else [{"ru": "…", "note": f"{n_ru} RUs (not listed)"}])
    # verdicts
    viol = []
    if L is not None and cell["I_hi"] is not None and L > cell["I_hi"]:
        viol.append(f"L_gt_legal_partition: L={L} > cost of legal partition {cell['I_hi']} ({cell['I_hi_source']})")
    if cell.get("U_literal") is not None and cell["optimal"] and cell["U_literal"] < cell["Istar"]:
        viol.append(f"U_lt_Istar: U_literal={cell['U_literal']} < I*={cell['Istar']}")
    if cell.get("U") is not None and cell.get("U_literal") is not None and cell["U"] < cell["U_literal"]:
        viol.append(f"U_lt_literal: claimed {cell['U']} < literal {cell['U_literal']}")
    if cell.get("U_legal") is False and not cell.get("U_cyclic"):
        viol.append("U_illegal")
    if spec.inference:
        # the honest single-session inference must be one RU with imports = token bytes, for both L and U
        if cell["binding"] != "none":
            viol.append(f"inference_not_one_RU: binding={cell['binding']} at F_hat=1.5, G_hat=4")
        if cell.get("Istar") != cell["token_bytes"]:
            viol.append(f"inference_Istar_ne_tokens: I*={cell.get('Istar')} != token bytes {cell['token_bytes']}")
        if cell.get("U") is not None and cell["U"] != cell["token_bytes"]:
            viol.append(f"inference_U_ne_tokens: U={cell['U']} != token bytes {cell['token_bytes']} (planner)")
        if L is not None and L != cell["token_bytes"]:
            viol.append(f"inference_L_ne_tokens: L={L} != token bytes {cell['token_bytes']} (certificate)")
    cell["violations"] = viol
    ref = cell["Istar"] if cell["optimal"] else cell["I_hi"]
    cell["ref"] = ref
    cell["L_verdict"] = ("VIOLATION" if any(v.startswith("L_gt") for v in viol) else
                         "exact" if cell["optimal"] else
                         "proved (L <= I_lo)" if (L is not None and L <= cell["I_lo"]) else
                         "consistent (I_lo < L <= I_hi), not proved" if L is not None else "L unavailable")
    cell["L_over_ref"] = (L / ref) if (L is not None and ref) else None
    cell["U_over_ref"] = (cell["U"] / ref) if (cell.get("U") is not None and ref and not cell.get("U_cyclic")) else None
    cell["U_over_L"] = (cell["U"] / L) if (cell.get("U") is not None and L) else None
    cell["I_hi_over_I_lo"] = (cell["I_hi"] / cell["I_lo"]) if (cell.get("I_hi") and cell["I_lo"]) else None
    for k in ("L", "U", "I_lo", "I_hi", "Istar"):
        cell[f"{k}_per_token"] = (cell[k] / tokens) if cell.get(k) is not None else None
    cell["seconds"] = time.perf_counter() - t0
    if verbose:
        print(f"{cell['circuit']} {label}: F={F} G={G} bind={cell['binding']} I*={cell['Istar']} [{cell['I_lo']}, {cell['I_hi']}] "
              f"L={L} U={cell.get('U')} U/ref={cell['U_over_ref']} {viol} ({cell['seconds']:.0f}s, {flat.n_gates} gates)", flush=True)
    return cell


# ---------------------------------------------------------------------------------------------------------
# fits (steady-state marginal)
# ---------------------------------------------------------------------------------------------------------

def _fit(points: list[tuple[float, float]]) -> Optional[dict]:
    """Least squares ``y ~ a + r x`` over >= 2 points; returns ``{a, r, n, resid_max}``."""
    if len(points) < 2:
        return None
    n = len(points)
    mx = sum(x for x, _ in points) / n
    my = sum(y for _, y in points) / n
    sxx = sum((x - mx) ** 2 for x, _ in points)
    if sxx == 0:
        return None
    r = sum((x - mx) * (y - my) for x, y in points) / sxx
    a = my - r * mx
    resid = max(abs(y - (a + r * x)) for x, y in points)
    return {"a": a, "r": r, "n": n, "resid_max": resid, "Q": [x for x, _ in points]}


def fits(rows: list[dict]) -> list[dict]:
    """Per ``(model, circuit, Q_inf, regime)``: fit ``I_lo``, ``I_hi``/``I*``, ``L``, ``U`` over the binding
    points (``Q_roll`` beyond the single-RU range) and check ``r_L <= r_hi`` and ``r_lo <= r_U``."""
    groups: dict[tuple, list[dict]] = {}
    for r in rows:
        if r.get("inference") or "error" in r:
            continue
        groups.setdefault((r["model"], r["algorithm"], r["Q_inf"], r["regime"]), []).append(r)
    out = []
    for key, rs in sorted(groups.items()):
        rs.sort(key=lambda r: r["Q_roll"])
        steady = [r for r in rs if r["binding"] != "none"]
        pts = lambda k: [(r["Q_roll"], r[k]) for r in steady if r.get(k) is not None]   # noqa: E731
        best = [(r["Q_roll"], r["Istar"] if r["optimal"] else r["I_hi"]) for r in steady if (r["Istar"] if r["optimal"] else r.get("I_hi")) is not None]
        f = {"model": key[0], "circuit": key[1], "Q_inf": key[2], "regime": key[3], "P": rs[0]["P"], "fwd": rs[0]["fwd"],
             "Q_all": [r["Q_roll"] for r in rs], "Q_steady": [r["Q_roll"] for r in steady],
             "fit_I_lo": _fit(pts("I_lo")), "fit_I_hi": _fit(best), "fit_L": _fit(pts("L")), "fit_U": _fit(pts("U"))}
        rl, ru = f["fit_L"], f["fit_U"]
        lo, hi = f["fit_I_lo"], f["fit_I_hi"]
        f["r_L"] = rl["r"] if rl else None
        f["r_U"] = ru["r"] if ru else None
        f["r_lo"] = lo["r"] if lo else None
        f["r_hi"] = hi["r"] if hi else None
        f["check_rL_le_rhi"] = None if (rl is None or hi is None) else bool(rl["r"] <= hi["r"] + 1e-9)
        f["check_rlo_le_rU"] = None if (lo is None or ru is None) else bool(lo["r"] <= ru["r"] + 1e-9)
        f["all_L_le_ref"] = all((r.get("L") is None) or (r.get("ref") is None) or r["L"] <= r["ref"] for r in rs)
        out.append(f)
    return out


# ---------------------------------------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------------------------------------

def run_parallel(jobs: int, budget_s: float, verbose: bool, only: Optional[list[tuple[int, int, int]]] = None,
                 reuse_brackets: bool = False) -> list[dict]:
    cells = only if only is not None else all_cells()
    tmp = "/tmp/redteam/rollout_scale"
    os.makedirs(tmp, exist_ok=True)
    procs: list[tuple[tuple[int, int, int], subprocess.Popen, str, float]] = []
    rows: list[dict] = []
    # big graphs first so the tail is short
    def size(c):
        s = specs()[c[0]]
        return -(s.mults[c[1]] * s.Q_inf)
    pending = sorted(cells, key=size)
    cap = budget_s * 4 + 600

    def launch(c):
        out = os.path.join(tmp, f"cell_{c[0]}_{c[1]}_{c[2]}.json")
        if os.path.exists(out):
            os.remove(out)
        p = subprocess.Popen([sys.executable, "-m", "accumulation.redteam.rollout_scale", "--cell", str(c[0]), str(c[1]), str(c[2]),
                              "--budget", str(budget_s), "--out-json", out] + (["--quiet"] if not verbose else [])
                             + (["--reuse-brackets"] if reuse_brackets else []),
                             cwd=os.path.dirname(HERE))
        procs.append((c, p, out, time.perf_counter()))

    def heavy(c) -> bool:                       # ~1.4 GB of reachability bitsets: never two at once
        s = specs()[c[0]]
        return s.mults[c[1]] * s.Q_inf >= 64

    retried: set = set()
    while pending or procs:
        while pending and len(procs) < jobs:
            nxt = pending[0]
            if nxt in retried and procs:
                break                                # retries run alone
            if heavy(nxt) and any(heavy(c) for c, *_ in procs):
                light = next((i for i, c in enumerate(pending) if not heavy(c)), None)
                if light is None:
                    break
                nxt = pending[light]
            pending.remove(nxt)
            launch(nxt)
        time.sleep(0.5)
        for item in list(procs):
            c, p, out, t0 = item
            if p.poll() is None:
                if time.perf_counter() - t0 > cap:
                    p.kill()
                    p.wait()
                    s = specs()[c[0]]
                    procs.remove(item)
                    rows.append(dict(circuit=s.name(s.mults[c[1]] * s.Q_inf), regime=s.regimes[c[2]][0],
                                     error=f"worker wall-clock cap {cap:.0f}s", violations=[]))
                continue
            procs.remove(item)
            if os.path.exists(out):
                with open(out) as f:
                    rows.append(json.load(f))
            elif p.returncode == -9 and c not in retried:
                retried.add(c)                       # SIGKILL under memory pressure: retry once, alone, at the end
                pending.append(c)
            else:
                s = specs()[c[0]]
                rows.append(dict(circuit=s.name(s.mults[c[1]] * s.Q_inf), regime=s.regimes[c[2]][0],
                                 error=f"worker exit {p.returncode}", violations=[]))
    rows.sort(key=lambda r: (r.get("model", ""), r.get("algorithm", ""), r.get("Q_inf", 0), r.get("Q_roll", 0), r.get("regime", "")))
    return rows


def _f(v, nd=2) -> str:
    if v is None:
        return "-"
    return f"{v:.{nd}f}" if isinstance(v, float) else str(v)


def render_md(doc: dict) -> str:
    m, rows, fts = doc["meta"], doc["rows"], doc["fits"]
    good = [r for r in rows if "error" not in r]
    viol = [r for r in good if r.get("violations")]
    L = ["# Dynamic-rollout validation on registry circuits (tiny2 dense, tiny-moe MoE; `X = inf`, acyclic RU quotient)", ""]
    L.append(f"Generated {m['generated']}; `bounds/lower_coarse.py` sha1 `{m['lower_coarse_sha1']}`, `bounds/coarse.py` sha1 "
             f"`{m['coarse_sha1']}`, `bounds/lower.py` sha1 `{m['lower_sha1']}`; module sha256[:10] {m['versions']}.")
    L.append("")
    L.append("Cells are the sweeps' rollout cells at exact-solver scale: `F = F_hat * fwd(Q_inf)`, `G = G_hat * fwd(Q_inf)` "
             "(`fwd` = checker work of the inference graph at `tokens = seq = Q_inf`, as `sweeps.calibration`), rollout of "
             "`Q_roll` tokens in `Q_roll / Q_inf` sequences with dynamic (accumulated) weights.  `I*` is exact where the single RU "
             "is legal; elsewhere `[I_lo, I_hi]` brackets it (`I_lo` = read charged roots + tokens, `I_hi` = cheapest legal partition "
             "constructed: planner plans at `G`, `G/2`, `G/4` and per-op seeds, greedily merged; every candidate re-checked with "
             "`is_legal` under the acyclic quotient).  `ref` = `I*` or `I_hi`.  `L > I_hi` is a soundness violation.  The true exact "
             "`I*` for these shapes lives in the micro analogues (`exact.micro.dense_rollout` / `moe_rollout`, in `validation.md`).")
    L.append("")
    L.append(f"- cells: {len(good)} ({len(rows) - len(good)} errors); exact (single RU legal): {sum(1 for r in good if r.get('optimal'))}; "
             f"bracketed: {sum(1 for r in good if not r.get('optimal') and r.get('I_hi') is not None)}; "
             f"**violations: {len(viol)}** (`L > I_hi` {sum(1 for r in viol if any(v.startswith('L_gt') for v in r['violations']))}, "
             f"`U < I*` {sum(1 for r in viol if any(v.startswith('U_lt') for v in r['violations']))}, "
             f"inference-not-tokens {sum(1 for r in viol if any(v.startswith('inference') for v in r['violations']))}).")
    dflt = [r for r in good if r.get("default_point") and not r.get("inference")]
    for alg in sorted({r["algorithm"] for r in dflt}):
        rs = [r for r in dflt if r["algorithm"] == alg and r.get("ref")]
        ur = sorted(r["U_over_ref"] for r in rs if r.get("U_over_ref") is not None)
        lr = sorted(r["L_over_ref"] for r in rs if r.get("L_over_ref") is not None)
        ul = sorted(r["U_over_L"] for r in rs if r.get("U_over_L") is not None)
        L.append(f"- `{alg}` at the default point: U/ref median {_f(ur[len(ur)//2]) if ur else '-'} max {_f(ur[-1]) if ur else '-'}; "
                 f"L/ref median {_f(lr[len(lr)//2]) if lr else '-'} min {_f(lr[0]) if lr else '-'}; U/L max {_f(ul[-1]) if ul else '-'} (n={len(rs)}).")
    L.append("")
    L.append("| circuit | Q_inf | Q_roll | seq | gates | regime | F | G | binds | I* / [I_lo, I_hi] | L | U (lit) | L/ref | U/ref | U/L | I_hi/I_lo | block? | L per tok | U per tok | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        if "error" in r:
            L.append(f"| {r['circuit']} | | | | | {r['regime']} | | | | ERROR {r['error']} | | | | | | | | | | |")
            continue
        istar = str(r["Istar"]) if r.get("optimal") else f"[{r['I_lo']}, {_f(r['I_hi'])}]"
        u = f"{_f(r.get('U'))}" + ("" if r.get("U_literal") in (None, r.get("U")) else f" ({r['U_literal']})") + (
            " CYCLIC" if r.get("U_cyclic") else "" if r.get("U_legal") in (None, True) else " ILLEGAL")
        if r.get("U") is None and r.get("U_error"):
            u = f"- ({r['U_error'][:50]})"
        L.append(f"| {r['circuit']} | {r['Q_inf']} | {r['Q_roll']} | {r['seq']} | {r['gates']} | {r['regime']} | {_f(r['F'])} | {_f(r['G'])} | {r['binding']} | {istar} | "
                 f"{_f(r.get('L'))} | {u} | {_f(r.get('L_over_ref'))} | {_f(r.get('U_over_ref'))} | {_f(r.get('U_over_L'))} | {_f(r.get('I_hi_over_I_lo'))} | "
                 f"{'yes' if r.get('block_term_fired') else 'no'} | {_f(r.get('L_per_token'))} | {_f(r.get('U_per_token'))} | "
                 f"{r.get('L_verdict', '')}{'; ' + '; '.join(r['violations']) if r.get('violations') else ''} |")
    L.append("")
    L.append("## Steady-state marginal fits (`X(Q) ~ a + r Q` over the binding points)")
    L.append("")
    L.append("`r_lo` / `r_hi` from `I_lo` / `I_hi` (or `I*`), `r_L` / `r_U` from the coarse bounds at the same `Q`.  Sound iff "
             "`r_L <= r_hi` and `r_lo <= r_U` (the marginal is bracketed, not just the totals).  Bytes per rollout token.")
    L.append("")
    L.append("| circuit | Q_inf | regime | Q (steady) | P | r_lo | r_hi | r_L | r_U | r_L <= r_hi | r_lo <= r_U | a_L (one-time) | a_U |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for f in fts:
        aL = f["fit_L"]["a"] if f["fit_L"] else None
        aU = f["fit_U"]["a"] if f["fit_U"] else None
        L.append(f"| {f['circuit']}[{f['model']}] | {f['Q_inf']} | {f['regime']} | {f['Q_steady']} | {f['P']} | {_f(f['r_lo'])} | {_f(f['r_hi'])} | "
                 f"{_f(f['r_L'])} | {_f(f['r_U'])} | {f['check_rL_le_rhi']} | {f['check_rlo_le_rU']} | {_f(aL)} | {_f(aU)} |")
    L.append("")
    if viol:
        L.append("## Violations")
        L.append("")
        for r in viol:
            L.append(f"- **{r['circuit']}** *{r['regime']}* (F={r['F']}, G={r['G']}): {'; '.join(r['violations'])}")
            b = r.get("L_breakdown") or {}
            if b:
                L.append(f"  - L breakdown: tokens {b.get('token_seed')}, root {b.get('root_bytes')}, block {b.get('block_bytes')}, "
                         f"weight_floor {b.get('weight_floor_bytes')}, cap {b.get('cap')}, notes {[str(n)[:120] for n in b.get('notes', [])[:4]]}")
            for ru in (r.get("partition") or [])[:24]:
                if "note" in ru:
                    L.append(f"  - {ru['note']}"); continue
                ops = ", ".join(f"{k} x{v}" for k, v in list(ru["ops"].items())[:12])
                imps = ", ".join(f"{k}={v}B" for k, v in list(ru["imports"].items())[:12]) + (" …" if len(ru["imports"]) > 12 else "")
                L.append(f"  - RU{ru['ru']}: work {ru['work']}, input {ru['in_bytes']} B; ops [{ops[:240]}]; crossing in: {imps}")
        L.append("")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", nargs=3, type=int, help="(spec, mult index, regime index): run one cell (worker mode)")
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--budget", type=float, default=240.0, help="heuristic budget per cell (s)")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--max-tokens", type=int, default=None, help="skip cells with Q_roll above this")
    ap.add_argument("--reuse-brackets", action="store_true",
                    help="reuse [I_lo, I_hi] from the previous results/rollout_scale.json; recompute L and U only (bound modules changed)")
    a = ap.parse_args(argv)
    if a.cell:
        s = specs()[a.cell[0]]
        Q_roll = s.mults[a.cell[1]] * s.Q_inf
        prev = previous_rows(os.path.join(a.out_dir, "rollout_scale.json")).get((s.name(Q_roll), s.regimes[a.cell[2]][0])) if a.reuse_brackets else None
        row = run_cell(s, Q_roll, s.regimes[a.cell[2]], budget_s=a.budget, verbose=not a.quiet, prev=prev)
        if a.out_json:
            with open(a.out_json, "w") as f:
                json.dump(row, f, default=str)
        return 0
    from accumulation.redteam.coarse_validation import lower_sha1
    cells = all_cells()
    if a.max_tokens is not None:
        cells = [c for c in cells if specs()[c[0]].mults[c[1]] * specs()[c[0]].Q_inf <= a.max_tokens]
    meta = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "lower_sha1": lower_sha1(), "lower_coarse_sha1": lower_sha1("lower_coarse.py"),
            "coarse_sha1": lower_sha1("coarse.py"), "versions": _versions(), "budget_s": a.budget, "legality": "acyclic RU quotient (SPEC §0)",
            "policy": "F = F_hat * fwd(Q_inf), G = G_hat * fwd(Q_inf); fwd = adw(inference graph at tokens = seq = Q_inf).all_work"}
    if a.reuse_brackets:
        # snapshot: workers read the previous file while the driver will overwrite it at the end
        import shutil
        src = os.path.join(a.out_dir, "rollout_scale.json")
        if os.path.exists(src):
            shutil.copy(src, src + ".prev")
    rows = run_parallel(a.jobs, a.budget, not a.quiet, only=cells, reuse_brackets=a.reuse_brackets)
    meta["lower_coarse_sha1_after"] = lower_sha1("lower_coarse.py")
    meta["coarse_sha1_after"] = lower_sha1("coarse.py")
    doc = {"meta": meta, "rows": rows, "fits": fits(rows)}
    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "rollout_scale.json"), "w") as f:
        json.dump(doc, f, indent=1, default=str)
    with open(os.path.join(a.out_dir, "validation_rollout.md"), "w") as f:
        f.write(render_md(doc))
    nv = sum(1 for r in rows if r.get("violations"))
    print(f"wrote {a.out_dir}/validation_rollout.md / rollout_scale.json: {len(rows)} cells, {nv} violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
