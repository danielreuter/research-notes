#!/bin/bash
# finish_row.sh N: row N once its run has ended (VM side).
#   1 the run is over (status.json on the pod)       2 its evidence/ copied to /workspace/epoch-evidence/N/ (small files)
#   3 custody: the run and both stored trees PRESERVED (`research data preserved`), else the pod stays up (FORCE=1 overrides, logged)
#   4 the pod terminated, its cap guard stopped, its registry entry removed; spend.tsv gets the end and the spend
#   5 gate_write.py: WRITE -> `rebaseline write --force` into the branch worktree, one commit, pushed; HOLD -> nothing written
#   6 the row's line in the digest table (digest_line.py)
set -u
N=${1:?row number}
H=$(cd "$(dirname "$0")" && pwd)
LANE=$RESEARCH_NOTES/lanes/vllm-epoch-run
R="env PYTHONPATH=/workspace/tools/research/src python3 -m research"
BR=/workspace-wt/epoch-run
EPOCH_SHA=$(cat "$LANE/evidence/epoch_sha")
IFS=$'\t' read -r _ POD PODID RUN START _ RATE _ CAP < <(awk -F'\t' -v n="$N" '$1==n && $8=="live"' "$LANE/evidence/spend.tsv" | tail -n 1)
[ -n "${RUN:-}" ] || { echo "#$N: no live row in spend.tsv"; exit 2; }
KEY=$(python3 -c "import json;print(json.load(open('$H/rows.json'))['rows']['$N']['key'])")
EVD=/workspace/epoch-evidence/$N; mkdir -p "$EVD"

st=$($R pods ssh "$POD" -- "python3 -c 'import json;t=json.load(open(\"/workspace/research/runs/$RUN/status.json\"))[\"transitions\"][-1];print(t.get(\"state\"), t.get(\"exit_code\", t.get(\"rc\", \"\")))'" 2>/dev/null | tail -n 1)
case "$st" in *RUNNING*|*running*|*STARTED*|*started*|"") echo "#$N $RUN not ended (state: ${st:-unreachable})"; exit 1;; esac
echo "#$N $RUN ended: $st"

$R pods ssh "$POD" -- "tar czf - -C /workspace/research/runs/$RUN evidence" > "$EVD/evidence.tgz" && tar xzf "$EVD/evidence.tgz" -C "$EVD"
tail -n 20 "$EVD/evidence/progress.txt"
arts=$(grep -o '^STORED [a-z]* art:[0-9a-f]* PRESERVED' "$EVD/evidence/store.log" 2>/dev/null | awk '{print $3}' | tr '\n' ' ')
ok=1
for i in $(seq 1 20); do
  $R data preserved "$RUN" $arts > "$EVD/preserved.txt" 2>&1 && { ok=0; break; }
  sleep 30
done
if [ "$ok" != 0 ]; then
  tail -n 5 "$EVD/preserved.txt"
  [ "${FORCE:-0}" = 1 ] || { echo "#$N: custody not complete; the pod stays up (FORCE=1 terminates, logged)"; exit 3; }
  echo "$(date -u +%FT%TZ) #$N FORCE terminate without complete custody" >> "$LANE/evidence/force.log"
fi
echo "custody: $RUN ${arts:-(no stored trees)} PRESERVED"

$R pods terminate "$PODID"; $R pods guard stop --prefix "$POD-" > /dev/null 2>&1; $R pods unregister "$POD" > /dev/null 2>&1
END=$(date -u +%FT%TZ)
SPENT=$(python3 -c "import datetime as d;f=lambda s:d.datetime.strptime(s,'%Y-%m-%dT%H:%M:%SZ');print(f'{(f(\"$END\")-f(\"$START\")).total_seconds()/3600*$RATE:.2f}')")
python3 - "$LANE/evidence/spend.tsv" "$N" "$RUN" "$END" "$SPENT" <<'EOF'
import sys
p, n, run, end, spent = sys.argv[1:]
rows = [ln.rstrip("\n").split("\t") for ln in open(p)]
for f in rows:
    if f[0] == n and f[3] == run:
        f[5], f[7] = end, spent
open(p, "w").write("".join("\t".join(f) + "\n" for f in rows))
EOF
echo "#$N terminated $END, spent \$$SPENT (cap \$$CAP)"

cd "$BR/integrations/vllm" || exit 4
export PYTHONPATH=.:../../packages/verity/src:../../tools/research/src
decision=$(python3 "$H/gate_write.py" "$EVD/evidence" "$KEY"); gate=$?
echo "gate: $decision"
if [ "$gate" = 0 ]; then
  python3 -m tests.regression.rebaseline table --record "$EVD/evidence/record" > "$EVD/table.txt" 2>&1
  python3 -m tests.regression.rebaseline write --record "$EVD/evidence/record" --commit "$EPOCH_SHA" --branch main \
    --release rebaseline-epoch-q-word --run-id "$RUN" --force > "$EVD/write.txt" 2>&1 || { cat "$EVD/write.txt"; exit 5; }
  cat "$EVD/write.txt"
  git add "tests/regression/expected/$KEY.json"
  git commit -q -m "epoch: re-baseline #$N under Q_word v1 at ${EPOCH_SHA:0:8} (run $RUN; forced: ${decision#WRITE forced=})" && git push -q -u origin HEAD
  git log --oneline -n 1
fi
python3 "$H/digest_line.py" "$N" "$EVD/evidence" "$RUN" "$EPOCH_SHA" "$SPENT" "$decision"
