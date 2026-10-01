"""On vy-nebius-1: cov-gm* items by stage from log.jsonl / done.jsonl, with each ended or failed task. Read-only."""
import collections
import json
from pathlib import Path

D = Path("/workspace/jobs/dispatch")
ev = collections.defaultdict(list)
for line in (D / "log.jsonl").read_text().splitlines():
    if "cov-gm" in line:
        e = json.loads(line)
        ev[e["key"]].append(e)
done = {}
for line in (D / "done.jsonl").read_text().splitlines():
    if "cov-gm" in line:
        e = json.loads(line)
        done[e["key"]] = e
stage = collections.Counter()
for k, es in sorted(ev.items()):
    last = es[-1]
    if k in done:
        d = done[k]
        s = f"ended {d.get('state')} rc {d.get('rc')} at task {d.get('task')}"
    elif last["ev"] == "submit":
        s = f"task {last['task']} in flight"
    elif last["ev"] == "end":
        s = f"task {last['task']} {last.get('state')} (next pending)"
    else:
        s = last["ev"]
    stage[s.split(" rc")[0] if s.startswith("ended") else s] += 1
    walls = [f"t{e['task']}:{e.get('state', '')[:4]}:{e.get('wall_s')}" for e in es if e["ev"] == "end"]
    print(f"{k.split('/')[1]} {s:40s} {' '.join(walls)}")
print(dict(stage))
