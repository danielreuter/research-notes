#!/usr/bin/env bash
# flock-bench: CUDA 13.3 + Rust + flock on the 5090 pod; runs clmad_peak / bench_f128; builds the Flock-CUDA roundtrip test.
set -euxo pipefail
W=/workspace/flock-bench; mkdir -p $W/out; cd $W
FLOCK_REV=${FLOCK_REV:-b684b12}
CUDA_VER=${CUDA_VER:-13-3}
nvidia-smi
if [ ! -x /usr/local/cuda-${CUDA_VER/-/.}/bin/nvcc ]; then
  export DEBIAN_FRONTEND=noninteractive
  if ! dpkg -s cuda-keyring >/dev/null 2>&1; then
    wget -q https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
    dpkg -i cuda-keyring_1.1-1_all.deb
  fi
  apt-get update -qq
  apt-cache search --names-only '^cuda-toolkit-13' | sort || true
  apt-get install -y -qq --no-install-recommends cuda-toolkit-${CUDA_VER}
fi
C13=/usr/local/cuda-${CUDA_VER/-/.}
$C13/bin/nvcc --version
$C13/bin/ptxas --version
if ! command -v cargo >/dev/null; then
  [ -x $HOME/.cargo/bin/cargo ] || curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable
fi
source $HOME/.cargo/env
[ -d flock ] || git clone -q https://github.com/succinctlabs/flock
cd flock && git fetch -q origin && git checkout -q $FLOCK_REV && git log --oneline -1
cd cuda-ghash
make NVCC=$C13/bin/nvcc bench_f128 test_f128 clmad_peak 2>&1 | tail -5 || \
  $C13/bin/nvcc -O3 -gencode arch=compute_120,code=sm_120 -std=c++17 clmad_peak.cu -o clmad_peak
[ -x clmad_peak ] || $C13/bin/nvcc -O3 -gencode arch=compute_120,code=sm_120 -std=c++17 clmad_peak.cu -o clmad_peak
$C13/bin/cuobjdump -sass clmad_peak | grep -c CLMAD || true
{ ./test_f128 || true; ./clmad_peak; ./bench_f128; } 2>&1 | tee $W/out/clmad-f128-5090.txt
nvidia-smi --query-gpu=name,driver_version,clocks.max.sm,clocks.sm,power.limit --format=csv | tee -a $W/out/clmad-f128-5090.txt
