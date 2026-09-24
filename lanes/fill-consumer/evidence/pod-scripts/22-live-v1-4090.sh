#!/usr/bin/env bash
# fill-consumer, RTX 4090: the frozen-set fallback for the bare column (coordinator 06:47Z: fp8-ada l=16384 p4 live),
# against vy-fill-consumer-vtest after the 5090's column-2 live rounds ended; 3 rounds, --reps 5.
source /workspace/fill-consumer/scripts/lib.sh
VERIFIER=${VERIFIER:-tcp://213.173.105.95:48843}
for r in 1 2 3; do run L-b-v1-p4-r$r live fp8-ada 16384 4 5; done
echo "LIVE_V1_DONE" | tee -a $LOG
