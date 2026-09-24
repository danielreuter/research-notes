#!/usr/bin/env bash
# d3-h100: preserve this pod's `research run` dirs (launch/status/stdout/stderr/resources of every job) + /workspace/d3-h100
# summary.txt and registered.txt as one run-files/v1 before the pod is terminated. Run over ssh (short) on the prover.
set -uo pipefail
source /workspace/env.sh
set -a; source /workspace/d3-h100/cred.env; set +a
export RESEARCH_STORE=/workspace/store RESEARCH_STORE_CONFIG=/workspace/src/tools/research/store.pod.toml
D=/workspace/d3-h100/pod-runs; rm -rf $D; mkdir -p $D
cp -r /workspace/research/runs $D/runs; cp /workspace/d3-h100/summary.txt /workspace/d3-h100/registered.txt $D/
cd $D && find . -type f ! -name sha256.txt -print0 | sort -z | xargs -0 sha256sum > sha256.txt
meta=$($PY -c 'import json; print(json.dumps({"lane": "d3-h100", "label": "d3-h100 prover pod run dirs + summary (vy-d3-h100 H100 US-MO-1)", "pod": "vy-d3-h100 (r79m8t4m58gq8o, US-MO-1)"}))')
$PY -m research data put --kind run-files/v1 --tree . --meta "$meta" --preserve --json | $PY -c 'import json,sys; d=json.load(sys.stdin); print("runs", d["id"], "preserved" if (d.get("preserve") or {}).get("preserved") else "NOT PRESERVED")'
