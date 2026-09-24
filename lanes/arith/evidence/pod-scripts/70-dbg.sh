#!/usr/bin/env bash
# arith (diagnostic): which graph captures land in the timed reps -- step 1 vs tip, both with dbg_patch.py's capture log
# (throwaway trees /workspace/src-dbg-*; results not registered).
source /workspace/arith/scripts/lib.sh
for t in s1 tip; do
  src=/workspace/src; [ $t = s1 ] && src=/workspace/src-s1
  rm -rf /workspace/src-dbg-$t && cp -a $src /workspace/src-dbg-$t && $PY /workspace/arith/scripts/dbg_patch.py /workspace/src-dbg-$t
done
export PYTHONUNBUFFERED=1
for rr in 1 2; do
  for t in s1 tip; do
    SRC=/workspace/src-dbg-$t COMMIT=dbg-$t run dbg-$t-r$rr fp8-ada-v3x4 4096 8 5
    grep -E "^DBG|^rep |^warm-up" $O/dbg-$t-r$rr/log | cut -c1-160 > $A/dbg-$t-r$rr.txt
  done
done
echo DONE-70
