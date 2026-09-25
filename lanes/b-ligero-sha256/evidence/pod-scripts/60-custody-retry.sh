#!/usr/bin/env bash
# b-ligero-sha256: re-publish a finished run's custody (`research data custody RUN --publish`) on the pod when the runner's own
# push failed (e.g. RemoteDisconnected), with the minted key of a still-staged custody dir of this pod (CRED_RUN's).
#   research pods ssh vy-b-ligero-sha256 -- 'nohup bash /workspace/b-ligero-sha256/60-custody-retry.sh RUN CRED_RUN > /workspace/b-ligero-sha256/custody-RUN.log 2>&1 &'
set -u
RUN=$1 CRED_RUN=$2 R=/workspace/research
C=$R/requests/$CRED_RUN/custody
TOOL=$(ls -d $R/tool/*/ | head -1)
export RESEARCH_STORE_CONFIG=$C/store.toml
eval "$(python3 -c "import json,shlex;d=json.load(open('$C/cred.json'));print(' '.join(f'export {k}={shlex.quote(d[k])}' for k in ('AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN')))")"
cd $TOOL && for i in 1 2 3 4; do
  echo "=== $(date -u +%H:%M:%SZ) try $i"
  PYTHONPATH=$TOOL python3 -m research data custody $RUN --publish --runs-dir $R/runs && break
  sleep $((4 * 2 ** i))
done
cat $R/runs/$RUN/.custody
