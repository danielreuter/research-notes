#!/usr/bin/env bash
# wave-h100-2: after 01-bare.sh round 1. Per relation: the two fastest round-1 candidates get rounds 2 (reversed order) and 3
# (round-1 order); headline = lowest median over the three rounds' t.total. Then per relation: live bare headline (3 sessions),
# committed +shared tile 64x64 local (rep1 dumped, Rust --system-h) and live, then RTT probe.
source /workspace/wave-h100-2/scripts/lib.sh
while ! grep -q R1_DONE $O/bare/summary.txt 2>/dev/null; do sleep 5; done
# cfg per round-1 tag: relation batch pipeline
declare -A CFG=(
  [fp8-v1-p4]="fp8-hopper 16384 4" [fp8-v3-p4]="fp8-hopper-v3 16384 4" [fp8-v3x4-p4]="fp8-hopper-v3x4 4096 4" [fp8-v3x4-p8]="fp8-hopper-v3x4 4096 8"
  [bf16-v1-p8]="bf16-hopper 16384 8" [bf16-v3-p8]="bf16-hopper-v3 16384 8" [bf16-v3x4-p4]="bf16-hopper-v3x4 4096 4" [bf16-v3x4-p8]="bf16-hopper-v3x4 4096 8")
top2() { for t in "${!CFG[@]}"; do [[ $t == $1-* ]] && echo "$(ttv $O/bare/r1-$t/result.json) $t"; done | sort -n | head -2 | awk '{print $2}'; }
F=($(top2 fp8)); B=($(top2 bf16))
echo "$(date -u +%H:%M:%S) top2 fp8: ${F[*]}  bf16: ${B[*]}" | tee -a $O/summary.txt
for t in ${F[1]} ${F[0]} ${B[1]} ${B[0]}; do b bare r2-$t ${CFG[$t]} 0; done
for t in ${F[0]} ${F[1]} ${B[0]} ${B[1]}; do b bare r3-$t ${CFG[$t]} 0; done
best() { for t in "$@"; do echo "$($PY -c 'import sys,statistics;print("%.5f"%statistics.median(map(float,sys.argv[1:])))' $(for r in r1 r2 r3; do ttv $O/bare/$r-$t/result.json; done)) $t"; done | sort -n | head -1 | awk '{print $2}'; }
HF=$(best ${F[@]}); HB=$(best ${B[@]})
echo "$(date -u +%H:%M:%S) headline fp8: $HF  bf16: $HB" | tee -a $O/summary.txt
echo "$HF $HB" > $O/headline.txt
probe
lv bare-fp8-$HF ${CFG[$HF]}
lv bare-bf16-$HB ${CFG[$HB]}
b shared fp8-shared-p4 fp8-hopper 16384 4 1 --auth included-hash-shared --tile 64x64
b shared bf16-shared-p4 bf16-hopper 16384 4 1 --auth included-hash-shared --tile 64x64
lv shared-fp8-p4 fp8-hopper 16384 4 --auth included-hash-shared --tile 64x64
lv shared-bf16-p4 bf16-hopper 16384 4 --auth included-hash-shared --tile 64x64
probe
wait
$PY -m verity_numerical.bench.summary $O/bare $O/live $O/shared > $O/summary_table.txt 2>&1
$PY -m verity_numerical.bench.summary $O/bare $O/live $O/shared --json > $O/summary_table.json 2>&1
echo REST_DONE | tee -a $O/summary.txt
