"""verdict.from_record(row_dir).dumps() for every regression record that has a Commit verdict (the T0 `verdict` check's reconstruction of
a row without verdict.json), written to OUT/<record>.json.  Run once with each tree on PYTHONPATH and compare the two directories.

    python verdict_ab.py OUT
"""
import glob
import os
import sys

from verity_vllm.check.verdict import from_record

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for p in sorted(glob.glob("/workspace/regress/records/*/commit/verdict.json")):
    root = os.path.dirname(os.path.dirname(p))
    name = os.path.basename(root)
    try:
        text = from_record(root).dumps()
    except Exception as e:  # recorded as the outcome, compared like any other
        text = f"ERROR {type(e).__name__}: {e}\n"
    with open(os.path.join(out, name + ".json"), "w") as f:
        f.write(text)
    print(name, len(text), text.splitlines()[0][:80] if text.startswith("ERROR") else "")
