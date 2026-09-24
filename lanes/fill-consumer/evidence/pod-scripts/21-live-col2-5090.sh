#!/usr/bin/env bash
# fill-consumer, RTX 5090, tree 444084d3: column 2 LIVE on the frozen-set ref (fp4-nvf4+poseidon2 --auth included-hash
# l=8192 p8) against vy-fill-consumer-vtest, started only after the 4090's live rounds on that verifier ended; 3 rounds.
source /workspace/fill-consumer/scripts/lib.sh
VERIFIER=${VERIFIER:-tcp://213.173.105.95:48843}
H="--auth included-hash --auth-cache /workspace/auth-cache-fp4h-frozen"
for r in 1 2 3; do run LF-h-l8192-p8-r$r live fp4-nvf4+poseidon2 8192 8 5 $H; done
echo "LIVE_COL2_DONE" | tee -a $LOG
