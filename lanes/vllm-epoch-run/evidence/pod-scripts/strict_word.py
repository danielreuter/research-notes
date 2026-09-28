"""strict_word.py ROW ROWDIR ROLE REPO REV [--world W] --out JSON: the strict word check before a row's Commit, from the Build's own files.

The Build's manifest step already ran `word.check_query` strictly (`manifest build` / `build-global`, default `--word-check 16/32`): a
violation raises before `manifest.json` is written and fails the Build, and manifest-verify inside the Commit re-derives the digest.  So
this reads what that step left (prep lane 16:03Z) instead of running it a second time.  PASS needs all of:
  1. ROWDIR/manifest.json states `Q_word_v1{X=16,W=32,R=no-recompute}` (the query of record) with a `query.partition`, and
     `call_boundaries` is not among its required families;
  2. ROWDIR/manifest.log has one `Q_word_v1{X=16,W=32,...}: N calls -> U units over G gates` line per component (the workload's requests
     x the TP world), and no traceback or query-rule violation;
  3. the Build ran with the record's word check: `VERITY_WORD_CHECK` unset (or 16/32), and `VERITY_QWORD_MAX_GATES` unset, except the one
     value a GO names for the row (#101: GumbelTopPTokenSelect_v2=110000000).
Exit 0 PASS, 1 FAIL; the report goes to --out with "check": "fast"."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

LINE = re.compile(r"Q_word_v1\{X=16,W=32[^}]*\}: (\d+) calls -> (\d+) units over (\d+) gates")
ALLOWED_MAX_GATES = {"101": "GumbelTopPTokenSelect_v2=110000000"}


def main() -> int:
    ap = argparse.ArgumentParser()
    for a in ("row", "rowdir", "role", "repo", "rev"):
        ap.add_argument(a)
    ap.add_argument("--world", type=int, default=1)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    from verity_vllm.query.required import QUERY_OF_RECORD
    problems: list[str] = []
    man = json.load(open(os.path.join(a.rowdir, "manifest.json")))
    q = man.get("query") or {}
    if q.get("query_id") != QUERY_OF_RECORD or not QUERY_OF_RECORD.startswith("Q_word_v1{X=16,W=32"):
        problems.append(f"manifest query {q.get('query_id')} is not the query of record {QUERY_OF_RECORD}")
    if not q.get("partition"):
        problems.append("the manifest names no partition (query.partition)")
    if "call_boundaries" in (q.get("required_families") or []):
        problems.append("call_boundaries in query.required_families")
    log = open(os.path.join(a.rowdir, "manifest.log"), errors="replace").read()
    lines = LINE.findall(log)
    wl = json.load(open(f"workloads/{a.row}.json"))
    batch = int((wl.get("sweep") or {}).get("batch") or len(wl.get("requests") or []) or 1)
    need = batch * max(1, a.world)
    if len(lines) < need:
        problems.append(f"manifest.log has {len(lines)} Q_word lines, fewer than the {need} components (batch {batch} x world {a.world})")
    if re.search(r"Traceback|QueryRuleViolation|RecomputeViolation", log):
        problems.append("manifest.log shows a traceback or a query-rule violation")
    wc = os.environ.get("VERITY_WORD_CHECK")
    if wc not in (None, "", "16/32"):
        problems.append(f"VERITY_WORD_CHECK={wc} in the Build's environment")
    mg = os.environ.get("VERITY_QWORD_MAX_GATES")
    rownum = os.environ.get("ROWNUM", "")
    if mg not in (None, "") and mg != ALLOWED_MAX_GATES.get(rownum):
        problems.append(f"VERITY_QWORD_MAX_GATES={mg} in the Build's environment (allowed for #{rownum}: {ALLOWED_MAX_GATES.get(rownum)})")
    calls = sum(int(c) for c, _u, _g in lines)
    units = sum(int(u) for _c, u, _g in lines)
    gates = sum(int(g) for _c, _u, g in lines)
    rep = {"row": a.row, "check": "fast", "query_of_record": QUERY_OF_RECORD, "query_id": q.get("query_id"), "partition": bool(q.get("partition")),
           "manifest_digest": man.get("manifest_digest"), "commit_manifest_digest": man.get("manifest_digest"),
           "word_lines": len(lines), "components": need, "calls": calls, "units": units, "gates": gates,
           "env": {"VERITY_WORD_CHECK": wc, "VERITY_QWORD_MAX_GATES": mg}, "problems": problems, "ok": not problems}
    json.dump(rep, open(a.out, "w"), indent=1)
    print(("PASS" if rep["ok"] else "FAIL") + f" fast: {len(lines)}/{need} word lines, {calls} calls -> {units} units over {gates} gates, "
          f"manifest {str(man.get('manifest_digest'))[:16]}" + ("" if rep["ok"] else ": " + "; ".join(problems)))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
