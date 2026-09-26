#!/usr/bin/env bash
# mt_vocab.sh: wait for $WAIT_RUN, then the vocabulary-range exactness property on a TP2 engine over both GPUs (tests/properties/
# vocab_range_exactness_gpu.py, model ${CASE:-tiny}); the sealed record lands in $RESEARCH_RUN_DIR/evidence.
set -u
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence"
if [ -n "${WAIT_RUN:-}" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
nvidia-smi --query-gpu=index,name,memory.used --format=csv
python tests/properties/vocab_range_exactness_gpu.py --case "${CASE:-tiny}" --out "$OUT/evidence" > "$OUT/vocab.log" 2>&1
echo "vocab rc $? $(date -u +%FT%TZ)"; grep -a "^\[vocab-range\]\|VOCAB-RANGE" "$OUT/vocab.log" | cut -c1-500 | tail -n 20; tail -n 5 "$OUT/vocab.log" | cut -c1-400
python tests/properties/vocab_range_exactness_gpu.py --verify "$OUT/evidence/vocab_range_exactness.json"
echo "MT-VOCAB-DONE $(date -u +%FT%TZ)"
