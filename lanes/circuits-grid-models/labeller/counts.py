#!/usr/bin/env python3
"""The report's numbers from the labeller's last gather (/tmp/gm-last-gather.jsonl) and questions.json: models and families with a
deployment run, deployments run (ended items), and pass / fail by cause. `python3 counts.py [GATHER.jsonl]`"""
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from label_loop import FAMILY_OF, base_of, desired  # noqa: E402

Q = json.loads((HERE / "questions.json").read_text())
recs = [json.loads(ln) for ln in Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/gm-last-gather.jsonl").read_text().splitlines() if ln.strip()]
by_cause = collections.Counter()
models, families, passed = set(), set(), 0
twins = []
for r in recs:
    item = r["key"].split("/", 1)[1]
    want = desired(r)
    role = Q[base_of(item)]["role"]
    models.add(role)
    families.add(FAMILY_OF[role])
    if base_of(item) != item:
        twins.append(f"{item} {want['ov.gate']}{' packed' if r.get('packed') else ' unpacked'}")
    if want["ov.gate"] == "pass":
        passed += 1
        continue
    note = want["ov.note"]
    m = re.search(r"(?:cause|failed): (.*)$", note)
    by_cause[re.sub(r"\d+(\.\d+)?", "N", (m.group(1) if m else note))[:140]] += 1
print(f"deployments run {len(recs)}: pass {passed}, fail {len(recs) - passed}; models {len(models)}; families {len(families)} "
      f"({', '.join(sorted(families))})")
for c, n in by_cause.most_common():
    print(f"  {n:4d}  {c}")
if twins:
    print(f"of which packed golden twins ({len(twins)}): {', '.join(sorted(twins))}")
