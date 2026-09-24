#!/usr/bin/env bash
# d3-h100 prover: register every finished live run dir from the pod (credential: /workspace/d3-h100/cred.env, minted on the laptop
# with `research data mint-credential --ttl 3h --env`, copied over ssh, never committed).
#   bash 03-register.sh TAG...     -> per TAG: run-files/v1 (the dir: result.json, log, meta.txt, proofs/) and bench-result/v1 =
#   result.json unchanged + {label, lane, tag, pod}, ref run_files; both --preserve. One line per TAG in /workspace/d3-h100/registered.txt.
set -uo pipefail
source /workspace/env.sh
set -a; source /workspace/d3-h100/cred.env; set +a
export RESEARCH_STORE=/workspace/store RESEARCH_STORE_CONFIG=/workspace/src/tools/research/store.pod.toml
O=/workspace/d3-h100/runs; OUT=/workspace/d3-h100/registered.txt
POD="vy-d3-h100 (H100 80GB HBM3, US-MO-1, r79m8t4m58gq8o); live verifier ${VERIFIER_POD:-vy-d3-h100v (cpu3c 4 vCPU, US-MO-1, 4tdtl6xuhxaa3o, tcp://64.247.201.13:16766)}"
id_of() { $PY -c 'import json,sys; d=json.load(sys.stdin); print(d["id"] if (d.get("preserve") or {}).get("preserved") else "")' 2>/dev/null; }
for tag in "$@"; do
  d=$O/$tag; [ -f $d/result.json ] || { echo "$tag: no result.json"; continue; }
  grep -q "^$tag " $OUT 2>/dev/null && { echo "$tag: already registered"; continue; }
  label="d3-h100 H100 LIVE separate-host same-DC verifier (US-MO-1) $(sed -n 's/^tag=[^ ]* \(rel=[^ ]* l=[^ ]* p=[^ ]* reps=[^ ]*\) args=\(.*\) load=.*/\1 \2/p' $d/meta.txt | sed 's/--dump-dir [^ ]*//; s/--verifier [^ ]*//; s/--dump-reps 1/rep1 dump/; s/  */ /g')"
  meta=$($PY -c 'import json,sys; print(json.dumps({"lane": "d3-h100", "tag": sys.argv[1], "label": sys.argv[2], "pod": sys.argv[3], "listed": ["proofs"]}))' "$tag" "$label" "$POD")
  tid=$(cd $d && $PY -m research data put --kind run-files/v1 --tree . --meta "$meta" --preserve --json 2>$d/../$tag.tree.err | id_of)
  [ -n "$tid" ] || { echo "$tag: tree put FAILED: $(tail -2 $d/../$tag.tree.err | tr '\n' ' ')"; continue; }
  $PY - $d/result.json "$label" "$tag" "$POD" > $d/../$tag.meta.json <<'PYEOF'
import json, sys
m = json.load(open(sys.argv[1]))
m.update(label=sys.argv[2], lane="d3-h100", tag=sys.argv[3], pod=sys.argv[4])
print(json.dumps(m))
PYEOF
  br=$($PY -m research data put --kind bench-result/v1 --meta @$d/../$tag.meta.json --ref run_files=$tid --preserve --json 2>$d/../$tag.br.err | id_of)
  [ -n "$br" ] || { echo "$tag: bench-result put FAILED: $(tail -2 $d/../$tag.br.err | tr '\n' ' ')"; continue; }
  echo "$tag result=$br tree=$tid | $label" | tee -a $OUT
done
