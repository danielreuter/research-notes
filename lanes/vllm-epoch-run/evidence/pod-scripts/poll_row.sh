#!/bin/bash
# poll_row.sh N UNTIL_UTC: launch_row.sh N once a minute until it launches (exit 0) or UNTIL_UTC (the row's latest start) passes.
# No stock (exit 5) retries; any other refusal stops the poller and is logged.  Log: evidence/poll-N.log.  Run in tmux (epoch-poll-N).
set -u
N=${1:?row}; UNTIL=$(date -d "${2:?latest start, e.g. 2026-09-28T14:30Z}" +%s)
H=$(cd "$(dirname "$0")" && pwd); LOG=$RESEARCH_NOTES/lanes/vllm-epoch-run/evidence/poll-$N.log
echo "$(date -u +%FT%TZ) polling #$N until $2" >> "$LOG"
while [ "$(date +%s)" -lt "$UNTIL" ]; do
  bash "$H/launch_row.sh" "$N" > "$LOG.last" 2>&1; rc=$?
  case "$rc" in
    0) cat "$LOG.last" >> "$LOG"; echo "$(date -u +%FT%TZ) #$N LAUNCHED" >> "$LOG"; exit 0;;
    5) echo "$(date -u +%FT%TZ) no shape: $(grep -o 'NO SHAPE.*\|NO STOCK.*' "$LOG.last" | head -n 1 | cut -c1-120)" >> "$LOG"; sleep 60;;
    *) if grep -q "REFUSED: #$N balance test\|REFUSED: #$N estimate .* does not fit the" "$LOG.last"; then   # money frees, cheaper offers appear: retry
         echo "$(date -u +%FT%TZ) balance: $(grep -o 'balance test.*' "$LOG.last" | head -n 1 | cut -c1-160)" >> "$LOG"; sleep 120; continue
       fi
       cat "$LOG.last" >> "$LOG"; echo "$(date -u +%FT%TZ) #$N refused rc=$rc: poller stops" >> "$LOG"; exit "$rc";;
  esac
done
echo "$(date -u +%FT%TZ) #$N latest start $2 passed with no shape: deferred, old record kept" >> "$LOG"
exit 5
