#!/bin/bash
# side_finish.sh N [KINDS]: after row N's main run has ended, a side run on its pod with a fresh custody key (VM side):
#   the regression record (`rebaseline run`, candidate = the pod's sweep, -k r<N>: the test ids are <tier>-<check>-r<number>) into its
#   evidence/record/, and `store_build.sh` for KINDS (default: none; `large` = the match/commit files over 200 MB, `build records` = both
#   trees when the main run's key expired before its store).  Prints the side run id; finish_row.sh N reads its record with SIDE_RUN=<id>.
set -u
N=${1:?row}; KINDS=${2:-}; H=$(cd "$(dirname "$0")" && pwd); LANE=$RESEARCH_NOTES/lanes/vllm-epoch-run
R="env PYTHONPATH=/workspace/tools/research/src python3 -m research"
IFS='|' read -r POD RUN < <(awk -F'\t' -v n="$N" '$1==n && $8=="live" {print $2"|"$4}' "$LANE/evidence/spend.tsv" | tail -n 1)
[ -n "${RUN:-}" ] || { echo "#$N: no live row"; exit 2; }
KEY=$(python3 -c "import json;print(json.load(open('$H/rows.json'))['rows']['$N']['key'])")
SHA=$($R pods ssh "$POD" -- "sed -n 's/^EPOCH_SHA=//p' /workspace/research/runs/$RUN/evidence/row_env.txt" < /dev/null 2>/dev/null | tail -n 1)
WT=/workspace-wt/epoch-${SHA:0:8}
$R run --on "$POD" --project verity --campaign vllm-rebaseline-epoch --custody-r2 --custody-ttl 3h --timeout 7200 --source "$WT" \
  --cwd source/integrations/vllm --send "$H/store_build.sh" --env ROWNUM="$N" --env EPOCH_SHA="$SHA" --env POD="$POD" --env STORE_KINDS="$KINDS" \
  -- bash -c "set -u; EV=\$RESEARCH_RUN_DIR/evidence; mkdir -p \$EV; T=\$(cd ../.. && pwd -P); PY=/workspace/venv312/bin/python
export PYTHONPATH=\$T/integrations/vllm:\$T/packages/verity/src:\$T/tools/research/src:\$T/protocols/sampled_proofs RESEARCH_STORE=/workspace/epoch/store GPU_NAME=side
[ -n \"\$STORE_KINDS\" ] && bash \$RESEARCH_RUN_DIR/inputs/store_build.sh /workspace/epoch/sweep/$KEY > \$EV/store.log 2>&1
VERITY_REGRESSION_CANDIDATE=/workspace/epoch/sweep timeout 5400 \$PY -m tests.regression.rebaseline run --record \$EV/record --tier T0,T1,T2 -- -k r$N -ra > \$EV/rebaseline_run.log 2>&1
echo \"rebaseline run rc=\$? \$(grep -E 'passed|failed|error' \$EV/rebaseline_run.log | tail -n 1)\"; cat \$EV/store.log 2>/dev/null | grep '^STORED'" \
  2>&1 | tee "$LANE/evidence/side-finish-$N.txt" | grep -o 'r20[0-9]\{6\}-[0-9]\{6\}-[0-9a-f]\{4\}' | head -n 1
