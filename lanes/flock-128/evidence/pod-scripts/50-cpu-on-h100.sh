#!/usr/bin/env bash
# flock-128: the CPU union cost run (30-cpu128.sh) on the H100 pod's host, the host flock-bench-80gb used for its CPU
# column. Runs after the GPU runs (the prover is host-bound; never concurrently). env as 30-cpu128.sh.
set -x
I=$RESEARCH_RUN_DIR/inputs
bash $I/00-setup-cpu.sh || exit 1
PROFILES=${PROFILES:-fastx1 fast100x1 fast100x2} bash $I/30-cpu128.sh
