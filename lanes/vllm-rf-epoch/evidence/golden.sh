#!/bin/bash
# golden.sh: re-record the golden corpus's two entries at the shipped tree (cwd = source/integrations/vllm), then --check.
# Out: $RESEARCH_RUN_DIR/golden/{corpus.json,record-*.json,check.json}
set -u
O=$RESEARCH_RUN_DIR/golden; mkdir -p $O
PY=/workspace/venv312/bin/python
export PYTHONPATH=.:../../packages/verity/src:../../tools/research/src
cp verity_vllm/properties/golden/corpus.json $O/corpus.before.json
$PY -m verity_vllm.properties.golden --record smollm2-135m-m1 --log data/logs/m1.jsonl.gz --profile vllm_d9105ea80_sm89_eager \
  --decision "epoch (vllm-rf-epoch): Programs cite core AmpereBF16TcDot16_v2" > $O/record-m1.json 2> $O/record-m1.err; echo "m1 rc $?"
$PY -m verity_vllm.properties.golden --record qwen2.5-1.5b-m6 --log data/logs/m6/log.jsonl.gz --profile vllm_d9105ea80_sm89_eager_qwen15 \
  --decision "epoch (vllm-rf-epoch): Programs cite core AmpereBF16TcDot16_v2" > $O/record-m6.json 2> $O/record-m6.err; echo "m6 rc $?"
cp verity_vllm/properties/golden/corpus.json $O/corpus.json
$PY -m verity_vllm.properties.golden --check --out $O/check.json; echo "check rc $?"
