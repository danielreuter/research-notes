import json, glob, os
from verity.verification import target as T
from verity_numerical.bench import contract, tables
EV = os.path.expanduser("~/.research/notes/lanes/fp4-fast/evidence")
for path in sorted(glob.glob(f"{EV}/r2026*/result.json")):
    r = json.load(open(path)); fp = r["workload_fingerprint"]
    tgt = T.NVFP4_SM120
    cand = tables.candidate_for(fp["software"]["backend"]["name"])
    m = {x["name"]: x["value"] for x in r["measurements"]}
    print(path.split("/")[-2], fp["profile"], fp["proof_class"][:22], "t.total", round(m["t.total"], 3), "validate", contract.validate(r), "reject", tables.reject_reasons(r, [], None, tgt, cand))
