#!/usr/bin/env bash
# hash-commit (pod): register + preserve runs of /workspace/hash-commit/runs/<tag>: a run-files/v1 tree (result.json, log,
# run_id, commit-evidence.json, proofs/ with system.bin, rep1/, rust_digest.json, rust_batch.json) and a bench-result/v1
# (meta = result.json + lane/tag/label/pod, ref run_files=<tree>), both --preserve.  bash 40-register.sh TAG[=LABEL] ...
# Credential: /workspace/hash-commit/r2.env (mode 600) = `research data mint-credential --env` piped in over ssh.
# Prints "TAG tree=art:... result=art:..." and appends it to /workspace/hash-commit/registered.txt.
set -uo pipefail
HC=/workspace/hash-commit
set -a; . $HC/r2.env; set +a
C=$HC/store.pod.toml
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
POD="${POD_DESC:-vy-hash-commit}"
LANE_LABEL="${LANE_LABEL:-hash-commit}"   # commit-gpu runs: LANE_LABEL="hash-commit commit-gpu"
for arg in "$@"; do
  tag=${arg%%=*}; label=${arg#*=}; [ "$label" = "$arg" ] && label=$tag
  d=${RUNS:-$HC/runs}/$tag
  [ -f $d/result.json ] || { echo "$tag: no result.json"; continue; }
  [ -d $d/proofs ] && ( cd $d && find proofs -type f | sort | xargs sha256sum > proofs.sha256 )
  if [ -n "${SLIM:-}" ]; then   # SLIM=1: everything but the rep-1 .proof files (system.bin, statements, coins, Rust verdicts
    s=$HC/slim/$tag; rm -rf $s; mkdir -p $s   # stay; every dumped file's sha256 in proofs.sha256)
    cp -a $d/result.json $d/log $d/run_id $d/commit-evidence.json $d/proofs.sha256 $d/proofs $s/
    rm -f $s/proofs/rep1/*.proof
    d=$s
  fi
  python3 - "$d/result.json" "$label" "$tag" "$POD" "$LANE_LABEL" > $d.meta.json <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
r.update(label=f"{sys.argv[5]} {sys.argv[2]}", lane="hash-commit", tag=sys.argv[3], pod=sys.argv[4])
print(json.dumps(r))
PY
  tree=$(python3 -m research data put --kind run-files/v1 --tree $d --preserve \
    --meta "{\"lane\": \"hash-commit\", \"tag\": \"$tag\", \"label\": \"$LANE_LABEL $label\"}" | grep -o 'art:[0-9a-f]*' | tail -1)
  [ -n "$tree" ] || { echo "$tag tree put failed"; continue; }
  res=$(python3 -m research data put --kind bench-result/v1 --meta @$d.meta.json --ref run_files=$tree --preserve | grep -o 'art:[0-9a-f]*' | tail -1)
  echo "$(date -u +%H:%M:%SZ) $tag tree=$tree result=${res:-FAILED}" | tee -a $HC/registered.txt
  rm -f $d.meta.json
done
