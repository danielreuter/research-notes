"""Normalized JSON diff of row #101's head and base trees: tree paths, sweep dirs, timings and code identities blanked.
usage: normdiff.py HEAD_ROWDIR BASE_ROWDIR      prints per file: same | DIFF <first differing key paths>"""
import json, re, sys
from pathlib import Path

H, B = Path(sys.argv[1]), Path(sys.argv[2])
VOL = re.compile(r"(time|wall|_s$|seconds|started|finished|^ts$|_at$|^at$|date|elapsed|duration|rss|pid|host|mtime|peak|mem|gb$|_ms$|utc|clock)", re.I)
SUB = [(re.compile(r"/workspace/(head2|basemain)"), "TREE"), (re.compile(r"sweep-(head|base)"), "sweep-X"),
       (re.compile(r"\b20\d\d-\d\d-\d\dT[\d:.]+Z?"), "TS")]


def norm(x, path=""):
    if isinstance(x, dict):
        return {k: norm(v, f"{path}.{k}") for k, v in x.items() if not VOL.search(k)}
    if isinstance(x, list):
        return [norm(v, path) for v in x]
    if isinstance(x, str):
        for r, s in SUB:
            x = r.sub(s, x)
    return x


def diffs(a, b, path="", out=None):
    out = [] if out is None else out
    if len(out) > 6:
        return out
    if type(a) is not type(b):
        out.append(path or "<root>")
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}.{k}(one side)")
            else:
                diffs(a[k], b[k], f"{path}.{k}", out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(f"{path}[len {len(a)}!={len(b)}]")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                diffs(x, y, f"{path}[{i}]", out)
    elif a != b:
        out.append(path)
    return out


same = 0
for f in sorted(H.rglob("*.json")):
    rel = f.relative_to(H)
    g = B / rel
    if f.stat().st_size > 50_000_000 or not g.exists():
        print("SKIP", rel); continue
    try:
        a, b = norm(json.loads(f.read_text())), norm(json.loads(g.read_text()))
    except Exception as e:
        print("ERR", rel, e); continue
    d = diffs(a, b)
    if d:
        print("DIFF", rel, " ".join(d[:6])[:300])
    else:
        same += 1
print("same", same)
