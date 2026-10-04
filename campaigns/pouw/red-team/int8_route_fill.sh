#!/usr/bin/env bash
# fill: owner=bc-d7d4b0d1 gpus=1 on=2-7 max_min=20 cpus=8 project=pous prio=10 mem_gb=32
# The int8-Strassen route end to end (the assessor, bc-d7d4b0d1), the replay of the Pearl-C4 fix's F2: breadth-first
# Strassen with int8 IMMA leaves on flat NVFP4 tiles (tiedmax, gauss, uniform codes), depth 0-8 at 8,192^3 and 0-6 at
# 16,384^3, every row checked word for word against the direct int8 GEMM with a poisoned word; a self-test with a
# negative control gates it. Divisor: the NVFP4 dense GEMM (CUTLASS 4.8 dense128, BF16 and FP32 words) in the same
# session, 3 interleaved reps. Preemptible, checkpointed per step; yields at step boundaries to the slot owners of GPUs
# 2-7 when no GPU is free. Needs up to ~75 GB of device memory at 16,384^3, depth 6.
set -uo pipefail
W=/workspace/pouw/fill-out/assessor-int8-route
B=/workspace/pouw/fill-out/assessor-basesplit-e2e
S=$W/state; mkdir -p $S $W/out
START=$(date +%s)
[ -n "${GPU_LEASE_UUID:-}" ] || { echo "no GPU lease" >&2; exit 3; }
nvidia-smi --id="$GPU_LEASE_UUID" --query-gpu=timestamp,clocks.sm,power.draw,memory.used,clocks_event_reasons.active \
  --format=csv,noheader -lms 250 >> $W/out/clocks-$GPU_LEASE_UUID.csv &
SMI=$!; trap 'kill $SMI 2>/dev/null' EXIT
others_waiting() {
  local n=0 f h free
  for f in /workspace/pouw/fill/queue/*.sh; do
    [ -e "$f" ] || continue
    h=$(sed -n '2,20{/# *fill:/p}' "$f" | head -1)
    case "$h" in *owner=bc-d7d4b0d1*) continue;; *gpus=0*) continue;; esac
    case "$h" in *owner=bc-0f3f8a2f*|*owner=bc-36186951*|*owner=bc-0de2d624*|*owner=bc-fb55a759*|*owner=bc-71c6ab78*) n=$((n+1));; esac
  done
  free=$(/workspace/pouw/infra/bin/gpu-lease status 2>/dev/null | grep -c " free")
  [ "$n" -gt 0 ] && [ "$free" -le 1 ]
}
step() {
  local name=$1; shift
  [ -e $S/$name.done ] && return 0
  if others_waiting; then echo "yield before $name"; exit 99; fi
  if [ $(( $(date +%s) - START )) -gt 420 ]; then echo "chunk budget used before $name"; exit 99; fi
  echo "{\"step\":\"$name\",\"uuid\":\"$GPU_LEASE_UUID\",\"t\":\"$(date -u +%FT%TZ)\"}" >> $W/out/steps.jsonl
  "$@" && touch $S/$name.done || { echo "step $name failed" >&2; exit 1; }
}
build() {
  [ -x $W/int8_route_replay ] && return 0
  /usr/local/cuda/bin/nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a -o $W/int8_route_replay \
    $W/int8_route_replay.cu -lcublasLt > $W/out/build.log 2>&1
}
tag() { sed "s/^{/{\"rep\":$1,\"uuid\":\"$GPU_LEASE_UUID\",/"; }
selftest() { $W/int8_route_replay selftest | tag 0 >> $W/out/selftest.jsonl && grep -q '"pass":true' $W/out/selftest.jsonl; }
route() {  # route REP N FAMILY L0 L1
  $W/int8_route_replay $2 $3 $4 $5 | tag $1 >> $W/out/route.jsonl
}
fp4_rep() {  # fp4_rep SIZE REP: the NVFP4 dense divisor, FP32 and BF16 words, same session
  local s=$1 rep=$2 it; it=$([ $s -le 8192 ] && echo 40 || echo 10)
  for v in dense128 dense128_bf16; do
    $B/bin/$v time $B/ops/flat $s $s $s $it | tag $rep >> $W/out/nvfp4.jsonl || return 1
  done
}
step build build
step selftest selftest
for rep in 1 2 3; do
  step fp4-8192-rep$rep fp4_rep 8192 $rep
  for fam in tiedmax gauss uniform; do step route-8192-$fam-rep$rep route $rep 8192 $fam 0 8; done
  step fp4-16384-rep$rep fp4_rep 16384 $rep
  for fam in tiedmax gauss; do step route-16384-$fam-rep$rep route $rep 16384 $fam 0 6; done
done
echo "all steps done"; exit 0
