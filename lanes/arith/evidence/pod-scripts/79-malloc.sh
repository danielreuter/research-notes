#!/usr/bin/env bash
# arith (diagnostic): are the random slow reps (all of it main-thread time in the last stage: numpy copies out of pinned
# buffers into fresh host arrays) page-fault stalls on memory glibc returned to the kernel? tip, default malloc (D) vs
# glibc pinned (M: MALLOC_MMAP_THRESHOLD_=1 GiB, MALLOC_TRIM_THRESHOLD_=64 GiB -> freed arrays stay in the heap and are
# reused), alternating x3. Results not registered.
source /workspace/arith/scripts/lib.sh
while pgrep -f "[7]8-dump.sh|[8]5-reg-rv.sh|[r]everify" >/dev/null; do sleep 5; done
for rr in 1 2 3; do
  run mal-D-r$rr fp8-ada-v3x4 4096 8 5
  MALLOC_MMAP_THRESHOLD_=1073741824 MALLOC_TRIM_THRESHOLD_=68719476736 run mal-M-r$rr fp8-ada-v3x4 4096 8 5
done
echo DONE-79
