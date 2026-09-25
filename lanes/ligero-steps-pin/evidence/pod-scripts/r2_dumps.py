"""ligero-steps-pin: reverify.commitment_problems (red-team-standard-hash R2) over every fetched dump under /workspace/reg.
Bare dumps: (hashed False, no problems).  Hashed dumps: the a/b/y trees recomputed from the manifest's instance set.
Writes /workspace/lsp/r2_dumps.json; prints one line per dump."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "/workspace/src")
from backends.direct.ligero.reverify import commitment_problems  # noqa: E402
from backends.direct.ligero.serialize import read_statement  # noqa: E402

out = []
for m in sorted(Path("/workspace/reg").rglob("manifest.json")):
    pdir = m.parent
    man = json.loads(m.read_text())
    reps = sorted(p.name for p in pdir.iterdir() if p.is_dir() and p.name.startswith("rep"))
    if not reps:
        reps = ["."] if list(pdir.glob("sub_*.stmt")) else []
    first = next(iter(sorted(pdir.rglob("sub_*.stmt"))), None)
    pinned = read_statement(first.read_bytes()).relation if first else None
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
