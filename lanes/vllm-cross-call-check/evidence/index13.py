"""index13.py OLD_INDEX GRAPH_DIR PLAN_TABLE_JSON: the dataset's index.json from the regenerated graphs, plus the checks the handoff asks for:
per row, the structure against the previous index (calls, modules, groups, edges), the Q_word_v1 totals (no violation, no recompute
class), the max_scaled words against the vLLM coordinator's plan table, and whether the graph records param_inputs."""
import json
import sys
from pathlib import Path

old = json.loads(Path(sys.argv[1]).read_text())
gdir = Path(sys.argv[2])
plan = {int(k): v for k, v in json.loads(Path(sys.argv[3]).read_text()).items()}      # row -> max_scaled words (the plan's table)
report = []
for r in old["rows"]:
    g = json.loads((gdir / r["file"]).read_text())
    q = g["q_word_v1"]
    tokens = sum(x["calls"] for x in g["groups"] if x["definition"].startswith("Embedding"))
    now = {"calls": sum(p["calls"] for p in g["programs"]), "modules": len(g["modules"]), "groups": len(g["groups"]), "edges": len(g["edges"])}
    same = {k: now[k] == r.get(k) for k in now}
    ms = [t for t in q["taps"] if t["value"] == "F32MulFtz_v1" and t["activation"].split("{")[0].rsplit("_v", 1)[0] in ("AttnBlock", "AttnBlockSoftcap", "AttnBlockFA3")]
    ms_words = sum(t["words"] for t in ms)
    new = [t for t in q["taps"] if not t["committed_today"]]
    pin = sum(1 for x in g["groups"] if x.get("param_inputs"))
    r.update(bytes=(gdir / r["file"]).stat().st_size, q_word_v1={k: q[k] for k in ("query", "units", "gates", "free_gates", "redundant_gates",
                                                                                      "committed_interior_words", "units_per_gate", "violations")},
             new_taps=[{k: t[k] for k in ("activation", "value", "words", "bytes", "new_tap_in")} for t in new],
             param_inputs_groups=pin if pin else g["row"].get("param_inputs", "none"))
    rep = {"row": r["row"], "structure_equal": same, "violations": q["violations"], "redundant_gates": q.get("redundant_gates"),
           "max_scaled_words": ms_words, "plan_words": plan.get(r["row"]), "max_scaled_new_tap_in": sorted({t["new_tap_in"] for t in ms}),
           "new_tap_bytes_per_token": round(sum(t["bytes"] for t in new) / tokens) if tokens else None, "param_inputs_groups": pin}
    report.append(rep)
    print(json.dumps(rep), flush=True)
print(json.dumps({"rows": len(report), "all_structure_equal": all(all(x["structure_equal"].values()) for x in report),
                  "violations": sum(bool(x["violations"]) for x in report)}))
json.dump(old, open(gdir / "index.json", "w"), indent=1)
json.dump(report, open(gdir / "checks.json", "w"), indent=1)
