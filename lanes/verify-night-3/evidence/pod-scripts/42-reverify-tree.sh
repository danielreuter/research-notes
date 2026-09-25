#!/usr/bin/env bash
# verify-night-3: reverify results with the reverify.py and a ligero-verify built from tree SRC (its own cargo target dir)
# usage: 42-reverify-tree.sh SRC RESULT_ART...
set -uo pipefail
source "$(dirname "$0")/lib.sh"
S=$1; shift
export PYTHONPATH="$S/packages/verity/src:$S/backends/numerical/python:$S/tools/research/src:$S"
T=/workspace/cargo-$(basename $S)
( cd $S/backends/ligero-verify && CARGO_TARGET_DIR=$T cargo build --release -q 2>&1 | tail -3 )
BIN=$T/release/ligero-verify; ls -la $BIN || exit 2; sha256sum $BIN
cd $S
for r in "$@"; do
  echo "=== $r $(date -u +%H:%M:%SZ)"
  $PY -m backends.direct.ligero.reverify $r --by verify-night-3 --verifier $BIN --work $W/work --jobs ${JOBS:-16} --json \
      > $W/rv-${r:4:8}.json 2> $W/rv-${r:4:8}.err
  echo "rc=$?"; tail -n 3 $W/rv-${r:4:8}.err | cut -c1-300
  R data evict --target-free-gb 40 >/dev/null 2>&1 || true
done
R data labels-sync --push-only 2>&1 | tail -1
