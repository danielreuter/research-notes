"""Step 3: old-vs-new evaluator equality of the primitives moved from the vLLM integration into core `verity.ml`.

old  = the base tree's integration evaluators (BASE/integrations/vllm + BASE/packages/verity/src, nothing from the head)
new  = the head tree's core evaluators (`verity.ml.prims`, `verity.ml.scalar`; no `verity_vllm` imported)

Each side runs in its own spawned pool; workers return sha256 digests of output words per chunk (and of the inputs,
for generated ones); on a mismatch the parent re-runs the chunk for words and names the first differing input.

    exhaustive 2^32   F32Sat, F32Fabs, F32Neg, F32BitsShl23, F32IsFinite (unary) and Bf16GtStrict (every (a, b) pair)
    structured        F32ToE4m3Sat: every sign x exponent x top-6 mantissa bits x 10 low-bit patterns + 8 M uniform
                      words; the body is also compared as source text
    pairs             F32Fmaxf, F32Fminf, F32Eq, I32Le, I32Eq, I32Add: the special-word cross product + seeded pair
                      chunks (y uniform / = x / sign-flipped / x +- 3 ulp / special / same exponent), both orders
    selects, bits     SelectF32/Bf16/I32 on c in 0..3 x seeded words; BitAnd/BitOr/BitNot on every input in 0..3
    k32 step          HopperE4m3QgmmaDot32: special grid, dense specials, core sample_tc, uniform bytes, accumulator
                      passthrough; old scalar vs new scalar vs core's registered kernel vs the old vectorised twin
    encodings         per moved id: primitive encoding, params, ret, conformance, doc (old vs new); and, with every
                      registry module imported on each side (base vs head): program_digest of every zero-static
                      composite and of curated specialisations, registry_version(), ref_vocab_digest(), every
                      Vocabulary.version(); plus the host NaN words of the numpy-backed F32 arithmetic (not moved)

usage: python equality3.py OUT.json [--quick]      (env C2_BASE: base tree root, default /workspace/base)
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import sys
import time
from array import array
from itertools import repeat

import numpy as np

SEED = 20260925
M32 = 0xFFFFFFFF
BASE = os.environ.get("C2_BASE", "/workspace/base")
HEAD = os.path.abspath(os.getcwd())
CHUNK = 1 << 22

SCALAR = ["F32Fabs", "F32Neg", "F32Fmaxf", "F32Fminf", "F32Sat", "F32BitsShl23", "F32IsFinite", "F32Eq", "Bf16GtStrict",
          "I32Le", "I32Eq", "I32Add", "BitAnd", "BitNot", "BitOr", "SelectF32", "SelectBf16", "SelectI32"]
FP8 = ["F32ToE4m3Sat", "HopperE4m3QgmmaDot32"]
MOVED = FP8 + SCALAR

_SIDE = None
_D: dict = {}


def _use_base() -> None:
    sys.path[:] = [p for p in sys.path if not os.path.abspath(p or ".").startswith(HEAD)]
    sys.path[:0] = [f"{BASE}/integrations/vllm", f"{BASE}/packages/verity/src"]


_INIT_ERR = None


def _init(side: str) -> None:
    """Pool initializer; an exception here would make the pool respawn workers forever, so it is recorded instead."""
    global _SIDE, _INIT_ERR
    _SIDE = side
    try:
        _init_side(side)
    except BaseException as e:  # noqa: BLE001
        import traceback
        _INIT_ERR = f"{type(e).__name__}: {e}\n{traceback.format_exc()[-3000:]}"


def _init_side(side: str) -> None:
    global _D
    if side in ("old", "oldall"):
        _use_base()
    import verity
    root = BASE if side in ("old", "oldall") else HEAD
    assert os.path.abspath(verity.__file__).startswith(root), (side, verity.__file__)
    if side == "old":
        from verity_vllm.program.registry import fp8 as F, moe as M, pad_prims as PP, prims as P, sampling as SM
        _D = {"F32ToE4m3Sat": F.F32ToE4m3Sat, "HopperE4m3QgmmaDot32": F.HopperE4m3QgmmaDot32, "F32Fabs": F.F32Fabs,
              "F32Fmaxf": F.F32Fmaxf, "F32Fminf": F.F32Fminf, "F32Sat": M.F32Sat, "F32Neg": M.F32Neg,
              "F32BitsShl23": M.F32BitsShl23, "F32IsFinite": M.F32IsFinite, "F32Eq": SM.F32Eq, "BitOr": SM.BitOr,
              "BitAnd": PP.BitAnd, "BitNot": PP.BitNot, "I32Le": P.I32Le, "I32Eq": P.I32Eq, "I32Add": P.I32Add,
              "SelectF32": P.SelectF32, "SelectBf16": P.SelectBf16, "SelectI32": P.SelectI32, "Bf16GtStrict": P.Bf16GtStrict}
        assert "verity.ml.scalar" not in sys.modules, "old side imported core scalar"
    elif side == "new":
        from verity.ml import prims as C, scalar as S
        _D = {"F32ToE4m3Sat": C.F32ToE4m3Sat, "HopperE4m3QgmmaDot32": C.HopperE4m3QgmmaDot32} | {n: getattr(S, n) for n in SCALAR}
        assert not any(m.startswith("verity_vllm") for m in sys.modules), "new side imported verity_vllm"
    if _D:
        assert sorted(_D) == sorted(MOVED) and all(d.id == f"{k}_v1" for k, d in _D.items())
        assert all(os.path.abspath(d.evaluate.__code__.co_filename).startswith(root) for d in _D.values())


def _whoami(_=None) -> dict:
    if _INIT_ERR:
        return {"side": _SIDE, "pid": os.getpid(), "init_error": _INIT_ERR}
    import verity
    return {"side": _SIDE, "pid": os.getpid(), "verity": verity.__file__, "modules_core_prims": "verity.ml.prims" in sys.modules,
            "defs": {k: {"id": d.id, "file": d.evaluate.__code__.co_filename, "line": d.evaluate.__code__.co_firstlineno}
                     for k, d in _D.items()}}


# ---- inputs -------------------------------------------------------------------------------------------------------------

F32_SP = [0x00000000, 0x80000000, 0x00000001, 0x80000001, 0x007FFFFF, 0x807FFFFF, 0x00800000, 0x80800000, 0x3F800000,
          0xBF800000, 0x3F7FFFFF, 0x3F800001, 0xBF7FFFFF, 0x7F7FFFFF, 0xFF7FFFFF, 0x7F800000, 0xFF800000, 0x7FC00000,
          0xFFC00000, 0x7F800001, 0xFF800001, 0x7FFFFFFF, 0xFFFFFFFF, 0x7FBFFFFF, 0x40000000, 0xC0000000, 0x43E00000,
          0x4B400001, 0x3F000000, 0x00400000]


def _f32_pairs(chunk: int, n: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng([SEED, 1, chunk])
    sp = np.asarray(F32_SP, np.uint64)
    x = rng.integers(0, 1 << 32, n, dtype=np.uint64)
    x = np.where(rng.random(n) < 0.1, sp[rng.integers(0, len(sp), n)], x)
    mode = rng.integers(0, 6, n)
    cand = [rng.integers(0, 1 << 32, n, dtype=np.uint64), x, x ^ 0x80000000,
            (x.astype(np.int64) + rng.integers(-3, 4, n)).astype(np.uint64) & M32, sp[rng.integers(0, len(sp), n)],
            (x & 0xFF800000) | rng.integers(0, 1 << 23, n, dtype=np.uint64)]
    y = np.choose(mode, cand)
    sw = rng.random(n) < 0.5
    return np.where(sw, y, x).astype(np.uint32), np.where(sw, x, y).astype(np.uint32)


def _cross() -> tuple[np.ndarray, np.ndarray]:
    sp = np.asarray(F32_SP, np.uint32)
    return np.repeat(sp, len(sp)), np.tile(sp, len(sp))


def _select_triples(chunk: int, n: int, width: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng([SEED, 2, chunk, width])
    hi = 1 << width
    return (rng.integers(0, 4, n).astype(np.uint32), rng.integers(0, hi, n, dtype=np.uint64).astype(np.uint32),
            rng.integers(0, hi, n, dtype=np.uint64).astype(np.uint32))


def _e4m3_words(quick: bool) -> np.ndarray:
    rng = np.random.default_rng([SEED, 3])
    s, e, top = np.meshgrid(np.arange(2, dtype=np.uint64), np.arange(256, dtype=np.uint64), np.arange(64, dtype=np.uint64),
                            indexing="ij")
    head = ((s << 31) | (e << 23) | (top << 17)).ravel()
    lows = [0, 1, 0xFFFF, 0x10000, 0x10001, 0x1FFFF] + [int(v) for v in rng.integers(0, 1 << 17, 4)]
    grid = (head[:, None] | np.asarray(lows, np.uint64)[None, :]).ravel()
    uni = rng.integers(0, 1 << 32, 200_000 if quick else 8_000_000, dtype=np.uint64)
    return np.concatenate([grid, uni]).astype(np.uint32)


def _inputs(spec) -> tuple:
    kind = spec[0]
    if kind == "range":
        return (range(spec[1], spec[1] + spec[2]),)
    if kind == "f32pairs":
        return _f32_pairs(spec[1], spec[2])
    if kind == "cross":
        return _cross()
    if kind == "select":
        return _select_triples(spec[1], spec[2], spec[3])
    if kind == "bits":
        return tuple(np.asarray(c, np.uint32) for c in spec[1])
    if kind == "words":
        return (np.asarray(spec[1], np.uint32),)
    raise ValueError(kind)


_TC = {1: "B", 8: "B", 16: "H", 32: "I"}


def _eval(task):
    """(name, spec, want_words) -> output (and input) digests of one chunk."""
    name, spec, want = task
    d = _D[name]
    f = d.evaluate
    tc = _TC[d.ret.w]
    if spec[0] == "bf16grid":
        a0, na = spec[1], spec[2]
        out = array(tc)
        for a in range(a0, a0 + na):
            out.extend(map(f, repeat(a, 1 << 16), range(1 << 16)))
        ins_sha = f"a[{a0},{a0 + na}) x b[0,65536)"
    else:
        cols = _inputs(spec)
        if spec[0] == "range":
            out = array(tc, map(f, cols[0]))
            ins_sha = f"[{spec[1]},{spec[1] + spec[2]})"
        else:
            out = array(tc, map(f, *(c.tolist() for c in cols)))
            ins_sha = hashlib.sha256(b"".join(c.tobytes() for c in cols)).hexdigest()
    res = {"name": name, "spec": [s if isinstance(s, (int, str)) else None for s in spec], "n": len(out),
           "out": hashlib.sha256(out.tobytes()).hexdigest(), "in": ins_sha}
    if want:
        res["words"] = out.tobytes()
        res["tc"] = tc
    return res


def _dot(task):
    cid, acc, a, b = task
    f = _D["HopperE4m3QgmmaDot32"].evaluate
    out = np.fromiter((f(int(acc[i]), *a[i].tolist(), *b[i].tolist()) for i in range(len(acc))), dtype=np.uint32, count=len(acc))
    res = {"cid": cid, "scalar": out}
    if _SIDE == "old":
        from verity_vllm.program.registry.derived_rows import tc_dot32_e4m3
        w, nonfin = tc_dot32_e4m3(acc.astype(np.uint32), a.astype(np.uint8), b.astype(np.uint8))
        res["twin"], res["twin_nonfinite"] = np.asarray(w, dtype=np.uint32), np.asarray(nonfin, dtype=bool)
    return res


ACC_SP = [0x00000000, 0x80000000, 0x7F800000, 0xFF800000, 0x7FC00000, 0xFFC00000, 0x7F800001, 0xFFFFFFFF, 0x7F7FFFFF,
          0xFF7FFFFF, 0x00000001, 0x807FFFFF, 0x00800000, 0x3F800000, 0xBF800000, 0x4B800000]
E4_SP = [0x00, 0x80, 0x01, 0x81, 0x07, 0x08, 0x38, 0xB8, 0x7E, 0xFE, 0x7F, 0xFF, 0x77, 0x40]


def _dot_inputs(quick: bool) -> dict:
    from verity.ir.types import Array, Value
    from verity.ml.kernels import sample_tc

    rng = np.random.default_rng([SEED, 4])
    parts = {}
    acc, a, b = [], [], []
    for x in ACC_SP:
        for p in (0, 13, 31):
            for sa in E4_SP:
                for sb in E4_SP:
                    for fill in (0, 1):
                        av = rng.integers(0x20, 0x58, size=32) * fill
                        bv = rng.integers(0x20, 0x58, size=32) * fill
                        av[p], bv[p] = sa, sb
                        acc.append(x), a.append(av), b.append(bv)
    parts["special_grid"] = (np.asarray(acc, np.uint32), np.asarray(a, np.uint8), np.asarray(b, np.uint8))
    n = 10_000 if quick else 300_000
    sp = np.asarray(E4_SP, np.uint8)
    mk = lambda: np.where(rng.random((n, 32)) < 0.3, sp[rng.integers(0, len(sp), (n, 32))],  # noqa: E731
                          rng.integers(0, 256, (n, 32))).astype(np.uint8)
    acc = np.where(rng.random(n) < 0.5, np.asarray(ACC_SP, np.uint32)[rng.integers(0, len(ACC_SP), n)],
                   rng.integers(0, 1 << 32, n)).astype(np.uint32)
    parts["dense_specials"] = (acc, mk(), mk())
    n = 20_000 if quick else 1_000_000
    s = sample_tc(rng, n, [Value(32), Array(32, Value(8)), Array(32, Value(8))])
    parts["sample_tc"] = (s[0].astype(np.uint32), s[1].astype(np.uint8), s[2].astype(np.uint8))
    n = 10_000 if quick else 300_000
    parts["uniform_bytes"] = (rng.integers(0, 1 << 32, n).astype(np.uint32), rng.integers(0, 256, (n, 32)).astype(np.uint8),
                              rng.integers(0, 256, (n, 32)).astype(np.uint8))
    n = 10_000 if quick else 200_000
    z = np.zeros((n + len(F32_SP), 32), np.uint8)
    parts["acc_passthrough"] = (np.concatenate([rng.integers(0, 1 << 32, n).astype(np.uint32), np.asarray(F32_SP, np.uint32)]), z, z)
    return parts


# ---- encodings, programs, pins (one process per side, every registry module imported) ------------------------------------

STATIC_BINDS = [
    ("Fp8RowAbsMax_v1", {"K": 256}), ("Fp8ActQuant_v1", {"K": 256}), ("DotE4m3_v1", {"K": 64}),
    ("ScaledMmFp8Coordinate_v1", {"K": 64, "BIAS": True}), ("ScaledMmFp8Coordinate_v1", {"K": 64, "BIAS": False}),
    ("ScaledMmFp8_v1", {"K": 64, "N": 2, "BIAS": False}), ("QuantLinearFp8_v1", {"K": 256, "N": 2, "BIAS": True}),
    ("Fp8GroupScale_v1", {"G": 128}), ("Fp8GroupQuant_v1", {"K": 256, "G": 128}),
    ("ScaledMmFp8BlockCoordinate_v1", {"K": 256, "G": 128}), ("ScaledMmFp8Block_v1", {"K": 256, "N": 2, "G": 128}),
    ("MoeRouterTopK_v1", {"E": 8, "TOPK": 2, "VPT": 8}), ("MoeRouterTopKNorm_v1", {"E": 8, "TOPK": 2, "VPT": 8}),
    ("MoeSumCoordinate_v1", {"TOPK": 2}), ("MoeSum_v1", {"TOPK": 2, "H": 4}),
    ("TemperatureScale_v1", {"V": 8}), ("GumbelSelectF32_v1", {"V": 8}), ("GumbelTokenSelect_v1", {"V": 8}),
    ("TopPMaskStep_v1", {"V": 8}), ("TopPMask_v1", {"V": 8}), ("GumbelTopPTokenSelect_v1", {"V": 8}),
    ("Accept_v1", {"K": 2}), ("Advance_v1", {"K": 2}), ("PadGuard_v1", {"EOS": 2}),
    ("MoeSlotDownCoordinate_v1", {"K": 64}), ("MoeSlotDown_v1", {"K": 64, "N": 2}),
    ("ArgmaxRef_v1", {"V": 8, "DT": "f32"}), ("ArgmaxRef_v1", {"V": 8, "DT": "bf16"}),
]


def _body_sha(fn) -> str:
    """sha256 of the function body's AST without its docstring (so a moved body compares equal under a new name/doc)."""
    import ast
    import inspect
    import textwrap
    node = ast.parse(textwrap.dedent(inspect.getsource(fn))).body[0]
    body = node.body
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]
    return hashlib.sha256(ast.dump(ast.Module(body=body, type_ignores=[])).encode()).hexdigest()


def _encodings(_=None) -> dict:
    import importlib
    import inspect
    import pkgutil

    if _INIT_ERR:
        raise RuntimeError(f"{_SIDE} init: {_INIT_ERR}")
    from verity.ir.codec import _encode_definition, canonical_json, program_digest
    from verity.ir.defs import REGISTRY, CompositeDefinition, bind
    from verity.ir.program import Program

    import verity_vllm
    assert os.path.abspath(verity_vllm.__file__).startswith(BASE if _SIDE == "oldall" else HEAD), verity_vllm.__file__
    import verity_vllm.program.registry as registry
    if _SIDE == "headall":
        import verity.ml.gemm, verity.ml.kernels, verity.ml.prims, verity.ml.scalar  # noqa: E401, F401
    mods, failed = sorted(m.name for m in pkgutil.walk_packages(registry.__path__, registry.__name__ + ".")), {}
    for m in mods:
        try:
            importlib.import_module(m)
        except Exception as e:  # noqa: BLE001
            failed[m] = f"{type(e).__name__}: {e}"[:300]
    out: dict = {"modules": len(mods), "import_failed": failed, "ids": sorted(REGISTRY.defs), "prims": {}, "programs": {},
                 "program_errors": {}, "pins": {}, "host_nan": {}}
    for n in MOVED:
        d = REGISTRY.defs[f"{n}_v1"]
        out["prims"][n] = {"enc": json.loads(canonical_json(_encode_definition(d))), "params": [[p, repr(t)] for p, t in d.params],
                           "ret": repr(d.ret), "conformance": d.conformance, "doc": d.doc,
                           "file": os.path.relpath(inspect.getsourcefile(d.evaluate), BASE if _SIDE == "oldall" else HEAD),
                           "body_sha": _body_sha(d.evaluate)}
    if _SIDE == "oldall":
        from verity_vllm.program.registry import fp8 as F
        out["e4m3_word_fn_body_sha"] = _body_sha(F.f32_to_e4m3_sat_bits)
    else:
        from verity.ml.tc import cast
        out["e4m3_word_fn_body_sha"] = _body_sha(cast.f32_to_e4m3_sat_word)
    for fid, d in sorted(REGISTRY.defs.items()):
        if isinstance(d, CompositeDefinition) and not d.statics:
            try:
                out["programs"][fid] = program_digest(Program(bind(d)))
            except Exception as e:  # noqa: BLE001
                out["program_errors"][fid] = f"{type(e).__name__}: {e}"[:200]
    for fid, kw in STATIC_BINDS:
        key = f"{fid}{json.dumps(kw, sort_keys=True)}"
        try:
            out["programs"][key] = program_digest(Program(bind(REGISTRY.defs[fid], **kw)))
        except Exception as e:  # noqa: BLE001
            out["program_errors"][key] = f"{type(e).__name__}: {e}"[:200]
    from verity_vllm.program.frontend.provenance import registry_version
    from verity_vllm.program.frontend.rules import vocab as V
    from verity_vllm.program.registry import prims as P, ref_prims as R
    out["pins"]["registry_version"] = registry_version()["digest"]
    out["pins"]["ref_vocab_digest"] = R.ref_vocab_digest()
    out["pins"]["vocabularies"] = {k: v.version for k, v in sorted(vars(V).items()) if isinstance(v, V.Vocabulary)}
    import platform
    out["host_nan"] = {"machine": platform.machine(), "numpy": np.__version__,
                       "F32Add(inf,-inf)": hex(P.F32Add.evaluate(0x7F800000, 0xFF800000)),
                       "F32Mul(inf,0)": hex(P.F32Mul.evaluate(0x7F800000, 0)),
                       "F32Div(0,0)": hex(P.F32Div.evaluate(0, 0)),
                       "F32Add(1,sNaN)": hex(P.F32Add.evaluate(0x3F800000, 0x7F800001)),
                       "F32Add(1,-qNaN)": hex(P.F32Add.evaluate(0x3F800000, 0xFFC00000))}
    return out


# ---- driver ---------------------------------------------------------------------------------------------------------------


def _submit(pools, name, specs):
    tasks = [(name, s, False) for s in specs]
    return name, specs, pools["old"].map_async(_eval, tasks, chunksize=1), pools["new"].map_async(_eval, tasks, chunksize=1)


def _collect(pools, job, res, t0):
    """Record chunk agreement of one submitted evaluator job and the first difference."""
    name, specs, ao, an = job
    ro, rn = ao.get(), an.get()
    tasks = specs
    bad = [i for i in range(len(tasks)) if ro[i]["out"] != rn[i]["out"] or ro[i]["in"] != rn[i]["in"]]
    first = None
    for i in bad[:1]:
        wo = pools["old"].apply(_eval, ((name, specs[i], True),))
        wn = pools["new"].apply(_eval, ((name, specs[i], True),))
        xo, xn = np.frombuffer(wo["words"], wo["tc"]), np.frombuffer(wn["words"], wn["tc"])
        j = int(np.flatnonzero(xo != xn)[0]) if len(xo) == len(xn) and (xo != xn).any() else -1
        first = {"spec": ro[i]["spec"], "in_equal": ro[i]["in"] == rn[i]["in"], "index": j,
                 "old": hex(int(xo[j])) if j >= 0 else None, "new": hex(int(xn[j])) if j >= 0 else None,
                 "n_differ_in_chunk": int((xo != xn).sum()) if len(xo) == len(xn) else None}
        if j >= 0:
            s = specs[i]
            if s[0] == "range":
                first["input"] = [hex(s[1] + j)]
            elif s[0] == "bf16grid":
                first["input"] = [hex(s[1] + j // 65536), hex(j % 65536)]
            else:
                first["input"] = [hex(int(c[j])) for c in _inputs(s)]
    roll = lambda r: hashlib.sha256("".join(x["out"] for x in r).encode()).hexdigest()  # noqa: E731
    key = name
    res["evaluators"][key] = {"cases": int(sum(x["n"] for x in ro)), "chunks": len(tasks), "chunks_differ": len(bad),
                              "first_difference": first, "rollup_old": roll(ro), "rollup_new": roll(rn),
                              "done_at_s": round(time.time() - t0, 1)}
    print(f"{key}: " + json.dumps({k: v for k, v in res["evaluators"][key].items() if k != "first_difference"}), flush=True)
    if first:
        print("  first difference:", json.dumps(first), flush=True)


def main() -> int:
    out_path = sys.argv[1]
    quick = "--quick" in sys.argv
    ctx = mp.get_context("spawn")
    ncpu = int(os.environ.get("C2_NPROC", "32"))  # the container's vCPUs (os.cpu_count() reports the host's)
    n_old, n_new = ncpu, max(1, ncpu // 2)
    t0 = time.time()
    res: dict = {"seed": SEED, "quick": quick, "base": BASE, "head": HEAD, "pools": {"old": n_old, "new": n_new},
                 "evaluators": {}, "dot": {}, "encodings": {}}

    with ctx.Pool(1, initializer=_init, initargs=("oldall",)) as po, ctx.Pool(1, initializer=_init, initargs=("headall",)) as ph:
        eo, eh = po.apply_async(_encodings), ph.apply_async(_encodings)
        eo, eh = eo.get(), eh.get()
    enc = res["encodings"]
    enc["import_failed"] = {"base": eo["import_failed"], "head": eh["import_failed"]}
    enc["modules"] = {"base": eo["modules"], "head": eh["modules"]}
    enc["ids_only_base"], enc["ids_only_head"] = sorted(set(eo["ids"]) - set(eh["ids"])), sorted(set(eh["ids"]) - set(eo["ids"]))
    enc["prims"] = {}
    for n in MOVED:
        o, h = eo["prims"][n], eh["prims"][n]
        enc["prims"][n] = {"encoding_equal": o["enc"] == h["enc"], "params_equal": o["params"] == h["params"],
                           "ret_equal": o["ret"] == h["ret"], "conformance_equal": o["conformance"] == h["conformance"],
                           "doc_equal": o["doc"] == h["doc"], "body_text_equal": o["body_sha"] == h["body_sha"],
                           "file": [o["file"], h["file"]]}
        if not enc["prims"][n]["conformance_equal"]:
            enc["prims"][n]["conformance"] = [o["conformance"], h["conformance"]]
    po_, ph_ = eo["programs"], eh["programs"]
    enc["programs"] = {"n_base": len(po_), "n_head": len(ph_), "keys_equal": sorted(po_) == sorted(ph_),
                       "differ": sorted(k for k in set(po_) & set(ph_) if po_[k] != ph_[k]),
                       "only_base": sorted(set(po_) - set(ph_)), "only_head": sorted(set(ph_) - set(po_)),
                       "errors_base": eo["program_errors"], "errors_head": eh["program_errors"], "digests_head": ph_}
    enc["e4m3_word_fn_body_equal"] = eo["e4m3_word_fn_body_sha"] == eh["e4m3_word_fn_body_sha"]
    enc["pins"] = {"base": eo["pins"], "head": eh["pins"]}
    enc["host_nan"] = {"base": eo["host_nan"], "head": eh["host_nan"]}
    print("encodings:", json.dumps({k: enc[k] for k in ("modules", "import_failed", "ids_only_base")}), flush=True)
    print("programs:", json.dumps({k: v for k, v in enc["programs"].items() if k != "digests_head"}), flush=True)
    print("prims:", json.dumps({n: {k: v for k, v in p.items() if not v} for n, p in enc["prims"].items()}), flush=True)
    print("pins:", json.dumps(enc["pins"]), "\nhost_nan:", json.dumps(enc["host_nan"]), flush=True)
    json.dump(res, open(out_path, "w"), indent=1)

    with ctx.Pool(n_old, initializer=_init, initargs=("old",)) as pold, ctx.Pool(n_new, initializer=_init, initargs=("new",)) as pnew:
        pools = {"old": pold, "new": pnew}
        res["whoami"] = {"old": pold.apply(_whoami), "new": pnew.apply(_whoami)}
        print(json.dumps(res["whoami"], indent=1), flush=True)
        if any("init_error" in v for v in res["whoami"].values()):
            json.dump(res, open(out_path, "w"), indent=1)
            raise SystemExit(1)

        total = 1 << (24 if quick else 32)
        na = 4 if quick else 64
        nchunks, m = (4, 1 << 16) if quick else (96, 1 << 20)
        w, mw = _e4m3_words(quick), 1 << 17
        g = [(x, y) for x in range(4) for y in range(4)]
        plan = [(n, [("range", s, min(CHUNK, total - s)) for s in range(0, total, CHUNK)])
                for n in ("F32Sat", "F32Fabs", "F32Neg", "F32BitsShl23", "F32IsFinite")]
        plan.append(("Bf16GtStrict", [("bf16grid", a, na) for a in range(0, (1 << 8) if quick else (1 << 16), na)]))
        plan.append(("F32ToE4m3Sat", [("words", w[s:s + mw]) for s in range(0, len(w), mw)]))
        plan += [(n, [("cross",)] + [("f32pairs", c, m) for c in range(nchunks)])
                 for n in ("F32Fmaxf", "F32Fminf", "F32Eq", "I32Le", "I32Eq", "I32Add")]
        plan += [(n, [("select", c, 1 << 18, wd) for c in range(4 if quick else 16)])
                 for n, wd in (("SelectF32", 32), ("SelectBf16", 16), ("SelectI32", 32))]
        plan += [("BitAnd", [("bits", ([x for x, _ in g], [y for _, y in g]))]),
                 ("BitOr", [("bits", ([x for x, _ in g], [y for _, y in g]))]), ("BitNot", [("bits", ([0, 1, 2, 3],))])]
        jobs = [_submit(pools, n, specs) for n, specs in plan]

        from verity.ml.kernels import group_sum_total_batch
        from verity.ml.tc.total_fp8 import HOPPER_E4M3_WGMMA_K32

        dots = []
        for part, (acc, a, b) in _dot_inputs(quick).items():
            m = 5_000
            tasks = [(i, acc[s:s + m], a[s:s + m], b[s:s + m]) for i, s in enumerate(range(0, len(acc), m))]
            dots.append((part, acc, a, b, tasks, pold.map_async(_dot, tasks, chunksize=1), pnew.map_async(_dot, tasks, chunksize=1)))
        print(f"submitted {len(jobs)} evaluator jobs, {len(dots)} dot parts at {time.time() - t0:.0f}s", flush=True)

        for job in jobs:
            _collect(pools, job, res, t0)
            json.dump(res, open(out_path, "w"), indent=1)

        for part, acc, a, b, tasks, ao, an in dots:
            t = time.time()
            ro, rn = {r["cid"]: r for r in ao.get()}, {r["cid"]: r for r in an.get()}
            so = np.concatenate([ro[i]["scalar"] for i in range(len(tasks))])
            sn = np.concatenate([rn[i]["scalar"] for i in range(len(tasks))])
            tw = np.concatenate([ro[i]["twin"] for i in range(len(tasks))])
            nf = np.concatenate([ro[i]["twin_nonfinite"] for i in range(len(tasks))])
            kern = group_sum_total_batch(HOPPER_E4M3_WGMMA_K32, acc, a, b)[0].astype(np.uint32)
            d_on, d_k, d_tw = np.flatnonzero(so != sn), np.flatnonzero(sn != kern), np.flatnonzero((so != tw) & ~nf)
            ex = lambda d: None if not len(d) else {"i": int(d[0]), "acc": hex(int(acc[d[0]])), "a": [hex(int(x)) for x in a[d[0]]],  # noqa: E731
                                                    "b": [hex(int(x)) for x in b[d[0]]], "old": hex(int(so[d[0]])),
                                                    "new": hex(int(sn[d[0]])), "kernel": hex(int(kern[d[0]])), "twin": hex(int(tw[d[0]]))}
            res["dot"][part] = {"cases": int(len(acc)), "old_vs_new_differ": int(len(d_on)), "new_vs_core_kernel_differ": int(len(d_k)),
                                "old_vs_old_twin_differ_where_twin_finite": int(len(d_tw)), "twin_nonfinite": int(nf.sum()),
                                "nonfinite_outputs": int(((sn & 0x7F800000) == 0x7F800000).sum()), "zero_outputs": int((sn == 0).sum()),
                                "sha256_old": hashlib.sha256(so.tobytes()).hexdigest(), "sha256_new": hashlib.sha256(sn.tobytes()).hexdigest(),
                                "first_old_vs_new": ex(d_on), "first_new_vs_kernel": ex(d_k), "first_old_vs_twin": ex(d_tw),
                                "collect_seconds": round(time.time() - t, 1), "done_at_s": round(time.time() - t0, 1)}
            print(f"dot {part}: " + json.dumps({k: v for k, v in res['dot'][part].items() if not k.startswith('first')}), flush=True)
            json.dump(res, open(out_path, "w"), indent=1)

    p = enc["prims"]
    ok_enc = (all(v["encoding_equal"] and v["params_equal"] and v["ret_equal"] for v in p.values())
              and not enc["programs"]["only_base"] and not enc["programs"]["differ"] and not enc["ids_only_base"]
              and not enc["import_failed"]["head"])
    ok_eval = all(v["chunks_differ"] == 0 for v in res["evaluators"].values())
    ok_dot = all(v["old_vs_new_differ"] == 0 and v["new_vs_core_kernel_differ"] == 0 for v in res["dot"].values())
    ok = ok_enc and ok_eval and ok_dot
    res["all_equal"], res["ok"] = ok, {"encodings": ok_enc, "evaluators": ok_eval, "dot": ok_dot}
    res["seconds"] = round(time.time() - t0, 1)
    json.dump(res, open(out_path, "w"), indent=1)
    print("ALL-EQUAL" if ok else "DIFFERENCES", json.dumps(res["ok"]), res["seconds"], "s", flush=True)
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
