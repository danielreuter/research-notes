"""One summary line for a hash-commit run dir: timings, commitment evidence digest, statement-file digest, Rust verdict."""
import hashlib
import json
import sys
from pathlib import Path

d = Path(sys.argv[1])
r = json.loads((d / "result.json").read_text())
m = {x["name"]: x["value"] for x in r["measurements"]}
ev = json.loads((d / "commit-evidence.json").read_text()) if (d / "commit-evidence.json").exists() else {}
stmts = sorted((d / "proofs" / "rep1").glob("*.stmt"))
h = hashlib.sha256()
for p in stmts:
    h.update(p.name.encode() + b"\0" + hashlib.sha256(p.read_bytes()).digest())
rb = d / "proofs" / "rust_batch.json"
rust = "none"
if rb.exists():
    j = json.loads(rb.read_text())
    rust = f"{j.get('accepted')}/{j.get('n_accepted', j.get('accepted_count', '?'))}"
f = lambda k: f"{m[k]:.4f}" if k in m else "-"  # noqa: E731
print(f"t.total={f('t.total')} commit={f('commit.seconds')} cold={f('commit.cold_seconds')} e2e={f('e2e.seconds')} "
      f"committer={f('commit.committer_seconds')} rows={f('commit.rows_seconds')} trees={f('commit.trees_seconds')} chain={f('commit.chain_seconds')} host={f('commit.host_seconds')} "
      f"ev={ev.get('sha256', '-')[:16]} stmts={len(stmts)}:{h.hexdigest()[:16]} rust={rust} val={r['validation']['status']}")
