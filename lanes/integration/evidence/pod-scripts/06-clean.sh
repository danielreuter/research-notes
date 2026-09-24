#!/usr/bin/env bash
# clean-GPU window: bench (contract column) first, then the A/B timings
nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader > /workspace/integration/clean_gpu_before.txt
bash /workspace/integration/scripts/04-bench.sh > /workspace/integration/bench.out 2>&1
bash /workspace/integration/scripts/03b-ab-timing.sh > /workspace/integration/abt.out 2>&1
echo CLEAN_DONE >> /workspace/integration/abt.out
