#!/usr/bin/env bash
# Places main_confirm.sh's one 0-GPU job on node 1 (ready/proofs-n2-hill/, rank -1) once a 16-core prover slice is free that no
# GPU point is waiting for: no GPU item in ready/, a slice lock free, and no more unfinished GPU provers jobs (submitted in the
# last 2 h) than slices held. Not after 10:00Z: about 2 h of staging must end before node 1's /workspace goes offline at 12:40Z.
# Prints "placed <file>", "waiting: <why>" or "too late". Runs on node 1 (python3, flock).
set -euo pipefail
D=/workspace/jobs/proofs-n2-hill/main-confirm
R=/workspace/jobs/ready/proofs-n2-hill
ID=main-confirm-aac1537-fullk
[ -e "$D/placed" ] && { echo "placed already: $(cat $D/placed)"; exit 0; }
[ "$(date -u +%H%M)" -lt 1000 ] || { echo "too late"; exit 3; }
held=0 free=0
for s in 128-143 144-159 160-175; do
  if flock -n /workspace/jobs/slices/$s.lock true; then free=$((free + 1)); else held=$((held + 1)); fi
done
why=$(python3 - "$held" <<'PY'
import glob, json, sys, time
from datetime import datetime, timezone
held = int(sys.argv[1])
for f in glob.glob("/workspace/jobs/ready/*/*.json"):
    try:
        g = ((json.load(open(f)).get("resources") or {}).get("prover-bench") or {}).get("gpus", 1)
    except (OSError, ValueError):
        continue
    if g:
        print(f"a GPU item waits in ready/: {f}"); sys.exit()
sub, end, t0 = {}, set(), time.time() - 7200
for ln in open("/workspace/jobs/dispatch/log.jsonl"):
    try:
        d = json.loads(ln)
    except ValueError:
        continue
    if d.get("ev") == "submit" and d.get("queue") == "provers" and (d.get("requests") or {}).get("nvidia.com/gpu"):
        if datetime.fromisoformat(d["t"].replace("Z", "+00:00")).timestamp() >= t0:
            sub[d["job"]] = d["key"]
    elif d.get("ev") == "end":
        end.add(d["job"])
live = [k for j, k in sub.items() if j not in end]
if len(live) > held:
    print(f"{len(live)} unfinished GPU provers jobs, {held} slices held: {live}")
PY
)
[ "$free" -gt 0 ] || why="no slice free (${held} held)${why:+; $why}"
[ -z "$why" ] || { echo "waiting: $why"; exit 2; }
mkdir -p "$R" && chmod 2775 "$R"
cat > "$R/.$ID.tmp" <<EOF
{"template": "prover-bench", "tree": "/workspace/research/trees/proofs-n2-hill-main-aac1537", "queue": "provers", "rank": -1,
 "env": {"CMD": "CONFIRM_DIR=$D CONFIRM_SCRATCH=$D/scratch PYBIN=/workspace/jobs/venv312/bin/python bash $D/main_confirm.sh",
         "CAMPAIGN": "proofs-554-review",
         "LABEL": "red-team-proofs-554's optional full-K confirmation: origin/main aac153709 stages BF16, E4M3, NVF4 and MXF4 at K = 2048..16384 (n = 16, --binary /bin/false), each circuit_sha512 against node 1's points (plan.json)",
         "QUESTION": "does origin/main aac153709 stage, at the overnight K, the same circuit (stage.circuit_sha512) as the lanes' points on #554's trees?"},
 "resources": {"prover-bench": {"cpus": 16, "memory": 64, "gpus": 0}}}
EOF
python3 -c 'import json, sys; json.load(open(sys.argv[1]))' "$R/.$ID.tmp"
mv "$R/.$ID.tmp" "$R/$ID.json"
echo "$R/$ID.json $(date -u +%FT%TZ)" > "$D/placed"
echo "placed $R/$ID.json"
