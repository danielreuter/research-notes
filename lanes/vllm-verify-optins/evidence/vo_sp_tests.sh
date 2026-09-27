#!/usr/bin/env bash
# vo_sp_tests.sh: the #106 follow-up (fp8.scale_products) on the shipped tree: its test and #106's, then the integration's lints.
set -u
L=$RESEARCH_RUN_DIR; T=$PWD; EV=$L/evidence; mkdir -p "$EV"
export PATH=/workspace/venv312/bin:$PATH CUDA_VISIBLE_DEVICES=""
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
python -c "import verity_sampled_proofs; print('verity_sampled_proofs importable')"
cd "$T"
python -m pytest integrations/vllm/tests/program/test_fp8_scale_products.py integrations/vllm/tests/program/test_fp8_shared_scale.py -q -p no:cacheprovider \
  -o junit_family=xunit1 --junitxml="$EV/tests.xml" > "$EV/tests.log" 2>&1
echo "tests rc=$? $(tail -1 "$EV/tests.log")"
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
  integrations/vllm/tests/test_no_dead_modules.py -q -p no:cacheprovider > "$EV/lints.log" 2>&1
echo "lints rc=$? $(tail -1 "$EV/lints.log")"
echo "SP-TESTS-DONE $(date -u +%FT%TZ)"
