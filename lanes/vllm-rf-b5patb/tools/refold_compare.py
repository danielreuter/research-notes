"""Compare re-folds of one regression row: head against base (strict), and both against the fixture's recorded fold.

usage: refold_compare.py ROWDIR HEAD_OUT BASE_OUT      (OUT = /workspace/b5patb/refold/TAG)

Head vs base: fold_summary.json and resolution.json equal with volatile fields dropped (key order included), and every
persisted run file byte-identical.  Fixture: the fold digest, the persisted program digest and every persisted size, and
fold.report.by_pattern (counts and order) must be equal; other differing top-level keys are listed (the record predates
the P6 profile rename and a4's module moves, which both sides share).
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
    if isinstance(d.get("fold"), dict):
        d["fold"] = {k: v for k, v in d["fold"].items() if k not in VOLATILE}
    return d


def ordered(x):
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
    print(f"profile fixture {fx.get('profile')} / head {hd.get('profile')} / base {bs.get('profile')}")
    print(f"digest fixture {fx['digest']}")
    for name, d in (("head", hd), ("base", bs)):
        print(f"digest {name:7s} {d['digest']}  {'==' if d['digest'] == fx['digest'] else '!='} fixture")
        ok &= d["digest"] == fx["digest"]
    pf = strip(fx)["persisted"]
    for name, d in (("head", hd), ("base", bs)):
        pd = strip(d)["persisted"]
        same = ordered(pd) == ordered(pf)
        print(f"persisted {name} vs fixture: {'equal (digest, bytes, counts)' if same else 'DIFFER: ' + ordered(pd) + ' vs ' + ordered(pf)}")
        ok &= same
    dk = diff_keys(strip(hd), strip(bs))
    print(f"fold_summary head vs base: {'identical (volatile fields dropped)' if not dk else 'DIFFER in ' + ', '.join(dk)}")
    ok &= not dk
    dk = diff_keys(strip(hd), strip(fx))
    print(f"fold_summary head vs fixture (information): {'identical' if not dk else 'differ in ' + ', '.join(dk)}")
    for name, other in (("fixture", fx), ("base", bs)):
        a, b = hd["fold"]["report"]["by_pattern"], other["fold"]["report"]["by_pattern"]
        same = list(a.items()) == list(b.items())
        print(f"fold.report.by_pattern head vs {name}: {'identical, same order' if same else 'DIFFER'} ({len(a)} patterns, {sum(a.values())} matches)")
        ok &= same
    fr = load(row / "match/resolution.json")
    hr = load(head / "run/resolution.json")
    br = load(base / "run/resolution.json")
    dk = diff_keys(strip(hr), strip(br))
    print(f"resolution.json head vs base: {'identical (log path dropped)' if not dk else 'DIFFER in ' + ', '.join(dk)}")
    ok &= not dk
    dk = diff_keys(strip(hr), strip(fr))
    print(f"resolution.json head vs fixture (information): {'identical' if not dk else 'differ in ' + ', '.join(dk)}")
    files = sorted({p.name for p in (head / "run").iterdir()} | {p.name for p in (base / "run").iterdir()})
    for f in files:
        hp, bp = head / "run" / f, base / "run" / f
        if not (hp.is_file() and bp.is_file()):
            print(f"{f:24s} present head={hp.is_file()} base={bp.is_file()}  DIFFER")
            ok = False
            continue
        h, b = sha(hp), sha(bp)
        print(f"{f:24s} head {h[:16]}  base {b[:16]}  {'byte-identical' if h == b else 'DIFFER'}  ({hp.stat().st_size} bytes)")
        ok &= h == b
    print("REFOLD-OK" if ok else "REFOLD-MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
