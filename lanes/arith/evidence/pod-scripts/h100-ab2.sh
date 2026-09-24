#!/usr/bin/env bash
# arith H100, second pass: BF16 bf16-hopper-v3x4 l=4096 p8 with LOCAL coins (the prover change without the same-pod live
# verifier's variance; the cell art:aadcd93f is live), 4 rounds, then 3 more E4M3 rounds (r4-r6).
export LIGERO_REFERENCE_HINTS=0
S=/workspace/arith/scripts
while pgrep -f "[h]100-ab.sh" >/dev/null; do sleep 5; done
ROUNDS=4 bash $S/port-ab.sh h16L bf16-hopper-v3x4 4096 8
ROUNDS=6 FROM=4 bash $S/port-ab.sh h8 fp8-hopper-v3x4 4096 8
echo DONE-h100-2
