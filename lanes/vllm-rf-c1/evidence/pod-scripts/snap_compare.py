"""Head vs base captured snapshot entries of one row (f3's snap_compare.py, trimmed): count and names of the entries whose bytes differ.
usage: python snap_compare.py ROW"""
import json
import sys

ROW = sys.argv[1]
H, B = f"/workspace/cp/sweep-head/{ROW}/match/capture", f"/workspace/cp/sweep-base/{ROW}/match/capture"
eh, eb = json.load(open(f"{H}/snapshots.json"))["entries"], json.load(open(f"{B}/snapshots.json"))["entries"]
print("entries", len(eh), len(eb))
diffs = [i for i, (x, y) in enumerate(zip(eh, eb)) if x.get("sha256") != y.get("sha256")]
print("differing entries", len(diffs))
names = {}
for i in diffs:
    x = eh[i]
    n = str(x.get("name") or x.get("identity") or x.get("key") or {k: v for k, v in x.items() if k not in ("file", "sha256")})[:160]
    names[n] = names.get(n, 0) + 1
for n, c in sorted(names.items()):
    print(c, n)
same_meta = all({k: v for k, v in eh[i].items() if k not in ("file", "sha256")} == {k: v for k, v in eb[i].items() if k not in ("file", "sha256")}
                for i in diffs)
print("metadata equal on every differing entry:", same_meta)
