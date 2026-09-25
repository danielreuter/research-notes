#!/usr/bin/env bash
# commit-gpu: benchmarks/commitments/commit_cost.py --impl gpu, the four variants, at the shapes of 4096 instances:
#   rows  4096 leaves x 1536 B (fp8 row) and x 3072 B (bf16 row)  -- frame-v3-sha256-row, frame-v3-blake3-row, vllm-v1
#   words 4096 x 1536 leaves x 2 B (the --auth included a-tree)  -- frame-v3 (word leaves), vllm-v1
# each a research-result dir under $HC/cc/<tag> (result.json + commit_cost.json); roots checked against the references.
source /workspace/hash-commit/scripts/lib.sh
cc() {
  local tag=$1; shift
  local d=$HC/cc/$tag; rm -rf $d; mkdir -p $d
  gpu_idle || return 1
  ( cd /workspace/src && PYTHONPATH="/workspace/src/packages/verity/src:/workspace/src/tools/research/src:/workspace/src" \
    RESEARCH_RUN_ID=r$(date -u +%Y%m%d-%H%M%S)-$(openssl rand -hex 2) \
    $PY benchmarks/commitments/commit_cost.py --impl gpu --reps ${CCREPS:-20} --out $d "$@" > $d/log 2>&1 )
  echo "$(date -u +%H:%M:%SZ) cc $tag rc=$? $(tr '\n' ' ' < $d/log | cut -c1-900)" | tee -a $LOG
}
cc rows1536 --scheme frame-v3-sha256-row --scheme frame-v3-blake3-row --scheme vllm-v1 --leaves 4096 --leaf-bytes 1536
cc rows3072 --scheme frame-v3-sha256-row --scheme frame-v3-blake3-row --scheme vllm-v1 --leaves 4096 --leaf-bytes 3072
cc words2 --scheme frame-v3 --scheme vllm-v1 --leaves 6291456 --leaf-bytes 2
