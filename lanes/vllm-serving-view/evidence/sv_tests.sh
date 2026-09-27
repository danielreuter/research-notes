#!/usr/bin/env bash
# sv_tests.sh: the serving view's tests, program_graph's, the lint ratchets and the CLI tests, from the shipped tree (research run --cwd source)
set -u
T=$PWD
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
python -c "import verity_sampled_proofs, verity_vllm; print('imports', verity_vllm.__file__)"
cd integrations/vllm
python -m pytest -q -p no:cacheprovider tests/pipeline/test_serving_view.py tests/pipeline/test_program_graph.py tests/lint tests/pipeline/test_cli.py \
  tests/check/test_sampled_replay.py -rfE 2>&1 | tail -30
