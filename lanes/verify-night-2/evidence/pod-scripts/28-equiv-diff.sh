#!/usr/bin/env bash
# verify-night-2: regenerate an instance-equiv/v1 doc at this tree and diff it field by field with a registered doc (its meta).
#   bash 28-equiv-diff.sh RELATION VUS DOC_JSON
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
REL=$1; N=$2; DOC=$3; D=/workspace/verify-night-2/equiv/regen-$REL-$N; rm -rf $D; mkdir -p $D
echo "tree $(python3 -c "import json;print(json.load(open('/workspace/src/.research-source.json'))['commit'][:8])")"
timeout 900 $PY -m verity_numerical.bench.instance_equiv --relation $REL --vus $N --out-dir $D 2>&1 | tail -2
G=$(ls $D/*.json | head -1); echo "regenerated: $G"
$PY - "$DOC" "$G" <<'EOF'
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
for k in sorted(set(a) | set(b)):
    if a.get(k) != b.get(k):
        print("DIFF", k, "\n  doc  :", json.dumps(a.get(k), sort_keys=True)[:900], "\n  regen:", json.dumps(b.get(k), sort_keys=True)[:900])
print("same:", sorted(k for k in set(a) & set(b) if a[k] == b[k]))
EOF
