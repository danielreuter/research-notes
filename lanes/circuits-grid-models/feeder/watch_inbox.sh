#!/usr/bin/env bash
# Poll the notes for circuits' reply: exits 0 with the inbox / new notes / changed handoffs when something arrives, 3 after MAX_S.
# A changed handoff is any lanes/circuits-grid-models/*.md other than my own report whose content changed (circuits may append to one).
MAX_S=${MAX_S:-1080}
N=~/.research/notes
start=$(date +%s)
seen=$(mktemp)
git -C "$N" ls-files lanes | sort > "$seen"
sums() { (cd "$N" && md5sum lanes/circuits-grid-models/*.md | grep -v -- '-report-circuits-grid-models.md'); }
before=$(sums)
while :; do
  git -C "$N" pull -q --rebase origin main > /dev/null 2>&1 || git -C "$N" rebase --abort > /dev/null 2>&1
  out=$(/workspace/.venv/bin/research notes inbox circuits-grid-models --peek 2>&1)
  new=$(comm -13 "$seen" <(git -C "$N" ls-files lanes | sort) | grep -v '^lanes/circuits-grid-models/' \
        | while read -r f; do grep -l -i 'grid-models' "$N/$f" 2> /dev/null; done)
  changed=$(diff <(echo "$before") <(sums) | grep '^>' | awk '{print $3}')
  if ! grep -q 'nothing new' <<< "$out" || [ -n "$new" ] || [ -n "$changed" ]; then
    echo "$(date -u +%H:%MZ) INBOX:"; echo "$out"; echo "NEW NOTES:"; echo "$new"; echo "CHANGED:"; echo "$changed"
    exit 0
  fi
  [ $(( $(date +%s) - start )) -ge "$MAX_S" ] && { echo "$(date -u +%H:%MZ) nothing after ${MAX_S}s"; exit 3; }
  sleep 90
done
