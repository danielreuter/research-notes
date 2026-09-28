"""strict_word.py ROW ROWDIR ROLE REPO REV [--world W] --out JSON: `word.check_query` strictly over a row's request Programs, before its Commit.

The row's manifest of record is rebuilt the way the row stages build it (`manifest build` at B=1, `build-global` at B>=2 and over the TP
ranks, with the row's tap policies) into a side file, with the word check named explicitly (`--word-check 16/32`: `word.check_query`
with strict=True, so the build fails naming every violation).  PASS needs all three:
  1. the rebuild exits 0 (no width, recompute or uncommitted-Call-boundary violation),
  2. its header, and ROWDIR/manifest.json's (the manifest the Commit binds), state the query of record and name the partition,
  3. its manifest digest equals ROWDIR/manifest.json's: the checked manifest is the one the Commit binds.
A raised gate limit (`VERITY_QWORD_MAX_GATES`, #101's sampler Call) reaches `--word-max-gates` through its environment variable.
Exit 0 PASS, 1 FAIL; the report (commands, per-request word lines, digests) goes to --out."""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time

from verity_vllm.pipeline import cli
from verity_vllm.pipeline import row_records as R

WORD = "16/32"
LINE = re.compile(r"Q_word_v1\{[^}]*\}: .*")


def command(row: str, d: str, role: str, repo: str, rev: str, world: int, out: str) -> list[str]:
    o = cli.parse("row", ["run", row, role, repo, rev])
    ck = o.commit
    wl = f"workloads/{row}.json"
    base = [sys.executable, "-m", "verity_vllm.pipeline.cli", "manifest"]
    tail = ["--word-check", WORD, "--out", out]
    if world > 1:
        ranks: list[str] = []
        for r in range(world):
            wd = R.tp_rank_workload_digest(f"{d}/build", r)
            if not wd:
                raise SystemExit(f"rank {r}: no GP-01 workload digest under {d}/build")
            ranks += ["--programs-root", f"{d}/build/rank{r}", "--rank", str(r), "--workload-digest", wd]
        return base + ["build-global", "--fixture", wl, *ranks, "--ranks", str(world), *R.tap_policy_flags(ck)] + tail
    policy = R.tap_policy_flags(ck) + (["--guarded-max"] if getattr(ck, "guarded_max_tap", "0") == "1" else [])
    if glob.glob(f"{d}/build_request_LP*_T*"):
        wd = R.workload_digest(d)
        return base + ["build-global", "--fixture", wl, "--programs-root", d, *(["--workload-digest", wd] if wd else []), *policy] + tail
    return base + ["build", "--program", f"{d}/build_request", "--workload", wl, *policy] + tail


def main() -> int:
    ap = argparse.ArgumentParser()
    for a in ("row", "rowdir", "role", "repo", "rev"):
        ap.add_argument(a)
    ap.add_argument("--world", type=int, default=1)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    from verity_vllm.query.required import QUERY_OF_RECORD
    side = os.path.join(os.path.dirname(os.path.abspath(a.out)), "strict_word.manifest.json")
    cmd = command(a.row, a.rowdir, a.role, a.repo, a.rev, a.world, side)
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    log = p.stdout + p.stderr
    with open(os.path.join(os.path.dirname(os.path.abspath(a.out)), "strict_word.build.log"), "w") as f:
        f.write(log)
    rep: dict = {"row": a.row, "word": WORD, "query_of_record": QUERY_OF_RECORD, "cmd": cmd[1:], "rc": p.returncode,
                 "wall_s": round(time.time() - t0, 1), "gate_limits": os.environ.get("VERITY_QWORD_MAX_GATES"),
                 "word_lines": LINE.findall(log)[:64], "problems": []}
    if p.returncode != 0:
        rep["problems"].append(f"the strict rebuild exited {p.returncode}: " + " | ".join(log.strip().splitlines()[-6:]))
    else:
        m = json.load(open(side))
        q = m.get("query") or {}
        rec = json.load(open(os.path.join(a.rowdir, "manifest.json")))
        rep.update(query_id=q.get("query_id"), partition=bool(q.get("partition")), manifest_digest=m.get("manifest_digest"),
                   commit_manifest_digest=rec.get("manifest_digest"), commit_query_id=(rec.get("query") or {}).get("query_id"))
        if q.get("query_id") != QUERY_OF_RECORD:
            rep["problems"].append(f"query {q.get('query_id')} is not the query of record {QUERY_OF_RECORD}")
        if not q.get("partition"):
            rep["problems"].append("the header names no partition (query.partition)")
        rq = rec.get("query") or {}
        if rq.get("query_id") != QUERY_OF_RECORD or not rq.get("partition"):
            rep["problems"].append(f"the Commit's manifest is built under {rq.get('query_id')}"
                                   f"{'' if rq.get('partition') else ', no partition'}: not the query of record")
        if m.get("manifest_digest") != rec.get("manifest_digest"):
            rep["problems"].append(f"manifest digest {str(m.get('manifest_digest'))[:16]} != the Commit's {str(rec.get('manifest_digest'))[:16]}")
        if not rep["word_lines"]:
            rep["problems"].append("no Q_word_v1 line in the rebuild's log: the word check did not run")
    rep["ok"] = not rep["problems"]
    json.dump(rep, open(a.out, "w"), indent=1)
    print(("PASS" if rep["ok"] else "FAIL") + f" {len(rep['word_lines'])} word lines, manifest {str(rep.get('manifest_digest'))[:16]}, "
          f"{rep['wall_s']} s" + ("" if rep["ok"] else ": " + "; ".join(rep["problems"])))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
