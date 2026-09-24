#!/usr/bin/env bash
# verify-night: verify modified-SP1 (TC_DOT) relation-bare/v2 proofs (sp1-tcdot handoff 20260924T0655Z).
#   TREE=art:<run-files> TAG=<name> [STAGE=fetch|verify] bash 13-tcdot-verify.sh      (AWS_* read credential for fetch)
# Statement: /workspace/verify-night/sp1-a100-2a10bc89/statement.mine.bin, written by 09-sp1-verify.sh from MY tree's frozen
# fixture (relation-bare/v2 is byte-identical between stock SP1 and the fork). Host: 12-tcdot-build.sh.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
H=${HOST_BIN:-/workspace/tcdot-verify/target/release/verity-tcdot-host}
S=/workspace/verify-night/sp1-a100-2a10bc89
O=/workspace/verify-night/tcdot-$TAG; mkdir -p $O
{
if [ "${STAGE:-verify}" = fetch ]; then
  echo "=== [$(date -u +%H:%M:%S)] fetch $TREE"
  $PY -m research data fetch $TREE --to $O/tree --path 'proofs/*' | tail -1
  sha256sum $O/tree/proofs/*
  cmp $O/tree/proofs/statement.bin $S/statement.mine.bin && echo "dump statement.bin == mine"
  exit 0
fi
echo "=== [$(date -u +%H:%M:%S)] verify (host sha256 $(sha256sum $H | cut -c1-16))"
SP1_PROVER=cpu RUST_LOG=error $H info 2>/dev/null | grep '^{'
for f in $O/tree/proofs/proof-rep*.bin; do
  echo "--- $(basename $f)"
  t0=$(date +%s)
  SP1_PROVER=cpu RUST_LOG=error $H verify --proof $f --statement $S/statement.mine.bin 2>/dev/null | grep '^{' | tail -1
  echo "rc=${PIPESTATUS[0]} wall=$(( $(date +%s) - t0 ))s"
done
echo "--- negatives on rep0: (a) last y byte flipped in the statement, (b) one proof byte flipped (middle)"
P0=$(ls $O/tree/proofs/proof-rep*.bin | head -1)
SP1_PROVER=cpu RUST_LOG=error $H verify --proof $P0 --statement $S/statement.neg.bin 2>/dev/null | grep '^{' | tail -1; echo "rc=${PIPESTATUS[0]}"
$PY - "$P0" "$O/proof-neg.bin" <<'PYEOF'
import sys
b = bytearray(open(sys.argv[1], "rb").read()); i = len(b) // 2; b[i] ^= 0x01
open(sys.argv[2], "wb").write(bytes(b)); print(f"flipped byte {i} of {len(b)}")
PYEOF
SP1_PROVER=cpu RUST_LOG=error $H verify --proof $O/proof-neg.bin --statement $S/statement.mine.bin 2>&1 | tail -2; echo "rc=${PIPESTATUS[0]}"
echo "=== [$(date -u +%H:%M:%S)] done"
} >> $O/verify.out 2>&1
