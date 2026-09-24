#!/bin/bash
# bench_fp4.sh STAGE SRC_DIR BATCH [bench-vu flags...]  -- one fp4-nvf4 contract row on vy-fp4-fast (fp4-proof's command line):
# --total-vus 4096 --reps 3 --target -128, dumps rep 1 under $RD/proofs.  Prints RUN=<id> and waits.
set -u
stage=$1; src=$2; batch=$3; shift 3
out=$(/tmp/fp4fast/launch_nowait.sh "$stage" --source-dir "$src" --tool bench_vu_fp4 --scratch triton --require-result -- \
      /workspace/venv312/bin/python -m backends.direct.ligero.run --relation fp4-nvf4 bench-vu "$@" --batch "$batch" --total-vus 4096 --reps 3 \
      --target -128 --device cuda --run-id @ID@ --out @RD@/result.json --dump-dir @RD@/proofs --dump-reps 1)
echo "$out"
id=$(echo "$out" | grep -o 'RUN=.*' | cut -d= -f2)
[ -n "$id" ] || exit 3
echo "$stage $src $batch $*" >> /tmp/fp4fast/bench_runs.txt
/tmp/fp4fast/wait.sh "$id" 25
