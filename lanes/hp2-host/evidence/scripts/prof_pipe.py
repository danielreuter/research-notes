"""hp2-host: profile the prover on one tree -- sequential and pipelined passes over N sub-batches.
(a) cProfile of the main thread during the pass (where the launch/host time goes), (b) torch.profiler kernel/launch counts,
(c) pipeline.LAST_STATS (main-thread busy vs blocked).
usage: prof_pipe.py --tree DIR --rel bf16-hopper --zk --vus 170 --subs 12 --pipeline 3 [--cprofile] [--torchprof]
"""
import argparse
import cProfile
import io
import os
import pstats
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument("--tree", required=True)
ap.add_argument("--rel", default="bf16-hopper")
ap.add_argument("--zk", action="store_true")
ap.add_argument("--mode", default="interactive")
ap.add_argument("--vus", type=int, default=170)
ap.add_argument("--subs", type=int, default=12)
ap.add_argument("--pipeline", type=int, default=3)
ap.add_argument("--cprofile", action="store_true")
ap.add_argument("--torchprof", action="store_true")
ap.add_argument("--cache", default="/workspace/instances-cache")
ap.add_argument("--total", type=int, default=4096)
ap.add_argument("--reps", type=int, default=3)
ap.add_argument("--host-trace", action="store_true")
ap.add_argument("--no-warm", action="store_true", help="disable the squeeze worker's core warming")
ap.add_argument("--warm-kb", type=int, default=0, help="warming burst size in KB (0 = default)")
args = ap.parse_args()
os.chdir(args.tree)
sys.path.insert(0, args.tree)
for sub in ("packages/verity/src", "backends/numerical/python"):
    sys.path.insert(0, os.path.join(args.tree, sub))
import torch  # noqa: E402

from backends.direct.ligero import protocol as protocol_mod  # noqa: E402
from backends.direct.ligero.relations import relation  # noqa: E402
from backends.direct.ligero.relchain import RelationChainRunner, instances  # noqa: E402

rel = relation(args.rel)
R = RelationChainRunner(rel, "cuda", -128.0, 2, n_proofs=args.subs, zk=args.zk, mode=args.mode)
data = instances(rel, args.total, procs=8, cache=args.cache)
lay = R.layout(args.vus)
l = lay.l
interactive = args.mode == protocol_mod.MODE_INTERACTIVE
coins = lambda: protocol_mod.Coins.sample() if interactive else None  # noqa: E731
subs = [(si * args.vus, min((si + 1) * args.vus, args.total)) for si in range(args.subs)]
batches = [data[lo:hi] for lo, hi in subs]
# warm-up: sequential (self-check) + every slot
R.prove_vus(batches[0], check=True, min_l=l, coins=coins())
if args.pipeline > 1:
    R.prove_vus_many(batches[:args.pipeline], coins, depth=args.pipeline, min_l=l)
torch.cuda.synchronize()
print("static sets:", [(k[1], {lk: bool(g) for lk, (g, _) in st.graphs.items()}, "commit", bool(st.commit_graph))
                       for k, st in getattr(protocol_mod, "_TESTS_STATIC", {}).items()],
      "ntt graphs:", len(getattr(protocol_mod, "_TGRAPHS", {})))
if args.host_trace:
    protocol_mod.HOST_TRACE = True
from backends.direct.ligero import pipeline as _pl  # noqa: E402
if args.no_warm:
    _pl.HotWorker.active = lambda self, on: None
import threading as _thr, collections as _coll  # noqa: E402
_XOF = _coll.Counter(); _XOF_T = _coll.defaultdict(float)
_orig_xof = _pl._xof_libcrypto
def _xof_traced(lib, seed, out):
    t0_ = time.perf_counter(); r = _orig_xof(lib, seed, out)
    nm = _thr.current_thread().name; _XOF[nm] += 1; _XOF_T[nm] += time.perf_counter() - t0_
    return r
_pl._xof_libcrypto = _xof_traced
if args.warm_kb:
    _pl.HotWorker._WARM = bytes(args.warm_kb * 1024)


def seq_pass():
    out = []
    for b in batches:
        out.append(R.prove_vus(b, check=False, min_l=l, coins=coins()))
    torch.cuda.synchronize()
    return out


def pipe_pass():
    return R.prove_vus_many(batches, coins, depth=args.pipeline, min_l=l)


from backends.direct.ligero import pipeline as pl  # noqa: E402

for name, fn in (("sequential", seq_pass), ("pipelined", pipe_pass)):
    if name == "pipelined" and args.pipeline <= 1:
        continue
    walls = []
    for _ in range(args.reps):
        t0 = time.perf_counter()
        res = fn()
        walls.append(time.perf_counter() - t0)
    print(f"{name}: {len(subs)} sub-batches, walls {[round(w, 3) for w in walls]} s -> best {min(walls) / len(subs) * 1e3:.1f} ms/sub-batch")
    print("  squeeze calls by thread:", dict(_XOF), {k: round(v * 1e3 / max(1, _XOF[k]), 2) for k, v in _XOF_T.items()}, "ms avg"); _XOF.clear(); _XOF_T.clear()
    if name == "pipelined":
        print("  LAST_STATS", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in pl.LAST_STATS.items()})
        tm = {}
        for _, pf, _, _ in res[0]:
            for k, v in pf.timings.items():
                if k.startswith("measured_"):
                    tm[k[9:]] = tm.get(k[9:], 0.0) + v
        print("  measured (event) phase sums over the pass:", {k: round(v / len(subs) * 1e3, 2) for k, v in tm.items() if not k.startswith("host_")}, "ms/sub-batch")
        if args.host_trace:
            ht = {}
            for _, pf, _, _ in res[0]:
                for k, v in pf.timings.items():
                    if k.startswith("host_"):
                        ht[k[5:]] = ht.get(k[5:], 0.0) + v
            print("  host trace:", {k: round(v / len(subs) * 1e3, 2) for k, v in ht.items()}, "ms/sub-batch")
    else:
        tm = {}
        for pf, _, _ in res:
            for k, v in pf.timings.items():
                tm[k] = tm.get(k, 0.0) + v
        print("  phase sums:", {k: round(v / len(subs) * 1e3, 2) for k, v in tm.items() if not k.startswith("host_")}, "ms/sub-batch")
        if args.host_trace:
            print("  host trace:", {k[5:]: round(v / len(subs) * 1e3, 2) for k, v in tm.items() if k.startswith("host_")}, "ms/sub-batch")
    if args.cprofile:
        pr = cProfile.Profile()
        pr.enable()
        fn()
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats("tottime")
        ps.print_stats(28)
        print(f"  --- cProfile ({name}) top by tottime:")
        print("\n".join(line for line in s.getvalue().splitlines()[:45] if line.strip()))
    if args.torchprof:
        from torch.profiler import ProfilerActivity, profile
        with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
            fn()
        evs = prof.key_averages()
        launches = sum(e.count for e in evs if e.device_type.name == "CUDA")
        cuda_ms = sum(e.device_time_total for e in evs if e.device_type.name == "CUDA") / 1e3
        print(f"  --- torch.profiler ({name}): {launches} kernel launches, {cuda_ms:.1f} ms GPU total over the pass = "
              f"{launches / len(subs):.0f} launches, {cuda_ms / len(subs):.2f} ms GPU per sub-batch")
        top = sorted([e for e in evs if e.device_type.name == "CUDA"], key=lambda e: -e.device_time_total)[:15]
        for e in top:
            print(f"    {e.device_time_total / 1e3 / len(subs):7.3f} ms/sub  x{e.count / len(subs):6.1f}  {e.key[:90]}")
        cpu_top = sorted([e for e in evs if e.device_type.name == "CPU"], key=lambda e: -e.self_cpu_time_total)[:12]
        print("    CPU self time top:")
        for e in cpu_top:
            print(f"    {e.self_cpu_time_total / 1e3 / len(subs):7.3f} ms/sub  x{e.count / len(subs):6.1f}  {e.key[:90]}")
