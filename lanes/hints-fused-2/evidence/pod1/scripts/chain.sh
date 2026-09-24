#!/bin/bash
cd /workspace
while ! grep -q "rc=" /workspace/logs/base_v3x4_p2_16k.log 2>/dev/null; do sleep 5; done
pkill -f /workspace/base.sh; sleep 1; pkill -f "src-base.*bench-vu"; sleep 3
echo "base queue stopped $(date -u +%H:%M:%S)" > /workspace/logs/chain.log
echo ff52e47 > /workspace/src/TREE_SHA
OMP_NUM_THREADS=4 LIGERO_INSTANCES_CACHE=/workspace/instances-cache /workspace/run.sh /workspace/src diff_full2 /workspace/venv312/bin/python -m pytest -q -rfE -p no:cacheprovider --durations=8 backends/direct/ligero/hints_fused_test.py
echo "diff done $(date -u +%H:%M:%S)" >> /workspace/logs/chain.log
/workspace/ab.sh
echo "ab done $(date -u +%H:%M:%S)" >> /workspace/logs/chain.log
