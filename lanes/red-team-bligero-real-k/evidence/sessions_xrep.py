"""red-team-bligero-real-k: every timed rep of a cell proved the same statements (the live verifier drops the files).

For each cell (bench.cell result): its 5 live sessions (validation.evidence.live_verifier.per_rep), read from the verifier
run's preserved record (sessions/<sid>/session.json); per sub-batch index the statement sha256 must be the same in every
session (so the rep-1 statements that file re-verification bound to the input set are the statements every timed rep
proved), each proof distinct (fresh verifier coins), every live check and Rust verdict accepted, n_proofs sub-batches.

  python sessions_xrep.py OUT CELL:VERIFIER_RUN ...
"""
import json, subprocess, sys
from pathlib import Path

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)


def research(*a):
    r = subprocess.run(["research", *a], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"research {' '.join(a)}: {r.stderr[-300:]}")
    return r.stdout


rows, bad = [], []
for spec in sys.argv[2:]:
    cell, vrun = spec.split(":")
    meta = json.loads(research("data", "show", f"art:{cell}", "--json"))["manifest"]["meta"]
    lv = meta["validation"]["evidence"]["live_verifier"]
    sids = [p["session_id"] for p in lv["per_rep"]]
    n_proofs = meta["workload_fingerprint"]["N_subbatches"]
    att = json.loads(research("data", "show", vrun, "--json"))
    rec = att["outputs"]["run_record"]
    d = out / f"rec-{vrun}"
    args = ["data", "fetch", rec, "--to", str(d)]
    for s in sids:
        args += ["--path", f"sessions/{s}/session.json"]
    research(*args)
    per_sub: dict[int, list] = {}
    problems = []
    for s in sids:
        f = next(d.rglob(f"sessions/{s}/session.json"), None)
        if f is None:
            problems.append(f"{s}: no session.json in {rec}")
            continue
        js = json.loads(f.read_text())
        v = js["verdict"]
        if not v.get("accepted") or v.get("n_proofs") != n_proofs:
            problems.append(f"{s}: verdict {v.get('accepted')} n_proofs {v.get('n_proofs')}")
        for sb in js["subbatches"]:
            per_sub.setdefault(sb["sub"], []).append(sb)
            if not (sb.get("live_check") or {}).get("accepted") or not (sb.get("verdict") or {}).get("accepted"):
                problems.append(f"{s} sub {sb['sub']}: live {sb.get('live_check')} verdict {(sb.get('verdict') or {}).get('accepted')}")
    if sorted(per_sub) != list(range(n_proofs)):
        problems.append(f"sub-batch indices {sorted(per_sub)[:5]}... not [0, {n_proofs})")
    same_stmt = all(len({sb["stmt_sha256"] for sb in v}) == 1 and len(v) == len(sids) for v in per_sub.values())
    distinct_proofs = all(len({sb["proof_sha256"] for sb in v}) == len(v) for v in per_sub.values())
    if not same_stmt:
        problems.append("a sub-batch's statement differs between sessions")
    if not distinct_proofs:
        problems.append("a proof repeats between sessions (coins not fresh?)")
    row = {"cell": cell, "verifier_run": vrun, "record": rec, "sessions": sids, "n_proofs": n_proofs,
           "same_statement_every_rep": same_stmt, "distinct_proofs": distinct_proofs,
           "rep1_stmt_sha256": {i: v[0]["stmt_sha256"] for i, v in sorted(per_sub.items())}, "problems": problems}
    rows.append(row)
    print(cell, vrun, "OK" if not problems else f"PROBLEMS {problems[:3]}", flush=True)
    if problems:
        bad.append(cell)
(out / "sessions-xrep.json").write_text(json.dumps({"ok": not bad, "bad": bad, "cells": rows}, indent=1))
print(f"{len(rows) - len(bad)}/{len(rows)} cells: every rep proved the rep-1 statements")
sys.exit(0 if not bad else 1)
