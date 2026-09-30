#!/usr/bin/env bash
# sm_120 TP2 rerun (lane vllm-sm120-kernels): the op-level two-rank collectives after the operand-copy synchronisation fix (4b96d529),
# NCCL with P2P off, on the pod captures_tp2.sh bootstrapped.
set -uo pipefail
T=$(pwd -P); OUT=$RESEARCH_RUN_DIR/out; mkdir -p "$OUT"
VENV=/workspace/venv312
export CUDA_HOME=/usr/local/cuda-12.9 PATH=$VENV/bin:/usr/local/cuda-12.9/bin:$PATH HF_HOME=/workspace/hf NCCL_P2P_DISABLE=1
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd "$T/integrations/vllm"
AD=verity_vllm.program.registry.collectives_difftest
verity-vllm properties-admission produce --adapter $AD --n 30 --seed 5 --out "$OUT/collectives" && \
verity-vllm properties-admission check --adapter $AD --dir "$OUT/collectives" --out "$OUT/collectives/collectives.json"
echo "SM120-TP2B-DONE rc=$?"
