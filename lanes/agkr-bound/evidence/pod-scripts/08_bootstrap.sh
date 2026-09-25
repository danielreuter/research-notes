#!/usr/bin/env bash
# agkr-bound: bootstrap vy-agkr-bound2 (A100-SXM4-80GB) for the operands-committed work
# research run --on vy-agkr-bound2 --project verity --source . --cwd source --send 08_bootstrap.sh \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/08_bootstrap.sh"'
# /workspace/venv312, rust + /workspace/cargo-target, /workspace/env.sh, the frozen bench-instances/v1 arrays
set -uo pipefail
echo "bootstrap from $(pwd) ($(date -u +%H:%M:%S))"
SRC=$(pwd) BENCH_INSTANCES=1 RELS=bf16-hopper NS=4096 TILE64= bash backends/direct/ligero/pod_bootstrap.sh 2>&1 | tail -40
ls -la /workspace/bench-instances/v1 2>&1 | head -5
echo "== done ($(date -u +%H:%M:%S))"
