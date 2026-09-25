#!/usr/bin/env bash
# b-ligero-sha256: finish a run's custody on the pod when the runner's own push failed (e.g. RemoteDisconnected) but the attempt is
# already published in the pod's store: `research data push RUN` (attempt + outputs + run record + assertions), then
# `research data custody RUN` (verify, writes .custody); with PUBLISH=1, `custody --publish` instead.  Uses the minted key of a
# still-staged custody dir of this pod (CRED_RUN's).  VERIFY=head (default) because sha256 readback GETs of the 70 MB proof
# blobs stalled at ~24 MB from this pod (2026-09-25 11:13-11:35Z).
#   research pods ssh vy-b-ligero-sha256 -- 'nohup bash /workspace/b-ligero-sha256/60-custody-retry.sh RUN CRED_RUN > /workspace/b-ligero-sha256/custody-RUN.log 2>&1 &'
set -u
RUN=$1 CRED_RUN=$2 R=/workspace/research
C=$R/requests/$CRED_RUN/custody
TOOL=$(ls -d $R/tool/*/ | head -1)
export RESEARCH_STORE_CONFIG=$C/store.toml PYTHONPATH=$TOOL
eval "$(python3 -c "import json,shlex;d=json.load(open('$C/cred.json'));print(' '.join(f'export {k}={shlex.quote(d[k])}' for k in ('AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN')))")"
cd $TOOL && for i in 1 2 3 4; do
  echo "=== $(date -u +%H:%M:%SZ) try $i"
  if [ "${PUBLISH:-0}" = 1 ]; then
    python3 -m research data custody $RUN --publish --runs-dir $R/runs && break
  else
    python3 -m research data push $RUN --jobs ${JOBS:-8} --verify ${VERIFY:-head} && python3 -m research data custody $RUN --runs-dir $R/runs && break
  fi
  sleep $((4 * 2 ** i))
done
echo "=== $(date -u +%H:%M:%SZ) end"
cat $R/runs/$RUN/.custody
