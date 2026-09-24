"""construction_version of THIS tree (the one on PYTHONPATH) next to the values the recorded Builds carry.

    python cv_evidence.py TAG
"""
import collections
import glob
import json
import sys

from verity_vllm.harness.derive_step import construction_version
from verity_vllm.program.frontend.rules.vllm_bindings import VLLM_BINDING_RULES

cv = construction_version(VLLM_BINDING_RULES)
out = {"tree": sys.argv[1], "sources_sha256": cv["sources_sha256"], "n_files": len(cv["files"]),
       "files_hashed_as_missing": sum(1 for f in cv["files"] if f["sha256"] is None), "n_rules": len(cv["rules"])}
rec = collections.Counter()
for p in sorted(glob.glob("/workspace/regress/records/*/build_*/artifact.json")):
    a = json.load(open(p))["construction_version"]
    rec[(a["sources_sha256"], sum(1 for f in a["files"] if f["sha256"] is None), len(a["files"]), a["sources_sha256"] == cv["sources_sha256"])] += 1
out["recorded_builds"] = [{"sources_sha256": k[0], "files_hashed_as_missing": f"{k[1]}/{k[2]}", "equals_this_tree": k[3], "n_builds": n}
                          for k, n in rec.most_common()]
print(json.dumps(out, indent=1))
