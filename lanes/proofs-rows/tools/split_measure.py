"""proofs-rows: one (b) chunk with the stage/prove split against the current way, on vy-nebius-1 (tmux proofs-rows-split).

    split_measure.py [--runs 10] [--tag m1]

Question: does staging a chunk in a CPU-only job cut GPU-held minutes, with byte-identical proofs?
Two ready items for the dispatcher (template prover-bench, tree /workspace/research/trees/proofs-rows, queue and priority backfill),
each written once (an item already taken is never written again):
  split-stage-<s8>-<tag>    the split's CPU job (gpus 0): this directory's 73-sweep-shape.sh MODE=shape STAGE_ONLY=1, into cache-b
  split-prove-<s8>-<tag>    once that succeeded: the split's one GPU job, the same script with REQUIRE_STAGED=1 RUNS=<runs> WARM=1
The current way is measured on backend-sweep-2's own (b) chunks of the same shape, read, never written: r0 (its GPU job staged: the
cache missed after a tree change) and r5000 (the cache hit). No other proving job is queued (Daniel's rule, 2:53 PM PDT).
Then writes measure/split-<tag>.json and a line to measure/measure.log: each job's GPU-held seconds (pod scheduled to container
finished), its seconds before the prove (container start to serve.log's birth) and per statement, and the statement's files' sha256
in cache-b and in backend-sweep-2's entry of r0's own stage.
Stop: tmux kill-session -t proofs-rows-split; a submitted job runs to its end, an unsubmitted item is deleted from the ready dir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

LANE = "proofs-rows"
HOME = Path("/workspace/jobs/proofs-rows")
READY = Path("/workspace/jobs/ready") / LANE
DISPATCH = Path("/workspace/jobs/dispatch")
RUNS_DIR = Path("/workspace/jobs/runs")
TREE = "/workspace/research/trees/proofs-rows"
ROW = "llama32-1b__bf16__rtxpro6000__tp1__b1__i1024__o128__mixed__greedy__bi-eager"
SHAPE = "f1e4d147fa9ffa170d24bf31b8e469d59393d7d31bcc53ebda55056eeca59f64"     # GemmCoordinate_v2{K=2048}, #1551's coordinate
REF_ENTRY = Path("/workspace/jobs/flock-sweep2/stage-cache/cdef5bd815bcd97f08f4baf9f0470080")   # r0's own GPU-job stage, 21:09Z
REF_DIGEST = "2b7bd0d9f988494ef0f1e7ab4721d5f9479d4bb372f31971992bdbc83b5c703fedc0cf565886521b9b31ddd75a59712bcda3eaa8a13ec0f3ce7c976abe2b6e9c"
BASELINES = {"r0": ("backend-sweep-2/b-llama32-1b-07b84a-f1e4d147-r0", "r20260930-210621-2a46", "the cache missed: staged in its GPU job"),
             "r5000": ("backend-sweep-2/b-llama32-1b-07b84a-f1e4d147-r5000", "r20260930-214647-a70b", "the cache hit")}
STAGE_RES = {"cpus": 2, "memory": 32, "gpus": 0}
PROVE_RES = {"cpus": 4, "memory": 48, "gpus": 1}
KUBE = {**os.environ, "KUBECONFIG": os.path.expanduser("~/.kube/config")}


def log(msg: str, **kv) -> None:
    line = json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "msg": msg, **kv})
    with (HOME / "measure" / "measure.log").open("a") as f:
        f.write(line + "\n")
    print(line, flush=True)


def item(cmd: str, res: dict) -> dict:
    return {"template": "prover-bench", "tree": TREE, "queue": "backfill", "priority": "backfill",
            "resources": {"prover-bench": res}, "env": {"CAMPAIGN": "backend-sweep", "CMD": cmd}}


def common(cache: str, sid: str) -> str:
    return (f"ROW={ROW} SHAPES={SHAPE} SWEEP={HOME}/sweep FLOCK_WORK={HOME}/flock FLOCK_STAGE_CACHE={HOME}/{cache} "
            f"SUMMARY={HOME}/summaries/{sid}.json")


def put(sid: str, it: dict) -> None:
    tmp = READY / f".{sid}.json.tmp"
    tmp.write_text(json.dumps(it, sort_keys=True))
    os.replace(tmp, READY / f"{sid}.json")
    log("ready", item=sid, cmd=it["env"]["CMD"], resources=it["resources"])


def done(sid: str) -> dict | None:
    key = f"{LANE}/{sid}"
    for ln in (DISPATCH / "done.jsonl").read_text().splitlines():
        if f'"{key}"' in ln:
            r = json.loads(ln)
            if r.get("key") == key:
                return r
    return None


def wait(ids: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    last = 0.0
    while len(out) < len(ids):
        for sid in ids:
            if sid not in out and (r := done(sid)):
                out[sid] = r
                log("ended", item=sid, state=r.get("state"), rc=r.get("rc"), job=r.get("job"))
        if time.time() - last > 300:
            last = time.time()
            log("waiting", pending=[s for s in ids if s not in out], ready=sorted(p.stem for p in READY.glob("*.json")))
        time.sleep(20)
    return out


def ts(s: str | None) -> float | None:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() if s else None


def pod(job: str) -> dict:
    j = json.loads(subprocess.run(["kubectl", "get", "pods", "-l", f"job-name={job}", "-o", "json"], env=KUBE, check=True,
                                  capture_output=True, text=True).stdout)["items"]
    if not j:
        return {}
    p = j[-1]
    sched = next((c.get("lastTransitionTime") for c in p["status"].get("conditions", []) if c["type"] == "PodScheduled"), None)
    term = ((p["status"].get("containerStatuses") or [{}])[0].get("state") or {}).get("terminated") or {}
    return {"pod": p["metadata"]["name"], "scheduled": sched, "started": term.get("startedAt"), "finished": term.get("finishedAt"),
            "exit": term.get("exitCode")}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while b := f.read(1 << 24):
            h.update(b)
    return h.hexdigest()


def files(d: Path) -> dict[str, str]:
    return {f.name: sha256(f) for f in sorted(d.iterdir()) if f.is_file() and f.name != "rec.json"} if d.is_dir() else {}


def entry(cache: Path) -> Path | None:
    for e in sorted(cache.iterdir()):
        if len(e.name) == 32 and (e / "rec.json").exists() and json.loads((e / "rec.json").read_text()).get("shape") == SHAPE:
            return e
    return None


def job_of(key: str) -> str | None:
    subs = [json.loads(ln) for ln in (DISPATCH / "log.jsonl").read_text().splitlines() if f'"{key}"' in ln and '"submit"' in ln]
    return subs[-1]["job"] if subs else None


def timing(job_name: str | None, run: str | None) -> dict:
    """A GPU job's clock: pod scheduled (the GPU is its from here), container started, serve.log born (the statement is staged
    and the loopback verifier starts), container finished or now; statements are serve.log's sessions."""
    p = pod(job_name) if job_name else {}
    r = {"job": job_name, "run": run, **p}
    t_sched, t_start, t_end = ts(p.get("scheduled")), ts(p.get("started")), ts(p.get("finished"))
    if t_start is None and p.get("pod"):
        st = json.loads(subprocess.run(["kubectl", "get", "pod", p["pod"], "-o", "json"], env=KUBE, capture_output=True,
                                       text=True).stdout or "{}")
        t_start = ts((((st.get("status") or {}).get("containerStatuses") or [{}])[0].get("state") or {}).get("running", {}).get("startedAt"))
        r["started"] = t_start and time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_start))
    if t_sched and t_end:
        r["gpu_held_s"] = round(t_end - t_sched)
    if t_sched and t_start:
        r["scheduled_to_start_s"] = round(t_start - t_sched)
    serve = next(iter((RUNS_DIR / run).rglob("serve.log")), None) if run else None
    if serve and t_start:
        born = int(subprocess.run(["stat", "-c", "%W", str(serve)], capture_output=True, text=True).stdout.strip() or 0)
        sessions = sum(1 for ln in serve.read_text(errors="replace").splitlines() if ln.startswith("SESSION"))
        upto = t_end or time.time()
        r |= {"before_prove_s": born - round(t_start), "proving_s": round(upto - born), "sessions": sessions,
              "gpu_held_s_per_statement": round((upto - born) / sessions, 3) if sessions else None, "finished_yet": t_end is not None}
    return r


def job(sid: str, end: dict, gpu: bool) -> dict:
    s = json.loads((HOME / "summaries" / f"{sid}.json").read_text()) if (HOME / "summaries" / f"{sid}.json").exists() else {}
    r = {"item": sid, "state": end.get("state"), "rc": end.get("rc"), **timing(end.get("job"), s.get("run"))}
    if not gpu:
        r["cpu_job_s"] = r.pop("gpu_held_s", None)
    n = s.get("statements") or 0
    r |= {k: s.get(k) for k in ("statements", "accepted_statements", "prove_total_s", "e2e_s", "stage_only", "staged", "stage_cached",
                                "stage_s", "stage_checks", "statement_digests", "binary_sha256", "script_sha256")}
    if n:
        r["e2e_s_per_statement"] = round(s["e2e_s"] / n, 3)
        r["prove_s_per_statement"] = round(s["prove_total_s"] / n, 3)
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--tag", default="m1")
    a = ap.parse_args()
    s8 = SHAPE[:8]
    st, pv = f"split-stage-{s8}-{a.tag}", f"split-prove-{s8}-{a.tag}"
    mine = f"bash {HOME}/tools/73-sweep-shape.sh MODE=shape"
    for sid, cmd, res_, after in ((st, f"{mine} STAGE_ONLY=1 {common('cache-b', st)}", STAGE_RES, None),
                                  (pv, f"{mine} REQUIRE_STAGED=1 RUNS={a.runs} WARM=1 FLOCK_KEEP_SESSIONS=3 {common('cache-b', pv)}",
                                   PROVE_RES, st)):
        if after and wait([after])[after].get("state") != "succeeded":
            log(f"stopped: {after} didn't succeed; {sid} not written", item=after)
            return 1
        if not (done(sid) or (READY / f"{sid}.json").exists() or any((DISPATCH / "taken" / LANE).glob(f"{sid}.*.json"))):
            put(sid, item(cmd, res_))
    end = wait([st, pv])
    res = {"question": "does staging a chunk in a CPU-only job cut GPU-held minutes, with byte-identical proofs?",
           "row": ROW, "shape": SHAPE, "runs": a.runs, "warm": 1,
           "stage": job(st, end[st], False), "split_prove": job(pv, end[pv], True),
           "current": {name: {"item": key, "why": why, **timing(job_of(key), run)} for name, (key, run, why) in BASELINES.items()}}
    eb = entry(HOME / "cache-b")
    fb, fr = files(eb) if eb else {}, files(REF_ENTRY)
    dig = res["split_prove"].get("statement_digests")
    res["bytes"] = {"cache_b": {"entry": eb and eb.name, "files": fb}, "r0_entry": {"entry": str(REF_ENTRY), "files": fr},
                    "statement_files_eq_r0": bool(fb) and fb == fr, "statement_digests": dig, "r0_statement_digest": REF_DIGEST,
                    "statement_digest_eq_r0": dig == [REF_DIGEST]}
    sp, r0, r5 = res["split_prove"], res["current"]["r0"], res["current"]["r5000"]
    if sp.get("gpu_held_s") is not None and sp.get("before_prove_s") is not None:
        # the same chunk the current way: the split's GPU job with its time before the prove replaced by the baseline's
        res["same_chunk_gpu_held_s"] = {"split": sp["gpu_held_s"],
                                        **{f"current, {k}": sp["gpu_held_s"] - sp["before_prove_s"] + b["before_prove_s"]
                                           for k, b in (("cache missed (r0)", r0), ("cache hit (r5000)", r5)) if b.get("before_prove_s") is not None}}
    out = HOME / "measure" / f"split-{a.tag}.json"
    out.write_text(json.dumps(res, indent=1))
    log("measured", out=str(out), same_chunk_gpu_held_s=res.get("same_chunk_gpu_held_s"),
        before_prove_s={"split": sp.get("before_prove_s"), "r0": r0.get("before_prove_s"), "r5000": r5.get("before_prove_s")},
        stage_cpu_job_s=res["stage"].get("cpu_job_s"), statement_files_eq_r0=res["bytes"]["statement_files_eq_r0"],
        statement_digest_eq_r0=res["bytes"]["statement_digest_eq_r0"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
