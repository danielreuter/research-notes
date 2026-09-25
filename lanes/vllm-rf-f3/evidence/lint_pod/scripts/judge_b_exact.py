"""Gate (b) head vs main from JUnit XML, keyed by classname::name, plus both against a1's base runs (xdist + serial).
usage: python judge_b_exact.py HEAD.xml[.gz] MAIN.xml[.gz] A1_XDIST.xml.gz A1_SERIAL.xml.gz"""
import collections, gzip, re, sys
import xml.etree.ElementTree as ET


def load(p):
    op = gzip.open if p.endswith(".gz") else open
    out = {}
    with op(p, "rb") as f:
        for tc in ET.parse(f).getroot().iter("testcase"):
            st, msg = "passed", ""
            for ch in tc:
                if ch.tag in ("failure", "error", "skipped"):
                    st, msg = ch.tag, (ch.get("message") or ch.text or "").strip()
            cls = re.sub(r"^integrations\.vllm\.", "", tc.get("classname", ""))
            out[f'{cls}::{tc.get("name")}'] = (st, msg)
    return out


def norm(m):
    m = re.sub(r"/workspace/[\w.-]+", "<tree>", m)
    m = re.sub(r"/tmp/pytest-of-root/pytest-\d+/popen-gw\d+", "<tmp>", m)
    m = re.sub(r"0x[0-9a-f]+", "<addr>", m)
    m = re.sub(r"\b[0-9a-f]{12,}\b", "<hex>", m)
    return re.sub(r"\d+(\.\d+)?", "<n>", m)[:160]


def fe(r):
    return {k for k, (s, _) in r.items() if s in ("failure", "error")}


h, m, ax, asr = (load(p) for p in sys.argv[1:5])
for tag, r in (("head", h), ("main", m)):
    print(tag, len(r), dict(collections.Counter(s for s, _ in r.values())))
print("F/E at head, not at main:", sorted(fe(h) - fe(m)))
print("F/E at main, not at head:", sorted(fe(m) - fe(h)))
new = sorted(set(h) - set(m))
print(f"tests only at head ({len(new)}):", dict(collections.Counter(h[k][0] for k in new)))
print("tests only at main:", sorted(set(m) - set(h)))
print("outcome changes main -> head:", sorted((k, m[k][0], h[k][0]) for k in set(h) & set(m) if h[k][0] != m[k][0]))
sh = collections.Counter(norm(x) for s, x in h.values() if s == "skipped")
sm = collections.Counter(norm(x) for s, x in m.values() if s == "skipped")
print("skip reasons whose count differs head vs main:", {r: (sh.get(r, 0), sm.get(r, 0)) for r in set(sh) | set(sm) if sh.get(r, 0) != sm.get(r, 0)})
allowed = fe(ax) | fe(asr)
a1_skips = {norm(x) for r in (ax, asr) for s, x in r.values() if s == "skipped"}
for tag, r in (("head", h), ("main", m)):
    print(f"{tag}: F/E outside a1's base F/E (xdist + serial): {sorted(fe(r) - allowed)}; in a1's xdist list {len(fe(r) & fe(ax))}, "
          f"only in its serial list {len((fe(r) & fe(asr)) - fe(ax))}")
    print(f"   skips whose reason is in neither a1 run: {[(k, x[:100]) for k, (s, x) in r.items() if s == 'skipped' and norm(x) not in a1_skips]}")
