"""cmpdig.py BASE_DIR LANE_DIR: compare the two bitexact.py runs' digests.json file maps (sha256 per written file)."""
import json
import sys

a, b = (json.load(open(f"{d}/digests.json")) for d in sys.argv[1:3])
fa, fb = a["files"], b["files"]
same = sorted(k for k in fa if fb.get(k) == fa[k])
diff = sorted(k for k in set(fa) | set(fb) if fa.get(k) != fb.get(k))
tag = f"{a['args']['rel']} zk={a['args']['zk']} pipeline={a['args']['pipeline']} subs={a['args']['subs']} vus/sub={a['args']['vus']}"
print(f"BITEXACT {tag}: {len(same)}/{len(set(fa) | set(fb))} files identical" + (f"; DIFFER: {diff}" if diff else "")
      + f"; urandom calls {a['urandom_calls']} vs {b['urandom_calls']}")
sys.exit(1 if diff else 0)
