#!/bin/bash
# lane hostphase merge validation on vy-hp-val (RTX 4090), cwd = the merged tree (lane/hostphase = main 24bd337 + hostphase):
#  1. pytest backends/direct/ligero (witness_device_test, chain_test, fp4/relation_test included), then v2
#  2. gates rc=0: bf16-ampere, bf16-hopper (--impl device, --impl legacy), fp8-hopper, fp8-ada, fp4-nvf4
#  3. bit-exactness --impl device vs --impl legacy on the merged tree (seeded harness): bf16-hopper int-ZK, fp8-hopper int-ZK
#  4. small bench-vu trees (bf16-hopper int-ZK, fp8-hopper int-ZK) -> Python verify-batch + Rust ligero-verify batch (python_agree)
#  5. fp4-nvf4 bench-vu 170 VUs x 1 rep (proves + self-verifies; Rust lacks system/v2 -> expected refusal, recorded)
set -u
export PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:$PATH
export PYTHONPATH=packages/verity/src:backends/numerical/python:.
PY=/workspace/venv312/bin/python
LV=/workspace/bin/ligero-verify
RD=$RESEARCH_RUN_DIR
H=$RD/inputs/bitexact.py
FAILS=0
mark () { echo "### $1: $2"; [ "$2" = "0" ] || FAILS=$((FAILS+1)); }
T0=$(date +%s)
lap () { echo "--- t+$(( $(date +%s) - T0 ))s"; }

echo "=== tree"; cat .research-source.json 2>/dev/null; nvidia-smi --query-gpu=name,driver_version --format=csv,noheader; grep -m1 'model name' /proc/cpuinfo; nproc

echo "=== 1. pytest backends/direct/ligero (minus v2)"
$PY -m pytest backends/direct/ligero -q -p no:cacheprovider --ignore backends/direct/ligero/v2 2>&1 | tail -12
mark pytest ${PIPESTATUS[0]}; lap
echo "=== 1b. pytest backends/direct/ligero/v2"
$PY -m pytest backends/direct/ligero/v2 -q -p no:cacheprovider 2>&1 | tail -3
mark pytest-v2 ${PIPESTATUS[0]}; lap

gate () {
  local name=$1; shift
  echo "=== 2. gate $name: $*"
  $PY -m backends.direct.ligero.run "$@" 2>&1 | grep -v Warning | tail -5
  mark "gate-$name" ${PIPESTATUS[0]}; lap
}
gate bf16-ampere gate-vu --root /workspace/bench-instances/v1 --vus 64 --device cuda
gate bf16-hopper-device --relation bf16-hopper gate-vu --vus 64 --device cuda --impl device --instances-cache /workspace/instances-cache
gate bf16-hopper-legacy --relation bf16-hopper gate-vu --vus 64 --device cuda --impl legacy --instances-cache /workspace/instances-cache
gate fp8-hopper --relation fp8-hopper gate-vu --vus 64 --device cuda --instances-cache /workspace/instances-cache
gate fp8-ada --relation fp8-ada gate-vu --vus 64 --device cuda --instances-cache /workspace/instances-cache
gate fp4-nvf4 --relation fp4-nvf4 gate-vu --vus 64 --batch 1024 --device cuda --out "$RD/gate_fp4.json"

echo "=== 3. bit-exactness on the merged tree: --impl device vs --impl legacy (seeded coins + mask keys)"
OUT=$RD/bitexact; mkdir -p "$OUT"; total_n=0; total_same=0
pair () {  # tag rel vus
  local tag=$1 rel=$2 vus=$3
  for impl in device legacy; do
    $PY "$H" --tree "$(pwd)" --rel "$rel" --zk --mode interactive --vus "$vus" --subs 3 --seed 20260922 --total 512 --impl $impl --out "$OUT/$tag/$impl" 2>&1 | grep -v Warning | tail -3
  done
  local n=0 same=0
  for f in "$OUT/$tag/legacy"/*.stmt "$OUT/$tag/legacy"/*.proof "$OUT/$tag/legacy"/*.coins "$OUT/$tag/legacy"/system.bin; do
    [ -e "$f" ] || continue; n=$((n+1)); b=$(basename "$f")
    a=$(sha256sum "$f" | cut -d' ' -f1); c=$(sha256sum "$OUT/$tag/device/$b" 2>/dev/null | cut -d' ' -f1)
    if [ "$a" = "$c" ]; then same=$((same+1)); else echo "  DIFF $b legacy=$a device=$c"; fi
  done
  echo "$tag: $same / $n files identical (device vs legacy)"; echo "$tag $rel $same $n" >> "$OUT/summary.txt"
  total_n=$((total_n+n)); total_same=$((total_same+same))
  [ "$same" = "$n" ] && [ "$n" -gt 0 ]; mark "bitexact-$tag" $?
  echo "-- Rust on the device dumps: $($LV system-digest --system "$OUT/$tag/device/system.bin" 2>&1 | tail -1)"
  $LV batch --system "$OUT/$tag/device/system.bin" --dir "$OUT/$tag/device" --jobs 3 --threads 1 --target-bits 128 --json "$OUT/$tag/rust.json" 2>&1 | tail -1
  lap
}
pair bf16h-int-zk bf16-hopper 170
pair fp8h-int-zk fp8-hopper 341
echo "BITEXACT TOTAL: $total_same / $total_n files identical"; echo "TOTAL $total_same $total_n" >> "$OUT/summary.txt"
find "$OUT" -name '*.proof' -delete

bench () {  # tag relation extra...
  local tag=$1 rel=$2; shift 2
  echo "=== 4. bench-vu $tag ($rel $*)"
  $PY -m backends.direct.ligero.run --relation "$rel" bench-vu "$@" --target -128 --device cuda --reps 1 \
      --run-id "$RESEARCH_RUN_ID-$tag" --out "$RD/result_$tag.json" --dump-dir "$RD/proofs_$tag" --dump-reps 1 2>&1 | grep -v Warning | tail -6
  mark "bench-$tag" ${PIPESTATUS[0]}; lap
  echo "-- python verify-batch ($tag)"
  $PY -m backends.direct.ligero.serialize verify-batch --dir "$RD/proofs_$tag/rep1" --target-bits 128 --json "$RD/pyverify_$tag.json" 2>&1 | tail -1
  mark "pyverify-$tag" ${PIPESTATUS[0]}
  echo "-- rust batch ($tag): $($LV system-digest --system "$RD/proofs_$tag/system.bin" 2>&1 | tail -1)"
  $LV batch --system "$RD/proofs_$tag/system.bin" --dir "$RD/proofs_$tag/rep1" --jobs 8 --threads 1 --target-bits 128 --json "$RD/rust_$tag.json" 2>&1 | tail -1
  echo "rust rc=$? (fp4: expected non-zero, ligero-verify lacks system/v2)"
  lap
}
bench bf16h bf16-hopper --zk --mode interactive --batch 16384 --total-vus 340 --instance-procs 8 --instances-cache /workspace/instances-cache
bench fp8h fp8-hopper --zk --mode interactive --batch 16384 --total-vus 682 --instance-procs 8 --instances-cache /workspace/instances-cache
bench fp4 fp4-nvf4 --zk --mode interactive --batch 4096 --total-vus 170
$PY - "$RD" <<'PYEOF'
import json, sys, glob, os
rd = sys.argv[1]
for f in sorted(glob.glob(f"{rd}/result_*.json")):
    r = json.load(open(f)); ms = {m["name"]: m["value"] for m in r["measurements"]}
    d = r.get("validation", {}).get("evidence", {}).get("dumps", {})
    print(os.path.basename(f), "t.total", round(ms.get("t.total", 0), 4), "impl", r["workload_fingerprint"]["software"]["backend"].get("impl"),
          "cold python verify", d.get("accepted"), "/", d.get("total"), "achieved", round(r["workload_fingerprint"]["security"]["achieved_log2"], 2))
for f in sorted(glob.glob(f"{rd}/rust_*.json")):
    try:
        j = json.load(open(f)); print(os.path.basename(f), "accepted", j["accepted"], "/", j["n"], "batch", j["batch_accepted"], "python_agree", j["python_agree"], "disagree", j["python_disagree"], "pinned", j["system_pinned"])
    except Exception as e: print(os.path.basename(f), "unreadable:", e)
PYEOF
find "$RD" -path '*/proofs_*' -name '*.proof' -delete     # keep the run-files small (stmt/coins/manifest/json stay)
echo "### FAILS=$FAILS"; lap
echo VALIDATE_DONE
