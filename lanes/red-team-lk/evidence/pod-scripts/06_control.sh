#!/usr/bin/env bash
# red-team-lk: tag-stripped CONTROL (unsound on purpose): the tag forgeries of forge.json against LK without its tag column.
# Expect LogUp to pass there (the collision is then a real LK row), so any rejection moves to the forged column's other
# constraints.  Outputs /workspace/red-team-lk/out/<rev>/forge-control.
set -uo pipefail
source /workspace/env.sh
for spec in "3be6a35f fp8-ada verify-main" "716ea008 fp4-nvf4 verify-nvf4"; do
  set -- $spec; REV=$1; REL=$2; V=/workspace/red-team-lk/bin/$3
  T=/workspace/tree-$REV; O=/workspace/red-team-lk/out/$REV/forge-control
  cp /workspace/red-team-lk/scripts/red_team_lk.py $T/backends/gkr/tools/red_team_lk.py
  export PYTHONPATH="$T/backends/gkr:$T/packages/verity/src:$T/backends/numerical/python:$T"
  cd $T/backends/gkr
  echo "== control $REV $(date -u +%H:%M:%S)"
  $PY tools/red_team_lk.py forge --relation $REL --vus 64 --out $O --verifier $V --threads 12 --control > $O.log 2>&1; echo "rc=$?"
  grep '^{"case"' $O.log | cut -c1-420
done
