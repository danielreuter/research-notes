#!/usr/bin/env bash
# agkr-bound: the sigma link on FP8 (fp8-hopper, sha256 row leaves so the Rust link loader can check x/w digests):
# export the fp8-hopper circuit, then 31 builds the commitment (unpinned: drill-down only) and the link and runs every
# negative against both verifiers.
# research run ... --send 37_fp8_link.sh --send 31_link_rust.sh --send 31_link_rust.py \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/37_fp8_link.sh"'
set -uo pipefail
HERE=$(pwd)
ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT/tools/research/src:$ROOT:$HERE"
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
I="$RESEARCH_RUN_DIR/inputs"
S=/workspace/agkr-bound/commit/fp8-hopper-sha256/stmt
echo "== 37 fp8 link, commit ${RESEARCH_SOURCE_COMMIT:-?} ($(date -u +%H:%M:%S))"
rm -rf $S; mkdir -p $S
/workspace/venv312/bin/python -m gpu.v2.export circuits --model hopper_e4m3_wgmma_k32 --out $S > /dev/null || { echo "export failed"; exit 2; }
ls $S
UNPINNED=1 REL=fp8-hopper LEAF=sha256 REPS=${REPS:-3} bash "$I/31_link_rust.sh"
