"""ligero-steps-pin regression: every fetched dump under /workspace/reg re-verified at the lane tip.  Rust: `ligero-verify
batch` PINNED (no --allow-any-system) over every sub-batch (+ --system-h for a row-sharing pair).  Python:
serialize.verify_files on the first and the last sub-batch of each dump dir (transcript coins replayed).  Writes
/workspace/lsp/reverify.json; exit 1 unless everything accepts."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, "/workspace/src")
from backends.direct.ligero.serialize import read_statement, verify_files  # noqa: E402

EXE = os.environ["LIGERO_VERIFY"]
out, bad = [], 0
for d in sorted({p.parent for p in Path("/workspace/reg").rglob("sub_*.stmt")}):
    sysf = next((q / "system.bin" for q in (d, d.parent) if (q / "system.bin").is_file()), None)
    sysh = next((q / "system_h.bin" for q in (d, d.parent) if (q / "system_h.bin").is_file()), None)
    if os.environ.get("FILTER") and os.environ["FILTER"] not in str(d):
        continue
    cmd = [EXE, "batch", "--system", str(sysf), "--dir", str(d), "--json", "/tmp/rb.json", "--jobs", "4", "--threads", "2"]
    if sysh is not None:
        cmd[2:2] = ["--system-h", str(sysh)]
    Path("/tmp/rb.json").unlink(missing_ok=True)
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        js = json.loads(Path("/tmp/rb.json").read_text())
        s = js.get("summary", js)
    except Exception as e:
        s = {"error": str(e), "stderr": r.stderr[-400:], "stdout": r.stdout[-400:]}
    rust = {"rc": r.returncode, "batch_accepted": s.get("batch_accepted"), "accepted": s.get("accepted"),
            "rejected": s.get("rejected"), "pinned_relation": (s.get("system") or {}).get("pinned_relation"),
            "system_pinned": s.get("system_pinned"), "python_agree": s.get("python_agree"), "python_disagree": s.get("python_disagree"),
            "batch_reason": str(s.get("batch_reason"))[:200], "seconds": round(time.time() - t0, 1)}
    stmts = sorted(d.glob("sub_*.stmt"))
    st0 = read_statement(stmts[0].read_bytes())
    py = []
    for sp in [] if os.environ.get("RUST_ONLY") else sorted({stmts[0], stmts[-1]}):
        t0 = time.time()
        ok, why, _ = verify_files(sp, sp.with_suffix(".proof"), "cpu")
        py.append({"sub": sp.name, "ok": bool(ok), "why": why[:200], "seconds": round(time.time() - t0, 1)})
    row = {"dir": str(d), "relation": st0.relation, "format": "v6" if st0.v6 else "v5" if st0.v5 else "v4/v2", "steps": st0.steps,
           "n_vus": st0.n_vus, "l": st0.l, "subs": len(stmts), "rust": rust, "python": py}
    good = rust["rc"] == 0 and rust["batch_accepted"] is True and all(p["ok"] for p in py)
    bad += not good
    print(("OK  " if good else "BAD ") + json.dumps(row), flush=True)
    out.append(row)
Path(os.environ.get("OUT", "/workspace/lsp/reverify.json")).write_text(json.dumps(out, indent=1) + "\n")
print(f"{len(out) - bad}/{len(out)} dump dirs accepted (Rust pinned batch + Python)")
sys.exit(1 if bad else 0)
