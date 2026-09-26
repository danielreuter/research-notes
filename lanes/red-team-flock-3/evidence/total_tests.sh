#!/usr/bin/env bash
# red-team-flock-3: flock-backend's total statement (cursor/flock-backend-4983 @ d4627b62, relation bf16-ampere-total, pin
# fef256df), CPU, local build of that tree: its probe selftests (K 1536 / 2048 at 8 and 64 VUs), its negatives, my negatives.
set -uo pipefail
T=/tmp/rtf3-fb; P=/tmp/rtf3/bin-fb/flock-pure-gpu; D=${RESEARCH_RUN_DIR:-/tmp/rtf3/total}/out; mkdir -p $D
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$T/packages/verity/src:$T/backends/numerical/python:$T/backends/flock/python:$T/integrations/vllm
echo "binary $(sha256sum $P | cut -c1-16) tree $(git -C $T rev-parse HEAD | cut -c1-8)"
python3 -c "from verity_flock import lowering as L; open('$D/net.txt','w').write(L.netlist('bf16-ampere-total')); assert L.digest('bf16-ampere-total') == L.PINS['bf16-ampere-total']; print('pin ok', L.PINS['bf16-ampere-total'][:16])"
for k in 1536 2048; do for n in 8 64; do
  python3 -c "from verity_flock import instances as I; I.write_probe('$D/probe-$k-$n.bin', 'bf16-ampere-total', $n, $k)"
  $P selftest --instances $D/probe-$k-$n.bin --netlist $D/net.txt > $D/selftest-$k-$n.txt 2>&1
  echo "SELFTEST k$k n$n pass=$(grep -c '"pass":true' $D/selftest-$k-$n.txt) fail=$(grep -c '"pass":false' $D/selftest-$k-$n.txt) $(grep -h '^SELFTEST' $D/selftest-$k-$n.txt | tail -1)"
done; done
python3 -m verity_flock.negatives --bin $P --relation bf16-ampere-total --vus 64 --out $D/negatives 2>&1 | grep '^NEG' | cut -c1-260
python3 $HOME/research-notes/lanes/red-team-flock-3/evidence/rtf3_total_negs.py $P $D/rtf3-negs 2048 2>&1 | cut -c1-300
