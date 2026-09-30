"""proofs-n2-guest's refill loop on vy-nebius-2 (tmux `proofs-n2-guest`): queues this lane's chunk scripts until each shape class of
rows.json has its CHUNKS_PER_CLASS chunks proved, and logs a JSON line every 5 min to /workspace/verity-guest/feed.log.

    python3 refill.py [--once] [--dry]      stop: touch /workspace/verity-guest/wholerow/STOP (queued jobs then exit 0 at once)

Per row (rows.json, one per shape class, rank order):
  - stage: a gpus=0 stage job, unless node 1 staged that shape in <= 10 s (then its gate stages inline, from the same cache key);
  - gate: once staged (or inline), chunk r0 with the GPU selftest; it covers ~240 s of statements (20 if the shape has no record);
  - chunks: once the gate is verified (done/<id>.json), the next CHUNKS_PER_CLASS - 1 chunks of the row, each ~600 s of statements
    at the gate's measured seconds per statement (the fill runner caps a GPU job at max_min 30).
Every script carries QUESTION in a header comment and as PN2G_QUESTION, which verify.py writes into the job's record.
A script in fill/failed/ stops its row (logged; nothing requeued). Scripts are written to scripts/, chmod +x, then mv'd into the
queue; this loop only reads /workspace/pouw/fill otherwise. Finished outputs are rsynced to vy-nebius-1
/workspace/jobs/proofs-n2-guest/ outside timed windows.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

G = Path("/workspace/verity-guest/wholerow")
FILL = Path(os.environ.get("FILL_DIR", "/workspace/pouw/fill"))
LOG = Path("/workspace/verity-guest/feed.log")
OWNER = "bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4"
N1 = "vy-n1:/workspace/jobs/proofs-n2-guest"
LOW, HIGH = 8, 12
GATE_S, CHUNK_S, OVERHEAD_S = 240, 600, 60
INLINE_STAGE_S = 10
EVERY_S, LOG_EVERY_S = 60, 300
PT = ZoneInfo("America/Los_Angeles")
QUESTION = "what is the whole-row proving cost against K, per shape class, on sm_120? (3 chunks per new class)"
CHUNKS_PER_CLASS = 3
PREFIX = "pn2g-q-"                                         # scripts queued before the question rule are pn2g-<idx>-*: withdrawn


def where(name: str) -> str | None:
    for d in ("running", "queue", "failed", "done"):
        if (FILL / d / name).exists():
            return d
    return None


def done(i: str) -> dict | None:
    p = G / "done" / f"{i}.json"
    return json.loads(p.read_text()) if p.exists() else None


def state(idx: int) -> dict:
    p = G / "state" / f"{idx}.json"
    return json.loads(p.read_text()) if p.exists() else {}


def save_state(idx: int, s: dict) -> None:
    p = G / "state" / f"{idx}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(s))


def timed() -> bool:
    try:
        head = (FILL / "status.txt").read_text().splitlines()[0]
    except (OSError, IndexError):
        return True
    return "timed True" in head or "window waiting True" in head


def submit(name: str, header: str, cmd: str, what: str, dry: bool) -> None:
    body = (f"#!/usr/bin/env bash\n# fill: owner={OWNER} {header}\n# question: \"{QUESTION}\"\n# proofs-n2-guest (bc-c951b059): {what}\n"
            f"exec env PN2G_QUESTION='{QUESTION}' {cmd}\n")
    if dry:
        print("would submit", name, header, cmd)
        return
    p = G / "scripts" / name
    p.write_text(body)
    p.chmod(0o755)
    os.replace(p, FILL / "queue" / name)                  # the same filesystem: an atomic rename, never a half-written script


def per_statement(row: dict) -> int | None:
    s = done(f"pn2g-{row['idx']}-stage") or done(f"pn2g-{row['idx']}-r0") or {}
    st = s.get("stage") or {}
    if st.get("n"):
        return int(st["n"]) * int(st.get("coords_per_instance") or 1)
    return row.get("units_per_statement")


def plan(row: dict, ready: bool) -> tuple[list[tuple[int, int, bool]], dict]:
    """The row's chunks (start, count, gate) as far as they are fixed, and its status. The gate's size is fixed once the row is
    ready (staged, or staged inline), the other chunks' once the gate is verified."""
    idx, st = row["idx"], state(row["idx"])
    per = per_statement(row)
    info = {"rank": row["rank"], "idx": idx, "shape": row["shape"][:16]}
    if not per or ("gate" not in st and not ready):
        return [], info | {"phase": "staging"}
    total = math.ceil(row["row_units"] / per)
    info["statements"] = total
    if "gate" not in st:
        e = row.get("rec_e2e_s")
        st["gate"] = min(total, max(100, int(GATE_S / e) // 100 * 100) if e else 20)
        save_state(idx, st)
    chunks = [(0, st["gate"], True)]
    g = done(f"pn2g-{idx}-r0")
    if g and "chunk" not in st:
        e = g.get("e2e_s_per_statement") or row.get("rec_e2e_s") or 1.0
        st["chunk"], st["e2e_s"] = max(100, min(20000, int(CHUNK_S / e) // 100 * 100)), e
        save_state(idx, st)
    if g:
        chunks += [(a, min(st["chunk"], total - a), False) for a in range(st["gate"], total, st["chunk"])]
        chunks = chunks[:CHUNKS_PER_CLASS]
        info["planned_statements"] = sum(m for _a, m, _g in chunks)
    info["e2e_s"] = st.get("e2e_s") or row.get("rec_e2e_s")
    return chunks, info


def rsync_done(dry: bool) -> None:
    if dry or timed():
        return
    for p in sorted((G / "done").glob("pn2g-*.json")):
        mark = G / "custody" / f"{p.stem}.n1"
        if mark.exists():
            continue
        mark.parent.mkdir(parents=True, exist_ok=True)
        try:
            r = subprocess.run(["bash", "-c", "ssh -o BatchMode=yes -o ConnectTimeout=10 vy-n1 mkdir -p /workspace/jobs/proofs-n2-guest/runs "
                                f"/workspace/jobs/proofs-n2-guest/done && rsync -a --bwlimit=50000 {G}/runs/{p.stem} {N1}/runs/ && rsync -a {p} {N1}/done/"],
                               capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired:
            return
        if r.returncode != 0:
            return
        mark.write_text(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ\n"))


def gpu_h_used() -> float:
    """GPU-h this lane's GPU jobs held, from the runner's exit events (minutes run, paused time excluded)."""
    mins = 0.0
    try:
        with open(FILL / "events.jsonl") as f:
            for ln in f:
                if f'"{PREFIX}' in ln and '"gpus": 1' in ln and '"minutes"' in ln:
                    r = json.loads(ln)
                    mins += float(r.get("minutes") or 0) - float(r.get("paused_min") or 0)
    except OSError:
        pass
    return round(mins / 60, 3)


def tick(rows: list[dict], dry: bool) -> dict:
    mine = {d: sorted(p.name for p in (FILL / d).glob(f"{PREFIX}*.sh")) for d in ("queue", "running", "failed")}
    queued_gpu = [n for n in mine["queue"] if "-stage" not in n]
    stages, gates, todo, per_row, ready_s = [], [], [], [], 0.0
    counts = {"queued": len(queued_gpu), "running": len([n for n in mine["running"] if "-stage" not in n]),
              "staging": len([n for n in mine["queue"] + mine["running"] if "-stage" in n]), "done": 0, "failed": len(mine["failed"])}
    all_done = True
    for row in rows:
        idx = row["idx"]
        stage_id = f"pn2g-{idx}-stage"
        inline = (row.get("rec_stage_s") or 1e9) <= INLINE_STAGE_S
        staged = bool(done(stage_id))
        chunks, info = plan(row, staged or inline)
        failed = [n for n in mine["failed"] if n.startswith(f"{PREFIX}{idx}-")]
        info["failed"] = failed
        if not staged and not inline and not failed and where(f"{PREFIX}{idx}-stage.sh") not in ("queue", "running"):
            stages.append((f"{PREFIX}{idx}-stage.sh", "gpus=0 project=verity cpus=16 max_min=60 mem_gb=64",
                           f"bash {G}/bin/job.sh stage {idx}", f"stage Llama-3.2-1B shape #{idx} ({row['definition'][:48]})"))
        if not chunks:
            info["phase"] = "staging" if not failed else "stopped"
            per_row.append(info)
            all_done = all_done and bool(failed)
            continue
        ok = [(a, m, g) for a, m, g in chunks if done(f"pn2g-{idx}-r{a}")]
        info["done_statements"] = sum(m for _a, m, _g in ok)
        info["gate"] = "passed" if done(f"pn2g-{idx}-r0") else ("failed" if f"{PREFIX}{idx}-r0.sh" in failed else "pending")
        counts["done"] += len(ok)
        complete = bool(done(f"pn2g-{idx}-r0")) and len(ok) == len(chunks)
        info["phase"] = "done" if complete else ("stopped" if failed else "proving")
        all_done = all_done and (complete or bool(failed))
        e = info.get("e2e_s") or 1.0
        for a, m, g in chunks:
            if f"{PREFIX}{idx}-r{a}.sh" in queued_gpu:
                ready_s += m * e + OVERHEAD_S
        if failed or complete or not (staged or inline):
            per_row.append(info)
            continue
        for a, m, g in chunks:
            name = f"{PREFIX}{idx}-r{a}.sh"
            if done(f"pn2g-{idx}-r{a}") or where(name) in ("queue", "running", "failed"):
                continue
            what = (f"Llama-3.2-1B shape #{idx} ({row['definition'][:48]}), chunk {chunks.index((a, m, g)) + 1} of {CHUNKS_PER_CLASS}: "
                    f"statements {a}..{a + m - 1} of the row's {info['statements']}" + (" (gate: GPU selftest)" if g else ""))
            job = (name, "gpus=1 project=verity cpus=16 max_min=30 mem_gb=128" + (" prio=1" if g else ""),
                   f"bash {G}/bin/job.sh chunk {idx} {a} {m} {int(g)}", what)
            (gates if g else todo).append(job)
        per_row.append(info)
    # stage jobs and gates whenever ready; the other chunk scripts only when fewer than LOW are queued, up to HIGH, in rank order
    for job in stages + gates:
        submit(*job, dry)
    counts["queued"] += len(gates)
    q = len(queued_gpu) + len(gates)
    for job in todo[:max(0, HIGH - q) if q < LOW else 0]:
        submit(*job, dry)
        counts["queued"] += 1
    rsync_done(dry)
    return {"counts": counts, "ready_s": ready_s, "rows": per_row, "all_done": all_done}


def line(t: dict) -> str:
    now = datetime.now(timezone.utc)
    rec = {"pt": now.astimezone(PT).strftime("%-I:%M %p %Z"), "utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), **t["counts"],
           "gpu_h_used": gpu_h_used(), "gpu_h_ready": round(t["ready_s"] / 3600, 3), "timed": timed(), "all_done": t["all_done"],
           "rows": t["rows"]}
    return json.dumps(rec)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    rows = json.loads((G / "rows.json").read_text())["rows"]
    last = 0.0
    while True:
        if (G / "STOP").exists():
            with LOG.open("a") as f:
                f.write(json.dumps({"pt": datetime.now(PT).strftime("%-I:%M %p %Z"), "stopped": "STOP file"}) + "\n")
            return 0
        t = tick(rows, a.dry)
        if a.once or a.dry:
            print(line(t))
            return 0
        if time.monotonic() - last >= LOG_EVERY_S or t["all_done"]:
            with LOG.open("a") as f:
                f.write(line(t) + "\n")
            last = time.monotonic()
        if t["all_done"]:
            return 0
        time.sleep(EVERY_S)


if __name__ == "__main__":
    raise SystemExit(main())
