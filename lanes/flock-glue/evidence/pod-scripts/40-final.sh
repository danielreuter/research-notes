#!/usr/bin/env bash
# flock-glue final recorded run (one per pod): rebuild from the sent inputs, bit-exact check + negatives, the
# end-to-end matrix under the Flock b684b12 default profile (before / devwit / devgpu / devovl + phase split), the
# flock-128-r2 cost stand-in (PROFILE=fast100 FREPS=2) for the device paths, and nsys kernel time per batch.
# env: PIPES="hopper_bf16 hopper_e4m3"  NVUS="1024 4096"
set -uxo pipefail
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
I=${INPUTS:-$RESEARCH_RUN_DIR/inputs}
export INPUTS=$I
bash $I/10-build.sh > $RESEARCH_RUN_DIR/build.log 2>&1 || { echo "BUILD FAILED"; tail -n 30 $RESEARCH_RUN_DIR/build.log; exit 1; }
PIPES="$PIPES" bash $I/20-check.sh
grep -h "VCHECK\|VNAN" $RESEARCH_RUN_DIR/check/*.txt
PIPES="$PIPES" NVUS="${NVUS:-1024 4096}" VARIANTS="before devwit devgpu devovl" REPS=${REPS:-5} PHASES=1 bash $I/30-bench.sh
PIPES="$PIPES" NVUS="${NVUS:-1024 4096}" VARIANTS="devgpu devovl" REPS=3 PHASES=0 PROFILE=fast100 FREPS=2 bash $I/30-bench.sh
PIPES="$PIPES" NVUS="${NVUS:-1024 4096}" VARIANTS="devgpu devovl" REPS=3 bash $I/25-nsys.sh
PIPES="$PIPES" NVUS=4096 VARIANTS="devovl" REPS=3 PROFILE=fast100 FREPS=2 bash $I/25-nsys.sh
rm -f $RESEARCH_RUN_DIR/nsys/*.nsys-rep
grep -h VSUMMARY $RESEARCH_RUN_DIR/bench/*.txt > $RESEARCH_RUN_DIR/bench/summary.txt
echo FINAL-DONE
