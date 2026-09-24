#!/usr/bin/env bash
# Screening (not registered) of fork 6655716e (patch 0011, home-par server): with the precompile trace generated in
# parallel, fewer and larger TcDotBf16 shards (ELEMENT_THRESHOLD 2x: 3 shards; 1.5x: 4) and more trace chunks with as
# many splicing workers (the CPU shards' records sooner).
set -uo pipefail
S=/workspace/sp1-tcdot/scripts/quick.sh
export SERVER_HOME=home-par MINIMAL_TRACE_CHUNK_THRESHOLD=2500000
TAG=p11-et2 ELEMENT_THRESHOLD=805306368 bash $S
TAG=p11-et15 ELEMENT_THRESHOLD=603979776 bash $S
TAG=p11-c3s3 ELEMENT_THRESHOLD=503316480 MINIMAL_TRACE_CHUNK_THRESHOLD=1600000 SP1_WORKER_NUM_SPLICING_WORKERS=3 bash $S
TAG=p11-et2c3s3 ELEMENT_THRESHOLD=805306368 MINIMAL_TRACE_CHUNK_THRESHOLD=1600000 SP1_WORKER_NUM_SPLICING_WORKERS=3 bash $S
echo "=== screen done"
