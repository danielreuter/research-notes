#!/usr/bin/env bash
# flock-glue: CUDA 13.3 + Rust + flock b684b12 on an A100/H100 pod, Flock-CUDA build.rs retargeted to sm_$SM,
# then flock-bench's 22-gpu-unit.sh patch (host-witness `flock_cuda_prove_host`) for the "before" baseline.
# Adapted from lanes/flock-bench-80gb/evidence/pod-scripts/00-setup.sh + 20-gpu.sh. env: SM=80|90
set -uxo pipefail
W=/workspace/flock-glue; mkdir -p $W/out; cd $W
FLOCK_REV=${FLOCK_REV:-b684b12}
SM=${SM:-80}
nvidia-smi
lscpu | grep -E 'Model name|^CPU\(s\)'; nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; free -g; df -h /workspace
if [ ! -x /usr/local/cuda-13.3/bin/nvcc ]; then
  export DEBIAN_FRONTEND=noninteractive
  . /etc/os-release; REPO=ubuntu${VERSION_ID/./}
  if ! dpkg -s cuda-keyring >/dev/null 2>&1; then
    wget -q https://developer.download.nvidia.com/compute/cuda/repos/$REPO/x86_64/cuda-keyring_1.1-1_all.deb
    dpkg -i cuda-keyring_1.1-1_all.deb
  fi
  apt-get update -qq
  apt-get install -y -qq --no-install-recommends cuda-toolkit-13-3 || exit 1
fi
[ -x /usr/bin/time ] || apt-get install -y -qq time
C13=/usr/local/cuda-13.3
DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | cut -d. -f1)
if [ "$DRV" -lt 580 ]; then
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq cuda-compat-13-3 || exit 1
fi
ls /opt/nvidia/nsight-systems/*/bin/nsys $C13/nsight-systems-*/bin/nsys $C13/bin/nsys 2>/dev/null
if ! command -v cargo >/dev/null; then
  [ -x $HOME/.cargo/bin/cargo ] || curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable
fi
source $HOME/.cargo/env
rustc --version
[ -d flock ] || git clone -q https://github.com/succinctlabs/flock
cd flock && git fetch -q origin && git checkout -q $FLOCK_REV && git log --oneline -1
sed -i "s/arch=compute_120,code=sm_120/arch=compute_$SM,code=sm_$SM/; s#/usr/local/cuda/lib64#/usr/local/cuda-13.3/lib64#g" crates/flock-cuda-ffi/build.rs
grep -n "gencode\|lib64" crates/flock-cuda-ffi/build.rs | head
git status --short
