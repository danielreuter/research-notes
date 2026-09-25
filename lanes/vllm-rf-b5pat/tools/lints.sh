#!/bin/bash
# lints: python -m pytest integrations/vllm/tests/lint tests/test_no_by_name_rules.py tests/test_imports_resolve.py -q, from the tree root,
# in venv312.
#   usage: lints.sh TREE TAG      logs: /workspace/b5pat/logs/TAG.{log,xml}
T=$1; TAG=$2
L=/workspace/b5pat/logs; mkdir -p $L
cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf
export PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITOR_REPO
echo "start $(date -u +%FT%TZ) tree $T"
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q -ra \
  -p no:cacheprovider -o junit_family=xunit1 --junitxml=$L/$TAG.xml > $L/$TAG.log 2>&1
rc=$?
echo "exit $rc $(date -u +%FT%TZ)"
echo "exit $rc $(date -u +%FT%TZ)" >> $L/$TAG.log
tail -5 $L/$TAG.log
exit $rc
