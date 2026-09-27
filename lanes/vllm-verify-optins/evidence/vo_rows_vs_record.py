"""vo_rows_vs_record.py OUT_JSON RECORD_DIR BUILD_DIR SHAPE...: a Build's request Programs against the recorded ones, row for row.  The
recorded Program digests cannot be reproduced by the current tree (the Program id's SRC static names the wrapper class, whose module
moved after the record), so equality is shown on what the digest covers: the params (names and types) and every Call's Definition
spec, form, name and argument runs, in order.  Streams both instance sequences (`program_view.iter_instance_rows`)."""
import json
import sys
from itertools import zip_longest

from verity_vllm.query.program_view import _read_instance_header, iter_instance_rows

out, rec_dir, build_dir, shapes = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
res = {}
for s in shapes:
    a, b = f"{rec_dir}/{s}/instances.json.gz", f"{build_dir}/{s}/instances.json.gz"
    ha, hb = _read_instance_header(a), _read_instance_header(b)
    n = diff = 0
    first = None
    for ra, rb in zip_longest(iter_instance_rows(a), iter_instance_rows(b)):
        n += 1
        if ra != rb:
            diff += 1
            if first is None:
                first = {"i": n - 1, "record": str(ra)[:300], "build": str(rb)[:300]}
    res[s] = {"rows": n, "rows_differing": diff, "params_equal": ha["params"] == hb["params"], "first_difference": first,
              "record_digest": ha.get("digest"), "build_digest": hb.get("digest")}
    print(f"[rows] {s}: {n} rows, {diff} differ, params equal {res[s]['params_equal']}", flush=True)
res["all_equal"] = all(v["rows_differing"] == 0 and v["params_equal"] for v in res.values() if isinstance(v, dict))
json.dump(res, open(out, "w"), indent=1)
print(f"ROWS-VS-RECORD all_equal={res['all_equal']} over {len(shapes)} Programs", flush=True)
