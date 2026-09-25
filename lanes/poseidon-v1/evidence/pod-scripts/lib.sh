#!/usr/bin/env bash
# poseidon-v1: B-Ligero + in-proof hash (Poseidon2 per row, no sharing) under the TABLES.md measurement protocol.
# Sourced on the prover pod. One heavy job at a time; timings only with an empty GPU.
#   /workspace/poseidon-v1/runs/<tag>/{result.json,log,run_id,commit-evidence.json,proofs/,rust_*}   one bench-vu each
#   bench-vu: zk interactive, --target -128 (union bound over sub-batches), --reps 5 timed after bench-vu's untimed warm-up
#   sub-batch + full untimed pipelined pass; the commitment built from scratch 1 + 5 times (--commit-reps 5, no --auth-cache):
#   commit.seconds = median of the 5 warm builds, e2e.seconds = commit.seconds + t.total (t.total = the median rep's).
source /workspace/env.sh
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# skips only the warm-up sub-batch's Python reference-hints comparison (untimed; fill-dc did the same for these cells)
export LIGERO_REFERENCE_HINTS=${LIGERO_REFERENCE_HINTS:-0}
PV=/workspace/poseidon-v1; O=$PV/runs; LOG=$PV/runs.txt; mkdir -p $O
V=/workspace/bin/ligero-verify
SCRIPTS=${SCRIPTS:-$PV/scripts}

gpu_idle() {  # wait up to ${1:-300} s for an empty GPU
  for i in $(seq $(( ${1:-300} / 2 ))); do
    [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ] && return 0; sleep 2
  done
  echo "GPU NOT IDLE: $(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader | tr '\n' ' ')" | tee -a $LOG; return 1
}

# run TAG TREE REL L P N [extra bench-vu args...]
run() {
  local tag=$1 tree=$2 rel=$3 l=$4 p=$5 n=$6; shift 6
  local d=$O/$tag; rm -rf $d; mkdir -p $d
  gpu_idle || return 1
  local t0=$(date +%s) rid=r$(date -u +%Y%m%d-%H%M%S)-$(openssl rand -hex 2)
  echo $rid > $d/run_id
  echo "tag=$tag tree=$tree rel=$rel l=$l p=$p n=$n reps=${REPS:-5} creps=${CREPS:-5} args=$* load=$(cut -d' ' -f1-3 /proc/loadavg) start=$(date -u +%FT%TZ) MALLOC_MMAP_MAX_=${MALLOC_MMAP_MAX_:-unset} MALLOC_TRIM_THRESHOLD_=${MALLOC_TRIM_THRESHOLD_:-unset}" > $d/meta.txt
  ( cd $tree && PYTHONPATH="$tree/packages/verity/src:$tree/backends/numerical/python:$tree/tools/research/src:$tree" \
    RESEARCH_GIT_COMMIT=$(python3 -c "import json;print(json.load(open('$tree/.research-source.json'))['commit'])" 2>/dev/null || cat $tree/.commit) \
    $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $l --pipeline $p \
      --total-vus $n --target -128 --reps ${REPS:-5} --device cuda --run-id $rid --out $d/result.json \
      --dump-dir $d/proofs --dump-reps 1 --auth included-hash --commit-reps ${CREPS:-5} --commit-evidence $d/commit-evidence.json \
      "$@" > $d/log 2>&1 )
  local rc=$? t1=$(date +%s) rrc=na
  echo "end=$(date -u +%FT%TZ) rc=$rc wall=$((t1 - t0))s load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $d/meta.txt
  if [ $rc -eq 0 ] && [ -d $d/proofs/rep1 ]; then
    ( cd $d/proofs && $V system-digest --system system.bin > rust_digest.json 2> rust_digest.err
      $V batch --system system.bin --dir rep1 --jobs 8 --threads 1 --target-bits 128 --json rust_batch.json > rust_batch.out 2>&1 )
    rrc=$?
  fi
  echo "$(date -u +%H:%M:%SZ) $tag rel=$rel l=$l p=$p n=$n rc=$rc rust=$rrc wall=$((t1 - t0))s $($PY $SCRIPTS/line.py $d 2>&1 | tail -1) $(grep -E 'Traceback|Error|out of memory' $d/log | tail -1 | cut -c1-160)" | tee -a $LOG
  return $rc
}
