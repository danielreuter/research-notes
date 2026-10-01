#!/usr/bin/env python3
"""circuits-grid-models' feeder on vy-nebius-1: submits the cov-gm* config-run items in order, as policy.json allows.

    gm_feed.py [--once] [--dry-run]      (tmux `gm-feed`, as research, KUBECONFIG=$HOME/.kube/config)

Each tick (60 s) it re-reads policy.json:
  {"mode": "hold" | "run", "waves": [1, 2, ...], "skip_roles": [...], "skip_tp": [2], "skip_keys": [...], "builds_cap": 6,
   "build_mem_gb": 300, "backlog_cap": 20, "commit_cap": 6, "big_cap": 6, "cpu_pending_max": 1, "per_tick": 3,
   "deadlines": [["12:10", "12:55"], ["14:35", "14:35"]]}
and submits the next items whose wave is allowed and whose role, TP and key aren't skipped while
  - fewer than builds_cap of its Builds are unfinished and their memory requests stay under build_mem_gb,
  - fewer than backlog_cap of its items are past Build and not ended (Commit or replay to come or running),
  - fewer than commit_cap of its Commits are queued or running on node 1, and, for a batch-8+ item, fewer than big_cap of its batch-8+
    items are in Build or Commit: a Commit that waits on release.py's caps (6 in flight, 4 at batch 8+) is moved to node 2, where
    tonight's windows let no Commit start (note:20261001T0920Z-handoff-from-circuits-grid-models-node2-no-commit-slot), and comes
    back an hour later,
  - deployments-cpu has at most cpu_pending_max unadmitted workloads (anyone's),
  - its Commit is estimated to end by the deadline that applies: the first [END, UNTIL] pair ("HH:MM" UTC) of `deadlines` whose
    UNTIL is still ahead, none once all have passed (circuits: a row whose Commit can't finish by 5:10 AM PDT waits until after
    5:55; then, until 14:35Z, a row whose deployment can't end by the 7:50 AM PDT count waits behind the rows that can). The estimate
    is QUEUE_MIN plus the slowest Build and Commit node 1 has logged for the same model, TP, batch and input length (anyone's row),
    times 1.1, else est_min's table.
It never submits a key that log.jsonl or done.jsonl names or that it attempted before (attempted.txt, written before the submit:
a failed submit is not retried; a new key is), and submits nothing from 11:30Z to 12:55Z (node 1's /workspace window and Kueue's
12:10Z hold) or while a file STOP sits beside it.
"""
import json
import re
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
ROW_RE = re.compile(r"(.+?)__\w+__\w+__tp(\d)__b(\d+)__i(\d+)__")
QUEUE_MIN = 10
# Commit minutes at batch 1-8 and 256 tokens, by model; Build minutes by input length and batch
COMMIT_MIN = (("qwen3-30b-a3b", 55), ("-14b", 28), ("olmoe", 14), ("-8b", 14), ("-7b", 14), ("-6b", 10), ("-4b", 10), ("-3b", 10))
BUILD_MIN = {256: {1: 15, 8: 15, 16: 40, 32: 60}, 1024: {1: 35, 8: 55, 16: 110, 32: 130}}


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


def walls():
    """{(model, tp, batch, input tokens): {task: slowest wall_s}} over node 1's succeeded Builds (0) and Commits (1)."""
    by_name = {}
    for line in (DISPATCH / "log.jsonl").read_text().splitlines():
        if '"ev": "end"' not in line or f'"{WS}/' not in line or '"wall_s"' not in line:
            continue
        e = json.loads(line)
        task = int(e.get("task", 0) or 0)
        if e.get("state") == "succeeded" and task < 2:
            w = by_name.setdefault(e["key"].split("/", 1)[1], {})
            w[task] = max(w.get(task, 0), e["wall_s"])
    out = {}
    for name, w in by_name.items():
        rows = list((Path("/workspace/jobs/cov") / name).glob("*__tp*"))
        m = ROW_RE.match(rows[0].name) if len(rows) == 1 else None
        if m:
            c = out.setdefault((m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))), {})
            for t, s in w.items():
                c[t] = max(c.get(t, 0), s)
    return out


def est_min(row, obs):
    model, tp, b, n = ROW_RE.match(row).groups()
    tp, b, n = int(tp), int(b), int(n)
    seen = dict(obs.get((model, tp, b, n), {}))
    # a base model's rows stand in for its variants' (qwen3-30b-a3b for qwen3-30b-a3b-2507, mistral-7b for mistral-7b-instruct)
    for (m, t, bb, nn), w in sorted(obs.items(), key=lambda kv: -len(kv[0][0])):
        if (t, bb, nn) == (tp, b, n) and model.startswith(m + "-"):
            seen = {**w, **seen}
    build = seen[0] / 60 * 1.1 if 0 in seen else BUILD_MIN[n][b] * (1.5 if model.startswith("qwen3-30b") else 1)
    commit = seen[1] / 60 * 1.1 if 1 in seen else (next((v for s, v in COMMIT_MIN if s in model), 8)
                                                   * {1: 1, 8: 1, 16: 2.5, 32: 3.5}[b] * (3 if n == 1024 else 1))
    return QUEUE_MIN + build + commit


def hhmm_today(s, now):
    h, m = map(int, s.split(":"))
    g = time.gmtime(now)
    return now - (g.tm_hour * 3600 + g.tm_min * 60 + g.tm_sec) + h * 3600 + m * 60


def deadline(pol, now):
    return next((hhmm_today(end, now) for end, until in pol.get("deadlines", []) if now < hhmm_today(until, now)), None)


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
    sent, late = 0, 0
    now = time.time()
    due = deadline(pol, now)
    gate = due is not None
    obs = walls() if gate else {}
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
        est = est_min(it["env"]["ROW"], obs) if gate else 0
        if gate and now + est * 60 > due:
            late += 1
            continue
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
        log(f"submit {i['key']} wave {i['wave']} {it['env']['ROW']}{f' est {est:.0f} min' if gate else ''} rc {r.returncode}: "
            f"{out} {r.stderr.strip()[-300:]}")
        if r.returncode:
            continue
        builds.append(k)
        if i["batch"] >= 8:
            big.append(k)
        build_mem += mem
        pend += 1
        sent += 1
    return summary + f" sent {sent}" + (f" past-deadline {late}" if gate else "")


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
