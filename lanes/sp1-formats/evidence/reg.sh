#!/bin/bash
# sp1-formats (laptop): register one research run of vector_run.py --backend sp1-bare (sp1-table's reg.sh, per pod).
#   reg.sh MACHINE RUN_ID "LABEL"      MACHINE in vy-sp1f-4090 | vy-sp1f-5090 | vy-sp1f-h100 (ssh from `research pods ssh --print`)
#   run-files/v1 = proofs/ + result.json + prove/verify/negatives/measurements json + prover.log.gz + host.log.gz (preserved)
#   bench-result/v1 = result.json + {label, lane, pod_run}, ref run_files (preserved).  Prints "RUN_ID art:<result> art:<run-files>".
set -euo pipefail
machine=$1 rid=$2 label=$3
set -a; source ~/.config/verity/r2.env; set +a
R=~/.research/bin/research
read -r -a SSHLINE <<< "$($R pods ssh "$machine" --print)"
W=/tmp/sp1-formats-reg/$rid; rm -rf "$W"; mkdir -p "$W/tree"
D=/workspace/research/runs/$rid
"${SSHLINE[@]}" "cd $D && gzip -kf prover.log && gzip -kf host.log && tar -cf - proofs result.json prove.json verify.json measurements.json prover.log.gz host.log.gz \$(ls negatives.json 2>/dev/null)" \
  < /dev/null | tar -C "$W/tree" -xf -
rf=$($R data put --kind run-files/v1 --tree "$W/tree" \
     --meta "{\"listed\": [\"proofs\", \"result.json\", \"prove.json\", \"verify.json\", \"measurements.json\", \"negatives.json\", \"prover.log.gz\", \"host.log.gz\"], \"run_id\": \"$rid\", \"lane\": \"sp1-formats\"}" \
     --preserve --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')
python3 - "$W/tree/result.json" "$label" "$machine" "$rid" > "$W/meta.json" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
m["label"] = sys.argv[2]; m["lane"] = "sp1-formats"; m["pod_run"] = sys.argv[3] + ":/workspace/research/runs/" + sys.argv[4]
print(json.dumps(m))
EOF
br=$($R data put --kind bench-result/v1 --meta @"$W/meta.json" --ref run_files="$rf" --preserve --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')
echo "$rid art:${br} art:${rf}"
rm -rf "$W"
