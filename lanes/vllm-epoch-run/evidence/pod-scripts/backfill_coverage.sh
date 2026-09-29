#!/bin/bash
# backfill_coverage.sh N: row N's pending coverage (evidence/coverage-backfill.tsv), once origin/main has #325 (`04d1204c`, the
#   coverage check that reads `norm_scales`; vLLM coordinator 2031Z).  VM only: main's harness reruns `coverage` for row N from its
#   stored trees (candidate = manifest.json + commit/layouts_pair0_instrumented.json.gz + commit/runs.jsonl, reference = side_record's
#   rows root), and a passing result is written with `rebaseline write` as one commit on the lane's expected/ branch.  `write` keeps the
#   contract's shape (missing_n, ok, recorded): `checked` and `manifest_digest` are named in the commit message, not added.
set -u
N=${1:?row}; H=$(cd "$(dirname "$0")" && pwd); LANE=$RESEARCH_NOTES/lanes/vllm-epoch-run; BR=/workspace-wt/epoch-run
R="env PYTHONPATH=/workspace/tools/research/src python3 -m research"
IFS=$'\t' read -r _ KEY WCOMMIT RUN BUILD RECORDS _ < <(awk -F'\t' -v n="$N" '$1==n' "$LANE/evidence/coverage-backfill.tsv" | tail -n 1)
[ -n "${KEY:-}" ] || { echo "#$N: not in coverage-backfill.tsv"; exit 2; }
cd /workspace && git fetch -q origin main && git merge-base --is-ancestor 04d1204c origin/main || { echo "#325 not on origin/main yet"; exit 3; }
MAIN=$(git rev-parse origin/main); WT=/workspace-wt/main-${MAIN:0:8}
[ -d "$WT" ] || git worktree add -q --detach "$WT" "$MAIN"
C=/tmp/cand$N; REF=/tmp/regref-$N
if [ ! -f "$C/$KEY/manifest.json" ]; then
  mkdir -p "$C/$KEY"
  $R data fetch "$BUILD" --to "$C/$KEY" --path manifest.json > /dev/null
  $R data fetch "$RECORDS" --to "$C/$KEY" --path commit/layouts_pair0_instrumented.json.gz --path commit/runs.jsonl > /dev/null
fi
[ -d "$REF/$KEY" ] || { echo "#$N: no reference root $REF (run side_record.sh's fetch part)"; exit 4; }
OUT=/workspace/epoch-evidence/$N/coverage-main-${MAIN:0:8}; rm -rf "$OUT"
(cd "$WT/integrations/vllm" && PYTHONPATH=.:../../packages/verity/src:../../tools/research/src:../../protocols/sampled_proofs \
  VERITY_REGRESSION_ROWS_ROOT=$REF VERITY_REGRESSION_CANDIDATE=$C /tmp/covenv/bin/python -m tests.regression.rebaseline run \
  --record "$OUT" --tier T0,T1,T2 -- -k "coverage-r$N" -ra > "$OUT.log" 2>&1)
line=$(python3 - "$OUT/$KEY/coverage.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1])); a = d["actual"]
ok = not d.get("problems") and a.get("ok") is True and a.get("missing_n") == 0
print(("OK " if ok else "FAIL ") + f"checked {a.get('checked')}, missing {a.get('missing_n')}, manifest {a.get('manifest_digest')}, ok {a.get('ok')}, problems {d.get('problems')}")
EOF
)
echo "coverage on main ${MAIN:0:8}: $line"
[[ "$line" == OK* ]] || exit 5
REC=$(python3 -c "import json;print(json.load(open('$BR/integrations/vllm/tests/regression/expected/$KEY.json'))['reference']['commit'])")
cd "$BR/integrations/vllm" && PYTHONPATH=.:../../packages/verity/src:../../tools/research/src /tmp/covenv/bin/python -m tests.regression.rebaseline write \
  --record "$OUT" --commit "$REC" --branch main --release rebaseline-epoch-q-word --run-id "$RUN" > "$OUT.write.txt" 2>&1 || { cat "$OUT.write.txt"; exit 6; }
git add "tests/regression/expected/$KEY.json"
git commit -q -m "epoch: backfill #$N coverage with #325's check on main ${MAIN:0:8} (run $RUN, stored trees ${BUILD:0:12} / ${RECORDS:0:12}): ${line#OK }; contract shape kept (missing_n, ok, recorded)" \
  && { git push -q -u origin HEAD 2>/dev/null && echo "pushed $(git rev-parse --short HEAD)" || echo "PUSH FAILED"; }
git log --oneline -n 1
