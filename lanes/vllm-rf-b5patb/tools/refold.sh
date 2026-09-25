#!/bin/bash
# Re-fold one regression row's recorded capture log: the Match `fold` stage (fold worker with --persist-dir) and the `resolve` stage
# (resolve_log), exactly as pipeline/match.py's Plan builds them, in venv312.  (b5pat's refold.sh, output under /workspace/b5patb.)
#   usage: refold.sh TREE TAG ROWDIR PROFILE      out: /workspace/b5patb/refold/TAG/{fold_summary.json,run/,fold.log,resolve.log,sha256.txt}
T=$1; TAG=$2; R=$3; P=$4
O=/workspace/b5patb/refold/$TAG; rm -rf "$O"; mkdir -p "$O/run"
cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf
export PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITOR_REPO AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
LOG=$R/match/capture/log.jsonl.gz
echo "start $(date -u +%FT%TZ) tree $T log $LOG profile $P"
python -m verity_vllm.pipeline.match --worker fold --log "$LOG" --profile "$P" --out "$O/fold_summary.json" --persist-dir "$O/run" > "$O/fold.log" 2>&1
echo "fold rc=$? $(date -u +%FT%TZ)"; tail -2 "$O/fold.log"
python -m verity_vllm.observe.fold.resolve_log "$LOG" --profile "$P" --out "$O/run/resolution" --quiet > "$O/resolve.log" 2>&1
echo "resolve rc=$? $(date -u +%FT%TZ)"; tail -2 "$O/resolve.log"
( cd "$O/run" && ls -la && sha256sum $(ls) 2>&1 ) > "$O/sha256.txt"
cat "$O/sha256.txt"
