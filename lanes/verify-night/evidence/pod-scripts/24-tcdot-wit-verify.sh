#!/usr/bin/env bash
# verify-night: sp1-tcdot witness-operands arm (handoff 20260924T0841Z): art:174d7b4d then art:76c113f4 with the witness host
# (12-tcdot-build.sh REV=0742a046 OPERANDS=witness FEATURES=stream-operands; fork 6096d886), 13-tcdot-verify.sh each (3 reps +
# statement-flip and proof-byte-flip negatives); then the MEMORY-arm host (fork d14b4c62) on rep0 of each: expected to reject.
W=/workspace/tcdot-verify-wit/target/release/verity-tcdot-host
M=/workspace/tcdot-verify-d14b/target/release/verity-tcdot-host
for t in 174d7b4d 76c113f4; do HOST_BIN=$W TAG=$t bash /workspace/verify-night/13-tcdot-verify.sh; done
for t in 174d7b4d 76c113f4; do
  { echo "=== [$(date -u +%H:%M:%S)] memory-arm host (d14b4c62, sha256 $(sha256sum $M | cut -c1-16)) on rep0"
    SP1_PROVER=cpu RUST_LOG=error $M verify --proof /workspace/verify-night/tcdot-$t/tree/proofs/proof-rep0.bin \
      --statement /workspace/verify-night/sp1-a100-2a10bc89/statement.mine.bin 2>&1 | tail -2; echo "rc=${PIPESTATUS[0]}"
  } >> /workspace/verify-night/tcdot-$t/verify.out 2>&1
done
