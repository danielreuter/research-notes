#!/usr/bin/env bash
# agkr-nvf4 recorded cell run (research run --source . --cwd source/backends/gkr): the fp4-nvf4 export of the SHIPPED tree,
# its Rust verifier built from the shipped tree, then bench_result --relation fp4-nvf4 at 4096 VUs, REPS reps.
# usage: bash 04_record.sh [REPS] [negatives]
set -uo pipefail
REPS=${1:-3}; MODE=${2:-cell}
HERE=$(pwd)                                   # <shipped tree>/backends/gkr
ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT:$HERE"
export CARGO_TARGET_DIR=/workspace/cargo-target PATH="$HOME/.cargo/bin:$PATH"
PY=/workspace/venv312/bin/python
# research run does not source env.sh: without its thread caps the pools size to nproc (32) under the pod's 13.6-core
# cgroup quota and every CPU phase is throttled (prover t.total 0.274 -> 0.314 s, Rust verify 0.164 -> 0.19 s at ab57df0a).
Q=$(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us 2>/dev/null || echo -1); PER=$(cat /sys/fs/cgroup/cpu/cpu.cfs_period_us 2>/dev/null || echo 100000)
NT=$(( Q > 0 ? Q / PER : $(nproc) ))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT
echo "cpu threads $NT (cgroup quota $Q / $PER, nproc $(nproc))"
RD=${RESEARCH_RUN_DIR:?}
echo "tree $ROOT; commit ${RESEARCH_SOURCE_COMMIT:-?}; run dir $RD"
( cd verifier && cargo build --release 2>&1 | tail -1 )
VB=/workspace/bin/verity-gkr-verify-$(basename $ROOT | cut -c1-12)
cp $CARGO_TARGET_DIR/release/verity-gkr-verify $VB && sha256sum $VB
$PY -m gpu.nvf4.circuit export --out $RD/export | cut -c1-240
if [ "$MODE" = negatives ]; then
    NVF4_SRC=$ROOT NVF4_VERIFIER=$VB bash /workspace/agkr-nvf4/pod-scripts/03_negatives.sh $RD/export $RD/negatives
    exit $?
fi
$PY bench_result.py $RD/export --relation fp4-nvf4 --vus 4096 --reps $REPS --warmup 1 --verifier $VB --threads 13
