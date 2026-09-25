#!/usr/bin/env bash
# agkr-bound step 1: the merged A-GKR tree (lane/agkr-fp8 + lane/agkr-nvf4) on the pod.
# research run --on vy-agkr-bound --project verity --source . --cwd source/backends/gkr --send 01_integration.sh \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/01_integration.sh"'
#  0. the Rust verifier: cargo build --release + cargo test --release
#  1. the backends/gkr Python tests (per directory)
#  2. one bench_result cell per relation family (1 rep after 1 warm-up, Python + Rust verifiers); the proof sha256 must equal
#     the verified cell's: bf16-ampere art:300a526a, bf16-hopper art:c09947fd, fp8-hopper art:ad76c106, fp4-nvf4 art:f277786d
# usage: bash 01_integration.sh [cells...]   (default: all four)
set -uo pipefail
HERE=$(pwd)
ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT/tools/research/src:$ROOT:$HERE"
export CARGO_TARGET_DIR=/workspace/cargo-target PATH="/workspace/venv312/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:$PATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/workspace/venv312/bin/python
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT
RD=${RESEARCH_RUN_DIR:?}
echo "tree $ROOT; commit ${RESEARCH_SOURCE_COMMIT:-?}; cpu threads $NT; run dir $RD"
H=/workspace/agkr-bound/integ
mkdir -p $H /workspace/bin
CELLS=${*:-bf16-ampere bf16-hopper fp8-hopper fp4-nvf4}

echo "== 0. verifier ($(date -u +%H:%M:%S))"
( cd verifier && cargo build --release 2>&1 | tail -1 && cargo test --release 2>&1 | grep -E "^test result|FAILED|panicked|error" )
VB=/workspace/bin/verity-gkr-verify-integ
cp $CARGO_TARGET_DIR/release/verity-gkr-verify $VB && sha256sum $VB

echo "== 1. python tests ($(date -u +%H:%M:%S))"
for t in gpu/v2/tests packed/tests tensor/tests tensor/fused/tests; do
  timeout 1500 $PY -m pytest -q -x -p no:cacheprovider $t 2>&1 | tail -3 | sed "s|^|$t: |"
done

declare -A WANT=([bf16-ampere]=f2c058519710faaa2cabae0fa8557ddfd82e7e48c1adf930e7f809623074729c
                 [bf16-hopper]=4a05ada66d857af23883e21d6e782d7053415b7aa5771ee11cf5fdc2c203aeaf
                 [fp8-hopper]=0021aa914caac40c
                 [fp4-nvf4]=ebe7c545705c7e43)
for c in $CELLS; do
  echo "== 2. $c ($(date -u +%H:%M:%S))"
  S=$H/$c/stmt; rm -rf $H/$c; mkdir -p $H/$c
  case $c in
    bf16-ampere) $PY -m gpu.v2.export circuits --model ampere_bf16_m16n8k16 --out $S > /dev/null
                 ARGS="--instances /workspace/bench-instances/v1";;
    bf16-hopper) $PY -m gpu.v2.export circuits --model hopper_bf16_m16n8k16 --out $S > /dev/null; ARGS="--relation $c";;
    fp8-hopper)  $PY -m gpu.v2.export circuits --model hopper_e4m3_wgmma_k32 --out $S > /dev/null; ARGS="--relation $c";;
    fp4-nvf4)    $PY -m gpu.nvf4.circuit export --out $S > /dev/null; ARGS="--relation $c";;
  esac
  RESEARCH_RUN_DIR=$H/$c/run $PY bench_result.py $S $ARGS --vus 4096 --reps 1 --warmup 1 --verifier $VB --threads $NT \
      > $H/$c/bench.log 2>&1
  echo "bench rc=$? ($(date -u +%H:%M:%S))"
  grep -E '^verify rep|Error|Traceback' $H/$c/bench.log | tail -3
  GOT=$($PY -c "import json;d=json.load(open('$H/$c/run/result.json'));r=d['validation']['evidence']['reps'][0];print(r['proof_sha256'], '%.4f' % r['t_total'], d['validation']['status'])" 2>&1)
  W=${WANT[$c]}
  case "$GOT" in "$W"*) echo "$c: MATCH $GOT";; *) echo "$c: DIFF want $W got $GOT";; esac
done
echo "== done ($(date -u +%H:%M:%S))"
