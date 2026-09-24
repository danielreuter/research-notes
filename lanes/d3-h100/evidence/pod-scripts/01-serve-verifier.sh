#!/usr/bin/env bash
# d3-h100 verifier (vy-d3-h100v, cpu3c 4 vCPU US-MO-1): live_serve.sh from /workspace/src = main 1d9c3198, 4 ligero-verify jobs,
# --target-bits 128 (live_serve default), listening on :7000 (public 64.247.201.13:16766).
LIVE_JOBS=4 bash /workspace/src/backends/direct/ligero/live_serve.sh
