#!/usr/bin/env python3
"""fu.py: the vLLM follow-up epoch's VM side (GO 2026-09-29T13:04Z on main 14f027c3).  The row itself runs on its pod as
`bash verity_vllm/ops/epoch_row.sh` (deadlines, STOP_AFTER, store + preserved inside the job); this only starts pods and jobs and,
after a row ends, takes its evidence, terminates what is left and writes it.

    fu.py balance [N]      the GO's live-balance test (guard-budgets.json on the control pod) and the committed-spend rule for row N
    fu.py launch N         the first offer in stock that passes: pods create (budget line, lease), host RAM, rate, then the job
    fu.py poll UNTIL_UTC   the GO's order, then the held rows while the balance covers them, once a minute until UTC (or all launched)
    fu.py status           each launched row's last progress line
    fu.py finish N         after the job's END: evidence, custody, the pod terminated, rule (a)'s gate, the expected/ write, the digest line

state.tsv beside this file: row, pod, pod_id, run, start_utc, rate, cap, timeout_s, state (live|ended), end_utc, spent."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "rows.json").read_text())
STATE = HERE / "state.tsv"
GO_TREE = Path("/workspace-wt/epoch-14f027c3")
RESEARCH = ["env", f"PYTHONPATH={GO_TREE}/tools/research/src", "python3", "-m", "research"]
FIELDS = ("row", "pod", "pod_id", "run", "start_utc", "rate", "cap", "timeout_s", "state", "end_utc", "spent")
STORE_RESERVE_H = 40 / 60          # the job's own STORE_RESERVE_S (2400) plus the lease's margin come out of the cap's hours


def utc(t: float | None = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t if t is not None else time.time()))


def epoch(s: str) -> float:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def rows_state() -> list[dict]:
    if not STATE.exists():
        return []
    return [dict(zip(FIELDS, ln.rstrip("\n").split("\t"))) for ln in STATE.read_text().splitlines()[1:] if ln.strip()]


def save_state(rows: list[dict]) -> None:
    STATE.write_text("\t".join(FIELDS) + "\n" + "".join("\t".join(str(r.get(f, "")) for f in FIELDS) + "\n" for r in rows))


def sh(argv: list[str], timeout: float = 900) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, cwd="/workspace")


def guard_state() -> dict:
    p = sh([*RESEARCH, "pods", "ssh", "vy-control", "--", "cat /root/.research/pods/guard-budgets.json"], timeout=120)
    text = p.stdout[p.stdout.index("{"):] if "{" in p.stdout else ""
    return json.loads(text)


def balance(n: str | None = None) -> dict:
    """available = live balance - floor - other lanes' open caps - running rows' remaining caps; committed = spent + running caps."""
    g = guard_state()
    now = time.time()
    lines, spent = g["budgets"]["lines"], g["lines"]
    others = 0.0
    for pfx, ln in lines.items():
        if pfx.startswith(CFG["line_prefix"]) or (ln.get("expires") and epoch(ln["expires"]) <= now):
            continue
        s = spent.get(pfx) or {}
        opens = [ln["cap_usd"] - (s.get("spent") or 0.0)] if ln.get("cap_usd") is not None else []
        opens += [ln["cap_usd_per_day"] - (s.get("window_usd") or 0.0)] if ln.get("cap_usd_per_day") is not None else []
        others += max(0.0, max(opens)) if opens else 0.0
    running = committed = 0.0
    for r in rows_state():
        if r["state"] == "live":
            used = float(r["rate"]) * (now - epoch(r["start_utc"])) / 3600
            running += max(0.0, float(r["cap"]) - used)
            committed += float(r["cap"])
        else:
            committed += float(r["spent"] or 0)
    avail = g["balance"] - CFG["balance_floor_usd"] - others - running
    out = {"balance": round(g["balance"], 2), "balance_utc": g.get("balance_utc"), "others_open": round(others, 2),
           "running_remaining": round(running, 2), "available": round(avail, 2), "committed": round(committed, 2)}
    if n:
        cap = CFG["rows"][n]["cap"]
        out.update(cap=cap, balance_ok=avail >= cap, committed_ok=committed + cap <= CFG["lane_cap_usd"])
    return out


def launch(n: str, *, held: bool) -> str:
    """Launch row n on the first offer that is in stock and passes; returns 'LAUNCHED ...', 'NO STOCK', or 'REFUSED ...'."""
    r = CFG["rows"][n]
    if any(s["row"] == n and s["state"] == "live" for s in rows_state()):
        return "REFUSED already live"
    b = balance(n)
    if not b["committed_ok"]:
        return f"REFUSED committed ${b['committed']} + cap ${r['cap']} passes ${CFG['lane_cap_usd']}"
    ahead = sum(CFG["rows"][m]["cap"] for m in CFG["order"] if not any(s["row"] == m for s in rows_state()))
    if held and b["available"] - ahead < r["cap"]:
        return f"REFUSED balance: available ${b['available']} less the unlaunched GO rows' ${ahead} < cap ${r['cap']} ({json.dumps(b)})"
    name = f"{CFG['line_prefix']}{n}"
    log = HERE / f"launch-{n}.log"
    for gpu, count, cloud in r["offers"]:
        lease_h = CFG["max_pod_hours"]
        p = sh([*RESEARCH, "pods", "create", "--name", name, "--gpu", gpu, "--gpu-count", str(count), "--cloud", cloud,
                "--min-ram", str(-(-r["floor_gb"] // count)), "--disk", "250", "--max-hours", str(lease_h), "--idle-min", "20",
                "--register", "--project", "verity"], timeout=1200)
        with log.open("a") as f:
            f.write(f"=== {utc()} {count}x {gpu} {cloud}: rc={p.returncode}\n{p.stdout[-3000:]}\n{p.stderr[-2000:]}\n")
        m = re.search(r"REGISTERED \S+ -> pod (\S+)", p.stdout + p.stderr)
        if p.returncode != 0 or not m:
            continue
        pod_id = m.group(1)
        info = json.loads(p.stdout[p.stdout.index("{"):p.stdout.rindex("}") + 1]) if "{" in p.stdout else {}
        rate, ram = float(info.get("costPerHr") or 0), int(info.get("memoryInGb") or 0)
        hours = r["cap"] / rate - STORE_RESERVE_H if rate else 0
        why = (f"host {ram} GB < {r['floor_gb']} GB" if ram and ram < r["floor_gb"] else
               f"${rate}/h leaves {hours:.2f} h in the ${r['cap']} cap" if hours < 1.5 else "")
        if why:
            sh([*RESEARCH, "pods", "terminate", pod_id], timeout=300)
            sh([*RESEARCH, "pods", "unregister", name], timeout=120)
            with log.open("a") as f:
                f.write(f"{utc()} refused pod {pod_id}: {why}; terminated\n")
            continue
        timeout_s = int(min(hours, CFG["max_pod_hours"] - 0.5) * 3600)
        env = {"ROW": r["key"], "ROWNUM": n, "CLASS": r["class"], "EPOCH_SHA": CFG["epoch_sha"], "PAIRS": str(r["pairs"]),
               "POD_START": str(int(time.time())), "POD": name, **r.get("env", {})}
        if r.get("sm89"):
            env.update(EXPECT_SMS="142", EXPECT_CC="8.9")
        argv = [*RESEARCH, "run", "--on", name, "--project", "verity", "--campaign", "vllm-followup-epoch", "--custody-r2",
                "--custody-ttl", f"{int(timeout_s / 3600 + 2.5)}h", "--timeout", str(timeout_s), "--source", str(GO_TREE),
                "--cwd", "source/integrations/vllm", *[x for k, v in env.items() for x in ("--env", f"{k}={v}")],
                "--", "bash", "verity_vllm/ops/epoch_row.sh"]
        q = sh(argv, timeout=1200)
        with log.open("a") as f:
            f.write(f"{utc()} run rc={q.returncode}\n{q.stdout[-2000:]}\n{q.stderr[-2000:]}\n")
        run = re.search(r"run (r20\d{6}-\d{6}-[0-9a-f]{4}) launched", q.stdout + q.stderr)
        if q.returncode != 0 or not run:
            sh([*RESEARCH, "pods", "terminate", pod_id], timeout=300)
            sh([*RESEARCH, "pods", "unregister", name], timeout=120)
            return f"REFUSED the job did not start on {pod_id} (launch-{n}.log); pod terminated"
        rows = rows_state()
        rows.append({"row": n, "pod": name, "pod_id": pod_id, "run": run.group(1), "start_utc": utc(), "rate": rate, "cap": r["cap"],
                     "timeout_s": timeout_s, "state": "live", "end_utc": "", "spent": ""})
        save_state(rows)
        return f"LAUNCHED #{n} {count}x {gpu} {cloud} pod {pod_id} ${rate}/h host {ram} GB run {run.group(1)} timeout {timeout_s / 3600:.2f} h"
    return "NO STOCK"


def poll(until: str) -> None:
    end = epoch(until)
    plog = HERE / "poll.log"
    while time.time() < end:
        live = {s["row"] for s in rows_state()}
        todo = [(n, False) for n in CFG["order"] if n not in live] + [(n, True) for n in CFG["held"] if n not in live]
        if not todo:
            break
        for n, held in todo:
            res = launch(n, held=held)
            with plog.open("a") as f:
                f.write(f"{utc()} #{n}{' (held)' if held else ''}: {res[:300]}\n")
            if res.startswith("LAUNCHED") and not (HERE / "first-launch-noted").exists():
                note_first(res)
            if held and res.startswith("REFUSED balance"):
                break                      # the held rows go in order: a later one never passes an earlier one
        time.sleep(60)


EXPECTED = Path("/workspace-wt/fu-expected")
PY = "/tmp/covenv/bin/python"
EVIDENCE = Path("/workspace/fu-evidence")


def _run_state(s: dict) -> tuple[str, str]:
    """(state, how): the job's last transition on its pod, or from the evidence store when the pod is gone."""
    p = sh([*RESEARCH, "pods", "ssh", s["pod"], "--", f"python3 -c \"import json;t=json.load(open('/workspace/research/runs/{s['run']}/status.json'))['transitions'][-1];print(t.get('state'))\""], timeout=90)
    out = [x for x in p.stdout.splitlines() if x.strip() and "setlocale" not in x]
    if p.returncode == 0 and out:
        return out[-1].strip(), "pod"
    q = sh([*RESEARCH, "data", "show", s["run"], "--json"], timeout=180)
    try:
        return json.loads(q.stdout)["status"].split()[0], "store"
    except (ValueError, KeyError, IndexError):
        return "unknown", "none"


def finish(n: str) -> str:
    rows = rows_state()
    s = next((x for x in rows if x["row"] == n and x["state"] == "live"), None)
    if s is None:
        return f"#{n}: no live row"
    st, how = _run_state(s)
    if st in ("running", "unknown", "starting", "launched"):
        return f"#{n}: {s['run']} still {st} ({how})"
    evd = EVIDENCE / n
    evd.mkdir(parents=True, exist_ok=True)
    if how == "pod":
        with (evd / "evidence.tgz").open("wb") as f:
            subprocess.run([*RESEARCH, "pods", "ssh", s["pod"], "--", f"tar czf - -C /workspace/research/runs/{s['run']} evidence"],
                           stdout=f, stderr=subprocess.DEVNULL, timeout=900, cwd="/workspace")
        sh(["tar", "xzf", str(evd / "evidence.tgz"), "-C", str(evd)])
        for _ in range(30):                       # the runner's custody push: its marker lists every file, preserved
            c = sh([*RESEARCH, "pods", "ssh", s["pod"], "--", f"cat /workspace/research/runs/{s['run']}/.custody"], timeout=90)
            if '"preserved": true' in c.stdout:
                break
            time.sleep(30)
        else:
            return f"#{n}: {s['run']} ended but its custody is not preserved yet; the pod stays up"
    else:
        rec = json.loads(sh([*RESEARCH, "data", "show", s["run"], "--json"], timeout=180).stdout)["outputs"]["run_record"]
        sh([*RESEARCH, "data", "fetch", rec, "--to", str(evd / "run")], timeout=1800)
        (evd / "evidence").exists() or (evd / "evidence").symlink_to(evd / "run" / "evidence")
    sh([*RESEARCH, "pods", "terminate", s["pod_id"]], timeout=300)
    sh([*RESEARCH, "pods", "unregister", s["pod"]], timeout=120)
    end = time.time()
    s.update(state="ended", end_utc=utc(end), spent=f"{float(s['rate']) * (end - epoch(s['start_utc'])) / 3600:.2f}")
    save_state(rows)
    r = CFG["rows"][n]
    env = {**os.environ, "PYTHONPATH": ".:../../packages/verity/src:../../tools/research/src:../../protocols/sampled_proofs"}
    vl = EXPECTED / "integrations" / "vllm"
    g = subprocess.run([PY, str(HERE / "gate_write.py"), str(evd / "evidence"), r["key"]], capture_output=True, text=True, cwd=vl, env=env)
    decision = (g.stdout.strip().splitlines() or ["HOLD gate produced nothing: " + g.stderr.strip()[-200:]])[-1]
    written = ""
    if g.returncode == 0:
        if "pending=coverage" in decision:
            (evd / "pending").mkdir(exist_ok=True)
            os.replace(evd / "evidence" / "record" / r["key"] / "coverage.json", evd / "pending" / "coverage.json")
        w = subprocess.run([PY, "-m", "tests.regression.rebaseline", "write", "--record", str(evd / "evidence" / "record"), "--commit",
                            CFG["epoch_sha"], "--branch", "main", "--release", "rebaseline-followup-epoch", "--run-id", s["run"], "--force"],
                           capture_output=True, text=True, cwd=vl, env=env)
        (evd / "write.txt").write_text(w.stdout + w.stderr)
        if w.returncode != 0:
            return f"#{n}: gate WRITE but rebaseline write failed (write.txt)"
        sh(["git", "-C", str(EXPECTED), "add", f"integrations/vllm/tests/regression/expected/{r['key']}.json"])
        sh(["git", "-C", str(EXPECTED), "commit", "-q", "-m", f"follow-up epoch: re-baseline #{n} under Q_word v1 at {CFG['epoch_sha'][:8]} (run {s['run']}; {decision})"])
        push = sh(["git", "-C", str(EXPECTED), "push", "-q", "-u", "origin", "HEAD"], timeout=300)
        written = f"written {sh(['git', '-C', str(EXPECTED), 'rev-parse', '--short', 'HEAD']).stdout.strip()}" + ("" if push.returncode == 0 else " (push failed)")
    d = subprocess.run([sys.executable, str(HERE / "digest_line.py"), n, str(evd / "evidence"), s["run"], CFG["epoch_sha"], s["spent"], decision,
                        str(r["pairs"]), "?", "?", str(HERE / f"launch-{n}.log"), "?", "?"], capture_output=True, text=True,
                       env={**os.environ, "STORE": os.environ.get("STORE", "/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d")})
    return f"#{n} ended ({st}), terminated, spent ${s['spent']}; gate: {decision[:200]}; {written or 'not written'}; digest rc={d.returncode}"


def note_first(res: str) -> None:
    """The one-line note the GO asks for when the first row launches (lanes/vllm-coordinator/)."""
    store = Path(os.environ.get("STORE", "/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d")) / "internal/lanes/vllm-coordinator"
    stamp, now = time.strftime("%Y%m%dT%H%MZ", time.gmtime()), time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    text = ('---\ncursor:\n  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"\n---\n\n'
            f"lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: {now} · re: the follow-up epoch GO (13:04Z)\n\n"
            f"**The first follow-up row launched:** {res}. The job runs `ops/epoch_row.sh` at `14f027c3`, with its stops inside the job.\n")
    for _ in range(6):
        try:
            (store / f"{stamp}-note-from-vllm-epoch-run-followup-first-launch.md").write_text(text)
            (HERE / "first-launch-noted").write_text(res + "\n")
            return
        except OSError:
            time.sleep(10)


def status() -> None:
    for s in rows_state():
        p = sh([*RESEARCH, "pods", "ssh", s["pod"], "--", f"tail -n 1 /workspace/research/runs/{s['run']}/evidence/progress.txt"], timeout=90)
        line = [x for x in p.stdout.splitlines() if x.strip() and "setlocale" not in x][-1:] or [p.stderr.strip()[-120:]]
        print(f"#{s['row']} {s['pod']} {s['run']} {s['state']} ${s['rate']}/h: {line[0][:200]}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "balance":
        print(json.dumps(balance(sys.argv[2] if len(sys.argv) > 2 else None)))
    elif cmd == "launch":
        print(launch(sys.argv[2], held=sys.argv[2] in CFG["held"]))
    elif cmd == "poll":
        poll(sys.argv[2])
    elif cmd == "status":
        status()
    elif cmd == "finish":
        print(finish(sys.argv[2]))
