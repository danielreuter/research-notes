"""agkr-nvf4: gpu.kernels.eq_rows_dot vs field.mm_mod (bit-exact) and timing.  PYTHONPATH = <tree>/backends/gkr."""
import time

import torch

from gpu import field, kernels

P = field.P
dev = torch.device("cuda")
g = torch.Generator(device=dev).manual_seed(7)
ok = True
for n_rows, n_in, dt in [(131072, 1024, torch.int32), (131072, 512, torch.int64), (4096, 4, torch.int64), (5, 3, torch.int32),
                         (4096, 8, torch.int32), (98304, 1024, torch.int32), (37, 129, torch.int64)]:
    rows = torch.randint(0, P, (n_rows, n_in), device=dev, generator=g, dtype=torch.int64)
    rows[: min(8, n_rows)] = P - 1
    rows = rows.to(dt)
    e = torch.randint(0, P, (n_rows, 6), device=dev, generator=g, dtype=torch.int64)
    e[: min(8, n_rows)] = P - 1
    ref = field.mm_mod(e.T, rows.to(torch.int64)).T.contiguous()
    got = kernels.eq_rows_dot(e, rows)
    same = bool(torch.equal(ref, got))
    ok &= same
    torch.cuda.synchronize()
    ts = []
    for f in (lambda: field.mm_mod(e.T, rows.to(torch.int64)).T.contiguous(), lambda: kernels.eq_rows_dot(e, rows)):
        f()
        torch.cuda.synchronize()
        t = time.perf_counter()
        for _ in range(3):
            f()
        torch.cuda.synchronize()
        ts.append((time.perf_counter() - t) / 3)
    print(f"{n_rows}x{n_in} {dt}: equal={same} mm_mod {ts[0]*1e3:.2f} ms  eq_rows_dot {ts[1]*1e3:.3f} ms", flush=True)
print("ALL EQUAL" if ok else "MISMATCH")
