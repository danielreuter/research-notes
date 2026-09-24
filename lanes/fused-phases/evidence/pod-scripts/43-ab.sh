#!/usr/bin/env bash
# fused-phases: timing A/B on an idle GPU, same pod, after everything else (42-more.sh's MORE_DONE): fp8-ada-v3x4 l=4096 p8,
# genuine os.urandom, 5 reps, alternating 3adf4c28 files (src-pre) and the lane tip (src).  Controls only: not registered
# as bench results (result.json lines go in the report).
source /workspace/fused-phases/scripts/lib.sh
until grep -q MORE_DONE $LOG; do sleep 10; done
run ab1-pre-v3x4-p8  /workspace/src-pre "" fp8-ada-v3x4 4096 8 5
run ab2-post-v3x4-p8 /workspace/src     "" fp8-ada-v3x4 4096 8 5
run ab3-pre-v3x4-p8  /workspace/src-pre "" fp8-ada-v3x4 4096 8 5
run ab4-post-v3x4-p8 /workspace/src     "" fp8-ada-v3x4 4096 8 5
for t in ab1-pre-v3x4-p8 ab2-post-v3x4-p8 ab3-pre-v3x4-p8 ab4-post-v3x4-p8; do
  echo "$t $(grep -E '^rep [0-9]' $O/$t/log | sed -E 's/.*prover ([0-9.]+)s \(\+hints ([0-9.]+)s\).*/\1+\2/' | tr '\n' ' ')" | tee -a $LOG
done
echo AB_DONE | tee -a $LOG
