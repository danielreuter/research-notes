"""Row #70: this run's Commit (PAIRS=1) against the record's (3 pairs), leg by leg. Runs on the TP2 pod, stdlib only."""
import hashlib
import json
import sys
from pathlib import Path

ROW = "olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager"
RUN = Path("/workspace/cp/sweep") / ROW / "commit"
REC = Path("/workspace/regress/records") / ROW / "commit"


def load(p):
    return json.loads(p.read_text())


def short(v, n=220):
    s = json.dumps(v, sort_keys=True, default=str)
    return s if len(s) <= n else s[:n] + f"... ({len(s)} chars, sha256 {hashlib.sha256(s.encode()).hexdigest()[:16]})"


def leg(v):
    """The pass/ok word of a leg, whatever its shape."""
    if isinstance(v, dict):
        for k in ("pass", "ok", "passed", "status", "verdict"):
            if k in v:
                return {k: v[k]}
    return v


run, rec = load(RUN / "summary.json"), load(REC / "summary.json")
print("keys only in run:", sorted(set(run) - set(rec)))
print("keys only in record:", sorted(set(rec) - set(run)))
print()
for k in sorted(set(run) | set(rec)):
    a, b = run.get(k, "<absent>"), rec.get(k, "<absent>")
    same = a == b
    print(f"{'=' if same else '≠'} {k}: run {short(leg(a), 160)}")
    if not same:
        print(f"    record {short(leg(b), 160)}")

print("\n-- roots")
print("run tp_run_roots:", short(run.get("tp_run_roots"), 600))
print("rec tp_run_roots:", short(rec.get("tp_run_roots"), 600))
print("run per_rank_roots:", short(run.get("per_rank_roots"), 600))
print("rec per_rank_roots:", short(rec.get("per_rank_roots"), 600))

print("\n-- files present in both, byte-compared")
for p in sorted(RUN.iterdir()):
    q = REC / p.name
    if q.exists() and p.stat().st_size < 60_000_000:
        ha = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        hb = hashlib.sha256(q.read_bytes()).hexdigest()[:16]
        print(f"{'=' if ha == hb else '≠'} {p.name}: run {ha} record {hb} ({p.stat().st_size} / {q.stat().st_size} bytes)")
    elif not q.exists():
        print(f"  {p.name}: run only")

for name in ("xrank_collectives.json", "fold_match_binding.json", "sampled_replay.json", "weights_pin.json"):
    a, b = load(RUN / name), load(REC / name)
    print(f"\n-- {name}: top-level keys differing")
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            print(f"  {k}: run {short(a.get(k), 200)}\n      record {short(b.get(k), 200)}")
sys.exit(0)
