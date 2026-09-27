"""vo_digests.py ROW_DIR EXPECTED_JSON OUT_JSON: one Build (a sweep row dir) against the row's record
(`tests/regression/expected/<row>.json`): the step, main request and every shape's Program digest, GP-01's workload digest, and the
required-value manifest (manifest_digest, keyed program digest, identity count, identity_rows_sha256 as `tests/regression/checks/
manifest_digest.py` computes them).  Prints one line per item (= / DIFF) and writes the comparison."""
import hashlib
import json
import sys
from pathlib import Path

from verity_vllm.query.manifest.format import IDENTITY_KEY

row, exp = Path(sys.argv[1]), json.load(open(sys.argv[2]))
bs = json.load(open(row / "build_summary.json"))
rec = exp["program_digest"]["build_summary"]
got = {"step": (bs.get("step") or {}).get("program_digest"), "request": (bs.get("request") or {}).get("program_digest"),
       "workload": (bs.get("workload") or {}).get("workload_digest")}
want = {"step": rec["step"], "request": rec["request"], "workload": rec["workload"]}
for k, v in rec["shapes"].items():
    got[k] = (bs.get(k) or {}).get("program_digest")
    want[k] = v
extra = sorted(k for k in bs if k.startswith("build_request_") and k not in rec["shapes"])


def identity_rows_sha256(ids):
    rows = sorted(json.dumps([r[k] if k != "element_range" else list(r[k]) for k in IDENTITY_KEY], separators=(",", ":"),
                             sort_keys=True).encode() for r in ids)
    h = hashlib.sha256()
    for b in rows:
        h.update(b)
        h.update(b"\n")
    return h.hexdigest()


man = {}
if (row / "manifest.json").is_file():
    m = json.load(open(row / "manifest.json"))
    man = {"manifest_digest": m.get("manifest_digest"), "program_digest": m.get("program_digest"),
           "identities": (m.get("populations") or {}).get("identities", len(m.get("identities") or [])),
           "complete": m.get("complete"), "identity_rows_sha256": identity_rows_sha256(m.get("identities") or [])}
em = exp["manifest_digest"]
for k in ("manifest_digest", "program_digest", "identities", "complete", "identity_rows_sha256"):
    if k in em:
        got[f"manifest.{k}"], want[f"manifest.{k}"] = man.get(k), em[k]
res = {k: {"got": got[k], "record": want[k], "equal": got[k] == want[k]} for k in want}
out = {"row_dir": str(row), "all_equal": all(v["equal"] for v in res.values()), "items": res, "shapes_not_in_record": extra}
json.dump(out, open(sys.argv[3], "w"), indent=1)
for k, v in res.items():
    print(f"  {'=   ' if v['equal'] else 'DIFF'} {k}: {str(v['got'])[:16]} (record {str(v['record'])[:16]})")
print(f"DIGESTS {row.name}: all_equal={out['all_equal']} ({sum(v['equal'] for v in res.values())}/{len(res)})", flush=True)
