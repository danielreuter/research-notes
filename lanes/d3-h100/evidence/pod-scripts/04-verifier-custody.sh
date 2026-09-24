#!/usr/bin/env bash
# d3-h100 verifier (vy-d3-h100v): preserve the live verifier's own records of every session it served (kb/live-verifier.md: the
# small records, not the proofs, which the prover's run-files trees carry): index.jsonl, serve.log, per session hello.json,
# session.json, verdict.json, rust_*.json, sub_*.coins, + serve.out and a sha256 list. One run-files/v1, --preserve.
set -uo pipefail
PY=/workspace/venv312/bin/python; SRC=/workspace/src
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
set -a; source /workspace/d3-h100/cred.env; set +a
export RESEARCH_STORE=/workspace/store RESEARCH_STORE_CONFIG=$SRC/tools/research/store.pod.toml
D=/workspace/d3-h100/verifier-records; rm -rf $D; mkdir -p $D
cd /workspace/live/sessions
find . -maxdepth 2 \( -name index.jsonl -o -name serve.log -o -name hello.json -o -name session.json -o -name verdict.json \
     -o -name 'rust_*.json' -o -name 'sub_*.coins' \) -print0 | tar cf - --null -T - | tar xf - -C $D
cp /workspace/live/serve.out $D/serve.out; cp /workspace/live/start.sh $D/start.sh
cd $D && find . -type f ! -name sha256.txt -print0 | sort -z | xargs -0 sha256sum > sha256.txt
echo "sessions=$(ls -d s* 2>/dev/null | wc -l) files=$(find . -type f | wc -l) bytes=$(du -sb . | cut -f1)"
meta=$($PY -c 'import json; print(json.dumps({"lane": "d3-h100", "label": "d3-h100 live verifier records (vy-d3-h100v cpu3c 4 vCPU, US-MO-1, host e5e505739a45, live-verifier@1d9c3198bbd7, ligero-verify 72565600)", "pod": "vy-d3-h100v (4tdtl6xuhxaa3o, US-MO-1)"}))')
$PY -m research data put --kind run-files/v1 --tree . --meta "$meta" --preserve --json | $PY -c 'import json,sys; d=json.load(sys.stdin); print("records", d["id"], "preserved" if (d.get("preserve") or {}).get("preserved") else "NOT PRESERVED")'
