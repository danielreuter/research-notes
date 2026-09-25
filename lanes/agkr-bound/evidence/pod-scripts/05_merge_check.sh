#!/usr/bin/env bash
# agkr-bound: the merged tree (lane/agkr-bound after origin/main c1891d48) on the pod
#  0. cargo build --release + cargo test --release (pins.rs, instances.rs, tests/cli.rs)
#  1. the circuit-pin pytest and the backends/gkr pytest
#  2. the merged-LK E4M3 circuit sets (default export) with torch blocked: the pins.txt lines to add
# usage (research run --on ... --cwd source/backends/gkr --send 05_merge_check.sh): bash 05_merge_check.sh
set -uo pipefail
HERE=$(pwd)
ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT/tools/research/src:$ROOT:$HERE"
export CARGO_TARGET_DIR=/workspace/cargo-target PATH="/workspace/venv312/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:$PATH"
PY=/workspace/venv312/bin/python
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT CARGO_BUILD_JOBS=$NT RAYON_NUM_THREADS=$NT
echo "tree $ROOT; commit ${RESEARCH_SOURCE_COMMIT:-?}; threads $NT; $(rustc --version)"
echo "== 0. cargo ($(date -u +%H:%M:%S))"
( cd verifier && cargo build --release 2>&1 | grep -E "^error|Finished" | head && cargo test --release 2>&1 | grep -E "^test result|FAILED|panicked|^error" )
VB=/workspace/bin/verity-gkr-verify-bound
cp $CARGO_TARGET_DIR/release/verity-gkr-verify $VB && sha256sum $VB
echo "== 1. pytest ($(date -u +%H:%M:%S))"
$PY -m pytest -q -x tests/test_circuit_pins.py 2>&1 | tail -4
$PY -m pytest -q tests 2>&1 | tail -4
echo "== 2. merged E4M3 sets, torch blocked ($(date -u +%H:%M:%S))"
for m in "fp8-ada ada_e4m3_m16n8k32" "fp8-hopper hopper_e4m3_wgmma_k32"; do
  set -- $m; D=$(mktemp -d)
  $PY -c "import sys, runpy; sys.modules['torch'] = None; sys.argv = ['x', 'circuits', '--model', '$2', '--out', '$D']; runpy.run_module('gpu.v2.export', run_name='__main__')" > /dev/null || { echo "$1: generator failed"; continue; }
  S=$($PY -c "import json; print(json.load(open('$D/manifest.json'))['steps'])")
  echo "$1 $S $(sha256sum $D/circuit.txt $D/epilogue.txt $D/chain.txt | cut -c1-64 | tr '\n' ' ')python -m gpu.v2.export circuits --model $2"
  $VB circuit-digest --dir $D
done
echo "== done ($(date -u +%H:%M:%S))"
