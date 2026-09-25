#!/bin/bash
# Start `SCRIPT TREE TAG [args]` (a script beside this one) detached, in a fresh copy TREE-TAG of TREE, at most once per TAG: a second
# launch of the same TAG exits at once on the lock.   usage: launch_once.sh SCRIPT TREE TAG [args...]
S=$1; T=$2; TAG=$3; shift 3
mkdir -p /workspace/rff3/locks /workspace/rff3/logs
cd /workspace/rff3 || exit 3
C=$T-$TAG
rm -rf "$C"; cp -a "$T" "$C"
setsid nohup flock -n /workspace/rff3/locks/$TAG.lock "./$S" "$C" "$TAG" "$@" > logs/$TAG.out 2>&1 < /dev/null &
