#!/usr/bin/env bash
# b-ligero-standard-hash (pod, over `research pods ssh`, never `research run`: the credential must not enter a custody tree):
# register + preserve result dirs as a run-files/v1 tree (result.json, bench.log, proofs/ with system.bin, rep1/, Rust verdicts,
# proofs.sha256) and a bench-result/v1 (meta = result.json + lane/tag/label/pod, ref run_files=<tree>), both --preserve.
#   bash 40-register.sh DIR=TAG[=LABEL] ...      (SLIM=1: drop the rep-1 .proof files, every file's sha256 stays in proofs.sha256)
# Credential: /workspace/b-lsh/r2.env (mode 600) = `research data mint-credential --ttl 8h --env` piped in over ssh.
# (adapted from lanes/hash-commit/evidence/pod-scripts/40-register.sh)
set -uo pipefail
W=/workspace/b-lsh
set -a; . $W/r2.env; set +a
C=$W/store.pod.toml
cat > "$C" <<'EOT'
[remote]
type = "s3"
bucket = "verity-dev"
endpoint = "https://1d4dfa0a7dc0639e19f5d0125f14a634.r2.cloudflarestorage.com"
region = "auto"
access_key_id_env = "AWS_ACCESS_KEY_ID"
secret_access_key_env = "AWS_SECRET_ACCESS_KEY"
session_token_env = "AWS_SESSION_TOKEN"
EOT
TOOL=$(ls -td /workspace/research/tool/*/ | head -1)
export PYTHONPATH=$TOOL RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$C"
POD="${POD_DESC:-vy-b-ligero-sh}"
for arg in "$@"; do
  d=${arg%%=*}; rest=${arg#*=}; tag=${rest%%=*}; label=${rest#*=}; [ "$label" = "$rest" ] && label=$tag
  [ -f $d/result.json ] || { echo "$tag: no result.json in $d"; continue; }
  [ -d $d/proofs ] && ( cd $d && find proofs -type f | sort | xargs sha256sum > proofs.sha256 )
  s=$W/stage/$tag; rm -rf $s; mkdir -p $s
  cp -a $d/result.json $d/bench.log $s/; [ -f $d/proofs.sha256 ] && cp -a $d/proofs.sha256 $s/
  [ -d $d/proofs ] && cp -a $d/proofs $s/
  # a live-verifier run (63-live.sh): its session records (hello / session / verdict / rust json, coins, index, logs), not
  # the sessions' proof copies (proofs/ holds rep 1)
  [ -d $d/live ] && ( cd $d && find live -maxdepth 2 -type f \( -name '*.json' -o -name '*.jsonl' -o -name '*.log' -o -name '*.coins' \) ) |
    while read -r f; do mkdir -p "$s/$(dirname "$f")"; cp -a "$d/$f" "$s/$f"; done
  [ -f $d/serve.log ] && cp -a $d/serve.log $s/
  [ -n "${SLIM:-}" ] && rm -f $s/proofs/rep1/*.proof
  python3 - "$s/result.json" "$label" "$tag" "$POD" > $s.meta.json <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
r.update(label=f"b-ligero-standard-hash {sys.argv[2]}", lane="b-ligero-standard-hash", tag=sys.argv[3], pod=sys.argv[4])
print(json.dumps(r))
PY
  tree=$(python3 -m research data put --kind run-files/v1 --tree $s --preserve \
    --meta "{\"lane\": \"b-ligero-standard-hash\", \"tag\": \"$tag\", \"label\": \"b-ligero-standard-hash $label\"}" | grep -o 'art:[0-9a-f]*' | tail -1)
  [ -n "$tree" ] || { echo "$tag tree put failed"; continue; }
  res=$(python3 -m research data put --kind bench-result/v1 --meta @$s.meta.json --ref run_files=$tree --preserve | grep -o 'art:[0-9a-f]*' | tail -1)
  echo "$(date -u +%H:%M:%SZ) $tag tree=$tree result=${res:-FAILED}" | tee -a $W/registered.txt
  rm -rf $s $s.meta.json
done
