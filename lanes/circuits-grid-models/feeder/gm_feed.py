#!/usr/bin/env python3
"""circuits-grid-models' feeder on vy-nebius-1: submits the cov-gm* config-run items in order, as policy.json allows.

    gm_feed.py [--once] [--dry-run]      (tmux `gm-feed`, as research, KUBECONFIG=$HOME/.kube/config)

Each tick (60 s) it re-reads policy.json:
  {"mode": "hold" | "run", "waves": [1, 2, ...], "skip_roles": [...], "skip_tp": [2], "skip_keys": [...], "builds_cap": 6,
   "build_mem_gb": 300, "backlog_cap": 20, "commit_cap": 6, "big_cap": 6, "cpu_pending_max": 1, "per_tick": 3}
and submits the next items whose wave is allowed and whose role, TP and key aren't skipped while
  - fewer than builds_cap of its Builds are unfinished and their memory requests stay under build_mem_gb,
  - fewer than backlog_cap of its items are past Build and not ended (Commit or replay to come or running),
  - fewer than commit_cap of its Commits are queued or running on node 1, and, for a batch-8+ item, fewer than big_cap of its batch-8+
    items are in Build or Commit: a Commit that waits on release.py's caps (6 in flight, 4 at batch 8+) is moved to node 2, where
    tonight's windows let no Commit start (note:20261001T0920Z-handoff-from-circuits-grid-models-node2-no-commit-slot), and comes
    back an hour later,
  - deployments-cpu has at most cpu_pending_max unadmitted workloads (anyone's).
It never submits a key that log.jsonl or done.jsonl names or that it attempted before (attempted.txt, written before the submit:
a failed submit is not retried; a new key is), and submits nothing from 11:30Z to 12:55Z (node 1's /workspace window and Kueue's
12:10Z hold) or while a file STOP sits beside it.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DISPATCH = Path("/workspace/jobs/dispatch")
PY = "/workspace/jobs/venv312/bin/python"
DISPATCH_PY = "/workspace/jobs/dispatch/infra/nebius/dispatch.py"
WS = "vllm-epoch-run"
GUARD = ((11, 30), (12, 55))
DRY = "--dry-run" in sys.argv


def log(msg):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {'DRY ' if DRY else ''}{msg}"
    print(line, flush=True)
    with open(HERE / "feed.log", "a") as f:
        f.write(line + "\n")


def jsonl(p):
    out = []
    if p.exists():
        for line in p.read_text().splitlines():
            if "cov-gm" in line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def stages():
    """{key: (stage, task)} from log.jsonl / done.jsonl: 'build' (task 0 unfinished), 'later' (past Build, not ended), 'ended'."""
    st = {}
    for e in jsonl(DISPATCH / "log.jsonl"):
        k = e.get("key", "")
        if not k.startswith(f"{WS}/cov-gm"):
            continue
        ev, task = e.get("ev"), int(e.get("task", 0) or 0)
        if ev in ("submit", "spool", "adopt"):
            st[k] = ("build" if task == 0 else "later", task)
        elif ev == "end":
            ok = e.get("state") == "succeeded"
            if ok and task < 2:
                st[k] = ("later", task + 1)
            elif e.get("rc") == 99:
                st[k] = ("build" if task == 0 else "later", task)
            else:
                st[k] = ("ended", task)
        elif ev == "rejected":
            st[k] = ("ended", task)
        elif ev == "moved":
            st[k] = ("moved", task)
    for e in jsonl(DISPATCH / "done.jsonl"):
        k = e.get("key", "")
        if k.startswith(f"{WS}/cov-gm"):
            st[k] = ("ended", int(e.get("task", 0) or 0))
    return st


def cpu_pending():
    wls = json.loads(subprocess.run(["kubectl", "get", "workloads", "-o", "json"], capture_output=True, text=True,
                                    check=True).stdout)["items"]
    n = 0
    for w in wls:
        s = w.get("status") or {}
        if (w.get("spec") or {}).get("queueName") != "deployments-cpu" or s.get("admission"):
            continue
        if any(c.get("type") == "Finished" and c.get("status") == "True" for c in s.get("conditions") or []):
            continue
        n += 1
    return n


def guarded(t=None):
    g = time.gmtime(time.time() if t is None else t)
    return GUARD[0] <= (g.tm_hour, g.tm_min) < GUARD[1]


def tick():
    pol = json.loads((HERE / "policy.json").read_text())
    if pol.get("mode") != "run" or (HERE / "STOP").exists() or guarded():
        return f"idle ({'STOP' if (HERE / 'STOP').exists() else 'guard' if guarded() else pol.get('mode')})"
    items = json.loads((HERE / "items.json").read_text())
    by_key = {f"{WS}/{i['key']}": i for i in items}
    attempted = set((HERE / "attempted.txt").read_text().split()) if (HERE / "attempted.txt").exists() else set()
    st = stages()
    builds = [k for k, (s, _) in st.items() if s == "build"]
    later = [k for k, (s, _) in st.items() if s == "later"]
    commits = [k for k, (s, t) in st.items() if s == "later" and t == 1]
    big = [k for k in builds + commits if k in by_key and by_key[k]["batch"] >= 8]
    build_mem = sum(by_key[k]["item"]["resources"]["build"]["memory"] for k in builds if k in by_key)
    pend = cpu_pending()
    summary = (f"builds {len(builds)} ({build_mem} GB) later {len(later)} (commits {len(commits)}, b8+ {len(big)}) "
               f"ended {sum(1 for s, _ in st.values() if s == 'ended')} moved {sum(1 for s, _ in st.values() if s == 'moved')} cpu-pending {pend}")
    sent = 0
    for i in items:
        k = f"{WS}/{i['key']}"
        if (k in st or i["key"] in attempted or i["wave"] not in pol.get("waves", []) or i["role"] in pol.get("skip_roles", [])
                or i["tp"] in pol.get("skip_tp", []) or i["key"] in pol.get("skip_keys", [])):
            continue
        mem = i["item"]["resources"]["build"]["memory"]
        if (len(builds) >= pol.get("builds_cap", 6) or len(later) >= pol.get("backlog_cap", 20) or pend > pol.get("cpu_pending_max", 1)
                or len(commits) >= pol.get("commit_cap", 6) or sent >= pol.get("per_tick", 3)):
            break
        if build_mem + mem > pol.get("build_mem_gb", 300):
            continue
        if i["batch"] >= 8 and len(big) >= pol.get("big_cap", 6):
            continue
        it = i["item"]
        cmd = [PY, DISPATCH_PY, "submit", it["template"], k, "--tree", it["tree"], "--resources", json.dumps(it["resources"])]
        for ek, ev in it["env"].items():
            cmd += ["--env", f"{ek}={ev}"]
        if DRY:
            cmd.append("--dry-run")
        else:
            with open(HERE / "attempted.txt", "a") as f:
                f.write(i["key"] + "\n")
        r = subprocess.run(cmd, capture_output=True, text=True)
        out = (r.stdout.strip().splitlines() or [""])[-1] if not DRY else f"rendered {len(r.stdout)} bytes"
        log(f"submit {i['key']} wave {i['wave']} {it['env']['ROW']} rc {r.returncode}: {out} {r.stderr.strip()[-300:]}")
        if r.returncode:
            continue
        builds.append(k)
        if i["batch"] >= 8:
            big.append(k)
        build_mem += mem
        pend += 1
        sent += 1
    return summary + f" sent {sent}"


def main():
    last = None
    while True:
        try:
            s = tick()
        except Exception as e:  # noqa: BLE001  (a failed tick is retried next time)
            s = f"tick failed: {e}"
        if s != last:
            log(s)
            last = s
        if "--once" in sys.argv:
            return
        time.sleep(60)


if __name__ == "__main__":
    main()
