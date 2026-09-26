#!/usr/bin/env bash
# mt_setup.sh: GPU bootstrap of the pod from the shipped tree (venv312, vLLM d9105ea80, checkpoint B0, hidden_gpu, FA2 tap),
# then the gate (b) pins gate_b2.sh installs only under BOOTSTRAP=1 (whose bootstrap is the CPU one).
#   research run --on <pod> --project verity --source <tree> --cwd source --custody-r2 --send mt_setup.sh -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/mt_setup.sh"'
set -u
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence"
export PATH=/workspace/venv312/bin:$HOME/.local/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv > "$OUT/evidence/gpu.txt" 2>&1; cat "$OUT/evidence/gpu.txt"; nproc
bash verity_vllm/ops/pod_bootstrap.sh --cases B0 --out /workspace/mt/bootstrap > "$OUT/bootstrap.log" 2>&1; echo "bootstrap rc $? $(date -u +%FT%TZ)"
tail -n 3 "$OUT/bootstrap.log"
cp /workspace/mt/bootstrap/readiness.json "$OUT/evidence/" 2>/dev/null
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 xgrammar==0.2.7 googleapis-common-protos==1.75.3 uvicorn==0.53.0 \
  > "$OUT/pins.log" 2>&1; echo "pins rc $? $(date -u +%FT%TZ)"
python -c "import vllm, torch; print('vllm', vllm.__version__, 'torch', torch.__version__, torch.version.cuda)"
echo "MT-SETUP-DONE $(date -u +%FT%TZ)"
