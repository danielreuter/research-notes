#!/usr/bin/env bash
# jolt-scout: 4c259be477 + 21-icicle-patch.py (local build fix), --features icicle; then sha2-chain CPU vs ICICLE runs
# under the pod-wide timing lock, GPU sampled during ICICLE runs. Arg: $1 = 21-icicle-patch.py
set -uo pipefail
PATCH=$(readlink -f "$1")
W=/workspace/jolt-scout; cd $W/jolt-icicle; source $HOME/.cargo/env
export PATH=/usr/local/cuda/bin:$PATH CUDACXX=/usr/local/cuda/bin/nvcc CUDA_HOME=/usr/local/cuda
L=$W/22-icicle-gpu.log; exec > >(tee -a $L) 2>&1
git checkout -q -- jolt-core/src/poly/commitment/kzg.rs; python3 $PATCH $W/jolt-icicle; git diff --stat
export CARGO_TARGET_DIR=$W/target-icicle-gpu
t0=$(date +%s); cargo build --release -p sha2-chain --features jolt-sdk/icicle 2>&1 | grep -E '^error|-->|Finished' | head -30; echo "BUILD_GPU rc=${PIPESTATUS[0]} $(( $(date +%s)-t0 ))s"
BK=$W/target-icicle-gpu/release/build/deps/icicle/lib/backend; ls $BK
exec 9>$W/timing.lock; flock 9; echo "LOCK $(date -u +%H:%M:%SZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
for i in 1 2 3; do echo "== CPU run $i"; RUST_LOG=info $W/target-icicle-cpu/release/sha2-chain 2>&1 | tail -4; done
for i in 1 2 3; do
  echo "== ICICLE run $i"
  nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used --format=csv,noheader -lms 100 > $W/22-gpu-sample-$i.csv &
  S=$!
  ICICLE_BACKEND_INSTALL_DIR=$BK RUST_LOG=info $W/target-icicle-gpu/release/sha2-chain 2>&1 | tail -6
  kill $S
  echo "GPU samples $(wc -l < $W/22-gpu-sample-$i.csv); max util $(cut -d, -f2 $W/22-gpu-sample-$i.csv | tr -dc '0-9\n' | sort -n | tail -1)%; samples>0%: $(cut -d, -f2 $W/22-gpu-sample-$i.csv | tr -dc '0-9\n' | awk '$1>0' | wc -l); max mem $(cut -d, -f3 $W/22-gpu-sample-$i.csv | tr -dc '0-9\n' | sort -n | tail -1) MiB"
done
flock -u 9
echo ICICLE_GPU_DONE
