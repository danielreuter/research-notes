"""vo_word.py OUT_JSONL LABEL JOBS PROGRAM_DIR... [--map module:NAME] [--only FAMILY[,FAMILY]]: the partition checker over one Build:
`Q_word_v1{X=16,W=32,R=no-recompute}` (`query.word.unit_rule`, PR #98's member check included) on EVERY distinct Definition
specialization the Programs call, each cut exactly (no interpolation between attention lengths), with its Call count summed over the
Programs.  `--map` substitutes a construction map's Definitions (same statics) before the cut.  Per specialization: violations (class,
codes, recomputed gates), units, gates, redundant gates, committed interior words; the Build's totals weight them by Calls.  JOBS worker
processes."""
import json
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

from verity_vllm.query.program_view import iter_instance_rows, spec_base, spec_statics

argv = sys.argv[1:]
MAPS: list[str] = []
ONLY: set[str] | None = None
while "--map" in argv:
    k = argv.index("--map")
    MAPS.append(argv[k + 1])
    del argv[k:k + 2]
if "--only" in argv:
    k = argv.index("--only")
    ONLY = set(argv[k + 1].split(","))
    del argv[k:k + 2]
out_path, label, jobs, dirs = argv[0], argv[1], int(argv[2]), argv[3:]


def _maps() -> dict:
    m: dict = {}
    for s in MAPS:
        mod, name = s.split(":")
        m.update(getattr(__import__(mod, fromlist=[name]), name))
    return m


def cut(spec: str) -> dict:
    from verity.ir.defs import bind
    from verity_vllm.query import word as W
    memo = cut.__dict__.setdefault("memo", {})
    maps = cut.__dict__.setdefault("maps", _maps())
    fam, st = spec_base(spec), spec_statics(spec)
    t = time.time()
    try:
        fn = bind(maps[fam], **st) if fam in maps else W.specialization(fam, st)
        r = W.unit_rule(fn, memo=memo)
    except Exception as e:  # noqa: BLE001 -- named in the record, never skipped
        return {"spec": spec, "error": f"{type(e).__name__}: {e}"[:400]}
    v = [{"class": a.get("class"), "codes": a.get("codes"), "recomputed": ((a.get("detail") or {}).get("gate-recomputed") or {}).get("n")}
         for a in r["violations"]]
    return {"spec": spec, "definition": fn.id, "substituted": fam in maps, "gates": r["gates"], "units": r["units_per_call"],
            "redundant_gates": r.get("redundant_gates"), "committed_interior_words": r["committed_interior_words"],
            "max_out_bits": r.get("max_out_bits"), "violations": v, "seconds": round(time.time() - t, 2)}


if __name__ == "__main__":
    calls: Counter = Counter()
    for d in dirs:
        for r in iter_instance_rows(f"{d}/instances.json.gz"):
            if ONLY is None or spec_base(r["spec"]) in ONLY:
                calls[r["spec"]] += 1
    specs = sorted(calls, key=lambda s: (spec_base(s), -calls[s]))
    print(f"[word {label}] {len(specs)} distinct specializations, {sum(calls.values())} Calls over {len(dirs)} Programs", flush=True)
    tot, viol, fams, errors = Counter(), Counter(), Counter(), 0
    t0 = time.time()
    with open(out_path, "a") as out, ProcessPoolExecutor(max_workers=jobs) as pool:
        for i, rec in enumerate(pool.map(cut, specs, chunksize=4)):
            n = calls[rec["spec"]]
            rec.update(label=label, calls=n)
            out.write(json.dumps(rec, default=str) + "\n")
            if "error" in rec:
                errors += 1
                print(f"[word {label}] ERROR {rec['spec'][:120]}: {rec['error'][:200]}", flush=True)
                continue
            fams[spec_base(rec["spec"])] += n
            tot["calls"] += n
            for k in ("gates", "units", "committed_interior_words"):
                tot[k] += int(rec[k] or 0) * n
            tot["redundant_gates"] += int(rec["redundant_gates"] or 0) * n
            tot["violations"] += len(rec["violations"]) * n
            tot["recomputed_gates"] += sum(int(v["recomputed"] or 0) for v in rec["violations"]) * n
            for v in rec["violations"]:
                viol[f"{v['class']}:{','.join(v['codes'] or [])}"] += n
            if (i + 1) % 200 == 0:
                print(f"[word {label}] {i + 1}/{len(specs)} ({round(time.time() - t0)} s)", flush=True)
        summary = {"label": label, "query": "Q_word_v1{X=16,W=32,R=no-recompute}", "maps": MAPS or None, "only": sorted(ONLY) if ONLY else None,
                   "programs": dirs, "specializations": len(specs), "errors": errors, "totals": dict(tot), "violations_by_class": dict(viol),
                   "calls_by_family": dict(fams), "seconds": round(time.time() - t0)}
        out.write(json.dumps({"summary": summary}) + "\n")
    print(f"WORD {label}: {json.dumps({k: summary[k] for k in ('specializations', 'errors', 'totals', 'violations_by_class')})}", flush=True)
