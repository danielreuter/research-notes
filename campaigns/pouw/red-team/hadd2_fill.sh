#!/usr/bin/env bash
# fill: owner=bc-d7d4b0d1 gpus=1 on=2-7 max_min=8 cpus=4 project=pous prio=10 mem_gb=16
# The assessor (bc-d7d4b0d1): HADD2 / HFMA2 / FADD / FFMA issue rates on sm_120, for bc-3006c44a's pre-add floor (4 or 8 W1).
set -uo pipefail
W=/workspace/pouw/fill-out/assessor-hadd2; mkdir -p $W
[ -n "${GPU_LEASE_UUID:-}" ] || exit 3
[ -e $W/done ] && exit 0
cd $W
nvidia-smi --id="$GPU_LEASE_UUID" --query-gpu=timestamp,clocks.sm,clocks_event_reasons.active --format=csv,noheader -lms 200 > clocks.csv &
SMI=$!; trap 'kill $SMI 2>/dev/null' EXIT
for r in 1 2 3; do ./hadd2_rate | sed "s/^{/{\"rep\":$r,\"uuid\":\"$GPU_LEASE_UUID\",/" >> rates.jsonl || exit 1; done
touch done; exit 0
