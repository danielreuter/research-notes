#!/usr/bin/env bash
# wave-5090-2: shared runner (adapted from wave-4090's lib.sh). One heavy job at a time; timings only with an empty GPU.
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
VERIFIER=${VERIFIER:-tcp://213.173.111.88:49715}   # vy-wave-5090-verifier gpziw35nrqxlyb, EU-RO-1 (same DC as the prover)
O=/workspace/wave-5090-2/runs; mkdir -p $O
LOG=/workspace/wave-5090-2/runs.txt

gpu_idle() {  # wait up to 120 s for an empty GPU
  for i in $(seq 60); do
    [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ] && return 0; sleep 2
  done
  echo "GPU NOT IDLE: $(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader | tr '\n' ' ')" | tee -a $LOG; return 1
}

# run TAG MODE(local|live) REL BATCH DEPTH REPS [extra args...]; rep 1 is dumped in both modes (outside the clocks)
run() {
  local tag=$1 mode=$2 rel=$3 batch=$4 depth=$5 reps=$6; shift 6
  local d=$O/$tag; rm -rf $d; mkdir -p $d
  local vargs=(--dump-dir $d/proofs --dump-reps 1)
  [ "$mode" = live ] && vargs+=(--verifier $VERIFIER)
  gpu_idle || return 1
  local t0=$(date +%s)
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $batch --pipeline $depth \
      --total-vus 4096 --target -128 --reps $reps --device cuda --run-id w5090-2-$tag --out $d/result.json "${vargs[@]}" "$@" > $d/log 2>&1
  local rc=$? t1=$(date +%s)
  local line=$($PY - $d/result.json <<'PYX' 2>/dev/null
import json, sys
r = json.load(open(sys.argv[1]))
m = {x["name"]: x.get("value") for x in r.get("measurements", []) if isinstance(x, dict) and "name" in x}
print("status=%s t.total=%s t.total_live=%s rtt_ms=%s bytes=%s" % (r["validation"]["status"], m.get("t.total"), m.get("t.total_live"),
      m.get("net.rtt_ms"), m.get("proof_bytes")))
PYX
)
  echo "$(date -u +%H:%M:%SZ) $tag $mode rel=$rel l=$batch p=$depth reps=$reps rc=$rc wall=$((t1-t0))s $line $*" | tee -a $LOG
}
