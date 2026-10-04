#!/usr/bin/env bash
# The honest E4M3 cast's price and mma.sync's data-independence, on one red-team GPU of vy-nebius-2, under a named lease:
#   research run --on vy-nebius-2 --project verity --source <tree> --campaign pouw-red-team --send cast_price_sm120.cu \
#     --send cast_price_sm120.sh -- gpu-lease 1 --wait --on 6 --max-min 10 -- bash inputs/cast_price_sm120.sh GPU-...
set -euo pipefail
UUID=${1:?gpu uuid}
cd "${RESEARCH_RUN_DIR:-$PWD}"
[ "${GPU_LEASE_UUID:-}" = "$UUID" ] || { echo "run under gpu-lease on $UUID (got ${GPU_LEASE_UUID:-none})" >&2; exit 3; }
/usr/local/cuda/bin/nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a inputs/cast_price_sm120.cu -o cast_price
/usr/local/cuda/bin/cuobjdump -sass cast_price | awk '/Function :/{f=$3} {for(i=1;i<=NF;i++) if ($i ~ /^(F2FP|STS|PRMT|LOP3|QMMA|IMAD|IADD3)/) c[f" "$i]++} END{for(k in c) print k, c[k]}' | sort > sass-ops.txt
nvidia-smi --id="$UUID" --query-gpu=clocks.sm,power.draw,clocks_event_reasons.active --format=csv -lms 200 > clocks.csv &
SMI=$!
./cast_price 4096 > summary.jsonl
kill $SMI || true
cat summary.jsonl
