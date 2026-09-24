#!/usr/bin/env bash
# verifier-cost (pod vy-live2b-verifier-ro): `research data preserved ART...` against the pod store that put them (blobs local,
# so each blob is HEAD + single-part ETag == local MD5; no 5 GB read-back over the laptop link). Read-only minted credential via --env.
#   research run --on vy-live2b-verifier-ro --project verity --send 02-custody-check.sh --env AWS_...=.. -- bash inputs/02-custody-check.sh art:...
set -uo pipefail
W=/workspace/verifier-cost
export RESEARCH_STORE_CONFIG=$W/store.toml RESEARCH_STORE=$W/store
python3 -m research data preserved "$@"
rc=$?; echo "preserved rc=$rc" | tee ${RESEARCH_RUN_DIR:-.}/custody.txt; exit $rc
