#!/bin/bash
# CPU bootstrap from the head tree, plus pytest-xdist.   log: /workspace/b4/logs/boot.log
L=/workspace/b4/logs; mkdir -p $L
cd /workspace/head/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap > $L/boot.log 2>&1
export PATH=$HOME/.local/bin:$PATH
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 >> $L/boot.log 2>&1
grep -E '^BOOTSTRAP-OK' $L/boot.log && echo XDIST $(/workspace/venv312/bin/python -c 'import xdist; print(xdist.__version__)')
