#!/usr/bin/env bash
# poseidon-v1 RTX 4090, re-measured with glibc's large-block mmap/trim off (coordinator 1003Z): a fresh sweep r4090m-fp8ada
# (row.sh, cap 1048576), a same-pod malloc-unset A/B at n=4096 and the plateau (ab.sh), then register (needs $PV/r2.env)
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
SCRIPTS=/workspace/poseidon-v1/scripts
GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
CPU=$(lscpu | sed -n 's/^Model name: *//p' | head -1)
POD="vy-poseidon-v1 ${POD_ID:?} ($GPU, $CPU)"
COMMITTER="main 3301c435 (lane/hash-commit b862be30 Poseidon2 committer + commit-gpu 58b113bc), via lane/poseidon-v1 7ffb7095"
bash $SCRIPTS/row.sh r4090m-fp8ada fp8-ada 8192 4 1048576
bash $SCRIPTS/ab.sh r4090m-fp8ada fp8-ada 8192 4
bash $SCRIPTS/register.sh r4090m-fp8ada "$POD" "$COMMITTER"
rm -f /workspace/poseidon-v1/r2.env
echo R4090M_DONE
