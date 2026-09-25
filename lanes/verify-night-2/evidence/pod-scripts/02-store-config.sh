#!/usr/bin/env bash
# verify-night-2: the pod's research store config. No secrets here: the credential is minted on the laptop
# (research data mint-credential --env --ttl 2h), piped into /root/r2.env (mode 600) over ssh, sourced by the job scripts
# and deleted after each request.
mkdir -p /root/.research
cat > /root/.research/store.toml <<'EOF'
[remote]
type = "s3"
bucket = "verity-dev"
endpoint = "https://1d4dfa0a7dc0639e19f5d0125f14a634.r2.cloudflarestorage.com"
region = "auto"
access_key_id_env = "AWS_ACCESS_KEY_ID"
secret_access_key_env = "AWS_SECRET_ACCESS_KEY"
session_token_env = "AWS_SESSION_TOKEN"
EOF
echo ok
