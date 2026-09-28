"""s1_rows_cb.py OUT.json ROW=ART[:tp]... : per row, the smallest request Program of its programs artifact (instances.json.gz only), and
the Values the query of record (Q_word) requires that the module-body population did not: `Population.interior` (family
call_boundaries), by (Definition, module leaf). The correspondence is the rows' recorded names (no result.json in these artifacts);
`:tp` marks a TP row (rank 0, world 2: TP-04's partials are protocol, not Call boundaries). Lane vllm-epoch-prep, S1 evidence."""
import json
import os
import subprocess
import sys
from collections import Counter

from verity_vllm.correspondence.reader_for_query import Correspondence
from verity_vllm.query.program_view import from_instances
from verity_vllm.query.required import Population

REPO = "/workspace"
MAX_BYTES = 200 << 20


def smallest(art: str) -> dict:
    r = subprocess.run([sys.executable, "-m", "research", "data", "fetch", art, "--list", "--json"], capture_output=True, text=True, cwd=REPO,
                       env=dict(os.environ, PYTHONPATH=f"{REPO}/tools/research/src"))
    if not r.stdout.strip():
        raise SystemExit(f"listing {art} failed: {r.stderr[-600:]}")
    files = [f for f in json.loads(r.stdout) if f["path"].endswith("instances.json.gz")]
    return min(files, key=lambda f: int(f["bytes"]))


def main() -> None:
    rows = []
    for spec in sys.argv[2:]:
        row, rest = spec.split("=", 1)
        tp = rest.endswith(":tp")
        art = rest.removesuffix(":tp")
        f = smallest(art)
        path = f["path"]
        if int(f["bytes"]) > MAX_BYTES:
            rows.append({"row": row, "art": art, "program": path, "skipped": f"{int(f['bytes']) >> 20} MB gz: too big for the VM"})
            print(f"#{row} skipped: its smallest Program {path} is {int(f['bytes']) >> 20} MB gz", flush=True)
            continue
        dest = f"/tmp/ab/rows/{row}"
        subprocess.run([sys.executable, "-m", "research", "data", "fetch", art, "--to", dest, "--path", path], capture_output=True, cwd=REPO,
                       env=dict(os.environ, PYTHONPATH=f"{REPO}/tools/research/src"), check=True)
        P = from_instances(os.path.join(dest, path))
        pop = Population(P, Correspondence(P), tp={"world": 2, "rank": 0} if tp else None)
        by = Counter()
        for v in pop.interior:
            c = P.call(v.call)
            by[(c.definition.split("{")[0], pop.corr.module_of(v.call).rsplit(".", 1)[-1])] += 1
        r = {"row": row, "art": art, "program": path, "calls": len(P.calls), "required": len(pop.required.values), "interior": len(pop.interior),
             "by_definition_module": [{"definition": d, "module": m, "values": n} for (d, m), n in by.most_common(20)]}
        rows.append(r)
        print(f"#{row} {path}: calls={r['calls']} required={r['required']} interior={r['interior']} {[(x['definition'], x['module'], x['values']) for x in r['by_definition_module'][:5]]}", flush=True)
    json.dump({"schema": "vllm-epoch-prep/s1-rows-call-boundaries/v1", "rows": rows}, open(sys.argv[1], "w"), indent=1)


if __name__ == "__main__":
    main()
