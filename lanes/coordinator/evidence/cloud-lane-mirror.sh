#!/bin/bash
# Mirror between the notes (~/.research/notes) and the Project store's internal/ for cloud lanes, which can't push notes until
# the Cursor GitHub App has access to danielreuter/research-notes (root, 2026-09-25 3:38 AM PT). Cloud lanes run with
# RESEARCH_NOTES=/cursor/stores/<project>/internal and RESEARCH_MACHINES_D=<same>/machines.d.
#   kb/ and every laptop lane's top-level *.md / binding.json      notes -> store   (read-only view for cloud lanes)
#   lanes/<cloud lane>/ (listed in internal/lanes/CLOUD-LANES.txt)  both ways, newer file wins, never deletes
#   machines.d/                                                     both ways, newer file wins, never deletes
# Then `research notes sync` publishes what came in from the store. Log: evidence/cloud-lane-mirror.log.
set -u
NOTES=~/.research/notes
STORE="$HOME/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/internal"
LOG=$NOTES/lanes/coordinator/evidence/cloud-lane-mirror.log
LIST="$STORE/lanes/CLOUD-LANES.txt"
mkdir -p "$STORE/kb" "$STORE/lanes" "$STORE/machines.d"
touch "$LIST"
cloud() { grep -qx "$1" "$LIST"; }

rsync -a --update "$NOTES/kb/" "$STORE/kb/"
for d in "$NOTES"/lanes/*/; do
  l=$(basename "$d")
  cloud "$l" && continue
  mkdir -p "$STORE/lanes/$l"
  rsync -a --update --include='*.md' --include='binding.json' --exclude='*' "$d" "$STORE/lanes/$l/"
done

in=0
while read -r l; do
  [ -n "$l" ] || continue
  mkdir -p "$NOTES/lanes/$l" "$STORE/lanes/$l"
  n=$(rsync -a --update --itemize-changes "$STORE/lanes/$l/" "$NOTES/lanes/$l/" | grep -c '^>f')
  rsync -a --update "$NOTES/lanes/$l/" "$STORE/lanes/$l/"
  in=$((in + n))
  [ "$n" -gt 0 ] && echo "$(date -u +%FT%TZ) IN $l: $n file(s) store -> notes" >> "$LOG"
done < "$LIST"
m=$(rsync -a --update --itemize-changes "$STORE/machines.d/" "$NOTES/machines.d/" | grep -c '^>f')
rsync -a --update "$NOTES/machines.d/" "$STORE/machines.d/"
[ "$m" -gt 0 ] && echo "$(date -u +%FT%TZ) IN machines.d: $m entry file(s) store -> notes" >> "$LOG"

if [ $((in + m)) -gt 0 ]; then
  (cd ~ && ~/.research/bin/research notes sync < /dev/null >> "$LOG" 2>&1) || echo "$(date -u +%FT%TZ) SYNC FAILED" >> "$LOG"
fi
