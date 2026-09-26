import subprocess, time
from pathlib import Path
from verity_flock import ir_lower as IL, ir_frame as IF
from verity_numerical.bench import lowerings, templates as TM
from verity_numerical.bench.input_sets import InputSet
REG = lowerings.registry("C-Flock")
m = REG.module("rmsnorm-triton")
art = "art:a5c7bd858c376c9eeefa4bceecbc817bc6a44e868d64f10d1cc2f5c8f2a70125"
p = Path(subprocess.run(["research", "data", "fetch", art], capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1])
s = InputSet.open(p); sub = s.subcircuit
t0 = time.time()
low = IL.lowering(m.definition(sub), f"{m.UNIT}/n128/eps1e-06", IL.reduction_cut(32))
fin, want = IL.flat_ports(s, sub.inputs, 0, s.n), IL.flat_ports(s, sub.outputs, 0, s.n)
cuts = IL.cut_words(low, fin)
got, cut_out, ok = low.evaluate(fin, cuts)
bad = ((got != want).any(axis=1) | (cut_out != cuts).any(axis=1))
print(sub.id, "pin", low.sha256, "units", low.units.n, "useful", low.layout.useful, "mismatched", int(bad.sum()), "of", s.n,
      "all_sat", ok == (1 << (s.n * low.units.n)) - 1, f"{time.time()-t0:.1f}s")
g = m.lowering(TM.subcircuit("rmsnorm-triton", N=2048, EPS=1e-05))
print("rows equal to the granted N2048 unit:", low.text.splitlines()[1:] == g.text.splitlines()[1:], "header", low.text.splitlines()[0][:100])
pl = IF.plan(low, sub)
print("plan", dict(G=pl.G, nb=pl.nb, chunk_nb=pl.chunk_nb, unit_log=pl.unit_log, units_per_block=pl.units_per_block, k_log=pl.k_log, comps=len(pl.comps), blocks_per_instance=pl.blocks(1)))
