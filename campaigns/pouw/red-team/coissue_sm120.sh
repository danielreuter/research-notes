#!/usr/bin/env bash
# `concurrent-budgets/sm120`: pipe co-issue on one red-team GPU of vy-nebius-2, under a named lease:
#   research run --on vy-nebius-2 --project verity --source <tree> --campaign pouw-red-team --send coissue_sm120.cu \
#     --send coissue_sm120.sh -- gpu-lease 1 --wait --on 6 --max-min 10 -- bash inputs/coissue_sm120.sh 6 GPU-...
set -euo pipefail
GPU=${1:?gpu index}
UUID=${2:?gpu uuid}
OUT=${RESEARCH_RUN_DIR:-$PWD}
cd "$OUT"
[ "${GPU_LEASE_UUID:-}" = "$UUID" ] || { echo "run under gpu-lease on $UUID (got ${GPU_LEASE_UUID:-none})" >&2; exit 3; }
/usr/local/cuda/bin/nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a inputs/coissue_sm120.cu -o coissue
/usr/local/cuda/bin/cuobjdump -sass coissue | grep -oE "\b(FFMA|IADD3|IMAD|IDP\.4A[A-Z0-9._]*|HFMA2[A-Z0-9._]*|QMMA[A-Z0-9._]*)\b" | sort | uniq -c > sass-ops.txt
nvidia-smi --id="$UUID" --query-gpu=clocks.sm,power.draw,clocks_event_reasons.active --format=csv -lms 200 > clocks.csv &
SMI=$!
./coissue 2100 2048 > summary.jsonl
kill $SMI || true
cat summary.jsonl sass-ops.txt
