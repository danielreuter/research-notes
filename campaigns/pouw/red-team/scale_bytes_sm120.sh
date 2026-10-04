#!/usr/bin/env bash
# NVFP4 scale bytes outside UE4M3 on one red-team GPU of vy-nebius-2, under a named lease:
#   research run --on vy-nebius-2 --project verity --source <tree> --campaign pouw-red-team --send scale_bytes_sm120.cu \
#     --send scale_bytes_sm120.sh -- gpu-lease 1 --wait --on 6 --max-min 10 -- bash inputs/scale_bytes_sm120.sh GPU-...
set -euo pipefail
UUID=${1:?gpu uuid}
cd "${RESEARCH_RUN_DIR:-$PWD}"
[ "${GPU_LEASE_UUID:-}" = "$UUID" ] || { echo "run under gpu-lease on $UUID (got ${GPU_LEASE_UUID:-none})" >&2; exit 3; }
/usr/local/cuda/bin/nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a inputs/scale_bytes_sm120.cu -o scale_bytes
/usr/local/cuda/bin/cuobjdump -sass scale_bytes | grep -oE "OMMA[A-Z0-9._]*" | sort | uniq -c > sass-ops.txt
./scale_bytes > summary.jsonl
cat sass-ops.txt
