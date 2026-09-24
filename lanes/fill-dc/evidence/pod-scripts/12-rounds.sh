#!/usr/bin/env bash
# fill-dc: extra local rounds (no dumps) over the given specs, e.g. the column-2 depth sweep (v1 + included-hash is the only
# relation that composes: x4 fails the poseidon2 rate block, v2 / v3 / v2x4 / v3x4 the operand-pin decode; 11-hash-probe).
#   ROUNDS="1 2 3" PREFIX=hd bash 12-rounds.sh SPEC...     SPEC = tag:rel:l:p[:extra,comma,separated]
source /workspace/fill-dc/scripts/lib.sh
while pgrep -f "scripts/(10-h100|20-a100)-sweep.sh|scripts/11-hash-probe.sh" >/dev/null; do sleep 5; done
for r in ${ROUNDS:-1 2 3}; do round $r "$@"; done
echo "$(date -u +%H:%M:%S) ROUNDS_DONE ${PREFIX:-}" | tee -a $SUM
