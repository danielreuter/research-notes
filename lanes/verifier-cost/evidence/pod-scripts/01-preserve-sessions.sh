#!/usr/bin/env bash
# verifier-cost (pod vy-live2b-verifier-ro): preserve the WHOLE 2026-09-23 live session store (/workspace/live/sessions,
# ~5.0 GB incl. sub_NN.proof / .stmt / .coins) to R2 as one run-files/v1 tree, from the pod.
#   research run --on vy-live2b-verifier-ro --project verity --send 01-preserve-sessions.sh \
#     --env AWS_ACCESS_KEY_ID=.. --env AWS_SECRET_ACCESS_KEY=.. --env AWS_SESSION_TOKEN=.. -- bash inputs/01-preserve-sessions.sh
# Credential: `research data mint-credential --ttl 3h --env` on the laptop (short-lived, never the account key, never a file).
# Reads /workspace/live/sessions only; writes the run dir and /workspace/verifier-cost/.
set -euo pipefail
SRC=/workspace/live/sessions
W=/workspace/verifier-cost; mkdir -p $W
cat > $W/store.toml <<'EOF'
[remote]
type = "s3"
bucket = "verity-dev"
endpoint = "https://1d4dfa0a7dc0639e19f5d0125f14a634.r2.cloudflarestorage.com"
region = "auto"
access_key_id_env = "AWS_ACCESS_KEY_ID"
secret_access_key_env = "AWS_SECRET_ACCESS_KEY"
session_token_env = "AWS_SESSION_TOKEN"
EOF
export RESEARCH_STORE_CONFIG=$W/store.toml RESEARCH_STORE=$W/store
OUT=${RESEARCH_RUN_DIR:-$PWD}
cd $SRC
find . -type f | sort > $OUT/files.txt
echo "files $(wc -l < $OUT/files.txt) bytes $(du -sb . | cut -f1) sessions $(ls -d */ | wc -l)" | tee $OUT/summary.txt
xargs -a $OUT/files.txt -d '\n' -P 4 -n 64 sha256sum > $OUT/sha256.unsorted
sort -k2 $OUT/sha256.unsorted > $OUT/sha256.txt; rm $OUT/sha256.unsorted
cp index.jsonl $OUT/index.jsonl
python3 - "$OUT/meta.json" <<'EOF'
import json, sys
json.dump({"lane": "verifier-cost", "label": "vy-live2b-verifier-ro live session store 2026-09-23 (whole tree: records + proofs, stmts, coins)",
           "pod": "vy-live2b-verifier-ro pitmqu0zrycw5i cpu3m EU-RO-1", "source": "/workspace/live/sessions",
           "server": "backends.direct.ligero.live serve --jobs 8 --threads 1 --target-bits 128 (/workspace/lv-src)"},
          open(sys.argv[1], "w"))
EOF
python3 -m research data put --kind run-files/v1 --tree . --meta @$OUT/meta.json --preserve --json > $OUT/put.json
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print("tree", d["id"], "preserved", (d.get("preserve") or {}).get("preserved"))' $OUT/put.json | tee -a $OUT/summary.txt
