#!/usr/bin/env bash
# fused-phases: shared runner. One heavy job at a time; timings only with an empty GPU (nvidia-smi compute apps).
#   /workspace/src      the lane tip (research pods sync; commit in .research-source.json)
#   /workspace/src-pre  the same tree with the files the lane changed restored from 3adf4c28 (the pre-fix prover/runner)
source /workspace/env.sh
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
FP=/workspace/fused-phases; O=$FP/runs; LOG=$FP/runs.txt; mkdir -p $O
TIP=$(python3 -c 'import json; print(json.load(open("/workspace/src/.research-source.json"))["commit"])')

gpu_idle() {  # wait up to ${1:-120} s for an empty GPU
  for i in $(seq $(( ${1:-120} / 2 ))); do
    [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ] && return 0; sleep 2
  done
  echo "GPU NOT IDLE: $(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader | tr '\n' ' ')" | tee -a $LOG; return 1
}

# run TAG SRC SEED REL BATCH DEPTH REPS [extra args...]
#   SRC /workspace/src | /workspace/src-pre; SEED '' = genuine os.urandom (registrable), else seeded_run.py (comparison only)
run() {
  local tag=$1 src=$2 seed=$3 rel=$4 batch=$5 depth=$6 reps=$7; shift 7
  local d=$O/$tag; rm -rf $d; mkdir -p $d
  local entry=(-m backends.direct.ligero.run) commit=$TIP
  [ -n "$seed" ] && entry=($FP/scripts/seeded_run.py)
  [ "$src" = /workspace/src-pre ] && commit="3adf4c28e-prefix-files"
  # seeded runs only compare proof bytes (and the accounting): they need no idle GPU; registrable runs wait for one
  [ -n "$seed" ] || gpu_idle 1200 || return 1
  local t0=$(date +%s)
  (cd $src && PYTHONPATH="$src/packages/verity/src:$src/backends/numerical/python:$src/tools/research/src:$src" \
     RESEARCH_GIT_COMMIT=$commit URANDOM_SEED=$seed \
     $PY "${entry[@]}" --relation $rel bench-vu --zk --mode interactive --batch $batch --pipeline $depth --total-vus 4096 \
       --target -128 --reps $reps --out $d/result.json --dump-dir $d/proofs --dump-reps 1 "$@" > $d/log 2>&1)
  local rc=$? t1=$(date +%s)
  echo "$(date -u +%H:%M:%SZ) $tag src=${src#/workspace/} seed=${seed:-none} rel=$rel l=$batch p=$depth reps=$reps rc=$rc wall=$((t1-t0))s $($PY $FP/scripts/line.py $d/result.json 2>&1 | tail -1) $*" | tee -a $LOG
}
