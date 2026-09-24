#!/bin/bash
# put_pack.sh TAG POD : one run-files/v1 tree per run (result json, Rust verdict json, bench + Rust logs, proofs/ = the rep-1 dump
# with system.bin + manifest.json) put into the pod-side store and PRESERVED on R2 (temporary credential); prints the art id.
set -a; source /workspace/r2tmp.env; set +a
export PYTHONPATH=/workspace/qol-research
TAG=$1; POD=$2; O=/workspace/v3s; D=$O/pack/$TAG
rm -rf $D; mkdir -p $D
cp $O/results/$TAG.json $D/result.json
[ -f $O/results/${TAG}_rust.json ] && cp $O/results/${TAG}_rust.json $D/rust_verdict.json
cp $O/logs/$TAG.log $D/bench.log; [ -f $O/logs/${TAG}_rust.log ] && cp $O/logs/${TAG}_rust.log $D/rust.log
[ -d $O/dumps/$TAG ] && cp -al $O/dumps/$TAG $D/proofs
cp /workspace/chain.sh $D/chain.sh
cat /workspace/src/.research-source.json > $D/source.json
META=$(/workspace/venv312/bin/python - "$D" "$TAG" "$POD" <<'EOF'
import json, sys
d, tag, pod = sys.argv[1:]
r = json.load(open(f"{d}/result.json"))
wf = r["workload_fingerprint"]
m = {x["name"]: x["value"] for x in r["measurements"]}
print(json.dumps({"lane": "v3-scout", "by": "v3-scout", "tag": tag, "run_id": r.get("run_id"), "pod": pod,
                  "relation": wf["software"]["backend"]["name"], "batch": wf["security"]["rs_l"],
                  "pipeline": wf["software"]["backend"].get("pipeline"), "total_vus": wf["B"], "zk": wf["security"]["zk"],
                  "coins": "local (interactive, in-process verifier coins)", "tree": "5e6b3e3", "t_total": m["t.total"],
                  "gpu": wf["hardware"]["gpu"]["name"]}))
EOF
)
/workspace/venv312/bin/python -m research data put --store /workspace/store --kind run-files/v1 --tree $D --meta "$META" --preserve --json
