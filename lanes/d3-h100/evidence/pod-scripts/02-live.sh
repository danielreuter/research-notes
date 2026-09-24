#!/usr/bin/env bash
# d3-h100 prover: the four H100 Table 2 cells' exact configs (fill-dc's L-* specs: 4096 VUs, --zk --mode interactive, --target -128,
# --reps 5, rep 1 dumped) against the live verifier on the separate CPU pod vy-d3-h100v in the same DC (US-MO-1).
#   LIVE=tcp://64.247.201.13:16766 ROUNDS="1" bash 02-live.sh      -> /workspace/d3-h100/runs/<tag>-r<n>/{result.json,log,meta.txt,proofs/}
# Warm-up first (local coins, --reps 1, untimed, not registered): the first v3x4 process per relation compiles the fused witness kernel.
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 LIGERO_REFERENCE_HINTS=${LIGERO_REFERENCE_HINTS:-0}
LIVE=${LIVE:?LIVE=tcp://HOST:PORT}
O=/workspace/d3-h100/runs; SUM=/workspace/d3-h100/summary.txt; mkdir -p $O
waitgpu() { while [ -n "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]; do sleep 2; done; }
tt() { $PY -c 'import json,sys;r=json.load(open(sys.argv[1]));m={d["name"]:d["value"] for d in r["measurements"]};lv=r.get("validation",{}).get("evidence",{}).get("live_verifier",{});print(" ".join("%s=%.4f"%(k,m[k]) for k in ("t.total","t.total_live","verify.cpu_s") if k in m), "acc=%s dc=%s->%s rtt=%.2f"%(lv.get("accepted"),lv.get("prover_dc"),lv.get("verifier_dc"),lv.get("rtt_ms_median") or -1))' $1 2>/dev/null; }
run() {
  local tag=$1 rel=$2 l=$3 p=$4 reps=$5; shift 5; local d=$O/$tag
  if [ -f $d/result.json ] && [ "${FORCE:-0}" != 1 ]; then echo "$(date -u +%H:%M:%S) skip $tag (done)" | tee -a $SUM; return 0; fi
  rm -rf $d; mkdir -p $d; waitgpu
  echo "tag=$tag rel=$rel l=$l p=$p reps=$reps args=$* load=$(cut -d' ' -f1-3 /proc/loadavg) start=$(date -u +%FT%TZ)" > $d/meta.txt
  local t0=$(date +%s)
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $l --pipeline $p \
      --total-vus 4096 --target -128 --reps $reps --out $d/result.json "$@" > $d/log 2>&1
  local rc=$?
  echo "end=$(date -u +%FT%TZ) rc=$rc wall=$(( $(date +%s) - t0 ))s load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $d/meta.txt
  echo "$(date -u +%H:%M:%S) $tag rc=$rc $(tt $d/result.json) wall=$(( $(date +%s)-t0 ))s $(grep -E 'Traceback|Error' $d/log | tail -1 | cut -c1-120)" | tee -a $SUM
}
SPECS=(b16b:bf16-hopper-v3x4:4096:8 f8b:fp8-hopper-v3x4:4096:8 b16h:bf16-hopper:16384:8:--auth,included-hash f8h:fp8-hopper:16384:8:--auth,included-hash)
if [ "${WARM:-1}" = 1 ]; then
  run warm-b16b bf16-hopper-v3x4 4096 8 1
  run warm-f8b fp8-hopper-v3x4 4096 8 1
fi
$PY -m backends.direct.ligero.live probe --verifier $LIVE --mb 2 --repeat 6 2>&1 | tail -2 | sed "s/^/$(date -u +%H:%M:%S) probe /" | tee -a $SUM
for r in ${ROUNDS:-1}; do
  S=("${SPECS[@]}"); if [ $((r % 2)) -eq 0 ]; then S=(); for ((i=${#SPECS[@]}-1; i>=0; i--)); do S+=("${SPECS[$i]}"); done; fi
  for spec in "${S[@]}"; do
    IFS=: read tag rel l p extra <<< "$spec"
    run L-$tag-r$r $rel $l $p 5 --dump-dir $O/L-$tag-r$r/proofs --dump-reps 1 --verifier $LIVE ${extra//,/ }
  done
done
echo "$(date -u +%H:%M:%S) LIVE_DONE" | tee -a $SUM
