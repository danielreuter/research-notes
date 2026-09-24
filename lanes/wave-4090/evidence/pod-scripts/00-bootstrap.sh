#!/usr/bin/env bash
# wave-4090: bootstrap the 4090 prover from the synced lane/wave-4090 tree (main 24f252b1)
mkdir -p /workspace/wave-4090
cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us /sys/fs/cgroup/cpu/cpu.cfs_period_us > /workspace/wave-4090/cpu_quota.txt 2>&1
RELS=fp8-ada,fp8-ada-v3,fp8-ada-v3x4 TILE64=fp8-ada \
  bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh > /workspace/wave-4090/bootstrap.log 2>&1
echo "BOOTSTRAP_EXIT $?" >> /workspace/wave-4090/bootstrap.log
