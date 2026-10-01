"""Runs on vy-nebius-1 (stdin of `research pods ssh vy-nebius-1 -- python3 -`): every ended `vllm-epoch-run/*` item since SINCE, from the
dispatcher's done.jsonl and the item's sweep dir, as one JSON line each. Read-only."""
import json
import re
import sys
from pathlib import Path

SINCE = "2026-10-01T04:30:00Z"
ROOT = Path("/workspace/jobs/dispatch")
COV = Path("/workspace/jobs/cov")
RUN = re.compile(r"r20\d{6}-\d{6}-[0-9a-f]{4}")

ends = {}
for line in (ROOT / "log.jsonl").read_text().splitlines():
    if '"vllm-epoch-run/' in line and '"ev": "end"' in line:
        e = json.loads(line)
        ends[e["key"]] = e["t"]
outcome = {}
for line in (ROOT / "done.jsonl").read_text().splitlines():
    if '"vllm-epoch-run/' in line:
        e = json.loads(line)
        outcome[e["key"]] = e
for key, e in outcome.items():
    t = e.get("t") or ends.get(key, "")
    if t < SINCE:
        continue
    item = key.split("/", 1)[1]
    rows = sorted(p for p in (COV / item).glob("*/") if p.is_dir()) if (COV / item).is_dir() else []
    rec = {"key": key, "state": e.get("state"), "rc": e.get("rc"), "task": e.get("task"), "t": t, "row": None, "runs": [],
           "stages": [], "max_gates": None, "word_fail": None}
    if rows:
        d = rows[0]
        rec["row"] = d.name
        runs = set()
        for f in d.rglob("*"):
            if f.is_file() and f.stat().st_size < 4_000_000 and f.suffix in ("", ".txt", ".log", ".json", ".jsonl"):
                try:
                    runs.update(RUN.findall(f.read_text(errors="replace")))
                except OSError:
                    pass
        rec["runs"] = sorted(runs)
        st = d / "stages.txt"
        if st.exists():
            rec["stages"] = [ln[:400] for ln in st.read_text(errors="replace").splitlines() if not ln.startswith(("release ", "precheck"))][-8:]
        sw = d / "strict_word.log"
        if sw.exists():
            txt = sw.read_text(errors="replace")
            m = re.search(r"--build-max-gates (\S*) --allowed-max-gates", txt)
            rec["max_gates"] = m.group(1) if m else ""
            m = re.search(r"QueryRuleViolation[^\n]{0,300}", txt)
            rec["word_fail"] = m.group(0) if m else None
    print(json.dumps(rec))
