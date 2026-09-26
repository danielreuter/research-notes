"""verify-bligero-real-k: session files read live over ssh vs the verifier run's preserved run record (sha256 per file).

  python snapshot_vs_record.py LIVE_DIR VERIFIER_RUN [SYSTEM_SHA_JSON]
"""
import hashlib, json, subprocess, sys
from pathlib import Path

live, vrun = Path(sys.argv[1]), sys.argv[2]
att = json.loads(subprocess.run(["research", "data", "show", vrun, "--json"], capture_output=True, text=True, check=True).stdout)
rec = att["outputs"]["run_record"]
files = {f["path"]: f["sha256"] for f in json.loads(subprocess.run(["research", "data", "show", rec, "--json"], capture_output=True,
                                                                     text=True, check=True).stdout)["manifest"]["payload"]["files"]}
checked, bad = 0, []
for p in sorted(live.rglob("*")):
    if not p.is_file() or p.name == "index.jsonl":
        continue
    rel = "sessions/" + str(p.relative_to(live))
    checked += 1
    if files.get(rel) != hashlib.sha256(p.read_bytes()).hexdigest():
        bad.append(rel)
sys_bad = []
if len(sys.argv) > 3:
    shas = json.loads(Path(sys.argv[3]).read_text())
    for sid in {p.name for p in live.iterdir() if p.is_dir()}:
        if files.get(f"sessions/{sid}/system.bin") != shas.get(sid):
            sys_bad.append(sid)
print(json.dumps({"live_dir": str(live), "verifier_run": vrun, "record": rec, "files_checked": checked, "mismatched": bad,
                  "system_bin_mismatched": sys_bad, "ok": not bad and not sys_bad}))
sys.exit(0 if not bad and not sys_bad else 1)
