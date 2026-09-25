#!/usr/bin/env bash
# agkr-bound: the operands-committed scaffold (gpu/commit.py, verifier commitments.rs) on the pod
# research run --on vy-agkr-bound2 --project verity --source . --cwd source/backends/gkr --send 09_commit_dev.sh \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/09_commit_dev.sh" [cells]'
#  0. cargo build --release + cargo test --release (commitments.rs conformance vs frame_v3/vectors.json)
#  1. pytest tests/test_commit.py tests/test_circuit_pins.py
#  2. the root pins of each cell (python -m gpu.commit pin): Rust literals for commitments.rs PINS
#  3. per cell: bench_result --commit (1 rep after 1 warm-up), Rust under --allow-any-circuit --require-commitment
# usage: [PINS=0] [BENCH=0] bash 09_commit_dev.sh [cells...]   cell = <relation>:<sha256|blake3>
set -uo pipefail
HERE=$(pwd)
ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT/tools/research/src:$ROOT:$HERE"
export CARGO_TARGET_DIR=/workspace/cargo-target PATH="/workspace/venv312/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:$PATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/workspace/venv312/bin/python
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT CARGO_BUILD_JOBS=$NT
RD=${RESEARCH_RUN_DIR:?}
echo "tree $ROOT; commit ${RESEARCH_SOURCE_COMMIT:-?}; cpu threads $NT; run dir $RD"
H=/workspace/agkr-bound/commit
mkdir -p $H /workspace/bin
CELLS=${*:-bf16-ampere:sha256 fp8-hopper:blake3 fp4-nvf4:sha256}

echo "== 0. verifier ($(date -u +%H:%M:%S))"
( cd verifier && cargo build --release 2>&1 | grep -E "^(warning|error)|Finished" | head -20 && cargo test --release 2>&1 | grep -E "^test |^test result|FAILED|panicked|^error" )
VB=/workspace/bin/verity-gkr-verify-commit
cp $CARGO_TARGET_DIR/release/verity-gkr-verify $VB && sha256sum $VB

echo "== 1. pytest ($(date -u +%H:%M:%S))"
$PY -m pytest -q -p no:cacheprovider tests/test_commit.py 2>&1 | tail -6
$PY -m pytest -q -p no:cacheprovider tests/test_circuit_pins.py 2>&1 | tail -3

if [ "${PINS:-1}" = 1 ]; then
  echo "== 2. root pins ($(date -u +%H:%M:%S))"
  for cell in $CELLS; do
    r=${cell%%:*}; l=${cell##*:}
    [ "$r" = fp4-nvf4 ] && continue
    extra=""; [ "$r" = bf16-ampere ] && extra="--instances /workspace/bench-instances/v1"
    $PY -m gpu.commit pin $r --leaf $l $extra --procs $NT 2>&1 | grep -v -i warn | tail -12
  done
fi

[ "${BENCH:-1}" = 1 ] || { echo "== done ($(date -u +%H:%M:%S))"; exit 0; }
for cell in $CELLS; do
  c=${cell%%:*}; l=${cell##*:}
  echo "== 3. $c --commit $l ($(date -u +%H:%M:%S))"
  O=$H/$c-$l; S=$O/stmt; rm -rf $O; mkdir -p $O
  case $c in
    bf16-ampere) $PY -m gpu.v2.export circuits --model ampere_bf16_m16n8k16 --out $S > /dev/null
                 ARGS="--instances /workspace/bench-instances/v1";;
    bf16-hopper) $PY -m gpu.v2.export circuits --model hopper_bf16_m16n8k16 --out $S > /dev/null; ARGS="--relation $c";;
    fp8-hopper)  $PY -m gpu.v2.export circuits --model hopper_e4m3_wgmma_k32 --out $S > /dev/null; ARGS="--relation $c";;
    fp8-ada)     $PY -m gpu.v2.export circuits --model ada_e4m3_m16n8k32 --out $S > /dev/null; ARGS="--relation $c";;
    fp4-nvf4)    $PY -m gpu.nvf4.circuit export --out $S > /dev/null; ARGS="--relation $c";;
  esac
  RESEARCH_RUN_DIR=$O/run $PY bench_result.py $S $ARGS --commit $l --vus 4096 --reps 1 --warmup 1 --verifier $VB --threads $NT \
      > $O/bench.log 2>&1
  echo "bench rc=$? ($(date -u +%H:%M:%S))"
  grep -E '^verify rep|Error|Traceback|error' $O/bench.log | tail -6
  $PY - $O/run/result.json <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
r = d["validation"]["evidence"]["reps"][0]
fp = d["workload_fingerprint"]
print("t.total %.4f status %s soundness %.2f proof %s" % (r["t_total"], d["validation"]["status"], fp["security"]["achieved_log2"], r["proof_sha256"][:16]))
print("buckets", {k: round(v, 4) for k, v in r["buckets"].items()}, "contract_problems", d.get("contract_problems"))
print("commitment", json.dumps(fp.get("operand_commitment")))
print("detail", d["validation"]["detail"])
EOF
  $VB verify --dir $O/run/statement --proof $O/run/proofs/rep0.bin --vus 4096 --threads $NT --allow-any-circuit --require-commitment \
      --allow-unpinned-commitment --json $O/scaffold.json | cut -c1-200
  $PY -c "import json; d=json.load(open('$O/scaffold.json')); print('scaffold accepted', d['accepted'], 'committed', d['operands_committed'], 'verify_s', d['verify_seconds'], d['commitment'])"
done
echo "== done ($(date -u +%H:%M:%S))"
