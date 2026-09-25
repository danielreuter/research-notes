#!/bin/bash
# lints + gate (b) from the tree in $PWD (research run --cwd source).  usage: gate_b.sh TAG   logs: /workspace/a5c/logs/TAG-{lints,gate_b}.{log,xml}
TAG=$1; L=/workspace/a5c/logs; mkdir -p $L
T=$PWD
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITOR_REPO AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
echo "tree $T rev $(cat .research-source-rev 2>/dev/null)"
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q -ra -o junit_family=xunit1 --junitxml=$L/$TAG-lints.xml > $L/$TAG-lints.log 2>&1
echo "lints rc=$? $(tail -1 $L/$TAG-lints.log)"
OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile -o junit_family=xunit1 --junitxml=$L/$TAG-gate_b.xml > $L/$TAG-gate_b.log 2>&1
echo "gate_b rc=$? $(tail -1 $L/$TAG-gate_b.log)"
