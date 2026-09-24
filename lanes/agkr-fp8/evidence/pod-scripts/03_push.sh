#!/bin/bash
# agkr-fp8 (pod): preserve research run attempts (records + outputs + labels) on R2, then the durability gate.
# Credential: /workspace/agkr-fp8/r2.env (mode 600), `research data mint-credential --env` output piped in over ssh.
#   bash 03_push.sh RUN_ID...
set -euo pipefail
set -a; . /workspace/agkr-fp8/r2.env; set +a
C=/workspace/agkr-fp8/store.pod.toml
cat > "$C" <<'EOF'
[remote]
type = "s3"
bucket = "verity-dev"
endpoint = "https://1d4dfa0a7dc0639e19f5d0125f14a634.r2.cloudflarestorage.com"
region = "auto"
access_key_id_env = "AWS_ACCESS_KEY_ID"
secret_access_key_env = "AWS_SECRET_ACCESS_KEY"
session_token_env = "AWS_SESSION_TOKEN"
EOF
TOOL=$(ls -td /workspace/research/tool/*/ | head -1)
export PYTHONPATH=$TOOL RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$C"
python3 -m research data push "$@" --jobs 8 --json
timeout 600 python3 -m research data preserved "$@"
