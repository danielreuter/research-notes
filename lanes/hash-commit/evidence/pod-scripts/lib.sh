#!/usr/bin/env bash
# hash-commit: shared runner on the prover pod. One heavy job at a time; timings only with an empty GPU.
#   trees: /workspace/src (research pods sync of lane/hash-commit), /workspace/src-<sha> (other commits, git archive)
#   /workspace/hash-commit/runs/<tag>/{result.json,log,run_id,commit-evidence.json,proofs/}   one run each; rep 1 dumped
source /workspace/env.sh
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
HC=/workspace/hash-commit; O=$HC/runs; LOG=$HC/runs.txt; mkdir -p $O
V=/workspace/bin/ligero-verify

gpu_idle() {  # wait up to ${1:-300} s for an empty GPU
  for i in $(seq $(( ${1:-300} / 2 ))); do
    [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ] && return 0; sleep 2
  done
  echo "GPU NOT IDLE: $(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader | tr '\n' ' ')" | tee -a $LOG; return 1
}

# tests TREE PYTEST-ARGS...: pytest in the tree (GPU tests included), the last line to runs.txt
tests() {
  local tree=$1; shift
  gpu_idle || return 1
  ( cd $tree && PATH=/workspace/bin:$PATH PYTHONPATH="$tree/packages/verity/src:$tree/backends/numerical/python:$tree/tools/research/src:$tree" \
    $PY -m pytest -q -x "$@" > $HC/tests.log 2>&1 )
  echo "$(date -u +%H:%M:%SZ) tests tree=$tree rc=$? $(tail -1 $HC/tests.log) $*" | tee -a $LOG
}

# run TAG TREE REL BATCH DEPTH REPS [extra bench-vu args...]: the bench (zk interactive, 4096 VUs, 2^-128, --auth included-hash,
# commitment built 1 + $CREPS times), then the pinned Rust batch verifier on the rep-1 dump, then one summary line
run() {
  local tag=$1 tree=$2 rel=$3 batch=$4 depth=$5 reps=$6; shift 6
  local d=$O/$tag; rm -rf $d; mkdir -p $d
  gpu_idle || return 1
  local t0=$(date +%s) rid=r$(date -u +%Y%m%d-%H%M%S)-$(openssl rand -hex 2)
  echo $rid > $d/run_id
  ( cd $tree && PYTHONPATH="$tree/packages/verity/src:$tree/backends/numerical/python:$tree/tools/research/src:$tree" \
    RESEARCH_GIT_COMMIT=$(python3 -c "import json;print(json.load(open('$tree/.research-source.json'))['commit'])" 2>/dev/null || cat $tree/.commit) \
    $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $batch --pipeline $depth \
      --total-vus 4096 --target -128 --reps $reps --device cuda --run-id $rid --out $d/result.json \
      --dump-dir $d/proofs --dump-reps 1 --auth included-hash --commit-reps ${CREPS:-3} --commit-evidence $d/commit-evidence.json \
      "$@" > $d/log 2>&1 )
  local rc=$? t1=$(date +%s) rrc=na
  if [ $rc -eq 0 ] && [ -d $d/proofs/rep1 ]; then
    ( cd $d/proofs && $V system-digest --system system.bin > rust_digest.json 2> rust_digest.err
      $V batch --system system.bin --dir rep1 --jobs 8 --threads 1 --target-bits 128 --json rust_batch.json > rust_batch.out 2>&1 )
    rrc=$?
  fi
  echo "$(date -u +%H:%M:%SZ) $tag tree=$tree rc=$rc rust=$rrc wall=$((t1-t0))s $($PY $HC/scripts/line.py $d 2>&1 | tail -1) $*" | tee -a $LOG
}
