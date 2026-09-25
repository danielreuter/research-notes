#!/usr/bin/env bash
# verify-night-2 request 1: hash-commit's 4090 fp8-ada Poseidon2 committer baselines (coordinator/20260925T0612Z-handoff-from-hash-commit.md).
# All checks write nothing to the store (reverify --dry-run); labels come after, from 11-label / reverify without --dry-run.
#   research run --on vy-verify-night-2 --project verity --cwd /workspace/src --send <these scripts> --send registered-4090.txt \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/10-hash-commit.sh"'
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
I=$RESEARCH_RUN_DIR/inputs; O=/workspace/verify-night-2/hc; mkdir -p $O
FULL=$(grep -E 'base-fp8ada-l8192-p4-r4|tip-fp8ada-l8192-p4-r1 |k515e-fp8ada-l8192-p4-r4|k0b40-fp8ada-l8192-p4-r7|tip-fp8ada-l8192-p4-r7' $I/registered-4090.txt \
       | sed -E 's/.*result=(art:[0-9a-f]+).*/\1/')
echo "full-tree results: $FULL"
{
echo "=== [$(date -u +%H:%M:%S)] reverify --dry-run (5 full-tree results)"
$PY -m backends.direct.ligero.reverify $FULL --dry-run --verifier /workspace/bin/ligero-verify --jobs 16 --work $O/rv --json > $O/reverify.json
echo "reverify rc=$?"
$PY - $O/reverify.json <<'EOF'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception as e:
    print("no json", e); sys.exit()
for r in (d if isinstance(d, list) else d.get("results", [d])):
    print({k: r.get(k) for k in ("result", "verdict", "status", "reason", "relation", "system_id", "n_proofs", "batch_log2", "custody") if k in r})
EOF
echo "=== [$(date -u +%H:%M:%S)] statement binding"
$PY $I/04-stmt-binding.py $FULL > $O/binding.json; echo "binding rc=$?"
echo "=== [$(date -u +%H:%M:%S)] core roots"
$PY $I/06-core-roots.py $FULL > $O/core-roots.json; echo "core-roots rc=$?"
echo "=== [$(date -u +%H:%M:%S)] byte identity over all 20 runs"
$PY $I/07-byte-identity.py $I/registered-4090.txt > $O/byte-identity.json; echo "byte-identity rc=$?"
echo "=== [$(date -u +%H:%M:%S)] negatives (after tree 13e1c916, before tree cc2e80a9)"
bash $I/05-negatives.sh art:13e1c916ea787bdec3ef99000aa9a0109985a01b50aaf7133d2c41e3437e4830 hc-after
bash $I/05-negatives.sh art:cc2e80a973a596d175e1707680eada3e83a2b29c39fb85e489b6dfba3bede5fd hc-before
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee $O/run.out
