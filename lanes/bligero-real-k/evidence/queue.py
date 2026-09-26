"""bligero-real-k queue: per pod, launch the next cell's prover job (bench.cell plan, SET pre-staged under /workspace/sets, no
--send) once the pod's previous run has ended.  Log: /tmp/queue.log; launched runs: /tmp/queue-runs.json."""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

QFILE = Path("/tmp/queue.json")      # {pod: {"after": run, "cells": [cell, ...]}}, re-read every pass (edit it to reorder)
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


def current_verifier(vpod):
    """The newest verifier run launched on vpod by any plan (launch_cell.py records job["run"])."""
    runs = []
    for f in Path("/tmp/cells").glob("*.json"):
        for j in json.loads(f.read_text()).get("jobs", []):
            if j["role"] == "verifier" and j.get("pod") == vpod and j.get("run"):
                runs.append(j["run"])
    return max(runs) if runs else None


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
    while True:
        QUEUES = json.loads(QFILE.read_text())
        if not any(q["cells"] for q in QUEUES.values()):
            break
        for pod, q in QUEUES.items():
            if not q["cells"]:
                continue
            st = state(q["after"])
            if st in ("done", "failed", "cancelled") and q["cells"][0].startswith("@verifier:"):
                # restart the pod pair's live verifier on the current tree: stop the running serve, launch the plan's verifier job
                vcell = q["cells"].pop(0).split(":", 1)[1]
                c = json.loads(Path(f"/tmp/cells/{vcell}.json").read_text())
                vpod = next(j for j in c["jobs"] if j["role"] == "verifier")["pod"]
                old = current_verifier(vpod)
                if old:
                    # stop the run through its workload's process group (status.json pgid), never pkill -f
                    k = subprocess.run(["uv", "run", "--frozen", "research", "pods", "ssh", vpod, "--",
                                        f"kill -TERM -$(python3 -c 'import json; print(json.load(open(\"/workspace/research/runs/{old}/status.json\"))[\"pgid\"])')"],
                                       capture_output=True, text=True, cwd="/workspace")
                    log(f"{pod}: stopped verifier run {old} on {vpod} rc={k.returncode} {k.stderr.strip()[-160:]}")
                time.sleep(25)
                r = subprocess.run(["python3", "/tmp/launch_cell.py", vcell, "verifier"], capture_output=True, text=True, cwd="/workspace")
                log(f"{pod}: restarted verifier on {vpod} from {vcell}: {r.stdout.strip()[-120:]} {r.stderr.strip()[-200:]}")
                cur = json.loads(QFILE.read_text())
                cur[pod] = q
                QFILE.write_text(json.dumps(cur, indent=1))
                if not q["cells"]:
                    continue
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
                cur = json.loads(QFILE.read_text())          # merge: only this pod's entry changed here
                cur[pod] = q
                QFILE.write_text(json.dumps(cur, indent=1))
        time.sleep(60)
    log("queue empty")


if __name__ == "__main__":
    sys.exit(main())
