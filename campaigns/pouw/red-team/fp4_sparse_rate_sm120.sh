#!/usr/bin/env bash
# OMMA.SF.SP against dense NVFP4, on one red-team GPU of vy-nebius-2 under a named lease (see fp4_sparse_rate_sm120.cu).
set -euo pipefail
UUID=${1:?gpu uuid}
cd "${RESEARCH_RUN_DIR:-$PWD}"
[ "${GPU_LEASE_UUID:-}" = "$UUID" ] || { echo "run under gpu-lease on $UUID (got ${GPU_LEASE_UUID:-none})" >&2; exit 3; }
/usr/local/cuda/bin/nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a inputs/fp4_sparse_rate_sm120.cu -o fp4_sparse 2> ptxas.log || { cat ptxas.log; exit 2; }
/usr/local/cuda/bin/cuobjdump -sass fp4_sparse | grep -oE "OMMA[A-Z0-9._]*" | sort | uniq -c > sass-ops.txt
./fp4_sparse 2100 4096 > summary.jsonl
cat summary.jsonl sass-ops.txt
