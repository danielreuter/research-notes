#!/usr/bin/env bash
# arith H100 port: base (main 22741456) vs tip, 3 alternating rounds each, on the Table 2 cells' configs:
#   E4M3  fp8-hopper-v3x4 l=4096 p8 local coins        (cell art:85569708)
#   BF16  bf16-hopper-v3x4 l=4096 p8, LIVE same-pod verifier tcp://127.0.0.1:7000 (niced; cell art:aadcd93f)
# LIGERO_REFERENCE_HINTS=0 as fill-dc ran them (skips only the warm-up reference-hints check).
export LIGERO_REFERENCE_HINTS=0
S=/workspace/arith/scripts
ROUNDS=${ROUNDS:-3} bash $S/port-ab.sh h8 fp8-hopper-v3x4 4096 8
ROUNDS=${ROUNDS:-3} bash $S/port-ab.sh h16 bf16-hopper-v3x4 4096 8 --verifier tcp://127.0.0.1:7000
echo DONE-h100
