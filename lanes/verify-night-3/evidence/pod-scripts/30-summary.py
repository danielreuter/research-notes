"""verify-night-3: one line per reverify JSON: status, relation, custody, reps n/accepted, pinned sys, union bound, verdict id."""
import glob, json, sys

for f in sorted(glob.glob("/workspace/verify-night-3/rv-*.json")):
    try:
        t = open(f).read()   # reverify's label writes print their paths before the JSON
        d = json.loads(t[t.index("[\n"):])[0]
    except Exception as e:
        print(f, "unreadable", type(e).__name__)
        continue
    reps = d.get("reps") or {}
    acc = sum(v.get("accepted", 0) for v in reps.values()); n = sum(v.get("n", 0) for v in reps.values())
    sysid = {(v.get("system") or {}).get("sys_id", "")[:8] for v in reps.values()}
    bits = {k: v for r in reps.values() for k, v in r.items() if "bit" in k and k not in ("target_bits", "per_proof_bits")}
    print(d["result"][:12], d["status"], d.get("relation"), f"custody={d.get('custody')}", f"{acc}/{n}", f"sys={sysid}",
          f"hashed={d.get('hashed')}", f"bits={bits}", f"verdict={d.get('verdict')}", f"why={d.get('why')}")
