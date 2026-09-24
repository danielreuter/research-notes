#!/bin/bash
# fetch every regression row fixture into the pod store with /root/r2ro.env, then delete the key (also on failure)
trap "rm -f /root/r2ro.env" EXIT
T=/workspace/base
cd $T || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
set -a; . /root/r2ro.env; set +a
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
python - "$T" > /workspace/rff3/prefetch.txt <<"PY"
import sys, tomllib
f = tomllib.load(open(sys.argv[1] + "/integrations/vllm/tests/regression/fixtures.toml", "rb"))
for k, v in f.get("artifacts", {}).items():
    if v: print("top", k, v)
for rid, r in f["rows"].items():
    for k, v in r.get("artifacts", {}).items():
        if v: print(r.get("row", rid), k, v)
PY
while read -r row kind art; do d=/workspace/prefetch/$row-$kind; rm -rf "$d"
  python -m research.cli data fetch "$art" --to "$d" > /dev/null 2>>/workspace/rff3/logs/prefetch.err && echo "ok $row $kind" || echo "FAIL $row $kind"; rm -rf "$d"
done < /workspace/rff3/prefetch.txt
rm -f /root/r2ro.env; unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
echo "prefetch done $(date -u +%FT%TZ); key present: $(test -e /root/r2ro.env && echo yes || echo no)"
