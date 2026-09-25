#!/usr/bin/env bash
# agkr-bound: Flock b684b12 hash_throughput on an AVX-512 + VPCLMULQDQ CPU (its fast x86 path), the counterpart of
# 12_hash_spike.sh step 3 on the A100 pod's Zen 2 (portable path).  CPU pod vy-agkr-bound-cpu.
# research run --on vy-agkr-bound-cpu --project verity --source . --send 19_flock_avx512.sh -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/19_flock_avx512.sh"'
set -uo pipefail
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
echo "cpu threads $NT; $(lscpu | grep 'Model name' | sed 's/  */ /g'); flags: $(grep -o -w -E 'avx512f|avx512vl|vpclmulqdq|gfni' /proc/cpuinfo | sort -u | tr '\n' ' ')"
export PATH="$HOME/.cargo/bin:$PATH"
command -v cargo > /dev/null || { curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal > /dev/null 2>&1; }
cargo --version
W=/workspace/agkr-bound; mkdir -p $W
F=/workspace/flock
[ -d $F ] || git clone -q https://github.com/succinctlabs/flock $F
( cd $F && git checkout -q b684b12 && git log --oneline -1 )
export CARGO_TARGET_DIR=/workspace/cargo-target-flock CARGO_BUILD_JOBS=$NT
for T in $NT 1; do
  ( cd $F && RUSTFLAGS="-C target-cpu=native" RAYON_NUM_THREADS=$T HASH_BENCH_LOG2S="${FLOCK_LOG2S:-8 12 16 18}" HASH_BENCH_RUNS=3 \
      cargo bench --bench hash_throughput ) > $W/flock-avx512-$T.log 2>&1
  echo "flock threads $T rc=$? ($(date -u +%H:%M:%S))"
  grep -E "^RESULT|error\[|panicked|portable|avx|fallback" $W/flock-avx512-$T.log | head -24
done
cp $W/flock-avx512-*.log "$RESEARCH_RUN_DIR/" 2>/dev/null || true
echo "== done ($(date -u +%H:%M:%S))"
