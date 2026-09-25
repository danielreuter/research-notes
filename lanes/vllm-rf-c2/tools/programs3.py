"""Program digests of the stored regression Programs, through one side's library (base or head).

For every `descriptor.json.gz` under ROWDIR (a materialized records artifact):
  stored     program_digest(desc) vs the sibling artifact.json `program_digest` / workload_program.json `workload_digest`
  reencode   decode_program(desc, REGISTRY) with every registry module (+ core verity.ml) imported, encode_program again
             under the descriptor's schema, program_digest vs the stored digest
  respec     every composite whose `Name_vN` is a registered CompositeDefinition, re-specialized through this side's
             library with the decoded bindings (function statics mapped to their re-specialized / registry objects):
             v1 encoding (own interning tables) vs the decoded definition's; sha of the library encoding per id (base
             vs head)
  scan       the definition ids containing AmpereBF16TcDot16, and the moved primitive ids each descriptor cites, with the
             file the registry object's evaluator comes from

usage: python programs3.py SIDE ROWDIR OUT.json      (SIDE base|head; the process's PYTHONPATH selects the tree)
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import importlib
import inspect
import json
import os
import pkgutil
import resource
import sys
import time

MOVED = ["F32ToE4m3Sat_v1", "HopperE4m3QgmmaDot32_v1", "F32Fabs_v1", "F32Neg_v1", "F32Fmaxf_v1", "F32Fminf_v1", "F32Sat_v1",
         "F32BitsShl23_v1", "F32IsFinite_v1", "F32Eq_v1", "Bf16GtStrict_v1", "I32Le_v1", "I32Eq_v1", "I32Add_v1", "BitAnd_v1",
         "BitNot_v1", "BitOr_v1", "SelectF32_v1", "SelectBf16_v1", "SelectI32_v1",
         "Bf16ToF32_v1", "F32ToBf16Rn_v1", "F2fpBf16_v1", "HopperBF16WgmmaDot16_v1", "DotBf16_v2", "GemmCoordinate_v2", "Gemm_v2"]


def _rss_gb() -> float:
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 2)


def _setup(side: str):
    import verity
    import verity_vllm
    root = os.environ["C2_TREE"]
    assert os.path.abspath(verity.__file__).startswith(root) and os.path.abspath(verity_vllm.__file__).startswith(root), \
        (side, verity.__file__, verity_vllm.__file__)
    if side == "head":
        import verity.ml.gemm, verity.ml.kernels, verity.ml.prims, verity.ml.scalar  # noqa: E401, F401
    import verity_vllm.program.registry as registry
    failed = {}
    for m in sorted(m.name for m in pkgutil.walk_packages(registry.__path__, registry.__name__ + ".")):
        try:
            importlib.import_module(m)
        except Exception as e:  # noqa: BLE001
            failed[m] = f"{type(e).__name__}: {e}"[:300]
    return root, failed


def _stored_digest(dpath: str) -> tuple[str | None, str | None]:
    d = os.path.dirname(dpath)
    for name, key in (("artifact.json", "program_digest"), ("workload_program.json", "workload_digest")):
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return json.load(open(p)).get(key), f"{name}:{key}"
    return None, None


def _respec(desc, dp, registry, root):
    from verity.ir.codec import SCHEMA_V1, _encode_definition, _Tables, canonical_json, lookup_primitive
    from verity.ir.defs import CompositeDefinition, FunctionDefinition, PrimitiveDefinition, SpecializedDefinition, bind

    lib: dict[str, object] = {}
    res = {"reproduced": 0, "differ": [], "n_differ": 0, "unregistered": 0, "errors": {}, "lib_sha": {}}

    def v1(fn) -> bytes:
        """One definition in the descriptor's v1 form with its own interning tables (v0 keeps the builder's Refs
        nesting, which a decoded body does not)."""
        t = _Tables()
        return canonical_json([_encode_definition(fn, SCHEMA_V1, t), t.to_json()])

    def fid_of(fn) -> str:
        from verity.ir.codec import _spec_id
        return _spec_id(fn)

    def map_static(v):
        if isinstance(v, PrimitiveDefinition):
            return lookup_primitive(registry, v.id)
        if isinstance(v, SpecializedDefinition):
            return get(fid_of(v))
        if isinstance(v, FunctionDefinition):
            return v
        if isinstance(v, tuple):
            return tuple(map_static(x) for x in v)
        if isinstance(v, list):
            return [map_static(x) for x in v]
        if isinstance(v, dict):
            return {k: map_static(x) for k, x in v.items()}
        return v

    def get(fid: str):
        if fid in lib:
            return lib[fid]
        dec = dp.defs[fid]
        if isinstance(dec, PrimitiveDefinition):
            lib[fid] = lookup_primitive(registry, dec.id)
            return lib[fid]
        lib[fid] = dec  # stand-in against cycles and for unregistered composites
        base = desc["definitions"][fid]["id"]
        defn = registry.defs.get(base)
        if not isinstance(defn, CompositeDefinition):
            res["unregistered"] += 1
            return dec
        try:
            sp = bind(defn, **{k: map_static(dec.bindings[k]) for k in dec.defn.statics})
            enc_lib = v1(sp)
            enc_dec = v1(dec)
        except Exception as e:  # noqa: BLE001
            res["errors"][fid] = f"{type(e).__name__}: {e}"[:300]
            return dec
        res["lib_sha"][fid] = hashlib.sha256(enc_lib).hexdigest()
        if enc_lib == enc_dec:
            res["reproduced"] += 1
        else:
            res["differ"].append(fid)
        lib[fid] = sp
        return sp

    for fid, d in desc["definitions"].items():
        if d["form"] == "composite":
            get(fid)
    res["n_differ"] = len(res["differ"])
    res["differ"] = sorted(res["differ"])[:50]
    return res


def main() -> int:
    side, rowdir, out = sys.argv[1], sys.argv[2], sys.argv[3]
    t0 = time.time()
    root, failed = _setup(side)
    from verity.ir.codec import decode_program, encode_program, program_digest
    from verity.ir.defs import REGISTRY, PrimitiveDefinition
    rep = {"side": side, "tree": root, "rowdir": rowdir, "import_failed": failed, "descriptors": {}}
    moved_files = {}
    for fid in MOVED:
        d = REGISTRY.defs.get(fid)
        if d is None:
            moved_files[fid] = None
        else:
            fn = d.evaluate if isinstance(d, PrimitiveDefinition) else d.body
            moved_files[fid] = os.path.relpath(inspect.getsourcefile(fn), root)
    rep["moved_files"] = moved_files
    for p in sorted(glob.glob(os.path.join(rowdir, "**", "descriptor.json.gz"), recursive=True)):
        rel = os.path.relpath(p, rowdir)
        r: dict = {}
        t1 = time.time()
        try:
            with gzip.open(p, "rt") as f:
                desc = json.load(f)
            r["schema"] = desc.get("schema")
            r["n_definitions"] = len(desc["definitions"])
            r["stored_digest"], r["stored_from"] = _stored_digest(p)
            r["desc_digest"] = program_digest(desc)
            r["stored_ok"] = r["stored_digest"] in (None, r["desc_digest"])
            ids = {d["id"] for d in desc["definitions"].values()}
            r["ampere_ids"] = sorted(i for i in ids if "AmpereBF16TcDot16" in i)
            r["ampere_specs"] = sum(1 for d in desc["definitions"].values() if "AmpereBF16TcDot16" in d["id"])
            r["moved_cited"] = sorted(i for i in ids if i in MOVED)
            dp = decode_program(desc, REGISTRY)
            r["reencode_digest"] = program_digest(encode_program(dp, schema=desc["schema"]))
            r["reencode_ok"] = r["reencode_digest"] == r["desc_digest"]
            r["respec"] = _respec(desc, dp, REGISTRY, root)
            del dp, desc
        except Exception as e:  # noqa: BLE001
            import traceback
            r["error"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()[-2000:]}"
        r["seconds"] = round(time.time() - t1, 1)
        r["maxrss_gb"] = _rss_gb()
        rep["descriptors"][rel] = r
        rs = r.get("respec") or {}
        print(f"{side} {rel}: stored_ok={r.get('stored_ok')} reencode_ok={r.get('reencode_ok')} respec={rs.get('reproduced')}"
              f"/differ={rs.get('n_differ')}/unreg={rs.get('unregistered')}/err={len(rs.get('errors', {}))} "
              f"ampere={r.get('ampere_ids')} {r['seconds']}s rss={r['maxrss_gb']}GB{' ERROR ' + r['error'][:200] if 'error' in r else ''}",
              flush=True)
    rep["seconds"] = round(time.time() - t0, 1)
    rep["maxrss_gb"] = _rss_gb()
    json.dump(rep, open(out, "w"), indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
