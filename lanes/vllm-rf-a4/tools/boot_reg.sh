#!/bin/bash
# bootstrap from the head tree (pod_bootstrap.sh --cpu), then a1's baseline freeze pins: pytest-xdist 3.8.0, xgrammar 0.2.7
L=/workspace/a4/logs; mkdir -p $L
cd /workspace/head2/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap > $L/bootstrap.log 2>&1
echo "bootstrap rc=$? $(date -u +%FT%TZ)" >> $L/progress
export PATH=$HOME/.local/bin:$PATH
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 xgrammar==0.2.7 >> $L/bootstrap.log 2>&1
echo "pins rc=$? $(date -u +%FT%TZ)" >> $L/progress
uv pip freeze --python /workspace/venv312/bin/python > $L/freeze.txt 2>&1
