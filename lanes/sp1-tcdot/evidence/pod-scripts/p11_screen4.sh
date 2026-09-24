#!/usr/bin/env bash
# Screening (not registered), fork 6655716e (home-par): larger TcDotBf16 shards combined with more trace chunks and as
# many splicing workers.
set -uo pipefail
S=/workspace/sp1-tcdot/scripts/quick.sh
export SERVER_HOME=home-par
while pgrep -f "p11_screen3[.]sh" >/dev/null; do sleep 5; done
TAG=p11-et234c3s3 ELEMENT_THRESHOLD=1178599424 MINIMAL_TRACE_CHUNK_THRESHOLD=1600000 SP1_WORKER_NUM_SPLICING_WORKERS=3 bash $S
TAG=p11-et2c4s4 ELEMENT_THRESHOLD=805306368 MINIMAL_TRACE_CHUNK_THRESHOLD=1250000 SP1_WORKER_NUM_SPLICING_WORKERS=4 bash $S
TAG=p11-et234c4s4 ELEMENT_THRESHOLD=1178599424 MINIMAL_TRACE_CHUNK_THRESHOLD=1250000 SP1_WORKER_NUM_SPLICING_WORKERS=4 bash $S
echo "=== screen done"
