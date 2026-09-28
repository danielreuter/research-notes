#!/bin/bash
# side_store.sh N: store row N's finished Build now, from a separate short run on its pod with that run's own custody key (VM side).
# For a row that may hit its --timeout in Match or Commit: epoch_row.sh stores the Build only after the Commit, so a timeout would lose it.
# Refuses unless the row's progress shows its Build passed.  Prints the run id; its evidence/store.log names the art id.
set -u
N=${1:?row}; H=$(cd "$(dirname "$0")" && pwd); LANE=$RESEARCH_NOTES/lanes/vllm-epoch-run
R="env PYTHONPATH=/workspace/tools/research/src python3 -m research"
IFS='|' read -r POD RUN < <(awk -F'\t' -v n="$N" '$1==n && $8=="live" {print $2"|"$4}' "$LANE/evidence/spend.tsv" | tail -n 1)
[ -n "${RUN:-}" ] || { echo "#$N: no live row"; exit 2; }
KEY=$(python3 -c "import json;print(json.load(open('$H/rows.json'))['rows']['$N']['key'])")
$R pods ssh "$POD" -- "grep -q ' build rc=0' /workspace/research/runs/$RUN/evidence/progress.txt" < /dev/null || { echo "#$N: Build not passed yet"; exit 3; }
SHA=$($R pods ssh "$POD" -- "sed -n 's/^EPOCH_SHA=//p' /workspace/research/runs/$RUN/evidence/row_env.txt" < /dev/null 2>/dev/null | tail -n 1)
WT=/workspace-wt/epoch-${SHA:0:8}
$R run --on "$POD" --project verity --campaign vllm-rebaseline-epoch --custody-r2 --custody-ttl 2h --timeout 3000 --source "$WT" \
  --cwd source/integrations/vllm --send "$H/store_build.sh" --env ROWNUM="$N" --env EPOCH_SHA="$SHA" --env POD="$POD" --env STORE_KINDS=build \
  -- bash -c "mkdir -p \"\$RESEARCH_RUN_DIR/evidence\"; export PYTHONPATH=\$PWD/../../tools/research/src RESEARCH_STORE=/workspace/epoch/store GPU_NAME=side-store; bash \"\$RESEARCH_RUN_DIR/inputs/store_build.sh\" /workspace/epoch/sweep/$KEY > \"\$RESEARCH_RUN_DIR/evidence/store.log\" 2>&1; cat \"\$RESEARCH_RUN_DIR/evidence/store.log\"" \
  2>&1 | tee "$LANE/evidence/side-store-$N.txt" | grep -o 'r20[0-9]\{6\}-[0-9]\{6\}-[0-9a-f]\{4\}' | head -n 1
