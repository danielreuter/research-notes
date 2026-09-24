#!/bin/bash
# bx.sh TREE TAG [bitexact args...]  -> /workspace/hp2/out/TAG ; prints the digests
TREE=$1; TAG=$2; shift 2
cd $TREE || exit 2
export PYTHONPATH=packages/verity/src:backends/numerical/python:.
mkdir -p /workspace/hp2/out /workspace/hp2/logs
/workspace/venv312/bin/python /workspace/hp2/bitexact.py --tree $TREE --out /workspace/hp2/out/$TAG "$@" > /workspace/hp2/logs/$TAG.log 2>&1
rc=$?
echo "== $TAG rc=$rc"; grep -v Warning /workspace/hp2/logs/$TAG.log | tail -8
