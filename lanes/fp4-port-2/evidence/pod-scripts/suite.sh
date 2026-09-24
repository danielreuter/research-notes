#!/usr/bin/env bash
# lane fp4-port-2 (from fp4-decode-3's suite.sh, adapted to main's CLI: --relation fp4-nvf4 --auth included-hash):
# one pod pass at the tip in /workspace/src, each stage into $RD/<stage>/.
#   build     cargo build --release + cargo test --release (backends/ligero-verify) -> $VER
#   sysid     protocol.system_id of hashchain.compose(FP4_HASHED) and of the bare unit (torch, the prover's own digest)
#   t1        pytest the touched fp4 / leaf / hashchain / steps-pin / witness_device files (fail-fast stage)
#   gate_hashed / gate_bare   gate-vu 2048 VUs + negatives
#   ab_fs     byte-identity A/B, fiat-shamir non-ZK, LIGERO_STMT_TRIM=0: bare fp4-nvf4 main@24f252b1 vs tip, hashed
#             lane/fp4-decode-3@6ffa0351 vs tip (trees in /workspace/ab-main, /workspace/ab-fp4d3)
#   bench     rounds of bench-vu, 4096 VUs, l=16384, --zk --mode interactive, local coins, 3 reps, dump rep 1, --pipeline $2,
#             arm order alternated per round (H B, B H, H B); pinned ligero-verify batch over every dump
#   t2        pytest the other files that import the touched modules (OMP_NUM_THREADS=2)
#   $1 = stages (comma list), $2 = depth (default 4), $3 = rounds (default 3)
set -uo pipefail
STAGES=${1:-build,sysid,t1,gate_hashed,gate_bare,ab_fs,bench}; D=${2:-4}; ROUNDS=${3:-3}
source /workspace/env.sh
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 OMP_NUM_THREADS=${OMP_NUM_THREADS:-10}
RD=${RD:-/workspace/fp4-port-2/run-$(date -u +%Y%m%dT%H%M%SZ)}; mkdir -p "$RD"
exec > >(tee -a "$RD/stdout.log") 2>&1
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total --format=csv,noheader
nproc; cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us 2>/dev/null; cat /proc/loadavg
echo "RD=$RD tree: $(cat /workspace/src/.synced-rev 2>/dev/null || true)"
VER=/workspace/bin/ligero-verify-fp4port
fail=0
has() { [[ ",$STAGES," == *",$1,"* ]]; }
t() { date -u +%H:%M:%S; }

if has build; then
  mkdir -p "$RD/build"; echo "=== [$(t)] build"
  ( cd backends/ligero-verify && cargo build --release 2>&1 | tail -2 && cargo test --release 2>&1 > "$RD/build/cargo_test.log"; echo "CARGO_TEST_RC=$?" )
  grep -E "^test result|FAILED|panicked" "$RD/build/cargo_test.log" | head -20
  grep -q "FAILED\|error\[" "$RD/build/cargo_test.log" && fail=1
  cp "$CARGO_TARGET_DIR/release/ligero-verify" "$VER"
fi
[ -x "$VER" ] && sha256sum "$VER"

if has sysid; then
  mkdir -p "$RD/sysid"; echo "=== [$(t)] sysid"
  python - > "$RD/sysid/sysid.txt" 2>&1 <<'PY'
from backends.direct.ligero import hashchain, protocol
from backends.direct.ligero.fp4.hashed import FP4_HASHED, system_id_np
from backends.direct.ligero.fp4.relation import NVFP4, compile_fp4_unit
hr = hashchain.compose(FP4_HASHED)
print("hashed m", hr.sys.m, "linked", len(hr.sys.chain["c"]), "sys_id", protocol.system_id(hr.sys).hex(), "np", system_id_np(hr.sys).hex())
print("census", hr.census)
b = compile_fp4_unit(NVFP4, chain=True)
print("bare m", b.m, "sys_id", protocol.system_id(b).hex())
PY
  cat "$RD/sysid/sysid.txt"
  "$VER" system-digest --system backends/ligero-verify/fixtures/fp4-nvf4-hash/system.bin | cut -c1-400
  grep -q "sys_id 8c6d260c675cad40ae7263db08974f1842d04997f344cb4f9e52821e70bb25f5" "$RD/sysid/sysid.txt" || { echo "SYSID MISMATCH"; fail=1; }
  grep -q "bare m 1583 sys_id a825ba0b826a15366bfb8cdd720a5e9978603cbe589491abcbba7346ad35bf3c" "$RD/sysid/sysid.txt" || { echo "BARE SYSID MISMATCH"; fail=1; }
fi

pyt() {  # $1 stage, $2.. files
  local S=$1; shift; mkdir -p "$RD/$S"; echo "=== [$(t)] $S: $*"
  python -m pytest -v -rfEs -p no:cacheprovider --durations 10 "$@" > "$RD/$S/pytest.log" 2>&1
  local rc=$?; grep -E "FAILED|ERROR|SKIPPED" "$RD/$S/pytest.log" | cut -c1-220 | head -30; tail -1 "$RD/$S/pytest.log"; echo "PYTEST_RC[$S]=$rc"
  [ "$rc" -eq 0 ] || fail=1
}
L=backends/direct/ligero
has t1 && pyt t1 $L/fp4/hashed_test.py $L/fp4/hashed_pipeline_test.py $L/witness_device_test.py $L/steps_pin_test.py \
  $L/hashchain_test.py $L/leaf_test.py $L/fp4/relation_test.py $L/fp4/hints_device_test.py

gate() {  # $1 stage, $2.. relation args
  local S=$1; shift; mkdir -p "$RD/$S"; echo "=== [$(t)] $S ($*)"
  python -m backends.direct.ligero.run "$@" gate-vu --vus 2048 --batch 16384 --device cuda --target -128 \
    --instances-cache /workspace/instances-cache --instance-procs 10 --out "$RD/$S/gate.json" > "$RD/$S/gate.log" 2>&1
  local rc=$?; tail -4 "$RD/$S/gate.log"; echo "GATE_RC[$S]=$rc"; [ "$rc" -eq 0 ] || fail=1
}
has gate_hashed && gate gate_hashed --relation fp4-nvf4+poseidon2 --auth included-hash
has gate_bare && gate gate_bare --relation fp4-nvf4

abrun() {  # $1 tree, $2 out dir, $3.. relation args
  local T=$1 O=$2; shift 2; mkdir -p "$O"
  ( cd "$T" && PYTHONPATH="$T/packages/verity/src:$T/backends/numerical/python:$T/tools/research/src:$T" LIGERO_STMT_TRIM=0 \
    python -m backends.direct.ligero.run "$@" bench-vu --mode fiat-shamir --batch 16384 --total-vus 1024 --reps 1 --target -128 \
      --device cuda --instances-cache /workspace/instances-cache --instance-procs 10 --auth-cache "$O/auth-cache" \
      --out "$O/result.json" --dump-dir "$O/proofs" --dump-reps 1 > "$O/stdout.log" 2>&1 )
  echo "rc=$? $(cd "$O/proofs" 2>/dev/null && find . -type f \( -name '*.proof' -o -name '*.stmt' -o -name 'system.bin' \) | sort | xargs sha256sum | sha256sum | cut -c1-16) $(find "$O/proofs" -type f | wc -l) files"
}
if has ab_fs; then
  echo "=== [$(t)] ab_fs"
  echo -n "bare main  : "; abrun /workspace/ab-main "$RD/ab_fs/bare_main" --relation fp4-nvf4
  echo -n "bare tip   : "; abrun /workspace/src "$RD/ab_fs/bare_tip" --relation fp4-nvf4
  echo -n "hash fp4d3 : "; abrun /workspace/ab-fp4d3 "$RD/ab_fs/hash_fp4d3" --relation fp4-nvf4+poseidon2
  echo -n "hash tip   : "; abrun /workspace/src "$RD/ab_fs/hash_tip" --relation fp4-nvf4+poseidon2 --auth included-hash
  for p in bare hash; do
    a=$(ls -d "$RD"/ab_fs/${p}_* | head -1); b=$(ls -d "$RD"/ab_fs/${p}_* | tail -1)
    if diff -r -q -x 'manifest.json' -x '*.json' "$a/proofs" "$b/proofs" > "$RD/ab_fs/diff_$p.txt" 2>&1; then echo "AB[$p] IDENTICAL"; else echo "AB[$p] DIFFER"; head -5 "$RD/ab_fs/diff_$p.txt"; fi
  done
fi

bench() {  # $1 stage, $2.. relation args
  local S=$1; shift; local O="$RD/$S"; mkdir -p "$O"; echo "=== [$(t)] $S ($*, --pipeline $D) gpu-apps=[$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | tr '\n' ' ')]"
  python -m backends.direct.ligero.run "$@" bench-vu --zk --mode interactive --batch 16384 --total-vus 4096 --reps 3 \
    --target -128 --device cuda --instances-cache /workspace/instances-cache --instance-procs 10 --auth-cache "/workspace/auth-cache-$S" \
    --pipeline "$D" --run-id "fp4-port-2-$S" --out "$O/result.json" --dump-dir "$O/proofs" --dump-reps 1 > "$O/stdout.log" 2>&1
  local rc=$?
  grep -E "^rep [0-9]|^dumps|^warm-up|Traceback|Error|out of memory" "$O/stdout.log" | cut -c1-300; echo "BENCH_RC[$S]=$rc"
  [ "$rc" -eq 0 ] || { fail=1; return; }
  python - "$O/result.json" <<'PY'
import json, sys
m = {x["name"]: x["value"] for x in json.load(open(sys.argv[1]))["measurements"]}
print("t.total %.4f s  split.hints %.4f s  mem.peak_device %.2f GB" % (m["t.total"], m.get("split.hints_seconds", 0), m.get("mem.peak_device_bytes", 0) / 1e9))
PY
  "$VER" batch --dir "$O/proofs/rep1" --system "$O/proofs/system.bin" --target-bits 128 --threads 8 > "$O/rust_batch_pinned.json" 2>&1
  local vrc=$?
  grep -oE '"pinned_relation":"[^"]*"|"accepted":[0-9]+,"rejected":[0-9]+' "$O/rust_batch_pinned.json" | tr '\n' ' '; echo "RUST_PINNED_RC[$S]=$vrc"; [ "$vrc" -eq 0 ] || fail=1
  sha256sum "$O/proofs/system.bin"
}
if has bench; then
  for r in $(seq 1 "$ROUNDS"); do
    if [ $((r % 2)) -eq 1 ]; then
      bench "bench_hashed_r$r" --relation fp4-nvf4+poseidon2 --auth included-hash; bench "bench_bare_r$r" --relation fp4-nvf4
    else
      bench "bench_bare_r$r" --relation fp4-nvf4; bench "bench_hashed_r$r" --relation fp4-nvf4+poseidon2 --auth included-hash
    fi
  done
fi
OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
has t2 && OMP_NUM_THREADS=2 pyt t2 $L/relations_test.py $L/leaf/ajtai_test.py $L/leaf/blake3_test.py $L/pipeline_race_test.py \
  $L/reverify_test.py $L/commit_gpu_test.py $L/hints_fused_test.py
echo "=== [$(t)] done fail=$fail"
exit $fail
