#!/usr/bin/env bash
# wave-h100-2: replaces the rest of 01-bare.sh round 1 (killed 03:59Z: each v3/v3x4 process spent ~100 s in the warm-up
# reference-hints check and the cold fp8-hopper-v3x4 run's reps 1-2 were still compiling, 3.1 / 2.1 s vs 0.071 s rep 3).
# Screening round (r1, rep1 dumped + pinned Rust) for the candidates 01-bare.sh had not finished, fp8-hopper-v3x4 p4 rerun
# with a warm kernel cache (the cold run kept as r0-fp8-v3x4-p4-cold), then 02-rest.sh.
source /workspace/wave-h100-2/scripts/lib.sh
[ -d $O/bare/r1-fp8-v3x4-p4 ] && [ ! -d $O/bare/r0-fp8-v3x4-p4-cold ] && mv $O/bare/r1-fp8-v3x4-p4 $O/bare/r0-fp8-v3x4-p4-cold
b bare r1-fp8-v3x4-p8   fp8-hopper-v3x4  4096  8 1
b bare r1-fp8-v3x4-p4   fp8-hopper-v3x4  4096  4 1
b bare r1-bf16-v1-p8    bf16-hopper      16384 8 1
b bare r1-bf16-v3-p8    bf16-hopper-v3   16384 8 1
b bare r1-bf16-v3x4-p4  bf16-hopper-v3x4 4096  4 1
b bare r1-bf16-v3x4-p8  bf16-hopper-v3x4 4096  8 1
echo R1_DONE | tee -a $O/bare/summary.txt
exec bash /workspace/wave-h100-2/scripts/02-rest.sh
