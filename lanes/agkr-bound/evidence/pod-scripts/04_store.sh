#!/bin/bash
# agkr-bound (pod): the evidence store on R2 (credential /workspace/agkr-bound/r2.env, minted on the laptop, piped in over ssh).
#   bash 04_store.sh push RUN_ID...                       preserve --tool run attempts, then the durability gate
#   bash 04_store.sh put TREE META_JSON [--ref k=art ...]  a gate-log/v1 tree (evidence), preserved
set -euo pipefail
set -a; . /workspace/agkr-bound/r2.env; set +a
C=/workspace/agkr-bound/store.pod.toml
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
cmd=$1; shift
case $cmd in
  push) python3 -m research data push "$@" --jobs 8 --json
        timeout 600 python3 -m research data preserved "$@";;
  put)  T=$1 META=$2; shift 2
        timeout 900 python3 -m research data put --kind gate-log/v1 --tree "$T" --preserve --meta "$META" "$@";;
  *) echo "push|put"; exit 2;;
esac
