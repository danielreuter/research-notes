#!/bin/bash
# rebase2.sh RUNID KEXPR: rebaseline.py run (T0,T1,T2) with the recorded rows as the v2 CANDIDATE (VERITY_REGRESSION_CANDIDATE =
# the recording run's sweep) against the prefetched fixtures in the pod store (no key: waits until prefetch deleted it); then table.
SW=/workspace/research/runs/$1/sweep
for i in $(seq 1 240); do [ -e /root/r2ro.env ] || pgrep -f "inputs/prefetch.sh" > /dev/null || break; sleep 15; done
[ -e /root/r2ro.env ] && { echo "key still present: refusing"; exit 4; }
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
PY=/workspace/venv312/bin/python
export PYTHONPATH=.:../../packages/verity/src:../../tools/research/src VERITY_REGRESSION_CANDIDATE=$SW
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=../../tools/research/store.pod.toml
$PY -m tests.regression.rebaseline run --record $RESEARCH_RUN_DIR/record --tier T0,T1,T2 -- -k "$2" -ra > $RESEARCH_RUN_DIR/run.log 2>&1
echo "run rc=$?"
$PY -m tests.regression.rebaseline table --record $RESEARCH_RUN_DIR/record > $RESEARCH_RUN_DIR/table.txt 2>&1; echo "table rc=$?"
grep -E "passed|failed" $RESEARCH_RUN_DIR/run.log | tail -1
