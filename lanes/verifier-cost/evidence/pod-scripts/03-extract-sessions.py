#!/usr/bin/env python3
"""verifier-cost (pod vy-live2b-verifier-ro): what the 2026-09-23 live session store already measures, per session.

    research run --on vy-live2b-verifier-ro --project verity --send 03-extract-sessions.py -- python3 inputs/03-extract-sessions.py

Reads /workspace/live/sessions (JSON records + file sizes only); writes sessions.jsonl and groups.tsv to the run dir.
Per `s…` (Ligero sub-batch) session: hello (relation, l = batch, VUs, window, lane, run_id, prover DC), verdict (verifier DC,
commit, batch cpu_s / wall_s at --jobs), bytes prover -> verifier (stmt + root + tests + proof per sub-batch) and verifier ->
prover (coins files + commitment), rounds per sub-batch, session wall. Per `c…` (Ligerito challenge stream): index line.
"""
import json
import os
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

S = Path("/workspace/live/sessions")
OUT = Path(os.environ.get("RESEARCH_RUN_DIR", "."))


def load(p):
    try:
        return json.loads(p.read_text())
    except Exception as e:  # noqa: BLE001
        return {"_error": f"{type(e).__name__}: {e}"}


rows = []
for d in sorted(p for p in S.iterdir() if p.is_dir()):
    h, v = load(d / "hello.json"), load(d / "verdict.json") if (d / "verdict.json").exists() else {}
    r = {"session": d.name, "proto": "ligero" if d.name.startswith("s") else "challenge-stream",
         "relation": h.get("relation"), "l": h.get("batch"), "total_vus": h.get("total_vus"), "window": h.get("window"),
         "n_proofs": h.get("n_proofs"), "rep": h.get("rep"), "lane": h.get("lane"), "run_id": h.get("run_id"),
         "prover_dc": h.get("prover_dc"), "prover_commit": (h.get("prover_commit") or "")[:10], "zk": h.get("zk"),
         "mode": h.get("mode"), "target_bits": h.get("target_bits"), "accepted": v.get("accepted"),
         "verifier": v.get("verifier"), "verifier_dc": v.get("verifier_dc"), "recorded": (d / "session.json").exists()}
    b = v.get("batch") or {}
    r.update(verify_cpu_s=b.get("cpu_s"), verify_wall_s=b.get("wall_s"), verify_sum_s=None, batch_bits=None, jobs=None)
    rb = load(d / "rust_batch.json") if (d / "rust_batch.json").exists() else {}
    r.update(verify_sum_s=rb.get("verify_seconds_sum"), batch_bits=rb.get("batch_bits"), jobs=rb.get("jobs"))
    if r["proto"] == "ligero" and r["recorded"]:
        s = load(d / "session.json")
        subs = s.get("subbatches") or []
        up = sum((x.get("bytes_stmt") or 0) + (x.get("bytes_root") or 0) + (x.get("bytes_tests") or 0) + (x.get("bytes_proof") or 0)
                 for x in subs)
        coins = sum(f.stat().st_size for f in d.glob("sub_*.coins"))
        t0 = min((x.get("t_commit_sent") for x in subs if x.get("t_commit_sent")), default=None)
        t1 = max((x.get("t_proof_recv") for x in subs if x.get("t_proof_recv")), default=None)
        r.update(subbatches=len(subs), bytes_up=up, bytes_proof=sum(x.get("bytes_proof") or 0 for x in subs),
                 bytes_stmt=sum(x.get("bytes_stmt") or 0 for x in subs), coins_file_bytes=coins,
                 session_wall_s=(t1 - t0) if t0 and t1 else None,
                 wire_rounds_per_sub=3, proof_file_bytes=sum(f.stat().st_size for f in d.glob("sub_*.proof")))
    rows.append(r)

with open(OUT / "sessions.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
idx = [json.loads(line) for line in (S / "index.jsonl").read_text().splitlines() if line.strip()]
with open(OUT / "index-copy.jsonl", "w") as f:
    f.write("\n".join(json.dumps(x) for x in idx) + "\n")

g = defaultdict(list)
for r in rows:
    g[(r["proto"], r["relation"], r["l"], r["total_vus"], r["window"], r["lane"], r["prover_dc"], r["verifier_dc"], r["prover_commit"])].append(r)


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 3) if xs else None


cols = ["proto", "relation", "l", "vus", "window", "lane", "prover_dc", "verifier_dc", "prover_commit", "n", "accepted",
        "subbatches", "verify_cpu_s_med", "verify_cpu_s_min", "verify_cpu_s_max", "verify_wall_s_med", "jobs", "bytes_up_med",
        "bytes_proof_med", "coins_bytes_med", "session_wall_s_med", "batch_bits", "sessions"]
with open(OUT / "groups.tsv", "w") as f:
    f.write("\t".join(cols) + "\n")
    for k, rs in sorted(g.items(), key=lambda kv: str(kv[0])):
        cpu = [r["verify_cpu_s"] for r in rs if r["verify_cpu_s"] is not None]
        line = [*k, len(rs), sum(1 for r in rs if r["accepted"]), med(r.get("subbatches") for r in rs), med(cpu),
                min(cpu) if cpu else None, max(cpu) if cpu else None, med(r["verify_wall_s"] for r in rs),
                med(r["jobs"] for r in rs), med(r.get("bytes_up") for r in rs), med(r.get("bytes_proof") for r in rs),
                med(r.get("coins_file_bytes") for r in rs), med(r.get("session_wall_s") for r in rs),
                med(r["batch_bits"] for r in rs), " ".join(r["session"] for r in rs)]
        f.write("\t".join("" if x is None else str(x) for x in line) + "\n")
print((OUT / "groups.tsv").read_text())
sys.exit(0)
