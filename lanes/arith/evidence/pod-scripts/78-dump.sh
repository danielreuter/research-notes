#!/usr/bin/env bash
# arith (diagnostic): is the slow timed rep 2 caused by rep 1's proof dump (host heap churn between timed reps)?
# tip, --dump-reps 0 (N) vs 1 (D), alternating x3. Results not registered (N has no proofs).
source /workspace/arith/scripts/lib.sh
while pgrep -f "[7]7-dbg3.sh" >/dev/null; do sleep 5; done
grep -E "^(always|madvise|never)|\[" /sys/kernel/mm/transparent_hugepage/enabled /sys/kernel/mm/transparent_hugepage/defrag | tee -a $LOG
for rr in 1 2 3; do
  run dump-D-r$rr fp8-ada-v3x4 4096 8 5
  run dump-N-r$rr fp8-ada-v3x4 4096 8 5 --dump-reps 0
done
echo DONE-78
