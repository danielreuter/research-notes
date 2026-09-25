#!/usr/bin/env bash
# Publish finished runs of this pod that were launched before the --custody-r2 rule (attempt + run record + every run file) to R2
# with this run's own minted key, then verify them (writes <run>/.custody).  Pattern: b-ligero-sha256's 60-custody-retry.sh / 62-repush.sh.
#   research run --on POD --project verity --custody-r2 --custody-ttl 2h --send custody_publish.sh --env RUNS="r... r..." \
#       -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/custody_publish.sh"'
set -u
R=/workspace/research
C=$R/requests/${RESEARCH_RUN_ID:?}/custody
export RESEARCH_STORE_CONFIG=$C/store.toml
eval "$(python3 -c "import json,shlex;d=json.load(open('$C/cred.json'));print(' '.join(f'export {k}={shlex.quote(d[k])}' for k in ('AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN')))")"
rc=0
for run in ${RUNS:?}; do
  ok=0
  for i in 1 2 3; do
    echo "=== $(date -u +%H:%M:%SZ) custody --publish $run try $i"
    python3 -m research data custody "$run" --publish --runs-dir $R/runs && { ok=1; break; }
    sleep $((8 * i))
  done
  [ $ok = 1 ] || rc=1
  head -c 800 $R/runs/$run/.custody 2>/dev/null; echo
done
echo "=== $(date -u +%H:%M:%SZ) end rc=$rc"
exit $rc
