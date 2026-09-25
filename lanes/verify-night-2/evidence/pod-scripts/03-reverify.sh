#!/usr/bin/env bash
# verify-night-2: non-producer reverify of stored B-Ligero results, labels --by verify-night-2.
#   ROUND=<name> bash 03-reverify.sh ART...
# Credential: /root/r2.env (read-write, objects/ manifests/ labels/ attempts/; minted on the laptop, short ttl).
# Verifier: /workspace/bin/ligero-verify, cargo --release of backends/ligero-verify from /workspace/src (main ab9573fd via
# research pods sync). Pass FULL art ids: the pod catalog is not rebuilt (reindex --remote fetches manifests one by one,
# ~150/min); get_manifest / get_attempt / fetch fall back to the remote. REINDEX=1 rebuilds it first anyway.
# Then statement binding (04-stmt-binding.py): the dumped statements' chain-end y words equal the frozen set drawn by my tree.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-night-2; mkdir -p $O/rv
ROUND=${ROUND:-r$(date -u +%H%M)}
{
if [ "${REINDEX:-0}" = 1 ]; then
  echo "=== [$(date -u +%H:%M:%S)] labels-sync --pull-only + reindex --remote"
  $PY -m research data labels-sync --pull-only --jobs 16 2>&1 | tail -2
  $PY -m research data reindex --remote 2>&1 | tail -2
fi
echo "=== [$(date -u +%H:%M:%S)] reverify $*"
$PY -m backends.direct.ligero.reverify "$@" --by verify-night-2 --verifier /workspace/bin/ligero-verify --jobs 16 --work $O/rv
echo "reverify rc=$?"
echo "=== [$(date -u +%H:%M:%S)] statement binding"
$PY $RESEARCH_RUN_DIR/inputs/04-stmt-binding.py "$@" > $O/binding-$ROUND.json
echo "binding rc=$?"
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee $O/reverify-$ROUND.out
