#!/usr/bin/env bash
# `fp-model/sm120-scalar` and `fp8-tile-only/sm120`'s untimed kinds on one red-team GPU of vy-nebius-2 (6 or 7), holding that index's gpu-lease lock itself:
#   research run --on vy-nebius-2 --project verity --source <tree> --campaign pouw-red-team \
#     --send scalar_model_sm120.cu --send scalar_model_sm120.sh --send scalar_model_check.py --send tc_kinds_sm120.cu \\
#     -- gpu-lease 1 --wait --on 6 --max-min 20 -- bash inputs/scalar_model_sm120.sh 6 GPU-...
set -euo pipefail
GPU=${1:?gpu index}
UUID=${2:?gpu uuid}
OUT=${RESEARCH_RUN_DIR:-$PWD}
IN=$OUT/inputs
TREE=/workspace/research/src/${RESEARCH_SOURCE_SHA:?}
NVCC=/usr/local/cuda/bin/nvcc
cd "$OUT"
"$NVCC" --version | tail -1 > nvcc.txt
"$NVCC" -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a "$IN/scalar_model_sm120.cu" -o scalar_model
"$NVCC" -O3 -std=c++17 -DPOSITIVE_CONTROL -gencode arch=compute_120a,code=sm_120a "$IN/scalar_model_sm120.cu" -o scalar_model_ftz
/usr/local/cuda/bin/cuobjdump -sass scalar_model | grep -oE "F2FP[A-Z0-9._]*|FADD[A-Z0-9._]*|[A-Z]*MMA[A-Z0-9._]*" | sort | uniq -c > sass-ops.txt
/usr/local/cuda/bin/cuobjdump -sass scalar_model_ftz | grep -oE "FADD[A-Z0-9._]*" | sort | uniq -c > sass-ops-control.txt

for flags in "" "-DSKIP_B1" "-DSKIP_B1 -DSKIP_MX"; do
  if "$NVCC" -O3 -std=c++17 $flags -gencode arch=compute_120a,code=sm_120a "$IN/tc_kinds_sm120.cu" -o tc_kinds 2> tc_kinds_ptxas.log; then
    echo "tc_kinds built with flags '$flags'" >> tc_kinds_ptxas.log; break
  fi
  cp tc_kinds_ptxas.log "tc_kinds_ptxas_failed${flags// /}.log"
done
/usr/local/cuda/bin/cuobjdump -sass tc_kinds | grep -oE "[A-Z]*MMA[A-Z0-9._]*" | sort | uniq -c > sass-ops-kinds.txt

if [ -z "${GPU_LEASE_UUID:-}" ]; then   # not under gpu-lease: hold the index's lease lock directly
  exec 9>>"/run/gpu-lease/$GPU.lock"
  flock -n -x 9 || { echo "GPU $GPU is leased by someone else: $(cat /run/gpu-lease/$GPU.owner 2>/dev/null)" >&2; exit 75; }
  echo "pid=$$ run=${RESEARCH_RUN_ID:--} since=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "/run/gpu-lease/$GPU.owner"
  export CUDA_VISIBLE_DEVICES=$GPU CUDA_DEVICE_ORDER=PCI_BUS_ID
elif [ "$GPU_LEASE_UUID" != "$UUID" ]; then
  echo "the lease gave $GPU_LEASE_UUID, not $UUID" >&2; exit 3
fi
got=$(nvidia-smi --id="$UUID" --query-gpu=index,uuid,name --format=csv,noheader)
case "$got" in "$GPU, $UUID, "*) ;; *) echo "index $GPU is not $UUID: $got" >&2; exit 3 ;; esac

py() { (cd "$TREE" && PYTHONPATH=packages/verity/src:protocols/pouw uv run --no-dev python "$IN/scalar_model_check.py" "$@"); }
{
  ./scalar_model cast
  ./scalar_model fadd
  ./scalar_model mma
  ./scalar_model_ftz fadd | sed 's/"check":"fadd"/"check":"fadd-positive-control-ftz"/'
  py mkcast "$OUT/cast_in.bin"; ./scalar_model castdump "$OUT/cast_in.bin" "$OUT/cast_dev.bin" > /dev/null
  py cmpcast "$OUT/cast_in.bin" "$OUT/cast_dev.bin"
  py mkfadd "$OUT/fadd_in.bin"; ./scalar_model fadddump "$OUT/fadd_in.bin" "$OUT/fadd_dev.bin" > /dev/null
  py cmpfadd "$OUT/fadd_in.bin" "$OUT/fadd_dev.bin"
  ./tc_kinds 2100 4096
} > summary.jsonl
rm -f cast_in.bin cast_dev.bin fadd_in.bin fadd_dev.bin
cat summary.jsonl
