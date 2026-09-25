#!/usr/bin/env bash
# reverify-tile: re-produce a shared-local cell's dump (shared-live-2: --auth included-hash-shared --tile 64x64 --zk --mode
# interactive --batch 16384 --total-vus 4096 --target -128, rep1 dumped; local coins) on this CPU pod at the committed tip,
# now with manifest set.tile; then tile_reverify.py on it.  Usage: reproduce_shared.sh REL [REL...]; runs in the source
# root (`research run --source . --cwd source`); outputs in $RESEARCH_RUN_DIR (custody on R2).
set -uo pipefail
source /workspace/env.sh
q=$(awk '{print $1}' /sys/fs/cgroup/cpu.max 2>/dev/null); p=$(awk '{print $2}' /sys/fs/cgroup/cpu.max 2>/dev/null)
[ -n "$q" ] && [ "$q" != max ] && export RAYON_NUM_THREADS=$((q / p)) OMP_NUM_THREADS=$((q / p))
S=$PWD
export PYTHONPATH="$S/packages/verity/src:$S/backends/numerical/python:$S/tools/research/src:$S"
O=${RESEARCH_RUN_DIR:-/workspace/reverify-tile}; rc=0
dumps=()
for REL in "$@"; do
  D=$O/dump-$REL
  echo "=== $(date -u +%H:%M:%SZ) bench-vu $REL +shared tile64x64 (CPU)"
  $PY -m backends.direct.ligero.run --relation $REL bench-vu --device cpu --auth included-hash-shared --tile 64x64 --zk \
    --mode interactive --batch 16384 --total-vus 4096 --target -128 --reps 1 --dump-reps 1 --pipeline 0 \
    --dump-dir $D --out $O/result-$REL.json 2>&1 | tee $O/bench-$REL.log | grep -vE "^\s*$" | tail -6
  [ ${PIPESTATUS[0]} -eq 0 ] || { rc=1; continue; }
  dumps+=($D)
done
echo "=== $(date -u +%H:%M:%SZ) tile_reverify ${dumps[*]}"
OUT=$O/tile_reverify.json JOBS=${JOBS:-8} $PY $O/inputs/tile_reverify.py "${dumps[@]}" 2>&1 | cut -c1-600 | tee $O/tile_reverify.log
[ ${PIPESTATUS[0]} -eq 0 ] || rc=1
echo "=== $(date -u +%H:%M:%SZ) done rc=$rc"; exit $rc
