#!/usr/bin/env bash
# red-team-lk: audit of the control run (06_control.sh): per tag forgery, the changed (query, unit) tuples that are not LK rows
# under the tagged and the tag-stripped statement.  CPU only.  Outputs /workspace/red-team-lk/out/<rev>/audit.json.
set -uo pipefail
source /workspace/env.sh
for REV in 3be6a35f 716ea008; do
  T=/workspace/tree-$REV; O=/workspace/red-team-lk/out/$REV
  cp /workspace/red-team-lk/scripts/red_team_lk.py $T/backends/gkr/tools/red_team_lk.py
  export PYTHONPATH="$T/backends/gkr:$T/packages/verity/src:$T/backends/numerical/python:$T"
  cd $T/backends/gkr
  echo "== audit $REV $(date -u +%H:%M:%S)"
  $PY tools/red_team_lk.py audit --out $O/forge-control > $O/audit.json 2> $O/audit.err; echo "rc=$?"
  tail -3 $O/audit.err
  $PY - $O/audit.json <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
for n, c in d["cases"].items():
    f = lambda m: [(x["q"], x["table"], x["unit"], x["tuple"]) for x in m][:6]
    print(n, "changed", c["changed_unit_col"], "| tagged miss", len(c["tagged"]), f(c["tagged"]), "| tagless miss", len(c["tagless"]), f(c["tagless"]))
EOF
done
