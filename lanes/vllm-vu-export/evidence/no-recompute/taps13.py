"""taps13.py IN_DIR OUT_DIR: each row's program.json under Q_word_v1 R=no-recompute (recorded Definitions) into OUT_DIR, and the row's tap
list with the MoE router stated round by round (taps13.json): per class of committed interior value, where serving commits it today or
the kernel a new tap goes in, with words, bytes and bytes per token."""
import copy
import json
import sys
import time
from pathlib import Path

from verity_vllm.pipeline import program_graph as PG
from verity_vllm.program.registry import moe

SUB = {"MoeRouterTopK_v1": moe.MoeRouterTopKOrdered, "MoeRouterTopKNorm_v1": moe.MoeRouterTopKOrderedNorm}
src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
report = json.load(open(out / "taps13.json")) if (out / "taps13.json").exists() else {}
only = sys.argv[3:]
for f in sorted(src.glob("*.program.json")):
    if f.name[: -len(".program.json")] in report or (only and not any(o in f.name for o in only)):
        continue
    t = time.time()
    g = json.loads(f.read_text())
    for x in g["groups"]:
        x.pop("q_word_v1", None)
    rec = PG.with_word_rules(copy.deepcopy(g))
    (out / f.name).write_text(json.dumps(rec, separators=(",", ":"), default=str) + "\n")
    has_router = any(x["definition"] in SUB for x in g["groups"])
    rnd = PG.with_word_rules(copy.deepcopy(g), substitute=SUB) if has_router else rec
    tokens = sum(x["calls"] for x in g["groups"] if x["definition"].startswith("Embedding"))
    row = {"row": g["row"].get("row"), "tokens": tokens, "recorded": {k: rec["q_word_v1"][k] for k in ("units", "gates", "free_gates", "committed_interior_words", "violations")},
           "rounds_router": {k: rnd["q_word_v1"][k] for k in ("units", "gates", "free_gates", "committed_interior_words", "violations")},
           "taps": [dict(t_, bytes_per_token=round(t_["bytes"] / tokens, 1) if tokens else None) for t_ in rnd["q_word_v1"]["taps"]],
           "recorded_router_taps": [dict(t_, bytes_per_token=round(t_["bytes"] / tokens, 1) if tokens else None) for t_ in rec["q_word_v1"]["taps"]
                                    if t_["activation"].startswith("MoeRouter")]}
    report[f.name[: -len(".program.json")]] = row
    new = [t_ for t_ in row["taps"] if not t_["committed_today"]]
    print(f"#{row['row']} {f.name[:40]} tokens={tokens} committed={rnd['q_word_v1']['committed_interior_words']:,} new-tap words={sum(t_['words'] for t_ in new):,} "
          f"bytes/token={sum(t_['bytes_per_token'] or 0 for t_ in new):.1f} viol={rnd['q_word_v1']['violations']} {time.time() - t:.0f}s", flush=True)
    json.dump(report, open(out / "taps13.json", "w"), indent=1)
