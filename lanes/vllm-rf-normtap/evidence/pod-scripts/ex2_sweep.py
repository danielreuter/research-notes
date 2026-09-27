"""ex2_sweep.py FIX MAIN LIB_FIX LIB_MAIN OUT: every f32 word (2^32) through MufuEx2Ftz's compiled rule of the fix and of main
(`mufu_ex2_words` of each tree's libfa2_model.so) and through the fix's numpy twin (`derived_rows.mufu_ex2_ftz`), in 256 chunks of
2^24 words.  Writes OUT/sweep.json: twin mismatches (must be 0), words the fix answers other than 1.0 at biased exponents 1..103
(must be 0), main-vs-fix differences by (sign, biased exponent) with examples, and the per-chunk sha256 of the fix's outputs (u32 LE),
which the Rust sweeps (SP1 `mufu_ex2_tab`, flock `ir_tail.rs` `mufu_ex2`) are compared with."""
import ctypes
import hashlib
import json
import sys
import time
from multiprocessing import Pool

import numpy as np

FIX, MAIN, LIB_FIX, LIB_MAIN, OUT = sys.argv[1:6]
sys.path[:0] = [f"{FIX}/integrations/vllm", f"{FIX}/packages/verity/src"]
from verity_vllm.program.kernels import derived_rows as D  # noqa: E402
from verity_vllm.program.kernels import fa2_relation  # noqa: E402

PER, CHUNKS = 1 << 24, 256
T = np.ascontiguousarray(fa2_relation.tables().ex2, dtype=np.uint32)
LIBS = {}


def lib(path):
    if path not in LIBS:
        L = ctypes.CDLL(path)
        L.mufu_ex2_words.restype = None
        L.mufu_ex2_words.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long, ctypes.c_void_p]
        LIBS[path] = L
    return LIBS[path]


def words(path, x):
    y = np.empty_like(x)
    lib(path).mufu_ex2_words(x.ctypes.data, y.ctypes.data, x.size, T.ctypes.data)
    return y


def chunk(k):
    x = np.arange(k * PER, (k + 1) * PER, dtype=np.uint64).astype(np.uint32)
    fix, main = words(LIB_FIX, x), words(LIB_MAIN, x)
    twin = D.mufu_ex2_ftz(x, T)
    e = (x >> 23) & 0xFF
    tiny = (e >= 1) & (e <= 103)
    d = np.flatnonzero(fix != main)
    hist = {}
    if d.size:
        key = (x[d] >> 31).astype(np.int64) * 256 + e[d].astype(np.int64)
        u, c = np.unique(key, return_counts=True)
        hist = {f"{'-' if kk >= 256 else '+'}e{kk % 256}": int(cc) for kk, cc in zip(u, c)}
    ex = [[f"{int(x[i]):#010x}", f"{int(main[i]):#010x}", f"{int(fix[i]):#010x}"] for i in d[:: max(1, d.size // 3)][:3]]
    return {"k": k, "sha256": hashlib.sha256(fix.astype("<u4").tobytes()).hexdigest(),
            "twin_mismatch": int(np.count_nonzero(twin != fix)), "tiny_not_one": int(np.count_nonzero(fix[tiny] != 0x3F800000)),
            "tiny_words": int(tiny.sum()), "main_diff": int(d.size), "hist": hist, "examples": ex}


if __name__ == "__main__":
    t0 = time.time()
    lib(LIB_FIX), lib(LIB_MAIN)
    with Pool(6) as p:
        rs = sorted(p.map(chunk, range(CHUNKS)), key=lambda r: r["k"])
    hist = {}
    for r in rs:
        for kk, c in r["hist"].items():
            hist[kk] = hist.get(kk, 0) + c
    changed_e = sorted({int(kk[2:]) for kk in hist})
    res = {"inputs": CHUNKS * PER, "table_sha256": hashlib.sha256(T.astype("<u4").tobytes()).hexdigest(),
           "twin_mismatch": sum(r["twin_mismatch"] for r in rs), "tiny_words": sum(r["tiny_words"] for r in rs),
           "tiny_not_one": sum(r["tiny_not_one"] for r in rs), "main_vs_fix_differ": sum(r["main_diff"] for r in rs),
           "main_vs_fix_by_sign_exponent": dict(sorted(hist.items(), key=lambda kv: (kv[0][0], int(kv[0][2:])))),
           "changed_biased_exponents": [min(changed_e), max(changed_e)] if changed_e else [],
           "examples_x_main_fix": [e for r in rs for e in r["examples"]][:12],
           "chunk_sha256": [r["sha256"] for r in rs], "seconds": round(time.time() - t0, 1)}
    json.dump(res, open(f"{OUT}/sweep.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "chunk_sha256"}, indent=1))
