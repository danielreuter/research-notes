#!/usr/bin/env bash
# verify-night: reverify.py (lane/verify-night @ 1b3c7be6) on stored B-Ligero results, labels --by verify-night.
#   ROUND=<name> bash 06-reverify.sh ART...        (AWS_* in the calling environment: the scoped read-write credential)
# Verifier: /workspace/cargo-target/release/ligero-verify, cargo --release build of backends/ligero-verify at 1b3c7be6
# (last commit touching the crate: 8729f457); /workspace/src is a tar sync (no .git), so reverify tags it by sha256.
cd /workspace/src && source /workspace/env.sh
O=/workspace/verify-night; mkdir -p $O/rv
ROUND=${ROUND:-r$(date -u +%H%M)}
nohup $PY -m backends.direct.ligero.reverify "$@" --by verify-night --jobs 16 --work $O/rv > $O/reverify-$ROUND.out 2>&1 &
echo "started $! -> $O/reverify-$ROUND.out"
