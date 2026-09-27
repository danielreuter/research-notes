"""cross_sub.py PROGRAM_DIR MAP [MAP ...]: query.cross_call (PR #98) over one request Program as recorded and with its Calls' Definitions
substituted by a construction map (module:NAME, e.g. verity_vllm.program.registry.fp8:SHARED_SCALE): same Calls, same operands."""
import copy
import gzip
import importlib
import json
import sys
import time

from verity_vllm.query import cross_call as X
from verity_vllm.query import word as W

path = sys.argv[1] + "/instances.json.gz"
doc = json.load(gzip.open(path))
maps = {}
for m in sys.argv[2:]:
    mod, name = m.split(":")
    maps.update(getattr(importlib.import_module(mod), name))


def specialize(family, statics):
    fn = maps.get(family)
    if fn is not None:
        from verity.ir.defs import bind
        return bind(fn, **statics)
    return W.specialization(family, statics)


for label, spec in (("recorded", W.specialization), ("substituted", specialize)):
    t = time.time()
    r = X.check_program(copy.deepcopy(doc), strict=False, specialize=spec)
    print(json.dumps({"program": sys.argv[1], "construction": label, "map": sys.argv[2:] if label == "substituted" else None, "ok": r["ok"],
                      "calls": r["calls"], "recomputed_gates": r["recomputed_gates"], "recomputes": r["recomputes"][:4],
                      "refined": r["refined"], "unrefined": r["unrefined"], "seconds": round(time.time() - t, 1)}, default=str), flush=True)
