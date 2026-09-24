#!/usr/bin/env bash
# fill-dc bench helpers (sourced on the prover pod). One job on the GPU at a time (waitgpu before every run).
#   run TAG REL L P [extra bench-vu args...]   -> $O/TAG/{result.json,log,meta.txt[,proofs/]}
# Flags (handoff fused-phases 0554Z): bench-vu --zk --mode interactive --total-vus 4096 --target -128 --reps $REPS
#   --batch L --pipeline P; DUMP=1 adds --dump-dir TAG/proofs --dump-reps 1; LIVE=tcp://H:P adds --verifier.
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
# skips only the warm-up sub-batch's Python reference-hints comparison (~100 s per v3/v3x4 process, wave-h100-2); self-check
# and the in-process verification still run
export LIGERO_REFERENCE_HINTS=${LIGERO_REFERENCE_HINTS:-0}
REPS=${REPS:-5}
O=/workspace/fill-dc/runs; SUM=/workspace/fill-dc/summary.txt; mkdir -p $O
waitgpu() { while [ -n "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]; do sleep 2; done; }
tt() { $PY -c 'import json,sys;m={d["name"]:d["value"] for d in json.load(open(sys.argv[1]))["measurements"]};print(" ".join("%s=%.4f"%(k,m[k]) for k in ("t.total","t.total_live") if k in m))' $1 2>/dev/null; }
ok() { $PY - "$1" <<'EOF' 2>/dev/null
import json, sys
from verity_numerical.bench import contract
r = json.load(open(sys.argv[1])); p = contract.validate(r)
print("contract=ok" if not p else "contract=" + str(len(p)) + ":" + p[0][:90].replace(" ", "_"))
EOF
}
run() {
  local tag=$1 rel=$2 l=$3 p=$4; shift 4; local d=$O/$tag
  if [ -f $d/result.json ] && [ "${FORCE:-0}" != 1 ]; then echo "$(date -u +%H:%M:%S) skip $tag (done)" | tee -a $SUM; return 0; fi
  rm -rf $d; mkdir -p $d; waitgpu
  local extra=(); [ "${DUMP:-0}" = 1 ] && extra+=(--dump-dir $d/proofs --dump-reps 1)
  [ -n "${LIVE:-}" ] && extra+=(--verifier $LIVE)
  echo "tag=$tag rel=$rel l=$l p=$p reps=$REPS dump=${DUMP:-0} live=${LIVE:-} args=$* load=$(cut -d' ' -f1-3 /proc/loadavg) start=$(date -u +%FT%TZ)" > $d/meta.txt
  local t0=$(date +%s)
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch $l --pipeline $p \
      --total-vus 4096 --target -128 --reps $REPS --out $d/result.json "${extra[@]}" "$@" > $d/log 2>&1
  local rc=$?
  echo "end=$(date -u +%FT%TZ) rc=$rc wall=$(( $(date +%s) - t0 ))s load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $d/meta.txt
  echo "$(date -u +%H:%M:%S) $tag rel=$rel l=$l p=$p $* rc=$rc $(tt $d/result.json) $(ok $d/result.json) wall=$(( $(date +%s)-t0 ))s load=$(cut -d' ' -f1 /proc/loadavg) $(grep -E 'Traceback|Error' $d/log | tail -1 | cut -c1-120)" | tee -a $SUM
  return $rc
}
# spec = tag:rel:l:p[:extra,comma,separated]; round r runs SPECS in order on odd r, reversed on even r
round() {
  local r=$1; shift; local S=("$@")
  if [ $((r % 2)) -eq 0 ]; then local R=(); for ((i=${#S[@]}-1; i>=0; i--)); do R+=("${S[$i]}"); done; S=("${R[@]}"); fi
  for spec in "${S[@]}"; do
    IFS=: read tag rel l p extra <<< "$spec"
    run $tag-r$r $rel $l $p ${extra//,/ }
  done
  echo "$(date -u +%H:%M:%S) ROUND_${r}_DONE ${PREFIX:-}" | tee -a $SUM
}
