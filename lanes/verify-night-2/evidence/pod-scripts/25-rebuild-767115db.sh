#!/usr/bin/env bash
# verify-night-2 11:00Z: /workspace/src = main 767115db (the sha256 leaf scheme merged; red team 1041Z: both class verdicts hold
# there). Rebuild ligero-verify from it (14, no pytest), keep 596529d2, then a LABEL=0 smoke test on an accepted +blake3 cell.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
I=$RESEARCH_RUN_DIR/inputs
[ -f /workspace/bin/ligero-verify-596529d2 ] || cp -p /workspace/bin/ligero-verify /workspace/bin/ligero-verify-596529d2
echo "=== [$(date -u +%H:%M:%S)] rebuild ligero-verify @ $(python3 -c "import json;print(json.load(open('/workspace/src/.research-source.json'))['commit'][:8])")"
PYTEST=0 bash $I/14-rebuild.sh | grep -vE '^\s*$'
LV=$(sha256sum /workspace/bin/ligero-verify | cut -c1-8)
export VN2_VDESC="ligero-verify sha256 $LV (main 767115db)"
echo "verifier: $VN2_VDESC"
echo "=== [$(date -u +%H:%M:%S)] smoke: art:e7d59ab6 at 767115db, LABEL=0"
TAG=smoke-767115db VN2_N=4096 LABEL=0 NEG=0 PV_NOTE="smoke" bash $I/20-cells.sh \
  art:08225c8c209777cde883d544ed19b59704b2e9d3e8c60000137b5f2cdbfa1c4a -- art:e7d59ab6a7bad2140c776f1d160efa302f46439ea1ceda9edff68d228a6df022
echo "=== [$(date -u +%H:%M:%S)] 25 done"
