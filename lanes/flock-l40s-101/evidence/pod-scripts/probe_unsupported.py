import time
from verity_flock import ir_lower as IL
from verity_numerical.bench import lowerings, templates as TM
REG = lowerings.registry("C-Flock")
for tpl, p, widths in (("rmsnorm-triton", {"N": 128, "EPS": 1e-06}, (32, 64, 128)),
                       ("rmsnorm-triton", {"N": 2560, "EPS": 1e-06}, (256, 128)),
                       ("rmsnorm-fused-cuda", {"N": 2560, "EPS": 1e-06}, (160, 192, 128))):
    m = REG.module(tpl); sub = TM.subcircuit(tpl, **p)
    print(sub.id, "supports:", REG.supports(sub, "frame-v3/blake3-keyed"))
    for w in widths:
        t0 = time.time()
        try:
            low = IL.lowering(m.definition(sub), f"{m.UNIT}/n{p['N']}/eps{p['EPS']:g}", IL.reduction_cut(w))
            print("   width", w, "-> units", low.units.n, "rows", low.text.count("\n"), "sha", low.sha256[:8], f"{time.time()-t0:.1f}s")
        except Exception as e:
            print("   width", w, "->", type(e).__name__, str(e)[:200], f"{time.time()-t0:.1f}s")
