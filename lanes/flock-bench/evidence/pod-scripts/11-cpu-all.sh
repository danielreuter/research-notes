#!/usr/bin/env bash
# flock-bench: setup (01) then the sweep (10) in one recorded run.
set -x
bash "$RESEARCH_RUN_DIR/inputs/01-setup-cpu.sh" || exit 1
bash "$RESEARCH_RUN_DIR/inputs/10-cpu-bench.sh"
