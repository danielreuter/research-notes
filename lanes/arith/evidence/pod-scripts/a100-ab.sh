#!/usr/bin/env bash
# arith A100 port: base (main 22741456) vs tip, bf16-ampere-v3 l=16384 p8 local coins (cell art:e1fcf643), 4 alternating
# rounds; LIGERO_REFERENCE_HINTS=0 as fill-dc.
export LIGERO_REFERENCE_HINTS=0
ROUNDS=${ROUNDS:-4} bash /workspace/arith/scripts/port-ab.sh a16 bf16-ampere-v3 16384 8
echo DONE-a100
