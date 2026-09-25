#!/usr/bin/env bash
# b-ligero-standard-hash: 51-r2check.sh (R2 negatives with the proofs in place, so R4 holds and R2 is what is tested),
# then 61-smoke.sh (main's GPU committer under --commit-per-rep, device vs host commit evidence).
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 51-r2check.sh --send 61-smoke.sh \
#     --send 62-r2-smoke.sh --env DUMP=/workspace/research/runs/r20260925-073210-f45c/sweep/p4-16384/proofs \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/62-r2-smoke.sh"'
IN=$(dirname "$0")
bash "$IN/51-r2check.sh"
bash "$IN/61-smoke.sh"
