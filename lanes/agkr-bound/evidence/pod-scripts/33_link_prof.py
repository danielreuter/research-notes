"""agkr-bound: where the prover's 0.72 s of link time goes (gpu/link.py on the BF16 4096-VU layout, synthetic bits and
operands of the real shapes): points + eq table, the stand-in y (z bits + plane sums), sigma (plane sums of b), the
term of a.  python 33_link_prof.py [REPS]   (cwd backends/gkr)"""
import sys
import time

import numpy as np
import torch

sys.path.insert(0, ".")
from gpu import link as LK                     # noqa: E402
from gpu.field import P                        # noqa: E402
from gpu.transcript import Transcript          # noqa: E402

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
dev = torch.device("cuda")
lay = LK.Layout(vus=4096, steps=96, K=1536, k=16, bits=16, col0=264, ncols=776)
rng = np.random.default_rng(1)
x = rng.integers(0, 1 << 16, (lay.vus, lay.K), dtype=np.uint16)
w = rng.integers(0, 1 << 16, (lay.vus, lay.K), dtype=np.uint16)
link = LK.Link(lay, b"\x01" * 32, x, w)
b = torch.randint(0, 2, (lay.n_cells,), dtype=torch.int32, device=dev)
acc_a = torch.zeros((lay.vus * lay.steps * lay.ncols, 6), dtype=torch.int32, device=dev)


class Acc:
    a = acc_a
    b = (0,) * 6


def t(f):
    torch.cuda.synchronize(dev)
    t0 = time.perf_counter()
    r = f()
    torch.cuda.synchronize(dev)
    return r, time.perf_counter() - t0


for rep in range(REPS + 1):
    tr = Transcript(b"prof")
    pts, t_pts = t(lambda: LK.points(tr, link))
    T, t_eq = t(lambda: LK.eq_table(pts, dev))
    z, t_z = t(lambda: LK.z_bits(link, dev))
    sy, t_y = t(lambda: LK.plane_sums(T, lay, z, True))
    del z
    sb, t_s = t(lambda: LK.plane_sums(T, lay, b, False))
    claim = LK.Claim(T, (3, 1, 4, 1, 5, 9), sb)
    _, t_add = t(lambda: LK.add(Acc, claim, lay, 0))
    tot = t_pts + t_eq + t_z + t_y + t_s + t_add
    print(f"rep {rep - 1}: points {t_pts:.4f} eq_table {t_eq:.4f} z_bits {t_z:.4f} y_sums {t_y:.4f} sigma_sums {t_s:.4f} "
          f"add {t_add:.4f} total {tot:.4f} s; peak {torch.cuda.max_memory_allocated(dev) / 2**30:.1f} GiB", flush=True)
    del T, claim
