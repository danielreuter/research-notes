#!/usr/bin/env bash
# Row #70 after its Commit: verdict.from_record(row).dumps() under each tree on the TP2 pod (read-only on the row), sha256 per tree,
# and the head text against the base text.  Output under /workspace/b2vb/fr70/.
set -u
ROW=olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager
D=/workspace/cp/sweep/$ROW
O=/workspace/b2vb/fr70
PY=/workspace/venv312/bin/python
mkdir -p "$O"
for t in base:/workspace/base run:/workspace/research/src/66eaaa50e548d0f9fb08e0ee3fa35cf12bdf00b6 head2:/workspace/head2; do
  name=${t%%:*} tree=${t#*:}
  echo "== $name $tree $(cat "$tree/.b2v-tree" 2>/dev/null | head -1 || true)"
  PYTHONPATH=$tree/integrations/vllm:$tree/packages/verity/src:$tree/tools/research/src CUDA_VISIBLE_DEVICES="" \
    $PY -c 'import sys; from verity_vllm.check.verdict import from_record; sys.stdout.write(from_record(sys.argv[1]).dumps())' "$D" \
    > "$O/$name.json" 2> "$O/$name.err"
  echo "rc=$? sha256=$(sha256sum < "$O/$name.json" | cut -c1-64) bytes=$(wc -c < "$O/$name.json")"
  tail -3 "$O/$name.err"
done
$PY - "$O" <<'EOF'
import json, sys
from pathlib import Path
o = Path(sys.argv[1])
docs = {n: json.loads((o / f"{n}.json").read_text()) for n in ("base", "run", "head2")}
for n, v in docs.items():
    print(n, "outcome", v.get("outcome"), "| program", v.get("program_digest"), "| manifest", v.get("manifest_digest"),
          "| roots", v.get("run_roots"), "| properties", [(c.get("name"), c.get("digest", "")[:16], c.get("ok")) for c in v.get("properties", [])])
    print("   notes", v.get("notes"))
b, h = docs["base"], docs["head2"]
print("keys head-only:", sorted(set(h) - set(b)), "base-only:", sorted(set(b) - set(h)))
print("every shared key equal:", all(b[k] == h[k] for k in b if k in h), [k for k in b if k in h and b[k] != h[k]])
hb = dict(h); hb.pop("properties", None)
print("head without `properties` == base, as JSON:", hb == b)
print("run tree == head2 bytes:", (o / "run.json").read_bytes() == (o / "head2.json").read_bytes())
EOF
