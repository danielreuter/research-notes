#!/usr/bin/env bash
# fused-phases (time allowed): once the registrable runs are done, the pytest pass beside the seeded runs (neither needs
# an idle GPU); once 41-rest.sh is done, seeded pairs for the remaining two cells, so all five are byte-compared.
source /workspace/fused-phases/scripts/lib.sh
until grep -q "real-v1-p4" $LOG; do sleep 10; done
bash $FP/scripts/50-pytest.sh > $FP/pytest.out 2>&1 &
while pgrep -f "41-rest.sh" > /dev/null; do sleep 10; done
CELLS="v3x4-p4 v3-p4" KINDS=seed bash $FP/scripts/30-cells.sh
wait
echo MORE_DONE | tee -a $LOG
