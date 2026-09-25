#!/usr/bin/env bash
# b-ligero-vllm-v1: shared pod environment (research run --on does not source env.sh; pod_bootstrap.sh wrote it)
set -uo pipefail
source /workspace/env.sh
Q=$(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us 2>/dev/null || echo -1); PER=$(cat /sys/fs/cgroup/cpu/cpu.cfs_period_us 2>/dev/null || echo 100000)
if [ -r /sys/fs/cgroup/cpu.max ]; then read -r Q PER < /sys/fs/cgroup/cpu.max; [ "$Q" = max ] && Q=-1; fi
NT=$(( Q > 0 ? Q / PER : $(nproc) )); [ "$NT" -lt 1 ] && NT=1
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}
# first-touch page faults on this host class run at ~20 MB/s (23-pinned-bench.py: a fresh 91 MB numpy copy 4-7 s, reused 8 ms);
# glibc's mmap'd large blocks are unmapped on free, so every proof's opened columns (M x t) re-fault. Keep freed memory in
# the heap: the process faults its peak in once (the warm-up rep), then reuses it.
export MALLOC_MMAP_MAX_=${MALLOC_MMAP_MAX_:-0} MALLOC_TRIM_THRESHOLD_=${MALLOC_TRIM_THRESHOLD_:-1000000000000}
V=${LIGERO_VERIFY:-/workspace/bin/ligero-verify}
echo "cpu threads $NT (quota $Q / $PER, nproc $(nproc)); cwd $(pwd); commit ${RESEARCH_SOURCE_COMMIT:-$(git rev-parse HEAD 2>/dev/null || cat .research-source.json 2>/dev/null | head -c 300)}"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
gpu_idle() {  # wait up to 120 s for an empty GPU
  for _ in $(seq 60); do [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ] && return 0; sleep 2; done
  echo "GPU NOT IDLE: $(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader | tr '\n' ' ')"; return 1
}
