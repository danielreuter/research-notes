#!/usr/bin/env bash
# agkr-table: gpu/v2/witness.GraphedGenerator (Generator.run captured as one CUDA graph) against the eager generator on
# the frozen vu-k1536 operands [0, 4096) and on a corrupted copy (every 7th VU gets out-of-domain operand bits, so the
# generator must flag it bad): identical units / epilogue / public / bad; capture time; min-of-5 timings of both.
set -uo pipefail
source /workspace/env.sh
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
$PY - <<'EOF'
import time
from pathlib import Path

import numpy as np
import torch

import bench_result as br
from gpu.v2.witness import Generator, GraphedGenerator, Ops

dev = torch.device("cuda")
x, w, y, _ = br.load_frozen(Path("/workspace/bench-instances/v1"), Path("/workspace/src/fixtures/bench-instances/v1/manifest.json"),
                            br.TIER, 0, 4096)
ops = Ops(str(dev))
gen = Generator(ops)
sync = lambda: torch.cuda.synchronize(dev)


def eager(x, w, y):
    sync()
    t = time.perf_counter()
    r = gen.run(ops.asarray(x), ops.asarray(w), ops.asarray(y))
    int(r.bad.sum())
    return r, time.perf_counter() - t


t = time.perf_counter()
gg = GraphedGenerator(gen, *x.shape)
print(f"capture {time.perf_counter() - t:.2f}s", flush=True)
ok = True
xb = np.array(x)
xb[::7, 5] = 0x7F81                     # a NaN pattern in the operand stream: rejected by T_OP / the chain
for tag, (xx, ww, yy) in (("frozen", (x, w, y)), ("corrupted", (xb, w, y))):
    ref, te = eager(xx, ww, yy)
    x16, w16, y16 = (np.ascontiguousarray(a).view(np.int16).copy() for a in (xx, ww, yy))
    tg = []
    for _ in range(5):
        sync()
        t = time.perf_counter()
        rows = gg.run(x16, w16, y16)
        nbad = int(rows.bad.sum())
        tg.append(time.perf_counter() - t)
    same = all(torch.equal(getattr(rows, f), getattr(ref, f)) for f in ("units", "epilogue", "public", "bad"))
    ok &= same
    print(f"{tag}: same={same} bad={nbad} (eager {int(ref.bad.sum())}) eager {te:.3f}s graphed min {min(tg):.4f}s max {max(tg):.4f}s", flush=True)
    del ref
print("OK" if ok else "MISMATCH", flush=True)
EOF
