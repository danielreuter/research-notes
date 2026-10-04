#!/usr/bin/env bash
# `__frsqrt_rn` exactness on one red-team GPU of vy-nebius-2, under a named lease:
#   research run --on vy-nebius-2 --project verity --source <tree> --campaign pouw-red-team --send frsqrt_sm120.cu \
#     --send frsqrt_sm120.sh -- gpu-lease 1 --wait --on 6 --max-min 10 -- bash inputs/frsqrt_sm120.sh GPU-...
set -euo pipefail
UUID=${1:?gpu uuid}
cd "${RESEARCH_RUN_DIR:-$PWD}"
[ "${GPU_LEASE_UUID:-}" = "$UUID" ] || { echo "run under gpu-lease on $UUID (got ${GPU_LEASE_UUID:-none})" >&2; exit 3; }
/usr/local/cuda/bin/nvcc --version | tail -1 > nvcc.txt
/usr/local/cuda/bin/nvcc -O3 -std=c++17 ${NVCC_FLAGS:-} -gencode arch=compute_120a,code=sm_120a inputs/frsqrt_sm120.cu -o frsqrt
/usr/local/cuda/bin/cuobjdump -sass frsqrt | awk '/Function :/{f=$3} {for(i=1;i<=NF;i++) if ($i ~ /^(FADD|FFMA|FMUL|MUFU|FSETP|CALL)/) c[f" "$i]++} END{for(k in c) print k, c[k]}' | sort > sass-fp-ops.txt
echo "flags: ${NVCC_FLAGS:-none}; .FTZ ops in the binary: $(/usr/local/cuda/bin/cuobjdump -sass frsqrt | grep -c "\.FTZ")" > flags.txt
./frsqrt > summary.jsonl
cat summary.jsonl flags.txt sass-fp-ops.txt nvcc.txt
