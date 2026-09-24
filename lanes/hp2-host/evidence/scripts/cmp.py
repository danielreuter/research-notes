import json, sys
a, b = [json.load(open(f"/workspace/hp2/out/{t}/digests.json")) for t in sys.argv[1:3]]
fa, fb = a["files"], b["files"]
same = [k for k in fa if fb.get(k) == fa[k]]
diff = [k for k in fa if fb.get(k) != fa[k]]
print(f"{sys.argv[1]} vs {sys.argv[2]}: {len(same)} identical, {len(diff)} differ {diff[:6]}; urandom calls {a['urandom_calls']} vs {b['urandom_calls']}")
