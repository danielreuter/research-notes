#!/usr/bin/env bash
# red-team-flock: flock-pure-gpu CPU-only at flock-gpu-link 7e640265; selftests of the sha256/row/v1 layouts (ShaFp8 on fp8-ada,
# ShaBf16 on bf16-hopper) at 8/64 VUs, plus the fp8-ada BLAKE3 regression at 8.
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh || exit 1
source $HOME/.cargo/env
P=/workspace/flock-gpu-link/flock/target/release/flock-pure-gpu
for rel in fp8-ada bf16-hopper; do for n in 8 64; do
  $P selftest --instances $I/inst-sha-$rel-$n.bin --netlist $I/net-$rel.txt > $O/selftest-sha-$rel-$n.txt 2>&1; grep -h 'SELFTEST\|"pass":false\|panicked' $O/selftest-sha-$rel-$n.txt | cut -c1-300
done; done
$P selftest --instances $I/inst-fp8-8.bin --netlist $I/net-fp8-ada.txt > $O/selftest-blake3-fp8-ada-8.txt 2>&1; grep -h 'SELFTEST\|"pass":false' $O/selftest-blake3-fp8-ada-8.txt | cut -c1-300
true
