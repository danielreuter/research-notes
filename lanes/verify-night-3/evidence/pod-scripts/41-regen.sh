#!/usr/bin/env bash
# verify-night-3: re-run instance_equiv for REL at N in tree SRC and compare it field by field with the instance-equiv/v1 artifact
# (the artifact's meta minus the producer's tags), then `--check` the stored doc when the tool can name its relation.
# usage: 41-regen.sh SRC EQUIV_ART REL N [RESULT_ART]     writes $W/regen-<art8>-<tree>/
set -uo pipefail
source "$(dirname "$0")/lib.sh"
S=$1; E=$2; REL=$3; N=$4; RES=${5:-}
export PYTHONPATH="$S/packages/verity/src:$S/backends/numerical/python:$S/tools/research/src:$S"
O=$W/regen-${E:4:8}-$(basename $S); mkdir -p $O; cd $S
R data show $E --json > $O/art.json || { echo "ERROR show $E"; exit 2; }
[ -n "$RES" ] && R data show $RES --json > $O/result.json
t0=$(date +%s)
$PY -m verity_numerical.bench.instance_equiv --relation $REL --vus $N --out $O/regen.json 2>&1 | tail -3
echo "regen seconds=$(( $(date +%s) - t0 ))"
$PY - $O <<'EOF' | tee $O/compare.json
import json, sys
from pathlib import Path
o = Path(sys.argv[1])
m = json.loads((o / "art.json").read_text())["manifest"]["meta"]
tags = [k for k in ("lane", "provenance", "for_result", "note", "produced_by_run") if k in m]
doc = {k: v for k, v in m.items() if k not in tags}
new = json.loads((o / "regen.json").read_text())
keys = sorted(set(doc) | set(new))
diff = [k for k in keys if k != "tool" and doc.get(k) != new.get(k)]
out = {"producer_tags_dropped": tags, "fields_compared": [k for k in keys if k != "tool"], "differ": diff,
       "equal_regen": new.get("equal"), "arrays": {a: {"doc": doc["arrays"][a], "regen": new["arrays"].get(a)} for a in doc.get("arrays", {})},
       "arrays_match": all(doc["arrays"][a] == new["arrays"].get(a) for a in doc.get("arrays", {})),
       "tool_doc": doc.get("tool"), "tool_regen": new.get("tool")}
if "canonical" in diff:
    out["canonical"] = {"doc": doc.get("canonical"), "regen": new.get("canonical")}
r = o / "result.json"
if r.exists():
    inst = (json.loads(r.read_text())["manifest"]["meta"].get("workload_fingerprint") or {}).get("instances")
    out["result_instances"] = inst
    out["candidate_equals_result_instances"] = inst == doc.get("candidate")
print(json.dumps(out, indent=1))
EOF
$PY -c "import json,sys; m=json.load(open(sys.argv[1]))['manifest']['meta']; [m.pop(k,None) for k in ('lane','provenance','for_result','note','produced_by_run')]; json.dump(m,open(sys.argv[2],'w'),indent=2)" $O/art.json $O/doc.json
$PY -m verity_numerical.bench.instance_equiv --vus $N --check $O/doc.json 2>&1 | tail -2 | tee $O/check.txt
