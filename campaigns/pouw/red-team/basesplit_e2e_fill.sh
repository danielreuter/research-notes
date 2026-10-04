#!/usr/bin/env bash
# fill: owner=bc-d7d4b0d1 gpus=1 on=2-4 max_min=8 cpus=8 project=pous prio=10 mem_gb=64
# The base-split end-to-end replay, GPU stage, as preemptible fill (the assessor, bc-d7d4b0d1), on GPUs 2-4 as the
# coordinator booked them (12:07Z; GPU 1 stays with its owner). Restartable: every step leaves a marker in $W/state and
# is skipped once done; exits 99 after ~6 minutes or to yield, 0 when all done.
# Yields to the slot owners of GPUs 2-4 (server.md 11:34Z: bc-0f3f8a2f, homes 3 and 2; bc-36186951, home 4): at each step
# boundary, if either has a GPU job queued and no GPU is free, exit 99. Reads what basesplit_e2e_prep.sh wrote.
set -uo pipefail
W=/workspace/pouw/fill-out/assessor-basesplit-e2e
S=$W/state; mkdir -p $S $W/dumps/gauss $W/dumps/flat $W/times
START=$(date +%s)
[ -n "${GPU_LEASE_UUID:-}" ] || { echo "no GPU lease" >&2; exit 3; }
nvidia-smi --id="$GPU_LEASE_UUID" --query-gpu=timestamp,clocks.sm,power.draw,temperature.gpu,clocks_event_reasons.active \
  --format=csv,noheader -lms 250 >> $W/times/clocks-$GPU_LEASE_UUID.csv &
SMI=$!
trap 'kill $SMI 2>/dev/null' EXIT

others_waiting() {
  local n=0 f
  for f in /workspace/pouw/fill/queue/*.sh; do
    [ -e "$f" ] || continue
    h=$(sed -n '2,20{/# *fill:/p}' "$f" | head -1)
    case "$h" in *owner=bc-0f3f8a2f*|*owner=bc-36186951*) ;; *) continue;; esac
    case "$h" in *gpus=0*) continue;; esac
    n=$((n + 1))
  done
  local free
  free=$(/workspace/pouw/infra/bin/gpu-lease status 2>/dev/null | grep -c " free")
  [ "$n" -gt 0 ] && [ "$free" -eq 0 ]
}
rot() {    # rot R WORDS...: WORDS rotated left by R, so each rep starts with a different variant
  local r=$1; shift; local a=("$@") n=$# x
  for ((x = 0; x < n; x++)); do printf "%s " "${a[$(( (x + r) % n ))]}"; done
}
step() {   # step NAME CMD...: run once, then mark done
  local name=$1; shift
  [ -e $S/$name.done ] && return 0
  if others_waiting; then echo "yield before $name"; exit 99; fi
  if [ $(( $(date +%s) - START )) -gt 360 ]; then echo "chunk budget used before $name"; exit 99; fi
  echo "{\"step\":\"$name\",\"uuid\":\"$GPU_LEASE_UUID\",\"t\":\"$(date -u +%FT%TZ)\"}" >> $W/times/steps.jsonl
  "$@" && touch $S/$name.done || { echo "step $name failed" >&2; exit 1; }
}

verify_at() {   # verify_at FAMILY SIZE VARIANT: poisoned sampled check + negative control; the verdict is recorded, and
                # a timed row counts only for a variant whose check ACCEPTs and whose negative control REJECTs
  [ -x $W/bin/$3 ] || return 0
  $W/bin/$3 verify $W/ops/$1 $2 $2 $2 >> $W/times/verify-$1-$2.jsonl
  echo "{\"mode\":\"verify-rc\",\"variant\":\"$3\",\"family\":\"$1\",\"size\":$2,\"rc\":$?}" >> $W/times/verify-$1-$2.jsonl
}
time_rep() {    # time_rep FAMILY SIZE ITERS REP VARIANT...: one timed rep per variant, in the given order
  local fam=$1 s=$2 it=$3 rep=$4 v; shift 4
  for v in "$@"; do
    [ -x $W/bin/$v ] || continue
    $W/bin/$v time $W/ops/$fam $s $s $s $it | sed "s/^{/{\"family\":\"$fam\",\"rep\":$rep,\"uuid\":\"$GPU_LEASE_UUID\",/" \
      >> $W/times/time-$fam-$s.jsonl || return 1
  done
}

for fam in gauss flat; do
  for v in dense128 dense256 sparse; do
    step check-$fam-$v $W/bin/$v check $W/ops/$fam $W/dumps/$fam
  done
done
V="dense128 dense256 sparse dense128_bf16 sparse_bf16"
for s in 8192 16384; do
  for v in $V; do step verify-flat-$s-$v verify_at flat $s $v; done
  it=$([ $s = 8192 ] && echo 40 || echo 10)
  for rep in 1 2 3 4 5 6; do step time-flat-$s-rep$rep time_rep flat $s $it $rep $(rot $((rep - 1)) $V); done
done
for v in dense128 sparse; do step verify-gauss-8192-$v verify_at gauss 8192 $v; done
for rep in 1 2; do step time-gauss-8192-rep$rep time_rep gauss 8192 40 $rep $(rot $((rep - 1)) dense128 sparse); done
echo "all steps done"
exit 0
