#!/bin/bash
# commitonly.sh RUNID ROW[:ENV=V,...] ...: re-run ONLY the Commit of rows whose Build+Match live in /workspace/research/runs/RUNID/sweep,
# from this run's (fixed) tree. Waits until the pod's recording chain (rows.sh / after.sh) has ended. Line per row in $RESEARCH_RUN_DIR/commits.txt.
set -u
RUNID=$1; shift
export SWEEP_DIR=/workspace/research/runs/$RUNID/sweep PAIRS=${PAIRS:-1} NCCL_P2P_DISABLE=1
S=$RESEARCH_RUN_DIR/commits.txt
for i in $(seq 1 2880); do
  pgrep -f "^bash .*inputs/(rows|after)\.sh|^bash verity_vllm/ops/(row_pod|tp_stage)\.sh" > /dev/null || break
  [ "$i" = 1 ] && echo "$(date -u +%FT%TZ) waiting for the recording chain" >> "$S"
  sleep 15
done
for spec in "$@"; do
  ROW=${spec%%:*}; EXTRA=""; [ "$spec" != "$ROW" ] && EXTRA=${spec#*:}
  [ -f "$SWEEP_DIR/$ROW/build_summary.json" ] || { echo "$(date -u +%FT%TZ) $ROW no Build in $SWEEP_DIR: skipped" >> "$S"; continue; }
  read -r ROLE REPO REV WORLD < <(/workspace/venv312/bin/python - "$ROW" <<'EOF'
import json, sys
row = sys.argv[1]
wl = json.load(open(f"workloads/{row}.json"))
role = wl["case"]
alias = {"B0": "HuggingFaceTB/SmolLM2-135M", "B1": "Qwen/Qwen2.5-1.5B"}
cps = json.load(open("manifests/checkpoints.json"))["checkpoints"]
cp = next(c for c in cps if c.get("role") == role or (role in alias and c["repo"] == alias[role] and c.get("local_path")))
tp = int((wl.get("sweep") or {}).get("tp") or wl.get("tp") or (2 if "__tp2__" in row else 1))
print(role, cp["repo"], cp["revision"], tp)
EOF
)
  (
    [ -n "$EXTRA" ] && { IFS=, read -r -a kv <<< "$EXTRA"; for x in "${kv[@]}"; do export "$x"; done; }
    export WORLD
    RUNNER=verity_vllm/ops/row_pod.sh; [ "$WORLD" -gt 1 ] && RUNNER=verity_vllm/ops/tp_stage.sh
    rm -rf "$SWEEP_DIR/$ROW/commit" "$SWEEP_DIR/$ROW/verdict.json"
    echo "$(date -u +%FT%TZ) $ROW commit start runner=$RUNNER extra=$EXTRA" >> "$S"
    bash $RUNNER "$ROW" "$ROLE" "$REPO" "$REV" commit
    echo "$(date -u +%FT%TZ) $ROW commit rc=$? $(grep '^commit' $SWEEP_DIR/$ROW/stages.txt | tail -n 1 | cut -c1-200)" >> "$S"
  )
done
echo "$(date -u +%FT%TZ) done" >> "$S"
