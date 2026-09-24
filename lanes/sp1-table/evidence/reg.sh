#!/bin/bash
# sp1-table (laptop): register one research run of vector_run.py --backend sp1-bare from vy-sp1-a100.   reg.sh RUN_ID "LABEL"
#   run-files/v1 = proofs/ + result.json + prove/verify/negatives/measurements json + prover.log.gz (preserved)
#   bench-result/v1 = result.json + {label, lane, pod_run}, ref run_files (preserved).  Prints "RUN_ID art:<result> art:<run-files>".
set -euo pipefail
rid=$1 label=$2
set -a; source ~/.config/verity/r2.env; set +a
R=~/.research/bin/research
W=/tmp/sp1-table-reg/$rid; rm -rf "$W"; mkdir -p "$W/tree"
SSH=(-i /Users/danielreuter/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no
     -o UserKnownHostsFile=/Users/danielreuter/.runpod/ssh/veritor-campaign-known_hosts -o LogLevel=ERROR)
D=/workspace/research/runs/$rid
ssh -n "${SSH[@]}" -p 16521 root@154.54.102.29 "cd $D && gzip -kf prover.log && gzip -kf host.log"
src=root@154.54.102.29:$D
scp -q -r "${SSH[@]}" -P 16521 "$src/proofs" "$src/result.json" "$src/prove.json" "$src/verify.json" "$src/measurements.json" \
    "$src/prover.log.gz" "$src/host.log.gz" "$W/tree/"
scp -q "${SSH[@]}" -P 16521 "$src/negatives.json" "$W/tree/" 2>/dev/null || true
rf=$($R data put --kind run-files/v1 --tree "$W/tree" \
     --meta "{\"listed\": [\"proofs\", \"result.json\", \"prove.json\", \"verify.json\", \"measurements.json\", \"negatives.json\", \"prover.log.gz\", \"host.log.gz\"], \"run_id\": \"$rid\", \"lane\": \"sp1-table\"}" \
     --preserve --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')
python3 - "$W/tree/result.json" "$label" "$rid" > "$W/meta.json" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
m["label"] = sys.argv[2]; m["lane"] = "sp1-table"; m["pod_run"] = "vy-sp1-a100:/workspace/research/runs/" + sys.argv[3]
print(json.dumps(m))
EOF
br=$($R data put --kind bench-result/v1 --meta @"$W/meta.json" --ref run_files="$rf" --preserve --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')
echo "$rid art:${br} art:${rf}"
rm -rf "$W"
