"""Policy calibration (corrected model, SPEC §6): ``F`` and ``G`` are multiples of one honest inference session.

For every model in ``configs`` and ``Q_inf`` in ``Q_INF``:

* ``fwd(model, Q_inf)`` = total matmul MACs of the inference circuit on ``Q_inf`` tokens (``adw(g).all_macs``;
  ``inference-dense`` for dense models, ``inference-moe`` for MoE models), and MACs/token;
* ``P`` = accumulated bytes of the training circuit (the weights, one copy; ``Program.state_bytes()``);
* per-step training MACs = ``credited_macs`` of one step of the multi-step training circuit at ``Q_step = Q_inf``
  (``local-sgd`` with ``local_steps = 1``; MoE models have no multi-step factory -> ``pretrain-moe``, single step,
  flagged), plus ``all_macs`` / ``all_work`` of that step.

A policy point ``(Q_inf, F_hat, G_hat)`` is then ``F = F_hat * fwd``, ``G = G_hat * fwd`` in absolute MACs (``G_hat``
= honest sessions batched per RU).  The table lists these for ``F_hat in {1, 1.5, 2}``, ``G_hat in {1, 4, 16, 100}``.

Output: ``results/calibration.{json,md}``.  Extraction only (no bounds); every cell is built and extracted in this
process -- run it inside a guarded child (``run_guarded``) from the CLI, as ``main`` does by default.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from accumulation.algorithms.registry import ALGORITHMS, build
from accumulation.bounds.adw import adw as compute_adw
from accumulation.configs import Workload
from accumulation.graph import extract
from accumulation.sweeps.synthetic import model_cfg
from accumulation.sweeps.util import RESULTS_DIR, write_json

Q_INF = (4096, 8192, 32768)
F_HAT = (1.0, 1.5, 2.0)
G_HAT = (1, 4, 16, 100)
DENSE = ("llama3-1b", "llama3-8b", "llama3-70b", "llama3-405b")
MOE = ("mixtral-8x7b", "qwen3-235b-a22b", "deepseek-v3")
MODELS_ORDER = DENSE + MOE
FWD_HAT = {"F": F_HAT, "G": G_HAT}


def honest_inference_alg(model: str) -> str:
    """The honest (calibration) inference circuit: ``inference-session`` (prefill + teacher-forced decode, KV internal,
    token ids the only runtime input) when the registry has it, else ``inference-dense``; MoE: ``inference-moe``."""
    if model_cfg(model).experts != 1:
        return "inference-moe"
    return "inference-session" if "inference-session" in ALGORITHMS else "inference-dense"


def circuits_for(model: str) -> tuple[str, str, bool]:
    """(honest inference circuit, one-step training circuit, multi_step_available)."""
    if model_cfg(model).experts != 1:
        return "inference-moe", "pretrain-moe", False
    return honest_inference_alg(model), "local-sgd", True


def training_workload(model: str, Q_step: int, K: int, seq: int) -> Workload:
    if model_cfg(model).experts != 1:
        if K != 1:
            raise ValueError("MoE training has no multi-step factory (pretrain-moe is one step)")
        return Workload(tokens=Q_step, seq=seq)
    return Workload(tokens=K * Q_step, seq=seq, local_steps=K)


def calibration_alg(model: str) -> str:
    """The circuit whose checker ``Work`` defines the unit of ``F`` and ``G``: ``inference-dense`` (prefill of one session of
    ``Q_inf`` tokens; ``inference-moe`` for MoE).  ``fwd(cfg, Q_inf) = adw(g).all_work`` -- every op, the same units the
    F/G checks use (verified equal to ``upper_coarse``'s single-unit work)."""
    return "inference-moe" if model_cfg(model).experts != 1 else "inference-dense"


def calibrate_cell(model: str, Q_inf: int, log=print) -> dict:
    cfg = model_cfg(model)
    inf_alg, tr_alg, multi = circuits_for(model)
    cal_alg = calibration_alg(model)
    row = {"model": model, "Q_inf": Q_inf, "inference_alg": inf_alg, "calibration_alg": cal_alg, "training_alg": tr_alg, "multi_step": multi,
           "params_total": cfg.total_params(), "params_active": cfg.active_params(), "layers": cfg.layers, "d": cfg.d,
           "units": "checker Work (all ops) of the calibration circuit", "error": None}
    t0 = time.perf_counter()
    try:
        wl = Workload(tokens=Q_inf, seq=Q_inf)
        for alg in {inf_alg, cal_alg}:
            why = ALGORITHMS[alg].supports(cfg, wl)
            if why:
                raise ValueError(f"{alg}: {why}")
        bpc = build(cal_alg, cfg, wl)
        gc = extract(bpc)
        ac = compute_adw(gc)
        fwd = ac.all_work
        row.update(fwd_work=fwd, fwd_work_per_token=fwd / Q_inf, fwd_macs=ac.all_macs, fwd_macs_per_token=ac.all_macs / Q_inf,
                   fwd_work_over_macs=fwd / ac.all_macs if ac.all_macs else None, cal_n_ops=len(gc.ops),
                   token_bytes=bpc.param_bytes("token"), token_bytes_per_token=bpc.param_bytes("token") / Q_inf)
        if inf_alg != cal_alg:                      # the honest session circuit alongside (must be one RU at F_hat = G_hat = 1)
            bp = build(inf_alg, cfg, wl)
            a = compute_adw(extract(bp))
            row.update(session_work=a.all_work, session_macs=a.all_macs, session_macs_per_token=a.all_macs / Q_inf,
                       session_over_fwd=a.all_work / fwd, session_token_bytes=bp.param_bytes("token"))
        else:
            row.update(session_work=fwd, session_macs=ac.all_macs, session_macs_per_token=ac.all_macs / Q_inf, session_over_fwd=1.0,
                       session_token_bytes=row["token_bytes"])
        t1 = time.perf_counter()
        wlt = training_workload(model, Q_inf, 1, Q_inf)
        why = ALGORITHMS[tr_alg].supports(cfg, wlt)
        if why:
            raise ValueError(f"{tr_alg}: {why}")
        bpt = build(tr_alg, cfg, wlt)
        gt = extract(bpt)
        at = compute_adw(gt)
        row.update(P=bpt.state_bytes(), P_per_token=bpt.state_bytes() / Q_inf,
                   step_credited_macs=at.credited_macs, step_matmul_macs=at.matmul_macs, step_all_macs=at.all_macs,
                   step_all_work=at.all_work, step_recompute_macs=at.recompute_macs,
                   step_credited_per_token=at.credited_macs / Q_inf, step_work_per_token=at.all_work / Q_inf,
                   w_tl=at.all_work / (Q_inf * cfg.layers), w_c=at.credited_macs / (Q_inf * cfg.layers),
                   train_over_fwd=at.credited_macs / ac.all_macs if ac.all_macs else None,
                   tr_n_ops=len(gt.ops), extract_s_inf=t1 - t0, extract_s_train=time.perf_counter() - t1)
        row["policy_points"] = {f"F_hat={fh:g}": int(round(fh * fwd)) for fh in F_HAT}
        row["policy_points"].update({f"G_hat={gh:g}": int(round(gh * fwd)) for gh in G_HAT})
    except Exception as e:  # noqa: BLE001
        row["error"] = f"{type(e).__name__}: {e}"
    log(f"[calib] {model:16s} Q_inf={Q_inf:6d} fwd={row.get('fwd_work', 0):.3e} work ({row.get('fwd_macs', 0):.3e} MAC, session {row.get('session_over_fwd') or 0:.3f} fwd) "
        f"P={row.get('P', 0):.3e} B step={row.get('step_credited_macs', 0):.3e} MAC ({row.get('train_over_fwd') or 0:.2f}x fwd)"
        + (f" ERR {row['error']}" if row["error"] else f"  ({time.perf_counter() - t0:.1f}s)"))
    return row


def _g(x, nd=3):
    return "-" if x is None else f"{x:.{nd}g}"


def calibration_md(rows: list[dict]) -> str:
    hdr = ["model", "Q_inf", "fwd = Work(calibration circuit)", "fwd MACs (all_macs)", "work/MACs", "honest session", "session/fwd", "MACs/token",
           "token B/tok", "training (1 step)", "P (B)", "step credited MACs", "step/fwd", "w_tl (work/token-layer)", "w_c (credited/token-layer)",
           "F (F_hat=1/1.5/2)", "G (G_hat=1/4/16/100)", "status"]
    lines = ["| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
    for r in rows:
        pp = r.get("policy_points", {})
        lines.append("| " + " | ".join([
            r["model"], str(r["Q_inf"]), f"{r.get('calibration_alg', '-')}: {_g(r.get('fwd_work'))}", _g(r.get("fwd_macs")), _g(r.get("fwd_work_over_macs"), 4),
            r["inference_alg"], _g(r.get("session_over_fwd"), 4), _g(r.get("fwd_macs_per_token")),
            _g(r.get("token_bytes_per_token")), r["training_alg"] + ("" if r["multi_step"] else " (single-step factory)"),
            _g(r.get("P")), _g(r.get("step_credited_macs")), _g(r.get("train_over_fwd")), _g(r.get("w_tl")), _g(r.get("w_c")),
            " / ".join(_g(pp.get(f"F_hat={fh:g}")) for fh in F_HAT) if pp else "-",
            " / ".join(_g(pp.get(f"G_hat={gh:g}")) for gh in G_HAT) if pp else "-",
            ("error: " + r["error"][:50]) if r.get("error") else "measured"]) + " |")
    return "\n".join(lines)


POD_CELLS = {("llama3-405b", 32768)}     # extraction alone exceeds the 2.4 GB cap on this machine (2411 MB); analytic fallback


def run_calibration(out_dir: Path = RESULTS_DIR, models=MODELS_ORDER, q_inf=Q_INF, log=print, resume: bool = True) -> list[dict]:
    out_dir = Path(out_dir)
    rows = []
    if resume and (out_dir / "calibration.json").exists():
        rows = [r for r in json.loads((out_dir / "calibration.json").read_text())["rows"]
                if (not r.get("error") or r.get("error", "").startswith("pod")) and r.get("inference_alg") == circuits_for(r["model"])[0]
                and r.get("calibration_alg") == calibration_alg(r["model"]) and (r.get("w_tl") or r.get("error"))]   # stale units / circuit -> redo
    have = {(r["model"], int(r["Q_inf"])) for r in rows}
    for m in models:
        for q in q_inf:
            if (m, q) in have:
                continue
            if (m, q) in POD_CELLS:
                cfg = model_cfg(m)
                rows.append({"model": m, "Q_inf": q, "inference_alg": circuits_for(m)[0], "calibration_alg": calibration_alg(m),
                             "training_alg": circuits_for(m)[1], "multi_step": circuits_for(m)[2], "params_total": cfg.total_params(),
                             "params_active": cfg.active_params(), "layers": cfg.layers, "d": cfg.d,
                             "error": "pod: extraction needs > 2.4 GB on this machine; analytic MAC model used instead"})
                log(f"[calib] {m:16s} Q_inf={q:6d} -> pod (analytic fallback)")
                continue
            rows.append(calibrate_cell(m, q, log=log))
            rows.sort(key=lambda r: (MODELS_ORDER.index(r["model"]) if r["model"] in MODELS_ORDER else 99, r["Q_inf"]))
            write_json(out_dir / "calibration.json", {"Q_inf": list(q_inf), "F_hat": list(F_HAT), "G_hat": list(G_HAT), "rows": rows})
    md = ["# Policy calibration: F and G as multiples of one honest inference session", "",
          "Corrected model (no per-RU input cap): an RU is legal iff `Work(R) <= G` and `Work(Up_R(g)) <= F` for every gate. "
          "`fwd(model, Q_inf)` = the checker's `Work` of the whole `inference-dense` circuit at `Workload(Q_inf, Q_inf)` -- all ops "
          "(`adw.all_work`, verified equal to the single-unit work of `upper_coarse`), the same units the F/G checks use; MoE: `inference-moe`. "
          "The honest session circuit (`inference-session`: prefill + teacher-forced decode, KV internal) has Work = 0.95-0.99 fwd, so it is one "
          "legal RU at F_hat = G_hat = 1 by construction. `all_macs` columns kept alongside; a policy point "
          "`(Q_inf, F_hat, G_hat)` is `F = F_hat * fwd`, `G = G_hat * fwd` (`G_hat` = honest sessions batched per RU). `P` = "
          "accumulated bytes of the training circuit (one copy of the weights). The one-step training MACs are the `credited_macs` "
          "(recompute excluded) of `local-sgd` with `local_steps = 1` at `Q_step = Q_inf` (MoE: `pretrain-moe`, whose factory is "
          "single-step; flagged). Token ingress: `toks` is V32 in the IR -> 4 B/token (2 B/token if the ids were 16-bit).", "",
          f"Generated by `accumulation.sweeps.calibration` ({len(rows)} cells, {sum(1 for r in rows if r.get('error'))} errors).", "",
          calibration_md(rows), ""]
    (out_dir / "calibration.md").write_text("\n".join(md))
    log(f"[calib] {len(rows)} cells -> {out_dir / 'calibration.{json,md}'}")
    return rows


def load_calibration(out_dir: Path = RESULTS_DIR) -> dict[tuple[str, int], dict]:
    p = Path(out_dir) / "calibration.json"
    if not p.exists():
        return {}
    return {(r["model"], int(r["Q_inf"])): r for r in json.loads(p.read_text())["rows"] if not r.get("error")}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="F/G calibration table")
    ap.add_argument("--out-dir", type=Path, default=RESULTS_DIR)
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--q-inf", nargs="*", type=int, default=None)
    ap.add_argument("--in-process", action="store_true", help="extract in this process (default: one guarded child)")
    ap.add_argument("--max-rss-mb", type=float, default=8192.0)
    ap.add_argument("--timeout", type=float, default=3600.0)
    args = ap.parse_args(argv)
    if args.in_process:
        run_calibration(args.out_dir, models=args.models or MODELS_ORDER, q_inf=tuple(args.q_inf or Q_INF),
                        log=lambda *a: print(*a, flush=True))
        return 0
    from accumulation.sweeps.guard import run_guarded
    cmd = [sys.executable, "-u", "-m", "accumulation.sweeps.calibration", "--in-process", "--out-dir", str(args.out_dir)]
    if args.models:
        cmd += ["--models", *args.models]
    if args.q_inf:
        cmd += ["--q-inf", *map(str, args.q_inf)]
    res = run_guarded(cmd, timeout_s=args.timeout, max_rss_mb=args.max_rss_mb, cwd=str(Path(__file__).resolve().parents[2]),
                      env={"PYTHONPATH": ".", "PATH": "/usr/bin:/bin"}, log=lambda *a: print(*a, flush=True))
    print(res.stdout or "", flush=True)
    print(f"[calib] child {res.status} {res.detail or ''} peak RSS {res.peak_rss_mb:.0f} MB in {res.elapsed_s:.0f}s", flush=True)
    return 0 if res.status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
