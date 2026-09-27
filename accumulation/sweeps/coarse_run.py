"""Sweep driver for the corrected policy model (no per-RU input cap): cells are
``(model, circuit, Q_inf, F_hat, G_hat, Q_step, K)``, bounds are ``bounds.coarse.upper_coarse`` (checked plan -> ``U``)
and ``bounds.lower.lower_coarse`` (certificate -> ``L``).

Policy point: ``F = F_hat * fwd(model, Q_inf)``, ``G = G_hat * fwd(model, Q_inf)`` with ``fwd`` from
``results/calibration.json`` (``calibration.py``; computed in the child when missing).

Circuits: inference (``inference-dense`` / ``inference-moe``, ``tokens = seq = Q_inf``, one session) and multi-step
training (``local-sgd`` with ``local_steps = K``, ``tokens = K * Q_step``, ``seq = Q_inf``; MoE and ES / forward-nonfixed /
RL have single-step factories only and are run with ``K = 1`` and flagged ``single_step_factory``).

One guarded child per **graph** ``(model, circuit, tokens, seq, K)``: the child builds and extracts once and evaluates
every policy point ``(F_hat, G_hat)`` requested on that graph (extraction at 405B is minutes; bounds are seconds).
The child appends finished rows to a fragment file that the parent merges into ``results/coarse.jsonl``.  RSS
watchdog (default 8 GB), wall-clock limit per child, ``--resume`` (skip complete rows), ``--redo {lower,upper,all}``.

Row: identity + ``tokens, seq, F, G, fwd_macs``; ``P`` (state bytes), ``token_bytes``; ADW (``all_macs, credited_macs,
recompute_macs, all_work``), ``M`` (= credited_macs for training, all_macs for inference); ``U`` + ``U_ru_stats`` +
``U_by_class`` + ``U_notes``; ``L`` + ``L_source, L_cap, L_state_floor, L_worst_ru, L_notes``; per token ``L_per_token,
U_per_token, M_per_token``; ``kappa_low = M/U``, ``kappa_high = M/L``; timings; module source hashes; errors.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from accumulation.sweeps.util import RESULTS_DIR, append_jsonl, read_jsonl, write_json

REPO = Path(__file__).resolve().parents[2]
OUT_FILE = "coarse.jsonl"
SPEC_DIR = Path("/tmp/accsweep/coarse")
# ~/.veritor/mem_guardian.py (the user's machine-level daemon) SIGKILLs any python process under projects/veritor above
# 2.5 GB resident; our own watchdog sits just below it so the kill is ours, classified ("oom-guard") and logged with the peak.
DEFAULT_MAX_RSS_MB = 2400.0
GUARDIAN_NOTE = "~/.veritor/mem_guardian.py kills >2.5 GB processes; cells above that are recorded as oom-guard"
INFERENCE = {"inference-dense", "inference-moe", "inference-decode", "inference-session"}
MULTISTEP_FACTORIES = {"local-sgd"}
FORWARD_ONLY = INFERENCE | {"forward-nonfixed", "forward-nonfixed-moe", "es"}    # no backward: every layer-chunk x token-chunk plan is convex by construction
DEFAULT_POLICY = {"Q_inf": 8192, "F_hat": 1.5, "G_hat": 4, "Q_step_mult": 16}
KEY = ("model", "circuit", "Q_inf", "F_hat", "G_hat", "Q_step", "K", "seq")


@dataclass(frozen=True, order=True)
class Cell:
    model: str
    circuit: str
    Q_inf: int
    F_hat: float
    G_hat: float
    Q_step: int | None   # None for inference
    K: int | None        # None for inference
    seq: int

    @property
    def tokens(self) -> int:
        return self.Q_inf if self.K is None else self.K * self.Q_step

    def graph_key(self) -> tuple:
        return (self.model, self.circuit, self.tokens, self.seq, self.K)

    def key(self) -> tuple:
        return tuple(getattr(self, k) for k in KEY)


def row_key(r: dict) -> tuple:
    return tuple(r.get(k) for k in KEY)


def cell_cost(c: Cell) -> float:
    from accumulation.sweeps.synthetic import model_cfg
    return model_cfg(c.model).total_params() * c.tokens * (1.0 if c.circuit in FORWARD_ONLY else 3.0)


def module_versions() -> dict[str, str]:
    out = {}
    for name in ("upper", "lower", "coarse", "adw"):
        p = REPO / "accumulation" / "bounds" / f"{name}.py"
        data = p.read_bytes() if p.exists() else b""
        if name == "lower":                                        # lower.py re-exports lower_coarse.py: hash both
            q = REPO / "accumulation" / "bounds" / "lower_coarse.py"
            data += q.read_bytes() if q.exists() else b""
        out[name] = hashlib.sha1(data).hexdigest()[:10] if data else "missing"
    p = REPO / "accumulation" / "graph" / "opgraph.py"
    out["extract"] = hashlib.sha1(p.read_bytes()).hexdigest()[:10]
    q = REPO / "accumulation" / "bounds" / "lower_wp.py"                # weight-presence certificate: its own stage ("wp")
    out["wp"] = hashlib.sha1(q.read_bytes()).hexdigest()[:10] if q.exists() else "missing"
    return out


def bound_symbols() -> dict[str, bool]:
    """Which coarse bound entry points exist (poll; never stub)."""
    out = {}
    try:
        from accumulation.bounds import coarse as _c  # noqa: F401
        out["upper_coarse"] = hasattr(_c, "upper_coarse")
    except Exception:  # noqa: BLE001
        out["upper_coarse"] = False
    try:
        from accumulation.bounds import lower as _l
        out["lower_coarse"] = hasattr(_l, "lower_coarse")
    except Exception:  # noqa: BLE001
        out["lower_coarse"] = False
    try:
        from accumulation.bounds import lower_wp as _w
        out["wp_coarse"] = hasattr(_w, "weight_presence_bound")
    except Exception:  # noqa: BLE001
        out["wp_coarse"] = False
    return out


# ---------------------------------------------------------------------------------------------------------
# circuits
# ---------------------------------------------------------------------------------------------------------

def circuits(model: str) -> tuple[str, str]:
    """(honest inference circuit, multi-step training circuit) -- see ``calibration.circuits_for``."""
    from accumulation.sweeps.calibration import circuits_for
    inf, tr, _ = circuits_for(model)
    return inf, tr


def make_workload(c: Cell):
    from accumulation.configs import Workload
    if c.K is None:
        return Workload(tokens=c.Q_inf, seq=c.seq)
    if c.circuit in MULTISTEP_FACTORIES:
        return Workload(tokens=c.K * c.Q_step, seq=c.seq, local_steps=c.K)
    if c.K != 1:
        raise ValueError(f"{c.circuit} has a single-step factory; K must be 1")
    return Workload(tokens=c.Q_step, seq=c.seq)


def supported(c: Cell) -> str | None:
    from accumulation.algorithms.registry import ALGORITHMS
    from accumulation.sweeps.guard import check_limits
    from accumulation.sweeps.synthetic import model_cfg
    if c.circuit not in ALGORITHMS:
        return f"unknown circuit {c.circuit}"
    try:
        wl = make_workload(c)
    except ValueError as e:
        return str(e)
    why = ALGORITHMS[c.circuit].supports(model_cfg(c.model), wl)
    if why:
        return why
    return check_limits(c.circuit, c.model, wl)


# ---------------------------------------------------------------------------------------------------------
# cell grids
# ---------------------------------------------------------------------------------------------------------

def _pts(Q_inf, F_hats, G_hats):
    return [(Q_inf, float(f), float(g)) for f in F_hats for g in G_hats]


def cells_for(model: str, points: list[tuple], Q_step_mults: tuple = (16,), Ks: tuple = (2, 3), seq: int | None = None,
              extra_train: tuple = (), prefill: bool = True) -> list[Cell]:
    inf_alg, tr_alg = circuits(model)
    out = []
    for Q_inf, fh, gh in points:
        s = seq or Q_inf
        out.append(Cell(model, inf_alg, Q_inf, fh, gh, None, None, s))
        if prefill and inf_alg == "inference-session":       # prefill-only circuit reported alongside
            out.append(Cell(model, "inference-dense", Q_inf, fh, gh, None, None, s))
        for mult in Q_step_mults:
            Q_step = mult * Q_inf
            for K in (Ks if tr_alg in MULTISTEP_FACTORIES else (1,)):
                out.append(Cell(model, tr_alg, Q_inf, fh, gh, Q_step, K, s))
            for alg in extra_train:  # single-step factories (ES, forward-nonfixed, RL, ...)
                out.append(Cell(model, alg, Q_inf, fh, gh, Q_step, 1, s))
    return out


# The sweep matrix (one axis varied at a time from the default point 8B, Q_inf = 8192, F_hat = 1.5, G_hat = 4,
# Q_step = 16 Q_inf, K = 3 (K = 2 alongside for the marginal), seq = Q_inf).
AXES = {
    "qinf": (2048, 8192, 32768, 131072),                       # 1. session length (F, G recalibrated to fwd(Q_inf))
    "ghat": (1, 3, 10, 30, 100, 1000),                          # 2. G_hat at F_hat = 1.5
    "heat_F": (1, 3, 10, 30, 100, 300, 1000),                   # 3. (F_hat, G_hat) heatmap
    "heat_G": (1, 10, 100, 1000),
    "qstep": (8192, 32768, 131072, 524288, 1048576, 4194304),   # 4. Q_step at G_hat in heat_G, K = 3 (+2)
    "ksweep": (2, 4, 8, 12, 16, 24, 32, 48, 64),                # 5. K at Q_step = 8192 (knee expected at K ~ 8-12; registry caps local_steps at 64)
    "roll_Q": (8192, 32768, 131072, 1048576),                   # 7. dynamic rollout volume (forward-nonfixed: inference graph, dynamic W)
    "roll_F": (1, 1.5, 3, 10, 30, 100),                         #    F_hat for rollout at Q_roll = 131072
    "ksweep_32k": (2, 3, 4, 6, 8),                              #    and at Q_step = 32768
    "scale": ("llama3-1b", "llama3-8b", "llama3-70b", "llama3-405b"),   # 6. scale at the default point
    "moe": ("mixtral-8x7b", "qwen3-235b-a22b", "deepseek-v3"),
}
SYN_MODELS = ("syn-base", "syn-wide", "syn-deep", "syn-ffn", "syn-attn", "syn-manyheads")


HEAVY_MODELS = ("llama3-70b", "llama3-405b", "mixtral-8x7b", "qwen3-235b-a22b", "deepseek-v3")


def too_heavy(c: Cell) -> bool:
    """Cells that cannot run under the machine guardian's 2.5 GB cap: training of the 70B+/MoE models, 8B training above
    ~140k tokens (Q_step >= 131072 with K >= 2), training at Q_inf = 131072 -- marked ``status = 'pod'`` and filled from
    the analytic model in the reports."""
    if c.circuit in INFERENCE:
        return c.model in HEAVY_MODELS and c.Q_inf > 32768
    if c.model in HEAVY_MODELS:
        return True
    if c.Q_inf >= 131072:
        return True
    return c.tokens > 140000 and c.model != "llama3-1b" or c.tokens > 400000


def preset_cells(name: str) -> list[Cell]:
    d = DEFAULT_POLICY
    Q, Fh, Gh = d["Q_inf"], float(d["F_hat"]), float(d["G_hat"])
    Qs = d["Q_step_mult"] * Q
    dp = [(Q, Fh, Gh)]
    if name == "smoke":
        return cells_for("tiny2", [(8, 1.5, 4.0)], Q_step_mults=(2,), Ks=(1, 2, 3), seq=8) + cells_for("tiny-moe", [(8, 1.5, 4.0)], Q_step_mults=(2,), seq=8)
    if name == "smoke-1b":
        return cells_for("llama3-1b", [(1024, 1.5, 4.0)], Q_step_mults=(2,), Ks=(2, 3), seq=1024)
    if name == "default-8b":          # the default point itself (first measured 8B point)
        return cells_for("llama3-8b", dp, Q_step_mults=(d["Q_step_mult"],), Ks=(2, 3))
    if name == "qinf":                # 1. session length; seq = Q_inf for training too
        return [c for q in AXES["qinf"] for c in cells_for("llama3-8b", [(q, Fh, Gh)], Q_step_mults=(d["Q_step_mult"],), Ks=(2, 3))]
    if name == "qinf-1b":             # fallback for Q_inf = 131072 when 8B does not fit
        return [c for q in AXES["qinf"] for c in cells_for("llama3-1b", [(q, Fh, Gh)], Q_step_mults=(d["Q_step_mult"],), Ks=(2, 3))]
    if name == "ghat":                # 2. G_hat sweep at F_hat = 1.5
        return cells_for("llama3-8b", [(Q, Fh, float(g)) for g in AXES["ghat"]], Q_step_mults=(d["Q_step_mult"],), Ks=(2, 3))
    if name == "heatmap":             # 3. (F_hat, G_hat)
        return cells_for("llama3-8b", _pts(Q, AXES["heat_F"], AXES["heat_G"]), Q_step_mults=(d["Q_step_mult"],), Ks=(2, 3))
    if name == "qstep":               # 4. Q_step x G_hat, K = 2, 3
        out = []
        for g in AXES["heat_G"]:
            for qs in AXES["qstep"]:
                out += [c for c in cells_for("llama3-8b", [(Q, Fh, float(g))], Q_step_mults=(qs // Q,), Ks=(2, 3)) if c.K is not None]
        out += cells_for("llama3-8b", [(Q, Fh, float(g)) for g in AXES["heat_G"]], Q_step_mults=(), Ks=())   # inference at each G_hat
        return out
    if name == "qstep-k2":            # fallback when K = 3 at 4M does not fit in 8 GB
        return [c for c in preset_cells("qstep") if c.K != 3]
    if name == "ksweep":              # 5. K at Q_step = 8192 and 32768 (past the transient knee)
        out = cells_for("llama3-8b", dp, Q_step_mults=(1,), Ks=AXES["ksweep"])
        out += [c for c in cells_for("llama3-8b", dp, Q_step_mults=(4,), Ks=AXES["ksweep_32k"]) if c.K is not None]
        return out
    if name == "ksweep-1b":
        out = cells_for("llama3-1b", dp, Q_step_mults=(1,), Ks=AXES["ksweep"])
        out += [c for c in cells_for("llama3-1b", dp, Q_step_mults=(4,), Ks=AXES["ksweep_32k"]) if c.K is not None]
        return out
    if name == "qstep-1b":            # 4b. larger Q_step at 1B (8B cells above 140k tokens go to the pod)
        out = []
        for g in AXES["heat_G"]:
            for qs in AXES["qstep"]:
                out += [c for c in cells_for("llama3-1b", [(Q, Fh, float(g))], Q_step_mults=(qs // Q,), Ks=(2, 3)) if c.K is not None]
        out += cells_for("llama3-1b", [(Q, Fh, float(g)) for g in AXES["heat_G"]], Q_step_mults=(), Ks=())
        return out
    if name == "scale":               # 6. dense scale at the default point (405B: K = 2 alongside K = 3, drop 3 if too heavy)
        return [c for m in AXES["scale"] for c in cells_for(m, dp, Q_step_mults=(d["Q_step_mult"],), Ks=(2, 3))]
    if name == "scale-405b-k2":
        return [c for c in cells_for("llama3-405b", dp, Q_step_mults=(d["Q_step_mult"],), Ks=(2,))]
    if name == "moe":                 # 6b. MoE (single-step pretrain-moe) at the default point
        return [c for m in AXES["moe"] for c in cells_for(m, dp, Q_step_mults=(d["Q_step_mult"],))]
    if name == "synthetic":           # 6c. architecture family at ~fixed P
        return [c for m in SYN_MODELS for c in cells_for(m, dp, Q_step_mults=(d["Q_step_mult"],), Ks=(2, 3))]
    if name == "others-8b":           # single-step factories at 8B, flagged in the report
        return [c for c in cells_for("llama3-8b", dp, Q_step_mults=(d["Q_step_mult"],), Ks=(),
                                     extra_train=("es", "forward-nonfixed", "rl-policy-gradient", "pretrain-dense", "lora"))
                if c.circuit not in INFERENCE]
    if name == "rollout":             # 7. dynamic rollout generation: the inference forward graph with dynamic (accumulated) weights,
        out = []                      #    same useful MACs/token as inference -> penalty = (U/Q) / (4 B/token) directly
        for m in AXES["scale"]:
            for q in AXES["roll_Q"]:
                out.append(Cell(m, "forward-nonfixed", Q, Fh, Gh, q, 1, min(q, Q)))
        for f in AXES["roll_F"]:      # policy knob at 8B, Q_roll = 131072
            out.append(Cell("llama3-8b", "forward-nonfixed", Q, float(f), Gh, 131072, 1, Q))
        for q in AXES["qinf"]:        # allowed session length at 8B, Q_roll = 131072 (F, G recalibrated to fwd(Q_inf))
            out.append(Cell("llama3-8b", "forward-nonfixed", q, Fh, Gh, 131072, 1, min(q, 131072)))
        return sorted(set(out))
    if name == "rollout-p0":          # ROLLOUT_PLAN P0/P1: dense + MoE dynamic rollout, Q_roll 8K..1M (+4M), default point
        out = []                      #    4M only where a cell finishes in < ~1.5 h on the pod (1B / 8B / 70B); 405B + MoE 4M: preset rollout-4m
        for m in AXES["scale"]:
            for q in AXES["roll_Q"] + ((4194304,) if m != "llama3-405b" else ()):
                out.append(Cell(m, "forward-nonfixed", Q, Fh, Gh, q, 1, min(q, Q)))
        for m in AXES["moe"]:
            out.append(Cell(m, "inference-moe", Q, Fh, Gh, None, None, Q))                       # fixed-weight reference
            for q in AXES["roll_Q"]:
                out.append(Cell(m, "forward-nonfixed-moe", Q, Fh, Gh, q, 1, min(q, Q)))
        return sorted(set(out))
    if name == "rollout-4m":          # the slow 4M cells (hours each): 405B dense + the three MoE models
        out = [Cell("llama3-405b", "forward-nonfixed", Q, Fh, Gh, 4194304, 1, Q)]
        for m in AXES["moe"]:
            out.append(Cell(m, "forward-nonfixed-moe", Q, Fh, Gh, 4194304, 1, Q))
        return sorted(set(out))
    if name == "rollout-p4":          # ROLLOUT_PLAN P4: robustness of 8B rollout at Q_roll = 1M
        out = []
        for q in AXES["qinf"]:
            out.append(Cell("llama3-8b", "forward-nonfixed", q, Fh, Gh, 1048576, 1, q))
        for f in (3.0, 10.0):
            out.append(Cell("llama3-8b", "forward-nonfixed", Q, f, Gh, 1048576, 1, Q))
        for g in (10.0, 1000.0):
            out.append(Cell("llama3-8b", "forward-nonfixed", Q, Fh, g, 1048576, 1, Q))
        return sorted(set(out))
    if name == "headline":            # the cells Table 1 / mandatory Table 2 rows need (the certified-L pass on the pod runs over these)
        out = preset_cells("scale") + preset_cells("ksweep") + preset_cells("moe")
        for qs in AXES["qstep"]:      # Q_step axis at the default G_hat only
            out += [c for c in cells_for("llama3-8b", dp, Q_step_mults=(qs // Q,), Ks=(2, 3)) if c.K is not None]
        out += preset_cells("rollout-p0") + preset_cells("rollout-p4")
        return sorted(set(out))
    if name == "all":
        out = []
        for n in ("default-8b", "qinf", "qinf-1b", "ghat", "heatmap", "qstep", "qstep-1b", "ksweep", "ksweep-1b", "scale", "moe", "synthetic",
                  "others-8b", "rollout", "rollout-p0", "rollout-p4", "rollout-4m"):
            out += preset_cells(n)
        return out
    raise SystemExit(f"unknown preset {name}")


# ---------------------------------------------------------------------------------------------------------
# rows
# ---------------------------------------------------------------------------------------------------------

def new_row(c: Cell) -> dict:
    r = {k: getattr(c, k) for k in KEY}
    r.update(tokens=c.tokens, is_training=c.circuit not in INFERENCE, single_step_factory=(c.K is not None and c.circuit not in MULTISTEP_FACTORIES),
             F=None, G=None, fwd_macs=None, fwd_units=None, status=None, P=None, token_bytes=None, all_macs=None, credited_macs=None, recompute_macs=None,
             all_work=None, M=None, U=None, L=None, error=None, lower_error=None, upper_error=None, versions=None)
    return r


def combine_lower(r: dict) -> dict:
    """``L = max(L_coarse, L_root_read + token_bytes + L_wp)``: the coarse certificate and the weight-presence
    certificate (``bounds/lower_wp.py``) are both sound lower bounds; the second is additive with the root floor
    (step-0 roots and tokens read at least once) because it counts disjoint values (chained step-k weights).
    ``L_coarse`` keeps the raw coarse value (rows from before the wp stage: ``L`` itself)."""
    if r.get("L") is not None and r.get("L_coarse") is None and r.get("L_from_wp") is None:
        r["L_coarse"] = r["L"]                       # legacy row (never combined): its L *is* the coarse certificate
    if r.get("L_wp") is None:
        return r
    if r.get("L_coarse") is not None and not (r.get("stage_versions") or {}).get("lower"):
        r["L_coarse"] = None                         # a coarse certificate always carries its lower stamp: this was the wp floor echoed back
    floor = (r.get("L_root_read") or 0) + (r.get("token_bytes") or 0) + r["L_wp"]
    base = r.get("L_coarse")
    r["L"] = max(base, floor) if base is not None else (floor if r["L_wp"] else None)
    r["L_from_wp"] = bool(r["L"] is not None and (base is None or r["L"] > base))
    return r


def coarse_L(r: dict | None) -> int | None:
    """The coarse certificate of a row (``None`` when only the wp floor is present); legacy rows carry it as ``L``."""
    if not r:
        return None
    if r.get("L_coarse") is not None:
        return r["L_coarse"]
    return None if r.get("L_from_wp") else r.get("L")


def finalize_row(r: dict) -> dict:
    combine_lower(r)
    Q = r.get("tokens") or 1
    for k in ("L", "U", "M"):
        r[f"{k}_per_token"] = (r[k] / Q) if r.get(k) is not None else None
    r["kappa_low"] = (r["M"] / r["U"]) if (r.get("M") is not None and r.get("U")) else None
    r["kappa_high"] = (r["M"] / r["L"]) if (r.get("M") is not None and r.get("L")) else None
    r["U_over_L"] = (r["U"] / r["L"]) if (r.get("U") is not None and r.get("L")) else None
    if r.get("U") is not None and r.get("L") is not None:
        r["soundness_violation"] = f"U={r['U']} < L={r['L']}" if r["U"] < r["L"] else None
    r["complete"] = r.get("U") is not None and r.get("L") is not None and not r.get("error")
    return r


def _call(fn, g, F, G, **opt):
    """Call a bound with the keyword arguments it accepts."""
    params = inspect.signature(fn).parameters
    kw = {k: v for k, v in opt.items() if k in params}
    if "X" in params and "X" not in kw:
        kw["X"] = 1 << 62
    return fn(g, F, G, **kw) if list(params)[1:3] == ["F", "G"] else fn(g, F=F, G=G, **kw)


def eval_graph(cells: list[Cell], stages: set[str], out_frag: Path, *, fwd_macs: float | None, log=print) -> None:
    """Child body: one graph, all its policy points."""
    from accumulation.algorithms.registry import build
    from accumulation.bounds.adw import adw as compute_adw
    from accumulation.graph import extract
    from accumulation.sweeps.synthetic import model_cfg
    c0 = cells[0]
    cfg = model_cfg(c0.model)
    vers = module_versions()
    t0 = time.perf_counter()
    bp = build(c0.circuit, cfg, make_workload(c0))
    g = extract(bp)
    a = compute_adw(g)
    extract_s = time.perf_counter() - t0
    log(f"[child] {c0.model} {c0.circuit} tokens={c0.tokens} seq={c0.seq} K={c0.K}: {len(g.ops)} ops extracted in {extract_s:.1f}s; "
        f"all_macs={a.all_macs:.3e} credited={a.credited_macs:.3e}")
    if fwd_macs is None:      # fwd := checker Work (all ops) of the calibration circuit (inference-dense / inference-moe) at Q_inf
        from accumulation.sweeps.calibration import calibration_alg
        cal_alg = calibration_alg(c0.model)
        if c0.circuit == cal_alg and c0.tokens == c0.Q_inf:
            fwd_macs = a.all_work
        else:
            from accumulation.configs import Workload
            fwd_macs = compute_adw(extract(build(cal_alg, cfg, Workload(tokens=c0.Q_inf, seq=c0.Q_inf)))).all_work
    try:
        from accumulation.bounds import coarse as coarse_mod
    except Exception as e:  # noqa: BLE001
        coarse_mod = None
        coarse_err = f"{type(e).__name__}: {e}"
    from accumulation.bounds import lower as lower_mod
    for c in cells:
        r = new_row(c)
        r.update(F=int(round(c.F_hat * fwd_macs)), G=int(round(c.G_hat * fwd_macs)), fwd_macs=fwd_macs, fwd_units="work", P=bp.state_bytes(),
                 token_bytes=bp.param_bytes("token"), all_macs=a.all_macs, credited_macs=a.credited_macs, recompute_macs=a.recompute_macs,
                 all_work=a.all_work, M=(a.all_macs if c.circuit in INFERENCE else a.credited_macs), extract_s=extract_s, n_ops=len(g.ops),
                 versions=vers)
        F, G = r["F"], r["G"]
        if "upper" in stages:
            t1 = time.perf_counter()
            try:
                if coarse_mod is None or not hasattr(coarse_mod, "upper_coarse"):
                    raise RuntimeError("bounds.coarse.upper_coarse not available" + (f" ({coarse_err})" if coarse_mod is None else ""))
                res = _call(coarse_mod.upper_coarse, g, F, G, program=bp.program, workload=make_workload(c), adw=a, bp=bp)
                plan = getattr(res, "plan", res)
                detail = dict(getattr(plan, "detail", {}) or {})
                if not detail.get("checked"):                      # planner did not re-check: run the trustworthy checker
                    checker = getattr(coarse_mod, "check_coarse_plan", None)
                    if checker is not None:
                        checker(g, plan, F, G, program=bp.program)
                        detail = dict(getattr(plan, "detail", {}) or {})
                r["U_checked"] = bool(detail.get("checked"))
                r["U"] = int(getattr(plan, "total", getattr(res, "total")))
                r["U_ru_stats"] = plan.ru_stats() if hasattr(plan, "ru_stats") else None
                bc = getattr(plan, "by_class", None) or getattr(res, "by_class", None)
                r["U_by_class"] = dict(bc) if bc else None
                r["U_notes"] = list(getattr(plan, "notes", []) or [])[:20]
                r["U_n_ru"] = (r["U_ru_stats"] or {}).get("n_ru")
                r["U_units"] = [{"label": u.label, "imports": u.imports_total, "work": u.work_max, "up": u.up_max}
                                for u in list(getattr(plan, "units", []))[:12]]
                r["U_detail"] = _jsonable({k: v for k, v in detail.items() if k != "checked"}) or None
            except Exception as e:  # noqa: BLE001
                r["upper_error"] = f"{type(e).__name__}: {str(e)[:300]}"
            r["upper_s"] = time.perf_counter() - t1
        if "lower" in stages:
            t1 = time.perf_counter()
            try:
                if not hasattr(lower_mod, "lower_coarse"):
                    raise RuntimeError("bounds.lower.lower_coarse not available")
                lb = _call(lower_mod.lower_coarse, g, F, G, program=bp.program, adw=a, workload=make_workload(c), bp=bp)
                r["L"] = r["L_coarse"] = int(lb.total)
                for k in ("source", "cap", "state_floor", "token_seed", "infeasible", "by_class",
                          "gap", "root_read", "recurring", "certified"):   # gap: MILP dual gap (0 = proven optimal LP/closed form)
                    if hasattr(lb, k):
                        r[f"L_{k}"] = _jsonable(getattr(lb, k))
                if getattr(lb, "detail", None):
                    r["L_detail"] = _jsonable(dict(lb.detail)) or None
                r["L_worst_ru"] = _jsonable(getattr(lb, "worst_ru", None))
                r["L_notes"] = list(getattr(lb, "notes", []) or [])[:20]
            except Exception as e:  # noqa: BLE001
                r["lower_error"] = f"{type(e).__name__}: {str(e)[:300]}"
            r["lower_s"] = time.perf_counter() - t1
        if "wp" in stages:                  # weight-presence certificate (chained step-k weights); cheap, graph-level
            t1 = time.perf_counter()
            try:
                from accumulation.bounds.lower_wp import weight_presence_bound
                wp = weight_presence_bound(g, F, G, program=bp.program)
                r["L_wp"] = int(wp.total)
                r["L_wp_detail"] = _jsonable({"n_candidates": wp.n_candidates, "n_forced": wp.n_forced, "binds": wp.binds,
                                              "by_producer_step": wp.by_producer_step, "notes": wp.notes, "forced": wp.forced[:8]})
            except Exception as e:  # noqa: BLE001
                r["wp_error"] = f"{type(e).__name__}: {str(e)[:300]}"
            r["wp_s"] = time.perf_counter() - t1
        # per-stage provenance: which bounds/{lower,coarse,upper,lower_wp}.py produced this row's L / U / L_wp (kept per stage across merges)
        r["stage_versions"] = {**({"lower": vers["lower"]} if "lower" in stages else {}),
                               **({"upper": vers["upper"], "coarse": vers["coarse"]} if "upper" in stages else {}),
                               **({"wp": vers["wp"]} if "wp" in stages and r.get("L_wp") is not None else {})}
        r["row_ts"] = time.time()                                # producer time: newest row wins in cross-file merges
        finalize_row(r)
        append_jsonl(out_frag, r)
        upt = "-" if r.get("U_per_token") is None else f"{r['U_per_token']:.3g}"
        lpt = "-" if r.get("L_per_token") is None else f"{r['L_per_token']:.3g}"
        wpt = "" if r.get("L_wp") is None else f" L_wp={r['L_wp']}"
        log(f"[child]   F_hat={c.F_hat:g} G_hat={c.G_hat:g}: U={r.get('U')} L={r.get('L')}{wpt} ({upt} / {lpt} B/tok) "
            f"{r.get('upper_error') or ''} {r.get('lower_error') or ''} {r.get('wp_error') or ''}")


def _jsonable(x):
    if x is None:
        return None
    try:
        json.dumps(x)
        return x
    except TypeError:
        return json.loads(json.dumps(x, default=lambda o: getattr(o, "__dict__", str(o))))


# ---------------------------------------------------------------------------------------------------------
# parent: scheduling, guarded children, resume
# ---------------------------------------------------------------------------------------------------------

def _wp_applies(circuit: str | None) -> bool:
    """The weight-presence stage only has work on circuits with chained weights (multi-step training)."""
    return circuit is not None and circuit not in INFERENCE and circuit not in FORWARD_ONLY


def needed_stages(existing: dict | None, redo: str | None, retry_errors: bool, versions: dict | None = None,
                  circuit: str | None = None) -> set[str]:
    circuit = circuit if circuit is not None else (existing or {}).get("circuit")
    wp = {"wp"} if _wp_applies(circuit) else set()
    if redo == "all" or existing is None:
        return {"upper", "lower"} | wp
    st = set()
    sv = existing.get("stage_versions") or {}
    cur = versions or module_versions()
    if wp and (existing.get("L_wp") is None or redo in ("lower", "stale") and sv.get("wp") != cur.get("wp")):
        st |= wp
    stale_upper = redo == "stale" and existing.get("U") is not None and (sv.get("coarse") != cur["coarse"] or sv.get("upper") != cur["upper"])
    # a training U is a witness only if the planner itself certified the RU quotient acyclic (SPEC s0); stamps on merged rows can lie
    if redo == "stale" and existing.get("U") is not None and existing.get("circuit") not in FORWARD_ONLY \
            and (existing.get("U_detail") or {}).get("acyclic") is not True:
        stale_upper = True
    Lc = coarse_L(existing)                                  # the wp floor alone does not make the lower stage "done"
    stale_lower = redo == "stale" and Lc is not None and sv.get("lower") != cur["lower"]
    if redo == "upper" or stale_upper or existing.get("U") is None and (retry_errors or not existing.get("upper_error")):
        st.add("upper")
    if redo == "lower" or stale_lower or Lc is None and (retry_errors or not existing.get("lower_error")):
        st.add("lower")
    if existing.get("error"):
        st |= {"upper", "lower"}
    return st


_CUR_VERSIONS: dict = {}


def _stage_recency(r: dict, stage: str) -> tuple:
    """Order rows for one stage: (produced at the current module hash?, row_ts).  Every pod shard file carries a copy of the
    seed, so a plain last-file-wins merge let an *older* copy of a cell overwrite a shard's freshly computed row; newer wins."""
    sv = r.get("stage_versions") or {}
    cur = _CUR_VERSIONS.setdefault("v", module_versions())
    if stage == "lower":
        at_cur = sv.get("lower") == cur["lower"]
    elif stage == "wp":
        at_cur = sv.get("wp") == cur.get("wp")
    else:
        at_cur = sv.get("coarse") == cur["coarse"] and sv.get("upper") == cur["upper"]
    return (1 if at_cur else 0, float(r.get("row_ts") or 0.0))


_WP_KEYS = ("L_wp", "L_wp_detail", "wp_error", "wp_s")


def _is_lower_key(k: str) -> bool:
    """Keys carried by the coarse lower stage (``L``, ``L_*`` except the wp stage's and the combined-L bookkeeping)."""
    return (k == "L" or k.startswith("L_")) and k not in _WP_KEYS and k != "L_from_wp"


def merge_row(old: dict | None, new: dict) -> dict:
    if old is None:
        return finalize_row(new)
    combine_lower(old)
    combine_lower(new)
    # per stage, the more recent producer wins regardless of file order: keep the old L (U, L_wp) when it is newer than the new one
    if old.get("L_coarse") is not None and new.get("L_coarse") is not None and _stage_recency(old, "lower") > _stage_recency(new, "lower"):
        new = {k: v for k, v in new.items() if not (_is_lower_key(k) or k in ("lower_error", "lower_s"))}
        new["stage_versions"] = {k: v for k, v in (new.get("stage_versions") or {}).items() if k != "lower"}
    if old.get("U") is not None and new.get("U") is not None and _stage_recency(old, "upper") > _stage_recency(new, "upper"):
        new = {k: v for k, v in new.items() if not (k == "U" or k.startswith("U_") or k in ("upper_error", "upper_s", "soundness_violation"))}
        new["stage_versions"] = {k: v for k, v in (new.get("stage_versions") or {}).items() if k not in ("upper", "coarse")}
    if old.get("L_wp") is not None and new.get("L_wp") is not None and _stage_recency(old, "wp") > _stage_recency(new, "wp"):
        new = {k: v for k, v in new.items() if k not in _WP_KEYS}
        new["stage_versions"] = {k: v for k, v in (new.get("stage_versions") or {}).items() if k != "wp"}
    if new.get("L_coarse") is None:                     # no coarse certificate in ``new``: its L (if any) is only the wp floor,
        new.pop("L", None)                              # and the combined L is recomputed from L_coarse / L_wp in finalize_row
        new.pop("L_from_wp", None)
    out = dict(old)
    for k, v in new.items():
        if v is not None or k not in out:
            out[k] = v
    # stage provenance follows the bound it stamps: a row that brings an L (U, L_wp) brings its lower (upper, wp) hash, else the old one stays
    sv = dict(old.get("stage_versions") or {})
    nv = new.get("stage_versions") or {}
    if new.get("L_coarse") is not None and "lower" in nv:
        sv["lower"] = nv["lower"]
    if new.get("U") is not None and "upper" in nv:
        sv["upper"], sv["coarse"] = nv["upper"], nv.get("coarse")
    if new.get("L_wp") is not None and "wp" in nv:
        sv["wp"] = nv["wp"]
    if sv:
        out["stage_versions"] = sv
    for k in ("upper_error", "lower_error", "error"):
        if new.get(k) is None and (k == "upper_error" and new.get("U") is not None or k == "lower_error" and new.get("L_coarse") is not None):
            out[k] = None
    # ``error`` is a whole-child failure (crash / OOM / missing module): once a later child produced *any* stage result for the
    # cell, the old error text is obsolete and must not survive the merge (it used to, and made fresh rows look failed).
    if new.get("error") is None and any(new.get(k) is not None for k in ("U", "L", "L_wp")):
        out["error"] = None
    return finalize_row(out)


def child_main(spec_path: str) -> int:
    spec = json.loads(Path(spec_path).read_text())
    cells = [Cell(**c) for c in spec["cells"]]
    eval_graph(cells, set(spec["stages"]), Path(spec["frag"]), fwd_macs=spec.get("fwd_macs"), log=lambda *a: print(*a, flush=True))
    return 0


def sweep(cells: list[Cell], out_path: Path, *, resume: bool = True, redo: str | None = None, retry_errors: bool = False,
          timeout_s: float = 3600.0, max_rss_mb: float = DEFAULT_MAX_RSS_MB, dry_run: bool = False, max_tokens: int | None = None,
          lock: bool = True, allow_heavy: bool = False, shard: tuple[int, int] | None = None, mem_gate_gb: float | None = None,
          only_stages: set[str] | None = None, log=print) -> list[dict]:
    """``allow_heavy`` runs the cells :func:`too_heavy` would defer (a pod with tens of GB, not the laptop); ``shard=(k, n)``
    runs every ``n``-th graph starting at ``k`` (parallel drivers on one machine, each writing its own ``out_path``);
    ``mem_gate_gb`` makes a driver wait before spawning a child until the machine's (cgroup's) used memory is below it --
    parallel drivers self-throttle instead of tripping the container OOM killer (children peak at 10-80 GB)."""
    from accumulation.sweeps.calibration import load_calibration
    from accumulation.sweeps.guard import run_guarded
    out_path = Path(out_path)
    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    existing = {row_key(r): finalize_row(r) for r in read_jsonl(out_path)} if (resume and out_path.exists()) else {}
    calib = load_calibration(out_path.parent)
    syms = bound_symbols()
    cur_versions = module_versions()
    log(f"[coarse] bound symbols: {syms}; versions {cur_versions}")
    # group by graph
    todo: dict[tuple, list[tuple[Cell, set[str]]]] = {}
    skipped = []
    deferred = 0
    for c in cells:
        why = supported(c)
        if why:
            skipped.append((c, why))
            continue
        if max_tokens is not None and c.tokens > max_tokens or (too_heavy(c) and not allow_heavy):
            deferred += 1
            r = existing.get(c.key()) or new_row(c)
            if r.get("U") is None and r.get("L") is None:      # never measured: mark for the pod, filled from the analytic model in reports
                r["status"] = "pod"
                r["error"] = None
                existing[c.key()] = finalize_row(r)
            continue
        prev = existing.get(c.key())
        cal = calib.get((c.model, c.Q_inf))
        if prev and prev.get("F") is not None and (prev.get("fwd_units") != "work" or
                                                   (cal and cal.get("fwd_work") and abs(prev["F"] - c.F_hat * cal["fwd_work"]) > 0.5)):
            prev = None                                          # F/G basis changed (MAC units -> checker work units): redo everything
            log(f"[coarse] stale F/G basis, redo: {c.model} {c.circuit} Q_inf={c.Q_inf} F_hat={c.F_hat:g} G_hat={c.G_hat:g} Q_step={c.Q_step} K={c.K}")
        st = needed_stages(prev, redo, retry_errors, cur_versions, circuit=c.circuit)
        if only_stages is not None:                              # e.g. a lower-only pass over rows whose U the pod already produced
            st &= set(only_stages)
        if prev is None and c.key() in existing:
            existing[c.key()] = new_row(c)
        if not dry_run:
            st = {s for s in st if syms.get(f"{s}_coarse")}  # do not spawn for a stage whose module is missing
        if not st:
            continue
        todo.setdefault(c.graph_key(), []).append((c, st))
    for c, why in skipped:
        log(f"[coarse] skip {c.model} {c.circuit} Q_inf={c.Q_inf} Q_step={c.Q_step} K={c.K}: {why}")
        r = existing.get(c.key()) or new_row(c)
        if r.get("error") != f"unsupported: {why}":
            r["error"] = f"unsupported: {why}"
            existing[c.key()] = finalize_row(r)
    # Secondary key: the graph key itself.  Sharding is by index, so the order must be identical in every driver process; ties
    # in cell_cost (e.g. local-sgd K=2 vs pretrain-dense at the same token count) were previously broken by set-iteration order,
    # which is hash-seed dependent -- two shards could pick the same graph and a third graph was run by nobody.
    graphs = sorted(todo.items(), key=lambda kv: (cell_cost(kv[1][0][0]), repr(kv[0])))
    if shard is not None:
        k, n = shard
        graphs = [g for i, g in enumerate(graphs) if i % n == k]
        log(f"[coarse] shard {k}/{n}: {len(graphs)} graphs")
    log(f"[coarse] {len(cells)} cells, {len(existing)} existing rows, {sum(len(v) for v in todo.values())} cells to run on {len(graphs)} graphs"
        + (f", {deferred} deferred to the pod (tokens > {max_tokens} or heavy model)" if deferred else "") + (" (dry run)" if dry_run else "")
        + f"; RSS cap {max_rss_mb:.0f} MB ({GUARDIAN_NOTE})")
    if dry_run:
        for gk, items in graphs:
            log(f"  graph {gk}: {len(items)} cells, stages {sorted(set().union(*(s for _, s in items)))}, cost {cell_cost(items[0][0]):.2e}")
        return list(existing.values())
    env = {"PYTHONPATH": ".", "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": os.environ.get("HOME", "/tmp")}
    for gk, items in graphs:
        model, circuit, tokens, seq, K = gk
        stages = set().union(*(s for _, s in items))
        cal = calib.get((model, items[0][0].Q_inf))
        spec = {"cells": [asdict(c) for c, _ in items], "stages": sorted(stages), "frag": str(SPEC_DIR / f"frag_{os.getpid()}_{abs(hash(gk))}.jsonl"),
                "fwd_macs": cal["fwd_work"] if cal and cal.get("fwd_work") else None}
        sp = SPEC_DIR / f"spec_{os.getpid()}_{abs(hash(gk))}.json"
        write_json(sp, spec)
        frag = Path(spec["frag"])
        if frag.exists():
            frag.unlink()
        log(f"[coarse] graph {model} {circuit} tokens={tokens} seq={seq} K={K}: {len(items)} policy points, stages {sorted(stages)}")
        if mem_gate_gb is not None:
            _wait_memory(mem_gate_gb, log)
        for attempt in range(2):
            res = run_guarded([sys.executable, "-u", "-m", "accumulation.sweeps.coarse_run", "--child-spec", str(sp)], timeout_s=timeout_s,
                              max_rss_mb=max_rss_mb, cwd=str(REPO), env=env, log=log, lock=lock)
            noise = 0
            for line in (res.stdout or "").splitlines():
                if "HighsMipSolverData::" in line:        # HiGHS (scipy 1.18) prints this on every new MIP incumbent
                    noise += 1
                    continue
                log("  " + line)
            if noise:
                log(f"  [{noise} HiGHS incumbent lines suppressed]")
            # an external SIGKILL well below our cap is the machine guardian's swap-pressure rule, not this cell's memory: retry once
            if attempt == 0 and res.status == "error" and res.returncode == -9 and res.peak_rss_mb < 0.7 * max_rss_mb:
                log(f"[coarse]   external SIGKILL at peak {res.peak_rss_mb:.0f} MB (machine swap pressure?): retrying once in 30 s")
                time.sleep(30)
                continue
            break
        rows = read_jsonl(frag) if frag.exists() else []
        done = {row_key(r) for r in rows}
        for r in rows:
            r["peak_rss_mb"] = res.peak_rss_mb
            merged = merge_row(existing.get(row_key(r)), r)
            existing[row_key(r)] = merged
        if res.status != "ok":
            detail = f"child {res.status}: {(res.detail or '')[:200]} (peak RSS {res.peak_rss_mb:.0f} MB, {res.elapsed_s:.0f}s)"
            log(f"[coarse]   {detail}")
            if res.status == "oom-guard" or (res.returncode == -9 and res.peak_rss_mb >= 0.7 * max_rss_mb):
                log(f"[coarse]   *** RSS cap hit on {gk} (peak {res.peak_rss_mb:.0f} MB): graph abandoned, report to user ***")
            for c, _ in items:
                if c.key() not in done:
                    r = existing.get(c.key()) or new_row(c)
                    r["error"] = detail
                    r["peak_rss_mb"] = res.peak_rss_mb
                    existing[c.key()] = finalize_row(r)
        else:
            log(f"[coarse]   ok: {len(rows)} rows, peak RSS {res.peak_rss_mb:.0f} MB, {res.elapsed_s:.0f}s")
        _rewrite(out_path, existing)
    _rewrite(out_path, existing)
    return list(existing.values())


def _used_memory_gb() -> float | None:
    """Used memory of the container (cgroup v2 ``memory.current``) or the machine (``free -b``); ``None`` if unknown."""
    p = Path("/sys/fs/cgroup/memory.current")
    if p.exists():
        return int(p.read_text()) / 1e9
    try:
        out = subprocess.run(["free", "-b"], capture_output=True, text=True, check=True).stdout.splitlines()
        return int(out[1].split()[2]) / 1e9
    except Exception:  # noqa: BLE001
        return None


def _wait_memory(gate_gb: float, log) -> None:
    """Block until used memory is below ``gate_gb`` (jittered re-check so parallel drivers do not all pass at once)."""
    import random
    waited = 0.0
    while True:
        used = _used_memory_gb()
        if used is None or used < gate_gb:
            time.sleep(random.uniform(0, 20))                # let a sibling that passed just before us show up
            used = _used_memory_gb()
            if used is None or used < gate_gb:
                if waited:
                    log(f"[coarse]   memory gate open after {waited:.0f}s (used {used:.0f} GB < {gate_gb:.0f} GB)")
                return
        if waited == 0:
            log(f"[coarse]   memory gate: used {used:.0f} GB >= {gate_gb:.0f} GB, waiting")
        time.sleep(30)
        waited += 30


def _rewrite(out_path: Path, rows: dict) -> None:
    tmp = out_path.with_suffix(".tmp")
    with tmp.open("w") as fh:
        for r in rows.values():
            fh.write(json.dumps(r, default=str) + "\n")
    tmp.replace(out_path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="coarse-policy sweep driver")
    ap.add_argument("--child-spec")
    ap.add_argument("--preset", action="append", default=[])
    ap.add_argument("--out-dir", type=Path, default=RESULTS_DIR)
    ap.add_argument("--file", default=OUT_FILE)
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--redo", choices=["lower", "upper", "all", "stale"],
                    help="stale: redo a stage only where the row's stage hash differs from the current bounds module (resumable)")
    ap.add_argument("--retry-errors", action="store_true")
    ap.add_argument("--timeout", type=float, default=3600.0)
    ap.add_argument("--max-rss-mb", type=float, default=DEFAULT_MAX_RSS_MB)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-tokens", type=int, default=None, help="defer cells whose circuit has more tokens than this")
    ap.add_argument("--no-lock", action="store_true", help="do not wait for the machine-wide one-child lock (children are RSS-capped anyway)")
    ap.add_argument("--models", nargs="*")
    ap.add_argument("--circuits", nargs="*", help="only these circuits; 'training' = every non-inference circuit")
    ap.add_argument("--allow-heavy", action="store_true", help="run the cells too_heavy() defers to the pod (only on a machine with tens of GB)")
    ap.add_argument("--shard", default=None, help="K/N: run every N-th graph starting at K (parallel drivers, one --file each)")
    ap.add_argument("--merge", nargs="*", default=None, help="merge these JSONL files into --out-dir/--file (rows with bounds win) and exit")
    ap.add_argument("--mem-gate-gb", type=float, default=None, help="wait before spawning a child until used memory is below this (parallel drivers)")
    ap.add_argument("--only", nargs="*", choices=["lower", "upper", "wp"], default=None, help="run only these stages (e.g. --only lower: fill L on pod rows; wp: weight-presence certificate)")
    args = ap.parse_args(argv)
    if args.child_spec:
        return child_main(args.child_spec)
    if args.merge is not None:
        out = args.out_dir / args.file
        existing = {row_key(r): finalize_row(r) for r in read_jsonl(out)} if out.exists() else {}
        n = 0
        for f in args.merge:
            for r in read_jsonl(Path(f)):
                if r.get("U") is None and r.get("L") is None:
                    continue                                   # never measured (pod / error / unsupported): keep whatever is local
                existing[row_key(r)] = merge_row(existing.get(row_key(r)), r)
                n += 1
        _rewrite(out, existing)
        print(f"merged {n} measured rows from {len(args.merge)} files into {out} ({len(existing)} rows)")
        return 0
    shard = None
    if args.shard:
        k, n = (int(x) for x in args.shard.split("/"))
        shard = (k, n)
    cells: list[Cell] = []
    for p in args.preset or ["smoke"]:
        cells += preset_cells(p)
    if args.models:
        cells = [c for c in cells if c.model in args.models]
    if args.circuits:
        cells = [c for c in cells if c.circuit in args.circuits or ("training" in args.circuits and c.circuit not in INFERENCE)]
    cells = sorted(set(cells), key=lambda c: (cell_cost(c), repr(c.key())))
    sweep(cells, args.out_dir / args.file, resume=not args.no_resume, redo=args.redo, retry_errors=args.retry_errors, timeout_s=args.timeout,
          max_rss_mb=args.max_rss_mb, dry_run=args.dry_run, max_tokens=args.max_tokens, lock=not args.no_lock,
          allow_heavy=args.allow_heavy, shard=shard, mem_gate_gb=args.mem_gate_gb, only_stages=set(args.only) if args.only else None,
          log=lambda *a: print(*a, flush=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
