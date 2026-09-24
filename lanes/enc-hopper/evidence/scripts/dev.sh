#!/bin/bash
# lane enc-hopper dev runner: overlay the --send'ed lane files onto /workspace/dev (a copy of the shipped main 6babe27 tree) and run "$@" there.
set -u
export PATH=/usr/local/cuda/bin:$PATH
export PYTHONPATH=packages/verity/src:backends/numerical/python:backends/shared:.
[ -d /workspace/dev ] || cp -a /workspace/src-main /workspace/dev
cd /workspace/dev
for f in "$RESEARCH_RUN_DIR"/inputs/*.py; do
  b=$(basename "$f")
  case $b in
    commit_gpu.py|encode_simt.py|merkle.py|protocol.py|encode_simt_test.py|commit_gpu_test.py) cp "$f" "backends/direct/ligero/$b"; echo "overlay $b";;
    *) ;;
  esac
done
echo "=== $(date -u +%H:%M:%S) run: $*"
exec "$@"
