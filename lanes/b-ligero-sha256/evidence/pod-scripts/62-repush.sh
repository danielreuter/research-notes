#!/usr/bin/env bash
# b-ligero-sha256: push finished runs of this pod whose runner custody push failed (RemoteDisconnected) from the runner's own store
# (/workspace/research/store, which holds every blob), with this run's minted custody key; then report `data preserved` per run.
#   research run --on vy-b-ligero-sha256 --project verity --custody-r2 --custody-ttl 2h --send 62-repush.sh \
#       --env RUNS="r... r..." -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/62-repush.sh"'
set -u
R=/workspace/research S=${STORE:-/workspace/research/store}
C=$R/requests/${RESEARCH_RUN_ID:?}/custody
TOOL=$(ls -d $R/tool/*/ | head -1)
export RESEARCH_STORE_CONFIG=$C/store.toml PYTHONPATH=$TOOL
eval "$(python3 -c "import json,shlex;d=json.load(open('$C/cred.json'));print(' '.join(f'export {k}={shlex.quote(d[k])}' for k in ('AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN')))")"
cd $TOOL
rc=0
for run in ${RUNS:?}; do
  for i in 1 2 3; do
    echo "=== $(date -u +%H:%M:%SZ) push $run try $i"
    python3 -m research data push $run --store $S --jobs ${JOBS:-16} --verify head && break
    sleep $((8 * i))
  done
  python3 -m research data preserved $run --store $S; r=$?; echo "preserved $run rc=$r"; [ $r -ne 0 ] && rc=$r
done
exit $rc
