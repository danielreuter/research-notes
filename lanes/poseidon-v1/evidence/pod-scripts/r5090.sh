#!/usr/bin/env bash
# poseidon-v1 RTX 5090: the NVFP4 row (row.sh), then register it (register.sh; needs $PV/r2.env)
SCRIPTS=/workspace/poseidon-v1/scripts
GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
CPU=$(lscpu | sed -n 's/^Model name: *//p' | head -1)
POD="vy-poseidon-v1 i1k6ayj2vk65nu ($GPU, $CPU)"
COMMITTER="main 58b113bc (lane/hash-commit b862be30 Poseidon2 committer + commit-gpu), via lane/poseidon-v1 82adc8a7"
bash $SCRIPTS/row.sh r5090-fp4nvf4 fp4-nvf4+poseidon2 8192 8 131072
bash $SCRIPTS/register.sh r5090-fp4nvf4 "$POD" "$COMMITTER"
rm -f /workspace/poseidon-v1/r2.env
echo R5090_DONE
