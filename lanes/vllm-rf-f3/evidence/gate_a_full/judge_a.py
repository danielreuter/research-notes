"""Gate (a) judgment from JUnit XML: head vs base (same pod, same env), and head vs a1's baseline (every check that passed there passes).
usage: python judge_a.py HEAD.xml BASE.xml [A1_BASELINE.xml[.gz]]"""
import collections, gzip, re, sys
import xml.etree.ElementTree as ET


def load(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rb") as f:
        root = ET.parse(f).getroot()
    out = {}
    for tc in root.iter("testcase"):
        state, msg = "passed", ""
        for child in tc:
            if child.tag in ("failure", "error", "skipped"):
                state, msg = child.tag, (child.get("message") or child.text or "").strip()
        out[tc.get("name")] = (state, msg)
    return out


def norm(msg):
    msg = re.sub(r"/workspace/\S+", "<path>", msg)
    msg = re.sub(r"\b[0-9a-f]{12,}\b", "<hex>", msg)
    return re.sub(r"\d+(\.\d+)?", "<n>", msg)


head, base = load(sys.argv[1]), load(sys.argv[2])
for tag, r in (("head", head), ("base", base)):
    print(tag, len(r), dict(collections.Counter(s for s, _ in r.values())))
print("only in head:", sorted(set(head) - set(base)))
print("only in base:", sorted(set(base) - set(head)))
changed = [(k, base[k][0], head[k][0]) for k in sorted(set(head) & set(base)) if head[k][0] != base[k][0]]
print(f"outcome changed base -> head ({len(changed)}):")
for k, b, h in changed:
    print(f"  {k}: {b} -> {h} | head: {head[k][1][:240]} | base: {base[k][1][:240]}")
msg_changed = [k for k in sorted(set(head) & set(base)) if head[k][0] == base[k][0] != "passed" and norm(head[k][1]) != norm(base[k][1])]
print(f"same outcome, different skip/fail message ({len(msg_changed)}):")
for k in msg_changed:
    print(f"  {k}: head: {head[k][1][:200]} | base: {base[k][1][:200]}")
bad = [k for k, (s, _) in head.items() if s in ("failure", "error")]
print(f"head failures/errors ({len(bad)}):")
for k in bad:
    print(f"  {k}: {head[k][0]} | {head[k][1][:300]} | base: {base.get(k, ('absent', ''))[0]}")
reasons = collections.Counter(norm(m)[:160] for s, m in head.values() if s == "skipped")
print("head skip reasons:")
for r, n in reasons.most_common():
    print(f"  {n} x {r}")
if len(sys.argv) > 3:
    a1 = load(sys.argv[3])
    passed_a1 = [k for k, (s, _) in a1.items() if s == "passed"]
    lost = [(k, head.get(k, ("absent", ""))[0]) for k in passed_a1 if head.get(k, ("absent", ""))[0] != "passed"]
    print(f"a1 baseline: {len(a1)} tests, {len(passed_a1)} passed; of those not passed at head ({len(lost)}): {lost}")
    gained = sorted(k for k, (s, _) in head.items() if s == "passed" and a1.get(k, ("absent", ""))[0] != "passed")
    print(f"passed at head, not passed in a1's baseline ({len(gained)}): {gained}")
