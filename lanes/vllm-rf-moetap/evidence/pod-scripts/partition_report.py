"""partition_report.py OUT: the no-recompute partition checker (Q_word_v1{X=16,W=32,R=no-recompute}, verity.ir.partition.validate_unit_cut) on
the Definitions the two taps serve, at the served shapes, with the tapped values acquired: per Definition the strict cut (every gate certified
once, gate count exact), committed boundaries only, widths, recomputed gates, the committed interior words and the tap's words for them."""
import json
import sys
import time

from verity_vllm.query import router_softmax as RS
from verity_vllm.query import vocab_range as VR
from verity_vllm.query import word as W

rows = []
cases = [("MoeRouterTopKOrdered_v1", RS.router_fn(64, 8, 8, False), RS.TAP_WORDS["MoeRouterTopKOrdered_v1"]({"E": 64, "TOPK": 8}), "#67 #68 #70 OLMoE"),
         ("MoeRouterTopKOrderedNorm_v1", RS.router_fn(128, 8, 8, True), RS.TAP_WORDS["MoeRouterTopKOrderedNorm_v1"]({"E": 128, "TOPK": 8}), "#75 Qwen3-30B-A3B"),
         ("EmbeddingShard_v1", VR.shard_fn(25152, 2048, 0), VR.WORDS, "#70 rank 0 (OLMoE V=50304, TP2)"),
         ("EmbeddingShard_v1", VR.shard_fn(25152, 2048, 25152), VR.WORDS, "#70 rank 1"),
         ("EmbeddingShard_v1", VR.shard_fn(75968, 2048, 0), VR.WORDS, "#75 rank 0 (Qwen3-30B-A3B V=151936, TP2)"),
         ("EmbeddingShard_v1", VR.shard_fn(75968, 2048, 75968), VR.WORDS, "#75 rank 1")]
for fam, fn, tap, where in cases:
    t0 = time.time()
    G = W.Graph(fn)
    R = W.units(G, 16, 32)
    rule = W.unit_rule(fn)
    cut = R["cut"].to_json()
    row = {"definition": fn.id, "rows": where, "gates": int(G.total), "structure_gates": int(G.free), "computing_units": cut["detail"].get("computing_units"),
           "units_per_call": rule["units_per_call"], "by_kind": rule["by_kind"], "cut_ok": cut["ok"], "cut_codes": cut["codes"],
           "certified": cut["detail"].get("certified"), "input_gates": cut["detail"].get("input_gates"), "committed": cut["detail"].get("committed"),
           "cross_unit_reads": cut["detail"].get("cross_unit_reads"), "recomputed_gates": len(G.recomputed),
           "committed_interior_words": rule["committed_interior_words"], "committed_interior": rule["committed_interior"],
           "tap_words": tap, "acquired_all": rule["committed_interior_words"] == tap, "max_out_bits": rule["max_out_bits"],
           "width_violations": [v for v in rule["violations"] if v.get("class") != "cut"], "violations": rule["violations"],
           "seconds": round(time.time() - t0, 1)}
    if fam in RS.ROUTERS:
        row["slots_in_tap_order"] = len(RS.slots(int(fn.id.split("E=")[1].split(",")[0]), 8, 8, RS.ROUTERS[fam]))
    rows.append(row)
    print(json.dumps({k: v for k, v in row.items() if k not in ("committed_interior", "violations")}), flush=True)
ok = all(r["cut_ok"] and r["recomputed_gates"] == 0 and r["acquired_all"] and not r["violations"] for r in rows)
json.dump({"query": W.query_id(16, 32), "ok": ok, "definitions": rows}, open(sys.argv[1], "w"), indent=1)
print(("PARTITION-OK" if ok else "PARTITION-FAIL"), sys.argv[1], flush=True)
