"""word_row.py GRAPH MAP: Q_word_v1{16,32,no-recompute} (PR #98's unit_rule with its members check) over one row's groups, recorded
construction vs the construction map (module:NAME) applied to every group whose Definition it restates.  Each distinct substituted
specialization is cut fresh, before and after; every other group's summary is the program graph's (art:c74deac4, same Definition).
Prints per specialization: Calls, violations, units, gates, committed interior words; and the row's totals both ways."""
import importlib
import json
import sys
import time
from collections import defaultdict

from verity.ir.defs import bind
from verity_vllm.query import word as W

g = json.load(open(sys.argv[1]))
mod, name = sys.argv[2].split(":")
MAP = getattr(importlib.import_module(mod), name)
memo: dict = {}
by_spec = defaultdict(int)
other = {"calls": 0, "violations": 0, "committed_interior_words": 0, "units": 0, "gates": 0}
for x in g["groups"]:
    if x["definition"] in MAP:
        by_spec[(x["definition"], json.dumps(x["statics"], sort_keys=True))] += x["calls"]
    else:
        q = x["q_word_v1"]
        other["calls"] += x["calls"]
        other["violations"] += len(q.get("violations") or [])
        for k in ("committed_interior_words", "units", "gates"):
            other[k] += int(q.get(k) or 0)
tot = {"recorded": dict(other), "substituted": dict(other)}
for (fam, st), calls in sorted(by_spec.items()):
    statics = json.loads(st)
    for label, fn in (("recorded", W.specialization(fam, statics)), ("substituted", bind(MAP[fam], **statics))):
        t = time.time()
        r = W.unit_rule(fn, memo=memo)
        v = [(a["class"], a.get("codes"), (a.get("detail") or {}).get("gate-recomputed", {}).get("n")) for a in r["violations"]]
        print(json.dumps({"construction": label, "definition": fn.id, "calls": calls, "gates_per_call": r["gates"], "units_per_call": r["units_per_call"],
                          "by_kind": r["by_kind"], "committed_interior_words_per_call": r["committed_interior_words"],
                          "committed_interior": r["committed_interior"], "violations": v, "redundant_gates": r.get("redundant_gates"),
                          "seconds": round(time.time() - t, 1)}), flush=True)
        T = tot[label]
        T["calls"] += calls
        T["violations"] += len(v)
        T["committed_interior_words"] += r["committed_interior_words"] * calls
        T["units"] += r["units_per_call"] * calls
        T["gates"] += r["gates"] * calls
        T.setdefault("recomputed_gates", 0)
        T["recomputed_gates"] += sum(n or 0 for _c, _k, n in v) * calls
print(json.dumps({"row": g["row"]["row"], "map": sys.argv[2], "totals": tot}, indent=1))
