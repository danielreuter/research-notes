"""vo_calls.py OUT_JSONL LABEL PROGRAM_DIR... [--map module:NAME]: `query.cross_call` (PR #98) over each request Program on its own, as
built or with a construction map's Definitions substituted (same Calls, same operands), and the Program's Call counts: every family,
the Calls that read only the weights parameter, and Gemma's `+ 1` (`AddScalarBf16_v1`) Calls.  One JSON line per Program, and a total."""
import json
import sys
import time
from collections import Counter

from verity.ir.defs import bind
from verity_vllm.query import call_scope as CS
from verity_vllm.query import cross_call as X
from verity_vllm.query.program_view import _read_instance_header, iter_instance_rows, spec_base

argv = sys.argv[1:]
maps: dict = {}
while "--map" in argv:
    k = argv.index("--map")
    mod, name = argv[k + 1].split(":")
    maps.update(getattr(__import__(mod, fromlist=[name]), name))
    del argv[k:k + 2]
out_path, label, dirs = argv[0], argv[1], argv[2:]


def specialize(family, statics):
    fn = maps.get(family)
    return bind(fn, **statics) if fn is not None else CS.specialization(family, statics)


memo: dict = {}
tot = Counter()
with open(out_path, "a") as out:
    for d in dirs:
        path = f"{d}/instances.json.gz"
        params = [n for n, _t in _read_instance_header(path)["params"]]
        W = params.index("weights") if "weights" in params else None
        fam, wonly, plus1 = Counter(), Counter(), 0
        for r in iter_instance_rows(path):
            f = spec_base(r["spec"])
            fam[f] += 1
            if W is not None and r["args"] and all(run[0] == "p" and run[1] == W for a in r["args"] for run in a):
                wonly[f] += 1
            plus1 += f == "AddScalarBf16_v1"
        t = time.time()
        res = X.check_program(path, strict=False, specialize=specialize if maps else CS.specialization, memo=memo)
        rec = {"label": label, "program": d, "map": sorted(maps) or None, "ok": res["ok"], "calls": res["calls"],
               "recomputed_gates": res["recomputed_gates"],
               "recomputes": [{k: a.get(k) for k in ("definition", "level", "calls", "gates")} for a in res["recomputes"]],
               "refined": res["refined"], "unrefined": res["unrefined"], "families": dict(fam), "weight_only_calls": dict(wonly),
               "plus_one_calls": plus1, "seconds": round(time.time() - t, 1)}
        out.write(json.dumps(rec, default=str) + "\n")
        out.flush()
        for k in ("calls", "recomputed_gates", "plus_one_calls"):
            tot[k] += rec[k]
        tot["recomputed_calls"] += sum(int(a.get("calls") or 0) for a in rec["recomputes"])
        tot["programs_not_ok"] += not rec["ok"]
        print(f"[calls {label}] {d.rsplit('/', 1)[-1]}: ok={rec['ok']} calls={rec['calls']} recomputed_gates={rec['recomputed_gates']} "
              f"+1 Calls={plus1} weight-only={sum(wonly.values())} ({rec['seconds']} s)", flush=True)
    out.write(json.dumps({"label": label, "total": dict(tot), "programs": len(dirs)}) + "\n")
print(f"CALLS {label}: {json.dumps(dict(tot))} over {len(dirs)} Programs", flush=True)
