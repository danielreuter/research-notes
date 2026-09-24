#!/bin/bash
# baselines on the pristine tree (5e6b3e3), same pod
cd /workspace
B="/workspace/venv312/bin/python -m backends.direct.ligero.run"
C="--zk --mode interactive --total-vus 4096 --reps 3 --device cuda --instances-cache /workspace/instances-cache"
mkdir -p /workspace/results /workspace/dumps
/workspace/run.sh /workspace/src-base base_v3_p4_16k $B --relation fp8-ada-v3 bench-vu $C --batch 16384 --pipeline 4 --out /workspace/results/base_v3_p4_16k.json
/workspace/run.sh /workspace/src-base base_v3x4_p2_16k $B --relation fp8-ada-v3x4 bench-vu $C --batch 16384 --pipeline 2 --out /workspace/results/base_v3x4_p2_16k.json
/workspace/run.sh /workspace/src-base base_v3x4_p4_16k $B --relation fp8-ada-v3x4 bench-vu $C --batch 16384 --pipeline 4 --out /workspace/results/base_v3x4_p4_16k.json
/workspace/run.sh /workspace/src-base base_v3x4_p4_4k $B --relation fp8-ada-v3x4 bench-vu $C --batch 4096 --pipeline 4 --out /workspace/results/base_v3x4_p4_4k.json
/workspace/run.sh /workspace/src-base base_v2x4_p4_16k $B --relation fp8-ada-v2x4 bench-vu $C --batch 16384 --pipeline 4 --out /workspace/results/base_v2x4_p4_16k.json
echo BASE_DONE > /workspace/logs/base_done
