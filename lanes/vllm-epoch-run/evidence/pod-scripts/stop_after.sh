#!/bin/bash
# stop_after.sh N build|match [DEADLINE_UTC]: end row N's run after its Build (the Match never runs) or after its Match (the Commit never runs), for a
#   row whose Commit cannot finish by the epoch's line (vLLM coordinator 20:44Z: #74 after its Build; #67, #68 after a Match for the GM
#   evidence).  Polls the run's progress once a minute (VM side).  At `build rc=0` a side store of the Build (side_store.sh, once); when
#   the next stage starts (build: `required_families:`, the Match follows; match: `strict word check rc=`, the Commit follows) it stops
#   that stage's `verity_vllm.pipeline.cli row run` and every descendant.  The row's run then stores its Build and records with its own
#   key and ends (`finish`), and finish_row.sh N takes it from there.  Log: evidence/stop-after-N.log.  Run in tmux (epoch-stop-N).
#   DEADLINE_UTC (match mode): a Match still running then is stopped too, so the run's own store ends inside the row's cap.
set -u
N=${1:?row}; AFTER=${2:?build|match}; DEADLINE=${3:-}; H=$(cd "$(dirname "$0")" && pwd); LANE=$RESEARCH_NOTES/lanes/vllm-epoch-run
R="env PYTHONPATH=/workspace/tools/research/src python3 -m research"
LOG=$LANE/evidence/stop-after-$N.log
IFS='|' read -r POD RUN < <(awk -F'\t' -v n="$N" '$1==n && $8=="live" {print $2"|"$4}' "$LANE/evidence/spend.tsv" | tail -n 1)
[ -n "${RUN:-}" ] || { echo "#$N: no live row" | tee -a "$LOG"; exit 2; }
case "$AFTER" in
  build) TRIGGER='required_families:'; STAGE=match;;
  match) TRIGGER='strict word check rc='; STAGE=commit;;
  *) echo "after build or match, not $AFTER"; exit 2;;
esac
say() { echo "$(date -u +%FT%TZ) #$N $*" >> "$LOG"; }
say "armed: stop the $STAGE stage once progress shows '$TRIGGER' ($POD $RUN)"
stored=0
while :; do
  prog=$($R pods ssh "$POD" -- "cat /workspace/research/runs/$RUN/evidence/progress.txt" < /dev/null 2>/dev/null)
  if [ -z "$prog" ]; then sleep 60; continue; fi
  if echo "$prog" | grep -q ' END$'; then say "run ended before the trigger"; exit 0; fi
  if [ "$stored" = 0 ] && [ "$AFTER" = match ] && echo "$prog" | grep -q 'build rc=0' && [ ! -f "$LANE/evidence/side-store-$N.txt" ]; then
    say "build rc=0: side store of the Build"; bash "$H/side_store.sh" "$N" > "$LANE/evidence/side-store-$N.txt" 2>&1 < /dev/null; stored=1
  fi
  if [ -n "$DEADLINE" ] && [ "$AFTER" = match ] && [ "$(date +%s)" -gt "$(date -d "$DEADLINE" +%s)" ] && ! echo "$prog" | grep -q "$TRIGGER" \
     && echo "$prog" | grep -q 'required_families:'; then
    say "deadline $DEADLINE passed with the Match still running: stopping the match stage so the store fits the cap"
    TRIGGER='required_families:'; STAGE=match
  fi
  if echo "$prog" | grep -q "$TRIGGER"; then
    say "trigger seen: $(echo "$prog" | grep "$TRIGGER" | tail -n 1 | cut -c1-160)"
    for i in 1 2 3 4 5; do
      out=$($R pods ssh "$POD" -- "p=\$(pgrep -f 'pipeline[.]cli row run .* --stages $STAGE' | head -n 1); [ -n \"\$p\" ] || { echo none; exit 0; }
all=\$p; q=\$p; while [ -n \"\$q\" ]; do q=\$(for x in \$q; do pgrep -P \$x; done | tr '\n' ' '); all=\"\$all \$q\"; done
kill -TERM \$all 2>/dev/null; sleep 15; kill -KILL \$all 2>/dev/null; echo \"stopped \$p (\$(echo \$all | wc -w) processes)\"" < /dev/null 2>/dev/null | tail -n 1)
      say "$STAGE stage: ${out:-unreachable}"
      case "$out" in stopped*) exit 0;; none) sleep 20;; *) sleep 30;; esac
    done
    say "the $STAGE stage never appeared after the trigger: look at the pod"; exit 3
  fi
  sleep 60
done
