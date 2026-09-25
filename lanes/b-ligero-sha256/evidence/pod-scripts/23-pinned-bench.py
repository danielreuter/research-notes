"""Host reads of a (M, t) int32 block after a device -> pinned DMA: numpy copy of the pinned view (what
openings_device.opened_from_pinned does), the same after a CPU touch, a pageable .cpu(), torch clone of the pinned view."""
import time

import numpy as np
import torch

M, t = int(89356 * 1.0), 256
dev = torch.device("cuda")
src = torch.randint(0, 2**30, (M, t), dtype=torch.int32, device=dev)
pin = torch.empty(M * t * 4, dtype=torch.uint8, pin_memory=True)
view = pin.view(torch.int32).view(M, t)


def tm(name, fn, reps=3):
    ts = []
    for _ in range(reps):
        view.copy_(src, non_blocking=True)
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t0)
    print(f"{name}: {min(ts) * 1e3:.1f} ms (reps {[round(x * 1e3, 1) for x in ts]})", flush=True)


tm("numpy copy after DMA", lambda: view.numpy().view(np.uint32).copy())
tm("np.array(copy=True)", lambda: np.array(view.numpy(), copy=True))
tm("torch clone of pinned", lambda: view.clone())
tm("torch empty+copy_ (pageable dst)", lambda: torch.empty((M, t), dtype=torch.int32).copy_(view))
tm("sum (read only)", lambda: view.numpy().sum(dtype=np.int64))
out = np.empty((M, t), dtype=np.uint32)
tm("np.copyto preallocated", lambda: np.copyto(out, view.numpy().view(np.uint32)))
t0 = time.perf_counter()
for _ in range(3):
    h = src.cpu()
torch.cuda.synchronize()
print(f"src.cpu() pageable: {(time.perf_counter() - t0) / 3 * 1e3:.1f} ms", flush=True)
view.numpy()[:] = 1
t0 = time.perf_counter()
x = view.numpy().copy()
print(f"numpy copy after CPU write (no DMA): {(time.perf_counter() - t0) * 1e3:.1f} ms", flush=True)
a = np.ones((M, t), dtype=np.int32)
for i in range(4):
    t0 = time.perf_counter()
    b = a.copy()
    print(f"plain numpy copy {i}: {(time.perf_counter() - t0) * 1e3:.1f} ms", flush=True)
    del b
for i in range(3):
    t0 = time.perf_counter()
    b = view.numpy().view(np.uint32).reshape(M, t).copy()
    print(f"opened_from_pinned-style copy {i}: {(time.perf_counter() - t0) * 1e3:.1f} ms", flush=True)
    del b
import subprocess  # noqa: E402
print(subprocess.run("grep -E 'MemTotal|MemFree|HugePages_Total|AnonHugePages' /proc/meminfo; cat /sys/kernel/mm/transparent_hugepage/enabled; "
                     "nvidia-smi -q | grep -iE 'confidential|CC mode|Persistence' | head", shell=True, capture_output=True, text=True).stdout)
