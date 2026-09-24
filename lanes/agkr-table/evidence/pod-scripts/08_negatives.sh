#!/usr/bin/env bash
# agkr-table: negatives after a prover change -- the 52 vu-k1536-neg instances proved by the CURRENT /workspace/src tree
# (prover-side rejection or the Python verifier), their proofs dumped and re-checked by the Rust verifier.
# $1 = a tag for the output names (e.g. qceval).
set -uo pipefail
source /workspace/env.sh
O=/workspace/agkr-table
TAG=${1:-cur}
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
ts() { date -u +%H:%M:%S; }
echo "=== $(ts) negatives $TAG (prover side, proofs dumped)"
rm -rf $O/negproofs_$TAG && mkdir -p $O/negproofs_$TAG
$PY -m gpu.run negatives $O/bb/neg --device cuda --json $O/neg_$TAG.json --proof-dir $O/negproofs_$TAG > $O/neg_$TAG.out 2>&1
echo "rc=$?"; tail -2 $O/neg_$TAG.out | cut -c1-300
echo "=== $(ts) negatives $TAG (Rust verifier on the dumped proofs)"
/workspace/bin/verity-gkr-verify negatives --dir $O/bb/neg --proofs $O/negproofs_$TAG --threads 15 --json $O/neg_rust_$TAG.json 2>&1 | tail -3
echo "=== $(ts) done"
