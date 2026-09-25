#!/usr/bin/env bash
# Preserve the run dirs of runs launched before the --custody-r2 rule (their attempts were published without a run record, so
# `data custody --publish` refuses them) as run-files/v1 trees in R2, with this run's minted key (`data put --preserve`, the
# coordinator's 11:46Z recipe).  Prints one `art:` id per run.
#   research run --on POD --project verity --custody-r2 --custody-ttl 2h --send put_runfiles.sh --env RUNS="r... r..." \
#       -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/put_runfiles.sh"'
set -u
R=/workspace/research
C=$R/requests/${RESEARCH_RUN_ID:?}/custody
export RESEARCH_STORE_CONFIG=$C/store.toml
eval "$(python3 -c "import json,shlex;d=json.load(open('$C/cred.json'));print(' '.join(f'export {k}={shlex.quote(d[k])}' for k in ('AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN')))")"
rc=0
for run in ${RUNS:?}; do
  d=$R/runs/$run
  printf '{"lane": "vllm-rf-b1b", "run": "%s", "label": "vllm-rf-b1b run files of %s (launched before --custody-r2)"}\n' \
    "$run" "$run" > $RESEARCH_RUN_DIR/meta-$run.json
  ok=0
  for i in 1 2 3; do
    echo "=== $(date -u +%H:%M:%SZ) put $run ($(du -sh $d | cut -f1)) try $i"
    python3 -m research data put --kind run-files/v1 --tree "$d" --meta @$RESEARCH_RUN_DIR/meta-$run.json --preserve --json \
      > $RESEARCH_RUN_DIR/put-$run.json 2> $RESEARCH_RUN_DIR/put-$run.err && { ok=1; break; }
    tail -3 $RESEARCH_RUN_DIR/put-$run.err
    sleep $((8 * i))
  done
  [ $ok = 1 ] || rc=1
  echo "$run: $(grep -o 'art:[0-9a-f]*' $RESEARCH_RUN_DIR/put-$run.json | sort -u | tr '\n' ' ') $(grep -o '"preserved": [a-z]*' $RESEARCH_RUN_DIR/put-$run.json | sort | uniq -c | tr '\n' ' ')"
done
echo "=== $(date -u +%H:%M:%SZ) end rc=$rc"
exit $rc
