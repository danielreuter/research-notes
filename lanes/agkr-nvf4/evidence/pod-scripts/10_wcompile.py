"""agkr-nvf4: NVF4 witness generator, eager vs VERITY_NVF4_COMPILE=1 (torch.compile'd chain step), graphed both ways:
same rows? replay time?   python 10_wcompile.py [VUS]   (cwd backends/gkr, dev tree on PYTHONPATH)"""
import os
import sys
import time

import torch

import bench_result
from gpu.nvf4.circuit import statement
from gpu.nvf4.witness import GraphedNVF4Generator, NVF4Generator

VUS = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
dev = torch.device("cuda")
A8, B8, Y32, _, _ = bench_result.load_nvf4(0, VUS, 13)
A, B, Y = (torch.from_numpy(x).to(dev) for x in (A8, B8, Y32))
A, B = A.long(), B.long()
st = statement()


def time_graphed(g, label, ref=None):
    for _ in range(3):
        g.run(A8, B8, Y32)
    torch.cuda.synchronize()
    ts = []
    for _ in range(5):
        t0 = time.perf_counter()
        rows = g.run(A8, B8, Y32)
        torch.cuda.synchronize()
        ts.append(time.perf_counter() - t0)
    same = None if ref is None else bool(all(torch.equal(x, y) for x, y in zip((rows.units, rows.epilogue, rows.bad), ref)))
    print(label, "replay ms", sorted(round(t * 1e3, 2) for t in ts), "same rows", same, flush=True)
    return rows


os.environ.pop("VERITY_NVF4_COMPILE", None)
gen = NVF4Generator(st, dev)
for _ in range(2):
    r = gen.run(A, B, Y, sync=True)
print("eager split", {k: round(v * 1e3, 2) for k, v in r.seconds.items()}, "bad", int(r.bad.sum()), flush=True)
ref = (r.units.clone(), r.epilogue.clone(), r.bad.clone())
time_graphed(GraphedNVF4Generator(gen, VUS), "graphed eager", ref)

os.environ["VERITY_NVF4_COMPILE"] = "1"
gen2 = NVF4Generator(st, dev)
t0 = time.perf_counter()
r2 = gen2.run(A, B, Y, sync=True)
print("compile+first s", round(time.perf_counter() - t0, 1), flush=True)
r2 = gen2.run(A, B, Y, sync=True)
print("compiled split", {k: round(v * 1e3, 2) for k, v in r2.seconds.items()}, flush=True)
time_graphed(GraphedNVF4Generator(gen2, VUS), "graphed compiled", ref)
