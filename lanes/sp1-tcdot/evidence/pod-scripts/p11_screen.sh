#!/usr/bin/env bash
# Screening (not registered) of fork 6655716e (patch 0011) with the home-par server, step 6 options, twice.
set -uo pipefail
export SERVER_HOME=home-par ELEMENT_THRESHOLD=503316480 MINIMAL_TRACE_CHUNK_THRESHOLD=2500000
TAG=p11-c1 bash /workspace/sp1-tcdot/scripts/quick.sh
TAG=p11-c1b bash /workspace/sp1-tcdot/scripts/quick.sh
echo "=== screen done"
