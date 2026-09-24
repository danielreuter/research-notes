#!/usr/bin/env bash
# fused-phases (replaces 40-all.sh after its first pair, for time): wait for the running seed-post-v3x4-p8, compare it, then the
# registrable runs of every cell, then seeded pairs for v3-p8 and v1-p4 (with v3x4-p8: v1 / v3 / v3x4, p4 and p8 covered).
source /workspace/fused-phases/scripts/lib.sh
while pgrep -f "seeded_run.py --relation fp8-ada-v3x4" > /dev/null; do sleep 5; done
$PY $FP/scripts/compare.py $O/seed-pre-v3x4-p8 $O/seed-post-v3x4-p8 2>&1 | tail -1 | tee -a $LOG
S=$FP/scripts
CELLS="v3x4-p8 v3x4-p4 v3-p8 v3-p4 v1-p4" KINDS=real bash $S/30-cells.sh
CELLS="v3-p8 v1-p4" KINDS=seed bash $S/30-cells.sh
echo REST_DONE | tee -a $LOG
