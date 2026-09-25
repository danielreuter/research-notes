#!/usr/bin/env bash
# b-ligero-standard-hash: where the +blake3 commitment spends its time (cProfile of one bench-vu, 1 rep, no dump).
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 12-prof.sh --env REL=fp8-ada+blake3 \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/12-prof.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
REL=${REL:?}; L=${L:-4096}; P=${P:-2}
RD=${RESEARCH_RUN_DIR:?}
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
gpu_idle || exit 3
$PY -m cProfile -o $RD/prof.out -m backends.direct.ligero.run --relation $REL bench-vu --zk --mode interactive \
    --auth included-hash --commit-per-rep --batch $L --pipeline $P --total-vus $L --target -128 --reps 1 --device cuda \
    --out $RD/result.json ${EXTRA:-} > $RD/bench.log 2>&1
echo "bench rc=$?"; grep -E "^rep " $RD/bench.log | cut -c1-400
$PY - "$RD/prof.out" <<'EOF'
import pstats, sys
s = pstats.Stats(sys.argv[1]); s.sort_stats("cumulative")
s.print_stats(r"hashauth|leaf/blake3|relchain|commitments|auth\.py", 30)
s.sort_stats("tottime"); s.print_stats(25)
EOF
