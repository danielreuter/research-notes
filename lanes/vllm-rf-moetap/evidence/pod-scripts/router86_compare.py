"""router86_compare.py RECORD OUT: for the edge rows of a router-tap exactness record, the words PR #86's MoeRouterProbs statement would
have committed (`_router_probs(interior=False)`: FA2's fast-math F32Max for the row max, the registry's x86 NaN encodings) next to the
words the tapped kernel wrote (the IR's committed gates after the fix).  CPU only; the edge rows are regenerated with the GPU driver's
seeds (`rows_of(E, 2026 + configuration index, ...)`, edge rows first).  Run from integrations/vllm with the tree on PYTHONPATH."""
import json
import random
import sys

from tests.properties.router_tap_exactness_gpu import edge_rows, rows_of
from verity.evaluation.reference import standalone_call
from verity.ir.defs import CompositeDefinition, bind
from verity.ir.evaluate import evaluate_call
from verity.ir.types import Array
from verity_vllm.program.registry import moe
from verity_vllm.program.registry.prims import BF16, F32
from verity_vllm.properties import router_tap_exactness as X
from verity_vllm.query import router_softmax as RS
from verity_vllm.query import word as W

Probs86 = CompositeDefinition("Probs86", 1, ("E", "VPT"), lambda S: ((("logits", Array(S.E, BF16)),), Array(S.E, F32)),
                              lambda B, S, logits: moe._array(moe._router_probs(B, S.E, S.VPT, logits)), register=False)
_CACHE = {}


def old_words(E, row):
    """max, ex[E], rcp, p[E] of #86's statement: its committed interior gates (max, ex, rcp) and its returned probabilities."""
    if E not in _CACHE:
        fn = bind(Probs86, E=E, VPT=8)
        G = W.Graph(fn)
        R = W.units(G, 16, 32)
        owner, kinds = R["owner"], R["kinds"]
        crossing = set(G.src[owner[G.src] != owner[G.dst]].tolist())
        interior = [int(G.keep[g]) for g in sorted(g for g in crossing if kinds[owner[g]] == "committed")]
        assert len(interior) == E + 2, len(interior)
        _CACHE[E] = (standalone_call(fn), interior)
    (prog, call), interior = _CACHE[E]
    t = {}
    out = evaluate_call(prog.circuit, call, [int(v) & 0xFFFF for v in row], transcript=t)
    return [t[call.lo + j] & 0xFFFFFFFF for j in interior] + [v & 0xFFFFFFFF for v in out]


doc = json.load(open(sys.argv[1]))
report = []
for i, c in enumerate(doc["configs"]):
    E, K, renorm = int(c["E"]), int(c["TOPK"]), bool(c["renormalize"])
    n_edge = len(edge_rows(E, random.Random(0)))
    named = dict(list(rows_of(E, 2026 + i, 0).items())[:n_edge])
    for name, row in named.items():
        tap = c["edge_taps"][name]
        old = old_words(E, row)
        new = tap[: 2 * E + 2]
        diff = [{"i": j, "value": X.classify(E, K, renorm, j), "tap": new[j], "pr86": old[j]} for j in range(2 * E + 2) if new[j] != old[j]]
        nan_ex = next((j for j in range(1, E + 1) if (new[j] & 0x7F800000) == 0x7F800000 and new[j] & 0x7FFFFF), None)
        report.append({"config": c["name"], "row": name, "max": {"tap": new[0], "pr86": old[0]}, "rcp": {"tap": new[E + 1], "pr86": old[E + 1]},
                       "first_nan_ex": None if nan_ex is None else {"i": nan_ex, "tap": new[nan_ex], "pr86": old[nan_ex]},
                       "words_differ": len(diff), "values_differ": sorted({d["value"] for d in diff}), "first_diffs": diff[:4]})
json.dump(report, open(sys.argv[2], "w"), indent=1)
for r in report:
    if r["words_differ"] or r["row"] in ("NaN first", "NaN heads thread 1", "negative NaN", "all NaN", "subnormal logits"):
        print(f"{r['config']:12s} {r['row']:22s} max tap {r['max']['tap']:#010x} pr86 {r['max']['pr86']:#010x}  rcp tap {r['rcp']['tap']:#010x} "
              f"pr86 {r['rcp']['pr86']:#010x}  nan-ex {r['first_nan_ex']}  words differ {r['words_differ']} {r['values_differ']}")
print("rows", len(report), "rows with a difference", sum(1 for r in report if r["words_differ"]))
