#!/usr/bin/env bash
# fill-consumer (POD side): register runs from /workspace/fill-consumer/runs, one at a time, into the pod's store and R2:
#   run-files/v1   the run dir (result.json, log, run_id, proofs/)                       --preserve
#   bench-result/v1 meta = result.json unchanged (run_id as the runner wrote it) + lane / tag / label / pod, ref run_files  --preserve
# The R2 credential comes from the calling shell's environment only (laptop: research data mint-credential --env); nothing
# is written to a file. /root/.research/store.toml names the bucket (no secrets). Appends "TAG result=art: run_files=art: run_id="
# to /workspace/fill-consumer/registered.txt.   Usage: POD="vy-fill-consumer-4090 (RTX 4090)" bash 60-register.sh TAG...
set -uo pipefail
source /workspace/env.sh
FC=/workspace/fill-consumer; O=$FC/runs; OUT=$FC/registered.txt; touch $OUT
: "${AWS_ACCESS_KEY_ID:?no R2 credential in the environment}" "${POD:?}"
for tag in "$@"; do
  grep -q "^$tag " $OUT && { echo "$tag already registered"; continue; }
  d=$O/$tag
  [ -f $d/result.json ] && [ -d $d/proofs ] || { echo "$tag: no result.json / proofs"; continue; }
  rid=$(cat $d/run_id)
  n=$(find $d -type f | wc -l | tr -d ' ')
  tree=$($PY -m research data put --kind run-files/v1 --tree $d --preserve \
      --meta "{\"run_id\": \"$rid\", \"files\": $n, \"listed\": [\"result.json\", \"log\", \"run_id\", \"proofs\"], \"missing\": [], \"lane\": \"fill-consumer\", \"tag\": \"$tag\"}" \
      2>&1 | tee -a $FC/register.log | grep -o 'art:[0-9a-f]*' | tail -1)
  [ -n "$tree" ] || { echo "$tag: run-files put failed (register.log)"; continue; }
  m=$(mktemp /tmp/fc-meta.XXXX.json)
  $PY - $d/result.json "$tag" "$POD" > $m <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
r.update(lane="fill-consumer", tag=sys.argv[2], label=f"fill-consumer {sys.argv[2]}", pod=sys.argv[3])
print(json.dumps(r))
PY
  res=$($PY -m research data put --kind bench-result/v1 --meta @$m --ref run_files=$tree --preserve 2>&1 | tee -a $FC/register.log | grep -o 'art:[0-9a-f]*' | tail -1)
  rm -f $m
  [ -n "$res" ] || { echo "$tag: bench-result put failed (register.log)"; continue; }
  echo "$tag result=$res run_files=$tree run_id=$rid" | tee -a $OUT
done
