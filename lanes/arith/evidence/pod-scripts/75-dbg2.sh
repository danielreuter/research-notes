#!/usr/bin/env bash
# arith (diagnostic): what makes timed reps 2-4 slow on the tip (fixed slots) -- capture log (dbg_patch.py) plus per-pass
# host / stage / allocator / gc log (dbg_patch2.py). Throwaway tree /workspace/src-dbg2; results not registered.
source /workspace/arith/scripts/lib.sh
rm -rf /workspace/src-dbg2 && cp -a /workspace/src /workspace/src-dbg2 && $PY /workspace/arith/scripts/dbg_patch.py /workspace/src-dbg2 \
  && $PY /workspace/arith/scripts/dbg_patch2.py /workspace/src-dbg2 || { echo PATCH-FAILED; exit 1; }
export PYTHONUNBUFFERED=1
for rr in 1 2 3; do
  SRC=/workspace/src-dbg2 COMMIT=dbg2 run dbg2-r$rr fp8-ada-v3x4 4096 8 5
  grep -E "^DBG|^rep |^warm-up" $O/dbg2-r$rr/log | cut -c1-260 > $A/dbg2-r$rr.txt
done
echo DONE-75
