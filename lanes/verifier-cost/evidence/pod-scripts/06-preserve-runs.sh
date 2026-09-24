#!/usr/bin/env bash
# verifier-cost: before the verifier pod is terminated, preserve this lane's pod run dirs (stdout, extraction outputs,
# custody.txt, A-GKR verify json, pytest logs) as one run-files/v1 tree. Same credential flow as 01-preserve-sessions.sh.
#   research run --on vy-live2b-verifier-ro --project verity --send 06-preserve-runs.sh --env AWS_...=.. -- bash inputs/06-preserve-runs.sh RUN...
set -euo pipefail
W=/workspace/verifier-cost
export RESEARCH_STORE_CONFIG=$W/store.toml RESEARCH_STORE=$W/store
OUT=${RESEARCH_RUN_DIR:-$PWD}
T=$W/runs-tree; rm -rf $T; mkdir -p $T
for r in "$@"; do cp -a /workspace/research/runs/$r $T/$r; done
du -sh $T
python3 - "$OUT/meta.json" "$@" <<'EOF'
import json, sys
json.dump({"lane": "verifier-cost", "label": "verifier-cost pod run dirs (vy-live2b-verifier-ro)", "runs": sys.argv[2:],
           "pod": "vy-live2b-verifier-ro pitmqu0zrycw5i EU-RO-1"}, open(sys.argv[1], "w"))
EOF
cd $T
python3 -m research data put --kind run-files/v1 --tree . --meta @$OUT/meta.json --preserve --json | tee $OUT/put.json
