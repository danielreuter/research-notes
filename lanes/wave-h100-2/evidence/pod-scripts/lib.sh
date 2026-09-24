#!/usr/bin/env bash
# wave-h100-2 helpers. b = local-coins timing run (--reps 3), lv = live run against the same-DC verifier (--reps 3 = 3 sessions).
# Both: --zk --mode interactive, 4096 VUs, --target -128, nvidia-smi empty before start. Extra args pass through (--auth/--tile).
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
# skips only the warm-up sub-batch's Python reference-hints comparison (~100 s per v3/v3x4 process); self-check still runs
export LIGERO_REFERENCE_HINTS=0
REPS=${REPS:-5}
VER=${VER:-tcp://69.30.85.40:22160}   # vy-wave-h100-verifier (GPU.ONE Montreal), prover vy-wave-h100b (GPU.ONE Dorval)
O=/workspace/wave-h100-2; mkdir -p $O/bare $O/live $O/shared
waitgpu() { while [ -n "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]; do sleep 2; done; }
tt() { $PY -c 'import json,sys;m={d["name"]:d["value"] for d in json.load(open(sys.argv[1]))["measurements"]};print(" ".join("%s=%.4f"%(k,m[k]) for k in ("t.total","t.total_live") if k in m))' $1 2>/dev/null; }
ttv() { $PY -c 'import json,sys;m={d["name"]:d["value"] for d in json.load(open(sys.argv[1]))["measurements"]};print("%.5f"%m["t.total"])' $1 2>/dev/null || echo 99; }
rust() {  # dir with proofs/ (system.bin, optional system_h.bin)
  local d=$1; local rep=$(ls -d $d/proofs/*/ 2>/dev/null | head -1)
  local hs=""; [ -f $d/proofs/system_h.bin ] && hs="--system-h $d/proofs/system_h.bin"
  $LIGERO_VERIFY batch --system $d/proofs/system.bin $hs --dir ${rep:-$d/proofs} --jobs 8 --threads 1 --target-bits 128 \
      --json $d/proofs/rust_batch.json > $d/rust_batch.out 2> $d/rust_batch.err
  echo "$(date -u +%H:%M:%S) $(basename $d) rust rc=$? $($PY -c 'import json,sys;x=json.load(open(sys.argv[1]));print("accepted",x["accepted"],"/",x["n"],"batch",x["batch_accepted"],"bits %.2f"%x["batch_bits"],"pinned",x["system_pinned"],x["system"]["pinned_relation"])' $d/proofs/rust_batch.json 2>&1 | tail -1)" | tee -a $O/summary.txt
}
b() {  # subdir tag relation batch pipeline dump(0/1) [extra...]
  local sub=$1 tag=$2 rel=$3 l=$4 p=$5 dump=$6; shift 6; local d=$O/$sub/$tag
  rm -rf $d; mkdir -p $d; waitgpu
  local da=""; [ "$dump" = 1 ] && da="--dump-dir $d/proofs --dump-reps 1"
  local t0=$(date +%s)
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $l --pipeline $p \
      --total-vus 4096 --target -128 --reps $REPS $da --out $d/result.json "$@" > $d/log 2>&1
  local rc=$?
  echo "$(date -u +%H:%M:%S) $sub/$tag rel=$rel l=$l p=$p $* rc=$rc $(tt $d/result.json) wall=$(( $(date +%s)-t0 ))s" | tee -a $O/summary.txt
  if [ "$dump" = 1 ] && [ $rc = 0 ]; then rust $d & fi
}
lv() {  # tag relation batch pipeline [extra...]
  local tag=$1 rel=$2 l=$3 p=$4; shift 4; local d=$O/live/$tag
  rm -rf $d; mkdir -p $d; waitgpu
  local t0=$(date +%s)
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $l --pipeline $p \
      --total-vus 4096 --target -128 --reps $REPS --verifier $VER --out $d/result.json "$@" > $d/log 2>&1
  local rc=$?
  echo "$(date -u +%H:%M:%S) live/$tag rel=$rel l=$l p=$p $* rc=$rc $(tt $d/result.json) wall=$(( $(date +%s)-t0 ))s" | tee -a $O/summary.txt
}
probe() { $PY -m backends.direct.ligero.live probe --verifier $VER --mb 2 --repeat 4 2>&1 | tail -3 | tee -a $O/summary.txt; }
