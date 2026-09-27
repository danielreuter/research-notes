"""eval_time.py: verity/partition/v1 as a named query (PR #111): the object's size, and core's evaluator (verity.ir.cut.evaluate_definition,
Q_word v1, X = 16) over every distinct Definition specialization of a request Program -- wall time, peak RSS, the units -- against the
Program's own serialized size (its instance sequence).  #101: the record's program graph (one request Program; its Build is not in
the store); #74: every request Program's instances.json.gz."""
import glob
import gzip
import json
import resource
import sys
import time
from collections import Counter

from verity.ir import cut, partition_object as PO
from verity_vllm.query import word as W
from verity_vllm.query.program_view import iter_instance_rows, spec_base, spec_statics

obj = {"format": PO.FORMAT, "program": "0" * 128, "query": PO.query()}
print("object bytes", len(PO.canonical(obj)), flush=True)


def evaluate(spec_calls: Counter, label: str, program_bytes: dict) -> dict:
    memo: dict = {}
    t = time.time()
    units = 0
    for spec, k in spec_calls.items():
        fn = W.specialization(spec_base(spec), spec_statics(spec))
        units += cut.evaluate_definition(fn, 16, memo).units * k
    dt = time.time() - t
    r = {"label": label, "calls": sum(spec_calls.values()), "distinct": len(spec_calls), "population": units, "seconds": round(dt, 1),
         "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024, **program_bytes}
    print(json.dumps(r), flush=True)
    return r


out = []
which = sys.argv[1:] or ["101", "74"]
if "101" in which:
    g = json.load(open("/tmp/xc/graphs/llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager.program.json"))
    specs: Counter = Counter()
    for x in g["groups"]:
        if x.get("varying"):
            (a,), = [tuple(x["varying"])]
            for v, k in x["varying_calls"].items():
                specs[W.specialization(x["definition"], dict(x["statics"], **{a: int(v)})).id] += k
        else:
            specs[x["spec"]] += x["calls"]
    r19 = "/tmp/xc/r101/build_request/instances.json.gz"                   # the r19-reference Build of #101 (same shape, older sampler)
    out.append(evaluate(specs, "101", {"program_gz_bytes_r19": len(open(r19, "rb").read()), "program_json_bytes_r19": len(gzip.open(r19).read())}))
if "74" in which:
    for p in sorted(glob.glob("/tmp/xc/rows/74/*/instances.json.gz")):
        specs = Counter(r["spec"] for r in iter_instance_rows(p))
        raw = 0
        with gzip.open(p) as f:
            while chunk := f.read(1 << 24):
                raw += len(chunk)
        out.append(evaluate(specs, "74/" + p.split("/")[-2], {"program_gz_bytes": len(open(p, "rb").read()), "program_json_bytes": raw}))
json.dump(out, open("/tmp/xc/eval_time.json", "w"), indent=1)
print("EVAL-DONE")
