#!/usr/bin/env python3
"""counts.py's numbers split by node, plus a per-model line: where each ended deployment's Build ran (node 2 when n2_build moved
it, from node 1's log.jsonl) and where its Commit ran (the gather's `on`). `python3 counts_nodes.py [GATHER.jsonl]`"""
import collections
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from label_loop import FAMILY_OF, ON_NODE, base_of, desired, ssh_cmd  # noqa: E402

Q = json.loads((HERE / "questions.json").read_text())
recs = [json.loads(ln) for ln in Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/gm-last-gather.jsonl").read_text().splitlines() if ln.strip()]
grep = "grep -h '\"ev\": \"moved\"' /workspace/jobs/dispatch/log.jsonl"
moved = subprocess.run(["bash", "-c", grep] if ON_NODE else [*ssh_cmd(), grep], capture_output=True, text=True,
                       timeout=120).stdout.splitlines()
built_n2 = {e["key"] for e in map(json.loads, moved) if "-build-" in e.get("job", "")}
node = collections.Counter()
per_model = collections.defaultdict(lambda: [0, 0])
causes = collections.Counter()
for r in recs:
    item = r["key"].split("/", 1)[1]
    role = Q[base_of(item)]["role"]
    ok = desired(r)["ov.gate"] == "pass"
    node[("build n2" if r["key"] in built_n2 else "build n1", "commit n2" if r.get("on") == "vy-nebius-2" else "commit n1")] += 1
    per_model[role][0 if ok else 1] += 1
    if not ok:
        m = re.search(r"cause: (.{0,90})", desired(r)["ov.note"])
        causes[(m.group(1) if m else desired(r)["ov.note"][-90:]).split(":")[0]] += 1
passed = sum(p for p, _ in per_model.values())
print(f"ended {len(recs)}: pass {passed}, fail {len(recs) - passed}")
print("by node (Build, Commit):", ", ".join(f"{b}/{c} {n}" for (b, c), n in sorted(node.items())))
print(f"models with an ended deployment {len(per_model)}, with a pass {sum(1 for p, _ in per_model.values() if p)}; "
      f"families {len({FAMILY_OF[m] for m in per_model})}, with a pass {len({FAMILY_OF[m] for m, (p, _) in per_model.items() if p})}")
for m, (p, f) in sorted(per_model.items()):
    print(f"  {m:22s} {FAMILY_OF[m]:8s} pass {p:3d} fail {f}")
for c, n in causes.most_common():
    print(f"  fail {n}: {c}")
