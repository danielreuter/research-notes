#!/usr/bin/env bash
# verify-night: bootstrap the CPU pod (no GPU). CPU torch; the GPU stack / GPU Merkle / health stages fail by design.
# Needed: /workspace/venv312 (torch CPU, numpy, blake3), /workspace/bin/ligero-verify, /workspace/env.sh.
mkdir -p /workspace/verify-night
cd /workspace/src
TORCH=2.6.0+cpu HEALTH=0 nohup bash backends/direct/ligero/pod_bootstrap.sh > /workspace/verify-night/bootstrap.out 2>&1 &
echo started $!
