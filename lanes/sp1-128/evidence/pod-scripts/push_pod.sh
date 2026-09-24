#!/bin/bash
# sp1-128 (pod) (copy of sp1-table/evidence/pod-scripts/push_pod.sh): push this pod's research run attempts (records + outputs + labels) to R2 before the pod is terminated.
# The credential is `research data mint-credential --env` output on STDIN, never a file; the store config holds no secret.
#   research data mint-credential --ttl 1h --env | research pods ssh POD -- bash /workspace/sec128/push_pod.sh RUN_ID...
set -euo pipefail
set -a; eval "$(cat)"; set +a
C=/workspace/sec128/store.pod.toml
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
export PYTHONPATH=${TOOL%/} RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$C"
python3 -m research data push "$@" --json
