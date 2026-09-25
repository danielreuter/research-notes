#!/bin/bash
# Fetch every regression row's fixtures into the pod store with the read-only key in /root/r2ro.env, then delete the key
# (baseline.md's gate (a) recipe). Never prints the key.   usage: prefetch.sh TREE     log: /workspace/a4/logs/prefetch.log
T=$1
L=/workspace/a4/logs; mkdir -p $L
trap 'rm -f /root/r2ro.env' EXIT
cd "$T" || exit 3
set -a; . /root/r2ro.env; set +a
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
python - "$T" > $L/prefetch.txt <<'PY'
import sys, tomllib
f = tomllib.load(open(sys.argv[1] + "/integrations/vllm/tests/regression/fixtures.toml", "rb"))
for k, v in f.get("artifacts", {}).items():
    if v: print("top", k, v)
for rid, r in f["rows"].items():
    for k, v in r.get("artifacts", {}).items():
        if v: print(r.get("row", rid), k, v)
PY
echo "start $(date -u +%FT%TZ) $(wc -l < $L/prefetch.txt) artifacts" > $L/prefetch.log
while read -r row kind art; do d=/workspace/prefetch/$row-$kind; rm -rf "$d"
  python -m research.cli data fetch "$art" --to "$d" > /dev/null 2>> $L/prefetch.err && echo "ok $row $kind" || echo "FAIL $row $kind"; rm -rf "$d"
done < $L/prefetch.txt >> $L/prefetch.log
rm -f /root/r2ro.env
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
echo "done $(date -u +%FT%TZ) ok=$(grep -c '^ok' $L/prefetch.log) fail=$(grep -c '^FAIL' $L/prefetch.log) key_deleted=$([ -e /root/r2ro.env ] && echo no || echo yes)" >> $L/prefetch.log
