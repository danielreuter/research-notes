#!/bin/bash
# 2x L40S: bootstrap (OLMOE); row #70 through tp_stage.sh one stage per call (build, match, commit; Match's fold step fails at the
# base, class FAIL, so the Commit runs from its own call as in the record's chain), PAIRS=${PAIRS:-1}.
#   logs: /workspace/b4/logs/{bootstrap,r70_build,r70_match,r70_commit}.log
ROW=olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager
L=/workspace/b4/logs; mkdir -p $L
cd /workspace/head/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --gpu --cases OLMOE --out /workspace/bootstrap > $L/bootstrap.log 2>&1
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK: $(tail -2 $L/bootstrap.log)"; exit 3; }
echo "bootstrap OK $(date -u +%FT%TZ)"
for st in build match commit; do
  (
    cd /workspace/head/integrations/vllm || exit 3
    unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
    export SWEEP_DIR=/workspace/cp/sweep-head PAIRS=${PAIRS:-1}
    echo "start $(date -u +%FT%TZ) stage $st"
    env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL|VLLM|NCCL)'
    bash verity_vllm/ops/tp_stage.sh $ROW OLMOE allenai/OLMoE-1B-7B-0924 6d84c48581ece794365f2b8e9cfb043c68ade9c5 $st
    echo "exit $? $(date -u +%FT%TZ)"
    cat "$SWEEP_DIR/$ROW/stages.txt"
  ) > $L/r70_$st.log 2>&1
  echo "r70 $st: $(grep '^exit' $L/r70_$st.log)"
done
echo "done $(date -u +%FT%TZ)"
