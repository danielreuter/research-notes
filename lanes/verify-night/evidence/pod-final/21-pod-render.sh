#!/usr/bin/env bash
# verify-night: Table 2 / D2 render on the pod (the laptop catalog is wiped and its reindex is killed by the guardian's disk floor).
# The pod store was seeded with the laptop's manifests/ attempts/ labels/ (tar, AppleDouble ._* removed); `reindex --remote`
# then fetches only what the remote has and the pod lacks (results registered from other pods), and rebuilds the pod catalog.
#   bash 21-pod-render.sh TAG        (AWS_* read credential in the environment) -> /workspace/verify-night/render-TAG.{md,json}, d2-TAG.md
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
O=/workspace/verify-night; T=${1:?TAG}
{
echo "=== [$(date -u +%H:%M:%S)] labels-sync --pull-only"
$PY -m research data labels-sync --pull-only --jobs 16 2>&1 | tail -1
echo "=== [$(date -u +%H:%M:%S)] reindex --remote"
for i in 1 2 3; do $PY -m research data reindex --remote 2>&1 | tail -1 && break; done
echo "=== [$(date -u +%H:%M:%S)] render"
$PY -m verity_numerical.bench.tables --root /root/.research/store --format md > $O/render-$T.md 2>$O/render-$T.err
$PY -m verity_numerical.bench.tables --root /root/.research/store --format json > $O/render-$T.json 2>/dev/null
$PY -m verity_numerical.bench.drilldown --root /root/.research/store --format md > $O/d2-$T.md 2>/dev/null
echo "=== [$(date -u +%H:%M:%S)] done"
} > $O/pod-render-$T.out 2>&1
