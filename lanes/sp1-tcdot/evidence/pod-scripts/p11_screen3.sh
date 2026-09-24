#!/usr/bin/env bash
# Screening (not registered), fork 6655716e (home-par): two balanced TcDotBf16 shards (ELEMENT_THRESHOLD 2.34x, about
# 197.7k calls each) and one (4.67x, all 393,152 calls).
set -uo pipefail
S=/workspace/sp1-tcdot/scripts/quick.sh
export SERVER_HOME=home-par MINIMAL_TRACE_CHUNK_THRESHOLD=2500000
TAG=p11-et234 ELEMENT_THRESHOLD=1178599424 bash $S
TAG=p11-et467 ELEMENT_THRESHOLD=2348810240 bash $S
echo "=== screen done"
