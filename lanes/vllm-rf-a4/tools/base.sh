#!/bin/bash
exec 9>/workspace/a4/base.lock; flock -n 9 || { echo "already running"; exit 0; }
mkdir -p /workspace/a4/logs
cd /workspace/base/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap > /workspace/a4/logs/bootstrap.log 2>&1
echo "bootstrap rc=$? $(date -u +%FT%TZ)" >> /workspace/a4/logs/progress
export PATH=$HOME/.local/bin:$PATH
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 >> /workspace/a4/logs/bootstrap.log 2>&1
echo "xdist rc=$? $(date -u +%FT%TZ)" >> /workspace/a4/logs/progress
bash /workspace/a4/lints.sh /workspace/base base >> /workspace/a4/logs/progress 2>&1
OMP_NUM_THREADS=3 bash /workspace/a4/gate_b.sh /workspace/base base-xdist -n 12 --dist loadfile >> /workspace/a4/logs/progress 2>&1
