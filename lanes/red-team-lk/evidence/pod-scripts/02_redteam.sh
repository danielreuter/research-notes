#!/usr/bin/env bash
# red-team-lk: static equivalence + forgeries for one producer tree (our copy /workspace/tree-<rev>, see 00_ship.sh).
# usage: 02_redteam.sh <rev> <relation> [static-nvf4 flags]
#   the tree's LogUp self-checks ("fractional sum is not zero") are sed'ed to a no-op in OUR copy (cheating prover);
#   the harness also swaps logup.multiplicities for a first-column match (adversarial multiplicities).
set -uo pipefail
source /workspace/env.sh
REV=$1; REL=$2; shift 2
T=/workspace/tree-$REV; O=/workspace/red-team-lk/out/$REV; mkdir -p $O
cp /workspace/red-team-lk/scripts/red_team_lk.py $T/backends/gkr/tools/red_team_lk.py
sed -i 's/raise ValueError("LogUp: fractional sum is not zero (a query is not in its table)")/pass  # red-team-lk: cheating prover/' \
    $T/backends/gkr/gpu/logup.py $T/backends/gkr/gpu/logup_packed.py
echo "self-checks disabled: $(grep -c 'red-team-lk: cheating prover' $T/backends/gkr/gpu/logup.py $T/backends/gkr/gpu/logup_packed.py | tr '\n' ' ')"
export PYTHONPATH="$T/backends/gkr:$T/packages/verity/src:$T/backends/numerical/python:$T"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd $T/backends/gkr
if [ "$REL" = fp4-nvf4 ]; then V=/workspace/red-team-lk/bin/verify-nvf4; else V=/workspace/red-team-lk/bin/verify-main; fi
if [ "$REL" = fp4-nvf4 ]; then
  echo "== static-nvf4 $* $(date -u +%H:%M:%S)"
  $PY tools/red_team_lk.py static-nvf4 "$@" > $O/static.json 2> $O/static.err; echo "static rc=$?"
  tail -3 $O/static.err
fi
echo "== forge $REL $(date -u +%H:%M:%S)"
$PY tools/red_team_lk.py forge --relation $REL --vus 64 --out $O/forge --verifier $V --threads 12 > $O/forge.log 2>&1; echo "forge rc=$?"
grep -vE "Warn|warn|searchsorted" $O/forge.log | grep '^{"case"' | cut -c1-400
grep -vE "Warn|warn|searchsorted" $O/forge.log | grep -E "Error|Traceback|line [0-9]+" | tail -8
if [ "$REL" = fp8-ada ]; then
  echo "== static-merge $(date -u +%H:%M:%S)"
  $PY tools/red_team_lk.py static-merge --plain $O/forge/plain --merged $O/forge/stmt > $O/static.json 2> $O/static.err; echo "static rc=$?"
  tail -3 $O/static.err
fi
sha256sum $O/forge/stmt/*.txt $V
echo "== done $(date -u +%H:%M:%S)"
