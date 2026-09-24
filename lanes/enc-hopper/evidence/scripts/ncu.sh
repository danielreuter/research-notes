#!/bin/bash
# lane enc-hopper: microbench + Nsight Compute on the encoder and Blake3 kernels (cwd = source tree). Args: extra microbench flags.
set -u
export PATH=/usr/local/cuda/bin:$PATH
export PYTHONPATH=packages/verity/src:backends/numerical/python:backends/shared:.
PY=/workspace/venv312/bin/python
OUT=${OUT:-$RESEARCH_RUN_DIR}
echo "=== microbench (un-profiled)"
$PY "$RESEARCH_RUN_DIR/inputs/microbench.py" --json "$OUT/microbench.json" "$@" 2>&1 | grep -v Warning
echo "=== ncu"
ncu --version | tail -1
ncu --set full --kernel-name "regex:rs_encode|blake3_chunks|blake3_parents" --launch-skip 0 --launch-count 6 \
    --csv --page raw -f -o "$OUT/ncu_profile" $PY "$RESEARCH_RUN_DIR/inputs/microbench.py" --reps 1 "$@" > "$OUT/ncu_stdout.log" 2>&1
echo "ncu rc=$?"
tail -3 "$OUT/ncu_stdout.log"
ncu -i "$OUT/ncu_profile.ncu-rep" --page details --print-units base 2>&1 | grep -E "^\s*(rs_encode|blake3|void|  [A-Z])" | head -400 > "$OUT/ncu_details.txt"
ncu -i "$OUT/ncu_profile.ncu-rep" --page details 2>&1 > "$OUT/ncu_details_full.txt"
wc -l "$OUT"/ncu_details*.txt
echo NCU_DONE
