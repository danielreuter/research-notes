#!/bin/bash
# usage: mkhead.sh PATCH DEST     DEST = copy of /workspace/basemain (no __pycache__, no numerics JIT build) + PATCH
set -e
P=$1; D=$2
rm -rf "$D"; cp -a /workspace/basemain "$D"
find "$D" -name __pycache__ -type d -prune -exec rm -rf {} +
rm -rf "$D/integrations/vllm/verity_vllm/program/numerics/cpp/build"
cd "$D" && git apply --check "$P" && git apply "$P"
find "$D/integrations/vllm" -type d -empty -delete
echo "HEAD-OK $D $(find "$D" -type f | wc -l) files"
