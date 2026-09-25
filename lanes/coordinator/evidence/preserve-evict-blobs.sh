#!/bin/bash
# Preserve local store blobs that R2 lacks as orphan-blob/v1 artifacts, verify them in R2 by direct hash, then evict them
# locally (root approval 2026-09-25 2:47 AM PT). Usage: preserve-evict-blobs.sh SHA256 [SHA256 ...]. Logs to the eviction log.
set -u
set -a; . ~/.config/verity/r2.env; set +a
PY=~/projects/verity-main-wt/main/.venv/bin/python
LOG=~/.research/notes/lanes/coordinator/evidence/20260924T2120Z-eviction-log.tsv
ts() { date -u +%FT%TZ; }
for s in "$@"; do
  f=~/.research/store/objects/sha256/$s
  [ -f "$f" ] || { printf '%s\tSKIP(no-file)\t0\t%s\t-\n' "$(ts)" "$f" >> "$LOG"; continue; }
  size=$(stat -f %z "$f")
  out=$(~/.research/bin/research data put --kind orphan-blob/v1 --file "$f" \
        --meta "{\"reason\":\"local store blob with no preserved holder, preserved before eviction (disk)\",\"sha256\":\"$s\"}" \
        --preserve --json < /dev/null 2>&1)
  rc=$?
  art=$(printf '%s' "$out" | grep -oE 'art:[0-9a-f]{64}' | head -1)
  if [ $rc -ne 0 ]; then printf '%s\tPUT-FAILED(rc=%s)\t%s\t%s\t%s\n' "$(ts)" "$rc" "$size" "$f" "$(printf '%s' "$out" | tail -c 200 | tr '\n\t' '  ')" >> "$LOG"; continue; fi
  printf '%s\tpreserved\t%s\t%s\t%s\n' "$(ts)" "$size" "$f" "$art" >> "$LOG"
  status=$(cd /tmp/coord-evict && "$PY" -c "from pathlib import Path; from check import check; print(check(Path('$f'))[0])")
  if [ "$status" != OK ]; then printf '%s\tKEPT(%s)\t%s\t%s\t-\n' "$(ts)" "$status" "$size" "$f" >> "$LOG"; continue; fi
  rm -f "$f"
  printf '%s\tdeleted-blob\t%s\t%s\tobjects/sha256/%s (R2 direct-hash OK; holder %s)\n' "$(ts)" "$size" "$f" "$s" "$art" >> "$LOG"
done
arts=$(grep -E $'\tdeleted-blob\t' "$LOG" | grep -oE 'holder art:[0-9a-f]{64}' | cut -d' ' -f2 | sort -u)
"$PY" - $arts <<'EOF'
import sys; from pathlib import Path
sys.path.insert(0, str(Path.home() / "projects/verity-main-wt/cli/tools/research/src"))
from research.store.local import LocalStore
st = LocalStore(Path.home() / ".research/store")
for art in sys.argv[1:]:
    try:
        st.index.set_presence(art, local=st.has_local(art))
        print("presence", art[:16], "local", st.has_local(art))
    except Exception as e:
        print("presence-update-failed", art[:16], e)
EOF
df -h / | tail -1
echo DONE
