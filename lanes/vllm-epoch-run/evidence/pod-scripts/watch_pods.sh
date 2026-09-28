#!/bin/bash
# watch_pods.sh [HOURS]: the VM-side watcher over the lane's live rows (evidence/spend.tsv), once a minute, until HOURS pass (default 9).
# Run it in tmux (`tmux new -d -s epoch-watch bash watch_pods.sh`); the section-1 environment must be exported.
#   fail-fast (coordinator 09:13Z): a pod whose row says "STOP failfast", or shows no "failfast OK" 17 min after its pod start, is
#     terminated: its evidence/ is copied to /workspace/epoch-evidence/N/failfast-<stamp>.tgz first, its cap guard is stopped, its registry
#     entry removed and its ledger line closed (spent = rate x hours).  The row may be relaunched while its latest start holds.
#   status: one line per live row (age, last progress line) in evidence/watch.txt, for the 45-minute checkpoints; ENDed rows are named
#     there for finish_row.sh.
set -u
HOURS=${1:-9}
LANE=$RESEARCH_NOTES/lanes/vllm-epoch-run; L=$LANE/evidence/spend.tsv
R="env PYTHONPATH=/workspace/tools/research/src python3 -m research"
stop_at=$(( $(date +%s) + HOURS * 3600 ))
while [ "$(date +%s)" -lt "$stop_at" ]; do
  # the GO's STOP rule (coordinator 12:15Z): a STOP note in the lane folder terminates every live pod at once (evidence copied first),
  # stops the pollers and leaves evidence/STOPPED, which makes finish_row.sh refuse any expected/ write
  if [ ! -f "$LANE/evidence/STOPPED" ] && { compgen -G "$STORE/internal/lanes/vllm-epoch-run/*STOP*" > /dev/null || compgen -G "$LANE/*STOP*" > /dev/null; }; then
    echo "$(date -u +%FT%TZ) STOP note found: $(ls "$STORE"/internal/lanes/vllm-epoch-run/*STOP* "$LANE"/*STOP* 2>/dev/null | head -n 1)" > "$LANE/evidence/STOPPED"
    for sess in $(tmux -f /exec-daemon/tmux.portal.conf ls -F '#{session_name}' 2>/dev/null | grep '^epoch-poll-'); do tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$sess"; done
    while IFS='|' read -r N POD PODID RUN START RATE; do
      [ -n "$N" ] || continue
      mkdir -p "/workspace/epoch-evidence/$N"
      timeout 120 $R pods ssh "$POD" -- "tar czf - -C /workspace/research/runs/$RUN evidence" > "/workspace/epoch-evidence/$N/stop-$(date -u +%H%MZ).tgz" 2>/dev/null < /dev/null
      $R pods terminate "$PODID" > /dev/null 2>&1 < /dev/null; $R pods guard stop --prefix "$POD-" > /dev/null 2>&1; $R pods unregister "$POD" > /dev/null 2>&1
      echo "$(date -u +%FT%TZ) #$N $POD $RUN: TERMINATED on STOP (records discarded, evidence kept)" | tee -a "$LANE/evidence/STOPPED" >> "$LANE/evidence/watch.log"
    done < <(awk -F'\t' '$8=="live" {print $1"|"$2"|"$3"|"$4"|"$5"|"$7}' "$L" 2>/dev/null)
  fi
  out=""
  while IFS='|' read -r N POD PODID RUN START RATE; do
    [ -n "$N" ] || continue
    age=$(( $(date +%s) - $(date -d "$START" +%s) ))
    prog=$($R pods ssh "$POD" -- "tail -n 40 /workspace/research/runs/$RUN/evidence/progress.txt 2>/dev/null" 2>/dev/null < /dev/null)
    last=$(echo "$prog" | grep -v '^$' | tail -n 1 | cut -c1-160)
    if echo "$prog" | grep -q "STOP failfast" || { [ "$age" -gt 1020 ] && ! echo "$prog" | grep -q "failfast OK"; }; then
      mkdir -p "/workspace/epoch-evidence/$N"
      $R pods ssh "$POD" -- "tar czf - -C /workspace/research/runs/$RUN evidence" > "/workspace/epoch-evidence/$N/failfast-$(date -u +%H%MZ).tgz" 2>/dev/null < /dev/null
      $R pods terminate "$PODID" > /dev/null 2>&1 < /dev/null; $R pods guard stop --prefix "$POD-" > /dev/null 2>&1; $R pods unregister "$POD" > /dev/null 2>&1
      END=$(date -u +%FT%TZ)
      python3 - "$L" "$N" "$RUN" "$END" "$RATE" "$START" <<'EOF'
import datetime as dt, sys
p, n, run, end, rate, start = sys.argv[1:]
f = lambda s: dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
rows = [ln.rstrip("\n").split("\t") for ln in open(p)]
for r in rows:
    if r[0] == n and r[3] == run:
        r[5], r[7] = end, f"{(f(end) - f(start)).total_seconds() / 3600 * float(rate):.2f}"
open(p, "w").write("".join("\t".join(r) + "\n" for r in rows))
EOF
      echo "$END #$N $POD $RUN: fail-fast TERMINATED at $((age / 60)) min ($last)" | tee -a "$LANE/evidence/attempts-$N.txt" >> "$LANE/evidence/watch.log"
      continue
    fi
    state=live; echo "$prog" | grep -q " END$" && state=ENDED
    out+="#$N $POD $RUN $state $((age / 60)) min: $last"$'\n'
  done < <(awk -F'\t' '$8=="live" {print $1"|"$2"|"$3"|"$4"|"$5"|"$7}' "$L" 2>/dev/null)
  printf '%s updated %s\n%s' "watch" "$(date -u +%FT%TZ)" "$out" > "$LANE/evidence/watch.txt"
  sleep 60
done
