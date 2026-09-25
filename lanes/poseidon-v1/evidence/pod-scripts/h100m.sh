#!/usr/bin/env bash
# poseidon-v1 H100, re-measured with glibc's large-block mmap/trim off (coordinator 1003Z): fresh sweeps h100m-bf16hopper and
# h100m-fp8hopper (row.sh each), a same-pod malloc-unset A/B at n=4096 and each plateau (ab.sh), then register both sweeps
# (register.sh; needs $PV/r2.env)
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
SCRIPTS=/workspace/poseidon-v1/scripts
GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
CPU=$(lscpu | sed -n 's/^Model name: *//p' | head -1)
POD="vy-poseidon-v1 h94xn599m62w1t ($GPU, US, $CPU)"
COMMITTER="main 3301c435 (lane/hash-commit b862be30 Poseidon2 committer + commit-gpu 58b113bc), via lane/poseidon-v1 7ffb7095"
bash $SCRIPTS/row.sh h100m-bf16hopper bf16-hopper 16384 8 1048576
bash $SCRIPTS/row.sh h100m-fp8hopper fp8-hopper 16384 8 1048576
bash $SCRIPTS/ab.sh h100m-bf16hopper bf16-hopper 16384 8
bash $SCRIPTS/ab.sh h100m-fp8hopper fp8-hopper 16384 8
bash $SCRIPTS/register.sh h100m-bf16hopper "$POD" "$COMMITTER"
bash $SCRIPTS/register.sh h100m-fp8hopper "$POD" "$COMMITTER"
rm -f /workspace/poseidon-v1/r2.env
echo H100M_DONE
