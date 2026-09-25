"""Evaluator and encoding equality of the Definitions the integration duplicates from core `verity.ml`.

Each side is imported alone in its own spawned worker processes: `core` imports `verity.ml.prims` / `verity.ml.gemm`,
`integ` imports `verity_vllm.program.registry.prims` / `.hopper` / `.b1`.  (Both at once raises today: the registry
refuses a second object under one id.)  Workers return sha256 digests of the output words per chunk; the parent
compares them, and on a mismatch re-runs the chunk returning words to name the first differing input.

    Bf16ToF32_v1            all 2^16 words
    F32ToBf16Rn_v1          all 2^32 words (scalar evaluators, both sides) + core's registered numpy kernel
    F2fpBf16_v1             all 2^32 words (same)
    HopperBF16WgmmaDot16_v1 special-value grid + seeded random samples (core `sample_tc`, uniform words, narrow
                            exponents); scalar evaluators both sides, core numpy kernel, integration vectorised twin
    encodings               program_digest of DotBf16_v2 / GemmCoordinate_v2 / Gemm_v2 specialisations, primitive
                            encodings of the four duplicates, and Const<w>[0x..]_v1 encodings and values

usage: python equality.py OUT.json [--quick]
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import sys
import time
from array import array

import numpy as np

SEED = 20260925
CONV_CHUNK = 1 << 22

_SIDE = None
_D: dict = {}


def _init(side: str) -> None:
    global _SIDE, _D
    _SIDE = side
    if side == "core":
        from verity.ml import prims as C
        _D = {"Bf16ToF32": C.Bf16ToF32, "F32ToBf16Rn": C.F32ToBf16Rn, "F2fpBf16": C.F2fpBf16,
              "HopperBF16WgmmaDot16": C.HopperBF16WgmmaDot16}
        assert not any(m.startswith("verity_vllm") for m in sys.modules), "core side imported verity_vllm"
    else:
        from verity_vllm.program.registry import hopper as H
        from verity_vllm.program.registry import prims as P
        _D = {"Bf16ToF32": P.Bf16ToF32, "F32ToBf16Rn": P.F32ToBf16Rn, "F2fpBf16": P.F2fpBf16,
              "HopperBF16WgmmaDot16": H.HopperBF16WgmmaDot16}
        assert "verity.ml.prims" not in sys.modules and "verity.ml.gemm" not in sys.modules, "integ side imported core prims"


def _whoami(_=None) -> dict:
    return {"side": _SIDE, "pid": os.getpid(),
            "defs": {k: {"id": d.id, "file": d.evaluate.__code__.co_filename, "line": d.evaluate.__code__.co_firstlineno}
                     for k, d in _D.items()}}


def _conv(task):
    name, start, n, words = task
    f = _D[name].evaluate
    out = array("H" if _D[name].ret.w == 16 else "I", map(f, range(start, start + n)))
    assert out.itemsize == (2 if _D[name].ret.w == 16 else 4)
    res = {"name": name, "start": start, "scalar": hashlib.sha256(out.tobytes()).hexdigest()}
    if words:
        res["words"] = out.tobytes()
    if _SIDE == "core":
        from verity.ml import kernels as K
        batch = {"Bf16ToF32": K.bf16_to_f32_batch, "F32ToBf16Rn": K.f32_to_bf16_rn_batch, "F2fpBf16": K.f2fp_bf16_batch}[name]
        a = np.arange(start, start + n, dtype=np.uint64).astype(np.uint32 if name != "Bf16ToF32" else np.uint16)
        k = batch(a)[0].astype(np.uint16 if _D[name].ret.w == 16 else np.uint32)
        res["kernel"] = hashlib.sha256(k.tobytes()).hexdigest()
    return res


def _dot(task):
    cid, acc, a, b = task
    f = _D["HopperBF16WgmmaDot16"].evaluate
    out = np.fromiter((f(int(acc[i]), *a[i].tolist(), *b[i].tolist()) for i in range(len(acc))), dtype=np.uint32, count=len(acc))
    res = {"cid": cid, "scalar": out}
    if _SIDE == "integ":
        from verity_vllm.program.registry.derived_rows import tc_dot16_hopper
        w, nonfin = tc_dot16_hopper(acc.astype(np.uint32), a.astype(np.uint16), b.astype(np.uint16))
        res["twin"], res["twin_nonfinite"] = np.asarray(w, dtype=np.uint32), np.asarray(nonfin, dtype=bool)
    return res


def _encodings(_=None) -> dict:
    from verity.ir.codec import _encode_definition, canonical_json, encode_program, program_digest
    from verity.ir.defs import PrimitiveDefinition, bind
    from verity.ir.program import Program
    from verity.ir.types import Array, Value

    F32, A16 = Value(32), Array(16, Value(16))
    if _SIDE == "core":
        from verity.ml import gemm as G
        from verity.ml import prims as C
        comps = {"DotBf16_v2": G.DotBf16, "GemmCoordinate_v2": G.GemmCoordinate, "Gemm_v2": G.Gemm}
        dots = {"HopperBF16WgmmaDot16_v1": C.HopperBF16WgmmaDot16,
                "AmpereBF16TcDot16_v1": PrimitiveDefinition("AmpereBF16TcDot16", 1, (("acc", F32), ("a", A16), ("b", A16)), F32,
                                                            lambda *x: 0, register=False)}
        const = C.const
    else:
        from verity_vllm.program.registry import b1
        comps = {"DotBf16_v2": b1.DotBf16V2, "GemmCoordinate_v2": b1.GemmCoordinateV2, "Gemm_v2": b1.GemmV2}
        from verity_vllm.program.registry import prims as P
        dots = {"HopperBF16WgmmaDot16_v1": _D["HopperBF16WgmmaDot16"], "AmpereBF16TcDot16_v1": P.AmpereBF16TcDot16}
        const = b1.const
    assert all(d.id == k for k, d in dots.items())
    out: dict = {"programs": {}, "prims": {}, "consts": {}}
    for dname, dot in dots.items():
        for K in (16, 64, 896, 1536):
            for cname, c in comps.items():
                for N in ((1, 3) if cname == "Gemm_v2" else (None,)):
                    kw = {"K": K, "DOT": dot} | ({"N": N} if N else {})
                    prog = Program(bind(c, **kw))
                    desc = encode_program(prog)
                    key = f"{cname}{{K={K}{',N=' + str(N) if N else ''},DOT={dname}}}"
                    out["programs"][key] = {"digest": program_digest(prog),
                                            "json_sha": hashlib.sha256(canonical_json(desc)).hexdigest(), "gates": prog.gates}
    for k, d in _D.items():
        out["prims"][k] = json.loads(canonical_json(_encode_definition(d)))
    rng = np.random.default_rng(SEED)
    cs = [(32, 0), (16, 0), (32, 0xFF800000), (32, 0x3F800000), (1, 0), (1, 1), (8, 0x7F)]
    cs += [(32, int(x)) for x in rng.integers(0, 1 << 32, size=8)] + [(16, int(x)) for x in rng.integers(0, 1 << 16, size=8)]
    for w, bits in cs:
        p = const(w, bits)
        out["consts"][p.id] = {"enc": json.loads(canonical_json(_encode_definition(p))), "value": p.evaluate(),
                               "family": getattr(p, "family", None), "conformance": p.conformance, "doc": p.doc}
    return out


# ---- inputs for the k16 step ----------------------------------------------------------------------------------------------

ACC_SP = [0x00000000, 0x80000000, 0x7F800000, 0xFF800000, 0x7FC00000, 0xFFC00000, 0x7F800001, 0xFFFFFFFF, 0x7F7FFFFF,
          0xFF7FFFFF, 0x00000001, 0x807FFFFF, 0x00800000, 0x3F800000, 0xBF800000, 0x4B800000]
BF_SP = [0x0000, 0x8000, 0x7F80, 0xFF80, 0x7FC0, 0x7F81, 0xFFFF, 0x7F7F, 0xFF7F, 0x0001, 0x807F, 0x0080, 0x3F80, 0xBF80]


def _dot_inputs(quick: bool):
    from verity.ir.types import Array, Value
    from verity.ml.kernels import sample_tc

    rng = np.random.default_rng(SEED)
    parts = {}
    acc, a, b = [], [], []
    for x in ACC_SP:
        for p in (0, 5, 15):
            for sa in BF_SP:
                for sb in BF_SP:
                    for fill in (0, 1):
                        av = rng.integers(0x3000, 0x4F00, size=16) * fill
                        bv = rng.integers(0x3000, 0x4F00, size=16) * fill
                        av[p], bv[p] = sa, sb
                        acc.append(x), a.append(av), b.append(bv)
    parts["special_grid"] = (np.asarray(acc, np.uint32), np.asarray(a, np.uint16), np.asarray(b, np.uint16))
    n = 20_000 if quick else 400_000
    sp = np.asarray(BF_SP, np.uint16)
    a = np.where(rng.random((n, 16)) < 0.3, sp[rng.integers(0, len(sp), (n, 16))], rng.integers(0, 1 << 16, (n, 16))).astype(np.uint16)
    b = np.where(rng.random((n, 16)) < 0.3, sp[rng.integers(0, len(sp), (n, 16))], rng.integers(0, 1 << 16, (n, 16))).astype(np.uint16)
    acc = np.where(rng.random(n) < 0.5, np.asarray(ACC_SP, np.uint32)[rng.integers(0, len(ACC_SP), n)],
                   rng.integers(0, 1 << 32, n)).astype(np.uint32)
    parts["dense_specials"] = (acc, a, b)
    n = 50_000 if quick else 5_000_000
    params = [Value(32), Array(16, Value(16)), Array(16, Value(16))]
    s = sample_tc(rng, n, params)
    parts["sample_tc"] = (s[0].astype(np.uint32), s[1].astype(np.uint16), s[2].astype(np.uint16))
    n = 20_000 if quick else 1_000_000
    parts["uniform_words"] = (rng.integers(0, 1 << 32, n).astype(np.uint32), rng.integers(0, 1 << 16, (n, 16)).astype(np.uint16),
                              rng.integers(0, 1 << 16, (n, 16)).astype(np.uint16))
    n = 20_000 if quick else 1_000_000
    e = rng.integers(1, 254, n)[:, None]
    mk = lambda: ((rng.integers(0, 2, (n, 16)) << 15) | (np.clip(e + rng.integers(-2, 3, (n, 16)), 1, 254) << 7)  # noqa: E731
                  | rng.integers(0, 128, (n, 16))).astype(np.uint16)
    ea = np.clip(2 * e[:, 0] - 127 + rng.integers(-3, 4, n), 0, 254)
    acc = ((rng.integers(0, 2, n) << 31) | (ea << 23) | rng.integers(0, 1 << 23, n)).astype(np.uint32)
    parts["narrow_exponent"] = (acc, mk(), mk())
    return parts


def main() -> int:
    out_path = sys.argv[1]
    quick = "--quick" in sys.argv
    ctx = mp.get_context("spawn")
    nproc = max(2, (os.cpu_count() or 2) // 2)
    t0 = time.time()
    res: dict = {"seed": SEED, "quick": quick, "nproc_per_side": nproc, "conversions": {}, "dot": {}, "encodings": {}}
    with ctx.Pool(nproc, initializer=_init, initargs=("core",)) as pc, ctx.Pool(nproc, initializer=_init, initargs=("integ",)) as pi:
        res["whoami"] = {"core": pc.apply(_whoami), "integ": pi.apply(_whoami)}
        print(json.dumps(res["whoami"], indent=1), flush=True)

        enc = {"core": pc.apply(_encodings), "integ": pi.apply(_encodings)}
        for sect in ("programs", "prims", "consts"):
            c, i = enc["core"][sect], enc["integ"][sect]
            diff = sorted(k for k in set(c) | set(i) if c.get(k) != i.get(k))
            res["encodings"][sect] = {"n": len(c), "keys_equal": sorted(c) == sorted(i), "differ": diff,
                                      "core": c if diff else None, "integ": i if diff else None}
            if sect == "programs":
                res["encodings"][sect]["digests"] = {k: v["digest"] for k, v in c.items()}
            print(f"encodings {sect}: n={len(c)} differ={diff}", flush=True)

        for name, total in (("Bf16ToF32", 1 << 16), ("F32ToBf16Rn", 1 << 32), ("F2fpBf16", 1 << 32)):
            if quick and total > 1 << 16:
                total = 1 << 24
            chunk = min(CONV_CHUNK, total)
            tasks = [(name, s, min(chunk, total - s), False) for s in range(0, total, chunk)]
            t = time.time()
            rc = {r["start"]: r for r in pc.imap_unordered(_conv, tasks, chunksize=1)}
            ri = {r["start"]: r for r in pi.imap_unordered(_conv, tasks, chunksize=1)}
            bad_scalar = sorted(s for s in rc if rc[s]["scalar"] != ri[s]["scalar"])
            bad_kernel = sorted(s for s in rc if rc[s]["kernel"] != rc[s]["scalar"])
            first = None
            for s in bad_scalar[:1]:
                n = min(chunk, total - s)
                wc = pc.apply(_conv, ((name, s, n, True),))["words"]
                wi = pi.apply(_conv, ((name, s, n, True),))["words"]
                dt = np.uint16 if len(wc) == 2 * n else np.uint32
                xc, xi = np.frombuffer(wc, dt), np.frombuffer(wi, dt)
                j = int(np.flatnonzero(xc != xi)[0])
                first = {"input": hex(s + j), "core": hex(int(xc[j])), "integ": hex(int(xi[j])), "n_differ_in_chunk": int((xc != xi).sum())}
            roll = hashlib.sha256("".join(rc[s]["scalar"] for s in sorted(rc)).encode()).hexdigest()
            res["conversions"][name] = {"inputs": total, "chunks": len(tasks), "chunk": chunk, "scalar_chunks_differ": len(bad_scalar),
                                        "kernel_chunks_differ": len(bad_kernel), "first_scalar_difference": first,
                                        "rollup_sha256_core": roll,
                                        "rollup_sha256_integ": hashlib.sha256("".join(ri[s]["scalar"] for s in sorted(ri)).encode()).hexdigest(),
                                        "seconds": round(time.time() - t, 1)}
            print(f"{name}: {res['conversions'][name]}", flush=True)
            json.dump(res, open(out_path, "w"), indent=1)

        from verity.ml.kernels import group_sum_total_batch
        from verity.ml.tc.total import HOPPER_BF16_WGMMA_K16

        for part, (acc, a, b) in _dot_inputs(quick).items():
            t = time.time()
            m = 20_000
            tasks = [(i, acc[s:s + m], a[s:s + m], b[s:s + m]) for i, s in enumerate(range(0, len(acc), m))]
            rc = {r["cid"]: r for r in pc.imap_unordered(_dot, tasks, chunksize=1)}
            ri = {r["cid"]: r for r in pi.imap_unordered(_dot, tasks, chunksize=1)}
            sc = np.concatenate([rc[i]["scalar"] for i in range(len(tasks))])
            si = np.concatenate([ri[i]["scalar"] for i in range(len(tasks))])
            tw = np.concatenate([ri[i]["twin"] for i in range(len(tasks))])
            nf = np.concatenate([ri[i]["twin_nonfinite"] for i in range(len(tasks))])
            kern = group_sum_total_batch(HOPPER_BF16_WGMMA_K16, acc, a, b)[0].astype(np.uint32)
            d_si = np.flatnonzero(sc != si)
            d_k = np.flatnonzero(sc != kern)
            d_tw = np.flatnonzero((sc != tw) & ~nf)
            ex = lambda d: None if not len(d) else {"i": int(d[0]), "acc": hex(int(acc[d[0]])), "a": [hex(int(x)) for x in a[d[0]]],  # noqa: E731
                                                    "b": [hex(int(x)) for x in b[d[0]]], "core": hex(int(sc[d[0]])),
                                                    "integ": hex(int(si[d[0]])), "kernel": hex(int(kern[d[0]])), "twin": hex(int(tw[d[0]]))}
            nan_out = int(((sc & 0x7F800000) == 0x7F800000).sum())
            res["dot"][part] = {"cases": int(len(acc)), "core_vs_integ_differ": int(len(d_si)), "core_vs_core_kernel_differ": int(len(d_k)),
                                "core_vs_integ_twin_differ_where_twin_finite": int(len(d_tw)), "twin_nonfinite": int(nf.sum()),
                                "nonfinite_outputs": nan_out, "zero_outputs": int((sc == 0).sum()),
                                "sha256_core": hashlib.sha256(sc.tobytes()).hexdigest(),
                                "sha256_integ": hashlib.sha256(si.tobytes()).hexdigest(),
                                "first_core_vs_integ": ex(d_si), "first_core_vs_kernel": ex(d_k), "first_core_vs_twin": ex(d_tw),
                                "seconds": round(time.time() - t, 1)}
            print(f"dot {part}: " + json.dumps({k: v for k, v in res['dot'][part].items() if not k.startswith('first')}), flush=True)
            json.dump(res, open(out_path, "w"), indent=1)

    ok = (all(v["scalar_chunks_differ"] == 0 and v["kernel_chunks_differ"] == 0 for v in res["conversions"].values())
          and all(v["core_vs_integ_differ"] == 0 and v["core_vs_core_kernel_differ"] == 0 for v in res["dot"].values())
          and all(not v["differ"] and v["keys_equal"] for v in res["encodings"].values()))
    res["all_equal"], res["seconds"] = ok, round(time.time() - t0, 1)
    json.dump(res, open(out_path, "w"), indent=1)
    print("ALL-EQUAL" if ok else "DIFFERENCES", res["seconds"], "s", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
