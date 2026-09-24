#!/usr/bin/env bash
# wave-h100-2: bare candidates per relation, --zk interactive, local coins, 4096 VUs, --reps 3, nvidia-smi empty before each run.
# Round 1 = every candidate (v1 best depth l=16384, v3 fused l=16384, v3x4 fused l=4096 p4 and p8), rep1 dumped + pinned Rust batch.
# Rounds 2-3 = the two fastest of round 1 per relation, arm order reversed each round (budget: ~30 min of H100 left).
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
O=/workspace/wave-h100-2/bare; mkdir -p $O
waitgpu() { while [ -n "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]; do sleep 2; done; }
b() {  # tag, relation, batch, pipeline, dump(0/1)
  local tag=$1 rel=$2 l=$3 p=$4 dump=$5; local d=$O/$tag
  rm -rf $d; mkdir -p $d; waitgpu
  local da=""; [ "$dump" = 1 ] && da="--dump-dir $d/proofs --dump-reps 1"
  local t0=$(date +%s)
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $l --pipeline $p \
      --total-vus 4096 --target -128 --reps 3 $da --out $d/result.json > $d/log 2>&1
  local rc=$?
  local tt=$($PY -c 'import json,sys;x=json.load(open(sys.argv[1]));m=x.get("measurement",x);print(m.get("t.total", m.get("t_total","?")))' $d/result.json 2>/dev/null)
  echo "$(date -u +%H:%M:%S) $tag rel=$rel l=$l p=$p rc=$rc t.total=$tt wall=$(( $(date +%s)-t0 ))s" | tee -a $O/summary.txt
  if [ "$dump" = 1 ] && [ $rc = 0 ]; then
    local rep=$(ls -d $d/proofs/*/ 2>/dev/null | head -1)
    $LIGERO_VERIFY batch --system $d/proofs/system.bin --dir ${rep:-$d/proofs} --jobs 8 --threads 1 --target-bits 128 \
        --json $d/proofs/rust_batch.json > $d/rust_batch.out 2> $d/rust_batch.err &
  fi
}
R=${1:-1}
if [ "$R" = 1 ]; then
  b r1-fp8-v1-p4      fp8-hopper       16384 4 1
  b r1-fp8-v3-p4      fp8-hopper-v3    16384 4 1
  b r1-fp8-v3x4-p4    fp8-hopper-v3x4  4096  4 1
  b r1-fp8-v3x4-p8    fp8-hopper-v3x4  4096  8 1
  b r1-bf16-v1-p8     bf16-hopper      16384 8 1
  b r1-bf16-v3-p8     bf16-hopper-v3   16384 8 1
  b r1-bf16-v3x4-p4   bf16-hopper-v3x4 4096  4 1
  b r1-bf16-v3x4-p8   bf16-hopper-v3x4 4096  8 1
  wait
  echo R1_DONE | tee -a $O/summary.txt
fi
