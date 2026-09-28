#!/bin/bash
# canary_pod.sh: the release canary at the epoch's main sha, for re-pinning ops/known_roots.json (cc 8.9) on the VM (repin_roots.py).
#   research run --on vyv-rf-epoch-canary --project verity --custody-r2 --timeout <S> --source <epoch worktree> --cwd source/integrations/vllm \
#     --send canary_pod.sh --env EPOCH_SHA=<sha> -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/canary_pod.sh"'
# Pass 1: positives smollm2,llama with the negatives arena,omitted,lateread (the pins are pre-epoch, so a positive is expected to FAIL only
# with "Build/Match/Commit green but run root ... != known-good"); pass 2, when pass 1 ended within 55 min: the same positives again, so
# each new root is reproduced before it is pinned.  The tree is never edited.  Out: evidence/canary-{a,b}.json, evidence/roots.json.
set -u
EV=$RESEARCH_RUN_DIR/evidence; mkdir -p "$EV"; P=$EV/progress.txt
say() { echo "$(date -u +%FT%TZ) $*" | tee -a "$P"; }
[ "${RESEARCH_SOURCE_SHA:-}" = "${EPOCH_SHA:?}" ] || { say "STOP tree ${RESEARCH_SOURCE_SHA:-?} is not $EPOCH_SHA"; exit 3; }
T=$(cd ../.. && pwd -P); t0=$(date +%s)
bash verity_vllm/ops/pod_bootstrap.sh --cases B0,LLAMA32_1B --out "$EV/bootstrap" --gpu > "$EV/bootstrap.log" 2>&1
rc=$?; say "bootstrap rc=$rc"; [ "$rc" = 0 ] || { tail -n 30 "$EV/bootstrap.log" > "$EV/bootstrap.tail"; exit 4; }
export PY=/workspace/venv312/bin/python
pass() {  # pass TAG POSITIVES NEGATIVES
  local tag=$1; export CANARY_DIR=/workspace/epoch/canary
  bash verity_vllm/ops/canary.sh "$tag" "$2" "$3" > "$EV/$tag.log" 2>&1
  say "$tag rc=$? $(tail -n 1 "$EV/$tag.log" | cut -c1-200)"
  local cd; cd=$(ls -d "$CANARY_DIR/$tag" 2>/dev/null || true)
  [ -n "$cd" ] && cp "$cd/canary.json" "$EV/$tag.json" 2>/dev/null
  for v in "$cd"/*/commit/verdict.json "$cd"/neg_*/verdict.json; do   # positives: <row>/commit/, negatives: neg_<name>/
    [ -f "$v" ] || continue
    who=$(basename "$(dirname "$v")"); [ "$who" = commit ] && who=$(basename "$(dirname "$(dirname "$v")")")
    python3 -c "import json,sys;v=json.load(open(sys.argv[1]));print(sys.argv[2], sys.argv[3], (v.get('run_roots') or ['-'])[0])" "$v" "$tag" "$who" >> "$EV/roots.txt"
  done
}
S8=${EPOCH_SHA:0:8}
pass "epoch-$S8-a" smollm2,llama arena,omitted,lateread
if [ $(( $(date +%s) - t0 )) -lt 3300 ]; then pass "epoch-$S8-b" smollm2,llama ""; else say "pass b skipped: $(( ($(date +%s) - t0) / 60 )) min used"; fi
python3 - "$EV/roots.txt" "$EV/roots.json" <<'EOF'
import json, sys
out = {}
for ln in open(sys.argv[1]) if __import__("os").path.exists(sys.argv[1]) else []:
    tag, row, root = (ln.split() + ["", "", ""])[:3]
    out.setdefault(row, {})[tag[-1]] = root
json.dump(out, open(sys.argv[2], "w"), indent=1)
print(json.dumps(out))
EOF
say "END"
