"""arith: profile one timed pipelined pass of `run.py ... bench-vu` (pod only).

    python prof.py OUTDIR [--profile-call N] -- <run.py args...>

Wraps pipeline.prove_many: every call's LAST_STATS (wall, host_busy, host_waited) goes to OUTDIR/passes.jsonl; call N
(default 3: after the warm-up passes) runs under torch.profiler (CUDA activities, graph kernels included) and writes
OUTDIR/kernels.txt (GPU time per kernel name, summed over the pass) and OUTDIR/trace.json.gz.
"""
import gzip
import json
import os
import shutil
import sys
import time
from collections import defaultdict

out = sys.argv[1]
argv = sys.argv[2:]
call_n = 3
if argv and argv[0] == "--profile-call":
    call_n = int(argv[1])
    argv = argv[2:]
if argv and argv[0] == "--":
    argv = argv[1:]
os.makedirs(out, exist_ok=True)

import torch  # noqa: E402
from backends.direct.ligero import pipeline  # noqa: E402

_orig = pipeline.prove_many
_calls = [0]


def wrapped(*a, **kw):
    _calls[0] += 1
    i = _calls[0]
    if i != call_n:
        r = _orig(*a, **kw)
        with open(os.path.join(out, "passes.jsonl"), "a") as f:
            f.write(json.dumps({"call": i, **{k: v for k, v in pipeline.LAST_STATS.items()}}) + "\n")
        return r
    from torch.profiler import ProfilerActivity, profile
    with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
        r = _orig(*a, **kw)
    st = dict(pipeline.LAST_STATS)
    with open(os.path.join(out, "passes.jsonl"), "a") as f:
        f.write(json.dumps({"call": i, "profiled": True, **st}) + "\n")
    tpath = os.path.join(out, "trace.json")
    prof.export_chrome_trace(tpath)
    with open(tpath, "rb") as fi, gzip.open(tpath + ".gz", "wb") as fo:
        shutil.copyfileobj(fi, fo)
    tr = json.load(open(tpath))
    os.remove(tpath)
    per = defaultdict(lambda: [0.0, 0])
    lo, hi = None, None
    busy = []
    for e in tr.get("traceEvents", []):
        if e.get("ph") != "X":
            continue
        cat = e.get("cat", "")
        if cat in ("kernel", "gpu_memcpy", "gpu_memset"):
            nm = e.get("name", "?")
            if cat != "kernel":
                nm = cat + ":" + nm
            per[nm][0] += e.get("dur", 0.0)
            per[nm][1] += 1
            s, d = e["ts"], e.get("dur", 0.0)
            busy.append((s, s + d))
            lo = s if lo is None else min(lo, s)
            hi = s + d if hi is None else max(hi, s + d)
    busy.sort()
    union, cur = 0.0, None
    for s, t in busy:
        if cur is None or s > cur[1]:
            if cur is not None:
                union += cur[1] - cur[0]
            cur = [s, t]
        else:
            cur[1] = max(cur[1], t)
    if cur is not None:
        union += cur[1] - cur[0]
    tot = sum(v[0] for v in per.values())
    with open(os.path.join(out, "kernels.txt"), "w") as f:
        f.write(f"pass wall {st.get('wall', 0):.4f} s host_busy {st.get('host_busy', 0):.4f} host_waited "
                f"{st.get('host_waited', 0):.4f}; gpu span {((hi or 0) - (lo or 0)) / 1e6:.4f} s, gpu busy (union) "
                f"{union / 1e6:.4f} s, kernel sum {tot / 1e6:.4f} s\n")
        for nm, (d, c) in sorted(per.items(), key=lambda kv: -kv[1][0]):
            f.write(f"{d / 1e3:10.3f} ms {c:6d}x {100 * d / max(tot, 1e-9):5.1f}%  {nm[:160]}\n")
    return r


pipeline.prove_many = wrapped
from backends.direct.ligero import run  # noqa: E402

t0 = time.time()
rc = run.main(argv)
print(f"prof: rc={rc} wall={time.time() - t0:.1f}s calls={_calls[0]} -> {out}")
sys.exit(rc or 0)
