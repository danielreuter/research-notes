#!/usr/bin/env bash
# vux_word_tests.sh: on a bootstrapped pod (venv at /workspace/venv312), from the shipped tree: the ratchet / by-name / dead-module
# lints, the Q_word_v1 tests, the program-graph and manifest tests, and the repo's import-boundary and repository tests
set -u
T=$PWD
export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
python -m pytest -q -p no:cacheprovider tests/test_no_by_name_rules.py tests/test_no_dead_modules.py tests/test_imports_resolve.py tests/lint \
  tests/query tests/pipeline/test_program_graph.py tests/pipeline/test_cli.py tests/pipeline/test_vu_export.py -rfE > $RESEARCH_RUN_DIR/pytest_vllm.log 2>&1; echo "vllm pytest rc $?"; grep -E '^(FAILED|ERROR)| passed| failed' $RESEARCH_RUN_DIR/pytest_vllm.log | tail -15
cd "$T"
python -m pytest -q -p no:cacheprovider packages/verity/tests/test_boundaries.py tests/test_repository.py -rfE > $RESEARCH_RUN_DIR/pytest_root.log 2>&1; echo "root pytest rc $? (test_repository needs a git clone)"; grep -E '^(FAILED|ERROR)| passed| failed' $RESEARCH_RUN_DIR/pytest_root.log | tail -8
