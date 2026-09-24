#!/usr/bin/env bash
# fill-dc H100: a 4th live round of the four chosen configs after 31-h100-live-then-dump.sh (L-f8b-x4p8-r1 was started by an
# orphaned 30-live.sh while a second one began its probe; it is kept but flagged, and r4 gives each config one more sample).
cd /workspace/fill-dc
while pgrep -f "scripts/31-h100-live-then-dump.sh" >/dev/null; do sleep 5; done
LIVE=tcp://127.0.0.1:7000 ROUNDS=4 bash scripts/30-live.sh L-f8b-x4p8:fp8-hopper-v3x4:4096:8 L-f8h-v1p8:fp8-hopper:16384:8:--auth,included-hash \
    L-b16b-x4p8:bf16-hopper-v3x4:4096:8 L-b16h-v1p8:bf16-hopper:16384:8:--auth,included-hash
