#!/usr/bin/env bash
# agkr-bound step 2 development pass (research run --on vy-agkr-bound --project verity --source . --cwd source/backends/gkr
#   --send 02_bind_dev.sh --send 03_negatives.py -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/02_bind_dev.sh" [cells]'):
#  0. the Rust verifier with the operand binding: cargo build --release + cargo test --release
#  1. the pinned-table entries of the five frozen sets (python -m gpu.bind pin)
#  2. per cell: bench_result --bind (1 rep after 1 warm-up; Rust with --require-bound; a recipe set that is not yet
#     pinned is re-verified with --allow-unpinned-instances), then 03_negatives.py
# usage: [PINS=0] bash 02_bind_dev.sh [cells...]   cells: bf16-ampere bf16-hopper fp8-hopper fp8-ada fp4-nvf4
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
H=/workspace/agkr-bound/dev
mkdir -p $H /workspace/bin
CELLS=${*:-bf16-ampere fp8-hopper fp4-nvf4}

echo "== 0. verifier ($(date -u +%H:%M:%S))"
( cd verifier && cargo build --release 2>&1 | grep -E "^(warning|error)|Finished" | head -20 && cargo test --release 2>&1 | grep -E "^test |^test result|FAILED|panicked|error" )
VB=/workspace/bin/verity-gkr-verify-bound
cp $CARGO_TARGET_DIR/release/verity-gkr-verify $VB && sha256sum $VB

if [ "${PINS:-1}" = 1 ]; then
  echo "== 1. pins ($(date -u +%H:%M:%S))"
  $PY -m gpu.bind pin vu-k1536 --instances /workspace/bench-instances/v1 2>&1 | grep -v -i warn | tail -9
  for r in bf16-hopper fp8-hopper fp8-ada fp4-nvf4; do
    $PY -m gpu.bind pin $r --procs $NT 2>&1 | grep -v -i warn | tail -9
  done
fi

for c in $CELLS; do
  echo "== 2. $c ($(date -u +%H:%M:%S))"
  S=$H/$c/stmt; rm -rf $H/$c; mkdir -p $H/$c
  case $c in
    bf16-ampere) $PY -m gpu.v2.export circuits --model ampere_bf16_m16n8k16 --out $S > /dev/null
                 ARGS="--instances /workspace/bench-instances/v1"; REL=vu-k1536;;
    bf16-hopper) $PY -m gpu.v2.export circuits --model hopper_bf16_m16n8k16 --out $S > /dev/null; ARGS="--relation $c"; REL=$c;;
    fp8-hopper)  $PY -m gpu.v2.export circuits --model hopper_e4m3_wgmma_k32 --out $S > /dev/null; ARGS="--relation $c"; REL=$c;;
    fp8-ada)     $PY -m gpu.v2.export circuits --model ada_e4m3_m16n8k32 --out $S > /dev/null; ARGS="--relation $c"; REL=$c;;
    fp4-nvf4)    $PY -m gpu.nvf4.circuit export --out $S > /dev/null; ARGS="--relation $c"; REL=$c;;
  esac
  RESEARCH_RUN_DIR=$H/$c/run $PY bench_result.py $S $ARGS --bind --vus 4096 --reps 1 --warmup 1 --verifier $VB --threads $NT \
      > $H/$c/bench.log 2>&1
  echo "bench rc=$? ($(date -u +%H:%M:%S))"
  grep -E '^verify rep|Error|Traceback|error' $H/$c/bench.log | tail -6
  $PY - $H/$c/run/result.json <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
r = d["validation"]["evidence"]["reps"][0]
fp = d["workload_fingerprint"]
print("t.total %.4f status %s soundness %.2f proof %s" % (r["t_total"], d["validation"]["status"], fp["security"]["achieved_log2"], r["proof_sha256"][:16]))
print("buckets", {k: round(v, 4) for k, v in r["buckets"].items()}, "contract_problems", d.get("contract_problems"))
print("binding", json.dumps(fp.get("operand_binding")))
print("soundness terms", d["validation"]["evidence"]["soundness"]["by_component_log2"])
EOF
  if ! grep -q '^verify rep0: accept' $H/$c/bench.log; then
    $VB verify --dir $H/$c/run/statement --proof $H/$c/run/proofs/rep0.bin --vus 4096 --threads $NT --require-bound \
        --allow-unpinned-instances --json $H/$c/unpinned.json | cut -c1-600
  fi
  echo "-- negatives $c ($(date -u +%H:%M:%S))"
  $PY "$RD/inputs/03_negatives.py" $REL $S $H/$c/neg $VB 4096 $NT 2>&1 | grep -v -i -E "warn|searchsorted" | tail -24
done
echo "== done ($(date -u +%H:%M:%S))"
