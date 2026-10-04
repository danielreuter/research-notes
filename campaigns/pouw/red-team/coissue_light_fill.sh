#!/usr/bin/env bash
# fill: owner=bc-d7d4b0d1 gpus=1 on=2-7 max_min=8 cpus=4 project=pous prio=10 mem_gb=16
# The assessor (bc-d7d4b0d1): light CUDA-core mixes beside FP8, NVFP4 and FP16 mma.sync, for concurrent-budgets/sm120.
set -uo pipefail
W=/workspace/pouw/fill-out/assessor-coissue-light; cd $W
[ -n "${GPU_LEASE_UUID:-}" ] || exit 3
[ -e done ] && exit 0
nvidia-smi --id="$GPU_LEASE_UUID" --query-gpu=timestamp,clocks.sm,clocks_event_reasons.active --format=csv,noheader -lms 200 > clocks.csv &
SMI=$!; trap 'kill $SMI 2>/dev/null' EXIT
for r in 1 2 3; do ./coissue_light 2092 | sed "s/^{/{\"rep\":$r,\"uuid\":\"$GPU_LEASE_UUID\",/" >> mixes.jsonl || exit 1; done
touch done; exit 0
