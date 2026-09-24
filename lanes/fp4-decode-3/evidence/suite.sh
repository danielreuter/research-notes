#!/usr/bin/env bash
# lane fp4-decode-3 (from fp4-decode-2's suite.sh): one pod pass at the tip, stages in order, each into $RD/<stage>/:
#   pipe_test  pytest -v fp4/hashed_pipeline_test.py (pipelined hashed == sequential bytes, ZK accepted)   [fail-fast]
#   gate_hashed / gate_bare   gate-vu 2048 VUs + negatives
#   bench      for each depth D in $2: bench-vu fp4-nvf4+poseidon2 then fp4-nvf4, 4096 VUs, l=16384, --zk --mode interactive,
#              local coins, 3 reps, dump rep 1, --pipeline D, then the pinned ligero-verify batch over every dumped sub-batch
#              (no --allow-any-system) + system-digest; a bench that fails (e.g. OOM at a deep pipeline) does not stop the next
#   pytest     pytest -v backends/direct/ligero (names survive a timeout)
#   $1 = stages (comma list; default pipe_test,gate_hashed,gate_bare,bench), $2 = depths (comma list; default 4,8,2), $3 = pytest wall s
set -uo pipefail
STAGES=${1:-pipe_test,gate_hashed,gate_bare,bench}; DEPTHS=${2:-4,8,2}; PYT=${3:-2400}
export PATH="/workspace/venv312/bin:$HOME/.cargo/bin:$PATH"
export PYTHONPATH="$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD"
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 OMP_NUM_THREADS=12
export CARGO_TARGET_DIR=/workspace/cargo-target
RD=${RESEARCH_RUN_DIR:-/tmp/suite}
nvidia-smi --query-gpu=name,uuid,driver_version,clocks.max.sm,power.limit,memory.total --format=csv,noheader
nproc; cat /proc/loadavg
echo "tree: $(git rev-parse HEAD 2>/dev/null || basename "$PWD")"
VER=/workspace/bin/ligero-verify
[ -x "$VER" ] || { mkdir -p /workspace/bin; ( cd backends/ligero-verify && cargo build --release 2>&1 | tail -1 ) && cp "$CARGO_TARGET_DIR/release/ligero-verify" "$VER"; }
sha256sum "$VER"
fail=0
has() { [[ ",$STAGES," == *",$1,"* ]]; }
t() { date -u +%H:%M:%S; }

if has wd_test; then  # the fused witness: native build == compute_89 PTX route (incl. the hashed kernel), == torch program
  mkdir -p "$RD/wd_test"; echo "=== [$(t)] wd_test"
  LIGERO_TEST_NATIVE_CC12=1 python -m pytest -v -p no:cacheprovider backends/direct/ligero/witness_device_test.py > "$RD/wd_test/pytest.log" 2>&1
  rc=$?; grep -E "PASSED|FAILED|SKIPPED|ERROR" "$RD/wd_test/pytest.log" | cut -c1-160; tail -1 "$RD/wd_test/pytest.log"; echo "WD_TEST_RC=$rc"
  [ "$rc" -eq 0 ] || fail=1
fi

if has cold_pipe; then  # pipe_test from EMPTY CuPy + driver JIT caches: what a fresh pod pays before its first proof
  mkdir -p "$RD/cold_pipe"; echo "=== [$(t)] cold_pipe"; s=$(date +%s)
  CUPY_CACHE_DIR="$RD/cold_pipe/kcache" CUDA_CACHE_PATH="$RD/cold_pipe/nvcache" \
    python -m pytest -v -p no:cacheprovider --durations 5 backends/direct/ligero/fp4/hashed_pipeline_test.py > "$RD/cold_pipe/pytest.log" 2>&1
  rc=$?; tail -8 "$RD/cold_pipe/pytest.log"; echo "COLD_PIPE_RC=$rc wall=$(( $(date +%s) - s ))s"; ls "$RD/cold_pipe/kcache" | head -30
  [ "$rc" -eq 0 ] || fail=1
fi

if has pipe_test; then
  mkdir -p "$RD/pipe_test"; echo "=== [$(t)] pipe_test"
  python -m pytest -v -p no:cacheprovider backends/direct/ligero/fp4/hashed_pipeline_test.py > "$RD/pipe_test/pytest.log" 2>&1
  rc=$?; tail -6 "$RD/pipe_test/pytest.log"; echo "PIPE_TEST_RC=$rc"
  [ "$rc" -eq 0 ] || { echo "=== pipe_test failed: stopping"; exit 1; }
fi

gate() {  # $1 = relation, $2 = stage
  mkdir -p "$RD/$2"; echo "=== [$(t)] $2 ($1)"
  python -m backends.direct.ligero.run --relation "$1" gate-vu --vus 2048 --batch 16384 --device cuda --target -128 \
    --instances-cache /workspace/instances-cache --instance-procs 16 --out "$RD/$2/gate.json" > "$RD/$2/gate.log" 2>&1
  local rc=$?; tail -4 "$RD/$2/gate.log"; echo "GATE_RC[$1]=$rc"; [ "$rc" -eq 0 ] || fail=1
}
has gate_hashed && gate fp4-nvf4+poseidon2 gate_hashed
has gate_bare && gate fp4-nvf4 gate_bare

bench() {  # $1 = relation, $2 = stage, $3 = depth
  local O="$RD/$2"; mkdir -p "$O"; echo "=== [$(t)] $2 ($1, --pipeline $3)"
  python -m backends.direct.ligero.run --relation "$1" bench-vu --zk --mode interactive --batch 16384 --total-vus 4096 --reps 3 \
    --target -128 --device cuda --instances-cache /workspace/instances-cache --instance-procs 16 --auth-cache "/workspace/auth-cache-$1" \
    --pipeline "$3" --run-id "${RESEARCH_RUN_ID:-local}-$2" --out "$O/result.json" --dump-dir "$O/proofs" --dump-reps 1 \
    > "$O/stdout.log" 2>&1
  local rc=$?
  grep -E "^rep [0-9]|^dumps|^warm-up|Traceback|Error|out of memory" "$O/stdout.log" | cut -c1-400; echo "BENCH_RC[$2]=$rc"
  [ "$rc" -eq 0 ] || { fail=1; return; }
  python - "$O/result.json" <<'PY'
import json, sys
m = {x["name"]: x["value"] for x in json.load(open(sys.argv[1]))["measurements"]}
print("t.total %.4f s  split.hints %.4f s  mem.peak_device %.2f GB  rows/unit %d" % (
    m["t.total"], m.get("split.hints_seconds", 0), m.get("mem.peak_device_bytes", 0) / 1e9, m.get("rows_per_unit", 0)))
PY
  "$VER" batch --dir "$O/proofs/rep1" --system "$O/proofs/system.bin" --target-bits 128 --threads 8 > "$O/rust_batch_pinned.json" 2>&1
  local vrc=$?
  grep -E "^[0-9]+ proofs:" "$O/rust_batch_pinned.json" | cut -c1-400; echo "RUST_PINNED_RC[$2]=$vrc"; [ "$vrc" -eq 0 ] || fail=1
  "$VER" system-digest --system "$O/proofs/system.bin" 2>&1 | cut -c1-200
}
if has bench; then
  for D in ${DEPTHS//,/ }; do
    bench fp4-nvf4+poseidon2 "bench_hashed_p$D" "$D"
    bench fp4-nvf4 "bench_bare_p$D" "$D"
  done
fi
if has ab; then  # the fused witness build A/B at the first depth: native sm_<cc> (CuPy) vs compute_89 PTX + JIT, interleaved x2
  D=${DEPTHS%%,*}
  for i in 1 2; do
    for mode in native 89; do
      LIGERO_WITNESS_PTX_ARCH=$mode bench fp4-nvf4+poseidon2 "ab_hashed_${mode}_$i" "$D"
      LIGERO_WITNESS_PTX_ARCH=$mode bench fp4-nvf4 "ab_bare_${mode}_$i" "$D"
    done
  done
fi

if has pytest; then
  mkdir -p "$RD/pytest"; echo "=== [$(t)] pytest backends/direct/ligero (-v, wall limit ${PYT}s)"
  timeout "$PYT" python -m pytest -v -rfE -p no:cacheprovider --durations 15 backends/direct/ligero > "$RD/pytest/pytest.log" 2>&1
  prc=$?; grep -E "FAILED|ERROR" "$RD/pytest/pytest.log" | head -20; tail -3 "$RD/pytest/pytest.log"; echo "PYTEST_RC=$prc"
  [ "$prc" -eq 0 ] || fail=1
fi
echo "=== [$(t)] done fail=$fail"
exit $fail
