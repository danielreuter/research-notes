"""once_rewrite.py SRC_DIR DST_DIR: a recorded request Program as the Build writes it under `weight_only_calls = "once"`: every Call that reads
only the weights parameter and repeats an earlier Call (same Definition, same operand runs) is dropped, and its readers read the first one.
Prints the Calls dropped, the committed words of the weight-only Calls before and after, and the gates removed."""
import gzip
import json
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
doc = json.load(gzip.open(src / "instances.json.gz"))
wparam = [i for i, (n, _t) in enumerate(doc["params"]) if n == "weights"]
assert len(wparam) == 1, doc["params"]
W = wparam[0]
first: dict = {}
new_index: dict[int, int] = {}
out = []
dropped: dict[str, int] = {}
for r in doc["rows"]:
    for a in r["args"]:
        for run in a:
            assert run[0] in ("n", "p"), run
    weight_only = bool(r["args"]) and all(run[0] == "p" and run[1] == W for a in r["args"] for run in a)
    key = (r["spec"], json.dumps(r["args"])) if weight_only else None
    if key is not None and key in first:
        new_index[r["i"]] = first[key]
        dropped[r["spec"]] = dropped.get(r["spec"], 0) + 1
        continue
    k = len(out)
    new_index[r["i"]] = k
    if key is not None:
        first[key] = k
    args = [[[run[0], new_index[run[1]] if run[0] == "n" else run[1], run[2], run[3]] for run in a] for a in r["args"]]
    out.append(dict(r, i=k, args=args))
dst.mkdir(parents=True, exist_ok=True)
with gzip.open(dst / "instances.json.gz", "wt") as f:
    json.dump(dict(doc, digest=None, rows=out), f)
print(json.dumps({"calls_before": len(doc["rows"]), "calls_after": len(out), "dropped": dropped, "weight_only_distinct": len(first)}))
