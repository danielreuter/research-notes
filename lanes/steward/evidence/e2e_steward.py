"""End-to-end check of the steward rules through the real `research notes watch --pods --reap --snapshot` loop, on a TEMP notes
root.  The RunPod API is faked at its lowest level (pod listing, GraphQL balance, DELETE /pods/<id>); the store (fs remote), the
runs dir, machines.toml, the guardian log and the render source are temp files.  Nothing touches ~/.research/notes or a real pod.

    cd /tmp && PYTHONPATH=<steward worktree>/tools/research/src ~/projects/verity-main-wt/main/.venv/bin/python e2e_steward.py

Two passes, as two `main()` calls: the second is a watcher restart, so what it does not repeat comes from steward-state.json.
"""
import datetime as dt
import json
import os
import subprocess
import tempfile
from pathlib import Path

base = Path(tempfile.mkdtemp(prefix="steward-e2e-"))
root, runs, store, vault, src, glog, wt = (base / x for x in ("notes", "runs", "store", "vault", "src", "guardian.log", "wt-alive"))
os.environ.update(RESEARCH_STORE=str(store), RESEARCH_STORE_CONFIG=str(base / "store.toml"), RESEARCH_RUNS=str(runs),
                  RESEARCH_MACHINES=str(base / "machines.toml"))
os.environ.pop("RESEARCH_REPO", None)
(base / "store.toml").write_text(f'[remote]\ntype = "fs"\npath = "{vault}"\n')
(base / "machines.toml").write_text('[machines.box-alive]\nprovider = "runpod"\npod_id = "podalive00001"\nproject = "verity"\n')

from research import notes  # noqa: E402
from research.pods import connect, runpod  # noqa: E402
from research.store.local import LocalStore  # noqa: E402

real = Path.home() / ".research" / "notes"
assert real != root and real not in root.parents
now = dt.datetime.now(dt.timezone.utc)


def ago(m: float) -> dt.datetime:
    return now - dt.timedelta(minutes=m)


def report(lane: str, body: str, minutes_ago: float, status: str = "open") -> None:
    p = root / "lanes" / lane / f"{ago(minutes_ago):%Y%m%dT%H%MZ}-report-{lane}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"---\nlane: {lane}\nkind: report\nstatus: {status}\n---\n\n{body}\n")
    os.utime(p, (ago(minutes_ago).timestamp(),) * 2)


def run(rid: str, pod_id: str, files: tuple[str, ...] = ()) -> None:
    (runs / rid).mkdir(parents=True)
    (runs / rid / "remote.json").write_text(json.dumps({"run_id": rid, "pod_id": pod_id, "phase": "launched"}))
    for f in files:
        (runs / rid / f).write_text("{}\n")


st = LocalStore()
(base / "result.txt").write_text("the dead lane's result\n")
art = st.put_artifact("fixture/v1", {}, file=base / "result.txt")
st.push(art)                                                           # preserved: verified remote replica recorded
report("dead", f"CHECKPOINT 1111111 ({ago(180):%H:%M}Z) [open] bench running; result art:{art.split(':')[1][:12]}", 180)
report("blocked", f"CHECKPOINT 2222222 ({ago(90):%H:%M}Z) [open] sweeping", 90)
report("alive", f"CHECKPOINT 3333333 ({ago(3):%H:%M}Z) [open] measuring", 3)
report("done", f"CHECKPOINT 4444444 ({ago(60):%H:%M}Z) [final] done\n\n## FINAL\nall preserved", 60, status="final")
notes.bind(root, "dead", final=f"{ago(120):%H:%M}Z", budget="$1: 1x 4090")
os.utime(root / "lanes" / "dead" / "binding.json", (ago(200).timestamp(),) * 2)     # bound at launch, 200 min ago
notes.bind(root, "blocked", budget="$10")
wt.mkdir()
notes.bind(root, "alive", worktree=str(wt))
(base / "wt-done").mkdir()
notes.bind(root, "done", worktree=str(base / "wt-done"))
run("r20260924-100000-aaaa", "poddead00001", ("job.json", "preserved.json"))           # fetched with --all
run("r20260924-100500-bbbb", "podblocked001", ("job.json",))                          # finished on the pod, never fetched

pods = [{"id": "poddead00001", "name": "vy-dead-veritor-campaign", "costPerHr": 0.74, "lastStartedAt": f"{ago(180):%Y-%m-%d %H:%M:%S}.000 +0000 UTC"},
        {"id": "podblocked001", "name": "vy-blocked", "costPerHr": 0.34, "lastStartedAt": f"{ago(100):%Y-%m-%d %H:%M:%S}.000 +0000 UTC"},
        {"id": "podalive00001", "name": "vy-alive", "costPerHr": 2.69, "lastStartedAt": f"{ago(30):%Y-%m-%d %H:%M:%S}.000 +0000 UTC"},
        {"id": "poddone000001", "name": "vy-done", "costPerHr": 0.24, "lastStartedAt": f"{ago(120):%Y-%m-%d %H:%M:%S}.000 +0000 UTC"}]
idle = {"busy": 0, "gpu_util": 0, "gpu_apps": 0, "serve": 0}
probes = {"poddead00001": {**idle, "file_age_s": 50 * 60}, "podblocked001": {**idle, "file_age_s": 45 * 60},
          "podalive00001": {"busy": 2, "gpu_util": 97, "gpu_apps": 1, "serve": 0, "file_age_s": 5}, "poddone000001": {**idle, "file_age_s": 3600}}
deleted: list[str] = []


def fake_request(method: str, path: str, *a, **k) -> dict:
    assert method == "DELETE" and path.startswith("/pods/"), (method, path)
    deleted.append(path.split("/")[2])
    return {}


connect._list_pods = lambda: [{**p, "desiredStatus": "RUNNING"} for p in pods if p["id"] not in deleted]
runpod._request = fake_request
runpod._graphql = lambda q, *a, **k: {"data": {"myself": {"clientBalance": 50.0, "currentSpendPerHr": 4.01}}}
_load_fleet = notes.load_fleet
notes.load_fleet = lambda r, probe=True: _load_fleet(r, probe, prober=lambda ps: {p["id"]: probes[p["id"]] for p in ps})
notes.R2_ENV = base / "r2.env"
notes.R2_ENV.write_text("E2E_R2_MARKER=loaded-from-r2.env\n")

glog.write_text("2026-09-24T10:00:00+00:00 heartbeat loops=30\n")
bench = src / "backends" / "numerical" / "python" / "verity_numerical" / "bench"
bench.mkdir(parents=True)
for f in (bench.parent / "__init__.py", bench / "__init__.py"):
    f.write_text("")
(bench / "tables.py").write_text("import sys\nprint('# tables (e2e)', *sys.argv[1:])\n")
(root / "steward.toml").write_text(f'[[render]]\nat = "00:00Z"\nsource = "{src}"\nout = "campaigns/e2e/render"\nstore = "{store}"\n')
subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
for k, v in (("user.email", "e2e@steward"), ("user.name", "e2e")):
    subprocess.run(["git", "-C", str(root), "config", k, v], check=True)

args = ["watch", "--root", str(root), "--pods", "--reap", "--snapshot", "--stale-min", "12", "--since-hours", "8", "--idle-min", "5",
        "--passes", "1", "--guardian-log", str(glog)]
print(f"=== temp root {root}\n=== pass 1 (the guardian log's first look only marks its end)", flush=True)
notes.main(args)
with glog.open("a") as f:
    f.write(f"{now:%Y-%m-%dT%H:%M:%S}+00:00 KILLED pid=4242 mem=0.58GB reason=swap 8.6GB used (95%) > 95% cwd={wt} "
            "cmd=/x/.venv/bin/python -m research run --on box-alive --project verity --source . --cwd source\n")
    f.write(f"{now:%Y-%m-%dT%H:%M:%S}+00:00 KILLED pid=4243 mem=0.69GB reason=disk floor 3.4GB free cwd=/Users/nobody "
            "cmd=/x/.venv/bin/python -m research data reindex --remote\n")
    f.write(f"{now:%Y-%m-%dT%H:%M:%S}+00:00 KILLED pid=4244 mem=1.10GB reason=per-proc cap 1.0GB cwd={base}/wt-done "
            "cmd=/x/.venv/bin/python -m pytest -q\n")
print("=== pass 2 (a restarted watcher: three new guardian kills, one under the worktree of the final lane `done`)", flush=True)
notes.main(args)
print(f"=== DELETE /pods/<id> calls: {deleted}")
print(f"=== r2.env loaded (unset vars only): E2E_R2_MARKER={os.environ.get('E2E_R2_MARKER')}")
print("=== reaper.log\n" + (root / "reaper.log").read_text(), end="")
print("=== notes repo: " + subprocess.run(["git", "-C", str(root), "log", "--format=%s", "--name-only"], capture_output=True, text=True).stdout)
print("=== steward-state.json tracked by git: " + str(bool(subprocess.run(["git", "-C", str(root), "ls-files", "steward-state.json"],
                                                                        capture_output=True, text=True).stdout.strip())))
for lane in ("alive", "coordinator"):
    h = sorted((root / "lanes" / lane).glob("*handoff-steward-guardian*"))
    print(f"=== lanes/{lane}/{h[0].name}\n{h[0].read_text()}", end="")
    print(notes.render_inbox(lane, notes.inbox(root, lane)))
