#!/bin/bash
# Publish finished run dirs to the store remote (R2) with the laptop-minted, delete-free key in /root/r2cu.env, then delete the key.
# Never prints the key.   usage: custody.sh RUN_ID...     log: /workspace/b4/logs/custody.log
T=/workspace/head-reg
L=/workspace/b4/logs
trap 'rm -f /root/r2cu.env' EXIT
[ -e /root/r2cu.env ] || { echo "no /root/r2cu.env"; exit 4; }
set -a; . /root/r2cu.env; set +a
export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$T/tools/research/src PYTHONDONTWRITEBYTECODE=1
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
rc=0
for R in "$@"; do
  echo "start $R $(date -u +%FT%TZ)"
  python -m research.cli data custody "$R" --publish --runs-dir /workspace/research/runs || rc=1
done
rm -f /root/r2cu.env
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
echo "done $(date -u +%FT%TZ) rc=$rc key_deleted=$([ -e /root/r2cu.env ] && echo no || echo yes)"
exit $rc
