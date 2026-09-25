#!/usr/bin/env bash
# jolt-scout: PR #1618 sweep with the binary 30-pr1618.sh built. `profile` compiles `{name}-guest` via `jolt build -p`, so
# it must run from the jolt-pr1618 workspace root (30's sweep ran from a scratch dir and every guest build failed).
# Env: RUNS="be:bench:scale ..." (default below), REPS (default 1).
set -uo pipefail
W=/workspace/jolt-scout; cd $W/jolt-pr1618; source $HOME/.cargo/env
export PATH=$W/pr1618-bin/bin:/usr/local/cuda/bin:$PATH CARGO_TARGET_DIR=$W/target-pr1618
L=$W/31-pr1618.log; exec > >(tee -a $L) 2>&1
B=$CARGO_TARGET_DIR/release/jolt-prover; ls -la $B || exit 1
RUNS=${RUNS:-"optimized:sha2-chain:20 cuda:sha2-chain:20 optimized:sha2-chain:22 cuda:sha2-chain:22 optimized:fibonacci:22 cuda:fibonacci:22 optimized:sha2-chain:24 cuda:sha2-chain:24"}
G=$W/pr1618-bench; mkdir -p $G
exec 9>$W/timing.lock; flock 9; echo "LOCK $(date -u +%H:%M:%SZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
for r in $RUNS; do
  IFS=: read be bench s <<<"$r"
  for rep in $(seq 1 ${REPS:-1}); do
    nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits -lms 200 > $G/gpu-$be-$bench-$s-$rep.csv &
    S=$!
    t0=$(date +%s.%N)
    /usr/bin/time -v timeout 1200 $B profile --name $bench --scale $s --format none --backend $be > $G/out-$be-$bench-$s-$rep.log 2>&1
    rc=$?; t1=$(date +%s.%N); kill $S
    grep -v '^\s*$' $G/out-$be-$bench-$s-$rep.log | grep -vE '^\s+(Page|Volun|Invol|Swaps|File|Socket|Signal|Average|Exit|Command|Percent|Major|Minor|System|User)' | tail -6 | cut -c1-250
    echo "PROFILE be=$be bench=$bench scale=$s rep=$rep rc=$rc wall=$(python3 -c "print(round($t1-$t0,2))")s gpu_max_util=$(cut -d, -f1 $G/gpu-$be-$bench-$s-$rep.csv | sort -n | tail -1) gpu_max_mem_mib=$(cut -d, -f2 $G/gpu-$be-$bench-$s-$rep.csv | sort -n | tail -1)"
  done
done
flock -u 9
echo PR1618_SWEEP_DONE $(date -u +%H:%M:%SZ)
