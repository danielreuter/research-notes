# Lints + the registry-adjacent test files at the shipped head (research run --cwd source).
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
OUT=${RESEARCH_RUN_DIR:-/workspace/c2-quick}
cat .research-source.json 2>/dev/null
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
  -q -p no:cacheprovider --junitxml="$OUT/lints.xml"
rc1=$?
T=integrations/vllm/tests
OMP_NUM_THREADS=2 python -m pytest $T/program/test_registry_one_process.py $T/program/test_nan_conversion.py $T/program/test_derived_rows.py \
  $T/program/test_composition.py $T/program/test_gemm_targets.py $T/program/test_target_profile.py $T/program/test_codec.py \
  $T/program/test_lifted_tiny.py $T/program/test_conformance_record.py $T/program/test_frontend_analyses.py ${EXTRA_TESTS:-} \
  -q -rfEs -p no:cacheprovider -n 8 --dist loadfile --junitxml="$OUT/registry-tests.xml"
rc2=$?
echo "lints rc=$rc1 registry-tests rc=$rc2"
exit $(( rc1 | rc2 ))
