#!/bin/bash
# Remove finished lanes' clean worktrees whose branch is fully pushed to origin (user rule, 2026-09-25 1:15 AM PT: only when free
# disk < 5 GiB). Candidates come from `research notes gc-worktrees` (finished lane, tip on origin); each is re-checked right before
# removal: `git status --porcelain` empty (incl. untracked), and `git rev-list origin/<branch>..HEAD` empty after a fetch. Logged.
set -u
LOG=~/.research/notes/lanes/coordinator/evidence/worktree-removals.log
MAIN=~/projects/verity-main-wt/main
~/.research/bin/research notes gc-worktrees 2>/dev/null | awk '$1=="remove"{print $2, $3}' | while read -r wt br; do
  wt="${wt/#\~/$HOME}"
  [ -d "$wt" ] || continue
  git -C "$MAIN" fetch -q origin "$br" 2>/dev/null || { echo "$(date -u +%FT%TZ) SKIP $wt ($br): fetch failed" >> "$LOG"; continue; }
  dirty=$(git -C "$wt" status --porcelain --untracked-files=all | wc -l | tr -d ' ')
  ahead=$(git -C "$wt" rev-list "origin/$br..HEAD" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$dirty" != 0 ] || [ "$ahead" != 0 ]; then
    echo "$(date -u +%FT%TZ) SKIP $wt ($br): dirty=$dirty unpushed=$ahead" >> "$LOG"; continue
  fi
  size=$(du -sh "$wt" 2>/dev/null | cut -f1)
  tip=$(git -C "$wt" rev-parse --short HEAD)
  if git -C "$MAIN" worktree remove "$wt"; then
    echo "$(date -u +%FT%TZ) REMOVED $wt ($br @ $tip, $size; branch kept, on origin)" >> "$LOG"
  else
    echo "$(date -u +%FT%TZ) FAILED $wt ($br)" >> "$LOG"
  fi
done
df -h / | tail -1
