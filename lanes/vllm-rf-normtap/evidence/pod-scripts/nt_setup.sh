#!/usr/bin/env bash
# nt_setup.sh: bootstrap the pod from the shipped tree (venv312, vLLM d9105ea80, checkpoints B0 + LLAMA32_1B, hidden_gpu, FA2 tap),
# then build and check the norm-scale tap op (ops/pod_norm_tap.sh).  research run --on <pod> --cwd source --send nt_setup.sh
set -u
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv > "$OUT/evidence/gpu.txt" 2>&1; cat "$OUT/evidence/gpu.txt"
bash verity_vllm/ops/pod_bootstrap.sh --cases B0,LLAMA32_1B --out /workspace/nt/bootstrap > "$OUT/bootstrap.log" 2>&1; echo "bootstrap rc $? $(date -u +%FT%TZ)"
tail -n 3 "$OUT/bootstrap.log"
cp /workspace/nt/bootstrap/readiness.json "$OUT/evidence/" 2>/dev/null
bash verity_vllm/ops/pod_norm_tap.sh > "$OUT/norm_tap.log" 2>&1; echo "norm tap rc $? $(date -u +%FT%TZ)"
tail -n 4 "$OUT/norm_tap.log"
cp /workspace/cp/norm_tap/build/build_info.json /workspace/cp/norm_tap/logs/build.log "$OUT/evidence/" 2>/dev/null
echo "NT-SETUP-DONE $(date -u +%FT%TZ)"
