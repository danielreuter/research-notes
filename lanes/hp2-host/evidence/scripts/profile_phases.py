"""Lane hostphase, step 1: attribute every prover phase of ONE bf16-hopper sub-batch (170 VUs, l = 16384) to kernel launches,
GPU kernel time, device->host syncs and host compute, from a torch.profiler chrome trace (CPU + CUDA activities).

Usage (pod, cwd = source tree):  python profile_phases.py --relation bf16-hopper [--zk] [--mode interactive] --out DIR
"""
import argparse, json, os, sys, time, collections
import numpy as np
import torch
from torch.profiler import profile, ProfilerActivity

from backends.direct.ligero import protocol as protocol_mod
from backends.direct.ligero.relations import relation
from backends.direct.ligero.relchain import RelationChainRunner, instances

ap = argparse.ArgumentParser()
ap.add_argument("--relation", default="bf16-hopper")
ap.add_argument("--zk", action="store_true")
ap.add_argument("--mode", default="interactive")
ap.add_argument("--vus", type=int, default=170)
ap.add_argument("--batch", type=int, default=16384)
ap.add_argument("--total-vus", type=int, default=4096)
ap.add_argument("--cache", default="/workspace/instances-cache")
ap.add_argument("--out", default=".")
ap.add_argument("--full", action="store_true", help="also time the full 4096-VU pass (no profiler) per phase")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)

rel = relation(args.relation)
steps = rel.steps
per_proof = args.batch // steps
n_proofs = -(-args.total_vus // per_proof)
R = RelationChainRunner(rel, "cuda", -128.0, 2, n_proofs=n_proofs, zk=args.zk, mode=args.mode)
sys_ = R.sys
kinds = collections.Counter(op[0] for op in sys_.program)
print(f"system m={sys_.m} pins={len(sys_.pins)} hints={len(sys_.hints)} L={R.tb.L} Q={R.tb.Q} program ops={len(sys_.program)} {dict(kinds)}")
data = instances(rel, args.total_vus, cache=args.cache)
lay = R.layout(per_proof)
cfg = R.cfg(lay.l)
print("config", cfg, "layout", lay)

# ---- patch the prover's clock so every phase is a named user annotation in the trace ----------------------------------
_names = []
_ranges = []
class ProfClock(protocol_mod._Clock):
    def __init__(self, device):
        super().__init__(device)
        self._rf = torch.autograd.profiler.record_function(f"phase_{len(_names)}")
        self._rf.__enter__()
        self._t0 = time.perf_counter()
    def lap(self, name):
        super().lap(name)
        self._rf.__exit__(None, None, None)
        _names.append(name)
        _ranges.append((self._t0, time.perf_counter()))
        self._rf = torch.autograd.profiler.record_function(f"phase_{len(_names)}")
        self._rf.__enter__()
        self._t0 = time.perf_counter()
    def total(self):
        t = super().total()
        self._rf.__exit__(None, None, None)
        _names.append("_tail")
        _ranges.append((self._t0, time.perf_counter()))
        return t
protocol_mod._Clock = ProfClock

vus = data[:per_proof]
# warm-up (compile, graph capture, self-check)
V = protocol_mod.Coins.sample() if R.interactive else None
proof, pubs, lay_i = R.prove_vus(vus, check=True, min_l=lay.l, coins=V)
ok, why = R.verify_vus(proof, pubs, lay_i, coins=V)
print("warm-up verify:", ok, why, {k: round(v, 4) for k, v in proof.timings.items()})
_names.clear(); _ranges.clear()
# a second un-profiled timing for the reference
V = protocol_mod.Coins.sample() if R.interactive else None
proof, pubs, lay_i = R.prove_vus(vus, check=False, min_l=lay.l, coins=V)
ref_t = dict(proof.timings)
print("un-profiled sub-batch:", {k: round(v, 4) for k, v in ref_t.items()})
_names.clear(); _ranges.clear()

# ---- the profiled sub-batch (marshalling + hints + prove) -------------------------------------------------------------
V = protocol_mod.Coins.sample() if R.interactive else None
torch.cuda.synchronize()
with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=True, with_stack=True) as prof:
    with torch.autograd.profiler.record_function("prove_vus_marshal_and_hints"):
        t_pv0 = time.perf_counter()
        proof, pubs, lay_i = R.prove_vus(vus, check=False, min_l=lay.l, coins=V)
        t_pv1 = time.perf_counter()
    torch.cuda.synchronize()
prof_t = dict(proof.timings)
print("profiled sub-batch:", {k: round(v, 4) for k, v in prof_t.items()}, "prove_vus wall", round(t_pv1 - t_pv0, 4))
trace = os.path.join(args.out, "trace_subbatch.json")
prof.export_chrome_trace(trace)
print("trace", trace, os.path.getsize(trace) // 1_000_000, "MB")

# ---- attribution from the trace ---------------------------------------------------------------------------------------
ev = json.load(open(trace))["traceEvents"]
phases = {}   # name -> (ts, te)
for e in ev:
    if e.get("cat") == "user_annotation" and e.get("name", "").startswith("phase_"):
        i = int(e["name"].split("_")[1])
        if i < len(_names):
            phases[_names[i]] = (e["ts"], e["ts"] + e["dur"])
    if e.get("cat") == "user_annotation" and e.get("name") == "prove_vus_marshal_and_hints":
        phases["_prove_vus_total"] = (e["ts"], e["ts"] + e["dur"])
# hints phase = from prove_vus start to the prover clock's first phase start
if "_prove_vus_total" in phases and phases:
    first = min(v[0] for k, v in phases.items() if not k.startswith("_"))
    phases["hints+marshal(pre-prove)"] = (phases["_prove_vus_total"][0], first)

def phase_of(ts):
    for name, (a, b) in phases.items():
        if name.startswith("_"):
            continue
        if a <= ts <= b:
            return name
    return None

SYNC_NAMES = ("cudaStreamSynchronize", "cudaDeviceSynchronize", "cudaMemcpyAsync", "cudaMemcpy", "cudaEventSynchronize", "cudaStreamWaitEvent")
runtime = [e for e in ev if e.get("cat") == "cuda_runtime"]
kernels = [e for e in ev if e.get("cat") in ("kernel", "gpu_memcpy", "gpu_memset")]
cpu_ops = [e for e in ev if e.get("cat") == "cpu_op"]
corr2phase = {}
stat = collections.defaultdict(lambda: collections.Counter())
kern_names = collections.defaultdict(lambda: collections.Counter())
for e in runtime:
    ph = phase_of(e["ts"])
    if ph is None:
        continue
    name = e["name"]
    corr = e.get("args", {}).get("correlation")
    if corr is not None:
        corr2phase[corr] = ph
    stat[ph]["runtime_calls"] += 1
    stat[ph]["runtime_cpu_us"] += e["dur"]
    if name == "cudaLaunchKernel":
        stat[ph]["launches"] += 1
        stat[ph]["launch_cpu_us"] += e["dur"]
    elif name == "cudaGraphLaunch":
        stat[ph]["graph_launches"] += 1
    elif name in SYNC_NAMES:
        stat[ph]["syncs"] += 1
        stat[ph]["sync_cpu_us"] += e["dur"]
    elif "Memcpy" in name or "memcpy" in name:
        stat[ph]["memcpy_calls"] += 1
        stat[ph]["memcpy_cpu_us"] += e["dur"]
for e in kernels:
    corr = e.get("args", {}).get("correlation")
    ph = corr2phase.get(corr)
    if ph is None:
        ph = phase_of(e["ts"])   # graph-launched kernels: attribute by time (they run when the graph runs)
    if ph is None:
        stat["_unattributed"]["kernels"] += 1
        stat["_unattributed"]["gpu_us"] += e["dur"]
        continue
    if e["cat"] == "kernel":
        stat[ph]["kernels"] += 1
        stat[ph]["gpu_kernel_us"] += e["dur"]
        kern_names[ph][e["name"][:60]] += e["dur"]
    else:
        stat[ph]["gpu_memcpy"] += 1
        stat[ph]["gpu_memcpy_us"] += e["dur"]
        if "DtoH" in e["name"] or "Device to Host" in e.get("name", "") or (e.get("args", {}).get("kind") or "").lower().find("dtoh") >= 0:
            stat[ph]["d2h_copies"] += 1
            stat[ph]["d2h_bytes"] += int(e.get("args", {}).get("bytes", 0))
for e in cpu_ops:
    ph = phase_of(e["ts"])
    if ph is None:
        continue
    stat[ph]["torch_ops"] += 1
    if e["name"] in ("aten::item", "aten::_local_scalar_dense", "aten::to", "aten::copy_", "aten::numpy", "aten::tolist"):
        stat[ph][f"op:{e['name']}"] += 1

rows = []
order = [n for n in _names if n in phases] + ["hints+marshal(pre-prove)"]
print()
print(f"{'phase':<28}{'wall ms':>9}{'GPU kern ms':>12}{'kernels':>9}{'launches':>9}{'graphs':>7}{'syncs':>6}{'sync ms':>9}{'memcpy':>7}{'D2H MB':>8}{'torch ops':>10}{'verdict':>16}")
for name in order:
    a, b = phases[name]
    wall = (b - a) / 1e3
    s = stat.get(name, collections.Counter())
    gpu = s["gpu_kernel_us"] / 1e3
    sync = s["sync_cpu_us"] / 1e3
    launches = s["launches"]
    kern = s["kernels"]
    d2h = s["d2h_bytes"] / 1e6
    if wall < 0.05:
        verdict = "-"
    elif gpu > 0.7 * wall:
        verdict = "GPU-bound"
    elif kern > 200 and gpu < 0.5 * wall and (launches * 5e-3 + s["graph_launches"] * 0) < wall and kern * 3e-3 > 0.4 * wall:
        verdict = "launch/granularity"
    elif sync > 0.5 * wall:
        verdict = "sync-bound"
    elif launches > 300 and launches * 4e-3 > 0.4 * wall:
        verdict = "launch-bound(host)"
    else:
        verdict = "CPU-compute/Python"
    rows.append({"phase": name, "wall_ms": wall, "gpu_kernel_ms": gpu, "kernels": kern, "launches": launches,
                 "graph_launches": s["graph_launches"], "syncs": s["syncs"], "sync_ms": sync, "memcpy": s["memcpy_calls"],
                 "d2h_mb": d2h, "torch_ops": s["torch_ops"], "verdict": verdict,
                 "top_kernels": kern_names[name].most_common(6)})
    print(f"{name:<28}{wall:>9.2f}{gpu:>12.2f}{kern:>9}{launches:>9}{s['graph_launches']:>7}{s['syncs']:>6}{sync:>9.2f}{s['memcpy_calls']:>7}{d2h:>8.2f}{s['torch_ops']:>10}{verdict:>16}")
print("\nunattributed:", dict(stat.get("_unattributed", {})))
for r in rows:
    if r["top_kernels"]:
        print(f"\n[{r['phase']}] top kernels (name: us):")
        for n, us in r["top_kernels"]:
            print(f"   {us:>10.0f}  {n}")

out = {"relation": args.relation, "zk": args.zk, "mode": args.mode, "vus": per_proof, "l": lay.l, "cfg": str(cfg),
       "system": {"m": sys_.m, "pins": len(sys_.pins), "hints": len(sys_.hints), "L": R.tb.L, "Q": R.tb.Q,
                  "program_ops": len(sys_.program), "kinds": dict(kinds)},
       "unprofiled_timings": ref_t, "profiled_timings": prof_t, "rows": rows}

# ---- the full pass, per phase, no profiler (the bench's own numbers, one rep) ----------------------------------------
if args.full:
    agg = collections.Counter()
    t0 = time.perf_counter()
    for lo in range(0, args.total_vus, per_proof):
        V = protocol_mod.Coins.sample() if R.interactive else None
        proof, pubs, lay_i = R.prove_vus(data[lo:lo + per_proof], check=False, min_l=lay.l, coins=V)
        for k, v in proof.timings.items():
            agg[k] += v
    wall = time.perf_counter() - t0
    agg["_pass_wall"] = wall
    print("\nfull pass (one rep, %d sub-batches):" % n_proofs, {k: round(v, 3) for k, v in agg.items()})
    out["full_pass"] = dict(agg)
json.dump(out, open(os.path.join(args.out, "attribution.json"), "w"), indent=1, default=str)
print("wrote", os.path.join(args.out, "attribution.json"))
