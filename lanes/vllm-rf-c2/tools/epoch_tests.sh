# The epoch tree's lints and gate (b) suite (head side only; compared with the pre-epoch head's gate_b-head.xml).
# Run with an absolute --cwd at the synced tree; copies it fresh (the suites write under the tree).
#   usage: epoch_tests.sh [PYTEST_ARGS ...]     (default: the whole integration suite, gate (b) flags)
OUT=${RESEARCH_RUN_DIR:-/workspace/c2/epoch_tests}; mkdir -p "$OUT"
W=/workspace/c2/gb-epoch; rm -rf $W; mkdir -p $W
cp -a "$PWD" $W/epoch
find $W -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
cat .research-source.json 2>/dev/null
T=$W/epoch; cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=3
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|MKL_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > "$OUT/epoch.env"
echo "start lints $(date -u +%FT%TZ)"
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
  -q -o junit_family=xunit1 --junitxml="$OUT/lints-epoch.xml" > "$OUT/lints-epoch.log" 2>&1
echo "lints rc=$? $(tail -1 $OUT/lints-epoch.log)"
echo "start suite $(date -u +%FT%TZ)"
if [ $# -gt 0 ]; then
  python -m pytest "$@" -ra -o junit_family=xunit1 --junitxml="$OUT/suite-epoch.xml" > "$OUT/suite-epoch.log" 2>&1
else
  python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile -o junit_family=xunit1 --junitxml="$OUT/suite-epoch.xml" \
    > "$OUT/suite-epoch.log" 2>&1
fi
echo "suite rc=$? $(date -u +%FT%TZ)"
tail -3 "$OUT/suite-epoch.log"
exit 0
