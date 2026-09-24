#!/usr/bin/env bash
# agkr-nvf4: does the A-GKR GPU prover run on sm_120 at all?  Rust verifier build, then agkr-table's bf16-hopper path
# (circuits at the Hopper model, bench_result --relation bf16-hopper, 1 warm-up + 1 rep) on the RTX 5090.
set -uo pipefail
source /workspace/env.sh
O=/workspace/agkr-nvf4/smoke; mkdir -p $O /workspace/bin
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
echo "== verifier build $(date -u +%H:%M:%S)"
( cd verifier && cargo build --release 2>&1 | tail -2 ) && cp $CARGO_TARGET_DIR/release/verity-gkr-verify /workspace/bin/ && sha256sum /workspace/bin/verity-gkr-verify
echo "== circuits $(date -u +%H:%M:%S)"
$PY -m gpu.v2.export circuits --model hopper_bf16_m16n8k16 --out $O/stmt | cut -c1-200
echo "== bench_result bf16-hopper $(date -u +%H:%M:%S)"
RESEARCH_RUN_DIR=$O/dev $PY bench_result.py $O/stmt --relation bf16-hopper --vus 4096 --reps 1 --warmup 1 \
    --verifier /workspace/bin/verity-gkr-verify --threads 13 > $O/dev.log 2>&1
echo "rc=$?"
grep -E '^\{"(rep|warmup)"|verify rep|"t_total"|"status"|contract_problems|soundness_log2|Error|error|memory' $O/dev.log | cut -c1-300 | tail -14
echo "== done $(date -u +%H:%M:%S)"
