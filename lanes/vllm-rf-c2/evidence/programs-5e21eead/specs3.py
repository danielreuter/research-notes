"""Definition closures of every stored regression Program's top-level calls, through one side's library.

The stored `programs` trees hold, per Build shape, `instances.json.gz`: the root body of the request Program as rows
`{"i", "spec", "form", "name", "args"}`.  A Program's digest hashes that root body (the frontend's output, not this lane's
code) and the encoding of every definition its calls reach.  This recomputes the second part from the library:

  extract   (once) the distinct `spec` ids of every instances.json.gz under /workspace/c2/progs/<row>, streamed from the
            gzip (the B=1 documents do not fit a json.load next to the gate), -> SPECS.json
  closure   (per side) each spec id parsed back into its registered CompositeDefinition + binding record (function statics
            recursively), bound through this side's library (the rebuilt `_spec_id` must equal the id), and its whole
            definition closure encoded (v1 form, own interning tables, per definition); sha256 over the sorted
            (id, encoding) pairs; the closure's AmpereBF16TcDot16 ids and the moved ids it reaches

usage: python specs3.py extract ROW [ROW ...] SPECS.json
       python specs3.py closure SIDE SPECS.json OUT.json       (PYTHONPATH selects the tree; env C2_TREE its root)
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import importlib
import json
import multiprocessing as mp
import os
import pkgutil
import re
import resource
import sys
import time

PROGS = "/workspace/c2/progs"
SPEC_RE = re.compile(r'"spec":\s*"((?:[^"\\]|\\.)*)"')
MOVED = ["F32ToE4m3Sat_v1", "HopperE4m3QgmmaDot32_v1", "F32Fabs_v1", "F32Neg_v1", "F32Fmaxf_v1", "F32Fminf_v1", "F32Sat_v1",
         "F32BitsShl23_v1", "F32IsFinite_v1", "F32Eq_v1", "Bf16GtStrict_v1", "I32Le_v1", "I32Eq_v1", "I32Add_v1", "BitAnd_v1",
         "BitNot_v1", "BitOr_v1", "SelectF32_v1", "SelectBf16_v1", "SelectI32_v1",
         "Bf16ToF32_v1", "F32ToBf16Rn_v1", "F2fpBf16_v1", "HopperBF16WgmmaDot16_v1", "DotBf16_v2", "GemmCoordinate_v2", "Gemm_v2"]


def _scan(path: str) -> tuple[str, dict]:
    specs: dict[str, int] = {}
    tail = ""
    with gzip.open(path, "rt") as f:
        while True:
            chunk = f.read(1 << 26)
            if not chunk:
                break
            buf = tail + chunk
            last = 0
            for m in SPEC_RE.finditer(buf):
                s = json.loads(f'"{m.group(1)}"')
                specs[s] = specs.get(s, 0) + 1
                last = m.end()
            tail = buf[max(last, len(buf) - (1 << 20)):]
    return path, {"rows_seen": sum(specs.values()), "specs": specs}


def extract(rows: list[str], out: str) -> int:
    files = []
    for r in rows:
        files += sorted(glob.glob(os.path.join(PROGS, r, "**", "instances.json.gz"), recursive=True))
    t0 = time.time()
    with mp.get_context("spawn").Pool(int(os.environ.get("C2_NPROC", "8"))) as pool:
        res = dict(pool.imap_unordered(_scan, files))
    doc = {"rows": {}, "seconds": round(time.time() - t0, 1)}
    for p, v in sorted(res.items()):
        r = os.path.relpath(p, PROGS).split(os.sep)[0]
        doc["rows"].setdefault(r, {})[os.path.relpath(p, os.path.join(PROGS, r))] = v
    json.dump(doc, open(out, "w"), indent=1, sort_keys=True)
    for r, fs in sorted(doc["rows"].items(), key=lambda kv: int(kv[0])):
        n = len({s for v in fs.values() for s in v["specs"]})
        print(f"row {r}: {len(fs)} files, {sum(v['rows_seen'] for v in fs.values())} rows, {n} distinct specs", flush=True)
    print(f"extract {doc['seconds']} s", flush=True)
    return 0


def _setup():
    import verity
    import verity_vllm
    root = os.environ["C2_TREE"]
    assert os.path.abspath(verity.__file__).startswith(root) and os.path.abspath(verity_vllm.__file__).startswith(root)
    try:
        import verity.ml.scalar  # noqa: F401
        import verity.ml.gemm, verity.ml.kernels, verity.ml.prims  # noqa: E401, F401
    except ImportError:
        pass
    import verity_vllm.program.registry as registry
    failed = {}
    for m in sorted(m.name for m in pkgutil.walk_packages(registry.__path__, registry.__name__ + ".")):
        try:
            importlib.import_module(m)
        except Exception as e:  # noqa: BLE001
            failed[m] = f"{type(e).__name__}: {e}"[:300]
    return root, failed


def closure(side: str, specs_path: str, out: str) -> int:
    t0 = time.time()
    root, failed = _setup()
    from verity.ir.codec import (SCHEMA_V1, _as_specialized, _encode_definition, _spec_id, _split_record, _static_functions,
                                 _Tables, canonical_json, lookup_primitive)
    from verity.ir.defs import REGISTRY, CompositeDefinition, PrimitiveDefinition, SpecializedDefinition, bind

    built: dict[str, object] = {}

    def static(v):
        if isinstance(v, dict) and set(v) == {"fn"}:
            return fn_of(v["fn"])
        if isinstance(v, dict) and set(v) == {"f64"}:
            return float.fromhex(v["f64"])
        if isinstance(v, dict) and set(v) == {"dict"}:
            return {k: static(x) for k, x in v["dict"].items()}
        if isinstance(v, list):
            return tuple(static(x) for x in v)
        return v

    def fn_of(fid: str):
        if fid in built:
            return built[fid]
        if "{" not in fid:
            d = REGISTRY.defs.get(fid)
            if d is None:
                d = lookup_primitive(REGISTRY, fid)
            sp = bind(d) if isinstance(d, CompositeDefinition) else d
        else:
            base = fid[:fid.index("{")]
            d = REGISTRY.defs.get(base)
            if not isinstance(d, CompositeDefinition):
                raise KeyError(f"{base} is not a registered composite")
            sp = bind(d, **{k: static(json.loads(v)) for k, v in _split_record(fid)})
        if _spec_id(sp) != fid:
            raise ValueError(f"rebuilt id differs: {_spec_id(sp)[:200]}")
        built[fid] = sp
        return sp

    enc_cache: dict[str, str] = {}

    def enc_sha(fn) -> str:
        fid = _spec_id(fn)
        h = enc_cache.get(fid)
        if h is None:
            t = _Tables()
            h = enc_cache[fid] = hashlib.sha256(canonical_json([_encode_definition(fn, SCHEMA_V1, t), t.to_json()])).hexdigest()
        return h

    deps_cache: dict[str, frozenset] = {}

    def closure_of(fn) -> dict[str, object]:
        seen: dict[str, object] = {}
        stack = [fn]
        while stack:
            f = stack.pop()
            fid = _spec_id(f)
            if fid in seen:
                continue
            seen[fid] = f
            if isinstance(f, SpecializedDefinition):
                stack += [n.fn for n in f.body.nodes]
                for k in f.defn.statics:
                    stack += [_as_specialized(g, fid) for g in _static_functions(f.bindings[k])]
        return seen

    doc = json.load(open(specs_path))
    all_specs = sorted({s.removeprefix("batch:") for fs in doc["rows"].values() for v in fs.values() for s in v["specs"]})
    res: dict[str, dict] = {}
    for i, s in enumerate(all_specs):
        r: dict = {}
        try:
            fn = fn_of(s)
            cl = closure_of(fn)
            pairs = sorted((fid, enc_sha(f)) for fid, f in cl.items())
            r["closure_sha"] = hashlib.sha256(canonical_json(pairs)).hexdigest()
            r["n_defs"] = len(pairs)
            r["ampere"] = sorted(fid for fid in cl if fid.startswith("AmpereBF16TcDot16_v"))
            r["moved"] = sorted(fid for fid in cl if fid in MOVED)
        except Exception as e:  # noqa: BLE001
            r["error"] = f"{type(e).__name__}: {e}"[:400]
        res[s] = r
        if i % 200 == 0:
            print(f"{side} {i}/{len(all_specs)} {round(time.time() - t0)} s rss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20:.1f} GB",
                  flush=True)
    rows = {}
    for row, fs in doc["rows"].items():
        ss = sorted({s.removeprefix("batch:") for v in fs.values() for s in v["specs"]})
        rows[row] = {"specs": len(ss), "errors": sum(1 for s in ss if "error" in res[s]),
                     "ampere_v1_specs": sum(1 for s in ss if "AmpereBF16TcDot16_v1" in res[s].get("ampere", [])),
                     "ampere_v2_specs": sum(1 for s in ss if "AmpereBF16TcDot16_v2" in res[s].get("ampere", [])),
                     "moved": sorted({m for s in ss for m in res[s].get("moved", [])}),
                     "row_sha": hashlib.sha256(canonical_json([[s, res[s].get("closure_sha")] for s in ss])).hexdigest()}
    json.dump({"side": side, "tree": root, "import_failed": failed, "rows": rows, "specs": res,
               "seconds": round(time.time() - t0, 1),
               "maxrss_gb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 2)},
              open(out, "w"), indent=1, sort_keys=True)
    for row, v in sorted(rows.items(), key=lambda kv: int(kv[0])):
        print(f"{side} row {row}: specs={v['specs']} errors={v['errors']} ampere_v1={v['ampere_v1_specs']} ampere_v2={v['ampere_v2_specs']} "
              f"row_sha={v['row_sha'][:16]} moved={v['moved']}", flush=True)
    print(f"{side} done {round(time.time() - t0, 1)} s", flush=True)
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "extract":
        sys.exit(extract(sys.argv[2:-1], sys.argv[-1]))
    sys.exit(closure(sys.argv[2], sys.argv[3], sys.argv[4]))
