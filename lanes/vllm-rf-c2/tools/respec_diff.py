"""First difference between a stored composite's v0 encoding and its re-specialization through this tree's library.

usage: python respec_diff.py DESCRIPTOR.json.gz FID [FID ...]      (PYTHONPATH selects the tree)
"""
from __future__ import annotations

import gzip
import importlib
import json
import pkgutil
import sys


def first_diff(a, b, path="$"):
    if type(a) is not type(b):
        return path, a, b
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                return f"{path}.{k}", a.get(k, "<missing>"), b.get(k, "<missing>")
            d = first_diff(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list):
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_diff(x, y, f"{path}[{i}]")
            if d:
                return d
        return (f"{path}.len", len(a), len(b)) if len(a) != len(b) else None
    return None if a == b else (path, a, b)


def main() -> int:
    import verity.ml.gemm, verity.ml.kernels, verity.ml.prims, verity.ml.scalar  # noqa: E401, F401
    import verity_vllm.program.registry as registry
    for m in sorted(m.name for m in pkgutil.walk_packages(registry.__path__, registry.__name__ + ".")):
        try:
            importlib.import_module(m)
        except Exception:  # noqa: BLE001
            pass
    from verity.ir.codec import _encode_definition, canonical_json, decode_program, lookup_primitive, _spec_id
    from verity.ir.defs import REGISTRY, PrimitiveDefinition, SpecializedDefinition, FunctionDefinition, bind
    desc = json.load(gzip.open(sys.argv[1], "rt"))
    dp = decode_program(desc, REGISTRY)

    def m(v):
        if isinstance(v, PrimitiveDefinition):
            return lookup_primitive(REGISTRY, v.id)
        if isinstance(v, SpecializedDefinition):
            base = REGISTRY.defs.get(v.defn.name + f"_v{v.defn.version}")
            return bind(base, **{k: m(v.bindings[k]) for k in v.defn.statics}) if base is not None else v
        if isinstance(v, tuple):
            return tuple(m(x) for x in v)
        if isinstance(v, dict):
            return {k: m(x) for k, x in v.items()}
        return v

    for fid in sys.argv[2:]:
        dec = dp.defs[fid]
        lib = m(dec)
        a = json.loads(canonical_json(_encode_definition(dec)))
        b = json.loads(canonical_json(_encode_definition(lib)))
        print("==", fid, "lib defn from", getattr(REGISTRY.defs.get(desc["definitions"][fid]["id"]), "body", None))
        print("  stored nodes", len(a["body"]["nodes"]), "library nodes", len(b["body"]["nodes"]))
        d = first_diff(a, b)
        print("  first diff:", d and (d[0], json.dumps(d[1])[:600], json.dumps(d[2])[:600]))
        sa = [n["fn"] for n in a["body"]["nodes"]]
        sb = [n["fn"] for n in b["body"]["nodes"]]
        print("  callees only in stored:", sorted(set(sa) - set(sb))[:10])
        print("  callees only in library:", sorted(set(sb) - set(sa))[:10])
    return 0


if __name__ == "__main__":
    sys.exit(main())
