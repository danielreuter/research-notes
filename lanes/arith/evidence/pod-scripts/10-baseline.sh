#!/usr/bin/env bash
# arith step 0 (4090): baseline of the Table 2 headline config (fp8-ada-v3x4 fused l=4096 p8) + p4, then a profile of p8.
source /workspace/arith/scripts/lib.sh
run base-v3x4-p8-r1 fp8-ada-v3x4 4096 8 5
run base-v3x4-p4-r1 fp8-ada-v3x4 4096 4 5
run base-v3x4-p8-r2 fp8-ada-v3x4 4096 8 5
prof base-v3x4-p8 fp8-ada-v3x4 4096 8
echo DONE-10
