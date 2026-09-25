#!/usr/bin/env bash
# b-ligero-vllm-v1: wait for WAIT_RUN (another run on this pod) to end, optionally run the screen (SCREEN=1, CONFIGS), pick
# the screen config with the highest e2e.vu_per_second (among SCREEN_DIR/*.json, default this run's or WAIT_RUN's), then
# the TABLES.md sweep of it (40-sweep.sh) with the plateau dump and the pod's producer Rust check.
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}
if [ -n "${WAIT_RUN:-}" ]; then
  for _ in $(seq 360); do
    grep -q '"state": "\(done\|failed\|killed\)"' /workspace/research/runs/$WAIT_RUN/status.json 2>/dev/null && break; sleep 10
  done
  echo "$(date -u +%H:%M:%SZ) $WAIT_RUN ended"
fi
SD=${SCREEN_DIR:-/workspace/research/runs/$WAIT_RUN}
if [ "${SCREEN:-0}" = 1 ]; then bash "$IN/30-screen.sh"; SD=$RD; fi
best=$($PY - "$SD" <<'PY'
import json, sys
from pathlib import Path
best = None
for f in sorted(Path(sys.argv[1]).glob("*.json")):
    try:
        d = json.loads(f.read_text()); m = {x["name"]: x["value"] for x in d["measurements"]}
    except Exception:
        continue
    v = m.get("e2e.vu_per_second")
    print(f"screen {f.stem}: e2e {v} VU/s, t.total {m.get('t.total')}, commit {m.get('commit.seconds')}, mem {m.get('mem.peak_device_bytes')}", file=sys.stderr)
    if isinstance(v, (int, float)) and (best is None or v > best[0]):
        best = (v, f.stem)
if best:
    rel, l, p = best[1].rsplit("-l", 1)[0].replace("_", "+"), best[1].rsplit("-l", 1)[1].split("-p")[0], best[1].rsplit("-p", 1)[1]
    print(f"{rel}:{l}:{p}")
PY
)
echo "best screen config: ${best:-none}"
[ -n "$best" ] || exit 3
SWEEPS=$best bash "$IN/40-sweep.sh"
