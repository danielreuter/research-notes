#!/usr/bin/env bash
# poseidon-v1 A100, re-measured with glibc's large-block mmap/trim off (coordinator 1003Z): a fresh sweep a100m-bf16ampere
# (row.sh), capped at the frozen vu-k1536 set's 4096 instances (beyond it a batch repeats instances: bench.views reason I),
# a same-pod malloc-unset A/B at n=4096 (ab.sh), then register (register.sh; needs $PV/r2.env)
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
SCRIPTS=/workspace/poseidon-v1/scripts
GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
CPU=$(lscpu | sed -n 's/^Model name: *//p' | head -1)
POD="vy-poseidon-v1 25b8diy5t3f3tc ($GPU, US, $CPU)"
COMMITTER="main 3301c435 (lane/hash-commit b862be30 Poseidon2 committer + commit-gpu 58b113bc), via lane/poseidon-v1 7ffb7095"
bash $SCRIPTS/row.sh a100m-bf16ampere bf16-ampere 16384 8 4096
bash $SCRIPTS/ab.sh a100m-bf16ampere bf16-ampere 16384 8
RULE_EXTRA="; bounded by the frozen vu-k1536 set's 4096 instances (a larger batch repeats instances, bench.views reason I)" \
  bash $SCRIPTS/register.sh a100m-bf16ampere "$POD" "$COMMITTER"
rm -f /workspace/poseidon-v1/r2.env
echo A100M_DONE
