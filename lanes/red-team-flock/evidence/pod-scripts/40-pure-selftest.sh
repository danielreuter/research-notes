#!/usr/bin/env bash
# red-team-flock: build flock-pure-gpu CPU-only from the shipped tree (flock-gpu-link d3e96304) and rerun its selftest at 8 and 64 VUs.
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh || exit 1
source $HOME/.cargo/env
P=/workspace/flock-gpu-link/flock/target/release/flock-pure-gpu
for n in 8 64; do
  $P selftest --instances $I/inst-$n.bin --netlist $I/net-bf16-hopper.txt > $O/selftest-cpu-$n.txt 2>&1; grep -h 'SELFTEST\|"pass":false' $O/selftest-cpu-$n.txt | cut -c1-300
done
