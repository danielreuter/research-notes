#!/usr/bin/env bash
# verify-night: the pod's research store config. No secrets: the credential comes from the calling shell's environment
# (research data mint-credential ... --env on the laptop, passed per ssh command, never written to a file).
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
