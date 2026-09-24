#!/bin/bash
# v3-scout bench chain (runs on the pod): v3 vs v1, 4096 VUs, --zk --mode interactive (local coins), 3 reps, dump rep 1,
# Rust `ligero-verify batch` on the rep-1 dump.  Usage: chain.sh SPEC... where SPEC = tag:relation:batch:depth
source /workspace/env.sh
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
O=/workspace/v3s; L=$O/logs; mkdir -p $O/results $O/dumps $L
log() { echo "$(date -u +%H:%M:%S) $*" >> $L/chain.log; }
for spec in "$@"; do
  IFS=: read tag rel batch depth <<< "$spec"
  if [ -f $O/results/$tag.json ]; then log "skip $tag (done)"; continue; fi
  log "start $tag rel=$rel l=$batch p=$depth load=$(cut -d' ' -f1-3 /proc/loadavg)"
  t0=$(date +%s)
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $batch --pipeline $depth \
      --total-vus 4096 --reps 3 --device cuda --instances-cache /workspace/instances-cache --instance-procs 16 \
      --dump-dir $O/dumps/$tag --dump-reps 1 --out $O/results/$tag.json > $L/$tag.log 2>&1
  rc=$?
  log "bench $tag rc=$rc wall=$(( $(date +%s) - t0 ))s | $(grep -iE 'OutOfMemory|Error|t\.total|validation' $L/$tag.log | tail -3 | tr '\n' ' ' | cut -c1-240)"
  if [ $rc -eq 0 ] && [ -d $O/dumps/$tag/rep1 ]; then
    $LIGERO_VERIFY batch --system $O/dumps/$tag/system.bin --dir $O/dumps/$tag/rep1 --target-bits 128 \
        --json $O/results/${tag}_rust.json > $L/${tag}_rust.log 2>&1
    log "rust $tag rc=$? | $(tail -2 $L/${tag}_rust.log | tr '\n' ' ' | cut -c1-240)"
  fi
done
log "CHAIN_DONE $*"
