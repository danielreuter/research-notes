"""agkr-nvf4: NVF4 witness generator, eager vs torch.compile'd program (graphed both ways): same rows? replay time?
python 10_wcompile.py [VUS]   (cwd backends/gkr, dev tree on PYTHONPATH)"""
import sys
import time

import torch

import bench_result
from gpu.nvf4.circuit import statement
from gpu.nvf4.witness import GraphedNVF4Generator, NVF4Generator

VUS = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
dev = torch.device("cuda")
A8, B8, Y32, _, _ = bench_result.load_nvf4(0, VUS, 13)
gen = NVF4Generator(statement(), dev)
A, B, Y = (torch.from_numpy(x).to(dev) for x in (A8, B8, Y32))
A, B = A.long(), B.long()

for _ in range(2):
    r = gen.run(A, B, Y, sync=True)
print("eager split", {k: round(v * 1e3, 2) for k, v in r.seconds.items()}, flush=True)
ref_units, ref_epi, ref_bad = r.units.clone(), r.epilogue.clone(), r.bad.clone()


def time_graphed(g, label):
    for _ in range(3):
        g.run(A8, B8, Y32)
    torch.cuda.synchronize()
    ts = []
    for _ in range(5):
        t0 = time.perf_counter()
        rows = g.run(A8, B8, Y32)
        torch.cuda.synchronize()
        ts.append(time.perf_counter() - t0)
    same = bool(torch.equal(rows.units, ref_units) and torch.equal(rows.epilogue, ref_epi) and torch.equal(rows.bad, ref_bad))
    print(label, "replay ms", sorted(round(t * 1e3, 2) for t in ts), "same rows", same, flush=True)


time_graphed(GraphedNVF4Generator(gen, VUS), "graphed eager")

plain_program = gen._program
t0 = time.perf_counter()
gen._program = torch.compile(plain_program, dynamic=False)
r2 = gen.run(A, B, Y, sync=True)
print("compile+first s", round(time.perf_counter() - t0, 1), "same", bool(torch.equal(r2.units, ref_units)), flush=True)
r2 = gen.run(A, B, Y, sync=True)
print("compiled split", {k: round(v * 1e3, 2) for k, v in r2.seconds.items()}, flush=True)
time_graphed(GraphedNVF4Generator(gen, VUS), "graphed compiled-program")
