# sourced by verify-night-3 pod scripts: env.sh + this run's minted custody key as the store remote (never printed)
source /workspace/env.sh
RID=${RESEARCH_RUN_ID:-$(basename "${RESEARCH_RUN_DIR:-$PWD}")}
C=/workspace/research/requests/$RID/custody
export RESEARCH_STORE=/workspace/research/store
export RESEARCH_STORE_CONFIG=$C/store.toml
eval "$($PY - "$C/cred.json" <<'EOF'
import json, shlex, sys
d = json.load(open(sys.argv[1]))
for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
    print(f"export {k}={shlex.quote(d[k])}")
EOF
)"
W=/workspace/verify-night-3; mkdir -p $W
R() { $PY -m research "$@"; }
