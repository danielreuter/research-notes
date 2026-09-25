#!/bin/bash
# Custody for runs launched before --custody-r2: copy each named run dir on this pod into this run's dir, so the runner
# publishes the copies (with this run's record) to R2.
#   usage: research run --on {pod} --project verity --source <worktree> --cwd source --custody-r2 --send custody_copy.sh \
#            -- bash -c 'bash $RESEARCH_RUN_DIR/inputs/custody_copy.sh RUN_ID ...'
L=$RESEARCH_RUN_DIR; ROOT=/workspace/research/runs
for r in "$@"; do
  [ -d "$ROOT/$r" ] || { echo "missing $r"; exit 3; }
  mkdir -p "$L/prior/$r" && cp -a "$ROOT/$r/." "$L/prior/$r/" && rm -f "$L/prior/$r/.custody"
  echo "copied $r files=$(find "$L/prior/$r" -type f | wc -l) bytes=$(du -sb "$L/prior/$r" | cut -f1)"
  (cd "$L/prior/$r" && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum) > "$L/prior-$r.sha256"
done
echo "done $(date -u +%FT%TZ)"
