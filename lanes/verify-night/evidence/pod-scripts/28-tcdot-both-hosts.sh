#!/usr/bin/env bash
# verify-night: sp1-tcdot handoff 20260924T0954Z, art:0a66c35e (runs art:2dc0261c) and art:b147a31c (runs art:ee9b4fdf).
# My 6655716e host (26: REV=97b5b60a, fork 6655716e / tree 4ca5a6ca, stream-operands) reports vk 0x009f022f..., not the 0x00896ef4...
# the handoff and manifests record; its embedded guest's loaded sections are byte-identical to my 6096d886 build's (vk 0x00896ef4),
# so the vk change is the fork's (patch 0010). Both hosts on both results decide which constraint system the proofs satisfy.
H6655=/workspace/tcdot-verify-6655/target/release/verity-tcdot-host
H6096=/workspace/tcdot-verify-wit/target/release/verity-tcdot-host
for t in 0a66c35e b147a31c; do HOST_BIN=$H6655 TAG=$t bash /workspace/verify-night/13-tcdot-verify.sh; done
for t in 0a66c35e b147a31c; do
  O=/workspace/verify-night/tcdot-$t
  { echo "=== [$(date -u +%H:%M:%S)] 6096d886 witness host ($(sha256sum $H6096 | cut -c1-16)) on all reps"
    SP1_PROVER=cpu RUST_LOG=error $H6096 info 2>/dev/null | grep -oE '"(fork_head|vk_hash)":"[0-9a-fx]*"' | tr '\n' ' '; echo
    for f in $O/tree/proofs/proof-rep*.bin; do echo "--- $(basename $f) [6096d886 host]"
      SP1_PROVER=cpu RUST_LOG=error $H6096 verify --proof $f --statement /workspace/verify-night/sp1-a100-2a10bc89/statement.mine.bin 2>&1 | grep -E '^\{|Error' | tail -2; echo "rc=${PIPESTATUS[0]}"
    done
    echo "=== [$(date -u +%H:%M:%S)] done"
  } >> $O/verify.out 2>&1
done
