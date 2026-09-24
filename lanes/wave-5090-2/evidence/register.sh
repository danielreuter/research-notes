#!/usr/bin/env bash
# wave-5090-2 (laptop): pull pod run dirs and register each as run-files/v1 (proofs/ + log) + bench-result/v1 (refs.run_files), both --preserve.
# Usage: bash register.sh TAG...   -> appends "TAG result=art:... run_files=art:..." to registered.txt
set -uo pipefail
set -a; source ~/.config/verity/r2.env; set +a
R=~/.research/bin/research
L=~/.research/notes/lanes/wave-5090-2/evidence
W=/tmp/w5090-2/runs; mkdir -p $W
K=(-i $HOME/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no -o UserKnownHostsFile=$HOME/.runpod/ssh/veritor-campaign-known_hosts -o LogLevel=ERROR)
for tag in "$@"; do
  grep -q "^$tag " $L/registered.txt 2>/dev/null && { echo "$tag already registered"; continue; }
  rsync -a -e "ssh ${K[*]} -p 41258" root@213.173.103.87:/workspace/wave-5090-2/runs/$tag/ $W/$tag/ || { echo "$tag: pull failed"; continue; }
  d=$W/$tag; s=$W/$tag.stage; rm -rf $s; mkdir -p $s; cp -R $d/proofs $s/proofs; cp $d/log $s/log
  n=$(find $s -type f | wc -l | tr -d ' ')
  rf=$($R data put --kind run-files/v1 --tree $s --preserve \
        --meta "{\"run_id\": \"w5090-2-$tag\", \"files\": $n, \"listed\": [\"proofs\", \"log\"], \"missing\": [], \"lane\": \"wave-5090-2\"}" | grep -o 'art:[0-9a-f]*' | head -1)
  [ -n "$rf" ] || { echo "$tag: run-files put failed"; continue; }
  python3 - $d/result.json $d/meta.json <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
m = {k: v for k, v in d.items() if k not in ("artifacts", "measurement_files")}
m["lane"] = "wave-5090-2"
json.dump(m, open(sys.argv[2], "w"))
PY
  res=$($R data put --kind bench-result/v1 --meta @$d/meta.json --ref run_files=$rf --preserve | grep -o 'art:[0-9a-f]*' | head -1)
  [ -n "$res" ] || { echo "$tag: result put failed"; continue; }
  echo "$tag result=$res run_files=$rf" | tee -a $L/registered.txt
  rm -rf $s
done
