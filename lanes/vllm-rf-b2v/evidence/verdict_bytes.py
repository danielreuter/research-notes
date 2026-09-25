"""The verdict JSON of every regression row that has a Commit record, byte for byte, under the tree on PYTHONPATH.

For each /workspace/regress/records/<row id> holding a `commit/verdict.json`: the row's `commit.log` from the top-level `commit_logs`
artifact is put beside it when the records tree omits it (as the regression resolver does), then `verdict.from_record(row).dumps()` is
written to OUT/<row id>.json.  When the row carries its own `verdict.json` (the verdict of record), from_record gets that record's
`compat.rc` / `compat.stage_ok` and the two texts are compared byte for byte.  Run once per tree and compare the OUT directories.

    python verdict_bytes.py OUT
"""
import glob
import hashlib
import json
import os
import shutil
import sys

from verity_vllm.check.verdict import from_record

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
logs = "/workspace/regress/commit_logs/top"
rows: dict[str, str] = {}
for p in sorted(glob.glob("/workspace/regress/records/*/**/commit/verdict.json", recursive=True), key=lambda q: (q.count(os.sep), q)):
    row = os.path.dirname(os.path.dirname(p))
    rows.setdefault(os.path.relpath(row, "/workspace/regress/records").split(os.sep)[0], row)
for name, row in sorted(rows.items()):
    log = os.path.join(logs, name, "commit.log")
    if not os.path.exists(os.path.join(row, "commit.log")) and os.path.isfile(log):
        shutil.copy(log, os.path.join(row, "commit.log"))
    rec_p = os.path.join(row, "verdict.json")
    rec = open(rec_p, "rb").read() if os.path.isfile(rec_p) else None
    kw = {}
    if rec is not None:
        compat = json.loads(rec).get("compat") or {}
        kw = {"rc": compat.get("rc"), "stage_ok": compat.get("stage_ok")}
    try:
        text = from_record(row, **kw).dumps()
    except Exception as e:  # recorded as the outcome, compared like any other
        text = f"ERROR {type(e).__name__}: {e}\n"
    with open(os.path.join(out, name + ".json"), "w") as f:
        f.write(text)
    h = hashlib.sha256(text.encode()).hexdigest()
    same = "-" if rec is None else ("record-identical" if rec == text.encode() else "RECORD-DIFFERS")
    print(name, h, same, os.path.relpath(row, "/workspace/regress/records"))
