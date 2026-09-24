#!/usr/bin/env bash
# agkr-table: checker-v2 BabyBear exports of the frozen vu-k1536 set (timed: CPU witness generation, the reference the GPU
# witness generator must reproduce byte for byte), the independent Rust verifier, and a baseline prove on the A100.
set -uo pipefail
source /workspace/env.sh
O=/workspace/agkr-table
mkdir -p $O/bb
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
NP=15   # cgroup quota 1530000/100000 (nproc reports the host's 128)
t0() { date +%s.%N; }
echo "=== $(date -u +%H:%M:%S) export pos4096 (procs $NP)"
a=$(t0); $PY -m gpu.v2.export export --root /workspace/src/fixtures/bench-instances/v1 --tier vu-k1536 --hi 4096 \
    --out $O/bb/pos4096 --procs $NP > $O/export_pos4096.json 2> $O/export_pos4096.err
echo "rc=$? wall $(python3 -c "print(round($(t0) - $a, 1))") s"
echo "=== $(date -u +%H:%M:%S) export neg"
a=$(t0); $PY -m gpu.v2.export export --root /workspace/src/fixtures/bench-instances/v1 --tier vu-k1536-neg \
    --out $O/bb/neg --procs $NP > $O/export_neg.json 2> $O/export_neg.err
echo "rc=$? wall $(python3 -c "print(round($(t0) - $a, 1))") s"
echo "=== $(date -u +%H:%M:%S) verifier build"
( cd verifier && cargo build --release 2>&1 | tail -2 ) && cp $CARGO_TARGET_DIR/release/verity-gkr-verify /workspace/bin/ && sha256sum /workspace/bin/verity-gkr-verify
echo "=== $(date -u +%H:%M:%S) baseline prove (bench_result.py --checker v2, graphed, 1 warmup + 2 reps)"
RESEARCH_RUN_DIR=$O/baseline $PY bench_result.py $O/bb/pos4096 --vus 4096 --checker v2 --path graphed --reps 2 --warmup 1 \
    --verifier /workspace/bin/verity-gkr-verify --threads $NP > $O/baseline.out 2>&1
echo "rc=$?"; tail -12 $O/baseline.out
echo "=== $(date -u +%H:%M:%S) done"
