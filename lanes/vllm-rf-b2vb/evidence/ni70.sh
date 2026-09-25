#!/usr/bin/env bash
# Row #70's world-2 non-interference record under the head tree: digest recomputes, the world is read from the arms, 3 and 4 refused.
set -u
ROW=olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager
D=/workspace/cp/sweep/$ROW
T=/workspace/head2
echo "== text diff base -> head2 (from_record on #70)"
diff /workspace/b2vb/fr70/base.json /workspace/b2vb/fr70/head2.json
echo "diff rc=$?"
PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src CUDA_VISIBLE_DEVICES="" /workspace/venv312/bin/python - "$D" "$ROW" <<'EOF'
import json, sys
from pathlib import Path
from verity_vllm.properties import noninterference as N
from verity_vllm.properties.record import PropertyRecord, records_of
d, row = Path(sys.argv[1]), sys.argv[2]
doc = json.loads((d / "properties" / "noninterference.json").read_text())
r = PropertyRecord(doc)
print("stored:", r.name, "ok", r.ok, "digest", r.digest, "problems", r.problems())
print("world", doc.get("world"), "| keys", sorted(doc))
print({k: doc[k] for k in doc if k not in ("digest",) and not isinstance(doc[k], (list, dict))})
again = N.record(d / "match", 2, run=row)
print("rebuilt from the row's Match arms at the head:", "ok" if again.get("ok") else "NOT ok", again.get("digest"),
      "== stored" if again.get("digest") == doc.get("digest") else "!= stored")
for w in (3, 4):
    try:
        N.record(d / "match", w, run=row)
        print(f"world {w}: NOT refused")
    except ValueError as e:
        print(f"world {w}: ValueError: {e}")
print("records_of(row):", [(x.name, x.digest[:16], x.ok) for x in records_of(d)])
EOF
echo "rc=$?"
