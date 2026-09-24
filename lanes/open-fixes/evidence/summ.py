"""summ.py RESULT.json ... : one line per bench-vu result (t.* medians, peak memory, validation)."""
import json, sys
keys = ["t.total", "t.witness", "t.encoding_commitment", "t.arithmetic", "t.serialization", "split.encode_seconds", "split.hints_seconds",
        "verifier.seconds", "mem.peak_device_bytes", "split.subbatches"]
for f in sys.argv[1:]:
    try:
        d = json.load(open(f))
    except Exception as e:
        print(f, "unreadable", e); continue
    m = {x["name"]: x["value"] for x in d["measurements"]}
    out = []
    for k in keys:
        v = m.get(k)
        if v is None: continue
        out.append(f"{k}={v/2**30:.2f}GiB" if k.startswith("mem") else f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}")
    print(f.split("/")[-1], d.get("run_id"), d["validation"]["status"], " ".join(out))
