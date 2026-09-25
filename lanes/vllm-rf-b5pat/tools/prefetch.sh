#!/bin/bash
# Fetch regression fixtures into the pod store with the read-only key in /root/r2ro.env, then delete the key (a23b's prefetch.sh,
# logs moved).  Never prints the key.
#   usage: prefetch.sh TREE [ROW]    ROW (e.g. 101) fetches only that row's artifacts into /workspace/b5pat/rows/ROW-KIND and keeps
#   them there; without ROW every row's artifacts land in the store only (gate (a) builds its row trees from the local blobs).
#   log: /workspace/b5pat/logs/prefetch[-ROW].log
T=$1; ONLY=$2
L=/workspace/b5pat/logs; mkdir -p $L
trap 'rm -f /root/r2ro.env' EXIT
cd "$T" || exit 3
set -a; . /root/r2ro.env; set +a
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
LOG=$L/prefetch${ONLY:+-$ONLY}.log
python - "$T" "$ONLY" > $L/prefetch${ONLY:+-$ONLY}.txt <<'PY'
import sys, tomllib
f = tomllib.load(open(sys.argv[1] + "/integrations/vllm/tests/regression/fixtures.toml", "rb"))
only = sys.argv[2]
if not only:
    for k, v in f.get("artifacts", {}).items():
        if v: print("top", k, v)
for rid, r in f["rows"].items():
    if only and str(r.get("row")) != only:
        continue
    for k, v in r.get("artifacts", {}).items():
        if v: print(r.get("row", rid), k, v)
PY
echo "start $(date -u +%FT%TZ) $(wc -l < $L/prefetch${ONLY:+-$ONLY}.txt) artifacts" > $LOG
while read -r row kind art; do
  if [ -n "$ONLY" ]; then d=/workspace/b5pat/rows/$row-$kind; else d=/workspace/prefetch/$row-$kind; fi
  rm -rf "$d"
  python -m research.cli data fetch "$art" --to "$d" > /dev/null 2>> $L/prefetch.err && echo "ok $row $kind" || echo "FAIL $row $kind"
  [ -z "$ONLY" ] && rm -rf "$d"
done < $L/prefetch${ONLY:+-$ONLY}.txt >> $LOG
rm -f /root/r2ro.env
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
echo "done $(date -u +%FT%TZ) ok=$(grep -c '^ok' $LOG) fail=$(grep -c '^FAIL' $LOG) key_deleted=$([ -e /root/r2ro.env ] && echo no || echo yes)" >> $LOG
cat $LOG
