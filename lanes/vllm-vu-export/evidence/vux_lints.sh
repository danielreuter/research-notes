#!/usr/bin/env bash
# vux_lints.sh: the by-name lint, the ratchet lints and the exporter's tests, from the shipped tree (research run --cwd source)
set -u
T=$PWD
export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
python -m pytest -q -p no:cacheprovider tests/test_no_by_name_rules.py tests/test_no_dead_modules.py tests/lint tests/pipeline/test_vu_export.py tests/pipeline/test_program_graph.py -rfE 2>&1 | tail -15
