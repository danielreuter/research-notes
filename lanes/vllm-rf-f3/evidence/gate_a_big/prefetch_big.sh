#!/bin/bash
# gate (a) fixtures for rows #11 and #39 (+ the top-level artifacts) into the pod store with the key in /root/r2ro.env (baseline.md recipe,
# filtered to the two B=1 rows), then DELETE the key -- at the end and on any exit.
#   usage: prefetch_big.sh [TREE]      log: stdout; per-artifact logs /workspace/rff3/logs/fetch_<row>-<kind>.log
T=${1:-/workspace/head}
trap 'rm -f /root/r2ro.env' EXIT
cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
set -a; . /root/r2ro.env; set +a
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
mkdir -p /workspace/rff3/logs /workspace/prefetch
python - "$T" > /workspace/rff3/prefetch.txt <<'PY'
import sys, tomllib
f = tomllib.load(open(sys.argv[1] + "/integrations/vllm/tests/regression/fixtures.toml", "rb"))
for k, v in f.get("artifacts", {}).items():
    if v: print("top", k, v)
for rid, r in f["rows"].items():
    if r.get("row") in (11, 39):
        for k, v in r.get("artifacts", {}).items():
            if v: print(r.get("row", rid), k, v)
PY
ok=0; fail=0
while read -r row kind art; do d=/workspace/prefetch/$row-$kind; rm -rf "$d"
  if python -m research.cli data fetch "$art" --to "$d" > /workspace/rff3/logs/fetch_$row-$kind.log 2>&1; then echo "ok $row $kind $(date -u +%T)"; ok=$((ok+1))
  else echo "FAIL $row $kind $(date -u +%T): $(tail -1 /workspace/rff3/logs/fetch_$row-$kind.log | cut -c1-200)"; fail=$((fail+1)); fi
  rm -rf "$d"
done < /workspace/rff3/prefetch.txt
rm -f /root/r2ro.env; unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
echo "prefetch done ok=$ok fail=$fail $(date -u +%FT%TZ); key present: $([ -f /root/r2ro.env ] && echo yes || echo no)"
