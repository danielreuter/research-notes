#!/usr/bin/env bash
# fill-consumer: shared runner on a prover pod. One heavy job at a time; timings only with an empty GPU.
#   /workspace/src       lane/fill-consumer @ .research-source.json's commit (research pods sync)
#   /workspace/fill-consumer/runs/<tag>/{result.json,log,run_id,proofs/}   one run each; rep 1 dumped (outside the clocks)
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
FC=/workspace/fill-consumer; O=$FC/runs; LOG=$FC/runs.txt; mkdir -p $O
VERIFIER=${VERIFIER:-}

gpu_idle() {  # wait up to ${1:-300} s for an empty GPU
  for i in $(seq $(( ${1:-300} / 2 ))); do
    [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ] && return 0; sleep 2
  done
  echo "GPU NOT IDLE: $(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader | tr '\n' ' ')" | tee -a $LOG; return 1
}

# run TAG MODE(local|live) REL BATCH DEPTH REPS [extra args...]
#   run_id: the research form (r<UTC>-<hex4>), passed as --run-id so result.json carries it as the runner wrote it
run() {
  local tag=$1 mode=$2 rel=$3 batch=$4 depth=$5 reps=$6; shift 6
  local d=$O/$tag; rm -rf $d; mkdir -p $d
  local vargs=(--dump-dir $d/proofs --dump-reps 1)
  if [ "$mode" = live ]; then [ -n "$VERIFIER" ] || { echo "$tag: live without VERIFIER" | tee -a $LOG; return 1; }; vargs+=(--verifier $VERIFIER); fi
  gpu_idle || return 1
  local t0=$(date +%s) rid=r$(date -u +%Y%m%d-%H%M%S)-$(openssl rand -hex 2)
  echo $rid > $d/run_id
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $batch --pipeline $depth \
      --total-vus 4096 --target -128 --reps $reps --device cuda --run-id $rid --out $d/result.json "${vargs[@]}" "$@" > $d/log 2>&1
  local rc=$? t1=$(date +%s)
  echo "$(date -u +%H:%M:%SZ) $tag $mode rel=$rel l=$batch p=$depth reps=$reps rc=$rc wall=$((t1-t0))s $($PY $FC/scripts/line.py $d/result.json 2>&1 | tail -1) $*" | tee -a $LOG
}
