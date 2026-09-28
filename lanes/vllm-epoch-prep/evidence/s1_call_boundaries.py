"""s1_call_boundaries.py OUT.json PROGRAM_DIR... : for each stored request Program (a Build dir with instances.json.gz, result.json), the
Call-level boundaries today's population (Q_module_body_v1 + policy) doesn't commit: `word.check_query` non-strict, violations of class
input-not-committed / output-not-committed by (Definition, module), and the Values a Call-granular population would add (every Value one
Call produces and another reads, minus literals, not already required). Lane vllm-epoch-prep, S1 evidence."""
import json
import os
import sys
import time
from collections import Counter

from verity.proofs.query import boundary, partition_by
from verity_vllm.correspondence.reader_for_query import Correspondence
from verity_vllm.pipeline.manifest import word_check
from verity_vllm.query.module_body import literal_calls, without_literals
from verity_vllm.query.program_view import from_instances
from verity_vllm.query.required import request_manifest
try:
    from verity_vllm.query.required import Q_MODULE_BODY_ID
    BASE = {"query": Q_MODULE_BODY_ID}          # S1 on the tree: compare against the module-body population explicitly
except ImportError:
    BASE = {}


def one(d: str) -> dict:
    t = time.time()
    P = from_instances(os.path.join(d, "instances.json.gz"))
    res = json.load(open(os.path.join(d, "result.json")))
    art = json.load(open(os.path.join(d, "artifact.json"))) if os.path.exists(os.path.join(d, "artifact.json")) else None
    corr = Correspondence.of(P, d, implementation_paths=Correspondence.implementation_paths_of(res))
    r = request_manifest(P, corr, res, artifact=art, program_dir=d, **BASE)
    w = word_check(P, corr, r.required, "16/32", strict=False)
    lit = literal_calls(P)
    Bc = without_literals(boundary(P, partition_by(lambda c: c.id)), lit)
    extra = Bc.values - r.required.values
    by = Counter()
    for v in extra:
        c = P.call(v.call) if v.call >= 0 else None
        by[(c.definition if c else "input", corr.module_of(v.call) if c else "")] += 1
    viol = [{k: x[k] for k in ("definition", "class", "calls", "where")} for x in w["violations"]]
    return {"dir": d, "program": (res.get("program") or {}).get("digest"), "calls": len(P.calls), "identities": r.manifest["populations"]["identities"],
            "required_values": len(r.required.values), "call_boundary_values": len(Bc.values), "extra_values": len(extra),
            "extra_by_definition_module": [{"definition": k[0], "module": k[1], "values": n} for k, n in by.most_common(40)],
            "violations": viol, "secs": round(time.time() - t, 1)}


def main() -> None:
    out = sys.argv[1]
    rows = []
    for d in sys.argv[2:]:
        row = one(d)
        rows.append(row)
        print(f"{d}: calls={row['calls']} required={row['required_values']} call_boundary={row['call_boundary_values']} extra={row['extra_values']} "
              f"violations={[(v['definition'][:40], v['class'], v['calls']) for v in row['violations'][:8]]} {row['secs']}s", flush=True)
    json.dump({"schema": "vllm-epoch-prep/s1-call-boundaries/v1", "rows": rows}, open(out, "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
