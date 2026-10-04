#!/usr/bin/env bash
# Red-team rate probe on one RTX PRO 6000 of vy-nebius-2 (`no-exact-rewrite/sm120-e4m3`). Holds the GPU's gpu-lease lock itself,
# because `gpu-lease N` takes the lowest free indices and the red team owns only GPUs 6-7:
#   research run --on vy-nebius-2 --project verity --source . --campaign pouw-red-team \
#     --send tc_rates_sm120.cu --send tc_rates_sm120.sh --send tc_rates_summary.py -- bash inputs/tc_rates_sm120.sh 6 GPU-2b59d5fe-...
set -euo pipefail
GPU=${1:?gpu index}
UUID=${2:?gpu uuid}
PROBE=${3:-tc_rates_sm120}
OUT=${RESEARCH_RUN_DIR:-$PWD}
IN=$OUT/inputs
NVCC=/usr/local/cuda/bin/nvcc
cd "$OUT"

"$NVCC" --version | tail -1 > nvcc.txt
if ! "$NVCC" -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a -Xptxas -v "$IN/$PROBE.cu" -o tc_rates 2> ptxas.log; then
  echo "int4 mma refused by ptxas; rebuilding without it" >> ptxas.log
  "$NVCC" -O3 -std=c++17 -DNO_INT4 -gencode arch=compute_120a,code=sm_120a -Xptxas -v "$IN/$PROBE.cu" -o tc_rates 2>> ptxas.log
fi
/usr/local/cuda/bin/cuobjdump -sass tc_rates > sass.txt

if [ -z "${GPU_LEASE_UUID:-}" ]; then   # not under `gpu-lease --on`: hold the index's lease lock directly
  exec 9>>"/run/gpu-lease/$GPU.lock"
  flock -n -x 9 || { echo "GPU $GPU is leased by someone else: $(cat /run/gpu-lease/$GPU.owner 2>/dev/null)" >&2; exit 75; }
  echo "pid=$$ run=${RESEARCH_RUN_ID:--} since=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "/run/gpu-lease/$GPU.owner"
  export CUDA_VISIBLE_DEVICES=$GPU CUDA_DEVICE_ORDER=PCI_BUS_ID
elif [ "$GPU_LEASE_UUID" != "$UUID" ]; then
  echo "the lease gave $GPU_LEASE_UUID, not $UUID" >&2; exit 3
fi
got=$(nvidia-smi --id="$UUID" --query-gpu=index,uuid,name --format=csv,noheader)
case "$got" in "$GPU, $UUID, "*) ;; *) echo "index $GPU is not $UUID: $got" >&2; exit 3 ;; esac

nvidia-smi --id="$UUID" --query-gpu=timestamp,clocks.sm,clocks.mem,power.draw,temperature.gpu,clocks_event_reasons.active \
  --format=csv -lms 200 > clocks.csv &
SMI=$!
./tc_rates 2100 "${ITERS:-4096}" > rates.jsonl
kill "$SMI" || true
python3 "$IN/tc_rates_summary.py" "$UUID"
