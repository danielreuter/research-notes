#!/usr/bin/env bash
# Poll the notes for circuits' reply: exits 0 with the inbox / new notes when something arrives, 3 after MAX_S.
MAX_S=${MAX_S:-1080}
N=~/.research/notes
start=$(date +%s)
seen=$(mktemp)
git -C "$N" ls-files lanes | sort > "$seen"
while :; do
  git -C "$N" pull -q --rebase origin main > /dev/null 2>&1 || git -C "$N" rebase --abort > /dev/null 2>&1
  out=$(/workspace/.venv/bin/research notes inbox circuits-grid-models --peek 2>&1)
  new=$(comm -13 "$seen" <(git -C "$N" ls-files lanes | sort) | grep -v '^lanes/circuits-grid-models/' \
        | while read -r f; do grep -l -i 'grid-models' "$N/$f" 2> /dev/null; done)
  if ! grep -q 'nothing new' <<< "$out" || [ -n "$new" ]; then
    echo "$(date -u +%H:%MZ) INBOX:"; echo "$out"; echo "NEW NOTES:"; echo "$new"
    exit 0
  fi
  [ $(( $(date +%s) - start )) -ge "$MAX_S" ] && { echo "$(date -u +%H:%MZ) nothing after ${MAX_S}s"; exit 3; }
  sleep 90
done
