#!/usr/bin/env bash
# sm_120 job D (lane vllm-sm120-kernels): job B's fused-MoE capture checked again, now against the Definitions a config run binds on
# cc 12.0 (MoeExpertGemm_v2 / MoeExpertGemmW_v2{DOT=HopperBF16WgmmaDot16_v1}, 7604eb59); CPU only.
set -uo pipefail
T=$(pwd -P); OUT=$RESEARCH_RUN_DIR/out; mkdir -p "$OUT"
VENV=/workspace/venv312
export PATH=$VENV/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd "$T/integrations/vllm"
verity-vllm properties-admission check --adapter verity_vllm.program.registry.moe_difftest --dir "${MOE_DIR:?}" --out "$OUT/moe_v2.json"
echo "SM120-D-DONE rc=$?"
