#!/bin/bash
# usage: lints.sh TREE TAG
T=$1; TAG=$2; L=/workspace/a4/logs; mkdir -p $L
cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q -p no:cacheprovider > $L/$TAG-lints.log 2>&1
echo "exit $? $(date -u +%FT%TZ)" >> $L/$TAG-lints.log
tail -3 $L/$TAG-lints.log
