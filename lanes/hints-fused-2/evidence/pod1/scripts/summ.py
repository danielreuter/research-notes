"""summ.py RESULT.json... : one line per result: t.total, the phases, validation, sub-batches, peak memory."""
import json, sys
for f in sys.argv[1:]:
    try:
        d = json.load(open(f))
    except Exception as e:
        print(f, "ERR", e); continue
    m = {x["name"]: x["value"] for x in d["measurements"]}
    keys = ["t.total", "t.witness", "t.encoding_commitment", "t.arithmetic", "t.serialization", "split.hints", "split.encode", "split.tests", "split.openings",
            "mem.peak_device_bytes", "census.sub_batches", "proof.bytes_total"]
    out = []
    for k in keys:
        if k in m:
            v = m[k]
            out.append(f"{k}={v/2**30:.2f}GiB" if k.startswith("mem") else (f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}"))
    print(f.split("/")[-1], d.get("run_id"), d.get("validation", {}).get("status") if isinstance(d.get("validation"), dict) else d.get("validation"), " ".join(out))
