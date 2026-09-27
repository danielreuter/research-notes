"""label13.py GRAPH_DIR FILE...: Q_word_v1 (program_graph.with_word_rules) on the named program.json files of GRAPH_DIR, in place."""
import copy
import json
import sys
import time
from pathlib import Path

from verity_vllm.pipeline import program_graph as PG

for name in sys.argv[2:]:
    f = Path(sys.argv[1]) / name
    t = time.time()
    g = json.loads(f.read_text())
    for x in g["groups"]:
        x.pop("q_word_v1", None)
    g = PG.with_word_rules(copy.deepcopy(g))
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(g, separators=(",", ":"), default=str) + "\n")
    tmp.replace(f)
    q = g["q_word_v1"]
    print(f"{name[:48]} units={q['units']} gates={q['gates']} committed={q['committed_interior_words']} viol={q['violations']} {time.time() - t:.0f}s",
          flush=True)
