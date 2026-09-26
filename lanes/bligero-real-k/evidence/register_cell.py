"""Register a finished cell (bench.cell register --force), record an interaction check that fails ONLY because measured is
under the serial model (overlap: the root's ruling 2026-09-26, the one-sided rule is Daniel's decision) as a note label, and
label the result it replaces superseded_by.  Usage: register_cell.py CELL PROVER_RUN [OLD_ART]"""
import json
import re
import subprocess
import sys

cell, run = sys.argv[1], sys.argv[2]
old = sys.argv[3] if len(sys.argv) > 3 else None
env = {"PYTHONPATH": "packages/verity/src:backends/numerical/python:tools/research/src:."}
import os
from pathlib import Path
env = {**os.environ, **env}


def serving_verifier(cell, run):
    """The verifier run that served ``run``: the newest verifier run launched on the plan's verifier pod before it."""
    vpod = next(j for j in json.loads(Path(f"/tmp/cells/{cell}.json").read_text())["jobs"] if j["role"] == "verifier")["pod"]
    runs = [j["run"] for f in Path("/tmp/cells").glob("*.json") for j in json.loads(f.read_text()).get("jobs", [])
            if j["role"] == "verifier" and j.get("pod") == vpod and j.get("run") and j["run"] < run]
    # a relaunch from the same plan overwrites job["run"]; the queue logs every run it stops
    runs += [m.group(1) for m in re.finditer(r"stopped verifier run (\S+) on (\S+)", Path("/tmp/queue.log").read_text())
             if m.group(2) == vpod and m.group(1) < run]
    return max(runs) if runs else None


vrun = serving_verifier(cell, run)
vargs = []
if vrun:
    f = subprocess.run(["uv", "run", "--frozen", "research", "fetch", vrun, "--all"], capture_output=True, text=True, cwd="/workspace")
    print(f"verifier run {vrun}: fetch --all rc={f.returncode}")
    vargs = ["--verifier-run", vrun]
r = subprocess.run(["uv", "run", "--frozen", "python", "-m", "verity_numerical.bench.cell", "register", "--cell", f"/tmp/cells/{cell}.json",
                    "--prover-run", run, *vargs, "--force"], capture_output=True, text=True, cwd="/workspace", env=env)
out = r.stdout
m = re.search(r'"art": "(art:[0-9a-f]+)"', out)
art = m.group(1) if m else None
probs = re.findall(r'"(interaction: [^"]*|contract: [^"]*|[^"]*relation[^"]*|instances[^"]*|protocol[^"]*|no [^"]*probe[^"]*)"', out)
print(json.dumps({"cell": cell, "run": run, "art": art, "rc": r.returncode, "problems": probs}, indent=1))
if not art:
    print(out[-1500:], r.stderr[-800:])
    sys.exit(1)


def label(target, key, value, ref=None):
    argv = ["uv", "run", "--frozen", "research", "data", "label", target, key, value, "--by", "bligero-real-k"]
    if ref:
        argv += ["--ref", ref]
    p = subprocess.run(argv, capture_output=True, text=True, cwd="/workspace")
    print(f"label {target[:14]} {key}: rc={p.returncode} {(p.stdout + p.stderr).strip()[-160:]}")


inter = [p for p in probs if p.startswith("interaction:")]
under = [p for p in inter if re.search(r"is -\d+% from the model", p)]
if inter and len(under) == len(inter) and len(probs) == len(inter):
    label(art, "note", f"{under[0]} -- measured UNDER the serial model only: the sender streams each proof during proving (overlap); "
                       f"the transfer tail is counted; a one-sided check is Daniel's decision (root's ruling 2026-09-26)", ref=run)
if old:
    label(old, "superseded_by", art, ref=run)
