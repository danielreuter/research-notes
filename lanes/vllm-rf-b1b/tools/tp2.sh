#!/bin/bash
# 2x L40S: bootstrap (OLMOE) from the head tree; row #70 at head through tp_stage.sh, one stage per call (build, match, commit;
# the Match's fold step fails as in the record, class FAIL, so the Commit runs from its own call), PAIRS=1; then the Commit's
# summary.json against f1's base Commit of record (b4's cmp70.py, field by field per pair).
#   logs: /workspace/b1/logs/{bootstrap,r70_build,r70_match,r70_commit,r70_cmp}.log
set -u
ROW=olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager
L=/workspace/b1/logs; mkdir -p $L
finish() { mkdir -p $RESEARCH_RUN_DIR/b1-logs; cp -a $L/. $RESEARCH_RUN_DIR/b1-logs/ 2>/dev/null
  d=/workspace/cp/sweep-head; [ -d $d/$ROW ] && ( cd $d && find $ROW -type f \( -name '*.json' -o -name '*.jsonl' -o -name '*.txt' \
    -o -name '*.log' \) -size -64M | tar -czf $RESEARCH_RUN_DIR/b1-logs/r70_head.tgz -T - ) 2>/dev/null
  echo "TP2-DONE $(date -u +%FT%TZ)"; }
trap finish EXIT
if ! grep -q '^BOOTSTRAP-OK' $L/bootstrap.log 2>/dev/null; then
  ( cd /workspace/head/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --gpu --cases OLMOE --out /workspace/bootstrap ) > $L/bootstrap.log 2>&1
  grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK: $(tail -2 $L/bootstrap.log)"; exit 3; }
fi
echo "bootstrap OK $(date -u +%FT%TZ)"
nvidia-smi --query-gpu=name,driver_version,compute_cap --format=csv,noheader
for st in build match commit; do
  (
    cd /workspace/head/integrations/vllm || exit 3
    unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
    export SWEEP_DIR=/workspace/cp/sweep-head PAIRS=1
    echo "start $(date -u +%FT%TZ) stage $st tree $(cat /workspace/head/.research-source.json)"
    env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL|VLLM|NCCL)'
    bash verity_vllm/ops/tp_stage.sh $ROW OLMOE allenai/OLMoE-1B-7B-0924 6d84c48581ece794365f2b8e9cfb043c68ade9c5 $st
    echo "exit $? $(date -u +%FT%TZ)"
    cat "$SWEEP_DIR/$ROW/stages.txt"
  ) > $L/r70_$st.log 2>&1
  echo "r70 $st: $(grep '^exit' $L/r70_$st.log)"
done
/workspace/venv312/bin/python /workspace/b1/tools/cmp70.py /workspace/cp/sweep-head/$ROW/commit/summary.json \
  /workspace/b1/tools/f1base70/sweep/$ROW/commit/summary.json > $L/r70_cmp.log 2>&1
cat $L/r70_cmp.log
echo "done $(date -u +%FT%TZ)"
