#!/bin/bash
# usage: runcheck.sh POD_NAME RUN_ID [RUN_ID...]   -> one line per run: RUNNING | DONE <last state> | MISSING
# POD_NAME is the vyv-rf-* machine name; ip/port come from `research pods list`.
cd /workspace
POD=$1; shift
line=$(PYTHONPATH=tools/research/src timeout 60 python3 -m research pods list 2>/dev/null | grep " $POD-" | head -1)
ip=$(echo "$line" | sed -n "s/.*ip=\([0-9.]*\).*/\1/p"); port=$(echo "$line" | sed -n "s/.*'22': \([0-9]*\).*/\1/p")
[ -z "$ip" ] && { for r in "$@"; do echo "$POD $r POD-GONE"; done; exit 0; }
for r in "$@"; do
  out=$(ssh -n -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15 -o BatchMode=yes \
    -i ~/.runpod/ssh/runpodctl-ssh-key -p "$port" root@"$ip" "
      d=/workspace/research/runs/$r
      [ -d \$d ] || { echo MISSING; exit; }
      if pgrep -f -- '[-]-id $r' >/dev/null; then echo RUNNING; else
        s=\$(python3 -c \"import json;t=json.load(open('\$d/status.json'))['transitions'][-1];print(t.get('state'),t.get('exit_code',t.get('rc','')))\" 2>/dev/null)
        echo DONE \$s; fi" 2>/dev/null | grep -v setlocale)
  echo "$POD $r ${out:-UNREACHABLE}"
done
