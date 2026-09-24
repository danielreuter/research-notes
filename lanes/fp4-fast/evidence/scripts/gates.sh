#!/bin/bash
# lane fp4-fast: pytest backends/direct/ligero + the fp4-nvf4 gate (device hints, the default; and numpy hints for A/B) + the
# five other relation gates on the lane tree (cwd), on the pod.  Same lines as hostphase's evidence/scripts/gates.sh.
set -u
export PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:$PATH
export PYTHONPATH=packages/verity/src:backends/numerical/python:.
PY=/workspace/venv312/bin/python
# the pod shows 120 CPUs to torch/OpenMP under a 12.75-CPU cgroup quota: without this the CPU tests spin at 118 running threads
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-12} MKL_NUM_THREADS=${MKL_NUM_THREADS:-12}
echo "OMP_NUM_THREADS=$OMP_NUM_THREADS cpu.max=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null) nproc=$(nproc)"
echo "=== tree $(git rev-parse HEAD 2>/dev/null || echo '?') at $(pwd)"
echo "=== pytest backends/direct/ligero"
t0=$(date +%s)
$PY -m pytest backends/direct/ligero -q -p no:cacheprovider --deselect backends/direct/ligero/v2 --durations=15 2>&1 | tail -34
echo "pytest rc=${PIPESTATUS[0]} wall=$(( $(date +%s) - t0 ))s"
gate () {
  local name=$1; shift
  echo "=== gate $name: $*"
  t0=$(date +%s)
  $PY -m backends.direct.ligero.run "$@" 2>&1 | grep -v Warning | tail -6
  echo "gate $name rc=${PIPESTATUS[0]} wall=$(( $(date +%s) - t0 ))s"
}
gate fp4-nvf4-device --relation fp4-nvf4 gate-vu --vus 256 --batch 1024 --device cuda --row-negatives 60 --unit-negatives 48 --fp4-hints device --out "$RESEARCH_RUN_DIR/gate_fp4_device.json"
gate fp4-nvf4-bench-pipe3 --relation fp4-nvf4 bench-vu --zk --mode interactive --batch 4096 --total-vus 1024 --reps 1 --target -128 --device cuda --pipeline 3 --dump-dir "$RESEARCH_RUN_DIR/pipe3_dumps" --dump-reps 1
gate fp4-nvf4-device-zk --relation fp4-nvf4 gate-vu --vus 64 --batch 1024 --device cuda --zk --fp4-hints device
gate fp4-nvf4-numpy --relation fp4-nvf4 gate-vu --vus 64 --batch 1024 --device cuda --fp4-hints numpy
gate bf16-ampere gate-vu --root /workspace/bench-instances/v1 --vus 64 --device cuda
gate bf16-hopper --relation bf16-hopper gate-vu --vus 64 --device cuda --instances-cache /workspace/instances-cache
gate bf16-hopper-zk --relation bf16-hopper gate-vu --vus 64 --device cuda --zk --instances-cache /workspace/instances-cache
gate fp8-hopper --relation fp8-hopper gate-vu --vus 64 --device cuda --instances-cache /workspace/instances-cache
gate fp8-ada --relation fp8-ada gate-vu --vus 64 --device cuda --instances-cache /workspace/instances-cache
gate bf16-hopper-legacy --relation bf16-hopper gate-vu --vus 64 --device cuda --impl legacy --instances-cache /workspace/instances-cache
echo GATES_DONE
