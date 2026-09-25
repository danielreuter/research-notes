#!/usr/bin/env bash
# gate_b.sh TAG: lints then gate (b) from the current tree (research run --cwd source); XMLs kept in /workspace/b4c/TAG
set -u
TAG=$1; OUT=/workspace/b4c/$TAG; mkdir -p "$OUT"
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
{ echo "tree $PWD"; cat .research-source.json 2>/dev/null; env | grep -E '^(PATH|PYTHONPATH|HF_HOME)='; } > "$OUT/env.txt"
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q \
  -o junit_family=xunit1 --junitxml="$OUT/lints.xml" > "$OUT/lints.log" 2>&1; echo "lints rc $?" | tee -a "$OUT/rc.txt"
tail -n 3 "$OUT/lints.log"
OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile \
  -o junit_family=xunit1 --junitxml="$OUT/gate_b.xml" > "$OUT/gate_b.log" 2>&1; echo "gate_b rc $?" | tee -a "$OUT/rc.txt"
tail -n 3 "$OUT/gate_b.log"
exit 0
