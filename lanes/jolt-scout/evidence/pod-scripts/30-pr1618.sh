#!/usr/bin/env bash
# jolt-scout: a16z/jolt PR #1618 "Draft: CUDA kernels" (head 66e33a9e, base main 2026-08-17). Build jolt-prover with
# profiling,cuda for sm_89 (4090), then sweep sha2-chain (and fibonacci) over log2 trace scales on --backend optimized
# (CPU) and --backend cuda, under the pod-wide timing lock. Env: SCALES_MIN/MAX (default 18/22), BENCHES.
set -uo pipefail
W=/workspace/jolt-scout; cd $W/jolt-pr1618; source $HOME/.cargo/env
export PATH=/usr/local/cuda/bin:$PATH CUDA_HOME=/usr/local/cuda JOLT_CUDA_ARCH=${JOLT_CUDA_ARCH:-sm_89}
L=$W/30-pr1618.log; exec > >(tee -a $L) 2>&1
echo "REV $(git rev-parse HEAD) arch $JOLT_CUDA_ARCH nvcc $(nvcc --version | tail -1)"
export CARGO_TARGET_DIR=$W/target-pr1618
# CUDA 12.4's nvcc forwards --split-compile=0 to llc for -cubin and llc rejects it; the flag only sets compile threads
# CUDA 12.4 also fails on the kernels ("unsupported operation"); CUDA_VER installs that toolkit's nvcc beside it
CUDA_VER=${CUDA_VER:-12-9}
if [ ! -x /usr/local/cuda-${CUDA_VER/-/.}/bin/nvcc ]; then
  (cd /tmp && curl -sSLO https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb && dpkg -i cuda-keyring_1.1-1_all.deb >/dev/null && apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq cuda-nvcc-$CUDA_VER cuda-cudart-dev-$CUDA_VER >/dev/null) || echo "CUDA $CUDA_VER install failed"
fi
NVCC_REAL=/usr/local/cuda-${CUDA_VER/-/.}/bin/nvcc; $NVCC_REAL --version | tail -1
cat > $W/nvcc-wrap <<EOF
#!/bin/sh
for a in "\$@"; do shift; [ "\$a" = "--split-compile=0" ] || set -- "\$@" "\$a"; done
exec $NVCC_REAL "\$@"
EOF
chmod +x $W/nvcc-wrap; export JOLT_NVCC=$W/nvcc-wrap
t0=$(date +%s); cargo install --locked --path . --root $W/pr1618-bin 2>&1 | tail -1; echo "INSTALL_JOLT_CLI rc=${PIPESTATUS[0]} $(( $(date +%s)-t0 ))s"
export PATH=$W/pr1618-bin/bin:$PATH
t0=$(date +%s); cargo build --release -p jolt-prover --features profiling,cuda 2>&1 | grep -E '^error|-->|Finished|nvcc' | head -40; echo "BUILD_PR1618 rc=${PIPESTATUS[0]} $(( $(date +%s)-t0 ))s"
B=$CARGO_TARGET_DIR/release/jolt-prover; ls -la $B || exit 1
$B profile --help | grep -A3 -i gpus
exec 9>$W/timing.lock; flock 9; echo "LOCK $(date -u +%H:%M:%SZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
mkdir -p $W/pr1618-bench; cd $W/pr1618-bench
for be in optimized cuda; do
  for bench in ${BENCHES:-sha2-chain fibonacci}; do
    for s in $(seq ${SCALES_MIN:-18} ${SCALES_MAX:-22}); do
      nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits -lms 200 > gpu-$be-$bench-$s.csv &
      S=$!
      t0=$(date +%s.%N)
      timeout 900 $B profile --name $bench --scale $s --format none --backend $be 2>&1 | grep -v '^\s*$' | tail -4 | cut -c1-250
      rc=${PIPESTATUS[0]}; kill $S
      echo "PROFILE be=$be bench=$bench scale=$s rc=$rc wall=$(echo "$(date +%s.%N) - $t0" | bc)s gpu_max_util=$(cut -d, -f1 gpu-$be-$bench-$s.csv | sort -n | tail -1) gpu_max_mem=$(cut -d, -f2 gpu-$be-$bench-$s.csv | sort -n | tail -1)"
    done
  done
done
flock -u 9
find $W/pr1618-bench -name '*.csv' -path '*results*' -exec sh -c 'echo "== $1"; cat "$1"' _ {} \;
echo PR1618_DONE
