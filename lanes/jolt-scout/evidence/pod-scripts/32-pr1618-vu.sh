#!/usr/bin/env bash
# jolt-scout: prove the vu-k1536 guest on PR #1618's modular prover, --backend cuda vs optimized (CPU), same synthetic
# inputs as 12-vu.sh (vu-input writes them). $1 = tgz of vu-k1536/ + vu-input/, $2 = 32-pr1618-vu-patch.py.
# Env: RUNS="B:mode:scale ..." (scale = log2 padded trace), BACKENDS (default "cuda optimized").
set -uo pipefail
TGZ=$(readlink -f "$1"); PATCH=$(readlink -f "$2")
W=/workspace/jolt-scout; source $HOME/.cargo/env
export PATH=$W/pr1618-bin/bin:/usr/local/cuda/bin:$PATH JOLT_CUDA_ARCH=sm_89 JOLT_NVCC=$W/nvcc-wrap
L=$W/32-pr1618-vu.log; exec > >(tee -a $L) 2>&1
# the lock also covers the builds: they would perturb 31's CPU timings, and they rewrite the binary 31 runs
exec 9>$W/timing.lock; flock 9; echo "LOCK $(date -u +%H:%M:%SZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
S=$W/scout-src; rm -rf $S; mkdir -p $S; tar xzf $TGZ -C $S
(cd $S/vu-input && CARGO_TARGET_DIR=$W/target-vu-input cargo build --release 2>&1 | tail -1)
G=$W/target-vu-input/release/vu-input
cd $W/jolt-pr1618
rm -rf examples/vu-k1536; mkdir -p examples/vu-k1536; cp -r $S/vu-k1536/guest examples/vu-k1536/
sed -i 's/^pub(crate) fn compress_direct(/pub fn compress_direct(/' jolt-inlines/blake3/src/sdk.rs
grep -q '"examples/vu-k1536/guest"' Cargo.toml || sed -i 's|^  "examples/sha2-chain",|  "examples/vu-k1536/guest",\n  "examples/sha2-chain",|' Cargo.toml
python3 $PATCH crates/jolt-prover/src/profile.rs
export CARGO_TARGET_DIR=$W/target-pr1618
t0=$(date +%s); cargo build --release -p jolt-prover --features profiling,cuda 2>&1 | grep -E '^error|-->|Finished' | head -30; echo "BUILD rc=${PIPESTATUS[0]} $(( $(date +%s)-t0 ))s"
B=$CARGO_TARGET_DIR/release/jolt-prover
RUNS=${RUNS:-"16:1:22 64:1:24 256:1:26"}
mkdir -p $W/pr1618-bench
for r in $RUNS; do IFS=: read n m s <<<"$r"; $G $n $m $W/pr1618-bench/vu-$n-$m.bin; done
for r in $RUNS; do
  IFS=: read n m s <<<"$r"
  for be in ${BACKENDS:-cuda optimized}; do
    O=$W/pr1618-bench/vu-$be-$n-$m
    nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits -lms 200 > $O.gpu.csv &
    SP=$!
    t0=$(date +%s.%N)
    JOLT_PROFILE_GUEST=vu-k1536-guest JOLT_PROFILE_INPUT=$W/pr1618-bench/vu-$n-$m.bin \
      /usr/bin/time -v timeout 1800 $B profile --name sha2-chain --scale $s --format none --backend $be > $O.log 2>&1
    rc=$?; t1=$(date +%s.%N); kill $SP
    grep -E 'MODULAR_TRACE_LEN|Prover completed|Peak RSS|panicked|rror|Maximum resident' $O.log | cut -c1-250
    echo "VUPROFILE be=$be B=$n mode=$m scale=$s rc=$rc wall=$(python3 -c "print(round($t1-$t0,2))")s gpu_max_util=$(cut -d, -f1 $O.gpu.csv | sort -n | tail -1) gpu_max_mem_mib=$(cut -d, -f2 $O.gpu.csv | sort -n | tail -1)"
  done
done
flock -u 9
echo PR1618_VU_DONE $(date -u +%H:%M:%SZ)
