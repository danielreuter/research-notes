"""verify-bligero-real-k: write the verdict labels from the recorded runs' outputs.

  python label.py --run RUN --commit SHA --sessions sessions-check.json [--sources sources.json] [--pins-run RUN] [--dry] CELL8...
"""
import argparse, json, subprocess, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("cells", nargs="+"); ap.add_argument("--run", required=True); ap.add_argument("--commit", required=True)
ap.add_argument("--sessions", type=Path, required=True); ap.add_argument("--sources", type=Path)
ap.add_argument("--pins-run", default=None); ap.add_argument("--dry", action="store_true"); ap.add_argument("--extra", default="")
ns = ap.parse_args()
BY = "verify-bligero-real-k"
cells_dir = Path.home() / ".research/runs" / ns.run / "cells"
sess = json.loads(ns.sessions.read_text())
srcs = json.loads(ns.sources.read_text()) if ns.sources else {}
for c in ns.cells:
    s = json.loads((cells_dir / c / "summary.json").read_text())
    rv, st = s["reverify"], s["input_set_check"]
    ss = next(v for k, v in sess.items() if k[4:].startswith(c))
    assert rv["status"] == "PASS" and ss["ok"] and st["ir_verify"]["ok"] and st["content_digest_eq_cell"] and st["prover_staged_copy"]["equal"]
    assert st["files_vs_manifest"] == "all match"
    reps = rv["reps"]["rep1"]
    secs = round(sum(x["verify_seconds_sum"] for x in rv["reps"].values()), 3)
    sids = [x["session"] for x in ss["sessions"]]
    src = srcs.get(c, {})
    vrun = f"{src.get('verifier_run', '?')} ({src.get('pod', '?')}; {src.get('source', '?')})"
    pins = f"; pins re-checked in the same run" if ns.pins_run in (None, ns.run) else f"; pins run {ns.pins_run}"
    note = (f"{BY} (non-producer) file re-verification at main {ns.commit[:8]} on pod vy-verify-bligero-real-k (run {ns.run}{pins}). "
            f"Input set {s['input_set'][:12]} re-staged from the store: files = its manifest, content digest = the cell's, "
            f"{st['ir_verify']['checked']}/{st['n']} outputs re-evaluated equal by the IR evaluator (input_sets.verify), byte-identical "
            f"to the prover's staged copy. reverify (main, dry run, my staged set as instances root): custody "
            f"{rv['custody']['files']}/{rv['custody']['files']}, system PINNED {rv['relation']} (= my own compile; the 16 real-K pins "
            f"confirmed), a/b/y commitments recomputed from my staged set, every VU covered once, batch {reps['accepted']}/{reps['n']} at "
            f"2^-{reps['batch_bits']:.2f}. Live verifier records ({vrun}; {sids[0]}..{sids[-1]}): 5/5 sessions accepted "
            f"{reps['n']}/{reps['n']} with fresh verifier coins, system sha256 = my compile, rep-1 proofs/statements/coins = the dump. "
            f"{ns.extra + ' ' if ns.extra else ''}Recorded coins replayed: not transferable. Not judged here: the cell's interaction check.")
    verifier = (f"{rv['verifier']['tag']} built on pod vy-verify-bligero-real-k from main {ns.commit[:8]} + backends.direct.ligero."
                f"reverify (main) via lanes/{BY}/evidence/pod-scripts/cell_check.py")
    for key, val, extra in (("verified", "accepted", []), ("verifier", verifier, []), ("verifier_seconds", str(secs), ["--value-json"]),
                            ("same_device", "false", []), ("note", note, [])):
        cmd = ["research", "data", "label", s["cell"], key, val, "--by", BY, "--ref", ns.run, *extra]
        if ns.dry:
            print(c, key, val[:160])
            continue
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(c, key, r.returncode, (r.stdout + r.stderr).strip().splitlines()[0][-120:])
        if r.returncode:
            sys.exit(1)
    if ns.dry:
        print(note)
