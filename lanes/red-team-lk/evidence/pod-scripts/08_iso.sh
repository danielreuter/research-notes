#!/usr/bin/env bash
# red-team-lk: fp8 (3be6a35f) forge --control again, now with the isolated range-tag case tag.<a>_as_<b>.iso (forged column read by
# no other query), then the audit.  Outputs /workspace/red-team-lk/out/3be6a35f/forge-iso{,.log}, audit-iso.json.
set -uo pipefail
source /workspace/env.sh
REV=3be6a35f; V=/workspace/red-team-lk/bin/verify-main
T=/workspace/tree-$REV; O=/workspace/red-team-lk/out/$REV/forge-iso
cp /workspace/red-team-lk/scripts/red_team_lk.py $T/backends/gkr/tools/red_team_lk.py
export PYTHONPATH="$T/backends/gkr:$T/packages/verity/src:$T/backends/numerical/python:$T"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd $T/backends/gkr
echo "self-checks disabled: $(grep -c 'red-team-lk: cheating prover' gpu/logup.py gpu/logup_packed.py | tr '\n' ' ')"
echo "== iso $(date -u +%H:%M:%S)"
$PY tools/red_team_lk.py forge --relation fp8-ada --vus 64 --out $O --verifier $V --threads 12 --control > $O.log 2>&1; echo "forge rc=$?"
grep '^{"case"' $O.log | cut -c1-420
grep -E "Error|Traceback" $O.log | tail -5
echo "== audit $(date -u +%H:%M:%S)"
$PY tools/red_team_lk.py audit --out $O > /workspace/red-team-lk/out/$REV/audit-iso.json 2> /workspace/red-team-lk/out/$REV/audit-iso.err; echo "audit rc=$?"
$PY - /workspace/red-team-lk/out/$REV/audit-iso.json <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
for n, c in d["cases"].items():
    f = lambda m: [(x["q"], x["table"], x["unit"], x["tuple"]) for x in m][:6]
    print(n, "changed", c["changed_unit_col"], "| tagged miss", len(c["tagged"]), f(c["tagged"]), "| tagless miss", len(c["tagless"]), f(c["tagless"]))
EOF
