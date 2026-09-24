"""Pipelined fp4 pass diagnostics on an integration tree: pipeline.LAST_STATS (main-thread busy vs blocked) and the
un-rescaled event-measured phases (timings['measured_<phase>']) per sub-batch, at depth N, 4096 VUs, l = --batch / STEPS."""
import argparse
import os
import statistics
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument("--tree", required=True)
ap.add_argument("--batch", type=int, default=16384)
ap.add_argument("--depth", type=int, default=3)
ap.add_argument("--zk", action="store_true")
ap.add_argument("--passes", type=int, default=3)
ap.add_argument("--vus", type=int, default=4096)
ap.add_argument("--squeeze-workers", type=int, default=1, help="DIAGNOSTIC: replace pipeline.SQUEEZE (one hot thread) by N round-robin hot threads")
args = ap.parse_args()
os.chdir(args.tree)
sys.path.insert(0, args.tree)
for sub in ("packages/verity/src", "backends/numerical/python"):
    sys.path.insert(0, os.path.join(args.tree, sub))
import torch  # noqa: E402

from backends.direct.ligero import pipeline, protocol  # noqa: E402
from backends.direct.ligero.fp4.chain import STEPS, FP4ChainRunner, instances_fp4  # noqa: E402

if args.squeeze_workers > 1:
    class MultiHot:
        """N of pipeline.HotWorker, requests round-robin: the challenge squeezes of the sub-batches in flight run on N cores
        (libcrypto XOF, GIL released) instead of queueing on one.  Same bytes, same order per sub-batch: protocol-identical."""
        def __init__(self, n):
            self.ws = [pipeline.HotWorker() for _ in range(n)]
            self.i = 0
        def active(self, on):
            for w in self.ws:
                w.active(on)
        def submit(self, fn, *a):
            w = self.ws[self.i % len(self.ws)]
            self.i += 1
            return w.submit(fn, *a)
    pipeline.SQUEEZE.active(False)
    pipeline.SQUEEZE = MultiHot(args.squeeze_workers)
    print(f"DIAGNOSTIC: pipeline.SQUEEZE -> {args.squeeze_workers} hot workers (shake_overlapped={pipeline.shake_overlapped()})")
per = args.batch // STEPS
n_proofs = -(-args.vus // per)
R = FP4ChainRunner("cuda", -128.0, 2, n_proofs=n_proofs, zk=args.zk, hints="device")
data = instances_fp4(args.vus)
lay = R.layout(per)
l = lay.l
subs = [(i * per, min(args.vus, (i + 1) * per)) for i in range(n_proofs)]
coins = lambda: protocol.Coins.sample()  # noqa: E731
print(f"l={l} n_proofs={n_proofs} per={per} zk={args.zk} depth={args.depth} m={R.sys.m}")
# warm-up: sequential over all sub-batches (compile, self-check on the first), then one full pipelined pass
for si, (lo, hi) in enumerate(subs):
    R.prove_vus(data[lo:hi], check=(si == 0), min_l=l, coins=coins())
R.prove_vus_many([data[lo:hi] for lo, hi in subs], coins, depth=args.depth, min_l=l)
if os.environ.get("COUNT_CAPTURES"):
    # DIAGNOSTIC: count CUDA graph captures, static-set rebuilds and pinned-buffer regrowth per pass
    _counts = {"CUDAGraph": 0, "TestsStatic": 0, "pinned_alloc": 0, "graph_reset": 0}
    _g_init = torch.cuda.CUDAGraph.__init__
    def _g_init2(self, *a, **k):
        _counts["CUDAGraph"] += 1
        return _g_init(self, *a, **k)
    torch.cuda.CUDAGraph.__init__ = _g_init2
    _g_reset = torch.cuda.CUDAGraph.reset
    def _g_reset2(self, *a, **k):
        _counts["graph_reset"] += 1
        return _g_reset(self, *a, **k)
    torch.cuda.CUDAGraph.reset = _g_reset2
    _ts_init = protocol._TestsStatic.__init__
    def _ts_init2(self, *a, **k):
        _counts["TestsStatic"] += 1
        return _ts_init(self, *a, **k)
    protocol._TestsStatic.__init__ = _ts_init2
    _pinned = pipeline.Slot.pinned
    def _pinned2(self, name, nbytes):
        buf = self._pinned.get(name)
        if buf is None or buf.numel() < nbytes:
            _counts["pinned_alloc"] += 1
            print(f"      pinned regrow slot {self.index} {name}: {0 if buf is None else buf.numel()} -> {nbytes}")
        return _pinned(self, name, nbytes)
    pipeline.Slot.pinned = _pinned2
    print("DIAGNOSTIC: counting graph captures / static-set rebuilds / pinned regrowth")
if os.environ.get("GC_OFF"):
    import gc
    gc.collect(); gc.disable(); print("DIAGNOSTIC: gc disabled for the timed passes")
for p in range(args.passes):
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    many, wall = R.prove_vus_many([data[lo:hi] for lo, hi in subs], coins, depth=args.depth, min_l=l)
    torch.cuda.synchronize()
    w2 = time.perf_counter() - t0
    st = dict(pipeline.LAST_STATS)
    if os.environ.get("COUNT_CAPTURES"):
        print(f"   captures this pass: {_counts}"); _counts.update({k: 0 for k in _counts})
    print(f"pass {p}: wall {wall*1e3:.1f} ms (sync {w2*1e3:.1f}); host busy {st['host_busy']*1e3:.1f} ms = {100*st['host_busy']/st['wall']:.0f}% of wall, "
          f"blocked {st['host_waited']*1e3:.1f} ms; stage_busy_ms {st['stage_busy_ms']}")
    meas = {}
    for (V, proof, pubs, lay_i) in many:
        for k, v in proof.timings.items():
            if k.startswith("measured_"):
                meas.setdefault(k[9:], []).append(v)
    if meas:
        print("   event-measured per sub-batch (ms, median over the %d; sum of medians %.1f):" % (n_proofs, sum(statistics.median(v) for v in meas.values()) * 1e3),
              " ".join(f"{k}={statistics.median(v)*1e3:.2f}" for k, v in sorted(meas.items(), key=lambda kv: -statistics.median(kv[1])) if statistics.median(v) > 0.00005))
        full = [i for i, (lo, hi) in enumerate(subs) if hi - lo == per]
        tail = [i for i, (lo, hi) in enumerate(subs) if hi - lo != per]
        for name, idx in (("full", full), ("tail", tail)):
            if idx:
                tot = [sum(v for k, v in many[i][1].timings.items() if k.startswith("measured_")) for i in idx]
                print(f"   {name} sub-batches {idx}: event-measured sum per sub-batch {statistics.median(tot)*1e3:.1f} ms")
print(f"peak device {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
if os.environ.get("PROFILE"):
    from torch.profiler import ProfilerActivity, profile
    torch.cuda.synchronize()
    with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
        t0 = time.perf_counter()
        many, wall = R.prove_vus_many([data[lo:hi] for lo, hi in subs], coins, depth=args.depth, min_l=l)
        torch.cuda.synchronize()
        w = time.perf_counter() - t0
    ka = prof.key_averages()
    cuda_total = sum(getattr(e, "self_device_time_total", getattr(e, "self_cuda_time_total", 0)) for e in ka) / 1e3
    print(f"PROFILE pass: wall {w*1e3:.1f} ms; sum of GPU kernel self time {cuda_total:.1f} ms ({100*cuda_total/(w*1e3):.0f}% of wall; streams overlap so > 100% is possible)")
    rows = sorted(ka, key=lambda e: -getattr(e, "self_device_time_total", getattr(e, "self_cuda_time_total", 0)))[:14]
    for e in rows:
        d = getattr(e, "self_device_time_total", getattr(e, "self_cuda_time_total", 0)) / 1e3
        if d > 0.2:
            print(f"   {d:7.2f} ms  x{e.count:<5d} {e.key[:110]}")
    cpu_rows = sorted(ka, key=lambda e: -e.self_cpu_time_total)[:8]
    print("   main-thread CPU self time (ms): " + "; ".join(f"{e.key[:40]}={e.self_cpu_time_total/1e3:.1f}" for e in cpu_rows))
