"""result_meta.py RESULT TAG ARM OUT: write OUT = the result document plus the lane's keys (the bench-result/v1 meta) and
print "t.total status source_commit shards achieved_log2"."""
import json
import sys

src, tag, arm, out = sys.argv[1:5]
d = json.load(open(src))
fp = d["workload_fingerprint"]
m = {x["name"]: x["value"] for x in d["measurements"]}
meta = dict(d)
meta.update({"lane": "sp1-tcdot", "tag": tag, "arm": arm})
with open(out, "w") as f:
    json.dump(meta, f)
print(f"{m['t.total']:.3f}", d["validation"]["status"], fp["software"]["backend"]["commit"], int(m["shards"]),
      f"{fp['security']['achieved_log2']:.1f}")
