#!/usr/bin/env bash
# fill: owner=bc-d7d4b0d1 gpus=1 on=2-7 max_min=8 cpus=8 project=pous prio=10 mem_gb=64
# The int8-Strassen replay (the assessor, bc-d7d4b0d1): pins c_L on the card. Interleaved reps of the int8 IMMA GEMM
# (cuBLASLt), its batched leaves, the s8 pre-add and s32 merge kernels, and the NVFP4 dense divisor (CUTLASS 4.8,
# basesplit_e2e_sm120 dense128, FP32 and BF16 words) at 8,192^3 / 16,384^3 / 32,768^3. Preemptible, checkpointed per step;
# yields at step boundaries to the slot owners of GPUs 2-7 when no GPU is free. Build happens once (CPU) under the lease.
set -uo pipefail
W=/workspace/pouw/fill-out/assessor-int8-strassen
B=/workspace/pouw/fill-out/assessor-basesplit-e2e
S=$W/state; mkdir -p $S $W/out
START=$(date +%s)
[ -n "${GPU_LEASE_UUID:-}" ] || { echo "no GPU lease" >&2; exit 3; }
nvidia-smi --id="$GPU_LEASE_UUID" --query-gpu=timestamp,clocks.sm,power.draw,clocks_event_reasons.active \
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
  if [ $(( $(date +%s) - START )) -gt 360 ]; then echo "chunk budget used before $name"; exit 99; fi
  echo "{\"step\":\"$name\",\"uuid\":\"$GPU_LEASE_UUID\",\"t\":\"$(date -u +%FT%TZ)\"}" >> $W/out/steps.jsonl
  "$@" && touch $S/$name.done || { echo "step $name failed" >&2; exit 1; }
}
build() {
  [ -x $W/int8_strassen_replay ] && return 0
  /usr/local/cuda/bin/nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a -o $W/int8_strassen_replay \
    $W/int8_strassen_replay.cu -lcublasLt > $W/out/build.log 2>&1
}
int8_rep() { $W/int8_strassen_replay "$@" | sed "s/^{/{\"uuid\":\"$GPU_LEASE_UUID\",/" >> $W/out/int8.jsonl; }
fp4_rep() {  # fp4_rep SIZE REP: the NVFP4 dense divisor, FP32 and BF16 words, same session
  local s=$1 rep=$2 it; it=$([ $s -le 8192 ] && echo 40 || { [ $s -le 16384 ] && echo 10 || echo 4; })
  for v in dense128 dense128_bf16; do
    $B/bin/$v time $B/ops/flat $s $s $s $it | sed "s/^{/{\"rep\":$rep,\"uuid\":\"$GPU_LEASE_UUID\",/" >> $W/out/nvfp4.jsonl || return 1
  done
}
step build build
for rep in 1 2 3; do
  for s in 8192 16384 32768; do
    step fp4-$s-rep$rep fp4_rep $s $rep
    step int8-$s-rep$rep int8_rep $s
  done
done
echo "all steps done"; exit 0
