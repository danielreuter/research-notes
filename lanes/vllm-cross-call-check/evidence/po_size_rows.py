"""po_size_rows.py: po_size for #101 (its program graph: one request Program) and #74 (each request Program's instance sequence)."""
import glob
import json
import time
from collections import Counter

import po_size as S
from verity_vllm.query import word as W
from verity_vllm.query.program_view import iter_instance_rows

out = {}
t = time.time()
g = json.load(open("/tmp/xc/graphs/llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager.program.json"))
specs: Counter = Counter()
for x in g["groups"]:
    if x.get("varying"):
        (a,), = [tuple(x["varying"])]
        for v, k in x["varying_calls"].items():
            specs[W.specialization(x["definition"], dict(x["statics"], **{a: int(v)})).id] += k
    else:
        specs[x["spec"]] += x["calls"]
out["101"] = S.program_bytes(specs, sum(specs.values()))
print("#101", out["101"], f"{time.time() - t:.0f}s", flush=True)
for p in sorted(glob.glob("/tmp/xc/rows/74/*/instances.json.gz")):
    t = time.time()
    specs = Counter(r["spec"] for r in iter_instance_rows(p))
    r = out[f"74/{p.split('/')[-2]}"] = S.program_bytes(specs, sum(specs.values()))
    print("#74", p.split("/")[-2], r, f"{time.time() - t:.0f}s", flush=True)
json.dump(out, open("/tmp/xc/po_size.json", "w"), indent=1)
print("SIZE-DONE")
