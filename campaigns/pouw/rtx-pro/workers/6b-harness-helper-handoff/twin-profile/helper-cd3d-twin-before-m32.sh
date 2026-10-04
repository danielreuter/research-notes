#!/usr/bin/env bash
# fill: owner=bc-2aa33ad8-7eb0-5ce2-8ffc-6420476ecd3d gpus=1 max_min=8 cpus=8 project=pous prio=10
# Harness helper bc-6da61042 (for bc-2aa33ad8): one chunk, the Pearl-C sm_120 arms' gate seconds (wall_s) at the headline shape
# m32-n8192-k8192, before: "before" is tree 14041d06c852 = the arm at 9f1e33b1 (ship3's cubin) beside harness a2da2b73c, its twin serial as on
# the coordinator's repeats; "after" is the same with the arm's twin in the harness's process pool (881eb05df's change). FP8
# baselines only, short tune and timing: a diagnostic of where the lease's seconds go, not a panel row. bench bounded by
# `timeout 450`. Out: /workspace/pouw/helper-cd3d/twin-before-m32-n8192-k8192/.
set -uo pipefail
S=/workspace/pouw/helper-cd3d/twin-14041d06c852
IN=/workspace/research/runs/r20260930-124211-a304/inputs
L=/workspace/pouw/harness/build/bab84c1606a8553a
OUT=/workspace/pouw/helper-cd3d/twin-before-m32-n8192-k8192
rm -rf "$OUT" && mkdir -p "$OUT/ship" || exit 1
tar -xf "$IN/pearl-c-sm120-ship3.tar" -C "$OUT/ship" --strip-components=1 || exit 1
(cd "$OUT/ship" && sha256sum -c MANIFEST.sha256) > "$OUT/ship-manifest-check.txt" 2>&1 || exit 1
cd "$S" || exit 1
export PYTHONDONTWRITEBYTECODE=1
. benchmarks/pouw/harness/jobs/env.sh "$L" || exit 1
export PEARLC_SHIP="$OUT/ship" PEARLC_ROWS="$OUT/rows" CUDA_DEVICE_ORDER=PCI_BUS_ID
echo "tree=$(cat COMMIT) uuid=${GPU_LEASE_UUID:-?} cvd=${CUDA_VISIBLE_DEVICES:-?} job=${FILL_JOB:-?} omp=${OMP_NUM_THREADS:-?} start=$(date -u +%FT%TZ) load=$(cut -d' ' -f1-3 /proc/loadavg)" | tee "$OUT/lease.txt"
trap 'echo preempted; exit 143' TERM
rc=0
timeout 450 "$PY" benchmarks/pouw/harness/bench.py --gpu lease --server-md "$IN/server.md" --clock-label locked-2100 \
  --shapes m32-n8192-k8192 --families fp8-e4m3 --methods graph --tune-reps 1 --finalists 2 --item-ms 10 --warmup-s 1 --warmup-max-s 5 \
  --arm-path benchmarks/pouw/pearl_c_sm120 --arm pearlc_arm:PearlCSm120 --arm pearlc_arm:PearlCSm120Unpromoted \
  --out "$OUT/bench.json" > "$OUT/bench.log" 2>&1 || rc=$?
trap - TERM
echo "exit=$rc end=$(date -u +%FT%TZ) load=$(cut -d' ' -f1-3 /proc/loadavg)" | tee -a "$OUT/lease.txt"
rm -rf "$OUT/rows"
tail -3 "$OUT/bench.log"
case $rc in 137|143) exit 143;; esac
exit 0
