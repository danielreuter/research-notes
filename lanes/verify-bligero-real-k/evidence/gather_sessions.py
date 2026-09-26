"""verify-bligero-real-k: collect the live verifier's session records for cells (read-only).

  python gather_sessions.py CELLS_JSON OUT CELL:VERIFIER_RUN:POD ...

A preserved verifier run is read from its run record in the store (json + coins; system.bin's sha256 from the record manifest);
a run still serving is read over ssh with tar / sha256sum to stdout (nothing written on the pod).  Writes OUT/<source>/<sid>/...
and OUT/system-sha256.json {sid: sha256 of the system.bin the verifier used}.
"""
import json, subprocess, sys
from pathlib import Path

cells = {x["id"][4:12]: x for x in json.loads(Path(sys.argv[1]).read_text()) if "cell" in x["manifest"]["meta"]}
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
shas = json.loads((out / "system-sha256.json").read_text()) if (out / "system-sha256.json").is_file() else {}
src = {}


def research(*a):
    r = subprocess.run(["research", *a], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"research {' '.join(a)}: {r.stderr[-300:]}")
    return r.stdout


for spec in sys.argv[3:]:
    c, vrun, pod = spec.split(":")
    sids = [p["session_id"] for p in cells[c]["manifest"]["meta"]["validation"]["evidence"]["live_verifier"]["per_rep"]]
    try:
        att = json.loads(research("data", "show", vrun, "--json"))
    except SystemExit:
        att = None
    if att and att.get("outputs", {}).get("run_record"):
        rec = att["outputs"]["run_record"]
        man = json.loads(research("data", "show", rec, "--json"))["manifest"]["payload"]["files"]
        d = out / f"rec-{vrun}"
        paths = ["sessions/index.jsonl"] + [f"sessions/{s}/{g}" for s in sids for g in ("*.json", "*.coins")]
        args = ["data", "fetch", rec, "--to", str(d)]
        for p in paths:
            args += ["--path", p]
        research(*args)
        for s in sids:
            shas[s] = next(f["sha256"] for f in man if f["path"] == f"sessions/{s}/system.bin")
        src[c] = {"verifier_run": vrun, "pod": pod, "source": f"store run record {rec}", "dir": str(d / "sessions")}
    else:
        ssh = subprocess.run(["research", "pods", "ssh", "--print", pod], capture_output=True, text=True).stdout.strip().splitlines()[-1]
        d = out / f"live-{vrun}"; d.mkdir(parents=True, exist_ok=True)
        base = f"/workspace/research/runs/{vrun}/sessions"
        files = " ".join(f"{s}/session.json {s}/verdict.json {s}/hello.json {s}/rust_batch.json {s}/*.coins" for s in sids)
        tar = subprocess.run(ssh.split() + [f"cd {base} && tar cf - index.jsonl {files}"], capture_output=True)
        subprocess.run(["tar", "xf", "-", "-C", str(d)], input=tar.stdout, check=True)
        sums = subprocess.run(ssh.split() + [f"cd {base} && sha256sum " + " ".join(f"{s}/system.bin" for s in sids)],
                              capture_output=True, text=True).stdout
        for line in sums.splitlines():
            h, p = line.split()
            shas[p.split("/")[0]] = h
        src[c] = {"verifier_run": vrun, "pod": pod, "source": "ssh read-only (run still serving)", "dir": str(d)}
    print(c, src[c]["source"], len(sids), flush=True)
(out / "system-sha256.json").write_text(json.dumps(shas, indent=0))
prev = json.loads((out / "sources.json").read_text()) if (out / "sources.json").is_file() else {}
(out / "sources.json").write_text(json.dumps(prev | src, indent=1))
