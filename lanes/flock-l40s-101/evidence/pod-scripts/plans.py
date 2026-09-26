from verity_flock import ir_frame as IF
from verity_numerical.bench import lowerings, templates as TM
REG = lowerings.registry("C-Flock")
for tpl, p in (("rope-head", {"D": 128}), ("rope-head", {"D": 64}), ("silu-mul", {"I": 9728}), ("silu-mul", {"I": 14336}), ("silu-mul", {"I": 8192}),
               ("rmsnorm-fused-cuda", {"N": 4096, "EPS": 1e-05}), ("rmsnorm-fused-cuda", {"N": 2048, "EPS": 1e-05}),
               ("rmsnorm-triton", {"N": 4096, "EPS": 1e-05}), ("rmsnorm-triton", {"N": 2048, "EPS": 1e-05})):
    m = REG.module(tpl); sub = TM.subcircuit(tpl, **p); low = m.frame_lowering(sub)
    try:
        pl = IF.plan(low, sub)
        print(sub.id, dict(G=pl.G, nb=pl.nb, chunk_nb=pl.chunk_nb, comp_slots=pl.comp_slots, unit_log=pl.unit_log, units_per_block=pl.units_per_block,
              k_log=pl.k_log, comps=len(pl.comps), chunks_per_comp=pl.chunks_per_comp, units_per_comp=pl.units_per_comp, blocks_per_instance=pl.blocks(1)))
    except Exception as e:
        print(sub.id, "PLAN FAILS:", str(e)[:300])
