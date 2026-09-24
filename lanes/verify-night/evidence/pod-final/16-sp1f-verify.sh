#!/usr/bin/env bash
# verify-night: sp1-formats (handoff 20260924T0712Z): fetch the 4 run-files trees (proofs/*) + the instance files, write my own
# statements (15-sp1f-statements.py), verify the 12 proofs with the 2581406f host (14-sp1f-build.sh), y-flip negative per format.
#   STAGE=prep bash 16-sp1f-verify.sh       (AWS_* read credential in the environment) -> fetch + statements
#   STAGE=verify bash 16-sp1f-verify.sh     -> 12 verifies + 4 negatives
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
O=/workspace/verify-night/sp1f; mkdir -p $O
H=${HOST_BIN:-/workspace/sp1f-target/release/veritor-zk-host}
{
if [ "${STAGE:-verify}" = prep ]; then
  echo "=== [$(date -u +%H:%M:%S)] fetch"
  while read -r f tree; do
    $PY -m research data fetch $tree --to $O/$f --path 'proofs/*' | tail -1
  done <<'EOF'
fp8-ada art:2c9abdc594bcc56c1c2a87bed59b7990ea2903da1544aa0449d486c560f6fd1e
fp8-hopper art:328ed64d4eb82c542e467705d02c2cbb0ad56dd5c731ad1ad5861fa7f8de6e64
bf16-hopper art:114f46e966d9ab534708874d1c43ec962746d9f0b3b8a0bd64cb1593a509e50f
fp4-nvf4 art:bede8807aa969610c2dd33389447172f3a1874749489b52aac69f1b7c24daafc
EOF
  $PY -m research data fetch art:4a6f7602d9962be856131e113d6fe2d2cb92a2701d1a6a7dc699f2e6a7d1a196 --to $O/inst | tail -1
  (cd $O && sha256sum */proofs/* inst/*.bin)
  echo "=== [$(date -u +%H:%M:%S)] statements (mine)"
  $PY /workspace/verify-night/15-sp1f-statements.py $O
  echo "=== [$(date -u +%H:%M:%S)] prep done"
  exit 0
fi
echo "=== [$(date -u +%H:%M:%S)] verify (host sha256 $(sha256sum $H | cut -c1-16))"
SP1_PROVER=cpu RUST_LOG=error $H info 2>/dev/null | grep '^{'
for f in fp8-ada fp8-hopper bf16-hopper fp4-nvf4; do
  for r in 0 1 2; do
    echo "--- $f rep$r"
    SP1_PROVER=cpu RUST_LOG=error $H verify --proof $O/$f/proofs/proof-rep$r.bin --statement $O/$f.mine.bin 2>/dev/null | grep '^{' | tail -1
    echo "rc=${PIPESTATUS[0]}"
  done
  echo "--- $f negative (last y byte flipped) on rep0"
  SP1_PROVER=cpu RUST_LOG=error $H verify --proof $O/$f/proofs/proof-rep0.bin --statement $O/$f.neg.bin 2>/dev/null | grep '^{' | tail -1
  echo "rc=${PIPESTATUS[0]}"
done
echo "=== [$(date -u +%H:%M:%S)] done"
} >> $O/verify.out 2>&1
