"""s1_prefix_cb.py OUT.json N ROW=instances.json.gz... : Q_word's Call boundaries a module-body population does not commit, on the first N
rows of a request Program's instance sequence (streamed with ijson, so a multi-GB Program of one request fits: the first rows already
run every layer). Extra = Values crossing Calls but not module bodies, minus literals and fused-MoE plane rows (`format.moe_plane_kind`);
TENSOR-RETURN is not applied (it only makes Values required anyway, so the count is an upper bound). Lane vllm-epoch-prep, S1 evidence."""
import gzip
import json
import sys
from collections import Counter

import ijson

from verity.proofs.query import boundary, partition_by
from verity_vllm.correspondence.reader_for_query import Correspondence
from verity_vllm.query.manifest.format import moe_plane_kind
from verity_vllm.query.module_body import literal_calls, module_body_boundary, without_literals
from verity_vllm.query.program_view import from_instances


def _first(path: str, key: str):
    with gzip.open(path, "rb") as f:
        return next(ijson.items(f, key, use_float=True))


def prefix(path: str, n: int) -> dict:
    rows = []
    with gzip.open(path, "rb") as f:
        for r in ijson.items(f, "rows.item", use_float=True):
            rows.append(r)
            if len(rows) >= n:
                break
    return {**{k: _first(path, k) for k in ("schema", "digest", "params")}, "rows": rows}


def main() -> None:
    out, n = sys.argv[1], int(sys.argv[2])
    res = []
    for spec in sys.argv[3:]:
        row, path = spec.split("=", 1)
        inst = prefix(path, n)
        P = from_instances(inst)
        corr = Correspondence(P)
        lit = literal_calls(P)
        bc = without_literals(boundary(P, partition_by(lambda c: c.id)), lit).values
        bm = module_body_boundary(P, corr, lit).values
        extra = [v for v in bc - bm if v.call >= 0 and moe_plane_kind(P.call(v.call).family, corr.module_of(v.call)) is None]
        by = Counter((P.call(v.call).family, corr.module_of(v.call).rsplit(".", 1)[-1]) for v in extra)
        last = inst["rows"][-1]["name"] if inst["rows"] else None
        r = {"row": row, "rows_read": len(inst["rows"]), "last_row": last, "extra": len(extra),
             "by_definition_module": [{"definition": d, "module": m, "values": k} for (d, m), k in by.most_common(12)]}
        res.append(r)
        print(f"#{row}: {len(inst['rows'])} rows (to {last}) extra={len(extra)} {[(x['definition'], x['module'], x['values']) for x in r['by_definition_module'][:6]]}", flush=True)
    json.dump({"schema": "vllm-epoch-prep/s1-prefix-call-boundaries/v1", "rows_per_program": n, "rows": res}, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
