#!/usr/bin/env bash
# red-team-flock: flock-pure-gpu CPU-only at flock-gpu-link 758a8edf; Chunk(n) selftests at 8/64 VUs (producer's instance files)
# plus the Chunk(3) = K 1536 bf16-hopper regression at 8.
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh > $O/build.log 2>&1 || { tail -30 $O/build.log; exit 1; }
source $HOME/.cargo/env
P=/workspace/flock-gpu-link/flock/target/release/flock-pure-gpu
for pair in fp8ada2k:fp8-ada bf16a2k:bf16-ampere fp8ada8k:fp8-ada bf16a8k:bf16-ampere fp8h8k:fp8-hopper fp8h2k:fp8-hopper; do
  t=${pair%%:*}; net=${pair##*:}
  for n in 8 64; do
    $P selftest --instances $I/inst-$t-$n.bin --netlist $I/net-$net.txt > $O/selftest-$t-$n.txt 2>&1; grep -h 'SELFTEST\|"pass":false' $O/selftest-$t-$n.txt | cut -c1-300
  done
done
$P selftest --instances $I/inst-8.bin --netlist $I/net-bf16-hopper.txt > $O/selftest-chunk3-bf16-hopper-8.txt 2>&1; grep -h 'SELFTEST\|"pass":false' $O/selftest-chunk3-bf16-hopper-8.txt | cut -c1-300
true
