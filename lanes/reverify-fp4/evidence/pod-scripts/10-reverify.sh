#!/usr/bin/env bash
# Re-verify results from lane/reverify-fp4's tree on the pod.  The pod has no store credential, so the store is a copy of the
# lane VM's local store (the results' run_files trees already fetched into it) with a filesystem remote; the verdicts and
# labels written here are copied back to the VM and pushed to R2 from there (content-addressed, so the ids do not change).
#   research run --on vy-reverify-fp4 --project verity --custody-r2 --cwd /workspace/src -- bash <this> art:... [--dry-run]
set -euo pipefail
source /workspace/env.sh
W=/workspace/reverify-fp4
mkdir -p "$W/vault" "$W/work"
printf '[remote]\ntype = "fs"\npath = "%s/vault"\n' "$W" > "$W/store.toml"
export RESEARCH_STORE=$W/store RESEARCH_STORE_CONFIG=$W/store.toml
cd /workspace/src
$PY -m backends.direct.ligero.reverify "$@" --by reverify-fp4 --jobs "$VY_CPU_THREADS" --work "$W/work"
