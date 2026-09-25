#!/usr/bin/env bash
# b-ligero-sha256: pod bootstrap on the synced tree (research pods sync -> /workspace/src).
# research run --on vy-b-ligero-sha256 --project verity --cwd /workspace/src --send 00-bootstrap.sh \
#     --env RELS=fp8-ada-x4 -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/00-bootstrap.sh"'
set -uo pipefail
RELS=${RELS:-fp8-ada-x4} BENCH_INSTANCES=${BENCH_INSTANCES:-1} bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh 2>&1 | tail -40
