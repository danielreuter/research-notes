#!/usr/bin/env bash
# verify-po: bootstrap the CPU pod (no GPU) from /workspace/src (research pods sync of lane/verify-po = main ab9573fd).
# CPU torch; the GPU stack / GPU Merkle / health stages fail by design on a CPU pod.
# Leaves: /workspace/venv312, /workspace/bin/ligero-verify (cargo --release of backends/ligero-verify), /workspace/env.sh.
#   research run --on vy-verify-po --project verity --cwd /workspace/src --send 01-bootstrap.sh -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/01-bootstrap.sh"'
mkdir -p /workspace/verify-po
cd /workspace/src
TORCH=2.6.0+cpu HEALTH=0 bash backends/direct/ligero/pod_bootstrap.sh 2>&1 | tee /workspace/verify-po/bootstrap.out
ls -la /workspace/bin/ligero-verify && sha256sum /workspace/bin/ligero-verify
