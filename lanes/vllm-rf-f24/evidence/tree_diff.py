"""Diff two output trees: every file by content (gzip decompressed), JSON files path by path.

    python tree_diff.py A B [--out diff.json]
"""
import gzip
import hashlib
import json
import os
import sys


def load(p):
    b = open(p, "rb").read()
    if p.endswith(".gz"):
        b = gzip.decompress(b)
    return b


def walk(a, b, p, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                out.append((f"{p}.{k}", a.get(k, "<absent>"), b.get(k, "<absent>")))
            else:
                walk(a[k], b[k], f"{p}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((f"{p}.<len>", len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{p}[{i}]", out)
    elif a != b:
        out.append((p, a, b))


def files(root):
    return {os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs}


def main(argv):
    ra, rb = argv[0], argv[1]
    fa, fb = files(ra), files(rb)
    rep = {"a": ra, "b": rb, "only_a": sorted(fa - fb), "only_b": sorted(fb - fa), "identical": [], "differ": {}}
    for f in sorted(fa & fb):
        x, y = load(os.path.join(ra, f)), load(os.path.join(rb, f))
        if x == y:
            rep["identical"].append(f)
            continue
        name = f[:-3] if f.endswith(".gz") else f
        if name.endswith(".json"):
            try:
                d = []
                walk(json.loads(x), json.loads(y), "$", d)
                rep["differ"][f] = [{"path": p, "a": str(u)[:200], "b": str(v)[:200]} for p, u, v in d]
                continue
            except ValueError:
                pass
        rep["differ"][f] = [{"sha256_a": hashlib.sha256(x).hexdigest(), "sha256_b": hashlib.sha256(y).hexdigest()}]
    if "--out" in argv:
        json.dump(rep, open(argv[argv.index("--out") + 1], "w"), indent=1)
    print(json.dumps({"identical": len(rep["identical"]), "only_a": rep["only_a"], "only_b": rep["only_b"],
                      "differ": {f: [e.get("path", "bytes") for e in v][:30] for f, v in rep["differ"].items()}}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
