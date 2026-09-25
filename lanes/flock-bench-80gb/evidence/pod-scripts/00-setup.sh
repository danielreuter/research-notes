#!/usr/bin/env bash
# flock-bench-80gb: CUDA 13.3 + Rust + flock b684b12 on an H100/A100 pod; clmad_peak / bench_f128 / test_f128 on
# the pod's arch; then the CPU prover build (bench profile, thin LTO) with the verity_shape harness.
# Adapted from lanes/flock-bench/evidence/pod-scripts/02-setup-gpu.sh + 01-setup-cpu.sh. env: SM=90|80
set -uxo pipefail
W=/workspace/flock-bench-80gb; mkdir -p $W/out; cd $W
FLOCK_REV=${FLOCK_REV:-b684b12}
SM=${SM:-90}
TAG=${TAG:-sm$SM}
nvidia-smi
lscpu | grep -E 'Model name|^CPU\(s\)|Thread'; nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; grep -o -w -E 'avx512f|vpclmulqdq|pclmulqdq|gfni' /proc/cpuinfo | sort | uniq -c
free -g
if [ ! -x /usr/local/cuda-13.3/bin/nvcc ]; then
  export DEBIAN_FRONTEND=noninteractive
  . /etc/os-release; REPO=ubuntu${VERSION_ID/./}
  if ! dpkg -s cuda-keyring >/dev/null 2>&1; then
    wget -q https://developer.download.nvidia.com/compute/cuda/repos/$REPO/x86_64/cuda-keyring_1.1-1_all.deb
    dpkg -i cuda-keyring_1.1-1_all.deb
  fi
  apt-get update -qq
  apt-cache search --names-only '^cuda-toolkit-13' | sort || true
  apt-get install -y -qq --no-install-recommends cuda-toolkit-13-3 || exit 1
fi
[ -x /usr/bin/time ] || { apt-get install -y -qq time || { apt-get update -qq && apt-get install -y -qq time; }; }
C13=/usr/local/cuda-13.3
$C13/bin/nvcc --version; $C13/bin/ptxas --version
# CUDA 13.x runtime needs driver >= 580; on older datacenter drivers use the forward-compat user-mode driver
DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | cut -d. -f1)
if [ "$DRV" -lt 580 ]; then
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq cuda-compat-13-3 || exit 1
  export LD_LIBRARY_PATH=$C13/compat:${LD_LIBRARY_PATH:-}
  echo "driver $DRV < 580: using cuda-compat-13-3 ($(ls $C13/compat/libcuda.so.*))"
fi
if ! command -v cargo >/dev/null; then
  [ -x $HOME/.cargo/bin/cargo ] || curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable
fi
source $HOME/.cargo/env
rustc --version
[ -d flock ] || git clone -q https://github.com/succinctlabs/flock
cd flock && git fetch -q origin && git checkout -q $FLOCK_REV && git log --oneline -1
cd cuda-ghash
FL="-O3 -gencode arch=compute_$SM,code=sm_$SM -lineinfo -std=c++17"
for b in test_f128 bench_f128 clmad_peak; do
  $C13/bin/nvcc $FL $b.cu -o $b.$TAG 2>&1 | tail -5
done
echo "CLMAD SASS count:"; $C13/bin/cuobjdump -sass clmad_peak.$TAG | grep -c CLMAD || true
$C13/bin/cuobjdump -sass bench_f128.$TAG | grep -c CLMAD || true
{ ./test_f128.$TAG || true; ./clmad_peak.$TAG; ./bench_f128.$TAG; } 2>&1 | tee $W/out/clmad-f128-$TAG.txt
nvidia-smi --query-gpu=name,driver_version,clocks.max.sm,clocks.sm,power.limit --format=csv | tee -a $W/out/clmad-f128-$TAG.txt
cp $W/out/clmad-f128-$TAG.txt "$RESEARCH_RUN_DIR/" 2>/dev/null || true
# CPU prover build (bench profile = thin LTO, as flock's own cargo bench numbers)
cd $W/flock
cp "$RESEARCH_RUN_DIR/inputs/verity_shape.rs" crates/flock-prover/benches/verity_shape.rs
grep -q 'name = "verity_shape"' crates/flock-prover/Cargo.toml || printf '\n[[bench]]\nname = "verity_shape"\nharness = false\n' >> crates/flock-prover/Cargo.toml
time cargo bench --no-run -p flock-prover --bench verity_shape -j $(nproc) 2>&1 | tail -3
ls -la target/release/deps | grep -E 'verity_shape' | grep -v '\.d$' || true
