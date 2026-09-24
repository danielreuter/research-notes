"""Which v2 manifest members does the promoted rule select on a row's Programs of record?

A member (op_path, member) is promoted when the Programs name consumers for it and every consumer is inside op_path's module subtree
(v1_bridge.under): the Value is handed down by the producer module's body, it is no return of that module.

    promoted57.py <row dir>        (run from integrations/vllm with PYTHONPATH=.:../../packages/verity/src:../../tools/research/src)
"""
import json
import sys
import time
from collections import defaultdict

from verity_capture.commit import manifest_format as MF
from verity_capture.commit import oracle_compare as OC
from verity_vllm.query.v1_bridge import under

R = sys.argv[1]
t0 = time.time()


def log(*a):
    print(f"[{time.time() - t0:7.1f}s]", *a, flush=True)


with open(f"{R}/match/instances.jsonl") as f:
    reqs = json.loads(f.readline())["requests"]
fx = {"requests": [{"request_id": f"r{int(r['index'])}", "prompt_len": int(r["prompt_len"]), "max_tokens": int(r["max_tokens"])} for r in reqs]}
man = json.load(open(f"{R}/manifest.json"))
loaded = MF.programs_for(fx, R)
log("programs", len(loaded))
derived = OC.producers_of_programs(loaded, aliases=man.get("op_path_aliases"))
log("derived members", len(derived))
rows_of = defaultdict(int)
for r in man["identities"]:
    if r.get("family") == "instance_outputs":
        rows_of[(str(r["op_path"]), str(r["output_member"]))] += 1
picked = {k: v for k, v in derived.items() if v.get("consumers") and all(under(c, k[0]) for c in v["consumers"])}
by_module = defaultdict(list)
for (op, mem), v in sorted(picked.items()):
    by_module[op].append(mem)
    log("PROMOTED", op, mem, "spec", v.get("spec"), "consumers", v["consumers"][:4], "manifest rows", rows_of.get((op, mem), 0))
log("promoted members", len(picked), "modules", len(by_module), "modules with >1 member", {m: v for m, v in by_module.items() if len(v) > 1})
