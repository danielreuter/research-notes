#!/usr/bin/env bash
# agkr-table: SHA-512 Merkle (proof.bin v2) correctness on the A100 -- prove + Python verify + Rust verify, the 52
# vu-k1536-neg negatives (prover side + Rust verifier), a sampled mutation campaign.  Warm-up time is logged per phase.
set -uo pipefail
source /workspace/env.sh
O=/workspace/agkr-table
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
ts() { date -u +%H:%M:%S; }
echo "=== $(ts) verifier build + unit tests"
( cd verifier && cargo build --release 2>&1 | grep -E "^(error|warning: unused)|Finished" ; cargo test --release --quiet 2>&1 | grep -E "test result|FAILED|panicked" ) \
  && cp $CARGO_TARGET_DIR/release/verity-gkr-verify /workspace/bin/verity-gkr-verify && sha256sum /workspace/bin/verity-gkr-verify
echo "=== $(ts) prove (bench_result.py, 1 warm-up + 2 reps) with the Rust verifier"
RESEARCH_RUN_DIR=$O/sha512 $PY bench_result.py $O/bb/pos4096 --vus 4096 --checker v2 --path graphed --reps 2 --warmup 1 \
    --verifier /workspace/bin/verity-gkr-verify --threads 15 > $O/sha512.out 2>&1
echo "rc=$?"; grep -v -i warn $O/sha512.out | grep -v searchsorted | cut -c1-400
echo "=== $(ts) negatives (prover side, proofs dumped)"
mkdir -p $O/negproofs
$PY -m gpu.run negatives $O/bb/neg --device cuda --json $O/neg.json --proof-dir $O/negproofs > $O/neg.out 2>&1
echo "rc=$?"; tail -3 $O/neg.out | cut -c1-400
echo "=== $(ts) negatives (Rust verifier on the dumped proofs)"
/workspace/bin/verity-gkr-verify negatives --dir $O/bb/neg --proofs $O/negproofs --threads 15 --json $O/neg_rust.json 2>&1 | tail -4
echo "=== $(ts) mutations (Rust verifier, sample 6 per group)"
/workspace/bin/verity-gkr-verify mutate --dir $O/bb/pos4096 --proof $O/sha512/proofs/rep0.bin --vus 4096 --threads 15 --sample 6 --parallel 1 \
    --json $O/mutate.json 2>&1 | tail -12
echo "=== $(ts) done"
