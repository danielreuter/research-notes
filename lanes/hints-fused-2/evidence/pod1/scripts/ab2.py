"""ab2.py DIR... : group bench results by config (tag minus the round prefix), per config: every run's t.total (median of its
3 reps), the median across runs, and the medians of the phases / splits.  Tags: <round>_<fu|to|base>_<rel>_p<depth>_<l>[...]."""
import glob, json, os, re, statistics as st, sys
from collections import defaultdict

KEYS = ["t.total", "t.witness", "split.hints_seconds", "t.encoding_commitment", "t.arithmetic", "t.serialization",
        "split.encode_seconds", "split.merkle_seconds", "split.tests_seconds", "split.openings_seconds"]
runs = defaultdict(list)
for d in sys.argv[1:]:
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        tag = os.path.basename(f)[:-5]
        if tag.startswith(("prof_", "gate")):
            continue
        m = re.match(r"^(ab\d|r\d|base|d)_(.*)$", tag)
        if not m:
            continue
        cfg = m.group(2) if m.group(1) != "base" else "base_" + m.group(2)
        try:
            j = json.load(open(f))
        except Exception:
            continue
        v = {x["name"]: x["value"] for x in j["measurements"]}
        val = j.get("validation")
        val = val.get("status") if isinstance(val, dict) else val
        runs[cfg].append((tag, v, val, j.get("run_id")))
print(f"{'config':28s} {'n':>2s} {'t.total med':>11s} {'min':>7s} {'max':>7s} {'witness':>8s} {'hints':>7s} {'enc+com':>8s} "
      f"{'arith':>7s} {'tests':>7s} {'subb':>4s} {'peakGiB':>7s} valid")
for cfg in sorted(runs):
    rs = runs[cfg]
    tt = [v["t.total"] for _, v, _, _ in rs]
    med = {k: st.median([v[k] for _, v, _, _ in rs if k in v]) for k in KEYS if any(k in v for _, v, _, _ in rs)}
    pk = max(v.get("mem.peak_device_bytes", 0) for _, v, _, _ in rs) / 2**30
    sb = rs[0][1].get("split.subbatches", "?")
    vals = ",".join(sorted(set(str(x) for _, _, x, _ in rs)))
    print(f"{cfg:28s} {len(rs):2d} {st.median(tt):11.4f} {min(tt):7.4f} {max(tt):7.4f} {med.get('t.witness', 0):8.4f} "
          f"{med.get('split.hints_seconds', 0):7.4f} {med.get('t.encoding_commitment', 0):8.4f} {med.get('t.arithmetic', 0):7.4f} "
          f"{med.get('split.tests_seconds', 0):7.4f} {sb!s:>4s} {pk:7.2f} {vals}")
if "-v" in os.environ.get("AB2", ""):
    for cfg in sorted(runs):
        for tag, v, val, rid in runs[cfg]:
            print(f"  {cfg:28s} {tag:34s} {v['t.total']:.4f} {rid}")
