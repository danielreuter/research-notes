#!/usr/bin/env bash
# vux_tests.sh: the exporter's tests + the lint ratchets + the replay tests it touches, from the shipped tree (research run --cwd source)
set -u
T=$PWD
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
python -m pytest -q -p no:cacheprovider tests/pipeline/test_vu_export.py tests/lint tests/check/test_sampled_replay.py \
  tests/check/test_sampled_replay_aliased_module.py tests/pipeline/test_cli.py -rfE 2>&1 | tail -40
