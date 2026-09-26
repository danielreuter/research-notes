"""launch_cell.py for the L40S #101 cells: the plan's jobs from the main worktree (--source . ships its clean HEAD), set pre-staged."""
import json, re, subprocess, sys
from pathlib import Path
REPO, RESEARCH = "/tmp/wt-main2", "/tmp/wt-main2/.venv/bin/research"
cell, roles = sys.argv[1], (sys.argv[2:] or ["verifier", "prover"])
p = Path(f"/tmp/cells/{cell}.json"); c = json.loads(p.read_text())
for job in c["jobs"]:
    if job["role"] not in roles:
        continue
    argv = list(job["argv"])
    tar = None
    while "--send" in argv:                       # the set is pre-staged under /workspace/sets on the prover
        i = argv.index("--send"); tar = Path(argv[i + 1]).name; del argv[i:i + 2]
    if tar:
        argv = [f"SET=/workspace/sets/{tar}" if a.startswith("SET=") else a for a in argv]
    assert argv[0] == "research"
    job["argv_launched"] = argv
    r = subprocess.run([RESEARCH, *argv[1:]], capture_output=True, text=True, cwd=REPO, timeout=1200)
    m = re.search(r"\br\d{8}-\d{6}-[0-9a-f]{4}\b", r.stdout + r.stderr)
    job["run"] = m.group(0) if m else None
    print(job["role"], job["run"], r.returncode, "" if m else (r.stdout + r.stderr)[-400:], flush=True)
p.write_text(json.dumps(c, indent=1))
