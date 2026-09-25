#!/usr/bin/env bash
# poseidon-v1 H100: both Hopper rows on one pod, one after the other (row.sh each), then register both (register.sh; needs $PV/r2.env)
SCRIPTS=/workspace/poseidon-v1/scripts
POD="vy-poseidon-v1 afx80tft4x2ejt (H100 80GB HBM3, EU-FR-1, EPYC 9554)"
COMMITTER="lane/hash-commit b862be30 (merged at lane/poseidon-v1 54ad119d; verified by verify-night-2 0715Z)"
bash $SCRIPTS/row.sh h100-bf16hopper bf16-hopper 16384 8 131072
bash $SCRIPTS/row.sh h100-fp8hopper fp8-hopper 16384 8 131072
bash $SCRIPTS/register.sh h100-bf16hopper "$POD" "$COMMITTER"
bash $SCRIPTS/register.sh h100-fp8hopper "$POD" "$COMMITTER"
rm -f /workspace/poseidon-v1/r2.env
echo H100_DONE
