#!/usr/bin/env bash
# fill-dc (laptop): preserve a live verifier's session records as run-files/v1, put from the verifier's pod.
#   put-sessions.sh h100|a100v      (FDC_CREDS = `research data mint-credential --env` output, this shell only)
# The tree is /workspace/live/sessions minus the received proof bytes (the prover-side dumps hold rep 1 of each run):
# index.jsonl, serve.log, and every session's hello / session / verdict / rust_*.json.
set -uo pipefail
pod=$1
OUT=~/.research/notes/lanes/fill-dc/evidence/registered.txt
K=(-i /Users/danielreuter/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/Users/danielreuter/.runpod/ssh/veritor-campaign-known_hosts -o ServerAliveInterval=30 -o LogLevel=ERROR -o ConnectTimeout=15)
case $pod in
  h100) S=(ssh "${K[@]}" -p 10179 root@91.199.227.82); PODNAME="vy-fill-dc-h100 same-pod verifier (niced), EU-NL-1" ;;
  a100v) S=(ssh "${K[@]}" -p 36022 root@157.157.221.29); PODNAME="vy-fill-dc-a100v cpu3c verifier, EUR-IS-1" ;;
  *) echo "pod h100|a100v"; exit 2 ;;
esac
[ -n "${FDC_CREDS:-}" ] || { echo "FDC_CREDS unset"; exit 2; }
meta=$(python3 -c 'import json,sys; print(json.dumps({"lane": "fill-dc", "label": "fill-dc live verifier session records " + sys.argv[1], "pod": sys.argv[1], "listed": ["index.jsonl", "serve.log", "s*/"]}))' "$PODNAME")
tid=$(printf '%s\n' "$FDC_CREDS" | "${S[@]}" "set -a; eval \"\$(cat)\"; set +a; source /workspace/env.sh 2>/dev/null; PY=\${PY:-/workspace/venv312/bin/python}; T=/tmp/fdc-sessions; rm -rf \$T; mkdir -p \$T;
    cd /workspace/live/sessions && find . \( -name '*.json' -o -name '*.jsonl' -o -name '*.log' \) -exec cp --parents {} \$T/ \; ;
    cd \$T && echo \"staged \$(find . -type f | wc -l) files \$(du -sh . | cut -f1)\" >&2;
    PYTHONPATH=/workspace/src/tools/research/src RESEARCH_STORE=/workspace/store RESEARCH_STORE_CONFIG=/workspace/src/tools/research/store.pod.toml \
    \$PY -m research data put --kind run-files/v1 --tree . --meta '$meta' --preserve --json" 2>/tmp/fdc-sess.err \
    | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"] if (d.get("preserve") or {}).get("preserved") else "")' 2>/dev/null)
[ -n "$tid" ] || { echo "session put FAILED ($(tail -3 /tmp/fdc-sess.err | tr '\n' ' '))"; exit 1; }
line="$(date -u +%H:%MZ) $pod sessions tree=$tid | $(grep staged /tmp/fdc-sess.err) | $PODNAME"
echo "$line" | tee -a $OUT
