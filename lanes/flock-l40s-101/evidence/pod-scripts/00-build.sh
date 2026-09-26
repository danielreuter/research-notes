# flock-l40s-101: pre-build both pods (research run --on POD ... -- bash -c "$(cat 00-build.sh)" with --env GPU=0|1 SM=89)
# flock-gpu-link + flock-pure-gpu through 20-gpu-link.sh (GPU=1: its 8-VU CPU+GPU selftest), then flock-ir-frame.
set -uxo pipefail
MODE=$([ "$GPU" = 1 ] && echo selftest || echo build) VUS=8 bash backends/flock/pod/20-gpu-link.sh || exit 1
source $HOME/.cargo/env; C13=${CUDA_TK:-/usr/local/cuda-13.3}
[ "$GPU" = 1 ] && export PATH=$C13/bin:$PATH NVCC=$C13/bin/nvcc LD_LIBRARY_PATH=$C13/compat:$C13/lib64:${LD_LIBRARY_PATH:-}
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { read -r Q < /sys/fs/cgroup/cpu/cpu.cfs_quota_us && read -r PER < /sys/fs/cgroup/cpu/cpu.cfs_period_us; } 2>/dev/null || { Q=max; PER=100000; }; [ "$Q" = -1 ] && Q=max
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
FEAT=; [ "$GPU" = 1 ] && FEAT="--features gpu"
cd /workspace/flock-gpu-link/flock && cargo build --release -p flock-live $FEAT --bin flock-ir-frame -j $TH 2>&1 | tail -3
sha256sum target/release/flock-pure-gpu target/release/flock-ir-frame
