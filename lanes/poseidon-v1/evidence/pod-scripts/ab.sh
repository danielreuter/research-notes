#!/usr/bin/env bash
# poseidon-v1 same-pod malloc A/B: re-run a finished sweep's n=4096 point and its plateau with MALLOC_MMAP_MAX_ /
# MALLOC_TRIM_THRESHOLD_ unset (tags SWEEP-unset-nN; evidence for the report, not sweep points).   bash ab.sh SWEEP REL L P
unset MALLOC_MMAP_MAX_ MALLOC_TRIM_THRESHOLD_
SCRIPTS=/workspace/poseidon-v1/scripts; source $SCRIPTS/lib.sh
sid=$1 rel=$2 l=$3 p=$4
pl=$($PY -c "
import json
pts=[json.loads(l) for l in open('$PV/sweeps/$sid.jsonl') if l.strip()]
print(max((p for p in pts if not p.get('failed') and p.get('P')), key=lambda p: p['P'])['n'])")
for n in $(echo 4096 $pl | tr ' ' '\n' | sort -un); do
  run $sid-unset-n$n /workspace/src $rel $l $p $n
  echo "AB $sid n=$n set: $($PY $SCRIPTS/line.py $O/$sid-n$n | tail -1) | unset: $($PY $SCRIPTS/line.py $O/$sid-unset-n$n | tail -1)" | tee -a $LOG
done
