#!/usr/bin/env bash
# arith: bounded `research data preserved` of every art in registered.txt + the reverify verdicts of ROUND (pod side).
#   bash 86-preserved.sh ROUND
source /workspace/env.sh
set -a; source /workspace/arith/.cred; set +a
arts=$( (cat /workspace/arith/registered.txt; grep -o "verdict art:[0-9a-f]*" /workspace/arith/reverify-$1.out) | grep -o "art:[0-9a-f]\{64\}" | sort -u)
echo "$(echo $arts | wc -w) arts"
for i in 1 2 3; do
  timeout 240 $PY -m research data preserved $arts > /workspace/arith/preserved-$1.out 2>&1; rc=$?
  echo "preserved $1 try $i rc=$rc: $(tail -1 /workspace/arith/preserved-$1.out)" | tee -a /workspace/arith/runs.txt
  [ $rc = 0 ] && break
done
