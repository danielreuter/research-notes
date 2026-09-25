"""agkr-nvf4: kernels.lookup_mults vs logup.multiplicities' torch key-map path on a synthetic LK-shaped table (110613 rows,
5 columns, keys < 2^25) and 16.3M query tuples (skewed toward a few hot rows); equal counts, the same miss detection,
and times.  python 16_mults.py"""
import time

import torch

from gpu import kernels

dev = torch.device("cuda")
g = torch.Generator(device=dev).manual_seed(3)
R, W, N = 110613, 5, 98304 * 166
keys = torch.randperm(1 << 25, device=dev, generator=g)[:R].to(torch.int64)
trows = torch.cat([keys[:, None], torch.randint(0, 1 << 30, (R, W - 1), device=dev, generator=g)], 1)
kmap = torch.full((int(keys.max()) + 1,), -1, dtype=torch.int64, device=dev)
kmap[keys] = torch.arange(R, dtype=torch.int64, device=dev)
pick = torch.where(torch.rand(N, device=dev, generator=g) < 0.5, torch.randint(0, 16, (N,), device=dev, generator=g),
                   torch.randint(0, R, (N,), device=dev, generator=g))
v = trows[pick].contiguous()


def torch_path(vals):
    m = torch.zeros((R,), dtype=torch.int64, device=dev)
    for x in vals:
        key = x[:, 0]
        if bool((key >= kmap.shape[0]).any()):
            return None
        idx = kmap[key]
        if not bool(((idx >= 0) & (trows[idx.clamp(min=0)] == x).all(dim=1)).all()):
            return None
        m += torch.bincount(idx, minlength=R)
    return m


def bench(f, reps=7):
    f()
    torch.cuda.synchronize()
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        f()
        torch.cuda.synchronize()
        ts.append(time.perf_counter() - t)
    return sorted(ts)[reps // 2] * 1e3


m_ref = torch_path([v])
m_new, bad = kernels.lookup_mults([v], kmap, trows)
print("equal", bool((m_ref == m_new).all()), "bad", bad, "sum", int(m_new.sum()), N)
for name, mut in (("col", lambda x: x.__setitem__((5, 3), x[5, 3] + 1)), ("key_gap", lambda x: x.__setitem__((7, 0), int(kmap.shape[0]) - 2)),
                  ("key_big", lambda x: x.__setitem__((9, 0), 1 << 40)), ("last", lambda x: x.__setitem__((N - 1, 4), -1))):
    x = v.clone()
    mut(x)
    print("negative", name, "torch", torch_path([x]) is None, "new_bad", kernels.lookup_mults([x], kmap, trows)[1])
print(f"torch {bench(lambda: torch_path([v])):.2f} ms  new {bench(lambda: kernels.lookup_mults([v], kmap, trows)):.2f} ms")
