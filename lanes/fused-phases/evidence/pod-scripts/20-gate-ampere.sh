#!/usr/bin/env bash
# fused-phases: the bf16-ampere-v3 / v3x4 relations now read the frozen vu-k1536 set (was a synthetic draw): their gate on it
# (honest sub-batches accepted, the negative battery rejected), zk interactive, local coins.  Untimed.
source /workspace/fused-phases/scripts/lib.sh
cd /workspace/src
G=$FP/gates; mkdir -p $G
gate() {  # gate NAME REL VUS BATCH
  local t0=$(date +%s)
  RESEARCH_GIT_COMMIT=$TIP OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 $PY -m backends.direct.ligero.run --relation $2 gate-vu --vus $3 \
      --batch $4 --zk --mode interactive --out $G/$1.json > $G/$1.log 2>&1
  echo "$1 rc=$? $(( $(date +%s) - t0 ))s :: $(grep -E 'gate: .* failures|frozen' $G/$1.log | tail -2 | tr '\n' ' ')" | tee -a $G/summary.txt
}
gate bf16-ampere-v3x4-frozen-256 bf16-ampere-v3x4 256 4096
gate bf16-ampere-v3-frozen-64 bf16-ampere-v3 64 16384
echo GATES_DONE | tee -a $G/summary.txt
