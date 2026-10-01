"""Fill /tmp/gm/report_0740.md's placeholders from the labeller's last gather and node 1's log; print the result."""
import collections
import json
import subprocess
import sys
from pathlib import Path

L = Path.home() / ".research/notes/lanes/circuits-grid-models/labeller"
sys.path.insert(0, str(L))
from label_loop import FAMILY_OF, desired, ssh_cmd  # noqa: E402

Q = json.loads((L / "questions.json").read_text())
G = Path("/tmp/gm-last-gather.jsonl")
recs = [json.loads(ln) for ln in G.read_text().splitlines() if ln.strip()]
moved = subprocess.run([*ssh_cmd(), "grep -h '\"ev\": \"moved\"' /workspace/jobs/dispatch/log.jsonl"], capture_output=True, text=True,
                       timeout=120).stdout.splitlines()
built_n2 = {e["key"] for e in map(json.loads, moved) if "-build-" in e.get("job", "")}
sub = subprocess.run([*ssh_cmd(), "python3 -"], input=Path("/tmp/gm/submitted.py").read_text(), capture_output=True, text=True,
                     timeout=120).stdout.splitlines()
node = collections.Counter()
per = collections.defaultdict(lambda: [0, 0])
mid = {}
for r in recs:
    role = Q[r["key"].split("/", 1)[1].removesuffix("-pk")]["role"]
    mid[role] = r["row"].split("__")[0]
    ok = desired(r)["ov.gate"] == "pass"
    node[(2 if r["key"] in built_n2 else 1, 2 if r.get("on") == "vy-nebius-2" else 1)] += 1
    per[role][0 if ok else 1] += 1
passed = sum(p for p, _ in per.values())
submitted = next(s for s in sub if s.startswith("submitted")).split()[1]
openl = next(s for s in sub if s.startswith("not ended"))
d = eval(openl.split(":", 1)[1].strip())  # {'moved task 0': n, ...}
inflight = sum(v for k, v in d.items() if not k.startswith("moved"))
table = "\n".join(f"| {mid[m]} | {FAMILY_OF[m]} | {p} | {f} |" for m, (p, f) in sorted(per.items()))
t = Path("/tmp/gm/report_0740.md").read_text()
mt = subprocess.run(["date", "-u", "-r", str(G), "+%H:%MZ"], capture_output=True, text=True).stdout.strip()
for k, v in {"__GATHER__": mt, "__ENDED__": len(recs), "__PASS__": passed, "__FAIL__": len(recs) - passed, "__N11__": node[(1, 1)],
             "__N21__": node[(2, 1)], "__N12__": node[(1, 2)], "__N22__": node[(2, 2)], "__INFLIGHT__": inflight,
             "__SUBMITTED__": submitted, "__TABLE__": table}.items():
    t = t.replace(k, str(v))
print(t)
print(f"<!-- models {len(per)}, with a pass {sum(1 for p, _ in per.values() if p)}; families {len({FAMILY_OF[m] for m in per})} -->",
      file=sys.stderr)
