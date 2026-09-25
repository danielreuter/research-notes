# Step 1 on a bootstrapped CPU pod, run from the shipped source root (research run --cwd source).
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
OUT=${RESEARCH_RUN_DIR:-/workspace/c2-step1}
mkdir -p "$OUT"
python -VV
cat .research-source.json 2>/dev/null
sha256sum "$OUT/inputs/equality.py" 2>/dev/null
python "$OUT/inputs/equality.py" "$OUT/equality.json" ${EQ_ARGS:-}
rc1=$?
python -m pytest integrations/vllm/tests/program/test_derived_rows.py packages/verity/tests/ml/test_prims.py -q -rA -p no:cacheprovider \
  --junitxml="$OUT/step1-tests.xml"
rc2=$?
echo "equality rc=$rc1 tests rc=$rc2"
exit $(( rc1 | rc2 ))
