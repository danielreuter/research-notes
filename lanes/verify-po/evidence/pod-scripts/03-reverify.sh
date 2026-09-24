#!/usr/bin/env bash
# verify-po: non-producer reverify of stored B-Ligero results, labels --by verify-po.
#   ROUND=<name> bash 03-reverify.sh ART...
# Credential: /root/r2.env (read-write, objects/ manifests/ labels/ attempts/; minted on the laptop, short ttl).
# Verifier: /workspace/bin/ligero-verify, cargo --release of backends/ligero-verify from /workspace/src (main ab9573fd via
# research pods sync). Pod catalog first: labels-sync --pull-only + reindex --remote so attempts_by_output resolves the run.
# Then statement binding (04-stmt-binding.py): the dumped statements' chain-end y words equal the frozen set drawn by my tree.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po; mkdir -p $O/rv
ROUND=${ROUND:-r$(date -u +%H%M)}
{
echo "=== [$(date -u +%H:%M:%S)] labels-sync --pull-only"
$PY -m research data labels-sync --pull-only --jobs 16 2>&1 | tail -2
echo "=== [$(date -u +%H:%M:%S)] reindex --remote"
for i in 1 2 3; do $PY -m research data reindex --remote 2>&1 | tail -2 && break; done
echo "=== [$(date -u +%H:%M:%S)] reverify $*"
$PY -m backends.direct.ligero.reverify "$@" --by verify-po --verifier /workspace/bin/ligero-verify --jobs 16 --work $O/rv
echo "reverify rc=$?"
echo "=== [$(date -u +%H:%M:%S)] statement binding"
$PY $RESEARCH_RUN_DIR/inputs/04-stmt-binding.py "$@" > $O/binding-$ROUND.json
echo "binding rc=$?"
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee $O/reverify-$ROUND.out
