"""contract.validate + tables.reject_reasons for every hostphase row (result.json files fetched from the pod)."""
import json
import sys

from verity.verification.target import BF16_HOPPER, FP8_HOPPER_WGMMA
from verity_numerical.bench import contract, tables

rows = json.load(open(sys.argv[1]))          # {run_id: path to result.json}
out = {}
for run, path in rows.items():
    r = json.load(open(path))
    problems = contract.validate(r)
    fp = r["workload_fingerprint"]
    prof = fp["profile"]
    target = BF16_HOPPER if prof == BF16_HOPPER.name else FP8_HOPPER_WGMMA
    cand = tables.candidate_for(fp["software"]["backend"]["name"])
    reasons = tables.reject_reasons(r, [], None, target, cand)
    m = {x["name"]: x["value"] for x in r["measurements"]}
    out[run] = {"validate": problems, "reject_reasons": reasons, "profile": prof, "proof_class": fp["proof_class"],
                "zk_mode": fp["zk_mode"][:40], "t.total": m["t.total"], "achieved_log2": fp["security"]["achieved_log2"],
                "commit": fp["software"]["backend"].get("commit"), "impl": fp["software"]["backend"].get("impl"),
                "gpu": fp["hardware"].get("gpu", {}).get("name"), "cpu": fp["hardware"].get("cpu", {}).get("model") or fp["hardware"].get("cpu"),
                "split": {k[6:]: round(v, 4) for k, v in m.items() if k.startswith("split.") and "seconds" in k},
                "t": {k[2:]: round(v, 4) for k, v in m.items() if k.startswith("t.")},
                "R_proved": m.get("R_proved") or m.get("rate.R_proved") or None,
                "meas_names": [k for k in m if not k.startswith(("split.", "t."))]}
    print(run, prof, fp["proof_class"], "t.total", round(m["t.total"], 4), "validate", problems, "reject", reasons)
json.dump(out, open(sys.argv[2], "w"), indent=1, default=str)
