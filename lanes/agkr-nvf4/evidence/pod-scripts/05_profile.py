"""agkr-nvf4 profiler: bench_result.main with sync timers patched around the prover's phases.

python 05_profile.py STMT_DIR [bench_result args...]   (PYTHONPATH = <tree>/backends/gkr:<tree>)
Prints one JSON line per (rep, key) with the summed seconds of the LAST rep after the run."""
from __future__ import annotations

import collections
import functools
import json
import sys
import time

import torch

import bench_result
from gpu import circuit, gkr, gkr_packed, ligero, logup, logup_packed, prover

REC: list[dict] = []
cur = collections.defaultdict(float)
cnt = collections.Counter()


def timed(mod, name, key=None, desc=None):
    f = getattr(mod, name)

    @functools.wraps(f)
    def w(*a, **k):
        torch.cuda.synchronize()
        t = time.perf_counter()
        r = f(*a, **k)
        torch.cuda.synchronize()
        kk = key or name
        if desc:
            kk += ":" + desc(*a, **k)
        cur[kk] += time.perf_counter() - t
        cnt[kk] += 1
        return r
    setattr(mod, name, w)


def lay(layer, rows, b, *a, **k):
    return f"{layer.name} g{layer.g_n} s{layer.s_in} b{b}"


def shp(*a, **k):
    return "x".join("L" if not hasattr(t, "shape") else "(" + ",".join(map(str, t.shape)) + ")" for t in a[:2])


timed(gkr, "mm_mod", key="gkr.mm_mod", desc=shp)
timed(gkr, "eq_table", key="gkr.eq_table", desc=lambda p, *a, **k: f"n{len(p)}")
timed(gkr, "sumcheck_prod", key="gkr.sumcheck_prod", desc=shp)
timed(gkr, "ext_mul", key="gkr.ext_mul")
timed(circuit.Layer, "matrices", key="Layer.matrices")
timed(circuit.Layer, "eval_a_at", key="Layer.eval_a_at")
timed(gkr, "prove_layer", desc=lay)
timed(gkr, "_phase2")
_orig_phase1 = gkr_packed.phase1
_patched_kern: set = set()


def _phase1(kern, *a, **k):
    cls = type(kern)
    if cls not in _patched_kern:
        _patched_kern.add(cls)
        for n in ("packed_round", "ext_round", "fold_k", "fold_pair", "set_fold"):
            if hasattr(cls, n):
                timed(cls, n, key="p1." + n)
    return _orig_phase1(kern, *a, **k)


gkr_packed.phase1 = _phase1
timed(gkr_packed, "phase1")
timed(gkr_packed, "_layout", key="p1._layout")
timed(gkr_packed, "_inputs", key="p1._inputs")
timed(gkr_packed, "_EqSlices", key="p1._EqSlices")
timed(gkr_packed, "py_exts", key="p1.py_exts")
timed(gkr, "phase1_round")
timed(circuit.Layer, "eval_gates")
for n in ("eval_wires", "masked_wires", "pad_rows", "add_chain", "add_lookup_claim", "add_input_claim", "start_transcript",
          "seg_query_values", "eq_table"):
    if hasattr(prover, n):
        timed(prover, n)
for n in ("prove_range_table_graphed", "prove_ext_table_graphed", "prove_range_table", "prove_ext_table"):
    timed(logup_packed, n, key="logup." + n, desc=lambda *a, **k: f"n{[x for x in a if isinstance(x, int)][-1]}")
for n in ("build_leaves", "multiplicities", "table_rows"):
    timed(logup, n, key="logup." + n)
timed(ligero, "commit", key="ligero.commit")

_GX = getattr(logup_packed, "_FSGraphExtDev", None)
if _GX is not None:
    def _replay_fs(self, tr, out):
        def lap(key, t):
            torch.cuda.synchronize()
            cur[key] += time.perf_counter() - t
            return time.perf_counter()
        torch.cuda.synchronize()
        t = time.perf_counter()
        self.fs.load(tr)
        self.g_tree.replay()
        t = lap("lx.tree", t)
        for lv in range(self.n):
            for (_, _, g) in self.g_levels[lv]:
                g.replay()
            if lv in (9, 19, 22, 23):
                t = lap(f"lx.levels<={lv}", t)
        t = lap("lx.levels_rest", t)
        r = self._finish_fs(tr, out)
        lap("lx.finish", t)
        return r
    _GX._replay_fs = _replay_fs
    timed(_GX, "prove_fs_ext", key="lx.prove_fs_ext")
timed(ligero, "prove_open", key="ligero.prove_open")
from gpu import kernels as _k
timed(ligero, "open_w_qc_eval", key="wq.eval")
timed(ligero, "row_coeffs", key="wq.row_coeffs")
timed(ligero, "_mm", key="wq._mm", desc=shp)
timed(ligero, "ntt", key="wq.ntt", desc=shp)
timed(_k, "row_code_dot", key="wq.row_code_dot")
timed(ligero, "exts_to_bytes", key="wq.exts_to_bytes")
timed(ligero, "open_set", key="wq.open_set")

orig_prove = prover.prove


def prove(*a, **k):
    cur.clear()
    cnt.clear()
    torch.cuda.synchronize()
    t = time.perf_counter()
    r = orig_prove(*a, **k)
    torch.cuda.synchronize()
    cur["prove.total"] = time.perf_counter() - t
    REC.append({k2: (round(v, 5), cnt[k2]) for k2, v in sorted(cur.items())})
    return r


prover.prove = prove

if __name__ == "__main__":
    rc = bench_result.main(sys.argv[1:])
    for i, r in enumerate(REC):
        print(json.dumps({"profile_rep": i, **r}), flush=True)
    sys.exit(rc)
