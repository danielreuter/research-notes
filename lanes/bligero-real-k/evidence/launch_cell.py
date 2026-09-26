"""Launch a bench.cell plan's jobs (roles given, default both) with the input set pre-staged under /workspace/sets on the prover
(no --send); records argv_launched and the run ids in the plan."""
import json, re, subprocess, sys
from pathlib import Path
cell, roles = sys.argv[1], (sys.argv[2:] or ["verifier", "prover"])
p = Path(f"/tmp/cells/{cell}.json"); c = json.loads(p.read_text())
for job in c["jobs"]:
    if job["role"] not in roles:
        continue
    argv = list(job["argv"])
    if "--send" in argv:
        i = argv.index("--send"); tar = Path(argv[i + 1]).name; del argv[i:i + 2]
        argv = [f"SET=/workspace/sets/{tar}" if a.startswith("SET=") else a for a in argv]
    job["argv_launched"] = argv
    r = subprocess.run(["uv", "run", "--frozen", *argv], capture_output=True, text=True, cwd="/workspace", timeout=1200)
    m = re.search(r"\br\d{8}-\d{6}-[0-9a-f]{4}\b", r.stdout + r.stderr)
    job["run"] = m.group(0) if m else None
    print(job["role"], job["run"], r.returncode, "" if m else (r.stdout + r.stderr)[-300:])
p.write_text(json.dumps(c, indent=1))
