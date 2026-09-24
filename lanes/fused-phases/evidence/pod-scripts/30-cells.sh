#!/usr/bin/env bash
# fused-phases validation on the 4090, fp8-ada, the wave-4090-2 flags (bench-vu --zk --mode interactive --total-vus 4096
# --target -128; v1 / v3 at --batch 16384, v3x4 at --batch 4096; dumps of rep 1):
#   real-<cell>       lane tip, genuine os.urandom, 5 reps: the results to register
#   seed-{pre,post}-<cell>  3adf4c28 files vs lane tip, seeded os.urandom (seeded_run.py), 3 reps: proofs byte-identical?
# Usage: CELLS="v3x4-p8 v3x4-p4 v3-p8 v3-p4 v1-p4" KINDS="real seed" bash 30-cells.sh
source /workspace/fused-phases/scripts/lib.sh
cfg() { case $1 in
  v1-p4) echo "fp8-ada 16384 4" ;;   v3-p4) echo "fp8-ada-v3 16384 4" ;;   v3-p8) echo "fp8-ada-v3 16384 8" ;;
  v3x4-p4) echo "fp8-ada-v3x4 4096 4" ;;   v3x4-p8) echo "fp8-ada-v3x4 4096 8" ;;
  *) echo "unknown" ;; esac; }
for c in $CELLS; do
  read -r rel batch depth <<< "$(cfg $c)"
  for k in ${KINDS:-real seed}; do
    case $k in
      real) run real-$c /workspace/src "" $rel $batch $depth 5 ;;
      seed) run seed-pre-$c /workspace/src-pre 20260924 $rel $batch $depth 3
            run seed-post-$c /workspace/src 20260924 $rel $batch $depth 3
            $PY $FP/scripts/compare.py $O/seed-pre-$c $O/seed-post-$c 2>&1 | tail -1 | tee -a $LOG ;;
    esac
  done
done
echo "CELLS_DONE $CELLS / ${KINDS:-real seed}" | tee -a $LOG
