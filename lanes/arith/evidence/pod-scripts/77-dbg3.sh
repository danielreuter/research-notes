#!/usr/bin/env bash
# arith (diagnostic): the slow timed rep 2 (0.5-1.9 s) seen without the capture log -- tip + dbg_patch2.py only (per-pass
# stage / allocator / gc log), buffered (B) vs PYTHONUNBUFFERED=1 (U) alternating. Throwaway tree; results not registered.
source /workspace/arith/scripts/lib.sh
while pgrep -f "[9]5-ab-warm.sh" >/dev/null; do sleep 5; done
rm -rf /workspace/src-dbg3 && cp -a /workspace/src /workspace/src-dbg3 && $PY /workspace/arith/scripts/dbg_patch2.py /workspace/src-dbg3 \
  || { echo PATCH-FAILED; exit 1; }
for rr in 1 2; do
  for m in B U; do
    if [ $m = U ]; then export PYTHONUNBUFFERED=1; else unset PYTHONUNBUFFERED; fi
    SRC=/workspace/src-dbg3 COMMIT=dbg3 run dbg3-$m-r$rr fp8-ada-v3x4 4096 8 5
    grep -E "^DBG|^rep |^warm-up" $O/dbg3-$m-r$rr/log | cut -c1-260 > $A/dbg3-$m-r$rr.txt
  done
done
unset PYTHONUNBUFFERED
echo DONE-77
