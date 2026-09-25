#!/usr/bin/env bash
# blake3-80gb: pod environment for recorded runs (research run --on ... --source . --cwd source); env.sh cds to /workspace/src, so
# come back to the shipped tree.
set -uo pipefail
HERE=$(pwd)
source /workspace/env.sh
cd "$HERE"
export PYTHONPATH="$HERE/packages/verity/src:$HERE/backends/numerical/python:$HERE/tools/research/src:$HERE"
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 LIGERO_REFERENCE_HINTS=0 PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}
# glibc would mmap/unmap the big host arrays per proof (re-faulting them every rep); coordinator 1003Z
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
V=${LIGERO_VERIFY:-/workspace/bin/ligero-verify}
NT=${OMP_NUM_THREADS:-8}
echo "cwd $HERE commit ${RESEARCH_SOURCE_COMMIT:-?}; threads $NT; MALLOC_MMAP_MAX_=$MALLOC_MMAP_MAX_ MALLOC_TRIM_THRESHOLD_=$MALLOC_TRIM_THRESHOLD_"; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
gpu_idle() {
  for _ in $(seq 60); do [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ] && return 0; sleep 2; done
  echo "GPU NOT IDLE"; return 1
}
