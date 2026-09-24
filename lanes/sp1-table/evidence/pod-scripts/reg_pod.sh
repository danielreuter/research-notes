#!/bin/bash
# sp1-table (pod): register one research run of vector_run.py --backend sp1-bare from this pod straight to R2 (the laptop's
# reg.sh cannot run while the laptop is under the guardian's disk floor).  Same artifacts as reg.sh:
#   run-files/v1 = proofs/ + result.json + prove/verify/negatives/measurements json + prover.log.gz + host.log.gz (preserved)
#   bench-result/v1 = result.json + {label, lane, pod_run}, ref run_files (preserved).
# The credential is `research data mint-credential --env` output on STDIN, never a file; the store config holds no secret.
#   printf '%s\n' "$CREDS" | ssh pod bash /workspace/sp1-table/reg_pod.sh RUN_ID "LABEL"   ->  "RUN_ID art:<result> art:<run-files>"
set -euo pipefail
rid=$1 label=$2
set -a; eval "$(cat)"; set +a
C=/workspace/sp1-table/store.pod.toml
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
export PYTHONPATH=/workspace/research/tool/fdc139c9183a52e8 RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$C
D=/workspace/research/runs/$rid
W=/workspace/sp1-table/reg/$rid; rm -rf "$W"; mkdir -p "$W/tree"
cp -r "$D/proofs" "$D/result.json" "$D/prove.json" "$D/verify.json" "$D/measurements.json" "$W/tree/"
[ -f "$D/negatives.json" ] && cp "$D/negatives.json" "$W/tree/"
gzip -c "$D/prover.log" > "$W/tree/prover.log.gz"
gzip -c "$D/host.log" > "$W/tree/host.log.gz"
id() { python3 -c 'import json,sys; d=json.load(sys.stdin); assert (d.get("preserve") or {}).get("preserved"), d; print(d["id"])'; }
rf=$(python3 -m research data put --kind run-files/v1 --tree "$W/tree" \
     --meta "{\"listed\": [\"proofs\", \"result.json\", \"prove.json\", \"verify.json\", \"measurements.json\", \"negatives.json\", \"prover.log.gz\", \"host.log.gz\"], \"run_id\": \"$rid\", \"lane\": \"sp1-table\"}" \
     --preserve --json | id)
python3 - "$W/tree/result.json" "$label" "$rid" > "$W/meta.json" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
m["label"] = sys.argv[2]; m["lane"] = "sp1-table"; m["pod_run"] = "vy-sp1-a100:/workspace/research/runs/" + sys.argv[3]
print(json.dumps(m))
EOF
br=$(python3 -m research data put --kind bench-result/v1 --meta @"$W/meta.json" --ref run_files="$rf" --preserve --json | id)
echo "$rid art:${br#art:} art:${rf#art:}"
rm -rf "$W"
