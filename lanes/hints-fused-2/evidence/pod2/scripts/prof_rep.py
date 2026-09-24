"""prof.py OUTSTEM -- run.py argv... : bench-vu unchanged, the LAST timed rep's prove_vus_many under torch.profiler (CUPTI sees the
cupy/NVRTC kernels too).  Writes OUTSTEM.trace.json (chrome trace) and OUTSTEM.txt: wall, device-busy union, kernel/memcpy counts,
top kernels by device time, host launch-API totals."""
import json, runpy, sys, time
from collections import defaultdict

import torch
from torch.profiler import ProfilerActivity, profile

stem = sys.argv[1]
sys.argv = ["backends.direct.ligero.run"] + sys.argv[2:]
reps = int(sys.argv[sys.argv.index("--reps") + 1])

from backends.direct.ligero import relchain  # noqa: E402

orig = relchain.RelationChainRunner.prove_vus_many
calls = [0]


def union(iv):
    tot, cur_s, cur_e = 0.0, None, None
    for s, e in sorted(iv):
        if cur_e is None or s > cur_e:
            if cur_e is not None:
                tot += cur_e - cur_s
            cur_s, cur_e = s, e
        else:
            cur_e = max(cur_e, e)
    return tot + ((cur_e - cur_s) if cur_e is not None else 0.0)


def wrapped(self, *a, **k):
    calls[0] += 1
    if calls[0] != reps + 1:                  # call 1 = the warm-up's pipeline slots; calls 2..reps+1 = the timed reps
        return orig(self, *a, **k)
    torch.cuda.synchronize()
    with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
        t0 = time.perf_counter()
        r = orig(self, *a, **k)
        torch.cuda.synchronize()
        wall = time.perf_counter() - t0
    prof.export_chrome_trace(stem + ".trace.json")
    ev = json.load(open(stem + ".trace.json"))["traceEvents"]
    kern = [e for e in ev if e.get("cat") == "kernel"]
    mcpy = [e for e in ev if e.get("cat") in ("gpu_memcpy", "gpu_memset")]
    rt = [e for e in ev if e.get("cat") == "cuda_runtime"]
    by = defaultdict(lambda: [0, 0.0])
    for e in kern:
        n = e["name"][:110]
        by[n][0] += 1
        by[n][1] += e["dur"]
    rtby = defaultdict(lambda: [0, 0.0])
    for e in rt:
        rtby[e["name"]][0] += 1
        rtby[e["name"]][1] += e["dur"]
    ksum = sum(e["dur"] for e in kern)
    L = [f"profiled rep {calls[0] - 1} (under the profiler): wall {wall * 1e3:.1f} ms",
         f"kernels: {len(kern)} launches, sum {ksum / 1e3:.1f} ms, device-busy union {union([(e['ts'], e['ts'] + e['dur']) for e in kern]) / 1e3:.1f} ms",
         f"memcpy/memset: {len(mcpy)}, sum {sum(e['dur'] for e in mcpy) / 1e3:.1f} ms; busy union incl. copies "
         f"{union([(e['ts'], e['ts'] + e['dur']) for e in kern + mcpy]) / 1e3:.1f} ms",
         f"streams with kernels: {sorted(set(e.get('tid') for e in kern), key=str)}", "", "top kernels by device time (count, ms, % of kernel sum):"]
    for n, (c, d) in sorted(by.items(), key=lambda x: -x[1][1])[:30]:
        L.append(f"  {d / 1e3:8.2f} ms {100 * d / max(ksum, 1):5.1f}%  x{c:<6d} {n}")
    L += ["", "host CUDA runtime API (count, ms):"]
    for n, (c, d) in sorted(rtby.items(), key=lambda x: -x[1][1])[:12]:
        L.append(f"  {d / 1e3:8.2f} ms  x{c:<6d} {n}")
    L += ["", "top host ops by self CPU time:", prof.key_averages().table(sort_by="self_cpu_time_total", row_limit=25, max_name_column_width=70)]
    open(stem + ".txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L[:40]), flush=True)
    return r


relchain.RelationChainRunner.prove_vus_many = wrapped
runpy.run_module("backends.direct.ligero.run", run_name="__main__")
