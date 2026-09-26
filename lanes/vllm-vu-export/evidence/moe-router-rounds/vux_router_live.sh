#!/usr/bin/env bash
# vux_router_live.sh N: bootstrap vLLM (B0) from the shipped tree, then router_live.py N (vLLM's topk_softmax vs the router Definitions)
set -u
T=$PWD; I=$RESEARCH_RUN_DIR/inputs; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
bash verity_vllm/ops/pod_bootstrap.sh --cases B0 --out /workspace/vux/bootstrap-router > "$OUT/bootstrap.log" 2>&1; echo "bootstrap rc $? $(date -u +%FT%TZ)"
cp "$I/router_eq.py" "$I/router_live.py" /tmp/
python /tmp/router_live.py "${1:-300}" "$OUT/evidence/router_live.json" 2>&1 | grep -v Warning; echo "router_live rc ${PIPESTATUS[0]} $(date -u +%FT%TZ)"
