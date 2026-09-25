#!/bin/bash
# vyv-rf-c1-g2 (1x L40S): bootstrap from the head tree (--gpu --cases LLAMA32_1B), the CUDA scheme tests at head, then #101
# build,match,commit at head and at base (row101.sh), the head/base row-file comparison and the per-scheme throughput.
#   trees: /workspace/head (lane head), /workspace/basetree (its base), both shipped with `research pods sync`
#   logs: /workspace/c1/logs/, copied to $RESEARCH_RUN_DIR/c1-logs/ at the end
set -u
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
L=/workspace/c1/logs; mkdir -p $L
IN=$RESEARCH_RUN_DIR/inputs
cp $IN/row101.sh $IN/ab_compare.py $IN/throughput.py /workspace/c1/
finish() { mkdir -p $RESEARCH_RUN_DIR/c1-logs; cp -a $L/. $RESEARCH_RUN_DIR/c1-logs/; echo "G2-DONE $(date -u +%FT%TZ)"; }
trap finish EXIT
echo "bootstrap start $(date -u +%FT%TZ)"
( cd /workspace/head/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --gpu --cases LLAMA32_1B --out /workspace/c1/bootstrap ) > $L/bootstrap.log 2>&1
tail -3 $L/bootstrap.log
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "BOOT-FAIL"; exit 3; }
cp /workspace/c1/bootstrap/readiness.json $L/ 2>/dev/null
(
  cd /workspace/head
  export PATH=/workspace/venv312/bin:/usr/local/cuda/bin:$PATH HF_HOME=/workspace/hf CUDA_HOME=/usr/local/cuda PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
  export PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src
  nvidia-smi --query-gpu=name,driver_version,compute_cap --format=csv,noheader
  nvcc --version | tail -2
  python -m pytest integrations/vllm/tests/commit/test_scheme_cuda.py integrations/vllm/tests/commit/test_production_vectors.py \
    integrations/vllm/tests/commit/test_leafhash_device.py integrations/vllm/tests/pipeline/test_spans.py \
    -ra -p no:cacheprovider -o junit_family=xunit1 --junitxml=$L/cuda_tests.xml
  echo "cuda tests exit $?"
) > $L/cuda_tests.log 2>&1
tail -4 $L/cuda_tests.log
bash /workspace/c1/row101.sh > $L/row101.out 2>&1
cat $L/row101.out
for tag in head base; do
  for f in commit/verdict.json commit/runs.jsonl stages.txt; do cp /workspace/cp/sweep-$tag/$ROW/$f $L/r101_${tag}_$(basename $f) 2>/dev/null; done
done
/workspace/venv312/bin/python /workspace/c1/ab_compare.py $ROW > $L/r101_ab_compare.txt 2>&1
tail -1 $L/r101_ab_compare.txt | cut -c1-300
/workspace/venv312/bin/python /workspace/c1/throughput.py $ROW > $L/throughput.json 2>&1
head -c 3000 $L/throughput.json
