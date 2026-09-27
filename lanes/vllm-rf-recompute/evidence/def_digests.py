"""def_digests.py OUT INSTANCES...: the descriptor digest of every Definition specialization the given request Programs call, with its
transitive closure (the `definitions` entries `encode_program` would write for it): sha256 of the canonical JSON.  Run on two trees and
compare: equal digests for every called Definition and an unchanged frontend are the same Program descriptors, so the same
program_digest."""
import hashlib
import json
import sys

from verity.ir.codec import _as_specialized, _encode_definition, _spec_id, _static_functions, canonical_json
from verity.ir.defs import PrimitiveDefinition
from verity_vllm.query import program_view as PV
from verity_vllm.query import word as W


def closure(fn) -> dict:
    defs: dict = {}

    def visit(f) -> None:
        fid = _spec_id(f)
        if fid in defs:
            return
        defs[fid] = None
        if not isinstance(f, PrimitiveDefinition):
            for n in f.body.nodes:
                visit(n.fn)
            for k in f.defn.statics:
                for g in _static_functions(f.bindings[k]):
                    visit(_as_specialized(g, fid))
        defs[fid] = _encode_definition(f)

    visit(fn)
    return defs


out = {}
for path in sys.argv[2:]:
    P = PV.from_instances(path)
    for c in P.calls:
        if c.definition in out:
            continue
        fn = W.specialization(c.family, c.statics)
        assert _spec_id(fn) == c.definition, (_spec_id(fn), c.definition)
        out[c.definition] = hashlib.sha256(canonical_json(closure(fn))).hexdigest()
json.dump(dict(sorted(out.items())), open(sys.argv[1], "w"), indent=1)
print(len(out), "definitions;", hashlib.sha256(canonical_json(out)).hexdigest())
