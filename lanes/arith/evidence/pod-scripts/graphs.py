"""arith: attribute a prof.py trace's GPU kernels to the launch that issued them (a CUDA graph replay or an eager call).

    python graphs.py TRACE.json.gz

Groups kernels by their runtime launch (correlation id); a group containing a marker kernel is classified (tests graph:
quad_*; commit graph: witness_program; hints: hints_fused); prints GPU time per class and the top kernels of each.
"""
import gzip
import json
import sys
from collections import defaultdict

tr = json.load(gzip.open(sys.argv[1]))
ev = [e for e in tr["traceEvents"] if e.get("ph") == "X"]
launch = {}
for e in ev:
    if e.get("cat") == "cuda_runtime":
        c = (e.get("args") or {}).get("correlation")
        if c is not None:
            launch[c] = e.get("name")
groups = defaultdict(list)
for e in ev:
    if e.get("cat") in ("kernel", "gpu_memcpy", "gpu_memset"):
        c = (e.get("args") or {}).get("correlation")
        groups[c].append(e)
MARK = [("tests", "quad_"), ("tests", "lincomb"), ("commit", "witness_program"), ("hints", "hints_fused"),
        ("merkle", "blake3"), ("encode", "rs_encode")]
cls_time = defaultdict(float)
cls_k = defaultdict(lambda: defaultdict(float))
cls_n = defaultdict(int)
for c, ks in groups.items():
    names = [k["name"] for k in ks]
    cl = "other:" + str(launch.get(c, "?"))[:40]
    for lab, mk in MARK:
        if any(mk in nm for nm in names):
            cl = lab
            break
    cls_n[cl] += 1
    for k in ks:
        cls_time[cl] += k.get("dur", 0.0)
        cls_k[cl][k["name"][:90]] += k.get("dur", 0.0)
tot = sum(cls_time.values())
for cl, t in sorted(cls_time.items(), key=lambda kv: -kv[1]):
    print(f"{cl:50s} {t / 1e3:9.3f} ms  {100 * t / tot:5.1f}%  launches {cls_n[cl]}")
    if t > 0.01 * tot:
        for nm, d in sorted(cls_k[cl].items(), key=lambda kv: -kv[1])[:14]:
            print(f"      {d / 1e3:8.3f} ms  {nm}")
