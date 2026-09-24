#!/bin/bash
# wave-a100-3 (laptop): register wave-a100-2's unregistered pod runs with its reg.sh, then dump the chosen live cells.
set -uo pipefail
REG=~/.research/notes/lanes/wave-a100-2/evidence/reg.sh
OUT=~/.research/notes/lanes/wave-a100-2/evidence/registered.txt
MINE=~/.research/notes/lanes/wave-a100-3/evidence/registered.txt
L="LIVE same-DC EU-RO-1"
run() { line=$(bash $REG "$@" 2>&1 | tail -1); echo "$line" | tee -a $OUT $MINE; }
# done 06:05Z (first launch was killed after these two): live-v3p4-r3 art:2cfd62d3, live-x4p4-r3 art:6f4201e7
# run live-v3p4-r3       "wave-a100-2 bf16-ampere-v3 fused bare p4 l=16384 $L r3 A100-SXM4"
# run live-x4p4-r3       "wave-a100-2 bf16-ampere-v3x4 fused bare p4 l=4096 $L r3 A100-SXM4"
run live-shared64p8-r3 "wave-a100-2 bf16-ampere committed included-hash-shared tile64x64 p8 l=16384 $L r3 A100-SXM4"
run live-x4p4-r4       "wave-a100-2 bf16-ampere-v3x4 fused bare p4 l=4096 $L r4 A100-SXM4"
run live-v3p4-r4       "wave-a100-2 bf16-ampere-v3 fused bare p4 l=16384 $L r4 A100-SXM4"
run live-v3p8-r4       "wave-a100-2 bf16-ampere-v3 fused bare p8 l=16384 $L r4 A100-SXM4"
run hashp8-r1          "wave-a100-2 bf16-ampere included-hash unshared p8 l=16384 local r1 A100-SXM4"
run live-hashp8-r1     "wave-a100-2 bf16-ampere included-hash unshared p8 l=16384 $L r1 A100-SXM4 (dump)" dump
run live-x4p4-r1       "wave-a100-2 bf16-ampere-v3x4 fused bare p4 l=4096 $L r1 A100-SXM4 (dump)" dump
run live-shared64p8-r1 "wave-a100-2 bf16-ampere committed included-hash-shared tile64x64 p8 l=16384 $L r1 A100-SXM4 (dump)" dump
run live-v3p8-r3       "wave-a100-2 bf16-ampere-v3 fused bare p8 l=16384 $L r3 A100-SXM4 (dump)" dump
echo REG_ALL_DONE
