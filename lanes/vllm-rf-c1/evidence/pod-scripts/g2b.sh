#!/bin/bash
# vyv-rf-c1-g2, second run at the lane head after the test-only module move: the CUDA scheme tests at head, then #101
# build,match,commit at head only; the base row of the first run (same pod, /workspace/cp/sweep-base) is the comparison.
# The first head row is kept as /workspace/cp/sweep-head-<its sha12>.   logs: /workspace/c1/logs/ -> $RESEARCH_RUN_DIR/c1-logs/
set -u
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
L=/workspace/c1/logs; mkdir -p $L
IN=$RESEARCH_RUN_DIR/inputs
cp $IN/row101.sh $IN/ab_compare.py $IN/throughput.py $IN/snap_compare.py /workspace/c1/
finish() { mkdir -p $RESEARCH_RUN_DIR/c1-logs; cp -a $L/. $RESEARCH_RUN_DIR/c1-logs/; echo "G2B-DONE $(date -u +%FT%TZ)"; }
trap finish EXIT
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK"; exit 3; }
[ -d /workspace/cp/sweep-head ] && mv /workspace/cp/sweep-head /workspace/cp/sweep-head-472207c33273
echo "head $(python3 -c 'import json;print(json.load(open("/workspace/head/.research-source.json"))["commit"])')"
(
  cd /workspace/head
  export PATH=/workspace/venv312/bin:/usr/local/cuda/bin:$PATH HF_HOME=/workspace/hf CUDA_HOME=/usr/local/cuda PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
  export PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src
  python -m pytest integrations/vllm/tests/commit/test_scheme_cuda.py integrations/vllm/tests/commit/test_production_vectors.py \
    integrations/vllm/tests/commit/test_leafhash_device.py integrations/vllm/tests/pipeline/test_spans.py \
    integrations/vllm/tests/commit/test_semantic_layout.py integrations/vllm/tests/commit/test_stream_merkle.py \
    -ra -p no:cacheprovider -o junit_family=xunit1 --junitxml=$L/cuda_tests2.xml
  echo "cuda tests exit $?"
) > $L/cuda_tests2.log 2>&1
tail -3 $L/cuda_tests2.log
PAIRS_TO_RUN="head:/workspace/head" bash /workspace/c1/row101.sh > $L/row101_2.out 2>&1
cat $L/row101_2.out
for f in commit/verdict.json commit/runs.jsonl stages.txt; do cp /workspace/cp/sweep-head/$ROW/$f $L/r101_head2_$(basename $f) 2>/dev/null; done
cp $L/r101_head.log $L/r101_head2.log
/workspace/venv312/bin/python /workspace/c1/ab_compare.py $ROW > $L/r101_ab_compare2.txt 2>&1
tail -1 $L/r101_ab_compare2.txt | cut -c1-300
/workspace/venv312/bin/python /workspace/c1/snap_compare.py $ROW > $L/r101_snap_compare2.txt 2>&1
cat $L/r101_snap_compare2.txt | head -20
/workspace/venv312/bin/python /workspace/c1/throughput.py $ROW > $L/throughput2.json 2>&1
head -c 2500 $L/throughput2.json
