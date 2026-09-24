#!/usr/bin/env bash
# Screening (not registered) of fork 0e00bd15 (patch 0010) with the home-sub server: step 5's options (ELEMENT_THRESHOLD
# 1.25x, MINIMAL_TRACE_CHUNK_THRESHOLD 2.5M), then the trace split re-tuned for the lower cycle count ($1 = cycles / 2
# rounded up, from p10_build's bare-execute).
set -uo pipefail
W=/workspace/sp1-tcdot
HALF=${1:?cycles/2}
export SERVER_HOME=home-sub ELEMENT_THRESHOLD=503316480
TAG=p10-c1 MINIMAL_TRACE_CHUNK_THRESHOLD=2500000 bash $W/scripts/quick.sh
TAG=p10-c2 MINIMAL_TRACE_CHUNK_THRESHOLD=$HALF bash $W/scripts/quick.sh
TAG=p10-c1b MINIMAL_TRACE_CHUNK_THRESHOLD=2500000 bash $W/scripts/quick.sh
echo "=== screen done"
