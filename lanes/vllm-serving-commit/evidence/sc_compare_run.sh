#!/usr/bin/env bash
# sc_compare_run.sh RUN1: run C again over run RUN1's served window on the same pod (sc_compare.py with M0's prover body hoisted).
set -u
R1=/workspace/research/runs/$1; ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
T=$PWD; OUT=$RESEARCH_RUN_DIR; IN=$OUT/inputs
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs:/workspace/sc/m0/backends/numerical/python:/workspace/sc/m0/backends/flock/python
mkdir -p "$OUT/evidence"
python "$IN/sc_compare.py" "$R1/serving-rows/$ROW" /workspace/sc/ropeset "$IN/partition-183680.json" "$OUT/m0-files" "$R1/evidence/on/stages.txt"
cp "$OUT/m0-files/compare.json" "$OUT/evidence/" 2>/dev/null
echo "SC-DONE $(date -u +%FT%TZ)"
