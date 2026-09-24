#!/bin/bash
# Start `gate_a_t01.sh TREE TAG [pytest args]` detached, at most once per TAG: a second launch of the same TAG (the research ssh wrapper
# can re-run a command) exits at once on the lock.   usage: launch_once.sh TREE TAG [pytest args...]
T=$1; TAG=$2; shift 2
mkdir -p /workspace/rff3/locks /workspace/rff3/logs
cd /workspace/rff3 || exit 3
setsid nohup flock -n /workspace/rff3/locks/$TAG.lock ./gate_a_t01.sh "$T" "$TAG" "$@" > logs/$TAG.out 2>&1 < /dev/null &
