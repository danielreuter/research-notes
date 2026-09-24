#!/bin/bash
# launch_nowait.sh STAGE [--source-dir DIR] [extra research-run flags...] -- CMD...   (foreground; prints RUN=<id>; no polling)
set -u
SRC=/Users/danielreuter/projects/verity-main-wt/fp4-fast
LOG=/tmp/fp4fast/drive.log
stage=$1; shift
EXTRA=()
while [ "$1" != "--" ]; do
  if [ "$1" = "--source-dir" ]; then SRC=$2; shift 2; else EXTRA+=("$1"); shift; fi
done; shift
cd /Users/danielreuter/projects/verity-main-wt/fp4-fast
ID=$(uv run python -c "from research.runs import new_run_id; print(new_run_id())" 2>/dev/null | tail -1)
RD=/workspace/research/runs/$ID
CMD=()
for a in "$@"; do a="${a//@RD@/$RD}"; CMD+=("${a//@ID@/$ID}"); done
echo "=== $(date -u +%H:%M:%S) $stage -> $ID (src $SRC): ${CMD[*]}" >> $LOG
out=$(uv run research run --on vy-fp4-fast --project verity --campaign r21-fp4-fast --source "$SRC" --exclusive --id "$ID" --stage "$stage" \
      --env PYTHONPATH=packages/verity/src:backends/numerical/python:tools/research/src:. --env PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
      "${EXTRA[@]}" -- "${CMD[@]}" 2>&1 | grep -v -E '^(Uninstalled|Installed)')
echo "$out" >> $LOG
if ! echo "$out" | grep -q "launched on vy-fp4-fast"; then echo "LAUNCH FAILED: $out"; exit 3; fi
echo "$stage $ID" >> /tmp/fp4fast/runs.txt
echo "RUN=$ID"
