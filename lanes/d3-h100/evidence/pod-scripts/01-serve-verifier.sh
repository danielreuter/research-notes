#!/usr/bin/env bash
# d3-h100 verifier: live_serve.sh from /workspace/src = main 1d9c3198, --target-bits 128 (live_serve default), listening on :7000.
#   vy-d3-h100v  (cpu3c 4 vCPU,  US-MO-1): LIVE_JOBS=4 (default), public tcp://64.247.201.13:16766, rounds 1-2
#   vy-d3-h100v2 (cpu3c 32 vCPU, US-MO-1): LIVE_JOBS=32,          public tcp://64.247.206.95:18347, round 3
LIVE_JOBS=${LIVE_JOBS:-4} bash /workspace/src/backends/direct/ligero/live_serve.sh
