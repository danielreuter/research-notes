import cProfile
import importlib.util
import os
import pstats
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("pearl_c_twin", ROOT / "benchmarks/pouw/pearl_c/twin.py")
W = sys.modules["pearl_c_twin"] = importlib.util.module_from_spec(spec)
spec.loader.exec_module(W)
from verity_pouw.schemes.pearl_c_device import DEVICES  # noqa: E402

m, n, k = (int(x) for x in sys.argv[2:5])
shape = W.Shape("p", m, n, k)
sd = {"seed_a": os.urandom(32), "seed_b": os.urandom(32), "salt": os.urandom(32), "root_b": os.urandom(32)}
t0 = time.perf_counter()
job = W.job(shape, DEVICES["sm120"], sd)
t1 = time.perf_counter()
rng = np.random.default_rng(1)
a = (rng.standard_normal((64, k)).astype(np.float32)).view(np.uint32)
b = (rng.standard_normal((64, k)).astype(np.float32)).view(np.uint32)
pr = cProfile.Profile()
pr.enable()
t = W.tile(job, 0, 0, a, b)
pr.disable()
t2 = time.perf_counter()
print(f"job {t1 - t0:.2f} s, tile {t2 - t1:.2f} s")
pstats.Stats(pr).sort_stats("cumulative").print_stats(25)
