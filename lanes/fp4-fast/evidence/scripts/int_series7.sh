#!/bin/bash
INT=/Users/danielreuter/projects/verity-main-wt/fp4-fast-int
L=/tmp/fp4fast/launch_nowait.sh
# (a) DIAGNOSTIC, not a table row: 4092 VUs = 6 x 682, no 4-VU tail sub-batch (the measured floor for hypothesis 6b.1)
out=$($L int7-intzk-l16384-pipe3-4092vus --source-dir "$INT" --tool bench_vu_fp4 --scratch triton --require-result -- \
      /workspace/venv312/bin/python -m backends.direct.ligero.run --relation fp4-nvf4 bench-vu --zk --mode interactive --warmup-subs 6 --pipeline 3 --batch 16384 --total-vus 4092 --reps 3 \
      --target -128 --device cuda --run-id @ID@ --out @RD@/result.json --dump-dir @RD@/proofs --dump-reps 1)
echo "$out"; id=$(echo "$out" | grep -o 'RUN=.*' | cut -d= -f2); [ -n "$id" ] && /tmp/fp4fast/wait.sh "$id" 8
# (b) non-ZK --pipeline 3 again (093904-5bbd spread 0.054-0.081)
/tmp/fp4fast/bench_fp4.sh int7-nonzk-l16384-pipe3 $INT 16384 --mode interactive --warmup-subs 7 --pipeline 3
echo INT_SERIES7_DONE
