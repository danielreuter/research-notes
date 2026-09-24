"""Compare two pytest JUnit XMLs (xunit1) test by test.

    python jdiff.py BASE.xml HEAD.xml

Prints: the counts of each, tests whose outcome changed, tests only in one of them (with their outcome), and skip reasons present in HEAD
but not in BASE (reasons with paths / numbers normalised).
"""
import collections
import gzip
import re
import sys
import xml.etree.ElementTree as ET


def load(p):
    raw = gzip.open(p).read() if p.endswith(".gz") else open(p, "rb").read()
    out = {}
    for tc in ET.fromstring(raw).iter("testcase"):
        tid = f"{tc.get('classname')}::{tc.get('name')}"
        kind, msg = "passed", ""
        for child in tc:
            if child.tag in ("failure", "error"):
                kind, msg = ("failed" if child.tag == "failure" else "error"), (child.get("message") or "")
            elif child.tag == "skipped":
                t = child.get("type") or ""
                kind = "xfailed" if "xfail" in t else "skipped"
                msg = child.get("message") or ""
        out[tid] = (kind, msg)
    return out


def norm(msg):
    msg = re.sub(r"/[\w./-]+", "<path>", msg)
    msg = re.sub(r"\b[0-9a-f]{12,}\b", "<hex>", msg)
    return re.sub(r"\d+", "<n>", msg)[:160]


a, b = load(sys.argv[1]), load(sys.argv[2])
print("BASE", dict(collections.Counter(k for k, _ in a.values())), "total", len(a))
print("HEAD", dict(collections.Counter(k for k, _ in b.values())), "total", len(b))
print("\n# outcome changed")
for t in sorted(set(a) & set(b)):
    if a[t][0] != b[t][0]:
        print(f"  {a[t][0]} -> {b[t][0]}  {t}  | {b[t][1][:200]}")
print("\n# only in HEAD")
for t in sorted(set(b) - set(a)):
    print(f"  {b[t][0]}  {t}  | {b[t][1][:160]}")
print("\n# only in BASE")
for t in sorted(set(a) - set(b)):
    print(f"  {a[t][0]}  {t}")
ra = {norm(m) for k, m in a.values() if k == "skipped"}
print("\n# skip reasons in HEAD, not in BASE")
for t, (k, m) in sorted(b.items()):
    if k == "skipped" and norm(m) not in ra:
        print(f"  {t}  | {m[:200]}")
