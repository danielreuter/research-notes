"""validate_definitions.py OUT_JSON EXPORT_DIR... : re-evaluate sample inputs of each exported set through the IR's reference
evaluator (`verity.evaluation.evaluate` on the registered Definition, plain ints) and compare with the recorded outputs.

Each set's Definition is bound from the set's relation: GemmCoordinate_v1{K} for a GEMM coordinate set, AttentionHead_v3{T,D,BN}
for an attention head (T from the instance), RoPEHead_v1{D}, else the row's own Definition and statics.  Up to 3 inputs per set
(the smallest-T ones for attention); an input whose evaluation raises is recorded with the reason."""
import json
import sys
import time
from pathlib import Path

import numpy as np

from verity.evaluation import evaluate
from verity.ir.codec import canonical_json
from verity_vllm.pipeline import program_graph as PG
from verity_vllm.pipeline import vu_export as VX

SAMPLES = 3


def target(rel: dict, sub: dict) -> tuple[str, dict]:
    """The row's own Definition, at one output unit for a decomposed set: Gemm at N = 1 (one coordinate), Attention at NH = KVH = 1
    (one head, T from the instance), RoPE at NHEADS = 1; its body's callee is the subcircuit the set's inputs belong to."""
    from verity_vllm.query.program_view import spec_statics
    st = spec_statics(rel["definition"] + "{" + ",".join(f"{k}={v}" for k, v in (rel.get("statics") or {}).items()) + "}")
    fam, t = rel["definition"], rel.get("subcircuit", "")
    if t.startswith("GemmCoordinate"):
        return fam, dict(st, N=1, **({"DOT": rel["dot"]} if fam != "Gemm_v1" else {}))
    if t.startswith("AttentionHead"):
        return fam, dict(st, T=sub["T"], NH=1, KVH=1, **({"DOT": rel["dot"], "INV": rel["inv"]} if fam != "Attention_v3" else {}))
    if t.startswith("RoPEHead"):
        return fam, dict(st, NHEADS=1)
    return fam, st


PORTS = {"GemmCoordinate": (["x", "w"], ["y"]), "AttentionHead": (["q", "k", "v"], ["out"]), "RoPEHead": (["x", "cs"], ["out"])}


def ports_of(rel: dict, P: dict) -> tuple[list, list]:
    t = rel.get("subcircuit", "")
    for k, v in PORTS.items():
        if t.startswith(k):
            return v
    ins = sorted((k for k in P if k.startswith("in")), key=lambda k: int(k[2:]))
    outs = sorted((k for k in P if k.startswith("out.")), key=lambda k: (not k[4:].isdigit(), int(k[4:]) if k[4:].isdigit() else k))
    return ins, outs


def main(out: str, *exports: str) -> None:
    from verity_vllm.query.program_view import _registry
    reg, _ = _registry()
    results = []
    for e in exports:
        for d in sorted((Path(e) / "sets").iterdir()):
            man = json.loads((d / "manifest.json").read_text())
            idx = json.loads((d / "index.json").read_text())["rows"]
            n, rel = int(man["n"]), man["relation"]
            P = {k: VX._read_port(d, p, n) for k, p in man["ports"].items()}
            order = list(range(n))
            if "k" in P:                                                # attention: the shortest, a middle and the longest history
                order.sort(key=lambda i: P["k"][i].size)
                order = [order[0], order[len(order) // 2], order[-1]]
            for i in order[:SAMPLES]:
                sub = idx[i][-1]
                base, st = target(rel, sub)
                ins, outs = ports_of(rel, P)
                t0 = time.perf_counter()
                rec = {"set": man["set"], "export": str(e), "instance": idx[i][0], "definition": None, "digest": None}
                try:
                    sp = PG._specialization(base, st)
                    fid, defs = PG._encoded(sp)
                    rec["definition"], rec["digest"] = fid, PG.definition_digest(defs[fid])
                    callees = sorted({n["fn"] for n in defs[fid].get("body", {}).get("nodes", [])} - {fid})
                    rec["subcircuit_definitions"] = {c: PG.definition_digest(defs[c]) for c in callees if c in defs and defs[c].get("form") == "composite"}
                    got = evaluate(sp, *[[int(v) for v in P[k][i].tolist()] for k in ins])
                    want = [int(v) for k in outs for v in P[k][i].tolist()]
                    rec["ok"] = list(got) == want
                    if not rec["ok"]:
                        rec["first_diff"] = next((j for j, (a, b) in enumerate(zip(got, want)) if a != b), min(len(got), len(want)))
                except Exception as ex:  # noqa: BLE001
                    rec["ok"], rec["why"] = None, f"{type(ex).__name__}: {ex}"[:300]
                rec["seconds"] = round(time.perf_counter() - t0, 2)
                results.append(rec)
                print(json.dumps(rec), flush=True)
    Path(out).write_text(json.dumps({"schema": "vllm-program-graph/validation/v1",
                                     "rule": "verity.evaluation.evaluate(registered Definition, recorded input words) == the recorded output words",
                                     "results": results}, indent=1) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], *sys.argv[2:])
