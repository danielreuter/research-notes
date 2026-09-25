"""verify-night-2: self-test of 06-core-roots.py's +blake3 path before the BLAKE3 cell arrives: the core-only roots of
fp8-ada+blake3 (my tree's instance set) against the backend's own committer (hashauth.build_trees, leaf blake3), same bindings.
    python 15-blake3-selftest.py     (run from the run dir's inputs/, beside 06-core-roots.py)
"""
import importlib.util
import sys
import time
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location("core_roots", Path(__file__).with_name("06-core-roots.py"))
cr = importlib.util.module_from_spec(spec)
sys.modules["core_roots"] = cr
spec.loader.exec_module(cr)

from backends.direct.ligero import hashauth, relchain  # noqa: E402
from backends.direct.ligero.leaf import registry  # noqa: E402
from backends.direct.ligero.relations import RELATIONS  # noqa: E402

t0 = time.time()
info, core = cr.core_trees("fp8-ada+blake3")
t1 = time.time()
rel = RELATIONS["fp8-ada"]
data = relchain.instances(rel, cr.N, procs=cr.PROCS)
leaf = registry.get("blake3")
bindings = {n: bytes.fromhex(core[n]["binding"]) for n in ("a", "b", "y")}
trees, _ = hashauth.build_trees(x_rows=np.asarray([v[0] for v in data], dtype=np.int64), w_cols=np.asarray([v[1] for v in data], dtype=np.int64),
                                y_words=np.asarray([rel.y_public(int(v[3])) for v in data], dtype=np.int64), word_bits=info["word_bits"],
                                y_bits=rel.y_bits, bindings=bindings, leaf=leaf)
t2 = time.time()
print(info)
ok = True
for n in ("a", "b", "y"):
    b = trees[n].ref.root.hex()
    print(n, "core", core[n]["root"][:16], "backend", b[:16], "MATCH" if b == core[n]["root"] else "DIFFER")
    ok &= b == core[n]["root"]
print(f"core {t1 - t0:.1f}s backend {t2 - t1:.1f}s -> {'OK' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
