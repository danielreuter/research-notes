#!/usr/bin/env bash
# sc_members_run.sh RUN1: sc_members.py served over run RUN1's serving-rows window on the same pod (M0 and the sets as RUN1 unpacked them)
set -u
R1=/workspace/research/runs/$1; ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
T=$PWD; OUT=$RESEARCH_RUN_DIR; IN=$OUT/inputs
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs:/workspace/sc/m0/backends/numerical/python:/workspace/sc/m0/backends/flock/python
mkdir -p "$OUT/evidence"
python "$IN/sc_members.py" served "$R1/serving-rows/$ROW" "$R1/inputs/${PARTITION_FILE:?}" "$OUT/m0-files" $SETS
cp "$OUT/m0-files/members.json" "$OUT/evidence/" 2>/dev/null
echo "SC-DONE $(date -u +%FT%TZ)"
