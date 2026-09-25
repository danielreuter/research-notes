#!/bin/bash
# sp1-committed (laptop): register one research run of vector_run.py --backend sp1-committed (sp1-formats' reg.sh, trimmed:
# the laptop has ~3 GB free, so only proof-rep0 of the 5 reps is preserved; reps 1-4 stay in the run's R2 custody).
#   reg.sh RUN_ID "LABEL"
#   run-files/v1 = proofs/{statement.json,proof-rep0.bin} + proofs-tampered/ + result/prove/verify/negatives/measurements json
#                  + prover.log.gz + host.log.gz (preserved)
#   bench-result/v1 = result.json + {label, lane, pod_run}, ref run_files (preserved).  Prints "RUN_ID art:<result> art:<run-files>".
set -euo pipefail
rid=$1 label=$2 machine=vy-sp1-committed
set -a; source ~/.config/verity/r2.env; set +a
R=~/.research/bin/research
read -r -a SSHLINE <<< "$($R pods ssh "$machine" --print)"
W=/tmp/sp1-committed-reg/$rid; rm -rf "$W"; mkdir -p "$W/tree"
D=/workspace/research/runs/$rid
"${SSHLINE[@]}" "cd $D && gzip -kf prover.log && gzip -kf host.log && tar -cf - proofs/statement.json proofs/proof-rep0.bin proofs-tampered result.json prove.json verify.json measurements.json prover.log.gz host.log.gz \$(ls negatives.json 2>/dev/null)" \
  < /dev/null | tar -C "$W/tree" -xf -
rf=$($R data put --kind run-files/v1 --tree "$W/tree" \
     --meta "{\"listed\": [\"proofs/statement.json\", \"proofs/proof-rep0.bin\", \"proofs-tampered\", \"result.json\", \"prove.json\", \"verify.json\", \"measurements.json\", \"negatives.json\", \"prover.log.gz\", \"host.log.gz\"], \"run_id\": \"$rid\", \"lane\": \"sp1-committed\", \"omitted\": \"proofs/proof-rep1..4.bin (R2 custody of the run)\"}" \
     --preserve --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')
python3 - "$W/tree/result.json" "$label" "$machine" "$rid" > "$W/meta.json" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
m["label"] = sys.argv[2]; m["lane"] = "sp1-committed"; m["pod_run"] = sys.argv[3] + ":/workspace/research/runs/" + sys.argv[4]
print(json.dumps(m))
EOF
br=$($R data put --kind bench-result/v1 --meta @"$W/meta.json" --ref run_files="$rf" --preserve --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')
echo "$rid ${br} ${rf}"
rm -rf "$W"
