"""replay_partition test times and outcomes per row: head merged, base (same pod), a23b base.
usage: rptimes.py HEAD.xml BASE.xml A23B.xml"""
import gzip
import sys
import xml.etree.ElementTree as ET


def load(p):
    f = gzip.open(p) if p.endswith(".gz") else open(p, "rb")
    out = {}
    for tc in ET.parse(f).iter("testcase"):
        n = tc.get("name", "")
        if not n.startswith("test_") or "replay_partition" not in n:
            continue
        st = "passed"
        for k in ("failure", "error", "skipped"):
            if tc.find(k) is not None:
                st = k
        out[n] = (st, float(tc.get("time") or 0))
    return out


h, b, a = (load(p) for p in sys.argv[1:4])
print(f"{'test':60s} {'head':>14s} {'base(samepod)':>18s} {'a23b base':>14s}")
for n in sorted(set(h) | set(b) | set(a)):
    cell = lambda d: f"{d[n][0][:4]} {d[n][1]:7.1f}" if n in d else "-"
    print(f"{n:60s} {cell(h):>14s} {cell(b):>18s} {cell(a):>14s}")
tot = lambda d: sum(t for s, t in d.values() if s == "passed")
print(f"passed total s: head {tot(h):.0f} base {tot(b):.0f} a23b {tot(a):.0f}")
