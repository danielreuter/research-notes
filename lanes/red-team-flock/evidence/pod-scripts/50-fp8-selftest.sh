#!/usr/bin/env bash
# red-team-flock: build flock-pure-gpu CPU-only at flock-gpu-link 48045063; fp8-ada selftest at 8/64 VUs, bf16 regression at 8,
# and one loopback session per layout to print the statement digests.
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh || exit 1
source $HOME/.cargo/env
P=/workspace/flock-gpu-link/flock/target/release/flock-pure-gpu
for n in 8 64; do
  $P selftest --instances $I/inst-fp8-$n.bin --netlist $I/net-fp8-ada.txt > $O/selftest-fp8-$n.txt 2>&1; grep -h 'SELFTEST\|"pass":false' $O/selftest-fp8-$n.txt | cut -c1-300
done
$P selftest --instances $I/inst-8.bin --netlist $I/net-bf16-hopper.txt > $O/selftest-bf16-8.txt 2>&1; grep -h 'SELFTEST\|"pass":false' $O/selftest-bf16-8.txt | cut -c1-300
for pair in "fp8-8:net-fp8-ada" "8:net-bf16-hopper"; do
  inst=${pair%%:*}; net=${pair##*:}; PIN=$(sha256sum $I/$net.txt | cut -d' ' -f1)
  $P serve --listen 127.0.0.1:7301 --out $O/sess-$inst --instances $I/inst-$inst.bin --netlist $I/$net.txt --pin $PIN --operator red-team-flock > $O/serve-$inst.log 2>&1 &
  SP=$!; for i in $(seq 120); do grep -q SERVING $O/serve-$inst.log && break; sleep 1; done
  $P prove --verifier 127.0.0.1:7301 --instances $I/inst-$inst.bin --netlist $I/$net.txt --warm 0 --runs 1 > $O/prove-$inst.txt 2>&1
  grep -o '"statement_digest":"[0-9a-f]*"\|"accepted":[a-z]*' $O/prove-$inst.txt | sort -u
  kill $SP; wait $SP 2>/dev/null
done
true
