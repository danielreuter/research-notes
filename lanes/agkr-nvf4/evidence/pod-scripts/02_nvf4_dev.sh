#!/usr/bin/env bash
# agkr-nvf4 dev loop: Rust verifier build, the fp4-nvf4 export, bench_result --relation fp4-nvf4 at VUS (default 64).
set -uo pipefail
source /workspace/env.sh
VUS=${1:-64}; REPS=${2:-1}
O=/workspace/agkr-nvf4/dev$VUS; rm -rf $O; mkdir -p $O /workspace/bin
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
echo "== verifier build $(date -u +%H:%M:%S)"
( cd verifier && cargo build --release 2>&1 | grep -E "^error|warning: unused|Finished" | tail -5 ) && cp $CARGO_TARGET_DIR/release/verity-gkr-verify /workspace/bin/ && sha256sum /workspace/bin/verity-gkr-verify
echo "== export $(date -u +%H:%M:%S)"
$PY -m gpu.nvf4.circuit export --out $O/stmt | cut -c1-300
echo "== bench_result fp4-nvf4 vus=$VUS $(date -u +%H:%M:%S)"
RESEARCH_RUN_DIR=$O/run $PY bench_result.py $O/stmt --relation fp4-nvf4 --vus $VUS --reps $REPS --warmup 1 \
    --verifier /workspace/bin/verity-gkr-verify --threads 15 > $O/dev.log 2>&1
echo "rc=$?"
grep -vE "UserWarning|searchsorted" $O/dev.log | cut -c1-400 | tail -30
nvidia-smi --query-gpu=memory.used --format=csv
echo "== done $(date -u +%H:%M:%S)"
