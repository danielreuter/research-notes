"""s1c_interior.py BUILD_REQUEST_DIR...: per request Program (a Build's build_request dir), the Values the query of record (Q_word, S1 #232)
requires that the module-body population does not commit: `Population.interior` (family call_boundaries), by (Definition, module
leaf), with the Build's recorded correspondence.  The same measure as vllm-epoch-prep's s1_rows_cb.py.  Run it with S1's population
code on the path (a tree that has #232)."""
import json
import sys
from collections import Counter

from verity_vllm.correspondence.reader_for_query import Correspondence
from verity_vllm.query.program_view import from_instances
from verity_vllm.query.required import Population

for d in sys.argv[1:]:
    P = from_instances(f"{d}/instances.json.gz")
    corr = Correspondence.of(P, d)
    pop = Population(P, corr)
    by = Counter()
    for v in pop.interior:
        c = P.call(v.call)
        by[(c.definition.split("{")[0], corr.module_of(v.call).rsplit(".", 1)[-1])] += 1
    fams = Counter(c.definition.split("{")[0] for c in P.calls)
    print(json.dumps({"program": d, "digest": P.digest, "correspondence": corr.source, "calls": len(P.calls), "required": len(pop.required.values),
                      "interior": len(pop.interior), "interior_by_definition_module": [[k[0], k[1], n] for k, n in by.most_common(12)],
                      "families": {k: v for k, v in sorted(fams.items()) if k.startswith(("Gemm", "Bias"))}}))
