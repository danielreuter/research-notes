import importlib.util, os, pickle, sys, time
from pathlib import Path
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
ROOT = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("pearl_c_twin", ROOT / "benchmarks/pouw/pearl_c/twin.py")
W = sys.modules["pearl_c_twin"] = importlib.util.module_from_spec(spec); spec.loader.exec_module(W)
from verity_pouw.schemes.pearl_c_device import DEVICES
k = int(sys.argv[2])
shape = W.Shape("p", 64, 128, k)
sd = {"seed_a": os.urandom(32), "seed_b": os.urandom(32), "salt": os.urandom(32), "root_b": os.urandom(32)}
job = W.job(shape, DEVICES["sm120"], sd)
print("job pickle MB", len(pickle.dumps(job)) / 1e6, sorted(DEVICES))
rng = np.random.default_rng(1)
a = rng.standard_normal((64, k)).astype(np.float32).view(np.uint32); b = rng.standard_normal((64, k)).astype(np.float32).view(np.uint32)
t0 = time.perf_counter(); ref = W.tile(job, 0, 64, a, b); t1 = time.perf_counter()
print("tile pickle MB", len(pickle.dumps(ref)) / 1e6, f"inline {t1-t0:.2f}s")
with ProcessPoolExecutor(2, mp_context=mp.get_context("fork")) as p:
    t0 = time.perf_counter(); got = p.submit(W.tile, job, 0, 64, a, b).result(); t1 = time.perf_counter()
print(f"pool {t1-t0:.2f}s", all(getattr(ref, f) == getattr(got, f) if isinstance(getattr(ref, f), (bytes, int, list)) else np.array_equal(getattr(ref, f), getattr(got, f)) for f in ("r0", "c0", "c", "u", "leaf", "tickets", "y_adopt", "row_leaf")))
