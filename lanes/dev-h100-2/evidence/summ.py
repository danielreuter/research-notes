import json, sys, statistics
p = sys.argv[1]
r = json.load(open(p))
m = {x["name"]: x for x in r["measurements"]}
def v(k):
    x = m.get(k)
    return None if x is None else x.get("value")
wf = r.get("workload_fingerprint", {})
inst = wf.get("instances", {})
print("run", r.get("run_id"), "| auth", wf.get("authentication"), "| relation", wf.get("relation") or wf.get("target"), "| pipeline", r.get("pipeline", wf.get("pipeline")))
print("instances.manifest_sha256", inst.get("manifest_sha256"), "range", inst.get("range"), "tier", inst.get("tier"))
keys = ["t.total", "t.total_live", "t.witness", "t.encoding_commitment", "t.arithmetic", "t.zk_additional", "t.serialization",
        "net.rtt_ms", "net.wait_seconds", "net.bytes_out", "net.bytes_in", "net.messages", "verify.wall_s", "verify.cpu_s",
        "peak_device_bytes", "achieved_bits", "transcript_bytes", "proof_bytes_total", "statement_bytes_total", "vu.seconds_per_vu", "overhead.vs_native_peak"]
for k in keys:
    if k in m:
        x = m[k]; extra = {kk: x[kk] for kk in x if kk not in ("name", "value", "unit")}
        print(f"  {k:26s} {x.get('value')} {x.get('unit','')}  {extra if extra else ''}")
others = [k for k in m if k not in keys and (k.startswith("t.") or k.startswith("bytes") or "bits" in k or "reps" in k or k.startswith("split."))]
for k in others:
    print(f"  {k:26s} {m[k].get('value')} {m[k].get('unit','')}")
val = r.get("validation", {})
print("validation:", val.get("status") if isinstance(val, dict) else val)
ev = (val.get("evidence") or {}) if isinstance(val, dict) else {}
lv = ev.get("live_verifier")
if lv:
    print("live_verifier evidence:", json.dumps(lv)[:600])
print("reps:", json.dumps(r.get("reps") or r.get("per_rep") or "")[:400])
