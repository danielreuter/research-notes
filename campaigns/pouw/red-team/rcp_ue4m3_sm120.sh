#!/usr/bin/env bash
# rcp.approx on the UE4M3 scale bytes, on one red-team GPU of vy-nebius-2 under a named lease (see rcp_ue4m3_sm120.cu).
set -euo pipefail
UUID=${1:?gpu uuid}
cd "${RESEARCH_RUN_DIR:-$PWD}"
[ "${GPU_LEASE_UUID:-}" = "$UUID" ] || { echo "run under gpu-lease on $UUID (got ${GPU_LEASE_UUID:-none})" >&2; exit 3; }
/usr/local/cuda/bin/nvcc --version | tail -1 > nvcc.txt
/usr/local/cuda/bin/nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a inputs/rcp_ue4m3_sm120.cu -o rcp_ue4m3
/usr/local/cuda/bin/cuobjdump -sass rcp_ue4m3 | grep -oE "MUFU[A-Z0-9._]*|CALL[A-Z0-9._]*" | sort | uniq -c > sass-ops.txt
./rcp_ue4m3 > summary.txt
cat summary.txt sass-ops.txt nvcc.txt
