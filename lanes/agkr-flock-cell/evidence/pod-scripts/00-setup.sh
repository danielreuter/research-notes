#!/usr/bin/env bash
# agkr-flock-cell: A100 prover pod setup (cwd = the run's source tree). venv + torch + frozen bench-instances/v1
# (pod_bootstrap.sh), a small checker-v2 BabyBear export for the Params-only statement files, the gkr Rust verifier,
# and flock b684b12 with the flock-link patch + live crate (00-setup-cpu.sh, 10-link.sh's install steps).
set -uxo pipefail
SRC=$(pwd)
export SRC BENCH_INSTANCES=1 HEALTH=0
bash backends/direct/ligero/pod_bootstrap.sh 2>&1 | tail -40
source /workspace/env.sh
C=/workspace/cell; mkdir -p $C
[ -f $C/export/circuit.txt ] || $PY -m verity_numerical.gkr_export.vu export --root /workspace/bench-instances/v1 --tier vu-k1536 \
  --lo 0 --hi 8 --out $C/export --field babybear --variant v2 2>&1 | tail -3
ls $C/export
bash backends/flock/pod/00-setup-cpu.sh 2>&1 | tail -5
