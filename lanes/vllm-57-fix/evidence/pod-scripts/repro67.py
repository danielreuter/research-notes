"""#67 offline check over the fresh Build's Programs + manifest (no GPU), before its Commit: population reconciliation (R17-3,
the sweep's 20,928 identities_without_rows) and which members 2c5e038b's promoted rule selects.

Run on vyv-sw-67b from <src>/integrations/vllm with PYTHONPATH=.:../../packages/verity/src:../../tools/research/src.
  repro67.py <row dir> <workload json>
"""
import json
import sys
import time
from collections import Counter, defaultdict

R, W = sys.argv[1], sys.argv[2]
t0 = time.time()


def log(*a):
    print(f"[{time.time() - t0:7.1f}s]", *a, flush=True)


from verity_capture.commit import manifest_format as MF
from verity_capture.commit import oracle_compare as OC
from verity_capture.commit import sampled_replay as SR
from verity_vllm.query.v1_bridge import under

reqs = json.load(open(W))["requests"]
fx = {"requests": [{"request_id": f"r{int(r['index'])}", "prompt_len": int(r["prompt_len"]), "max_tokens": int(r["max_tokens"])} for r in reqs]}
man = json.load(open(f"{R}/manifest.json"))
log("manifest", len(man["identities"]), "rule", SR.address_rule_of(man), "families", dict(Counter(i.get("family") for i in man["identities"])))
loaded = MF.programs_for(fx, R)
log("programs", len(loaded))

arrive = {}
for i in man["identities"]:
    if i.get("step") not in (None, "*") and i.get("engine_step") is not None and i.get("request_id") not in (None, "*"):
        arrive.setdefault(str(i["request_id"]), int(i["engine_step"]) - int(i["step"]))
addresses, indices, vus_n = {}, {}, 0
for rid, v in loaded.items():
    inst = v["instances"]
    pi = indices.get(id(inst))
    if pi is None:
        pi = SR.ProgramIndex(inst, padded_slots=SR.manifest_boundary_of(man) == "module-pad", promoted=SR.promoted_addresses_of(man),
                             rule=SR.address_rule_of(man), program_dir=v.get("dir"))
        indices[id(inst)] = pi
    vus, ne, nef = SR.population(pi, rid, rank=0, arrive=arrive.get(rid, 0), addresses=addresses, last_step=pi.n_steps - 1)
    vus_n += len(vus)
log("vus", vus_n)
qp = SR.query_population(man, addresses, set(), ranks=[0])
qc = qp["query_checks"]
log("query_checks ok", qc.get("ok"), "accounted", qc.get("accounted"))
for k in ("vus_outside_query", "identities_without_rows", "identities_unreachable_by_alias", "rows_disagree"):
    c = qc.get(k) or {}
    log(" ", k, c.get("n"), json.dumps(c.get("first", [])[:3])[:600])

derived = OC.producers_of_programs(loaded, aliases=man.get("op_path_aliases"))
log("derived members", len(derived), "conflicts", sum(1 for d in derived.values() if d.get("conflict")))
rows_of = defaultdict(int)
for r in man["identities"]:
    if r.get("family") == "instance_outputs":
        rows_of[(str(r["op_path"]), str(r["output_member"]))] += 1
picked = {k: v for k, v in derived.items() if v.get("consumers") and all(under(c, k[0]) for c in v["consumers"])}
shapes = Counter()
for (op, mem), v in sorted(picked.items()):
    import re
    shapes[(re.sub(r"layers\.\d+", "layers.N", op), mem, str(v.get("spec"))[:60], tuple(re.sub(r"layers\.\d+", "layers.N", c) for c in v["consumers"][:3]))] += rows_of.get((op, mem), 0)
for k, n in shapes.most_common(15):
    log("PROMOTED", k, "manifest rows", n)
log("promoted members", len(picked), "manifest rows", sum(rows_of.get(k, 0) for k in picked))
