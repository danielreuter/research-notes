#!/usr/bin/env bash
# wave-a100 bench helpers (sourced). One heavy job at a time; timings only with no other compute app on the GPU.
#   b TAG RELATION BATCH DEPTH COINS [extra bench-vu args...]     COINS = local | live
# -> /workspace/wave-a100/runs/TAG/{result.json,log,proofs/ (rep-1 dump),meta.txt}
# Rust batch re-verify of the dump is a separate step (rust TAG), run after the timing rounds so it never overlaps a timing.
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
O=/workspace/wave-a100/runs; mkdir -p $O
VERIFIER_URL=${VERIFIER_URL:-}
SUM=/workspace/wave-a100/summary.txt

b() {
  local tag=$1 rel=$2 batch=$3 depth=$4 coins=$5; shift 5
  local d=$O/$tag
  if [ -f $d/result.json ]; then echo "$(date -u +%H:%M:%S) skip $tag (done)" | tee -a $SUM; return 0; fi
  rm -rf $d; mkdir -p $d
  local busy; busy=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)
  local live=(); [ "$coins" = live ] && live=(--verifier "$VERIFIER_URL")
  { echo "tag=$tag rel=$rel l=$batch p=$depth coins=$coins extra=$* gpu_apps_before=$busy load=$(cut -d' ' -f1-3 /proc/loadavg) start=$(date -u +%FT%TZ)"; } > $d/meta.txt
  local t0=$(date +%s)
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $batch --pipeline $depth \
      --total-vus 4096 --target -128 --reps ${REPS:-3} --device cuda --dump-dir $d/proofs --dump-reps 1 \
      --out $d/result.json "${live[@]}" "$@" > $d/log 2>&1
  local rc=$?
  echo "end=$(date -u +%FT%TZ) rc=$rc wall=$(( $(date +%s) - t0 ))s" >> $d/meta.txt
  local tt; tt=$($PY -c 'import json,sys;m={x["name"]:x["value"] for x in json.load(open(sys.argv[1]))["measurements"]};print("t.total %.4f"%m["t.total"], ("t.total_live %.4f"%m["t.total_live"]) if "t.total_live" in m else "")' $d/result.json 2>/dev/null)
  echo "$(date -u +%H:%M:%S) $tag rc=$rc gpu_apps_before=$busy wall=$(( $(date +%s) - t0 ))s $tt | $(grep -iE 'OutOfMemory|Traceback|Error|RTT' $d/log | tail -2 | tr '\n' ' ' | cut -c1-200)" | tee -a $SUM
  return $rc
}

rust() {  # TAG: pinned Rust batch over the rep-1 dump (system_h.bin -> +shared pair)
  local tag=$1 d=$O/$1
  local rep; rep=$(ls -d $d/proofs/rep1 2>/dev/null || ls -d $d/proofs/*/ 2>/dev/null | head -1)
  local hs=(); [ -f $d/proofs/system_h.bin ] && hs=(--system-h $d/proofs/system_h.bin)
  $LIGERO_VERIFY batch --system $d/proofs/system.bin "${hs[@]}" --dir ${rep:-$d/proofs} --jobs ${RUST_JOBS:-16} --threads 1 \
      --target-bits 128 --json $d/rust_batch.json > $d/rust_batch.out 2> $d/rust_batch.err
  local rc=$?
  echo "$(date -u +%H:%M:%S) $tag rust rc=$rc $($PY -c 'import json,sys;x=json.load(open(sys.argv[1]));print("accepted",x["accepted"],"/",x["n"],"batch",x["batch_accepted"],"bits %.2f"%x["batch_bits"],"pinned",x["system_pinned"],x["system"]["pinned_relation"])' $d/rust_batch.json 2>&1 | tail -1)" | tee -a $SUM
}
