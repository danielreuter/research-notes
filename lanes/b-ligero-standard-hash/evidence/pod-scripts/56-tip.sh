#!/usr/bin/env bash
# b-ligero-standard-hash: the merged R1/R2/R4 tree (ligero-steps-pin 06176b41 merged): 53-unit.sh (pytest + the red team's
# R4 harness + honest / proof-removed commitment_problems), then 51-r2check.sh (verify_tree end to end + R2 negatives).
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 51-r2check.sh --send 52-r4check.sh \
#     --send 53-unit.sh --send 56-tip.sh --send rtsh_orphan_e2e.py \
#     --env DUMP=/workspace/research/runs/r20260925-073210-f45c/sweep/p4-16384/proofs -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/56-tip.sh"'
IN=$(dirname "$0")
bash "$IN/53-unit.sh"
bash "$IN/51-r2check.sh"
