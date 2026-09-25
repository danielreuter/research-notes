#!/usr/bin/env bash
# Custody of the TP2 pod's runs (launched before --custody-r2): publish each attempt with its run record to the store's remote and
# verify (.custody), with a delete-free key minted on the laptop (store.custody.ACTIONS) and piped into /root/r2cust.env.  The key is
# deleted on exit, whatever happens.   log: /workspace/b2vb/custody.log
set -u
K=/root/r2cust.env
trap 'rm -f $K; unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN' EXIT
[ -s $K ] || { echo "no key at $K"; exit 3; }
set -a; . $K; set +a
export PYTHONPATH=/workspace/research/tool/8c8197e4710d8b90 RESEARCH_STORE=/workspace/research/store \
       RESEARCH_STORE_CONFIG=/workspace/head2/tools/research/store.pod.toml PYTHONDONTWRITEBYTECODE=1
cd /tmp
echo "start $(date -u +%FT%TZ); AWS_* set: $(env | grep -c '^AWS_')"
for r in $(ls /workspace/research/runs); do
  t0=$(date +%s)
  /workspace/venv312/bin/python -m research data custody "$r" --publish --runs-dir /workspace/research/runs 2>&1 | tail -4
  echo "== $r rc=${PIPESTATUS[0]} $(( $(date +%s) - t0 ))s custody-marker=$([ -f /workspace/research/runs/$r/.custody ] && echo yes || echo no)"
done
rm -f $K; unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
echo "key deleted $(date -u +%FT%TZ): $([ -e $K ] && echo STILL-THERE || echo gone)"
/workspace/venv312/bin/python -m research data custody --triage --runs-dir /workspace/research/runs 2>&1 | tail -10
