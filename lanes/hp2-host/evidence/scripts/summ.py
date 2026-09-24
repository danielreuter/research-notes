import json, sys, glob, os
for rd in sys.argv[1:]:
    r = json.load(open(os.path.join(rd, "result.json")))
    m = {x["name"]: x["value"] for x in r["measurements"]}
    wf = r["workload_fingerprint"]
    be = wf["software"]["backend"]
    print(f"{r['run_id']}  {wf['relation'][:26]:26s} zk={wf['security']['zk']} pipeline={be.get('pipeline')} impl={be.get('impl')}")
    print("   t.total %.4f | witness %.4f enc+commit %.4f arith %.4f zk %.4f serial %.4f | verifier %.3f | R_proved %.4g overhead %.4g | peak dev %.2f GB" % (
        m["t.total"], m["t.witness"], m["t.encoding_commitment"], m["t.arithmetic"], m["t.zk_additional"], m["t.serialization"],
        m.get("verifier.seconds", 0), m.get("rate.proved_flop_per_second", 0), m.get("overhead.vs_native_peak", 0), m.get("mem.peak_device_bytes", 0) / 1e9))
    print("   validation:", r["validation"].get("status"), "| reject_reasons:", r["validation"].get("reject_reasons"), "| measurement names with 'overhead':", [k for k in m if "overhead" in k or "rate" in k])
    out = open(os.path.join(rd, "stdout.log")).read().splitlines()
    for line in out:
        if line.startswith("medians") or "median" in line[:30] or line.startswith("rep ") or "phase medians" in line:
            print("   ", line[:400])
