#!/bin/bash
# sp1-128 (pod): register one research run of backends/sp1/sec128/run.sh from this pod straight to R2 (after sp1-table's
# reg_pod.sh).  run-files/v1 = proofs/ + result.json + prove/verify/negatives/measurements json + prover.log.gz +
# host.log.gz + variant.json + sec128-checks.json (preserved); bench-result/v1 = result.json + {label, lane, pod_run},
# ref run_files (preserved).  The credential is `research data mint-credential --env` output on STDIN, never a file.
#   research data mint-credential --ttl 1h --env | research pods ssh POD -- bash /workspace/sec128/reg_pod.sh RUN_ID "LABEL"
set -euo pipefail
rid=$1 label=$2
set -a; eval "$(cat)"; set +a
C=/workspace/sec128/store.pod.toml
cat > $C <<'EOF'
[remote]
type = "s3"
bucket = "verity-dev"
endpoint = "https://1d4dfa0a7dc0639e19f5d0125f14a634.r2.cloudflarestorage.com"
region = "auto"
access_key_id_env = "AWS_ACCESS_KEY_ID"
secret_access_key_env = "AWS_SECRET_ACCESS_KEY"
session_token_env = "AWS_SESSION_TOKEN"
EOF
TOOL=$(ls -td /workspace/research/tool/*/ | head -1)
export PYTHONPATH=${TOOL%/} RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$C
D=/workspace/research/runs/$rid
[ -f "$D/result.json" ] || D=$(dirname "$(ls "$D"/*/result.json "$D"/*/*/result.json 2>/dev/null | head -1)")
W=/workspace/sec128/reg/$rid; rm -rf "$W"; mkdir -p "$W/tree"
cp -r "$D/proofs" "$D/result.json" "$D/prove.json" "$D/verify.json" "$D/measurements.json" "$D/variant.json" \
  "$D/sec128-checks.json" "$W/tree/"
[ -f "$D/negatives.json" ] && cp "$D/negatives.json" "$W/tree/"
gzip -c "$D/prover.log" > "$W/tree/prover.log.gz"
gzip -c "$D/host.log" > "$W/tree/host.log.gz"
id() { python3 -c 'import json,sys; d=json.load(sys.stdin); assert (d.get("preserve") or {}).get("preserved"), d; print(d["id"])'; }
rf=$(python3 -m research data put --kind run-files/v1 --tree "$W/tree" \
     --meta "{\"listed\": [\"proofs\", \"result.json\", \"prove.json\", \"verify.json\", \"measurements.json\", \"negatives.json\", \"prover.log.gz\", \"host.log.gz\", \"variant.json\", \"sec128-checks.json\"], \"run_id\": \"$rid\", \"lane\": \"sp1-128\"}" \
     --preserve --json | id)
python3 - "$W/tree/result.json" "$label" "$rid" > "$W/meta.json" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
m["label"] = sys.argv[2]; m["lane"] = "sp1-128"; m["pod_run"] = "vy-sp1-128-a100:/workspace/research/runs/" + sys.argv[3]
print(json.dumps(m))
EOF
br=$(python3 -m research data put --kind bench-result/v1 --meta @"$W/meta.json" --ref run_files="$rf" --preserve --json | id)
echo "$rid art:${br#art:} art:${rf#art:}"
rm -rf "$W"
