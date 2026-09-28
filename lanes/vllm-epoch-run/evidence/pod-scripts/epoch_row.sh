#!/bin/bash
# epoch_row.sh: one re-baseline row on this pod, at the epoch's main sha, with every epoch default on.
#
#   research run --on vyv-rf-epoch-<n> --project verity --campaign vllm-rebaseline-epoch --custody-r2 --custody-ttl <T> \
#     --timeout <S> --source <clean worktree at EPOCH_SHA> --cwd source/integrations/vllm \
#     --send epoch_row.sh --send strict_word.py --send store_build.sh \
#     --env ROW=<row id> --env ROWNUM=<n> --env CLASS=<GREEN|FAIL> --env EPOCH_SHA=<sha> [--env K=V ...] \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/epoch_row.sh"'
#
# One line per step in evidence/progress.txt; "STOP <why>" ends the row with no Commit (or no store) after it:
#   0 guard      the shipped tree is EPOCH_SHA; no epoch default is switched off (taps, word check, query of record)
#   1 bootstrap  B0 + the row's checkpoint role (pod_bootstrap.sh builds the taps)
#   2 Build, then Match (`verity-vllm row run --stages build`, `--stages match`); between them the row stops when the manifest's
#                query.required_families names call_boundaries (it moves to wave 2); a GREEN row whose Match FAILs stops (deferred)
#   3 word check strict_word.py: `word.check_query` strictly over the row's request Programs, the Commit's manifest reproduced
#   4 Commit     `verity-vllm row run --stages commit` (manifest-verify and the verdict record inside)
#   5 store      store_build.sh: the Build and the records as fixture/v1 trees, `research data put --preserve` (this run's custody key)
#   6 record     the digests and `rebaseline run` (candidate = this sweep), for `rebaseline table / write` on the VM
# The sweep is outside the run dir: custody uploads every run-dir file, so evidence/ holds only small files.
set -u
export EV=$RESEARCH_RUN_DIR/evidence; IN=$RESEARCH_RUN_DIR/inputs; mkdir -p "$EV"
P=$EV/progress.txt
say() { echo "$(date -u +%FT%TZ) $*" | tee -a "$P"; }
: "${ROW:?}" "${ROWNUM:?}" "${CLASS:?}" "${EPOCH_SHA:?}"
T=$(cd ../.. && pwd -P)
export PY=/workspace/venv312/bin/python PY312=/workspace/venv312/bin/python HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
export SWEEP_DIR=/workspace/epoch/sweep NCCL_P2P_DISABLE=${NCCL_P2P_DISABLE:-1}
D=$SWEEP_DIR/$ROW
mkdir -p "$SWEEP_DIR"

small() {   # the row's small files into evidence/ (idempotent; called after each step)
  mkdir -p "$EV/row"
  for f in stages.txt row.log timeline.jsonl build_summary.json verdict.json target_family.json admission.json manifest.log \
           match_summary.json global_match.json commit/manifest_verify.json commit/verdict.json commit/summary.json commit/runs.jsonl; do
    [ -f "$D/$f" ] && [ "$(stat -c %s "$D/$f")" -lt 50000000 ] && { mkdir -p "$EV/row/$(dirname "$f")"; cp "$D/$f" "$EV/row/$f"; }
  done
  [ -f "$D/manifest.json" ] && python3 - "$D/manifest.json" "$EV/row/manifest_header.json" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
json.dump({k: m.get(k) for k in ("schema", "manifest_digest", "program_digest", "complete", "populations", "query")}, open(sys.argv[2], "w"), indent=1)
EOF
}
store() {  # once per run, whenever a Build exists: deferred rows keep their Build too
  [ -f "$D/build_summary.json" ] || [ -d "$D/build" ] || return 0
  [ -f "$EV/stored" ] && return 0
  bash "$IN/store_build.sh" "$D" > "$EV/store.log" 2>&1
  src=$?; touch "$EV/stored"
  say "store rc=$src $(grep '^STORED' "$EV/store.log" | cut -d' ' -f2-4 | tr '\n' ' ')"
  $PY -m tests.regression.rebaseline digests "$D" --out "$EV/digests.json" --markdown "$EV/digests.md" > "$EV/digests.log" 2>&1 \
    || $PY "$IN/row_digests.py" "$D" --out "$EV/digests.json" --markdown "$EV/digests.md" >> "$EV/digests.log" 2>&1   # a tree without #243
  say "digests rc=$? $(tail -n 1 "$EV/digests.md" 2>/dev/null | cut -c1-240)"
}
src=0
finish() { small; store; say "END"; }

# ---- 0 guard ----------------------------------------------------------------------------------------------------------------------------
[ "${RESEARCH_SOURCE_SHA:-}" = "$EPOCH_SHA" ] || { say "STOP guard: shipped tree ${RESEARCH_SOURCE_SHA:-?} is not the epoch sha $EPOCH_SHA"; finish; exit 3; }
for v in NORM_TAP GUARDED_MAX_TAP ROUTER_TAP VOCAB_TAP ROW_TAPS; do
  [ "${!v:-1}" = "1" ] || { say "STOP guard: $v=${!v} switches an epoch default off"; finish; exit 3; }
done
case "${VERITY_WORD_CHECK:-16/32}" in 16/32) ;; *) say "STOP guard: VERITY_WORD_CHECK=$VERITY_WORD_CHECK is not the record's 16/32"; finish; exit 3;; esac
[ -z "${VERITY_QUERY_ID:-}" ] || { say "STOP guard: VERITY_QUERY_ID is set ($VERITY_QUERY_ID); the row runs the query of record"; finish; exit 3; }
[ -z "${TARGET_FAMILY_WAIVER:-}" ] || { say "STOP guard: a row of record carries no target-family waiver"; finish; exit 3; }
env | grep -E '^(PAIRS|VU_EXPORT|GPU_UTIL|COMMIT_GPU_UTIL|BUILD_TIMEOUT|VERITY_QWORD_MAX_GATES|NCCL_P2P_DISABLE|ROW|ROWNUM|CLASS|EPOCH_SHA)=' \
  | sort > "$EV/row_env.txt"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader > "$EV/gpus.txt" 2>&1
export GPU_NAME=$(head -n 1 "$EV/gpus.txt" | cut -d, -f1) RESEARCH_STORE=/workspace/epoch/store
{ grep MemTotal /proc/meminfo; cat /sys/fs/cgroup/memory.max 2>/dev/null || cat /sys/fs/cgroup/memory/memory.limit_in_bytes 2>/dev/null; } > "$EV/host_mem.txt"
say "guard PASS tree=$EPOCH_SHA row=#$ROWNUM class=$CLASS $(tr '\n' ' ' < "$EV/row_env.txt")"

read -r ROLE REPO REV WORLD < <(python3 - "$ROW" <<'EOF'
import json, sys
row = sys.argv[1]
wl = json.load(open(f"workloads/{row}.json"))
role = wl["case"]
alias = {"B0": "HuggingFaceTB/SmolLM2-135M", "B1": "Qwen/Qwen2.5-1.5B"}
cps = json.load(open("manifests/checkpoints.json"))["checkpoints"]
cp = next(c for c in cps if c.get("role") == role or (role in alias and c["repo"] == alias[role] and c.get("local_path")))
tp = int((wl.get("sweep") or {}).get("tp") or wl.get("tp") or (2 if "__tp2__" in row else 1))
print(role, cp["repo"], cp["revision"], tp)
EOF
)
[ -n "${REV:-}" ] || { say "STOP resolve: no checkpoint for $ROW"; finish; exit 2; }
say "resolved role=$ROLE repo=$REPO rev=${REV:0:12} world=$WORLD"

# ---- 1 bootstrap ------------------------------------------------------------------------------------------------------------------------
CASES=B0; [ "$ROLE" = B0 ] || CASES=B0,$ROLE
bash "$IN/failfast_bootstrap.sh" "$CASES" "$EV/bootstrap"   # the 15-minute fail-fast (coordinator 09:13Z)
rc=$?
[ "$rc" = 40 ] && { finish; exit 40; }
say "bootstrap cases=$CASES rc=$rc"
[ "$rc" = 0 ] || { tail -n 30 "$EV/bootstrap.log" > "$EV/bootstrap.tail"; say "STOP bootstrap rc=$rc (bootstrap.tail)"; finish; exit 4; }
export HF_HUB_OFFLINE=1
row() { $PY -m verity_vllm.pipeline.cli row run "$ROW" "$ROLE" "$REPO" "$REV" --stages "$1"; }

# ---- 2 Build, the Call-boundary stop, Match ---------------------------------------------------------------------------------------------
row build > "$EV/build.log" 2>&1
rc=$?; small
say "build rc=$rc $(grep '^build ' "$D/stages.txt" 2>/dev/null | tail -n 1 | cut -c1-240)"
[ "$rc" = 0 ] || { say "STOP build rc=$rc"; finish; exit "$rc"; }
fams=$(python3 -c "import json;print(','.join((json.load(open('$D/manifest.json')).get('query') or {}).get('required_families') or []))" 2>/dev/null)
echo "$fams" > "$EV/required_families.txt"
case ",$fams," in
  *,call_boundaries,*) say "STOP call_boundaries in the manifest's query.required_families: no Commit, the row moves to wave 2"; finish; exit 21;;
  ,,) say "STOP the manifest states no query.required_families"; finish; exit 21;;
esac
say "required_families: $fams (no call_boundaries)"
row match > "$EV/match.log" 2>&1
rc=$?; small
say "match rc=$rc $(grep '^match ' "$D/stages.txt" 2>/dev/null | tail -n 1 | cut -c1-240)"
if [ "$ROWNUM" = 39 ]; then
  { for f in "$D"/build_request*/instances.json.gz; do echo "== $f"; zcat "$f" | grep -o 'GemmBias_v1{[^}]*}\|BiasAdd_v1{[^}]*}' | sort | uniq -c; done
    grep -h -o '"GemmBias_v1[^"]*"' "$D"/match/*.json 2>/dev/null | sort | uniq -c | head; } > "$EV/gemmbias.txt" 2>&1
  say "gemmbias $(grep -c GemmBias_v1 "$EV/gemmbias.txt") lines, BiasAdd_v1 $(grep -c BiasAdd_v1 "$EV/gemmbias.txt") lines (gemmbias.txt)"
fi
case "$rc" in
  0) ;;
  11) [ "$CLASS" = FAIL ] || { say "STOP GREEN row, Match FAIL: deferred, not committed"; finish; exit 11; }
      say "Match FAIL on a FAIL-class row: the Commit runs (the class's record carries one)";;
  *) say "STOP match rc=$rc"; finish; exit "$rc";;
esac

# ---- 3 strict word check ----------------------------------------------------------------------------------------------------------------
$PY "$IN/strict_word.py" "$ROW" "$D" "$ROLE" "$REPO" "$REV" --world "$WORLD" --out "$EV/strict_word.json" > "$EV/strict_word.log" 2>&1
rc=$?; say "strict word check rc=$rc $(tail -n 1 "$EV/strict_word.log" | cut -c1-240)"
[ "$rc" = 0 ] || { say "STOP strict word check FAILED: not committed (strict_word.json)"; finish; exit 20; }

# ---- 4 Commit ---------------------------------------------------------------------------------------------------------------------------
row commit > "$EV/commit.log" 2>&1
rc=$?; small
out=$($PY -c "import json;print(json.load(open('$D/verdict.json')).get('outcome'))" 2>/dev/null)
mv=$($PY -c "import json;print(json.load(open('$D/commit/manifest_verify.json')).get('ok'))" 2>/dev/null)
say "commit rc=$rc verdict=${out:-none} manifest_verify=${mv:-none} $(grep '^commit ' "$D/stages.txt" 2>/dev/null | tail -n 1 | cut -c1-200)"

# ---- 5 store the Build and the records, 6 digests + regression record -------------------------------------------------------------------
small; store
VERITY_REGRESSION_CANDIDATE=$SWEEP_DIR timeout 3600 $PY -m tests.regression.rebaseline run --record "$EV/record" --tier T0,T1,T2 -- -k "r$ROWNUM" -ra \
  > "$EV/rebaseline_run.log" 2>&1
say "rebaseline run rc=$? $(grep -E 'passed|failed|error' "$EV/rebaseline_run.log" | tail -n 1 | cut -c1-200)"
finish
[ "$src" = 0 ] || exit 30
exit 0
