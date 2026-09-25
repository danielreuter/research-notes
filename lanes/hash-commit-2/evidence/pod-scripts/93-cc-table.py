# hash-commit-2: one line per (shape, scheme) from $HC/cc/*/commit_cost.json: commit (leaf + tree) and h2d medians in ms, root == reference
import json, sys
from pathlib import Path

for d in sorted(Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/hash-commit-2/cc").iterdir()):
    j = json.loads((d / "commit_cost.json").read_text())
    rows = j if isinstance(j, list) else j.get("results", j.get("rows", []))
    for r in rows:
        print(f"{d.name:9s} {r['scheme']:20s} n={r['leaves']} B={r['leaf_bytes']} commit={r['commit_s']*1e3:.3f}ms "
              f"(leaf {r['leaf_s']*1e3:.3f} tree {r['tree_s']*1e3:.3f}) h2d={r['h2d_s']*1e3:.3f}ms "
              f"root==ref={r['root'] == r['reference_root']} open={r['opening_verified']} {r.get('device', '')}")
