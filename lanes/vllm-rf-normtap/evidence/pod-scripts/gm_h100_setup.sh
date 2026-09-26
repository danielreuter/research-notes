#!/usr/bin/env bash
# gm_h100_setup.sh: bootstrap the H100 pod from the shipped tree (venv312, vLLM, the FA taps; FA2 at head dim 64 only, since this pod only
# checks FA3), then build the FA3 guarded-max tap (FA3_TAP_ROW_GUARD=1) beside the default FA3 tap the bootstrap built.
#   research run --on vyv-rf-normtap-h1 --project verity --source <worktree> --cwd source --custody-r2 --send gm_h100_setup.sh \
#     -- bash -c 'bash $RESEARCH_RUN_DIR/inputs/gm_h100_setup.sh'
set -u
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv > "$OUT/evidence/gpu.txt" 2>&1; cat "$OUT/evidence/gpu.txt"
FA2_TAP_HDIMS=64 bash verity_vllm/ops/pod_bootstrap.sh --cases B0 --out /workspace/gm/bootstrap > "$OUT/bootstrap.log" 2>&1
echo "bootstrap rc $? $(date -u +%FT%TZ)"; tail -n 3 "$OUT/bootstrap.log"
FA3_TAP_ROW_GUARD=1 bash verity_vllm/ops/pod_fa3_tap.sh > "$OUT/fa3_guard.log" 2>&1; echo "fa3 guard rc $? $(date -u +%FT%TZ)"; tail -n 2 "$OUT/fa3_guard.log"
for b in fa3_matReq fa3_matReqG; do cp /workspace/cp/fa2/build/$b/build_info.json "$OUT/evidence/${b}_build_info.json" 2>/dev/null; done
echo "GM-H100-SETUP-DONE $(date -u +%FT%TZ)"
