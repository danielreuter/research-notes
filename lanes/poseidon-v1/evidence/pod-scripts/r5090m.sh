#!/usr/bin/env bash
# poseidon-v1 RTX 5090, re-measured with glibc's large-block mmap/trim off (coordinator 1003Z): a fresh sweep r5090m-fp4nvf4
# (row.sh: sweep from 1024 to the stop rule or OOM, cap 1048576, then the main-committer byte-identity run), then register it.
# fp4-nvf4 + lib.sh's --auth included-hash = fp4-nvf4+poseidon2 (fp4/hashed.py). Needs $PV/r2.env for registration.
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
SCRIPTS=/workspace/poseidon-v1/scripts
GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
CPU=$(lscpu | sed -n 's/^Model name: *//p' | head -1)
POD="vy-poseidon-v1 i1k6ayj2vk65nu ($GPU, $CPU)"
COMMITTER="main 58b113bc (lane/hash-commit b862be30 Poseidon2 committer + commit-gpu), via lane/poseidon-v1 82adc8a7"
bash $SCRIPTS/row.sh r5090m-fp4nvf4 fp4-nvf4 8192 8 1048576
bash $SCRIPTS/register.sh r5090m-fp4nvf4 "$POD" "$COMMITTER"
rm -f /workspace/poseidon-v1/r2.env
echo R5090M_DONE
