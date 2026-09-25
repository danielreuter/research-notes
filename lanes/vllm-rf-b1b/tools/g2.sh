#!/bin/bash
# 1x L40S 188 GB: bootstrap (OLMOE) from the head tree; row #67 Build+Match once at head (PAIRS=1), the row dir copied for base before
# any Commit, then Commit at head and at base (PAIRS=1; one Build/Match shared by both arms, as lane f1 did); then the record comparison.
#   trees: /workspace/head (lane head), /workspace/base (10996616)   logs: /workspace/b1/logs/{bootstrap,r67_*,r67_cmp}.log
set -u
ROW=olmoe-1b-7b__bf16__l40s__tp1__b32__i1024__o128__mixed__greedy__bi-eager
L=/workspace/b1/logs; mkdir -p $L
finish() { mkdir -p $RESEARCH_RUN_DIR/b1-logs; cp -a $L/. $RESEARCH_RUN_DIR/b1-logs/ 2>/dev/null
  for tag in head base; do d=/workspace/cp/sweep-$tag; [ -d $d/$ROW ] && ( cd $d && find $ROW -type f \( -name '*.json' -o -name '*.jsonl' \
    -o -name '*.txt' -o -name '*.log' \) -size -64M | tar -czf $RESEARCH_RUN_DIR/b1-logs/r67_$tag.tgz -T - ) 2>/dev/null; done
  echo "G2-DONE $(date -u +%FT%TZ)"; }
trap finish EXIT
if ! grep -q '^BOOTSTRAP-OK' $L/bootstrap.log 2>/dev/null; then
  echo "bootstrap start $(date -u +%FT%TZ)"
  ( cd /workspace/head/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --gpu --cases OLMOE --out /workspace/bootstrap ) > $L/bootstrap.log 2>&1
  grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK: $(tail -2 $L/bootstrap.log)"; exit 3; }
fi
echo "bootstrap OK $(date -u +%FT%TZ)"
nvidia-smi --query-gpu=name,driver_version,compute_cap --format=csv,noheader
arm() {  # TAG TREE STAGES
  local TAG=$1 T=$2 S=$3
  (
    cd "$T/integrations/vllm" || exit 3
    unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
    export SWEEP_DIR=/workspace/cp/sweep-$TAG PAIRS=1
    echo "start $(date -u +%FT%TZ) tree $T $(cat $T/.research-source.json) stages $S"
    env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL|VLLM)'
    bash verity_vllm/ops/row_pod.sh $ROW OLMOE allenai/OLMoE-1B-7B-0924 6d84c48581ece794365f2b8e9cfb043c68ade9c5 $S
    rc=$?
    echo "exit $rc $(date -u +%FT%TZ)"
    cat "$SWEEP_DIR/$ROW/stages.txt"
    exit $rc
  ) > $L/r67_${TAG}_${S//,/_}.log 2>&1
  local rc=$?
  echo "r67 $TAG $S: $(grep '^exit' $L/r67_${TAG}_${S//,/_}.log)"
  return $rc
}
if [ ! -f /workspace/cp/sweep-base/$ROW/match_summary.json ]; then
  arm head /workspace/head build,match || exit 11
  mkdir -p /workspace/cp/sweep-base && cp -a /workspace/cp/sweep-head/$ROW /workspace/cp/sweep-base/ || exit 4
  echo "row dir copied for base $(date -u +%FT%TZ): $(cd /workspace/cp/sweep-head && find $ROW -type f | wc -l) head files," \
       "$(cd /workspace/cp/sweep-base && find $ROW -type f | wc -l) base files"
fi
for pair in ${ARMS:-head:/workspace/head base:/workspace/base}; do
  arm ${pair%%:*} ${pair#*:} commit
done
/workspace/venv312/bin/python /workspace/b1/tools/rowcmp.py $ROW fdd998d46fac4b37 4799063127e655ff - > $L/r67_cmp.log 2>&1
cat $L/r67_cmp.log
echo "done $(date -u +%FT%TZ)"
