#!/usr/bin/env bash
# red-team-flock: flock-pure-gpu CPU-only at flock-gpu-link 48045063; selftests for fp8-hopper and bf16-ampere at 8/64 VUs.
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh || exit 1
source $HOME/.cargo/env
P=/workspace/flock-gpu-link/flock/target/release/flock-pure-gpu
for pair in fp8h:fp8-hopper bf16a:bf16-ampere; do
  t=${pair%%:*}; rel=${pair##*:}
  for n in 8 64; do
    $P selftest --instances $I/inst-$t-$n.bin --netlist $I/net-$rel.txt > $O/selftest-$rel-$n.txt 2>&1; grep -h 'SELFTEST\|"pass":false' $O/selftest-$rel-$n.txt | cut -c1-300
  done
done
true
