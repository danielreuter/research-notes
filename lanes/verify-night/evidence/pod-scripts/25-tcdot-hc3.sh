#!/usr/bin/env bash
# verify-night: sp1-tcdot hill-climb 3 art:a68f2446 (handoff 20260924T0841Z, lower priority): its own host, source d3a5b955 witness
# arm (fork cbf66ccd = f66b4bff + 0001-0006 + witness-operands/0007, tree dc7b3cbd), no stream-operands; vk expected 0x00b4876f
# (the memory arm's vk, different AIR). Then 13-tcdot-verify.sh, and the memory-arm host (d14b4c62) on rep0 (expected: reject).
REV=d3a5b955 SRC=/workspace/tcdot-src-d3a5b955 TGT=/workspace/tcdot-verify-cbf6/target FROOT=/workspace/tcdot-verify-cbf6 OPERANDS=witness \
  bash /workspace/verify-night/12-tcdot-build.sh
cd /workspace/src && source /workspace/env.sh
O=/workspace/verify-night/tcdot-a68f2446; mkdir -p $O
[ -d $O/tree ] || $PY -m research data fetch art:204f58d00c7c015138bed1759a428efc9e55f3782b975cea4b0cf4afff3d2148 --to $O/tree --path 'proofs/*' > $O/fetch.out 2>&1
{ (cd $O/tree && sha256sum proofs/*); cmp $O/tree/proofs/statement.bin /workspace/verify-night/sp1-a100-2a10bc89/statement.mine.bin && echo "dump statement.bin == mine"; } >> $O/verify.out 2>&1
HOST_BIN=/workspace/tcdot-verify-cbf6/target/release/verity-tcdot-host TAG=a68f2446 bash /workspace/verify-night/13-tcdot-verify.sh
M=/workspace/tcdot-verify-d14b/target/release/verity-tcdot-host
{ echo "=== [$(date -u +%H:%M:%S)] memory-arm host (d14b4c62, sha256 $(sha256sum $M | cut -c1-16)) on rep0"
  SP1_PROVER=cpu RUST_LOG=error $M verify --proof $O/tree/proofs/proof-rep0.bin \
    --statement /workspace/verify-night/sp1-a100-2a10bc89/statement.mine.bin 2>&1 | tail -2; echo "rc=${PIPESTATUS[0]}"
} >> $O/verify.out 2>&1
