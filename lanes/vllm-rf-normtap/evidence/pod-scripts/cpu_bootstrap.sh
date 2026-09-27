#!/usr/bin/env bash
# cpu_bootstrap.sh: the CPU pod's environment from the shipped tree (pod_bootstrap.sh --cpu: venv312, vLLM CPU wheels, torch), plus the
# gate (b) pins gate_b3.sh BOOTSTRAP=1 installs (pytest-xdist and the three serving-side pins).
set -u
L=$RESEARCH_RUN_DIR
(cd integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap) > $L/bootstrap.log 2>&1
echo "bootstrap rc=$? $(date -u +%FT%TZ) $(tail -1 $L/bootstrap.log)"
export PATH=$HOME/.local/bin:$PATH
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 xgrammar==0.2.7 googleapis-common-protos==1.75.3 uvicorn==0.53.0 >> $L/bootstrap.log 2>&1
echo "pins rc=$? $(date -u +%FT%TZ)"
