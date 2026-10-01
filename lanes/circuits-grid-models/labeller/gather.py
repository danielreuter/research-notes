"""Runs on vy-nebius-1 (stdin of `research pods ssh vy-nebius-1 -- python3 -`): every ended `vllm-epoch-run/cov-gm*` item (circuits-grid-models) since SINCE, from the
dispatcher's done.jsonl and the item's sweep dir, as one JSON line each. Read-only."""
import json
import re
import sys
import time
from pathlib import Path

SINCE = "2026-10-01T07:00:00Z"
ROOT = Path("/workspace/jobs/dispatch")
COV = Path("/workspace/jobs/cov")
RUN = re.compile(r"r20\d{6}-\d{6}-[0-9a-f]{4}")
#: only the feeder's own keys and their packed golden twins (-pk, -pk2, -pk3): other lanes run variants of them (cov-gm006-plan)
MINE = re.compile(r'"vllm-epoch-run/cov-gm\d{3}(?:-pk\d*)?"')

ends, moved, tree, packed = {}, set(), {}, {}
for line in (ROOT / "log.jsonl").read_text().splitlines():
    if not MINE.search(line):
        continue
    if '"packed": "' in line:
        e = json.loads(line)
        packed[e.get("key")] = e["packed"]
    if '"ev": "submit"' in line and '"task": 0' in line:
        e = json.loads(line)
        tree[e["key"]] = e.get("tree")
    elif '"ev": "end"' in line:
        e = json.loads(line)
        ends[e["key"]] = e["t"]
    elif '"ev": "moved"' in line:
        moved.add(json.loads(line)["key"])
outcome = {}
for line in (ROOT / "done.jsonl").read_text().splitlines():
    if MINE.search(line):
        e = json.loads(line)
        outcome[e["key"]] = e
# a Commit that n2_commit.sh moved to node 2 and that replayed there with rc 0 never reaches done.jsonl: its row's .n2-replay
# marker ("RUN_ID RC", copied home with the row) is the end. A failure on node 2 goes back to node 1's dispatcher, which ends it.
for key in moved - outcome.keys():
    for mk in (COV / key.split("/", 1)[1]).glob("*/.n2-replay"):
        parts = mk.read_text().split()
        if len(parts) == 2 and parts[1] == "0":
            t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mk.stat().st_mtime))
            outcome[key] = {"key": key, "state": "succeeded", "rc": 0, "task": 2, "t": t, "on": "vy-nebius-2"}
for key, e in outcome.items():
    t = e.get("t") or ends.get(key, "")
    if t < SINCE:
        continue
    item = key.split("/", 1)[1]
    rows = sorted(p for p in (COV / item).glob("*/") if p.is_dir()) if (COV / item).is_dir() else []
    rec = {"key": key, "state": e.get("state"), "rc": e.get("rc"), "task": e.get("task"), "t": t, "on": e.get("on", "vy-nebius-1"),
           "tree": tree.get(key), "packed": packed.get(key), "moved": key in moved, "lease": None, "row": None, "runs": [],
           "stages": [], "max_gates": None, "word_fail": None}
    if rows:
        d = rows[0]
        rec["row"] = d.name
        try:
            rec["lease"] = json.loads((d / "gpu_lease.json").read_text())
        except (OSError, ValueError):
            pass
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
