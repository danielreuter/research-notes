#!/usr/bin/env bash
# wave-4090: shared runner. One heavy job at a time; timings only with an empty GPU (nvidia-smi compute apps).
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
VERIFIER=${VERIFIER:-tcp://213.173.110.201:12166}
O=/workspace/wave-4090/runs; mkdir -p $O
LOG=/workspace/wave-4090/runs.txt

gpu_idle() {  # wait up to 120 s for an empty GPU
  for i in $(seq 60); do
    [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ] && return 0; sleep 2
  done
  echo "GPU NOT IDLE: $(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader | tr '\n' ' ')" | tee -a $LOG; return 1
}

# run TAG MODE(local|live) REL BATCH DEPTH REPS [extra args...]
run() {
  local tag=$1 mode=$2 rel=$3 batch=$4 depth=$5 reps=$6; shift 6
  local d=$O/$tag; rm -rf $d; mkdir -p $d
  local vargs=(--dump-dir $d/proofs --dump-reps 1)
  [ "$mode" = live ] && vargs=(--verifier $VERIFIER)
  gpu_idle || return 1
  local t0=$(date +%s)
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $batch --pipeline $depth \
      --total-vus 4096 --target -128 --reps $reps --out $d/result.json "${vargs[@]}" "$@" > $d/log 2>&1
  local rc=$? t1=$(date +%s)
  local line=$($PY - $d/result.json <<'PYX' 2>/dev/null
import json, sys
r = json.load(open(sys.argv[1]))
found = {}
def walk(x):
    if isinstance(x, dict):
        n = x.get("name") or x.get("metric")
        if n in ("t.total", "t.total_live") and n not in found:
            found[n] = x.get("value", x.get("median"))
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
walk(r)
lv = (r.get("evidence") or {}).get("live_verifier") or {}
acc = [p.get("accepted") for p in lv.get("per_rep", [])]
print("t.total=%s t.total_live=%s live_acc=%s/%s" % (found.get("t.total"), found.get("t.total_live"), sum(map(bool, acc)), len(acc)))
PYX
)
  echo "$(date -u +%H:%M:%SZ) $tag $mode rel=$rel l=$batch p=$depth reps=$reps rc=$rc wall=$((t1-t0))s $line $*" | tee -a $LOG
}
