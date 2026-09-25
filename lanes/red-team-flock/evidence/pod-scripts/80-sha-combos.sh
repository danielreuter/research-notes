#!/usr/bin/env bash
# red-team-flock: flock-pure-gpu CPU-only at ad0aa41d; SHA layouts x the new lowerings (ShaFp8 x fp8-hopper, ShaBf16 x bf16-ampere) at 8/64 VUs.
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh || exit 1
source $HOME/.cargo/env
P=/workspace/flock-gpu-link/flock/target/release/flock-pure-gpu
for rel in fp8-hopper bf16-ampere; do for n in 8 64; do
  $P selftest --instances $I/inst-sha-$rel-$n.bin --netlist $I/net-$rel.txt > $O/selftest-sha-$rel-$n.txt 2>&1; grep -h 'SELFTEST\|"pass":false\|panicked' $O/selftest-sha-$rel-$n.txt | cut -c1-300
done; done
true
