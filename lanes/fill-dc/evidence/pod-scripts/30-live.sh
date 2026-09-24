#!/usr/bin/env bash
# fill-dc live rounds against the verifier at $LIVE (A100: same-DC cpu3c pod; H100: same-pod, niced), rep 1 dumped.
#   LIVE=tcp://H:P ROUNDS="1 2 3" bash 30-live.sh SPEC...     SPEC = tag:rel:l:p[:extra,comma,separated]; even rounds reversed
# -> runs/<tag>-r<n>/ (t.total_live + the session verdicts in result.json), proofs/ = rep 1 dump.
source /workspace/fill-dc/scripts/lib.sh
export LIVE=${LIVE:?LIVE=tcp://HOST:PORT} DUMP=1
while pgrep -f "scripts/(10-h100|20-a100)-sweep.sh|scripts/11-hash-probe.sh|scripts/12-rounds.sh" >/dev/null; do sleep 5; done
waitgpu
$PY -m backends.direct.ligero.live probe --verifier $LIVE --mb 2 --repeat 4 2>&1 | tail -2 | sed "s/^/$(date -u +%H:%M:%S) probe /" | tee -a $SUM
for r in ${ROUNDS:-1 2 3}; do PREFIX=live round $r "$@"; done
echo "$(date -u +%H:%M:%S) LIVE_DONE" | tee -a $SUM
