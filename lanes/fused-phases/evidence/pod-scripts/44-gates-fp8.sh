#!/usr/bin/env bash
# fused-phases: gate-vu for the three validated fp8-ada relations at the lane tip (fused hints default on): honest sub-batches
# accepted, the negative battery rejected, zk interactive, local coins.  Untimed; beside the seeded runs (43-ab.sh's timed
# runs wait for an empty GPU).  v3x4: one full sub-batch at the l = 4096 shape (341 VUs).
source /workspace/fused-phases/scripts/lib.sh
cd /workspace/src
G=$FP/gates; mkdir -p $G
gate() {  # gate NAME REL VUS BATCH
  local t0=$(date +%s)
  RESEARCH_GIT_COMMIT=$TIP OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 $PY -m backends.direct.ligero.run --relation $2 gate-vu --vus $3 \
      --batch $4 --zk --mode interactive --out $G/$1.json > $G/$1.log 2>&1
  echo "$1 rc=$? $(( $(date +%s) - t0 ))s :: $(grep -E 'gate: .* failures' $G/$1.log | tail -1)" | tee -a $G/summary.txt
}
gate fp8-ada-v3x4-341 fp8-ada-v3x4 341 4096
gate fp8-ada-v3-64 fp8-ada-v3 64 16384
gate fp8-ada-64 fp8-ada 64 16384
echo GATES_FP8_DONE | tee -a $G/summary.txt
