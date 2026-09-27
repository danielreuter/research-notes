"""SPEC §6 validation table: ``tiny circuit | (F, G, X) | I* | L | U(recompute=False) | L/I* | U/I*``.

Sources
    * the torture suite (:mod:`accumulation.redteam.torture`): hand-derived sharing-heavy cases, the dense
      inference (``i*``) and dense training (``r*``) micro circuits, the ``G`` forced-split case (``k1``) and the
      automatic binding-``G`` points of every case;
    * adversarial fuzz (:mod:`accumulation.redteam.fuzz`) JSONL files, given with ``--fuzz``.

Outputs (``--out-dir``, default ``accumulation/results``)
    * ``validation.md``   -- the table, the fuzz aggregate ("``k/N`` soundness violations over ``N`` instances;
      median and 5th-percentile ``L/I*``; median ``U/I*``"), the robustness gaps, and for every fuzz instance
      with ``L/I* < 0.5`` the family and the exact optimal partition (the attack the certificate misses);
    * ``validation.json`` -- machine-readable: ``{"meta", "aggregate", "rows": [one per instance]}``.

Conventions
    ``I*`` ratios use only instances where the exact solver *proved* optimality.  ``U`` in the table is the
    literal partition (``recompute=False``) -- the object ``I*`` matches; the headline ``U`` (``recompute=True``)
    is kept in the JSON.  ``L@G=None`` marks rows where ``lower_bound`` did not receive the binding ``G`` (the
    certificate is then a valid but looser bound for that policy).  Soundness = ``L <= I*`` and ``I* <= U``
    (``U`` present); an instance where ``upper_bound`` raised although ``I*`` exists is a robustness gap and is
    counted separately, not as a soundness violation.

Usage::

    PYTHONPATH=. .venv/bin/python -m accumulation.redteam.validation --fuzz "/tmp/redteam/g/fuzz_*.jsonl"
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import time
from typing import Optional

from accumulation.redteam.harness import BIG, VERSIONS, Record

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(HERE, "results")

FAMILY_LABEL = {
    "a": "independent generation", "b": "shared compact precursor", "c": "independent accumulated precursors",
    "d": "two-layer dense mixing", "e": "shared weights across branches", "f": "LoRA compact state",
    "g": "residual / copy / embedding", "h": "weight gradient / reduction", "t": "torture (overlapping reads, epilogues)",
    "k": "G forced split (hand)", "i": "dense inference", "r": "dense training",
}
GROUP_ORDER = ["i", "r", "k", "d", "a", "b", "c", "e", "f", "g", "h", "t"]


# ---------------------------------------------------------------------------------------------------------
# rows
# ---------------------------------------------------------------------------------------------------------

def _fmt(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int) and v >= (1 << 20):
        return "inf"
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def _ratio(a: Optional[int], b: Optional[int]) -> Optional[float]:
    if a is None or b is None or b <= 0:
        return None
    return a / b


def row_from_dict(d: dict, source: str) -> dict:
    """One validation row from a ``Record.to_json()`` dict (torture or fuzz)."""
    I = d.get("Istar")
    opt = bool(d.get("Istar_optimal"))
    L = None if d.get("L_infeasible") else d.get("L")
    Ul = d.get("Ulit")
    G = d.get("G")
    r = {
        "source": source,
        "circuit": d["name"],
        "family": d.get("family", ""),
        "family_label": FAMILY_LABEL.get(d.get("family", ""), d.get("family", "")),
        "F": d["F"], "G": G, "X": d["X"],
        "gates": d.get("gates"), "work": d.get("work"),
        "Istar": I, "Istar_optimal": opt, "Istar_infeasible": bool(d.get("Istar_infeasible")),
        "Istar_timeout": bool(d.get("Istar_timeout")), "Istar_units": d.get("Istar_units"),
        "L": L, "L_G": d.get("L_G"), "L_at_G_none": G is not None and d.get("L_G") is None and L is not None,
        "L_noprog": d.get("L_noprog"), "L_source": d.get("L_source"), "L_cap": d.get("L_cap"), "L_error": d.get("L_error", ""),
        "U_lit": Ul, "U_lit_legal": d.get("Ulit_legal"), "U_lit_error": d.get("Ulit_error", ""),
        "U_rec": d.get("U"), "U_rec_error": d.get("U_error", ""),
        "L_over_Istar": _ratio(L, I) if opt else None,
        "U_over_Istar": _ratio(Ul, I) if opt else None,
        "Urec_over_Istar": _ratio(d.get("U"), I) if opt else None,
        "hand_kind": d.get("hand_kind", ""), "hand": d.get("hand"), "hand_ok": d.get("hand_ok"),
        "violations": list(d.get("violations", [])),
        "sound": None,
        "robustness_gap": bool(I is not None and (d.get("Ulit_error") or d.get("U_error"))),
        "optimal_partition": d.get("Istar_partition", []),
        "snippet": d.get("snippet", ""),
        "versions": d.get("versions", {}),
        "seed": d.get("seed"), "idx": d.get("idx"),
    }
    # soundness verdict: needs I* (proved) and L; U side only when U exists
    if I is not None and L is not None:
        ok = True
        if opt:
            ok = L <= I and (Ul is None or I <= Ul)
        else:
            ok = L <= I                       # L above a *found* cost already refutes the certificate
        if d.get("Ulit_legal") is False:
            ok = False
        r["sound"] = ok
    return r


def rows_from_records(recs: list[Record], source: str = "torture") -> list[dict]:
    return [row_from_dict(r.to_json(), source) for r in recs]


def rows_from_fuzz(paths: list[str]) -> tuple[list[dict], dict]:
    rows = []
    other = {"build_error": 0, "eval_error": 0, "mono": 0}
    for p in paths:
        with open(p) as f:
            for line in f:
                d = json.loads(line)
                k = d.get("kind", "point")
                if k == "point":
                    rows.append(row_from_dict(d, "fuzz"))
                else:
                    other[k] = other.get(k, 0) + 1
    return rows, other


# ---------------------------------------------------------------------------------------------------------
# aggregate
# ---------------------------------------------------------------------------------------------------------

def _pct(xs: list[float], p: float) -> Optional[float]:
    if not xs:
        return None
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p * (len(xs) - 1))))]


def aggregate(rows: list[dict]) -> dict:
    judged = [r for r in rows if r["sound"] is not None]
    proved = [r for r in judged if r["Istar_optimal"]]
    LI = [r["L_over_Istar"] for r in proved if r["L_over_Istar"] is not None]
    UI = [r["U_over_Istar"] for r in proved if r["U_over_Istar"] is not None]
    UrI = [r["Urec_over_Istar"] for r in proved if r["Urec_over_Istar"] is not None]
    viol = [r for r in judged if r["sound"] is False]
    kinds: dict[str, int] = {}
    for r in rows:
        for v in r["violations"]:
            kinds[v] = kinds.get(v, 0) + 1
    gb = [r for r in rows if r["G"] is not None]
    return {
        "instances": len(rows),
        "judged": len(judged),
        "proved_optimal": len(proved),
        "soundness_violations": len(viol),
        "soundness_violation_rows": [(r["source"], r["circuit"], r["F"], r["G"], r["X"], r["L"], r["Istar"], r["U_lit"], r["violations"])
                                     for r in viol],
        "L_over_Istar": {"n": len(LI), "median": _pct(LI, 0.5), "p05": _pct(LI, 0.05), "min": min(LI) if LI else None,
                         "frac_eq_1": (sum(1 for x in LI if abs(x - 1) < 1e-9) / len(LI)) if LI else None,
                         "frac_lt_0.5": (sum(1 for x in LI if x < 0.5) / len(LI)) if LI else None},
        "U_over_Istar": {"n": len(UI), "median": _pct(UI, 0.5), "p95": _pct(UI, 0.95), "max": max(UI) if UI else None,
                         "frac_eq_1": (sum(1 for x in UI if abs(x - 1) < 1e-9) / len(UI)) if UI else None},
        "Urec_over_Istar": {"n": len(UrI), "median": _pct(UrI, 0.5)},
        "Istar_timeouts": sum(1 for r in rows if r["Istar_timeout"]),
        "Istar_infeasible": sum(1 for r in rows if r["Istar_infeasible"]),
        "Istar_found_not_proved": sum(1 for r in rows if r["Istar"] is not None and not r["Istar_optimal"]),
        "robustness_gaps_U_unavailable": sum(1 for r in rows if r["robustness_gap"]),
        "binding_G_points": len(gb),
        "binding_G_points_L_at_G_none": sum(1 for r in gb if r["L_at_G_none"]),
        "violation_kinds": dict(sorted(kinds.items(), key=lambda kv: -kv[1])),
        "hand_mismatches": sum(1 for r in rows if r["hand_ok"] is False),
    }


def by_group(rows: list[dict], key: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(str(r.get(key, "")), []).append(r)
    for k, sel in sorted(groups.items()):
        a = aggregate(sel)
        out[k] = {"n": a["instances"], "violations": a["soundness_violations"], "L_over_Istar": a["L_over_Istar"],
                  "U_over_Istar": a["U_over_Istar"], "U_unavailable": a["robustness_gaps_U_unavailable"]}
    return out


# ---------------------------------------------------------------------------------------------------------
# markdown
# ---------------------------------------------------------------------------------------------------------

def _policy(r: dict) -> str:
    return f"({_fmt(r['F'])}, {_fmt(r['G'])}, {_fmt(r['X'])})"


def _istar(r: dict) -> str:
    if r["Istar_infeasible"]:
        return "infeasible"
    if r["Istar_timeout"]:
        return "timeout"
    if r["Istar"] is None:
        return "-"
    return str(r["Istar"]) + ("" if r["Istar_optimal"] else " (found, not proved)")


def _L(r: dict) -> str:
    if r["L_error"] and r["L"] is None:
        return "error"
    s = _fmt(r["L"])
    if r["L_at_G_none"]:
        s += " L@G=None"
    return s


def _U(r: dict) -> str:
    if r["U_lit"] is None:
        return "unavailable" if r["U_lit_error"] else "-"
    s = str(r["U_lit"])
    if r["U_lit_legal"] is False:
        s += " ILLEGAL"
    return s


def table_md(rows: list[dict]) -> str:
    head = ("| circuit | (F, G, X) | I* | L | U (recompute=False) | L/I* | U/I* | hand | note |\n"
            "|---|---|---|---|---|---|---|---|---|")
    lines = [head]
    for r in rows:
        hand = "" if not r["hand_kind"] else (f"{r['hand_kind']} {'inf' if r['hand_kind'] == 'inf' else r['hand']}"
                                              + ("" if r["hand_ok"] is not False else " MISMATCH"))
        note = ", ".join(r["violations"])
        lines.append(f"| {_cell(r['circuit'])} | {_policy(r)} | {_istar(r)} | {_L(r)} | {_U(r)} | {_fmt(r['L_over_Istar'])} | "
                     f"{_fmt(r['U_over_Istar'])} | {hand} | {note} |")
    return "\n".join(lines)


def _partition_md(part: list[dict]) -> list[str]:
    """RUs of the optimal partition; RUs with an identical description are collapsed into one line."""
    groups: dict[str, list[int]] = {}
    for ru in part:
        ops = ", ".join(f"{k} x{v}" for k, v in ru["ops"].items())
        imps = ", ".join(f"{k}={v}B" for k, v in ru["imports"].items()) or "nothing charged"
        key = f"work {ru['work']}, input {ru['in_bytes']} B; ops [{ops}]; imports {imps}"
        groups.setdefault(key, []).append(ru["ru"])
    out = []
    for key, rus in groups.items():
        lab = f"RU{rus[0]}" if len(rus) == 1 else f"{len(rus)} RUs (RU{rus[0]}, RU{rus[1]}, ...)" if len(rus) > 2 else f"RU{rus[0]}, RU{rus[1]}"
        out.append(f"  - {lab}: {key}")
    return out


def _cell(s) -> str:
    return str(s).replace("|", "\\|")


def attacks_md(rows: list[dict], threshold: float = 0.5, limit: int = 40) -> str:
    """Fuzz (and torture) instances where ``L/I* < threshold``: the exact optimal partition is the attack the
    certificate does not see (``L`` is far below what the adversary must actually pay)."""
    sel = [r for r in rows if r["L_over_Istar"] is not None and r["L_over_Istar"] < threshold]
    sel.sort(key=lambda r: (r["L_over_Istar"], r["circuit"]))
    fams: dict[str, int] = {}
    for r in sel:
        fams[r["family"]] = fams.get(r["family"], 0) + 1
    lines = [f"{len(sel)} instances with L/I* < {threshold} "
             f"(families: {', '.join(f'{k}: {v}' for k, v in sorted(fams.items(), key=lambda kv: -kv[1]))}).", ""]
    seen_circ: set[str] = set()
    shown = 0
    for r in sel:
        # one entry per circuit (its loosest policy point), so the list stays readable
        if r["circuit"] in seen_circ:
            continue
        seen_circ.add(r["circuit"])
        shown += 1
        if shown > limit:
            lines.append(f"... {len(seen_circ) - limit} more circuits in validation.json (`rows[*].optimal_partition`).")
            break
        lines.append(f"### {r['circuit']}  [{r['source']}; family `{r['family']}`]  policy (F, G, X) = {_policy(r)}")
        lines.append(f"L = {r['L']}  I* = {r['Istar']}  U = {_U(r)}  L/I* = {r['L_over_Istar']:.3f}"
                     f"{'  (L@G=None)' if r['L_at_G_none'] else ''}; gates {r['gates']}, work {r['work']}; "
                     f"optimal partition has {r['Istar_units']} RUs:")
        lines += _partition_md(r["optimal_partition"])
        if r["snippet"]:
            lines.append("")
            lines.append("~~~python")
            lines.append(r["snippet"].rstrip())
            lines.append("~~~")
        lines.append("")
    return "\n".join(lines)


def _agg_md(a: dict, title: str) -> list[str]:
    li, ui = a["L_over_Istar"], a["U_over_Istar"]
    out = [f"**{title}**: {a['soundness_violations']}/{a['judged']} soundness violations (L <= I* and I* <= U) over "
           f"{a['judged']} judged instances ({a['instances']} evaluated; {a['proved_optimal']} with I* proved optimal, "
           f"{a['Istar_found_not_proved']} found-not-proved, {a['Istar_timeouts']} solver timeouts, "
           f"{a['Istar_infeasible']} infeasible policies).",
           f"  L/I*: median {_fmt(li['median'])}, 5th percentile {_fmt(li['p05'])}, min {_fmt(li['min'])}, "
           f"fraction exactly 1: {_fmt(li['frac_eq_1'])}, fraction < 0.5: {_fmt(li['frac_lt_0.5'])} (n = {li['n']}).",
           f"  U/I* (recompute=False): median {_fmt(ui['median'])}, 95th percentile {_fmt(ui['p95'])}, max {_fmt(ui['max'])}, "
           f"fraction exactly 1: {_fmt(ui['frac_eq_1'])} (n = {ui['n']}); headline U/I* median {_fmt(a['Urec_over_Istar']['median'])}.",
           f"  Robustness gaps (upper_bound raised although a legal partition exists): {a['robustness_gaps_U_unavailable']}; "
           f"binding-G points: {a['binding_G_points']} (L computed at G=None on {a['binding_G_points_L_at_G_none']} of them); "
           f"violation kinds: {a['violation_kinds'] or 'none'}."]
    if a["soundness_violation_rows"]:
        out.append("  Violating rows (source, circuit, F, G, X, L, I*, U_lit, violations):")
        for v in a["soundness_violation_rows"][:30]:
            out.append(f"    - {v}")
    return out


def _versions_md(rows: list[dict]) -> list[str]:
    vs: dict[str, dict[str, int]] = {}
    for r in rows:
        for k, h in (r.get("versions") or {}).items():
            vs.setdefault(k, {})
            vs[k][h] = vs[k].get(h, 0) + 1
    out = ["Module versions (sha256[:10] of the file at evaluation time; several hashes = the module changed while "
           "the campaign ran):"]
    for k, hs in sorted(vs.items()):
        out.append(f"  - `{k}`: " + ", ".join(f"`{h}` x{n}" for h, n in sorted(hs.items(), key=lambda kv: -kv[1])))
    return out


def render_md(tort_rows: list[dict], fuzz_rows: list[dict], fuzz_other: dict, mono: list[str], meta: dict) -> str:
    all_rows = tort_rows + fuzz_rows
    lines = ["# Validation table (SPEC §6): exact `I*` vs certified `L` and constructive `U`", ""]
    lines.append(f"Generated {meta['generated']} by `accumulation.redteam.validation`; `I*` from `exact_min_input(flat, F, X, G)` "
                 f"(SPEC §4, brute force / HiGHS MILP, time box {meta['time_limit']} s per point on torture rows). "
                 "Policy `(F, G, X)`: `F` = per-gate upstream-work cap, `G` = per-RU total-work cap (`-` = unbounded), "
                 "`X` = per-RU runtime-input cap in bytes; `inf` = unbounded.  `U` is the literal partition "
                 "(`recompute=False`), the object `I*` matches.  All byte quantities are bytes for the whole micro circuit "
                 "(`Workload.tokens` is 1--3 here; per-token normalisation is not meaningful at this scale).")
    lines.append("")
    lines += _versions_md(all_rows)
    lines.append("")
    lines.append("## Aggregate")
    lines.append("")
    lines += _agg_md(aggregate(all_rows), "All instances")
    lines.append("")
    lines += _agg_md(aggregate(tort_rows), "Torture / hand suite")
    lines.append("")
    lines += _agg_md(aggregate(fuzz_rows), "Adversarial fuzz")
    if fuzz_other:
        lines.append(f"  Fuzz side records: {fuzz_other}.")
    lines.append("")
    lines.append("### By family")
    lines.append("")
    lines.append("| family | n | soundness violations | L/I* median | L/I* p05 | L/I* min | U/I* median | U unavailable |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for k, a in by_group(all_rows, "family").items():
        lab = f" ({FAMILY_LABEL[k]})" if k in FAMILY_LABEL else ""
        lines.append(f"| {_cell(k)}{lab} | {a['n']} | {a['violations']} | {_fmt(a['L_over_Istar']['median'])} | "
                     f"{_fmt(a['L_over_Istar']['p05'])} | {_fmt(a['L_over_Istar']['min'])} | {_fmt(a['U_over_Istar']['median'])} | "
                     f"{a['U_unavailable']} |")
    lines.append("")
    lines.append("### By policy regime")
    lines.append("")
    for r in all_rows:
        r["_regime"] = (("F<inf" if r["F"] < BIG else "F=inf") + ", " + ("G<work" if r["G"] is not None else "G=None") + ", "
                        + ("X<inf" if r["X"] < (1 << 20) else "X=inf"))
    lines.append("| regime | n | soundness violations | L/I* median | L/I* p05 | U/I* median | U unavailable |")
    lines.append("|---|---|---|---|---|---|---|")
    for k, a in by_group(all_rows, "_regime").items():
        lines.append(f"| {k} | {a['n']} | {a['violations']} | {_fmt(a['L_over_Istar']['median'])} | {_fmt(a['L_over_Istar']['p05'])} | "
                     f"{_fmt(a['U_over_Istar']['median'])} | {a['U_unavailable']} |")
    for r in all_rows:
        r.pop("_regime", None)
    lines.append("")
    lines.append("## Table: torture suite, dense inference / training micro circuits, G forced split")
    lines.append("")
    lines.append("Rows are grouped by family; `hand` is the analytically derived `I*` (`eq`), bound (`ge`/`le`) or "
                 "infeasibility (`inf`) from the case docstring in `redteam/torture.py`.  `L@G=None`: the certificate ran "
                 "without the binding `G`.")
    lines.append("")
    for fam in GROUP_ORDER + sorted({r["family"] for r in tort_rows} - set(GROUP_ORDER)):
        sel = [r for r in tort_rows if r["family"] == fam]
        if not sel:
            continue
        lines.append(f"### {fam}. {FAMILY_LABEL.get(fam, fam)}")
        lines.append("")
        lines.append(table_md(sel))
        lines.append("")
    if mono:
        lines.append("### Monotonicity violations (torture grids)")
        lines.append("")
        lines += [f"- {m}" for m in mono]
        lines.append("")
    lines.append("## Attacks the certificate misses (L/I* < 0.5)")
    lines.append("")
    lines.append("For every such instance: the family, the policy, and the exact optimal partition -- the RUs, their work, "
                 "their charged input and which values they import.  This is *what the adversary does* that `L` does not "
                 "charge for.")
    lines.append("")
    lines.append(attacks_md(fuzz_rows + tort_rows))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------------------------------------

def build_validation(*, fuzz_globs: list[str], out_dir: str, time_limit: Optional[float], run_torture: bool = True,
                     verbose: bool = True) -> dict:
    from accumulation.redteam import torture
    t0 = time.perf_counter()
    tort_recs: list[Record] = []
    mono: list[str] = []
    if run_torture:
        tort_recs, mono = torture.run_torture(time_limit=time_limit, verbose=verbose)
    tort_rows = rows_from_records(tort_recs, "torture")
    paths = sorted(p for pat in fuzz_globs for p in glob.glob(pat))
    fuzz_rows, fuzz_other = rows_from_fuzz(paths)
    meta = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "time_limit": time_limit,
        "fuzz_files": paths,
        "versions_now": dict(VERSIONS),
        "torture_cases": [c.name for c in torture.CASES],
        "seconds": None,
    }
    all_rows = tort_rows + fuzz_rows
    doc = {
        "meta": meta,
        "aggregate": {"all": aggregate(all_rows), "torture": aggregate(tort_rows), "fuzz": aggregate(fuzz_rows),
                      "by_family": by_group(all_rows, "family"), "fuzz_other_records": fuzz_other},
        "monotonicity_violations": mono,
        "attacks": [r for r in all_rows if r["L_over_Istar"] is not None and r["L_over_Istar"] < 0.5],
        "rows": all_rows,
    }
    meta["seconds"] = time.perf_counter() - t0
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "validation.json"), "w") as f:
        json.dump(doc, f, indent=1, default=str)
    with open(os.path.join(out_dir, "validation.md"), "w") as f:
        f.write(render_md(tort_rows, fuzz_rows, fuzz_other, mono, meta))
    return doc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SPEC §6 validation table from the torture suite and fuzz JSONL")
    ap.add_argument("--fuzz", action="append", default=[], help="glob(s) of fuzz JSONL files")
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--time-limit", type=float, default=None, help="exact-solver time box for torture points")
    ap.add_argument("--no-torture", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    doc = build_validation(fuzz_globs=a.fuzz, out_dir=a.out_dir, time_limit=a.time_limit, run_torture=not a.no_torture,
                           verbose=not a.quiet)
    agg = doc["aggregate"]["all"]
    print(f"\n{agg['soundness_violations']}/{agg['judged']} soundness violations over {agg['judged']} judged instances "
          f"({agg['instances']} rows); L/I* median {_fmt(agg['L_over_Istar']['median'])} p05 {_fmt(agg['L_over_Istar']['p05'])}; "
          f"U/I* median {_fmt(agg['U_over_Istar']['median'])}; U unavailable {agg['robustness_gaps_U_unavailable']}; "
          f"attacks (L/I* < 0.5): {len(doc['attacks'])}")
    print(f"wrote {os.path.join(a.out_dir, 'validation.md')} and validation.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
