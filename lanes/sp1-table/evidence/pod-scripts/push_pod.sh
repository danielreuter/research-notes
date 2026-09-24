#!/bin/bash
# sp1-table (pod): push this pod's research run attempts (records + outputs + labels) to R2 before the pod is terminated.
# The credential is `research data mint-credential --env` output on STDIN, never a file; the store config holds no secret.
#   research data mint-credential --ttl 1h --env | psshi bash /workspace/sp1-table/push_pod.sh RUN_ID...
set -euo pipefail
set -a; eval "$(cat)"; set +a
C=/workspace/sp1-table/store.pod.toml
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
export PYTHONPATH=/workspace/research/tool/fdc139c9183a52e8 RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$C"
python3 -m research data push "$@" --json
