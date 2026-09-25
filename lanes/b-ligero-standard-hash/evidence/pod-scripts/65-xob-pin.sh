#!/usr/bin/env bash
# b-ligero-standard-hash: after the blake3-xob PINS rows are in leaf.rs (synced): rebuild + cargo test + the pinned batch verify
# of 64-xob.sh's fixtures (FIX_RUN), then the gate of each relation under blake3-xob (2048 VUs + the negatives battery).
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 10-pins-gates.sh --send 15-rust.sh \
#     --send 65-xob-pin.sh --env FIX_RUN=<64 run id> -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/65-xob-pin.sh"'
IN=$(dirname "$0"); RD=${RESEARCH_RUN_DIR:?}
(bash "$IN/15-rust.sh"); echo "rust rc=$?"
cd /workspace/src
RESEARCH_RUN_DIR=$RD LEAF=blake3-xob RELS="${XRELS:-fp8-ada fp8-ada-x4}" bash "$IN/10-pins-gates.sh"
