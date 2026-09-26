"""bligero-real-k queue: per pod, launch the next cell's prover job (bench.cell plan, SET pre-staged under /workspace/sets, no
--send) once the pod's previous run has ended.  Log: /tmp/queue.log; launched runs: /tmp/queue-runs.json."""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

QUEUES = {
    "a100": {"after": "r20260926-050018-6e45", "cells": ["a100-k2048-sha256", "a100-k8192-sha256"]},
    "h100": {"after": "r20260926-051056-ded6", "cells": ["h100-k8192-xob", "h100-k2048-sha256", "h100-k8192-sha256"]},
}
RUN_ID = re.compile(r"\br\d{8}-\d{6}-[0-9a-f]{4}\b")
LOG = Path("/tmp/queue.log")
RUNS = Path("/tmp/queue-runs.json")


def log(msg):
    with LOG.open("a") as f:
        f.write(f"{time.strftime('%H:%M:%SZ', time.gmtime())} {msg}\n")


def state(run):
    r = subprocess.run(["uv", "run", "--frozen", "research", "fetch", run], capture_output=True, text=True, cwd="/workspace")
    m = re.search(r"observed \S+: (\w+)", r.stdout + r.stderr)
    return m.group(1) if m else "unknown"


def launch(cell):
    c = json.loads(Path(f"/tmp/cells/{cell}.json").read_text())
    job = next(j for j in c["jobs"] if j["role"] == "prover")
    argv = list(job["argv"])
    if "--send" in argv:
        i = argv.index("--send")
        tar = Path(argv[i + 1]).name
        del argv[i:i + 2]
        argv = [f"SET=/workspace/sets/{tar}" if a.startswith("SET=") else a for a in argv]
    job["argv_launched"] = argv
    Path(f"/tmp/cells/{cell}.json").write_text(json.dumps(c, indent=1))
    r = subprocess.run(["uv", "run", "--frozen", *argv], capture_output=True, text=True, cwd="/workspace", timeout=1200)
    m = RUN_ID.search(r.stdout + r.stderr)
    return (m.group(0) if m else None), r.returncode, (r.stdout + r.stderr)[-300:]


def main():
    runs = json.loads(RUNS.read_text()) if RUNS.is_file() else {}
    while any(q["cells"] for q in QUEUES.values()):
        for pod, q in QUEUES.items():
            if not q["cells"]:
                continue
            st = state(q["after"])
            if st in ("done", "failed", "cancelled"):
                cell = q["cells"].pop(0)
                rid, rc, tail = launch(cell)
                log(f"{pod}: {q['after']} {st}; launched {cell} -> {rid} rc={rc} {tail if not rid else ''}")
                runs[cell] = rid
                RUNS.write_text(json.dumps(runs, indent=1))
                if rid:
                    q["after"] = rid
                else:
                    q["cells"].insert(0, cell)
        time.sleep(60)
    log("queue empty")


if __name__ == "__main__":
    sys.exit(main())
