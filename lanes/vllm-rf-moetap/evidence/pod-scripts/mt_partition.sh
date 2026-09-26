#!/usr/bin/env bash
# mt_partition.sh: wait for $WAIT_RUN, then partition_report.py (the no-recompute checker on the tapped Definitions at the served shapes).
set -u
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence"
if [ -n "${WAIT_RUN:-}" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
python "$OUT/inputs/partition_report.py" "$OUT/evidence/partition.json" 2>&1 | tee "$OUT/partition.log" | cut -c1-700
echo "MT-PARTITION-DONE $(date -u +%FT%TZ)"
