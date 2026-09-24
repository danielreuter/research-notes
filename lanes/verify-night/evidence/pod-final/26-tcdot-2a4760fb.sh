#!/usr/bin/env bash
# verify-night: sp1-tcdot art:2a4760fb (no handoff; found in the 09:50Z pod render): witness arm at lane/sp1-tcdot@97b5b60a,
# fork 6655716e (tree 4ca5a6ca = 6096d886's tree + patches 0010 [chip constrains subnormal GroupSum outputs: an AIR change]
# + 0011 [prover only]); host --features stream-operands. The producer's vk 0x00896ef4 equals 174d7b4d's (6096d886 AIR), so the
# 6096d886 host is run on rep0 as the AIR-pin cross-check.
REV=97b5b60a SRC=/workspace/tcdot-src-97b5b60a TGT=/workspace/tcdot-verify-6655/target FROOT=/workspace/tcdot-verify-6655 OPERANDS=witness FEATURES=stream-operands \
  bash /workspace/verify-night/12-tcdot-build.sh
cd /workspace/src && source /workspace/env.sh
O=/workspace/verify-night/tcdot-2a4760fb; mkdir -p $O
[ -d $O/tree ] || $PY -m research data fetch art:4b3dc262d6111854dcc39697ca4f525be53dd2a2163d8ad6901805c46106e2bb --to $O/tree --path 'proofs/*' > $O/fetch.out 2>&1
{ (cd $O/tree && sha256sum proofs/*); cmp $O/tree/proofs/statement.bin /workspace/verify-night/sp1-a100-2a10bc89/statement.mine.bin && echo "dump statement.bin == mine"; } >> $O/verify.out 2>&1
HOST_BIN=/workspace/tcdot-verify-6655/target/release/verity-tcdot-host TAG=2a4760fb bash /workspace/verify-night/13-tcdot-verify.sh
W=/workspace/tcdot-verify/target-wit/release/verity-tcdot-host
[ -x $W ] || W=$(ls -d /workspace/tcdot-verify*/target*/release/verity-tcdot-host | xargs -n1 sh -c '"$0" info 2>/dev/null | grep -q 6096d886 && echo "$0"' | head -1)
{ echo "=== [$(date -u +%H:%M:%S)] 6096d886 witness host ($W, sha256 $(sha256sum $W | cut -c1-16)) on rep0"
  SP1_PROVER=cpu RUST_LOG=error $W info 2>/dev/null | grep -o '"fork_head":"[0-9a-f]*"'
  SP1_PROVER=cpu RUST_LOG=error $W verify --proof $O/tree/proofs/proof-rep0.bin \
    --statement /workspace/verify-night/sp1-a100-2a10bc89/statement.mine.bin 2>&1 | tail -2; echo "rc=${PIPESTATUS[0]}"
} >> $O/verify.out 2>&1
