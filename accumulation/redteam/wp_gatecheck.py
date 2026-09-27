"""Gate-level check of the weight-presence certificate's op-level rule (``bounds/lower_wp.py``, fact (ii)).

For every chained weight tensor ``W_k`` of a tiny registry training circuit the certificate charges
``bytes(W_k)`` when ``Up_lb = sum(op.work over ops between producer and update) > min(F, G)``.  Soundness needs,
for **every element** ``e`` of ``W_k``: the true upstream work of ``e``'s update gate inside any RU that also
holds ``e``'s producer gate is at least ``Up_lb``.  That RU contains the gate-level hull, so the truth is

    T_e = sum of gate work over  desc(producer gate of e)  intersect  anc(update output gate of e),

computed here on the flattened circuit (``exact.solve.flatten``).  The check is ``Up_lb <= min_e T_e`` for every
chained tensor; a failure means the op-level between set contains gates that are *not* upstream of some
element's update (the mixing argument does not hold for that op) and the certificate would be unsound there.
Also reports how tight the rule is (``min_e T_e / Up_lb``).

    PYTHONPATH=. .venv/bin/python -m accumulation.redteam.wp_gatecheck
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from accumulation.bounds.lower_wp import UPDATE_KINDS, chained_weights
from accumulation.exact.solve import flatten
from accumulation.graph import extract
from accumulation.redteam.harness import op_gate_lists

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(HERE, "results")


def _cells():
    """Registry ``local-sgd`` at the exact-solver shapes plus 3- and 4-layer variants of ``tiny2`` (the rule counts
    layers two or more above the weight's own, so depth >= 3 is what exercises it)."""
    from dataclasses import replace
    from accumulation.configs import MODELS, Workload
    t2 = MODELS["tiny2"]
    out = []
    for name, cfg in (("tiny", MODELS["tiny"]), ("tiny2", t2),
                      ("tiny2-L3", replace(t2, name="tiny2-L3", layers=3)), ("tiny2-L4", replace(t2, name="tiny2-L4", layers=4)),
                      ("tiny2-L4-kv2", replace(t2, name="tiny2-L4-kv2", layers=4, kv_heads=2))):
        for K in (2, 3):
            for q, seq in ((2, 2), (4, 2), (4, 4)):
                if K == 3 and q == 4:
                    continue
                out.append((name, cfg, "local-sgd", K, q, seq, Workload(tokens=K * q, seq=seq, local_steps=K)))
    return out


def check_graph(bp, g) -> dict:
    flat = flatten(bp)
    gates_of = op_gate_lists(bp, g, flat)
    n = flat.n
    operands = flat.operands
    consumers: list[list[int]] = [[] for _ in range(n)]
    for i in range(n):
        for j in operands[i]:
            consumers[j].append(i)
    work = flat.work
    op_of_gate = [-1] * n
    for oid, gl in gates_of.items():
        for i in gl:
            op_of_gate[i] = oid
    weights, skipped = chained_weights(g, bp.program)
    rows = []
    worst = None
    for w in weights:
        p_gates = set(gates_of[w.producer])
        u_gates = set(gates_of[w.update])
        # output gates of the producer: gates of p read by some gate outside p
        p_out = [i for i in p_gates if any(op_of_gate[c] != w.producer for c in consumers[i])]
        min_T = None
        n_el = 0
        for gp in p_out:
            # update gates for this element: gates of u reading gp, and everything of u downstream of them
            seeds = [c for c in consumers[gp] if c in u_gates]
            if not seeds:
                continue
            u_el = set(seeds)
            stack = list(seeds)
            while stack:
                x = stack.pop()
                for c in consumers[x]:
                    if c in u_gates and c not in u_el:
                        u_el.add(c)
                        stack.append(c)
            u_out = [i for i in u_el if not any(c in u_gates for c in consumers[i])] or list(u_el)
            # anc of the element's update output gate(s)
            anc = set(u_out)
            stack = list(u_out)
            while stack:
                x = stack.pop()
                for j in operands[x]:
                    if j not in anc and not flat.is_input[j]:
                        anc.add(j)
                        stack.append(j)
            # desc of the producer gate (bounded by anc: only what can matter)
            desc = {gp}
            stack = [gp]
            while stack:
                x = stack.pop()
                for c in consumers[x]:
                    if c not in desc and c in anc:
                        desc.add(c)
                        stack.append(c)
            T = sum(work[i] for i in desc)      # desc is already inside anc
            n_el += 1
            if min_T is None or T < min_T:
                min_T = T
        ok = min_T is not None and w.up_lb <= min_T
        row = {"tid": w.tid, "name": g.tensors[w.tid].name, "bytes": w.bytes, "elements": n_el, "up_lb": w.up_lb,
               "min_T": min_T, "ratio": (min_T / w.up_lb) if (min_T and w.up_lb) else None, "ok": ok,
               "between_ops": len(w.between)}
        rows.append(row)
        if not ok and (worst is None or (min_T or 0) - w.up_lb < (worst["min_T"] or 0) - worst["up_lb"]):
            worst = row
    return {"gates": n, "ops": len(g.ops), "chained": len(weights), "skipped_partial": skipped, "rows": rows,
            "violations": sum(1 for r in rows if not r["ok"]), "worst": worst}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    from accumulation.algorithms.registry import build
    from accumulation.redteam.harness import _versions
    doc = {"meta": {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "versions": _versions()}, "cells": []}
    total_v = 0
    for model, cfg, circuit, K, q, seq, wl in _cells():
        t0 = time.time()
        bp = build(circuit, cfg, wl)
        g = extract(bp)
        res = check_graph(bp, g)
        res.update(model=model, circuit=circuit, K=K, Q_step=q, seq=seq, seconds=round(time.time() - t0, 1))
        total_v += res["violations"]
        ratios = [r["ratio"] for r in res["rows"] if r["ratio"]]
        print(f"{model} {circuit} K={K} q={q} seq={seq}: {res['gates']} gates, {res['chained']} chained tensors "
              f"({res['skipped_partial']} skipped), violations {res['violations']}, "
              f"min_e T_e / Up_lb in [{min(ratios):.3f}, {max(ratios):.3f}]  ({res['seconds']}s)" if ratios else
              f"{model} {circuit} K={K}: no chained tensors")
        if res["worst"]:
            print("   worst:", res["worst"])
        doc["cells"].append(res)
    doc["meta"]["violations"] = total_v
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "wp_gatecheck.json"), "w") as fh:
        json.dump(doc, fh, indent=1, default=str)
    lines = ["# Weight-presence certificate: gate-level check of the op-level rule", "",
             f"Generated {doc['meta']['generated']} by `accumulation.redteam.wp_gatecheck`.  For every chained weight tensor of the tiny "
             "registry training circuits, `Up_lb` (op-level between work, `bounds/lower_wp.py`) must not exceed the smallest true "
             "upstream work `T_e` of any element's update gate inside the gate-level hull (`exact.solve.flatten`).", "",
             "| cell | gates | chained tensors | skipped (partial reads) | violations | min_e T_e / Up_lb |", "|---|---|---|---|---|---|"]
    for c in doc["cells"]:
        ratios = [r["ratio"] for r in c["rows"] if r["ratio"]]
        rng = f"[{min(ratios):.3f}, {max(ratios):.3f}]" if ratios else "-"
        lines.append(f"| {c['model']} {c['circuit']} K={c['K']} Q_step={c['Q_step']} seq={c['seq']} | {c['gates']} | {c['chained']} | "
                     f"{c['skipped_partial']} | {c['violations']} | {rng} |")
    lines += ["", f"**Total violations: {total_v}.**" + ("" if total_v == 0 else "  The op-level rule is NOT sound on these circuits.")]
    with open(os.path.join(args.out_dir, "wp_gatecheck.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"total violations: {total_v}")
    return 1 if total_v else 0


if __name__ == "__main__":
    sys.exit(main())
