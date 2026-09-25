#!/usr/bin/env bash
# flock-bench-80gb: the whole A100 line in one recorded run: setup + clmad (00), CPU unit/union/BLAKE3 sweep (10),
# Flock-CUDA BLAKE3 (20), census unit on Flock-CUDA via flock-bench's port (23 -> 22). Each step continues on failure.
set -x
I=$RESEARCH_RUN_DIR/inputs
bash $I/00-setup.sh || exit 1
bash $I/10-cpu.sh
bash $I/20-gpu.sh
bash $I/23-gpu-unit-80gb.sh
