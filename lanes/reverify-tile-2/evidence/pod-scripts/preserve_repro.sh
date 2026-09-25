#!/bin/bash
# Copy (hardlink) the finished shared-local re-production run dirs into this --custody-r2 run, so its run-record carries them.
set -euo pipefail
for r in rvt-repro-fp8-ada-2 rvt-repro-bf16-hopper; do
  cp -al "/workspace/research/runs/$r" "$RESEARCH_RUN_DIR/$r"
  grep -h 'dumps PASS' "$RESEARCH_RUN_DIR/$r/tile_reverify.log" | tail -n 1
done
du -sh "$RESEARCH_RUN_DIR"
