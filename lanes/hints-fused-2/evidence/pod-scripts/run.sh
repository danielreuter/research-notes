#!/bin/bash
# /workspace/run.sh TREE LOG cmd... : run from TREE with the lane env; log to /workspace/logs/LOG.log
TREE=$1; LOG=$2; shift 2
cd $TREE || exit 2
export PATH=/workspace/venv312/bin:/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:$PATH
export PYTHONPATH=packages/verity/src:backends/numerical/python:tools/research/src:.
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
mkdir -p /workspace/logs
{ echo "=== $(date -u +%H:%M:%S) tree=$TREE sha=$(cat $TREE/TREE_SHA 2>/dev/null) cmd: $*"; t0=$(date +%s)
  "$@"; rc=$?
  echo "=== $(date -u +%H:%M:%S) rc=$rc wall=$(( $(date +%s) - t0 ))s"; } > /workspace/logs/$LOG.log 2>&1
