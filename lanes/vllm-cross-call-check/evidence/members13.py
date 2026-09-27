"""members13.py GRAPH_DIR: word.unit_rule's member check (PR #98) over every separable Definition of the 13 rows' groups (a varying
static at its recorded endpoints): per row, the Definitions whose members compute a value twice, with the gates per Call and in all."""
import json
import sys
from pathlib import Path

from verity_vllm.query import word as W

memo: dict = {}
out = {}
for f in sorted(Path(sys.argv[1]).glob("*.program.json")):
    g = json.loads(f.read_text())
    hits = []
    for x in g["groups"]:
        vals = [dict(x["statics"])]
        if x.get("varying") and len(x["varying"]) == 1:
            (a, (lo, hi)), = x["varying"].items()
            vals = [dict(x["statics"], **{a: int(lo)}), dict(x["statics"], **{a: int(hi)})]
        for st in vals:
            try:
                fn = W.specialization(x["definition"], st)
            except Exception:
                continue
            if not hasattr(fn, "body") or W._separable(fn) is None:
                continue
            r = W.unit_rule(fn, memo=memo)
            for v in r["violations"]:
                if v["class"] == "cut" and "gate-recomputed" in v.get("codes", []):
                    n = v["detail"]["gate-recomputed"]["n"]
                    hits.append({"group": x["id"], "module": x["module"], "definition": fn.id, "calls": x["calls"], "gates_per_call": n,
                                 "classes": [(c["definition"], c["level"], c["calls"], c["gates"]) for c in v["detail"]["gate-recomputed"]["classes"]]})
            if len(vals) == 2:
                break
    out[g["row"]["row"]] = hits
    print(g["row"]["row"], len(hits), sum(h["calls"] * h["gates_per_call"] for h in hits), sorted({h["definition"].split("{")[0] for h in hits}), flush=True)
json.dump(out, open(Path(sys.argv[1]) / "members13.json", "w"), indent=1)
