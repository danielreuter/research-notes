#!/usr/bin/env bash
# integration: bootstrap the 4090 from the synced lane/integration tree
mkdir -p /workspace/integration
RELS=fp8-ada,bf16-hopper,bf16-ampere,fp8-hopper TILE64=fp8-ada,bf16-hopper,bf16-ampere,fp8-hopper BENCH_INSTANCES=1 \
  bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh > /workspace/integration/bootstrap.log 2>&1
echo "BOOTSTRAP_EXIT $?" >> /workspace/integration/bootstrap.log
