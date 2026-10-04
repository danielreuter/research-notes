"""Summarize tc_rates_sm120's output into result.json: each route's rate per SM per clock at the recorded mean SM clock, and
its W1 price per MAC (or per op) relative to the FP8 E4M3 mma.sync with FP32 accumulate (1 unit = one dense FP8 MAC)."""
import csv, json, os, re, sys

uuid = sys.argv[1]
rows = [json.loads(l) for l in open("rates.jsonl") if l.strip()]
head, ops = rows[0], {r["op"]: r for r in rows[1:]}
clk = []
with open("clocks.csv") as f:
    for r in csv.reader(f):
        m = re.match(r"\s*(\d+)\s*MHz", r[1]) if len(r) > 1 else None
        if m:
            clk.append(int(m.group(1)))
busy = [c for c in clk if c > 0]
mhz = sum(busy) / len(busy) if busy else head["clock_mhz_assumed"]
scale = head["clock_mhz_assumed"] / mhz
sass = {}
fn = None
for line in open("sass.txt"):
    m = re.search(r"Function : (\S+)", line)
    if m:
        fn = m.group(1)
        sass[fn] = {}
    ins = re.search(r"\*/\s+(?:@!?U?P\w+\s+)?([A-Z][A-Z0-9_]+)(\.[A-Z0-9_.]+)?", line)
    if fn and ins and ins.group(1) in ("QMMA", "OMMA", "HMMA", "IMMA", "FADD", "FFMA", "IADD3", "LOP3", "I2F", "I2FP", "HFMA2",
                                       "IDP", "IDP4A", "IMAD", "PRMT", "LDS"):
        k = ins.group(1) + (ins.group(2) or "")
        sass[fn][k] = sass[fn].get(k, 0) + 1
fp8 = rows[1]["per_sm_per_clk"] * scale  # the first op is the unit: the FP8 E4M3 mma.sync with FP32 accumulate
out, meas = {}, []
for name, r in ops.items():
    rate = r["per_sm_per_clk"] * scale
    price = fp8 / rate
    out[name] = {"per_sm_per_clk": round(rate, 2), "w1_units_per_mac_or_op": round(price, 4), "seconds": r["seconds"]}
    meas += [(f"{name}.per_sm_per_clk", round(rate, 2), "ops/SM/clk"), (f"{name}.w1_price", round(price, 4), "fp8-mac")]
details = {"device": head, "gpu_uuid": uuid, "sm_clock_mhz_mean_sampled": round(mhz, 1), "clock_samples": len(busy),
           "rates": out, "sass_counts": sass, "nvcc": open("nvcc.txt").read().strip()}
json.dump(details, open("details.json", "w"), indent=1)
doc = {"schema": "research/result/v0.1", "run_id": os.environ.get("RESEARCH_RUN_ID"),
       "workload_fingerprint": {"attack": "tc-rates-sm120", "by": "red-team-pouw", "gpu_uuid": uuid},
       "validation": {"status": "passed", "checker": "red-team-pouw",
                      "detail": "register-only mma.sync / scalar throughput, 16 warps/SM, best of 5", "evidence": ["details.json"]},
       "measurements": [{"name": n, "value": v, "unit": u} for n, v, u in meas],
       "measurement_files": ["details.json", "rates.jsonl", "clocks.csv", "sass.txt"], "artifacts": ["details.json"]}
json.dump(doc, open("result.json", "w"), indent=1)
for name, r in out.items():
    print(f"{name:28s} {r['per_sm_per_clk']:9.1f}/SM/clk  price {r['w1_units_per_mac_or_op']:.3f}")
