#!/usr/bin/env bash
# flock-128: phase breakdown (PCS_TRACE) of today's profile (Fast, b684b12) for the CPU union proof
# (census unit hopper_bf16 + BLAKE3 row leaves, one union proof) at N VUs. Uses the build from 00-setup-cpu.sh.
set -uxo pipefail
W=/workspace/flock-128; OUT=$W/out/trace-$(date -u +%H%MZ); mkdir -p $OUT $W/net
source $HOME/.cargo/env
cp $RESEARCH_RUN_DIR/inputs/unit-*.netlist $W/net/ 2>/dev/null || true
cd $W/flock
UBIN=$(ls -t target/release/deps/unit_shape-* | grep -v '\.d$' | head -1)
QUOTA=$(awk '$1 != "max" {print int($1 / $2)}' /sys/fs/cgroup/cpu.max 2>/dev/null)
TH=${THREADS:-${QUOTA:-$(nproc)}}; [ "$TH" -gt "$(nproc)" ] && TH=$(nproc)
for net in ${NETS:-hopper_bf16}; do
  for n in ${NS:-4096}; do
    tag=trace-$net-mixed-n$n-t$TH
    PCS_TRACE=1 RAYON_NUM_THREADS=$TH US_NET=$W/net/unit-$net.netlist US_MODE=mixed US_NS=$n US_RUNS=${RUNS:-1} \
      /usr/bin/time -v $UBIN > $OUT/$tag.out 2> $OUT/$tag.err
    echo "rc=$? $tag"; grep RESULT $OUT/$tag.out; grep -E 'Maximum resident|panicked' $OUT/$tag.err
  done
done
cp -r $OUT "$RESEARCH_RUN_DIR/out"
