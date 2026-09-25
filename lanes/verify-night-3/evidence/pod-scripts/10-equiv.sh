#!/usr/bin/env bash
# verify-night-3: re-run instance_equiv --check on instance-equiv/v1 docs + the renderer's tables._equiv_content against the results
# usage: 10-equiv.sh EQUIV_ART VUS RESULT_ART...   (full ids); writes $W/equiv-<art8>/{doc.json,check.txt,content.json}
set -uo pipefail
source "$(dirname "$0")/lib.sh"
E=$1; N=$2; shift 2
O=$W/equiv-${E:4:8}; mkdir -p $O
t0=$(date +%s)
# the document is the artifact's meta; the producer's `lane` / `provenance` tags are not tool fields, so --check compares without them
R data show $E --json > $O/art.json || { echo "ERROR show $E"; exit 2; }
$PY -c "import json,sys; m=json.load(open(sys.argv[1]))['manifest']['meta']; print('producer tags dropped:', sorted(k for k in ('lane','provenance') if k in m), file=sys.stderr); [m.pop(k,None) for k in ('lane','provenance')]; json.dump(m, open(sys.argv[2],'w'), indent=2)" $O/art.json $O/doc.json
cd /workspace/src
$PY -m verity_numerical.bench.instance_equiv --vus $N --check $O/doc.json 2>&1 | tee $O/check.txt; rc=${PIPESTATUS[0]}
echo "check rc=$rc seconds=$(( $(date +%s) - t0 ))" | tee -a $O/check.txt
for r in "$@"; do R data show $r --json > $O/result-${r:4:8}.json; done
$PY - $O "$@" <<'EOF' | tee $O/content.json
import json, sys, types
from pathlib import Path
from verity_numerical.bench import tables
o = Path(sys.argv[1]); doc = json.loads((o / "doc.json").read_text())
out = {}
for r in sys.argv[2:]:
    m = json.loads((o / f"result-{r[4:12]}.json").read_text())["manifest"]["meta"]
    inst = (m.get("workload_fingerprint") or {}).get("instances")
    tgt = types.SimpleNamespace(name=doc.get("target"))
    out[r] = {"relation": m.get("relation"), "instances": inst, "equiv_content_problems": tables._equiv_content(doc, tgt, inst or {})}
print(json.dumps(out, indent=1))
EOF
exit $rc
