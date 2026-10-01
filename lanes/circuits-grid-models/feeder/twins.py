#!/usr/bin/env python3
"""circuits-grid-models' packed golden twins (note:20261001T1158Z-handoff-from-circuits-refill-node2-pack-goldens): one per small
model, an already-run TP1 B1 256/32 greedy row resubmitted as `<key>-pk` on the plan tree, same config, its own sweep dir.
cov-gm001 stands in for qwen3-06b: none of that model's B1 256 rows passed (their Commits did; each replay hit SiluMul_v1's
expf-overflow edge), so its twin compares the Commit (run root, binding map) and expects the same replay mismatch.

    twins.py [--at HH:MM:SS] [--dry-run]     (on vy-nebius-1, as research, KUBECONFIG=$HOME/.kube/config; tmux `gm-twins`)

Waits until --at (UTC, today), then submits each twin whose key log.jsonl doesn't name yet. Log: twins.log beside it."""
import calendar
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = Path("/workspace/jobs/dispatch/log.jsonl")
PY = "/workspace/jobs/venv312/bin/python"
DISPATCH_PY = "/workspace/jobs/dispatch/infra/nebius/dispatch.py"
TREE = "/workspace/research/trees/cursor-grid-plan-gm-827a"
BASES = ["cov-gm002", "cov-gm003", "cov-gm004", "cov-gm005", "cov-gm006", "cov-gm007", "cov-gm008", "cov-gm009", "cov-gm001"]
DRY = "--dry-run" in sys.argv


def log(msg):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {'DRY ' if DRY else ''}{msg}"
    print(line, flush=True)
    with open(HERE / "twins.log", "a") as f:
        f.write(line + "\n")


def main():
    if "--at" in sys.argv:
        at = sys.argv[sys.argv.index("--at") + 1]
        day = time.strftime("%Y-%m-%d", time.gmtime())
        t = calendar.timegm(time.strptime(f"{day} {at}", "%Y-%m-%d %H:%M:%S"))
        log(f"waiting until {at}Z")
        while time.time() < t:
            time.sleep(min(30, max(1, t - time.time())))
    items = {i["key"]: i for i in json.loads((HERE / "items.json").read_text())}
    named = LOG.read_text()
    for base in BASES:
        key = f"{base}-pk"
        it = items[base]["item"]
        if f'"vllm-epoch-run/{key}"' in named:
            log(f"skip {key}: log.jsonl names it")
            continue
        env = {**it["env"], "SWEEP_DIR": f"/workspace/jobs/cov/{key}",
               "RESEARCH_QUESTION": (f"Packed golden twin of {base}: does a packed Commit of {it['env']['ROW']} on the plan tree give "
                                     f"the same run root, binding map and verdict as {base}'s unpacked one? (circuits-grid-models, "
                                     "note:20261001T1158Z-handoff-from-circuits-refill-node2-pack-goldens)")}
        cmd = [PY, DISPATCH_PY, "submit", it["template"], f"vllm-epoch-run/{key}", "--tree", TREE,
               "--resources", json.dumps(it["resources"])]
        for k, v in env.items():
            cmd += ["--env", f"{k}={v}"]
        if DRY:
            cmd.append("--dry-run")
        r = subprocess.run(cmd, capture_output=True, text=True)
        out = (r.stdout.strip().splitlines() or [""])[-1] if not DRY else f"rendered {len(r.stdout)} bytes"
        log(f"submit {key} {it['env']['ROW']} rc {r.returncode}: {out} {r.stderr.strip()[-300:]}")


if __name__ == "__main__":
    main()
