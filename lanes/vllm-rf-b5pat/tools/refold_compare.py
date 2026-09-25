"""Compare re-folds of one regression row: the fixture's recorded fold against the head and base re-folds, and head against base.

usage: refold_compare.py ROWDIR HEAD_OUT BASE_OUT      (OUT = /workspace/b5pat/refold/TAG)
Volatile fields (wall clock, paths, RSS, timings) are dropped; everything else, key order included, must be equal.
"""
import hashlib
import json
import sys
from pathlib import Path

VOLATILE = {"utc", "log", "seconds", "timings", "max_rss_gb", "memory"}


def load(p):
    return json.loads(Path(p).read_text())


def strip(d):
    d = {k: v for k, v in d.items() if k not in VOLATILE}
    if isinstance(d.get("persisted"), dict):
        d["persisted"] = {k: {kk: vv for kk, vv in v.items() if kk != "path"} for k, v in d["persisted"].items()}
    return d


def ordered(x):
    """JSON text with insertion order kept, so a reordered by_pattern (or any dict) counts as a difference."""
    return json.dumps(x, sort_keys=False)


def diff_keys(a, b):
    ks = list(dict.fromkeys([*a, *b]))
    return [k for k in ks if ordered(a.get(k)) != ordered(b.get(k))]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    row, head, base = map(Path, sys.argv[1:4])
    fx = load(row / "match/fold_summary.json")
    hd = load(head / "fold_summary.json")
    bs = load(base / "fold_summary.json")
    ok = True
    print(f"digest fixture {fx['digest']}")
    print(f"digest head    {hd['digest']}  {'==' if hd['digest'] == fx['digest'] else '!='} fixture")
    print(f"digest base    {bs['digest']}  {'==' if bs['digest'] == fx['digest'] else '!='} fixture")
    ok &= hd["digest"] == fx["digest"] == bs["digest"]
    for name, other in (("fixture", fx), ("base", bs)):
        dk = diff_keys(strip(hd), strip(other))
        print(f"fold_summary head vs {name}: {'identical (volatile fields dropped)' if not dk else 'DIFFER in ' + ', '.join(dk)}")
        ok &= not dk or (name == "fixture" and set(dk) <= {"persisted"})
    for name, other in (("fixture", fx), ("base", bs)):
        a, b = hd["fold"]["report"]["by_pattern"], other["fold"]["report"]["by_pattern"]
        same = list(a.items()) == list(b.items())
        print(f"fold.report.by_pattern head vs {name}: {'identical, same order' if same else 'DIFFER'} ({len(a)} patterns, {sum(a.values())} matches)")
        ok &= same
    fr = load(row / "match/resolution.json")
    hr = load(head / "run/resolution.json")
    br = load(base / "run/resolution.json")
    for name, other in (("fixture", fr), ("base", br)):
        dk = diff_keys(strip(hr), strip(other))
        print(f"resolution.json head vs {name}: {'identical (log path dropped)' if not dk else 'DIFFER in ' + ', '.join(dk)}")
        ok &= not dk
    for f in ("program.json", "instances.jsonl", "accesses.jsonl.gz", "resolution.json"):
        h, b = sha(head / "run" / f), sha(base / "run" / f)
        print(f"{f:20s} head {h[:16]}  base {b[:16]}  {'byte-identical' if h == b else 'DIFFER'}")
        ok &= h == b
    print("REFOLD-OK" if ok else "REFOLD-MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
