#!/usr/bin/env python3
"""verifier-cost: re-verify each A-GKR Table 2 cell's proofs on this CPU host and register a verification-verdict/v1 per cell.

    python3 04-agkr-verify.py VERIFIER COMMIT        (run by 04-agkr-verify.sh; needs RESEARCH_STORE[_CONFIG] + an R2 credential)

Per cell: `research data fetch <run_files> --to W/agkr/<cell>`; every proofs/rep*.bin verified 3x at --threads = nproc and 1x at
--threads 1; verifier CPU s = rusage user+sys of the child (the process's own CPU, all threads); verify.cpu_s = the median over the
nproc-thread runs.  Writes OUT/agkr-<cell>/ (per-run json + summary.json) and registers it as the verdict's payload tree.
"""
import json
import os
import platform
import resource
import statistics
import subprocess
import sys
import time
from pathlib import Path

VERIFIER, COMMIT = sys.argv[1], sys.argv[2]
W = Path("/workspace/verifier-cost")
OUT = Path(os.environ.get("RESEARCH_RUN_DIR", "."))
CELLS = {  # Table 2 cell art -> (label, its run_files art)
    "art:300a526a9ed8ac4f4677176b3ad48ce181d10ef8058b98eb9c018776aa018405":
        ("A100 BF16 · A-GKR", "art:e201b726a21d4fa55c1466becfbc73ac2a6a96cc19548132fdc1b3663545f016"),
    "art:c09947fd5184047d90bc24ec87bbb37ba1215a92cabed467e7647a6ff7f8804f":
        ("H100 BF16 · A-GKR", "art:c00624fa2727b5092fbf60155ee6d209dda11c80b25ad9b9c4e6ddfca50365fc"),
}
NPROC = os.cpu_count() or 1
CPU = next((ln.split(":", 1)[1].strip() for ln in open("/proc/cpuinfo") if ln.startswith("model name")), platform.processor())


def research(*args):
    r = subprocess.run([sys.executable, "-m", "research", "data", *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"research data {args[0]} rc={r.returncode}: {r.stderr[-800:]}")
    return r.stdout


def verify(stmt, proof, threads, js):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.perf_counter()
    p = subprocess.run([VERIFIER, "verify", "--dir", str(stmt), "--proof", str(proof), "--vus", "4096", "--threads", str(threads),
                        "--json", str(js)], capture_output=True, text=True)
    wall = time.perf_counter() - t0
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    out = json.loads(js.read_text()) if js.exists() else {}
    return {"proof": proof.name, "threads": threads, "rc": p.returncode, "accepted": bool(out.get("accepted")) and p.returncode == 0,
            "cpu_s": (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime), "wall_s": wall,
            "verify_seconds": out.get("verify_seconds"), "peak_rss_bytes": out.get("peak_rss_bytes"), "error": out.get("error"),
            "stderr_tail": p.stderr[-400:], "json": js.name}


registered = {}
for cell, (label, rf) in CELLS.items():
    tag = cell[4:12]
    d = W / "agkr" / tag
    d.mkdir(parents=True, exist_ok=True)
    research("fetch", rf, "--to", str(d))
    stmt = next(p.parent for p in d.rglob("manifest.json") if p.parent.name == "statement")
    proofs = sorted(stmt.parent.glob("proofs/rep*.bin"))
    o = OUT / f"agkr-{tag}"
    o.mkdir(exist_ok=True)
    runs = []
    for proof in proofs:
        for i in range(3):
            runs.append(verify(stmt, proof, NPROC, o / f"{proof.stem}-t{NPROC}-{i}.json"))
        runs.append(verify(stmt, proof, 1, o / f"{proof.stem}-t1.json"))
    many = [r for r in runs if r["threads"] == NPROC]
    one = [r for r in runs if r["threads"] == 1]
    ok = bool(runs) and all(r["accepted"] for r in runs)
    cpu, wall = statistics.median(r["cpu_s"] for r in many), statistics.median(r["wall_s"] for r in many)
    cpu1 = statistics.median(r["cpu_s"] for r in one)
    summary = {"cell": cell, "label": label, "run_files": rf, "accepted": ok, "n_runs": len(runs), "proofs": [p.name for p in proofs],
               "threads": NPROC, "verify_cpu_s_median": cpu, "verify_wall_s_median": wall, "verify_cpu_s_threads1_median": cpu1,
               "host_cpu": CPU, "nproc": NPROC, "runs": runs}
    (o / "summary.json").write_text(json.dumps(summary, indent=1))
    meta = {"result": "PASS" if ok else "FAIL", "lane": "verifier-cost", "label": f"verifier-cost A-GKR re-verification {label}",
            "verifier": f"verity-gkr-verify (backends/gkr/verifier @ {COMMIT}, independent Rust)",
            "detail": (f"{len(runs)} verifications of the cell's {len(proofs)} proof file(s), all {'accepted' if ok else 'NOT accepted'}; "
                       f"verifier CPU s = rusage user+sys of the verifier process; median {cpu:.3f} CPU-s / {wall:.3f} s wall at --threads "
                       f"{NPROC}, {cpu1:.3f} CPU-s at --threads 1; host {CPU}, {NPROC} vCPU, RunPod EU-RO-1 (vy-live2b-verifier-ro). "
                       "Offline: A-GKR has no live protocol (coins = SHA-256(transcript)), so no live tax."),
            "cell": cell, "cell_label": label, "host_cpu": CPU, "nproc": NPROC, "pod": "vy-live2b-verifier-ro pitmqu0zrycw5i EU-RO-1",
            "measurements": [{"name": "verify.cpu_s", "unit": "s", "value": cpu}, {"name": "verify.wall_s", "unit": "s", "value": wall},
                             {"name": "verify.cpu_s_threads1", "unit": "s", "value": cpu1}]}
    mf = o / "verdict-meta.json"
    mf.write_text(json.dumps(meta))
    put = json.loads(research("put", "--kind", "verification-verdict/v1", "--tree", str(o), "--meta", f"@{mf}",
                              "--ref", f"result={cell}", "--ref", f"proof={rf}", "--preserve", "--json"))
    registered[label] = {"verdict": put["id"], "preserved": (put.get("preserve") or {}).get("preserved"), "accepted": ok,
                         "verify_cpu_s": cpu, "verify_wall_s": wall, "verify_cpu_s_threads1": cpu1}
    print(label, json.dumps(registered[label]), flush=True)
(OUT / "registered.json").write_text(json.dumps(registered, indent=1))
