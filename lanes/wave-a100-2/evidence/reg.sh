#!/bin/bash
# wave-a100-2 (laptop): register one pod run dir.   reg.sh TAG "LABEL" [dump]
#   dump: pull runs/TAG/proofs too -> run-files/v1 tree (preserved), referenced as run_files by the bench-result.
#   Always: bench-result/v1 = runs/TAG/result.json + {label, lane} (preserved). Prints "TAG art:<result> [art:<run-files>]".
set -euo pipefail
tag=$1 label=$2 dump=${3:-}
set -a; source ~/.config/verity/r2.env; set +a
R=~/.research/bin/research
W=/tmp/wa2/reg/$tag; rm -rf $W; mkdir -p $W
SCP=(scp -q -r -i /Users/danielreuter/.runpod/ssh/runpodctl-ssh-key -P 12629 -o StrictHostKeyChecking=no
     -o UserKnownHostsFile=/Users/danielreuter/.runpod/ssh/veritor-campaign-known_hosts -o LogLevel=ERROR)
src=root@213.173.102.5:/workspace/wave-a100/runs/$tag
"${SCP[@]}" $src/result.json $src/meta.txt $W/
refs=()
rf=""
if [ "$dump" = dump ]; then
  mkdir -p $W/tree; "${SCP[@]}" $src/proofs $W/tree/
  for f in rust_batch.json rust_batch.out; do "${SCP[@]}" $src/$f $W/tree/ 2>/dev/null || true; done
  cp $W/result.json $W/meta.txt $W/tree/
  rf=$($R data put --kind run-files/v1 --tree $W/tree --meta "{\"listed\": [\"proofs\"], \"run_id\": \"wave-a100-2/$tag\", \"lane\": \"wave-a100-2\"}" --preserve --json \
       | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')
  refs=(--ref run_files=$rf)
fi
python3 - "$W/result.json" "$label" "$tag" > $W/meta.json <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
m["label"] = sys.argv[2]; m["lane"] = "wave-a100-2"; m.setdefault("run_id", "wave-a100-2/" + sys.argv[3])
print(json.dumps(m))
EOF
br=$($R data put --kind bench-result/v1 --meta @$W/meta.json ${refs[@]+"${refs[@]}"} --preserve --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')
echo "$tag ${br:0:12} ${rf:0:12}"
[ "$dump" = dump ] && rm -rf $W/tree
exit 0
