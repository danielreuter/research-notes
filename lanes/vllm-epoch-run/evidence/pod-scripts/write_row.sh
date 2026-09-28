#!/bin/bash
# write_row.sh N: row N's `expected/` write from its evidence on the VM (/workspace/epoch-evidence/N/evidence, as finish_row.sh left
#   it), then its line in the digest table.  gate_write.py: WRITE -> `rebaseline write --force` into the branch worktree, one commit,
#   pushed; HOLD, or a row whose rows.json `hold_write` is set -> nothing written.  A pending coverage result (the harness misses the
#   `norm_scales` family the Commit covered; coordinator 20:14Z) is moved to pending/ first, so `write` keeps its previous contract and
#   lists it until checks/coverage.py is fixed and coverage is backfilled from the stored trees.  finish_row.sh runs this once the pod
#   is gone; run it by hand for a row whose hold was lifted.
set -u
N=${1:?row number}
H=$(cd "$(dirname "$0")" && pwd)
LANE=$RESEARCH_NOTES/lanes/vllm-epoch-run
BR=/workspace-wt/epoch-run
push() {  # push the branch; when GitHub refuses, the contract's §5b route: a bundle in the Project store's artifacts/ for the coordinator
  git push -q -u origin HEAD 2>/dev/null && { echo "pushed $(git rev-parse --short HEAD)"; return 0; }
  local b="$STORE/artifacts/vllm-epoch-run-expected-$(git rev-parse --short HEAD).bundle"
  git bundle create "$b" "$(git rev-parse --abbrev-ref HEAD)" > /dev/null 2>&1 && echo "PUSH FAILED: bundle $b (hand it to the coordinator)"
}
cov_line() {  # the Commit's own coverage of record, quoted in a pending write's commit (vLLM coordinator 20:17Z)
  python3 - "$1/row/verdict.json" <<'EOF'
import json, sys
c = next(c for c in json.load(open(sys.argv[1]))["checks"] if c["name"] == "required_value_coverage/manifest_coverage")
s = c.get("scope") or {}
print(f"the Commit's own: \"required_value_coverage/manifest_coverage {c.get('outcome')}: checked {s.get('checked')}, missing {len(c.get('differences') or [])}, "
      f"norm_scales {(s.get('checked_by_family') or {}).get('norm_scales')} checked\"")
EOF
}
IFS='|' read -r RUN SPENT PAIRS CLOUD DRIVER GPUS VCPUS < <(awk -F'\t' -v n="$N" '$1==n {print $4"|"$8"|"$10"|"$11"|"$12"|"$13"|"$14}' "$LANE/evidence/spend.tsv" | tail -n 1)
[ -n "${RUN:-}" ] || { echo "#$N: not in spend.tsv"; exit 2; }
[ "$SPENT" = live ] && { echo "#$N $RUN is still live: finish_row.sh first"; exit 2; }
KEY=$(python3 -c "import json;print(json.load(open('$H/rows.json'))['rows']['$N']['key'])")
EVD=/workspace/epoch-evidence/$N
[ -d "$EVD/evidence" ] || { echo "#$N: no evidence under $EVD"; exit 2; }
EPOCH_SHA=$(python3 -c "import json;print(json.load(open('$H/rows.json'))['rows'].get('$N', {}).get('record_sha', ''))" 2>/dev/null)
[ -n "$EPOCH_SHA" ] || EPOCH_SHA=$(sed -n 's/^EPOCH_SHA=//p' "$EVD/evidence/row_env.txt" 2>/dev/null)
[ -n "$EPOCH_SHA" ] || EPOCH_SHA=$(cat "$LANE/evidence/epoch_sha")

if [ -f "$LANE/evidence/STOPPED" ] && awk -v n="$N" '/rows ALL/ {f=1} {for (i = 1; i <= NF; i++) if ($i == n) f=1} END {exit !f}' "$LANE/evidence/STOPPED"; then
  echo "STOPPED for #$N (evidence/STOPPED): no expected/ write, evidence only"; exit 8
fi
cd "$BR/integrations/vllm" || exit 4
export PYTHONPATH=.:../../packages/verity/src:../../tools/research/src
decision=$(python3 "$H/gate_write.py" "$EVD/evidence" "$KEY"); gate=$?
echo "gate: $decision"
HOLDW=$(python3 -c "import json;print(json.load(open('$H/rows.json'))['rows'].get('$N', {}).get('hold_write', ''))" 2>/dev/null)
if [ "$gate" = 0 ] && [ -n "$HOLDW" ]; then
  python3 -m tests.regression.rebaseline table --record "$EVD/evidence/record" > "$EVD/table.txt" 2>&1
  echo "gate WRITE, but held: $HOLDW (record dir $EVD/evidence/record kept for the write)"; decision="HOLD write held for the coordinator's verdict (${decision})"; gate=9
fi
if [ "$gate" = 0 ]; then
  note=""
  if [[ "$decision" == *pending=coverage* ]]; then
    mkdir -p "$EVD/pending" && mv "$EVD/evidence/record/$KEY/coverage.json" "$EVD/pending/" && echo "coverage.json -> $EVD/pending/ (pending the harness fix)"
    note="; coverage pending the coverage.py fix, backfill ($(cov_line "$EVD/evidence"))"
  fi
  python3 -m tests.regression.rebaseline table --record "$EVD/evidence/record" > "$EVD/table.txt" 2>&1
  python3 -m tests.regression.rebaseline write --record "$EVD/evidence/record" --commit "$EPOCH_SHA" --branch main \
    --release rebaseline-epoch-q-word --run-id "$RUN" --force > "$EVD/write.txt" 2>&1 || { cat "$EVD/write.txt"; exit 5; }
  cat "$EVD/write.txt"
  git add "tests/regression/expected/$KEY.json"
  forced=${decision#WRITE forced=}; forced=${forced% pending=*}
  git commit -q -m "epoch: re-baseline #$N under Q_word v1 at ${EPOCH_SHA:0:8} (run $RUN; forced: $forced$note)" && push
  git log --oneline -n 1
  [ -n "$note" ] && printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$N" "$KEY" "$(git rev-parse --short HEAD)" "$RUN" \
    "$(grep -o '^STORED build art:[0-9a-f]*' "$EVD/evidence/store.log" | tail -n 1 | cut -d' ' -f3)" \
    "$(grep -o '^STORED records art:[0-9a-f]*' "$EVD/evidence/store.log" | tail -n 1 | cut -d' ' -f3)" "$(cov_line "$EVD/evidence")" >> "$LANE/evidence/coverage-backfill.tsv"
fi
python3 "$H/digest_line.py" "$N" "$EVD/evidence" "$RUN" "$EPOCH_SHA" "$SPENT" "$decision" "${PAIRS:-3}" "${CLOUD:-?}" "${DRIVER:-?}" "$LANE/evidence/attempts-$N.txt" "${GPUS:-?}" "${VCPUS:-?}"
