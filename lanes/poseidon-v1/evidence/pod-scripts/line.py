"""One summary line for a poseidon-v1 run dir: P, timings, contention, commitment evidence digest, statement digest, Rust verdict.
python line.py DIR [--json]   (--json: the sweep point as one JSON object)"""
import hashlib
import json
import sys
from pathlib import Path

d = Path(sys.argv[1])
r = json.loads((d / "result.json").read_text())
m = {x["name"]: x["value"] for x in r["measurements"]}
fp = r.get("workload_fingerprint") or {}
ev = json.loads((d / "commit-evidence.json").read_text()) if (d / "commit-evidence.json").exists() else {}
stmts = sorted((d / "proofs" / "rep1").glob("*.stmt"))
h = hashlib.sha256()
for p in stmts:
    h.update(p.name.encode() + b"\0" + hashlib.sha256(p.read_bytes()).digest())
rb = d / "proofs" / "rust_batch.json"
rust = None
if rb.exists():
    j = json.loads(rb.read_text())
    rust = j.get("accepted")
cont = r.get("contention") or {}
n = fp.get("B")
e2e = m.get("e2e.seconds")
pt = {"tag": d.name, "n": n, "t_total": m.get("t.total"), "commit": m.get("commit.seconds"), "commit_cold": m.get("commit.cold_seconds"),
      "commit_reps": m.get("commit.reps"), "e2e": e2e, "P": (n / e2e) if (n and e2e) else None,
      "P_proving_only": (n / m["t.total"]) if (n and m.get("t.total")) else None,
      "contended": cont.get("contended"), "contention_reasons": cont.get("reasons"), "reps": len((r.get("validation") or {}).get("evidence", {}).get("reps", []) or []),
      "evidence_sha256": ev.get("sha256"), "stmts": f"{len(stmts)}:{h.hexdigest()}", "rust_accepted": rust,
      "validation": (r.get("validation") or {}).get("status"), "run_id": (d / "run_id").read_text().strip() if (d / "run_id").exists() else None}
if "--json" in sys.argv:
    print(json.dumps(pt))
else:
    f = lambda k: f"{pt[k]:.4f}" if isinstance(pt[k], (int, float)) and pt[k] is not None else str(pt[k])  # noqa: E731
    print(f"n={n} P={f('P')} e2e={f('e2e')} t.total={f('t_total')} commit={f('commit')} cold={f('commit_cold')} "
          f"contended={pt['contended']} reps={pt['reps']} ev={str(pt['evidence_sha256'])[:16]} stmts={pt['stmts'][:24]} "
          f"rust={rust} val={pt['validation']}")
