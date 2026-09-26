"""rc13.py IN_DIR OUT.json: every row's groups under Q_word_v1 (recorded Definitions): violations and redundant gates by Definition."""
import copy, json, sys, time
from pathlib import Path
from verity_vllm.pipeline import program_graph as PG
src, out = Path(sys.argv[1]), Path(sys.argv[2])
rep = json.loads(out.read_text()) if out.exists() else {}
for f in sorted(src.glob("*.program.json")):
    name = f.name[: -len(".program.json")]
    if name in rep:
        continue
    t = time.time()
    g = json.loads(f.read_text())
    for x in g["groups"]:
        x.pop("q_word_v1", None)
    r = PG.with_word_rules(copy.deepcopy(g))
    defs = {}
    for x in r["groups"]:
        q = x.get("q_word_v1", {})
        d = defs.setdefault(x["definition"], {"calls": 0, "violations": [], "redundant_gates_per_call": q.get("per_call", {}).get("redundant_gates"), "unresolved": q.get("unresolved")})
        d["calls"] += x["calls"]
        for v in q.get("violations", []):
            d["violations"].append({k: v[k] for k in ("class", "codes") if k in v})
    rep[name] = {"row": g["row"].get("row"), "violations": r["q_word_v1"]["violations"], "redundant_gates": r["q_word_v1"].get("redundant_gates"),
                 "definitions": defs}
    bad = {k: v for k, v in defs.items() if v["violations"] or v["unresolved"]}
    red = {k: v["redundant_gates_per_call"] for k, v in defs.items() if v["redundant_gates_per_call"]}
    print(f"#{rep[name]['row']} {name[:44]} viol={r['q_word_v1']['violations']} bad={list(bad)} redundant/call={red} {time.time()-t:.0f}s", flush=True)
    out.write_text(json.dumps(rep, indent=1))
