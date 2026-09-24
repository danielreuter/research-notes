#!/usr/bin/env bash
# verify-night: sp1-formats re-proofs from the faster guest at 3510cfcf (handoff 20260924T0742Z): same statements, new ELF / vk.
#   STAGE=prep bash 19-sp1f2-verify.sh      (AWS_* read credential in the environment) -> fetch the 4 trees, compare statement.bin
#   STAGE=verify bash 19-sp1f2-verify.sh    -> 12 verifies + 4 y-flip negatives with the 3510cfcf host (18-sp1-build-rev.sh)
# Statements: MY <fmt>.mine.bin / <fmt>.neg.bin written by 15-sp1f-statements.py for the 07:12Z set (/workspace/verify-night/sp1f),
# from my tree's frozen loaders; the dumps' statement.bin are only compared with them.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
S=/workspace/verify-night/sp1f; O=/workspace/verify-night/sp1f-3510; mkdir -p $O
H=${HOST_BIN:-/workspace/sp1-target-3510cfcf/release/veritor-zk-host}
{
if [ "${STAGE:-verify}" = prep ]; then
  echo "=== [$(date -u +%H:%M:%S)] fetch"
  while read -r f tree; do
    $PY -m research data fetch $tree --to $O/$f --path 'proofs/*' | tail -1
  done <<'EOF'
fp8-ada art:8f3a4cfc4008dab6c8970f438819ef877a719d9859635aa7f9cb394dc5448602
fp8-hopper art:4d63c3571dc0f3b14daacd7711cc68097dcb88f220e916e952f4458152596a0f
bf16-hopper art:0cabdd776e842e76b181c7807120510e244357e14ec139863911774edd6537e0
fp4-nvf4 art:5bd375d2c6a868452f7812d9787fef59e1e0fd6fa203a2a54a89db60cd81f9a8
EOF
  (cd $O && sha256sum */proofs/*)
  for f in fp8-ada fp8-hopper bf16-hopper fp4-nvf4; do
    P=$(dirname $(find $O/$f -name statement.bin | head -1))
    cmp $P/statement.bin $S/$f.mine.bin && echo "$f: dump statement.bin == mine"
  done
  echo "=== [$(date -u +%H:%M:%S)] prep done"
  exit 0
fi
echo "=== [$(date -u +%H:%M:%S)] verify (host sha256 $(sha256sum $H | cut -c1-16))"
SP1_PROVER=cpu RUST_LOG=error $H info 2>/dev/null | grep '^{'
for f in fp8-ada fp8-hopper bf16-hopper fp4-nvf4; do
  P=$(dirname $(find $O/$f -name statement.bin | head -1))
  for r in 0 1 2; do
    echo "--- $f rep$r"
    SP1_PROVER=cpu RUST_LOG=error $H verify --proof $P/proof-rep$r.bin --statement $S/$f.mine.bin 2>/dev/null | grep '^{' | tail -1
    echo "rc=${PIPESTATUS[0]}"
  done
  echo "--- $f negative (last y byte flipped) on rep0"
  SP1_PROVER=cpu RUST_LOG=error $H verify --proof $P/proof-rep0.bin --statement $S/$f.neg.bin 2>/dev/null | grep '^{' | tail -1
  echo "rc=${PIPESTATUS[0]}"
done
echo "=== [$(date -u +%H:%M:%S)] done"
} >> $O/verify.out 2>&1
