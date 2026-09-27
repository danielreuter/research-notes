"""Block-term check on *registry* transformer circuits at tiny scale (``X = inf``, F/G policy).

`lower_coarse`'s block term (the certificate behind the headline) only fires on transformer-shaped circuits;
the hand-built micro chains are not transformer-shaped, so on them it falls back to the token + root floor.
This module builds the real registry circuits exactly as the sweeps do (``sweeps.coarse_run.make_workload``,
``sweeps.synthetic.model_cfg``) -- ``local-sgd`` at ``tiny``/``tiny2`` with ``K`` chained steps and
``forward-nonfixed`` at ``tiny2`` -- and, per ``(F, G)`` regime,

* ``L = lower_coarse(...)`` with its breakdown (tokens, root floor, ``block_bytes``, ``weight_floor_bytes``,
  ``cap``) and whether the block term fired (``worst_ru.block_bytes > 0``);
* ``U = upper_coarse(...)`` (literal cost of the expanded plan, re-checked with ``is_legal``);
* the exact optimum ``I*`` where the single-RU partition is legal (then ``I* = tokens + read charged roots``);
  otherwise a **bracket** ``[I_lo, I_hi]``: ``I_lo`` = the trivial floor (every read charged root and token
  enters at least once), ``I_hi`` = the cheapest *legal* partition we can construct (the ``upper_coarse`` plan,
  one-RU-per-op / per-op-block seeds, each improved by greedy adjacent-RU merging under a time budget).
  These circuits have 660-8700 gates, far beyond the gate-level exact solver at binding cells; a bracket is the
  honest object.  ``L > I_hi`` is a definite soundness violation (``I_hi`` is the cost of a legal partition);
  ``L <= I_lo`` is a definite pass; anything in between is "consistent, not proved".

Outputs ``results/block_term.json`` and ``results/validation_block_term.md``; ``coarse_validation`` folds the
rows into ``results/validation.{md,json}`` as bracket cells.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Optional

from accumulation.redteam.harness import (SolverTimeout, _versions, describe_partition, op_gate_lists,
                                          with_timeout)

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(HERE, "results")


# ---------------------------------------------------------------------------------------------------------
# cells
# ---------------------------------------------------------------------------------------------------------

@dataclass
class Spec:
    model: str
    circuit: str
    K: Optional[int]        # None = inference-style (forward-nonfixed)
    Q: int                  # Q_step (training) or Q_inf (forward)
    seq: int
    regimes: list[tuple[str, Optional[float], Optional[float]]]   # (label, F multiplier of `unit`, G multiplier of `unit`)

    @property
    def name(self) -> str:
        if self.K is None:
            return f"{self.circuit}[{self.model},q={self.Q}]"
        return f"{self.circuit}[{self.model},K={self.K},Q_step={self.Q},seq={self.seq}]"


TRAIN_REGIMES_K1 = [("anchor: one RU legal", None, None),
                    ("a: F < step (F=step/2), G=inf", 0.5, None),
                    ("a+G: F=step/2, G=step/2", 0.5, 0.5),
                    ("c: G-only, G=step/2 (>=2 RUs), F=inf", None, 0.5)]
TRAIN_REGIMES_K = [("anchor: one RU legal", None, None),
                   ("a: F < step (F=step/2), G=inf", 0.5, None),
                   ("a+G: F=step/2, G=step", 0.5, 1.0),
                   ("b: one step fits, two do not (F=step: Up(one step) ~ step/2 < F < Up(two steps) ~ 1.5*step), G=inf", 1.0, None),
                   ("b2: F=1.5*step (just below the two-step Up: only the embeds must leave), G=inf", 1.5, None),
                   ("c: G-only, G=step (>=K RUs), F=inf", None, 1.0),
                   ("c: G-only, G=1.5*step, F=inf", None, 1.5)]
# forward-nonfixed @ tiny2 (2 layers): unit = W / layers = one layer's work
FWD_REGIMES = [("anchor: one RU legal", None, None),
               ("G-only, G=layer (>=2 RUs along layers or tokens), F=inf", None, 1.0),
               ("G-only, G=layer/2 (>=4 RUs), F=inf", None, 0.5),
               ("F < layer (F=layer/2), G=inf", 0.5, None),
               ("F=layer/2, G=layer", 0.5, 1.0)]


def specs() -> list[Spec]:
    out = [Spec("tiny", "local-sgd", 1, 1, 1, TRAIN_REGIMES_K1),
           Spec("tiny", "local-sgd", 2, 1, 1, TRAIN_REGIMES_K),
           Spec("tiny", "local-sgd", 3, 1, 1, TRAIN_REGIMES_K),
           Spec("tiny", "local-sgd", 2, 2, 2, TRAIN_REGIMES_K),
           Spec("tiny2", "local-sgd", 1, 1, 1, TRAIN_REGIMES_K1),
           Spec("tiny2", "local-sgd", 2, 1, 1, TRAIN_REGIMES_K),
           Spec("tiny2", "forward-nonfixed", None, 1, 1, FWD_REGIMES),
           Spec("tiny2", "forward-nonfixed", None, 2, 2, FWD_REGIMES),
           Spec("tiny2", "forward-nonfixed", None, 4, 4, FWD_REGIMES)]
    return out


def build(spec: Spec):
    """The sweeps' graph: ``ALGORITHMS[circuit].build(model_cfg(model), make_workload(Cell(...)))``."""
    from accumulation.algorithms.registry import ALGORITHMS
    from accumulation.sweeps.coarse_run import Cell, make_workload
    from accumulation.sweeps.synthetic import model_cfg
    if spec.K is None:
        c = Cell(model=spec.model, circuit=spec.circuit, Q_inf=spec.Q, F_hat=1.0, G_hat=1.0, Q_step=None, K=None, seq=spec.seq)
    else:
        c = Cell(model=spec.model, circuit=spec.circuit, Q_inf=spec.Q, F_hat=1.0, G_hat=1.0, Q_step=spec.Q, K=spec.K, seq=spec.seq)
    wl = make_workload(c)
    return ALGORITHMS[spec.circuit].build(model_cfg(spec.model), wl), wl


def unit_work(spec: Spec, flat) -> tuple[int, str]:
    """``step`` = work of the same circuit with ``K = 1`` (training); ``layer`` = ``W / layers`` (forward)."""
    from accumulation.exact.solve import flatten
    from accumulation.sweeps.synthetic import model_cfg
    if spec.K is None:
        return flat.total_work() // model_cfg(spec.model).layers, "layer"
    if spec.K == 1:
        return flat.total_work(), "step"
    bp1, _ = build(Spec(spec.model, spec.circuit, 1, spec.Q, spec.seq, []))
    return flatten(bp1).total_work(), "step"


# ---------------------------------------------------------------------------------------------------------
# fast legality + greedy merge heuristic (I_hi)
# ---------------------------------------------------------------------------------------------------------

class _Fast:
    """Bitset ``Up`` evaluation: legality of a partition in O(gates) big-int operations."""

    def __init__(self, flat):
        from accumulation.exact.solve import reach_masks
        self.flat = flat
        self.by_work: dict[int, int] = {}
        for gt in flat.gates:
            if flat.work[gt]:
                self.by_work[flat.work[gt]] = self.by_work.get(flat.work[gt], 0) | (1 << gt)
        self.cons = flat.consumers()
        self.anc, self.desc = reach_masks(flat)

    def convex(self, members: list[int]) -> bool:
        """SPEC §0: no gate outside the RU lies on a path between two of its gates (acyclic RU quotient)."""
        if len(members) <= 1:
            return True
        mem = a = d = 0
        for gt in members:
            mem |= 1 << gt
            a |= self.anc[gt]
            d |= self.desc[gt]
        return not (a & d & ~mem)

    def ru_ok(self, asg: dict, r: int, members: list[int], F: Optional[int], G: Optional[int]) -> bool:
        flat = self.flat
        if G is not None and sum(flat.work[gt] for gt in members) > G:
            return False
        if not self.convex(members):
            return False
        if F is None:
            return True
        reach: dict[int, int] = {}
        mem = set(members)
        for gt in members:                        # flat.gates order is topological; members ascend
            m = 1 << gt
            for p in flat.operands[gt]:
                if p in mem:
                    m |= reach[p]
            reach[gt] = m
        # max over gates is attained at in-RU sinks, but checking all is cheap enough
        for gt in members:
            if any(c in mem for c in self.cons.get(gt, ())):
                continue
            m = reach[gt]
            if sum(w * (m & mk).bit_count() for w, mk in self.by_work.items()) > F:
                return False
        return True

    def legal(self, asg: dict, F: Optional[int], G: Optional[int]) -> bool:
        groups: dict[int, list[int]] = {}
        for gt in self.flat.gates:
            groups.setdefault(asg[gt], []).append(gt)
        return all(self.ru_ok(asg, r, mem, F, G) for r, mem in groups.items())


def greedy_merge(flat, fast: _Fast, asg: dict, F: Optional[int], G: Optional[int], *, budget_s: float) -> tuple[dict, int]:
    """Merge wire-adjacent RUs (first improvement, largest saving first among a sample) while legal.  Merging
    never raises ``sum_R in(R)``, so every accepted merge is a strict improvement or neutral."""
    from accumulation.exact.solve import partition_cost
    t0 = time.perf_counter()
    asg = dict(asg)
    members: dict[int, list[int]] = {}
    for gt in flat.gates:
        members.setdefault(asg[gt], []).append(gt)
    cost = partition_cost(flat, asg)

    def crossing(a: int, b: int) -> int:
        """Bytes saved by merging a and b: values of a read by b (counted once in b) and vice versa."""
        sa, sb = set(members[a]), set(members[b])
        saved = 0
        seen = set()
        for gt in members[b]:
            for p in flat.operands[gt]:
                if p in sa and p not in seen:
                    seen.add(p); saved += flat.bytes_of(p)
        for gt in members[a]:
            for p in flat.operands[gt]:
                if p in sb and p not in seen:
                    seen.add(p); saved += flat.bytes_of(p)
        # shared external imports are also de-duplicated
        ia = {p for gt in members[a] for p in flat.operands[gt] if p not in sa and (not flat.is_input[p] or p in flat.nonfixed_inputs)}
        ib = {p for gt in members[b] for p in flat.operands[gt] if p not in sb and (not flat.is_input[p] or p in flat.nonfixed_inputs)}
        saved += sum(flat.bytes_of(p) for p in (ia & ib) - seen)
        return saved

    improved = True
    while improved and time.perf_counter() - t0 < budget_s:
        improved = False
        # adjacency
        adj: dict[tuple[int, int], int] = {}
        for gt in flat.gates:
            r = asg[gt]
            for p in flat.operands[gt]:
                if not flat.is_input[p] and asg[p] != r:
                    key = (min(r, asg[p]), max(r, asg[p]))
                    adj[key] = adj.get(key, 0) + flat.bytes_of(p)
        cands = sorted(adj, key=lambda k: -adj[k])
        for a, b in cands:
            if time.perf_counter() - t0 > budget_s:
                break
            if a not in members or b not in members:
                continue
            save = crossing(a, b)
            if save <= 0:
                continue
            merged = members[a] + members[b]
            merged.sort()
            if not fast.ru_ok(asg, a, merged, F, G):
                continue
            for gt in members[b]:
                asg[gt] = a
            members[a] = merged
            del members[b]
            cost -= save
            improved = True
            break
    return asg, partition_cost(flat, asg)


def seeds(flat, og: dict, blocks: tuple[int, ...] = (2, 4, 8)) -> list[tuple[str, dict]]:
    gate_op = {gt: oid for oid, gl in og.items() for gt in gl}
    ops = sorted(og)
    out = [("per-op", {gt: gate_op.get(gt, -1 - gt) for gt in flat.gates})]
    for k in blocks:
        out.append((f"op-blocks/{k}", {gt: (ops.index(gate_op[gt]) // k if gt in gate_op else -1 - gt) for gt in flat.gates}))
    out.append(("per-gate", {gt: gt for gt in flat.gates}))
    return out


# ---------------------------------------------------------------------------------------------------------
# one cell
# ---------------------------------------------------------------------------------------------------------

def _lower(g, F: Optional[int], G: Optional[int], bp) -> tuple[Optional[int], str, dict]:
    from accumulation.bounds.lower import lower_coarse
    try:
        res = lower_coarse(g, F, G, program=bp.program)
    except Exception as e:                            # noqa: BLE001
        return None, f"{type(e).__name__}: {str(e)[:200]}", {}
    tot = getattr(res, "L", getattr(res, "total", res))
    b = {k: getattr(res, k) for k in ("total", "source", "cap", "token_seed", "state_floor", "target_macs") if hasattr(res, k)}
    b["notes"] = list(getattr(res, "notes", []) or [])[:12]
    wr = getattr(res, "worst_ru", None) or {}
    b["worst_ru"] = wr
    b["block_bytes"] = wr.get("block_bytes")
    b["weight_floor_bytes"] = wr.get("weight_floor_bytes")
    b["root_bytes"] = wr.get("root_bytes")
    b["by_class"] = wr.get("by_class")
    return int(tot), "", b


def block_fired(brk: dict) -> bool:
    """``worst_ru.block_bytes > 0`` up to LP round-off (the module reports e.g. ``-9.7e-13``)."""
    return bool(float(brk.get("block_bytes") or 0.0) > 1e-6)     # plain bool: numpy.bool_ would be JSON-dumped as a string


def run_cell(spec: Spec, regime: tuple[str, Optional[float], Optional[float]], *, budget_s: float, verbose: bool) -> dict:
    from accumulation.exact.solve import exact_min_input, flatten, is_legal, partition_cost
    from accumulation.graph.opgraph import extract
    from accumulation.redteam.coarse_validation import binding_constraint, eval_upper

    t0 = time.perf_counter()
    bp, wl = build(spec)
    flat = flatten(bp)
    g = extract(bp)
    og = op_gate_lists(bp, g, flat)
    unit, unit_name = unit_work(spec, flat)
    W = flat.total_work()
    label, fm, gm = regime
    F = None if fm is None else int(round(fm * unit))
    G = None if gm is None else int(round(gm * unit))
    cell: dict = dict(circuit=spec.name, model=spec.model, algorithm=spec.circuit, K=spec.K, Q=spec.Q, seq=spec.seq,
                      tokens=wl.tokens, gates=flat.n_gates, ops=len(g.ops), work=W, unit=unit, unit_name=unit_name,
                      regime=label, F=F, G=G, F_label="inf" if F is None else f"{fm:g}*{unit_name}",
                      G_label="inf" if G is None else f"{gm:g}*{unit_name}", token_bytes=bp.token_bytes() if hasattr(bp, "token_bytes") else None)
    cell["binding"] = binding_constraint(flat, F, G)
    cons = flat.consumers()
    floor = sum(flat.bytes_of(v) for v in flat.nonfixed_inputs if cons.get(v))
    cell["I_lo"] = floor
    cell["I_hi"] = None
    cell["I_hi_source"] = ""
    cell["Istar"] = None
    cell["optimal"] = False
    cell["partition"] = []

    # exact where the single RU is legal (the fast path inside exact_min_input)
    if cell["binding"] == "none":
        one = {gt: 0 for gt in flat.gates}
        ok, _ = is_legal(flat, one, F, None, G)
        assert ok
        cell.update(Istar=partition_cost(flat, one), optimal=True, I_hi=partition_cost(flat, one), I_hi_source="single RU",
                    partition=describe_partition(flat, g, og, one))
        assert cell["Istar"] == floor
    # U
    cell.update(eval_upper(bp, flat, g, F, G))
    # L
    L, err, brk = _lower(g, F, G, bp)
    cell.update(L=L, L_error=err, L_breakdown=brk, block_term_fired=block_fired(brk) if brk else None)
    # bracket: cheapest legal partition we can construct
    if not cell["optimal"]:
        fast = _Fast(flat)
        best, best_cost, src = None, None, ""
        cands: list[tuple[str, dict]] = []
        if cell.get("U_legal") and cell.get("U_literal") is not None:
            try:
                from accumulation.bounds.coarse import plan_gate_assignment, upper_coarse
                plan = upper_coarse(g, flat.total_work() if F is None else F, G, program=bp.program)
                asg = plan_gate_assignment(g, plan, bp.program)
                cands.append(("upper_coarse plan", {k: asg[k] for k in flat.gates}))
            except Exception:                      # noqa: BLE001
                pass
        cands += seeds(flat, og)
        per = max(5.0, budget_s / max(1, len(cands)))
        for name, s0 in cands:
            if time.perf_counter() - t0 > budget_s * 1.5:
                break
            if not fast.legal(s0, F, G):
                continue
            asg, c = greedy_merge(flat, fast, s0, F, G, budget_s=per)
            ok, why = is_legal(flat, asg, F, None, G)       # ground truth re-check
            if not ok:
                continue
            c = partition_cost(flat, asg)
            if best_cost is None or c < best_cost:
                best, best_cost, src = asg, c, f"{name} + greedy merge"
        if best is not None:
            cell.update(I_hi=best_cost, I_hi_source=src, n_units_hi=len(set(best.values())),
                        partition=describe_partition(flat, g, og, best) if len(set(best.values())) <= 64 else
                        [{"ru": "…", "note": f"{len(set(best.values()))} RUs (not listed)"}])
    # verdict
    viol = []
    if L is not None and cell["I_hi"] is not None and L > cell["I_hi"]:
        viol.append(f"L_gt_legal_partition: L={L} > cost of legal partition {cell['I_hi']} ({cell['I_hi_source']})")
    if cell.get("U_literal") is not None and cell["I_hi"] is not None and cell["optimal"] and cell["U_literal"] < cell["Istar"]:
        viol.append("U_lt_Istar")
    if cell.get("U_legal") is False:
        viol.append("U_illegal")
    if L is not None and cell["I_lo"] is not None:
        cell["L_verdict"] = ("VIOLATION" if viol and viol[0].startswith("L_gt") else
                             "proved (L <= I_lo)" if L <= cell["I_lo"] else
                             "exact" if cell["optimal"] else "consistent (I_lo < L <= I_hi), not proved")
    cell["violations"] = viol
    ref = cell["Istar"] if cell["optimal"] else cell["I_hi"]
    cell["L_over_ref"] = (L / ref) if (L is not None and ref) else None
    cell["U_over_ref"] = (cell["U"] / ref) if (cell.get("U") is not None and ref) else None
    cell["seconds"] = time.perf_counter() - t0
    if verbose:
        print(f"{spec.name} {label}: F={F} G={G} bind={cell['binding']} I*={cell['Istar']} [{cell['I_lo']}, {cell['I_hi']}] "
              f"L={L} block={cell['block_term_fired']} U={cell.get('U')} {viol} ({cell['seconds']:.0f}s)", flush=True)
    return cell


# ---------------------------------------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------------------------------------

def all_cells() -> list[tuple[int, int]]:
    return [(i, j) for i, s in enumerate(specs()) for j in range(len(s.regimes))]


def run_parallel(jobs: int, budget_s: float, verbose: bool) -> list[dict]:
    cells = all_cells()
    tmp = "/tmp/redteam/block_term"
    os.makedirs(tmp, exist_ok=True)
    procs: list[tuple[tuple[int, int], subprocess.Popen, str]] = []
    rows: list[dict] = []
    pending = list(cells)

    def launch(c):
        out = os.path.join(tmp, f"cell_{c[0]}_{c[1]}.json")
        p = subprocess.Popen([sys.executable, "-m", "accumulation.redteam.block_term", "--cell", str(c[0]), str(c[1]),
                              "--budget", str(budget_s), "--out-json", out] + (["--quiet"] if not verbose else []),
                             cwd=os.path.dirname(HERE))
        procs.append((c, p, out))

    while pending or procs:
        while pending and len(procs) < jobs:
            launch(pending.pop(0))
        time.sleep(0.5)
        for item in list(procs):
            c, p, out = item
            if p.poll() is None:
                continue
            procs.remove(item)
            if os.path.exists(out):
                with open(out) as f:
                    rows.append(json.load(f))
            else:
                s = specs()[c[0]]
                rows.append(dict(circuit=s.name, regime=s.regimes[c[1]][0], error=f"worker exit {p.returncode}", violations=[]))
    rows.sort(key=lambda r: (r["circuit"], r.get("regime", "")))
    return rows


def _f(v, nd=2) -> str:
    if v is None:
        return "-"
    return f"{v:.{nd}f}" if isinstance(v, float) else str(v)


def render_md(doc: dict) -> str:
    m, rows = doc["meta"], doc["rows"]
    for r in rows:
        if r.get("L_breakdown"):
            r["block_term_fired"] = block_fired(r["L_breakdown"])
    L = ["# Block-term check: `lower_coarse` on registry transformer circuits (tiny scale, `X = inf`)", ""]
    L.append(f"Generated {m['generated']}; `bounds/lower.py` sha1 `{m['lower_sha1']}`, `bounds/lower_coarse.py` sha1 "
             f"`{m['lower_coarse_sha1']}`; graphs built with `sweeps.coarse_run.make_workload` / `sweeps.synthetic.model_cfg`.")
    L.append("")
    L.append("`I*` is exact only where the single-RU partition is legal.  Elsewhere the cell is a **bracket** "
             "`[I_lo, I_hi]`: `I_lo` = read charged roots + tokens (trivial floor), `I_hi` = cost of the cheapest legal "
             "partition constructed (`upper_coarse` plan / per-op seeds + greedy merging; re-checked with `is_legal`).  "
             "`L > I_hi` is a soundness violation.  Legality model: acyclic RU quotient (SPEC §0); a `U` marked CYCLIC is a stale planner family (not a witness, not counted).  `block` = the block term fired (`worst_ru.block_bytes > 0`).  "
             "`unit` = work of one training step (`K=1` build of the same circuit) or of one layer (forward).")
    L.append("")
    fired = [r for r in rows if r.get("block_term_fired")]
    not_fired = [r for r in rows if r.get("block_term_fired") is False and r.get("binding") != "none"]
    viol = [r for r in rows if r.get("violations")]
    L.append(f"- cells: {len(rows)}; exact: {sum(1 for r in rows if r.get('optimal'))}; bracketed: {sum(1 for r in rows if not r.get('optimal') and r.get('I_hi') is not None)}; "
             f"block term fired: {len(fired)}; **did not fire at a binding cell: {len(not_fired)}**; violations: {len(viol)}.")
    L.append("")
    L.append("| circuit | gates | regime | F | G | binds | I* / [I_lo, I_hi] | L | tokens | root floor | block_bytes | weight_floor | cap | block? | U (lit) | L/ref | U/ref | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        if "error" in r:
            L.append(f"| {r['circuit']} | - | {r['regime']} | | | | ERROR {r['error']} | | | | | | | | | | | |")
            continue
        b = r.get("L_breakdown") or {}
        istar = str(r["Istar"]) if r.get("optimal") else f"[{r['I_lo']}, {_f(r['I_hi'])}]"
        u = f"{_f(r.get('U'))}" + ("" if r.get("U_literal") in (None, r.get("U")) else f" ({r['U_literal']})") + (
            " CYCLIC" if r.get("U_cyclic") else "" if r.get("U_legal") in (None, True) else " ILLEGAL")
        L.append(f"| {r['circuit']} | {r['gates']} | {r['regime']} | {r['F_label']} ({_f(r['F'])}) | {r['G_label']} ({_f(r['G'])}) | {r['binding']} | {istar} | "
                 f"{_f(r.get('L'))} | {_f(b.get('token_seed'))} | {_f(b.get('root_bytes'))} | {_f(b.get('block_bytes'))} | {_f(b.get('weight_floor_bytes'))} | {_f(b.get('cap'))} | "
                 f"{'yes' if r.get('block_term_fired') else 'no'} | {u} | {_f(r.get('L_over_ref'))} | {_f(r.get('U_over_ref'))} | {r.get('L_verdict', '')}{'; ' + '; '.join(r['violations']) if r.get('violations') else ''} |")
    L.append("")
    if not_fired:
        L.append("## Block term did NOT fire on a genuine tiny transformer at a binding cell (bug report for the lower-bound agent)")
        L.append("")
        for r in not_fired:
            b = r.get("L_breakdown") or {}
            L.append(f"- **{r['circuit']}** ({r['gates']} gates, {r['ops']} ops, tokens={r['tokens']}), regime *{r['regime']}*: F={_f(r['F'])}, G={_f(r['G'])} "
                     f"(unit {r['unit_name']} = {r['unit']} work, W = {r['work']}), binding {r['binding']}.  "
                     f"L={r.get('L')} = tokens {b.get('token_seed')} + max(root {b.get('root_bytes')}, block {b.get('block_bytes')} + weight_floor {b.get('weight_floor_bytes')}); cap={b.get('cap')}.  "
                     f"Best legal partition found: {_f(r.get('I_hi'))} B ({r.get('I_hi_source')}, {r.get('n_units_hi')} RUs); U={_f(r.get('U'))}.")
            for n in b.get("notes", [])[:8]:
                L.append(f"  - note: {str(n)[:220]}")
            wr = b.get("worst_ru") or {}
            if wr.get("model"):
                L.append(f"  - worst_ru.model: {str(wr['model'])[:400]}")
            L.append("  - best legal partition (the attack the certificate must price):")
            for ru in (r.get("partition") or [])[:40]:
                if "note" in ru:
                    L.append(f"    - {ru['note']}"); continue
                ops = ", ".join(f"{k} x{v}" for k, v in ru["ops"].items())
                imps = ", ".join(f"{k}={v}B" for k, v in list(ru["imports"].items())[:12]) + (" …" if len(ru["imports"]) > 12 else "")
                L.append(f"    - RU{ru['ru']}: work {ru['work']}, input {ru['in_bytes']} B; ops [{ops[:300]}]; crossing in: {imps}")
            L.append("")
    if viol:
        L.append("## Violations")
        L.append("")
        for r in viol:
            L.append(f"- **{r['circuit']}** {r['regime']}: {'; '.join(r['violations'])}")
        L.append("")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", nargs=2, type=int, help="(spec index, regime index): run one cell (worker mode)")
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--budget", type=float, default=240.0, help="heuristic budget per cell (s)")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.cell:
        s = specs()[a.cell[0]]
        row = run_cell(s, s.regimes[a.cell[1]], budget_s=a.budget, verbose=not a.quiet)
        if a.out_json:
            with open(a.out_json, "w") as f:
                json.dump(row, f, default=str)
        return 0
    from accumulation.redteam.coarse_validation import lower_sha1
    meta = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "lower_sha1": lower_sha1(), "lower_coarse_sha1": lower_sha1("lower_coarse.py"),
            "versions": _versions(), "budget_s": a.budget}
    rows = run_parallel(a.jobs, a.budget, not a.quiet)
    meta["lower_coarse_sha1_after"] = lower_sha1("lower_coarse.py")
    doc = {"meta": meta, "rows": rows}
    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "block_term.json"), "w") as f:
        json.dump(doc, f, indent=1, default=str)
    with open(os.path.join(a.out_dir, "validation_block_term.md"), "w") as f:
        f.write(render_md(doc))
    print(f"wrote {a.out_dir}/validation_block_term.md / block_term.json: {sum(1 for r in rows if r.get('violations'))} violations, "
          f"{sum(1 for r in rows if r.get('block_term_fired'))}/{len(rows)} block-term cells fired")
    return 0


if __name__ == "__main__":
    sys.exit(main())
