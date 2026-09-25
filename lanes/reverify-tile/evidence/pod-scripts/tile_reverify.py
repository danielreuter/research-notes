"""reverify-tile: reverify.verify_tree (custody, system pin, commitment recomputation incl. the tile, Rust `batch` pinned
with --system-h) on each dump dir given, as `reverify.py` runs it after fetching; then commitment_problems on the same
dump under three manifests it must refuse: set.tile removed, set.tile with another seed, and the pre-set.tile shape (no
tile, the unshared set's digest: what the shared-local cells' manifests carry).  Writes $OUT (JSON); exit 1 unless the
honest dumps PASS and every negative is refused."""
import json
import os
import sys
import time
from pathlib import Path

from backends.direct.ligero.relations import relation
from backends.direct.ligero.relchain import instances_digest
from backends.direct.ligero.reverify import Report, Verifier, _sha256, commitment_problems, verify_tree

exe = Path(os.environ["LIGERO_VERIFY"])
v = Verifier(exe, _sha256(exe), os.environ.get("VERIFIER_COMMIT") or None)
jobs = int(os.environ.get("JOBS", "8"))
rows, bad = [], 0
for d in map(Path, sys.argv[1:]):
    man = json.loads((d / "manifest.json").read_text())
    reps = sorted(p.name for p in d.iterdir() if p.is_dir() and p.name.startswith("rep"))
    rep = Report(str(d))
    t0 = time.time()
    verify_tree(d, man, v, rep, jobs=jobs, params={}, asserted=None, out_dir=d.parent / f"{d.name}.reps")
    row = {"dump": str(d), "status": rep.status, "why": rep.why, "relation": rep.relation, "hashed": rep.hashed, "tile": rep.tile,
           "custody": rep.custody, "seconds": round(time.time() - t0, 1), "set": man.get("set"),
           "reps": {r: {k: x.get(k) for k in ("n", "accepted", "rejected", "batch_accepted", "batch_reason", "batch_bits", "system_pinned",
                                              "python_agree", "python_disagree", "verify_seconds_sum")} for r, x in rep.reps.items()}}
    bad += rep.status != "PASS"
    s = man["set"]
    rel = relation(man["relation"]["name"] if isinstance(man["relation"], dict) else man["relation"])
    no_tile = {k: x for k, x in s.items() if k != "tile"}
    negs = {"no set.tile": dict(man, set=no_tile),
            "set.tile other seed": dict(man, set=dict(s, tile=dict(s["tile"], seed=s["tile"]["seed"] + 1))),
            "pre-set.tile manifest (unshared digest)": dict(man, set=dict(no_tile, instances=instances_digest(rel, s["total_vus"])))}
    row["negatives"] = {}
    for name, m in negs.items():
        hashed, probs = commitment_problems(d, m, rep.relation, reps, procs=jobs)
        row["negatives"][name] = {"refused": bool(probs), "problems": probs}
        bad += not probs
    print(json.dumps(row), flush=True)
    rows.append(row)
Path(os.environ.get("OUT", "tile_reverify.json")).write_text(json.dumps(rows, indent=1) + "\n")
print(f"{sum(r['status'] == 'PASS' for r in rows)}/{len(rows)} dumps PASS; {bad} unexpected outcome(s)")
sys.exit(1 if bad else 0)
