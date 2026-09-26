#!/usr/bin/env bash
# verify-bligero-real-k: CPU-pod bootstrap from the shipped source (main), then cell_check.py per cell (args: full art ids).
# Run as: research run --on vy-verify-bligero-real-k --project verity --campaign bligero-real-k --source . --cwd source
#         --custody-r2 --send 10-verify.sh --send cell_check.py -- bash $RESEARCH_RUN_DIR/inputs/10-verify.sh ART...
set -uo pipefail
SRC=$PWD
I=$RESEARCH_RUN_DIR/inputs
W=/workspace/verify-bligero-real-k; mkdir -p $W
echo "##### $(date -u +%H:%M:%SZ) bootstrap SRC=$SRC"
if [ ! -x /workspace/bin/ligero-verify ] || [ "${REBOOT:-0}" = 1 ]; then
  HEALTH=0 SRC=$SRC bash $SRC/backends/direct/ligero/pod_bootstrap.sh > $RESEARCH_RUN_DIR/bootstrap.log 2>&1
  grep -E "FAILED|BOOTSTRAP" $RESEARCH_RUN_DIR/bootstrap.log | tail -5
fi
source /workspace/env.sh
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
# cargo build of THIS tree's verifier (the bootstrap's may predate it)
( cd $SRC/backends/ligero-verify && cargo build --release -q ) > $RESEARCH_RUN_DIR/cargo.log 2>&1; echo "cargo rc=$?"
V=$CARGO_TARGET_DIR/release/ligero-verify
sha256sum $V | tee $RESEARCH_RUN_DIR/ligero_verify.sha256
# the run's minted custody key as the store remote (never printed)
C=/workspace/research/requests/$RESEARCH_RUN_ID/custody
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$C/store.toml
eval "$($PY - "$C/cred.json" <<'EOF'
import json, shlex, sys
d = json.load(open(sys.argv[1]))
for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
    if d.get(k):
        print(f"export {k}={shlex.quote(d[k])}")
EOF
)"
research() { $PY -m research "$@"; }
export -f research 2>/dev/null
mkdir -p $W/bin; printf '#!/bin/sh\nexec %s -m research "$@"\n' "$PY" > $W/bin/research; chmod +x $W/bin/research; export PATH=$W/bin:$PATH
if [ "${PINS:-1}" = 1 ]; then
  echo "##### $(date -u +%H:%M:%SZ) system digests of the 16 real-K pins on this pod"
  VBRK_VERIFIER=$V $PY $I/pins_check.py $W/pins > $RESEARCH_RUN_DIR/pins.out 2>&1; echo "pins rc=$?"; tail -1 $RESEARCH_RUN_DIR/pins.out
  cp $W/pins/pins-check.json $RESEARCH_RUN_DIR/pins-check.json 2>/dev/null
fi
for a in "$@"; do
  echo "##### $(date -u +%H:%M:%SZ) cell $a"
  $PY $I/cell_check.py $a --out $RESEARCH_RUN_DIR/cells/${a:4:8} --work $W/work --verifier $V --jobs ${JOBS:-${VY_CPU_THREADS:-16}} 2> $RESEARCH_RUN_DIR/cells-${a:4:8}.err
  echo "rc=$?"; tail -3 $RESEARCH_RUN_DIR/cells-${a:4:8}.err
  rm -rf $W/work/rv
done
echo "##### $(date -u +%H:%M:%SZ) done"
