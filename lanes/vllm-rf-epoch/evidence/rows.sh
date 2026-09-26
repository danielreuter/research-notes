#!/bin/bash
# rows.sh ROW[:ENV=V,ENV=V] ... : re-record regression rows at the shipped tree (cwd = source/integrations/vllm).
# Per row: Build + Match, then Commit even when the Match FAILs (the FAIL-class rows' records carry a Commit), PAIRS=1.
# Evidence: $RESEARCH_RUN_DIR/sweep/<row>/ (row_pod.sh / tp_stage.sh layout); a line per stage in $RESEARCH_RUN_DIR/rows.txt.
set -u
export SWEEP_DIR=$RESEARCH_RUN_DIR/sweep PAIRS=${PAIRS:-1} NCCL_P2P_DISABLE=1
mkdir -p "$SWEEP_DIR"
S=$RESEARCH_RUN_DIR/rows.txt
for i in $(seq 1 240); do
  pgrep -f "pod_bootstrap.sh" > /dev/null || break
  [ "$i" = 1 ] && echo "$(date -u +%FT%TZ) waiting for the running bootstrap" >> "$S"
  sleep 30
done
if [ -n "${BOOT_CASES:-}" ]; then
  bash verity_vllm/ops/pod_bootstrap.sh --cases "$BOOT_CASES" --out "$RESEARCH_RUN_DIR/bootstrap" --gpu
  echo "$(date -u +%FT%TZ) bootstrap $BOOT_CASES rc=$?" >> "$S"
fi
for spec in "$@"; do
  ROW=${spec%%:*}; EXTRA=""; [ "$spec" != "$ROW" ] && EXTRA=${spec#*:}
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
    echo "$(date -u +%FT%TZ) $ROW start role=$ROLE world=$WORLD extra=$EXTRA" >> "$S"
    RUNNER=verity_vllm/ops/row_pod.sh; [ "$WORLD" -gt 1 ] && RUNNER=verity_vllm/ops/tp_stage.sh   # row_pod.sh has no TP hook
    bash $RUNNER "$ROW" "$ROLE" "$REPO" "$REV" build,match
    rc=$?; echo "$(date -u +%FT%TZ) $ROW build,match rc=$rc runner=$RUNNER" >> "$S"
    if [ "$rc" = 0 ] || [ "$rc" = 11 ]; then
      bash $RUNNER "$ROW" "$ROLE" "$REPO" "$REV" commit
      echo "$(date -u +%FT%TZ) $ROW commit rc=$?" >> "$S"
    fi
  )
done
echo "$(date -u +%FT%TZ) done" >> "$S"
