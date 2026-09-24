#!/bin/bash
# lane hostphase: pytest backends/direct/ligero + the four relation gates on the lane tree (cwd), --impl device (default)
set -u
export PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:$PATH
export PYTHONPATH=packages/verity/src:backends/numerical/python:.
PY=/workspace/venv312/bin/python
RUN=$PY -m backends.direct.ligero.run
echo "=== pytest backends/direct/ligero"
t0=$(date +%s)
$PY -m pytest backends/direct/ligero -q -p no:cacheprovider -x --deselect backends/direct/ligero/v2 2>&1 | tail -15
echo "pytest rc=${PIPESTATUS[0]} wall=$(( $(date +%s) - t0 ))s"
gate () {
  local name=$1; shift
  echo "=== gate $name: $*"
  t0=$(date +%s)
  $PY -m backends.direct.ligero.run "$@" 2>&1 | grep -v Warning | tail -6
  echo "gate $name rc=${PIPESTATUS[0]} wall=$(( $(date +%s) - t0 ))s"
}
gate bf16-ampere gate-vu --root /workspace/bench-instances/v1 --vus 64 --device cuda
gate bf16-hopper --relation bf16-hopper gate-vu --vus 64 --device cuda --instances-cache /workspace/instances-cache
gate bf16-hopper-zk --relation bf16-hopper gate-vu --vus 64 --device cuda --zk --instances-cache /workspace/instances-cache
gate fp8-hopper --relation fp8-hopper gate-vu --vus 64 --device cuda --instances-cache /workspace/instances-cache
gate fp8-ada --relation fp8-ada gate-vu --vus 64 --device cuda --instances-cache /workspace/instances-cache
gate bf16-hopper-legacy --relation bf16-hopper gate-vu --vus 64 --device cuda --impl legacy --instances-cache /workspace/instances-cache
echo GATES_DONE
