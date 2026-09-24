import time, torch, sys
sys.path.insert(0, "/workspace/src-hp2")
from backends.direct.ligero import tests_fused
from backends.direct.ligero.field import P
from torch.profiler import profile, ProfilerActivity
dev = torch.device("cuda")
f = tests_fused.fused_for(6, dev)
g = torch.Generator(device="cpu").manual_seed(1)
def ktime(fn, reps=20):
    fn(); torch.cuda.synchronize()
    with profile(activities=[ProfilerActivity.CUDA]) as prof:
        for _ in range(reps): fn()
        torch.cuda.synchronize()
    tot = {}
    for e in prof.key_averages():
        if e.device_type.name == "CUDA" and ("comb" in e.key):
            tot[e.key] = e.device_time_total / reps / 1e3 if hasattr(e, "device_time_total") else e.cuda_time_total / reps / 1e3
    return tot
for R, cols, dt in ((512, 16384, torch.int32), (1024, 8192, torch.int64), (2534, 65536, torch.int32), (3328, 16384, torch.int64)):
    X = torch.randint(0, P, (R, cols), generator=g).to(dt).to(dev)
    C = torch.randint(0, P, (6, R), generator=g).to(dev)
    mb = R * cols * X.element_size() / 1e6
    for sq in (False, True):
        tests_fused.VEC_COLS = 1; ts = ktime(lambda: f.lincomb(C, X, square_minus=sq))
        tests_fused.VEC_COLS = 4; tv = ktime(lambda: f.lincomb(C, X, square_minus=sq))
        el = R * cols
        a = sum(ts.values()); b = sum(tv.values())
        print(f"{R}x{cols} {str(dt)[6:]} {mb:.0f} MB sq={sq}: scalar {a:.3f} ms ({el/a/1e6:.0f} Melem/ms, {mb/a:.0f} GB/s) | v4 {b:.3f} ms ({el/b/1e6:.0f} Melem/ms, {mb/b:.0f} GB/s)  x{a/b:.2f}")
