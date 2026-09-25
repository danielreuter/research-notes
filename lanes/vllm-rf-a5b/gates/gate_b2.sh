#!/bin/bash
# gate (b) head then base on the same pod, sequentially: gate_b2.sh HEAD_TREE HEAD_TAG BASE_TREE BASE_TAG [pytest args...]
H=$1; HT=$2; B=$3; BT=$4; shift 4
bash /workspace/a5/gate_b.sh "$H" "$HT" "$@"
bash /workspace/a5/gate_b.sh "$B" "$BT" "$@"
