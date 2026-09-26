#!/usr/bin/env bash
# gm_l40s_setup.sh: bootstrap the L40S pod from the shipped tree (venv312, vLLM d9105ea80, checkpoints B0 + LLAMA32_1B, hidden_gpu, the default
# FA2 tap at head dims 64/96/128/256), then build the FA2 guarded-max tap (FA2_TAP_ROW_GUARD=1) beside it.
#   research run --on vyv-rf-normtap-g2 --project verity --source <worktree> --cwd source --custody-r2 --send gm_l40s_setup.sh \
#     -- bash -c 'bash $RESEARCH_RUN_DIR/inputs/gm_l40s_setup.sh'
set -u
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv > "$OUT/evidence/gpu.txt" 2>&1; cat "$OUT/evidence/gpu.txt"
bash verity_vllm/ops/pod_bootstrap.sh --cases B0,LLAMA32_1B --out /workspace/gm/bootstrap > "$OUT/bootstrap.log" 2>&1
echo "bootstrap rc $? $(date -u +%FT%TZ)"; tail -n 3 "$OUT/bootstrap.log"
FA2_TAP_ROW_GUARD=1 bash verity_vllm/ops/pod_fa2_tap.sh > "$OUT/fa2_guard.log" 2>&1; echo "fa2 guard rc $? $(date -u +%FT%TZ)"; tail -n 2 "$OUT/fa2_guard.log"
for b in matReq matReqG; do cp /workspace/cp/fa2/build/$b/build_info.json "$OUT/evidence/${b}_build_info.json" 2>/dev/null; done
echo "GM-L40S-SETUP-DONE $(date -u +%FT%TZ)"
