"""ligero-steps-pin: reverify.commitment_problems (red-team-standard-hash R2) over every fetched dump under /workspace/reg.
The pinned relation from `ligero-verify system-digest`; bare dumps: (hashed False, no problems).  Hashed dumps: the a/b/y trees recomputed from the manifest's instance set.
Writes /workspace/lsp/r2_dumps.json; prints one line per dump."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, "/workspace/src")
from backends.direct.ligero.reverify import commitment_problems  # noqa: E402

out = []
for m in sorted(Path("/workspace/reg").rglob("manifest.json")):
    pdir = m.parent
    man = json.loads(m.read_text())
    reps = sorted(p.name for p in pdir.iterdir() if p.is_dir() and p.name.startswith("rep"))
    if not reps:
        reps = ["."] if list(pdir.glob("sub_*.stmt")) else []
    sysf = pdir / (man.get("system_file") or {}).get("path", "system.bin")
    dig = subprocess.run([os.environ["LIGERO_VERIFY"], "system-digest", "--system", str(sysf)], capture_output=True, text=True)
    pinned = json.loads(dig.stdout).get("pinned_relation") if dig.returncode == 0 else None
    t0 = time.time()
    try:
        hashed, bad = commitment_problems(pdir, man, pinned, reps)
        row = {"dump": str(pdir), "pinned": pinned, "reps": reps, "hashed": hashed, "problems": bad}
    except Exception as e:  # noqa: BLE001
        row = {"dump": str(pdir), "pinned": pinned, "reps": reps, "error": f"{type(e).__name__}: {e}"[:300]}
    row["seconds"] = round(time.time() - t0, 1)
    print(json.dumps(row), flush=True)
    out.append(row)
Path("/workspace/lsp/r2_dumps.json").write_text(json.dumps(out, indent=1) + "\n")
