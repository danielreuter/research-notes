#!/usr/bin/env bash
# wave-a100: bootstrap the A100 prover from the synced lane/wave-a100 tree (= main 24f252b1)
# bf16-ampere (v1) reads the frozen bench-instances/v1 set (BENCH_INSTANCES=1); v3 / v3x4 the synthetic Ampere set (RELS);
# +shared needs the 64x64 tiles of bf16-ampere (TILE64). VERIFIER = the same-DC live verifier pod (vy-wave-a100-verifier).
mkdir -p /workspace/wave-a100
RELS=bf16-ampere,bf16-ampere-v3,bf16-ampere-v3x4 TILE64=bf16-ampere BENCH_INSTANCES=1 NS=4096 \
  VERIFIER=${VERIFIER:-} \
  bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh > /workspace/wave-a100/bootstrap.log 2>&1
echo "BOOTSTRAP_EXIT $?" >> /workspace/wave-a100/bootstrap.log
