#!/usr/bin/env bash
# Screening (not registered), fork 6655716e (home-par): around the registered hill-climb 8 config (ET 2x, 4 chunks,
# 4 splicers): 5 and 6 chunks, and ET 1.94x (three balanced ~131k-call TcDotBf16 shards).
set -uo pipefail
S=/workspace/sp1-tcdot/scripts/quick.sh
export SERVER_HOME=home-par
TAG=p11-et2c5s5 ELEMENT_THRESHOLD=805306368 MINIMAL_TRACE_CHUNK_THRESHOLD=1000000 SP1_WORKER_NUM_SPLICING_WORKERS=5 bash $S
TAG=p11-et2c6s6 ELEMENT_THRESHOLD=805306368 MINIMAL_TRACE_CHUNK_THRESHOLD=850000 SP1_WORKER_NUM_SPLICING_WORKERS=6 bash $S
TAG=p11-et194c4s4 ELEMENT_THRESHOLD=781000000 MINIMAL_TRACE_CHUNK_THRESHOLD=1250000 SP1_WORKER_NUM_SPLICING_WORKERS=4 bash $S
echo "=== screen done"
