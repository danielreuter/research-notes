#!/usr/bin/env bash
# b-ligero-sha256: per-proof settings screen at 4096 VUs (no dump), --commit-per-rep, 3 reps. CONFIGS="rel:l:p ..."
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}
for c in ${CONFIGS:?}; do
  IFS=: read -r REL L PP <<<"$c"; tag=$(echo "$REL-l$L-p$PP" | tr '+' '_')
  gpu_idle || exit 3
  echo "=== $(date -u +%H:%M:%SZ) $tag"
  $PY -u -m backends.direct.ligero.run --relation $REL bench-vu --zk --mode interactive --auth included-hash --commit-per-rep \
      --batch $L --pipeline $PP --total-vus ${VUS:-4096} --target -128 --reps ${REPS:-3} --device cuda --instance-procs ${IPROCS:-16} --out $RD/$tag.json > $RD/$tag.log 2>&1
  echo "rc=$?"; grep -E "^rep |OOM|OutOfMemory|Error" $RD/$tag.log | cut -c1-300 | tail -6
  $PY - $RD/$tag.json <<'PY' 2>/dev/null
import json,sys; d=json.load(open(sys.argv[1])); m={x["name"]:x["value"] for x in d["measurements"]}
print({k: m.get(k) for k in ("t.total","commitment.seconds","end_to_end.seconds","end_to_end.vu_per_second","mem.peak_device_bytes","split.subbatches","soundness_bits")}, d.get("contention",{}).get("contended"))
PY
done
