"""Table 2 validity predicate on a result.json (no labels, no attempt): python 02_reject.py RESULT TARGET_NAME"""
import json
import sys

from verity.verification.target import TARGETS
from verity_numerical.bench import tables as T

res = json.load(open(sys.argv[1]))
tgt = TARGETS[sys.argv[2]]
cand = next(c for c in T.CANDIDATES if c.id == "A-GKR")
for r in T.reject_reasons(res, [], None, tgt, cand):
    print("REJECT", r)
fp = res["workload_fingerprint"]
print("t.total", res.get("t", {}).get("total"), "class", fp.get("proof_class"), "sec", json.dumps(fp.get("security")))
