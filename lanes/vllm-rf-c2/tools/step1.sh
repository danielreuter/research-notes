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
# one pytest process per side: at this base the two registries cannot share a process
python -m pytest integrations/vllm/tests/program/test_derived_rows.py -q -rA -p no:cacheprovider --junitxml="$OUT/step1-integ-tests.xml"
rc2=$?
python -m pytest packages/verity/tests/ml -q -rA -p no:cacheprovider --junitxml="$OUT/step1-core-tests.xml"
rc3=$?
echo "equality rc=$rc1 integ-tests rc=$rc2 core-tests rc=$rc3"
exit $(( rc1 | rc2 | rc3 ))
