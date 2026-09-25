#!/usr/bin/env bash
# agkr-bound hash spike (hash-proving survey §4.3, coordinator 0752Z): the CPU cost of proving SHA-256 compressions
#  (b) in-field: tools/sha256_flat.py (Longfellow flat layout, BabyBear) in A-GKR's Rust CPU prover (verity-gkr --features babybear)
#  (a) Flock (succinctlabs/flock b684b12) hash_throughput on the same pod CPU, SHA-256 and BLAKE3
#  plus the same-pod A-GKR baseline: the v1 transition unit (fixtures/babybear) at B = 4096 tiled
# research run --on vy-agkr-bound2 --project verity --source . --cwd source/backends/gkr --send 12_hash_spike.sh \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/12_hash_spike.sh"'
# usage: [BS="64 4096"] [FLOCK_LOG2S="6 12 16"] [FLOCK=1] bash 12_hash_spike.sh
set -uo pipefail
HERE=$(pwd)
ROOT=$(cd ../.. && pwd)
export PATH="/workspace/venv312/bin:$HOME/.cargo/bin:$PATH"
PY=/workspace/venv312/bin/python
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT CARGO_BUILD_JOBS=$NT RAYON_NUM_THREADS=$NT
export VERITY_GKR_THREADS=$NT
RD=${RESEARCH_RUN_DIR:?}
echo "tree $ROOT; commit ${RESEARCH_SOURCE_COMMIT:-?}; cpu threads $NT; run dir $RD; $(lscpu | grep 'Model name' | sed 's/  */ /g')"
H=/workspace/agkr-bound/hash
mkdir -p $H

summ() {
  $PY - "$1" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
m = {x["name"]: x["value"] for x in d["measurements"]}
keys = ["units", "columns_per_unit", "t.total", "t.arithmetic", "t.encoding_commitment", "t.witness", "verifier.seconds",
        "proof_bytes", "ligero_rows", "rounds.sequential_depth", "threads", "peak_rss_bytes"]
print("  " + ", ".join(f"{k} {m[k]:.4g}" if isinstance(m.get(k), float) else f"{k} {m.get(k)}" for k in keys))
print("  status", d["validation"]["status"], "|", d["validation"]["detail"][:200])
EOF
}

echo "== 0. verity-gkr --features babybear ($(date -u +%H:%M:%S))"
export CARGO_TARGET_DIR=/workspace/cargo-target-gkr
cargo build --release --features babybear 2>&1 | grep -E "^(warning: unused|error)|Finished" | head -10
VG=$CARGO_TARGET_DIR/release/verity-gkr
sha256sum $VG

echo "== 1. baseline: v1 transition unit x 4096 ($(date -u +%H:%M:%S))"
$VG run --circuit fixtures/babybear/circuit.txt --witness fixtures/babybear/honest8.bin --units 4096 --out $H/base-4096.json > $H/base-4096.log 2>&1
echo "rc=$?"; grep -E "^(ncols|nwires)" fixtures/babybear/circuit.txt | tr '\n' ' '; echo; summ $H/base-4096.json

for B in ${BS:-64 4096}; do
  O=$H/flat-$B
  echo "== 2. in-field flat SHA-256, B = $B ($(date -u +%H:%M:%S))"
  $PY tools/sha256_flat.py --out $O --blocks $B | cut -c1-300
  $VG check-witness --circuit $O/circuit.txt --witness $O/witness.bin > $O/check.log 2>&1; echo "check-witness honest rc=$? $(tail -1 $O/check.log | cut -c1-160)"
  $VG check-witness --circuit $O/circuit.txt --witness $O/neg.bin > $O/check_neg.log 2>&1; echo "check-witness neg rc=$? (want nonzero) $(tail -1 $O/check_neg.log | cut -c1-160)"
  $VG run --circuit $O/circuit.txt --witness $O/witness.bin --units $B --out $O/result.json > $O/run.log 2>&1
  echo "run rc=$? ($(date -u +%H:%M:%S))"; tail -3 $O/run.log | cut -c1-200
  [ -f $O/result.json ] && summ $O/result.json
  rm -f $O/witness.bin
done

[ "${FLOCK:-1}" = 1 ] || { echo "== done ($(date -u +%H:%M:%S))"; exit 0; }
echo "== 3. Flock b684b12 hash_throughput, $NT threads and 1 ($(date -u +%H:%M:%S))"
F=/workspace/flock
[ -d $F ] || git clone -q https://github.com/succinctlabs/flock $F
( cd $F && git checkout -q b684b12 && git log --oneline -1 )
export CARGO_TARGET_DIR=/workspace/cargo-target-flock
for T in $NT 1; do
  ( cd $F && RUSTFLAGS="-C target-cpu=native" RAYON_NUM_THREADS=$T HASH_BENCH_LOG2S="${FLOCK_LOG2S:-6 12 16}" HASH_BENCH_RUNS=3 \
      cargo bench --bench hash_throughput ) > $H/flock-$T.log 2>&1
  echo "flock threads $T rc=$? ($(date -u +%H:%M:%S))"
  grep -E "^RESULT|error\[|panicked" $H/flock-$T.log | head -20
done
echo "== done ($(date -u +%H:%M:%S))"
