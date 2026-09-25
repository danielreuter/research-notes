import gzip, hashlib, json, sys
from pathlib import Path
h, b = Path(sys.argv[1]), Path(sys.argv[2])
def paths(a, c, p="$", out=None):
    out = [] if out is None else out
    if isinstance(a, dict) and isinstance(c, dict):
        if list(a) != list(c): out.append((p + " [key order/set]", list(a)[:5], list(c)[:5]))
        for k in a:
            if k in c: paths(a[k], c[k], f"{p}.{k}", out)
    elif isinstance(a, list) and isinstance(c, list) and len(a) == len(c):
        for i, (x, y) in enumerate(zip(a, c)): paths(x, y, f"{p}[{i}]", out)
    elif a != c:
        out.append((p, a, c))
    return out
import re
for f in ("fold_summary.json", "run/resolution.json"):
    d = paths(json.load(open(h / f)), json.load(open(b / f)))
    leaf = sorted({re.sub(r"\[\d+\]", "[]", p.split(".")[-1] if "." in p else p) for p, _, _ in d})
    print(f, len(d), "differing leaves; leaf names:", leaf[:20])
    for p, x, y in d[:4]: print("   ", p, str(x)[:80], "|", str(y)[:80])
raw = [gzip.open(x / "run/accesses.jsonl.gz").read() for x in (h, b)]
print("accesses decompressed:", len(raw[0]), len(raw[1]), "identical" if raw[0] == raw[1] else "DIFFER")
for x in (h, b):
    hd = open(x / "run/accesses.jsonl.gz", "rb").read(10)
    print("  gzip header", x.name, hd.hex(), "mtime", int.from_bytes(hd[4:8], "little"))
