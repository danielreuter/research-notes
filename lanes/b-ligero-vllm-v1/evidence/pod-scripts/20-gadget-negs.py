"""Supplementary negatives on the vllm-v1 position-leaf gadget's own rows (the 86-battery's 60 row picks all land on the operand bit
rows hash.a[i].b*, before the gadget).  One row per (name with digits normalized, kind) among rows named *.vllm.*,
a random representative of the class, +delta in a random VU column; every proof must be rejected.
env: REL (default fp8-ada-x4), CAP (max classes, default 400), OUT (json path)."""
import collections
import json
import os
import re
import sys
import time
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, os.getcwd())
from backends.direct.ligero import relchain as rc  # noqa: E402
from backends.direct.ligero.compile import P  # noqa: E402
from backends.direct.ligero.relations import relation  # noqa: E402

rel_name = os.environ.get("REL", "fp8-ada-x4")
cap = int(os.environ.get("CAP", "400"))
out = os.environ.get("OUT", f"gadget-negs-{rel_name}.json")
rel = relation(rel_name)
args = SimpleNamespace(device="cuda", target=-128.0, rate_log2=2, zk=True, mode="interactive", auth="included-hash",
                       leaf="vllm-v1")
R = rc.make_runner(args, rel)
print(f"{R.relation}: {R.sys.summary()}; census {R.hr.census}", flush=True)
data = rc.instances(rel, 4, procs=4)
R.commit_vus(data, manifest_sha256=rc.instances_digest(rel, 4))
steps = R.steps
base, ids = data[:2], [0, 1]
proof, pubs, lay = R.prove_vus(base, check=True, vu_ids=ids)
ok, why = R.verify_vus(proof, pubs, lay)
print(f"honest 2-VU proof: {ok} {why}", flush=True)
assert ok, why

classes = collections.defaultdict(list)
for r in R.sys.rows:
    if ".vllm." in r.name:
        classes[(re.sub(r"\d+", "#", r.name), r.kind)].append(r)
print(f"{sum(len(v) for v in classes.values())} gadget rows in {len(classes)} classes", flush=True)
rng = np.random.default_rng(17)
keys = sorted(classes)[:cap]
report = {"relation": R.relation, "leaf": R.leaf.name, "system": R.sys.summary(), "honest": [ok, why],
          "classes": len(classes), "negatives": []}
failures = 0
t0 = time.perf_counter()
for key in keys:
    r = classes[key][int(rng.integers(0, len(classes[key])))]
    col = int(rng.integers(0, 2 * steps))
    delta = int(rng.integers(1, 3))

    def mutate(W, idx_=r.idx, col=col, delta=delta, kind=r.kind):
        if kind == "inv":
            nz = (W[idx_, :2 * steps] != 0).nonzero().flatten()
            col = int(nz[col % len(nz)]) if len(nz) else col
        W[idx_, col] = (W[idx_, col] + delta) % P
    pf, pb, ly = R.prove_vus(base, check=False, mutate=mutate, vu_ids=ids)
    acc, why = R.verify_vus(pf, pb, ly)
    failures += bool(acc)
    name = f"row {r.name} ({r.kind}; class {key[0]}, {len(classes[key])} rows) +{delta} in column {col}"
    print(f"  negative {name}: {'ACCEPTED (BUG)' if acc else 'REJECTED'} {why}", flush=True)
    report["negatives"].append({"name": name, "accepted": bool(acc), "why": why})
report["failures"] = failures
report["seconds"] = time.perf_counter() - t0
print(f"{R.relation} vllm-v1 gadget negatives: {len(keys)} of {len(classes)} classes, {failures} failures "
      f"in {report['seconds']:.0f}s", flush=True)
with open(out, "w") as f:
    json.dump(report, f, indent=1, default=str)
sys.exit(2 if failures else 0)
