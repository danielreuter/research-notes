#!/bin/bash
# The gate (a) credential route (vllm-refactor/20260924T1942Z-gate-a-credential-route.md, recipe in vllm-rf-a1/baseline.md): fetch every
# regression row's fixtures into the pod store, then delete the key at once.  Lane f24's prefetch.sh, except that each row's `records`
# tree and the top-level `commit_logs` are kept under /workspace/regress/<kind>/<row id> for the verdict byte comparison (verdict_bytes.py).
#   usage: prefetch.sh TREE   log: /workspace/out/gates/prefetch.log
T=$1; L=/workspace/out/gates/prefetch.log; mkdir -p /workspace/out/gates /workspace/prefetch /workspace/regress
trap 'rm -f /root/r2ro.env' EXIT
cd "$T" || exit 3
set -a; . /root/r2ro.env; set +a
export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
python - "$PWD" > /workspace/prefetch.txt <<'PY'
import sys, tomllib
f = tomllib.load(open(sys.argv[1] + "/integrations/vllm/tests/regression/fixtures.toml", "rb"))
for k, v in f.get("artifacts", {}).items():
    if v: print("top", k, v)
for rid, r in f["rows"].items():
    for k, v in r.get("artifacts", {}).items():
        if v: print(rid, k, v)
PY
echo "start $(date -u +%FT%TZ) $(wc -l < /workspace/prefetch.txt) artifacts" > $L
while read -r row kind art; do d=/workspace/prefetch/$row-$kind; rm -rf "$d"
  t0=$(date +%s)
  python -m research.cli data fetch "$art" --to "$d" > /dev/null 2>>$L.err && echo "ok $row $kind $(( $(date +%s) - t0 ))s" >> $L || echo "FAIL $row $kind" >> $L
  if [ -d "$d" ] && { [ "$kind" = records ] || [ "$kind" = commit_logs ]; }; then
    mkdir -p /workspace/regress/$kind; rm -rf "/workspace/regress/$kind/$row"; mv "$d" "/workspace/regress/$kind/$row"
  else rm -rf "$d"; fi
done < /workspace/prefetch.txt
rm -f /root/r2ro.env; unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
echo "key deleted; done $(date -u +%FT%TZ)" >> $L
