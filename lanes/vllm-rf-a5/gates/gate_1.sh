#!/bin/bash
# gate 1 (lints, by-name, imports) and the research store's vllm Tool tests, from the tree root, in venv312.
#   usage: gate_1.sh TREE TAG      logs: /workspace/a5/logs/TAG.{log,xml}
T=$1; TAG=$2; shift 2
L=/workspace/a5/logs; mkdir -p $L
cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf
export PYTHONDONTWRITEBYTECODE=1
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
  integrations/vllm/tests/test_no_dead_modules.py -q -o junit_family=xunit1 --junitxml=$L/$TAG-lint.xml > $L/$TAG-lint.log 2>&1
r1=$?
python -m pytest tools/research/tests/test_store_vllm_tools.py -q -o junit_family=xunit1 --junitxml=$L/$TAG-tools.xml > $L/$TAG-tools.log 2>&1
r2=$?
tail -3 $L/$TAG-lint.log; tail -3 $L/$TAG-tools.log
echo "lint rc=$r1 tools rc=$r2"
[ $r1 = 0 ] && [ $r2 = 0 ]
