#!/usr/bin/env bash
# verify-night: sp1-tcdot handoff 20260924T0954Z: art:0a66c35e (runs art:2dc0261c) and hill-climb 6 art:b147a31c (runs art:ee9b4fdf,
# fork 0e00bd15 = 0010 alone) with the 6655716e witness host (26-tcdot-2a4760fb.sh builds it); then the 6096d886 witness host
# (vk 0x00896ef4 too, 1166-column TC_DOT_BF16) on 0a66c35e rep0 as the AIR-pin cross-check.
B=/workspace/verify-night/tcdot-build-97b5b60a.out
until grep -q '^=== \[.*\] done' $B 2>/dev/null && [ -s /workspace/verify-night/tcdot-2a4760fb/verify.out ] && grep -q 'witness host' /workspace/verify-night/tcdot-2a4760fb/verify.out; do sleep 15; done
sleep 60
H=/workspace/tcdot-verify-6655/target/release/verity-tcdot-host
for t in 0a66c35e b147a31c; do HOST_BIN=$H TAG=$t bash /workspace/verify-night/13-tcdot-verify.sh; done
O=/workspace/verify-night/tcdot-0a66c35e; W=/workspace/tcdot-verify-wit/target/release/verity-tcdot-host
{ echo "=== [$(date -u +%H:%M:%S)] 6096d886 witness host ($W, sha256 $(sha256sum $W | cut -c1-16)) on rep0"
  SP1_PROVER=cpu RUST_LOG=error $W info 2>/dev/null | grep -o '"fork_head":"[0-9a-f]*"'
  SP1_PROVER=cpu RUST_LOG=error $W verify --proof $O/tree/proofs/proof-rep0.bin \
    --statement /workspace/verify-night/sp1-a100-2a10bc89/statement.mine.bin 2>&1 | tail -2; echo "rc=${PIPESTATUS[0]}"
  echo "=== [$(date -u +%H:%M:%S)] done"
} >> $O/verify.out 2>&1
