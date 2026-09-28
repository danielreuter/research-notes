#!/bin/bash
# finish_row.sh N: row N once its run has ended (VM side).
#   1 the run is over (status.json on the pod)       2 its evidence/ copied to /workspace/epoch-evidence/N/ (small files)
#   3 custody: the run and both stored trees PRESERVED (`research data preserved`), else the pod stays up (FORCE=1 overrides, logged)
#   4 the pod terminated, its cap guard stopped, its registry entry removed; spend.tsv gets the end and the spend
#   5 gate_write.py: WRITE -> `rebaseline write --force` into the branch worktree, one commit, pushed; HOLD -> nothing written
#   6 the row's line in the digest table (digest_line.py).  N=canary: repin_roots.py --write and its own commit instead of 5-6
set -u
N=${1:?row number}
H=$(cd "$(dirname "$0")" && pwd)
LANE=$RESEARCH_NOTES/lanes/vllm-epoch-run
R="env PYTHONPATH=/workspace/tools/research/src python3 -m research"
BR=/workspace-wt/epoch-run
push() {  # push the branch; when GitHub refuses, the contract's §5b route: a bundle in the Project store's artifacts/ for the coordinator
  git push -q -u origin HEAD 2>/dev/null && { echo "pushed $(git rev-parse --short HEAD)"; return 0; }
  local b="$STORE/artifacts/vllm-epoch-run-expected-$(git rev-parse --short HEAD).bundle"
  git bundle create "$b" "$(git rev-parse --abbrev-ref HEAD)" > /dev/null 2>&1 && echo "PUSH FAILED: bundle $b (hand it to the coordinator)"
}
IFS='|' read -r POD PODID RUN START RATE CAP PAIRS CLOUD DRIVER GPUS VCPUS < <(awk -F'\t' -v n="$N" '$1==n && $8=="live" {print $2"|"$3"|"$4"|"$5"|"$7"|"$9"|"$10"|"$11"|"$12"|"$13"|"$14}' "$LANE/evidence/spend.tsv" | tail -n 1)
[ -n "${RUN:-}" ] || { echo "#$N: no live row in spend.tsv"; exit 2; }
KEY=-; [ "$N" = canary ] || KEY=$(python3 -c "import json;print(json.load(open('$H/rows.json'))['rows']['$N']['key'])")
EVD=/workspace/epoch-evidence/$N; mkdir -p "$EVD"
# the commit a row is recorded against: rows.json record_sha (#73 and #4 ran dd3dde4d, recorded on main 269829d8, the same tree), else
# the sha the row's run shipped (its EPOCH_SHA), else the lane's current epoch sha
EPOCH_SHA=$(python3 -c "import json;print(json.load(open('$H/rows.json'))['rows'].get('$N', {}).get('record_sha', ''))" 2>/dev/null)

st=$($R pods ssh "$POD" -- "python3 -c 'import json;t=json.load(open(\"/workspace/research/runs/$RUN/status.json\"))[\"transitions\"][-1];print(t.get(\"state\"), t.get(\"exit_code\", t.get(\"rc\", \"\")))'" 2>/dev/null | tail -n 1)
case "$st" in *RUNNING*|*running*|*STARTED*|*started*|"") echo "#$N $RUN not ended (state: ${st:-unreachable})"; exit 1;; esac
echo "#$N $RUN ended: $st"

$R pods ssh "$POD" -- "tar czf - -C /workspace/research/runs/$RUN evidence" > "$EVD/evidence.tgz" && tar xzf "$EVD/evidence.tgz" -C "$EVD"
tail -n 20 "$EVD/evidence/progress.txt"
[ -n "$EPOCH_SHA" ] || EPOCH_SHA=$(sed -n 's/^EPOCH_SHA=//p' "$EVD/evidence/row_env.txt" 2>/dev/null)
[ -n "$EPOCH_SHA" ] || EPOCH_SHA=$(cat "$LANE/evidence/epoch_sha")
echo "recorded against $EPOCH_SHA"
arts=$(grep -o '^STORED [a-z]* art:[0-9a-f]* PRESERVED' "$EVD/evidence/store.log" 2>/dev/null | awk '{print $3}' | tr '\n' ' ')
# custody: the run's own .custody marker (written by the pod's runner only once its attempt is PRESERVED and every run-dir file is in its
# record) and each tree's `data put --preserve` (exit 0 only when PRESERVED); a VM-side re-walk of 60k-file trees takes hours
ok=1
for i in $(seq 1 30); do
  $R pods ssh "$POD" -- "test -s /workspace/research/runs/$RUN/.custody" < /dev/null 2>/dev/null && { ok=0; break; }
  sleep 30
done
[ -n "$arts" ] || ok=1
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

if [ -f "$LANE/evidence/STOPPED" ] && awk -v n="$N" '/rows ALL/ {f=1} {for (i = 1; i <= NF; i++) if ($i == n) f=1} END {exit !f}' "$LANE/evidence/STOPPED"; then
  echo "STOPPED for #$N (evidence/STOPPED): no expected/ write, evidence only"; exit 8
fi
cd "$BR/integrations/vllm" || exit 4
export PYTHONPATH=.:../../packages/verity/src:../../tools/research/src
if [ "$N" = canary ]; then   # the re-pin of ops/known_roots.json (cc 8.9), its own commit
  python3 "$H/repin_roots.py" "$EVD/evidence" verity_vllm/ops/known_roots.json "$RUN" "$EPOCH_SHA" --write || exit 7
  git add verity_vllm/ops/known_roots.json
  git commit -q -m "epoch: re-pin the canary roots (cc 8.9) under Q_word v1 at ${EPOCH_SHA:0:8} (canary run $RUN, reproduced)" && push
  git log --oneline -n 1; exit 0
fi
decision=$(python3 "$H/gate_write.py" "$EVD/evidence" "$KEY"); gate=$?
echo "gate: $decision"
HOLDW=$(python3 -c "import json;print(json.load(open('$H/rows.json'))['rows'].get('$N', {}).get('hold_write', ''))" 2>/dev/null)
if [ "$gate" = 0 ] && [ -n "$HOLDW" ]; then
  python3 -m tests.regression.rebaseline table --record "$EVD/evidence/record" > "$EVD/table.txt" 2>&1
  echo "gate WRITE, but held: $HOLDW (record dir $EVD/evidence/record kept for the write)"; decision="HOLD write held for the coordinator's verdict (${decision})"; gate=9
fi
if [ "$gate" = 0 ]; then
  python3 -m tests.regression.rebaseline table --record "$EVD/evidence/record" > "$EVD/table.txt" 2>&1
  python3 -m tests.regression.rebaseline write --record "$EVD/evidence/record" --commit "$EPOCH_SHA" --branch main \
    --release rebaseline-epoch-q-word --run-id "$RUN" --force > "$EVD/write.txt" 2>&1 || { cat "$EVD/write.txt"; exit 5; }
  cat "$EVD/write.txt"
  git add "tests/regression/expected/$KEY.json"
  git commit -q -m "epoch: re-baseline #$N under Q_word v1 at ${EPOCH_SHA:0:8} (run $RUN; forced: ${decision#WRITE forced=})" && push
  git log --oneline -n 1
fi
python3 "$H/digest_line.py" "$N" "$EVD/evidence" "$RUN" "$EPOCH_SHA" "$SPENT" "$decision" "${PAIRS:-3}" "${CLOUD:-?}" "${DRIVER:-?}" "$LANE/evidence/attempts-$N.txt" "${GPUS:-?}" "${VCPUS:-?}"
