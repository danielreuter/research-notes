#!/usr/bin/env bash
# arith: after 78-dump.sh -- register the given runs (80-register.sh SPECs), then reverify every bench-result that has a
# run-files tree among them.   bash 85-reg-rv.sh ROUND POD_LABEL SPEC...
while pgrep -f "[7]8-dump.sh" >/dev/null; do sleep 5; done
ROUND=$1; shift
n0=$(wc -l < /workspace/arith/registered.txt 2>/dev/null || echo 0)
bash /workspace/arith/scripts/80-register.sh "$@"
arts=$(tail -n +$((n0 + 1)) /workspace/arith/registered.txt | grep -v "tree=none" | grep -o "result=art:[0-9a-f]*" | cut -d= -f2)
echo "reverify $ROUND: $arts"
[ -n "$arts" ] && bash /workspace/arith/scripts/30-reverify.sh $ROUND $arts
tail -30 /workspace/arith/reverify-$ROUND.out
echo DONE-85
